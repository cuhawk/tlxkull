---
source: bughunters
source_url: https://bughunters.google.com/blog/securing-the-container-world-with-policies-acjs-and-ctrdac
title: "Securing the Container World with Policies: acjs and ctrdac - Google Bug Hunters"
description: "We released two new open-source projects aimed at enhancing security and flexibility in containerized and Kubernetes environments. Check out this post to learn more!"
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/securing-the-container-world-with-policies-acjs-and-ctrdac#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Securing the Container World with Policies: acjs and ctrdac

![](https://storage.googleapis.com/bughunters-article-images/blogs/imrer.jpg)

Imre Rad

Information Security Engineer

Published: Jul 8, 2024

[RSS Feed](https://bughunters.google.com/feed/en)

# Securing the Container World with Policies: acjs and ctrdac

We are excited to announce the release of two new open-source projects aimed at
enhancing security and flexibility in containerized and Kubernetes environments:

- [acjs](https://github.com/google/acjs) (Admission Control with JavaScript) –
A highly customizable Kubernetes admission controller
- [ctrdac](https://github.com/google/ctrdac) (Containerd Admission Controller)
– An adapter to use Kubernetes admission controllers with plain
Docker/containerd

These projects are designed to work well together, providing a robust framework
for managing and enforcing security policies in various deployment scenarios,
but they can also be used independently from each other.

Another advantage is that the powerful security policies these tools provide can
be implemented **even outside** of Kubernetes clusters (native, containerized
environments).

In this post, you'll learn more about both tools and we'll take a closer look at
an illustrative example of use.

## A short recap of Admission controllers

[Pod security admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
(aka pod security policy) is a widely used feature of the Kubernetes
orchestration system that allows cluster administrators to define security
policies that deployments need to meet. Under the hood, this is implemented as
an
[admission controller](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/),
which is called by
[the webhook mechanism](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#what-are-admission-webhooks)
of the Kubernetes API server. When a pod creation request is not in line with
the defined policies, the admission controller rejects it.

Both acjs and ctrdac heavily rely on these technologies. The following diagram
illustrates the architecture of deployments both outside and inside of a
Kubernetes cluster:

![](https://storage.googleapis.com/bughunters-article-images/blogs/container_policies_01.png)

_Fig 1. Architecture of deployments both outside and inside of a Kubernetes_
_cluster_

## acjs (Admission Controller with JavaScript)

acjs is a Kubernetes Admission Controller that leverages JavaScript as the
policy language. This project allows for flexible and dynamic policy management,
making it easier to address both standard and unique security requirements. acjs
can function as both a validating and a mutating webhook, enabling it to not
only validate incoming requests, but also modify them to comply with security
policies. The latter point explains the design decision of choosing a
Turing-complete language for the policies.

Key features of acjs are:

- JavaScript Policies: Uses JavaScript to define and enforce admission
policies, providing flexibility and ease of use.
- Webhook Integration: Supports both validating and mutating webhooks for
comprehensive policy enforcement.
- Dynamic Policy Management: Allows for real-time updates and modifications to
policies without requiring cluster restarts.

acjs enhances security of Kubernetes and native containerized environments by
providing a powerful tool for managing admission policies, ensuring that all
requests are thoroughly inspected and compliant.

## ctrdac (Containerd Admission Controller)

As explained in the previous sections, the Kubernetes world has a
straightforward design which allows inspecting and modifying the configuration
of workloads. But how to do the same in environments outside of a Kube cluster?
This is where ctrdac enters the picture, which tries to solve this problem by
building on top of well-established industry solutions.

ctrdac integrates with [containerd](https://containerd.io/), a widely used
container runtime (which is also the container runtime interface under Docker!).
The goal is to inspect and validate container images \_before \_they are executed,
ensuring that only trusted and compliant images are deployed and
security-sensitive settings of applications are in line with expectations.

ctrdac is implemented as a light-weight, API-compatible proxy layer in front of
[containerd](https://containerd.io/). It was developed to catch container
creation requests, turning them into Kubernetes
[AdmissionReview requests](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/#request)
emulating pod creation, and calling out to a standard Kubernetes Admission
webhook. Creation of the container is rejected, allowed, or mutated based on the
response of the admission controller.

This tool allows organizations to enforce security policies and verify container
images at runtime. ctrdac is particularly beneficial in environments where
Kubernetes is not used, providing a versatile solution for container security
across various infrastructures.

## Show me what they can do!

### Example \#1: Are you running as root?

To get the gist of it, let’s start with a simple example. Given the following
policy in acjs:

```
policies:
- name: reject privileged containers
  code: |
    if (object.spec.containers[0].securityContext.capabilities.add.includes("cap_sys_admin"))
      return "cap_sys_admin is dangerous!"
```

Running privileged containers would no longer be possible:

```
user@host:~$ docker run --privileged --rm -it ubuntu
docker: Error response from daemon: VIOLATES_POLICY: reject privileged containers: cap_sys_admin is dangerous!: invalid argument.
```

### Example \#2: Provenance verification

acjs also supports provenance verification (with the help of
[slsa-verifier](https://github.com/slsa-framework/slsa-verifier)). Given the
following policy assessing SLSA attestations:

```
- name: verify provenance
  kind: Request
  code: |
    var trustedSourceRepos = ["github.com/some-tool/gcb-tests"]
    if (!slsaEnsureComingFrom(trustedSourceRepos))
       return "SLSA verification of the image failed. Trusted repos are: "+(trustedSourceRepos.join(", "))
```

Only container images coming from a trusted source would be allowed:

```
user@cloudshell:~$ docker run --rm -it us-west2-docker.pkg.dev/some-user/quickstart-docker-repo/quickstart-image:unsigned
docker: Error response from daemon: some name of the policy: SLSA verification of the image failed. Trusted repos are: github.com/irsl/gcb-tests: invalid argument.

user@cloudshell:~$ docker run --rm -it us-west2-docker.pkg.dev/some-user/quickstart-docker-repo/quickstart-image:golden
someuser: Hello! The time is Wed Feb 22 13:44:13 UTC 2024.
```

### Example \#3: Transforming requests

To demonstrate the real power of acjs, let’s see how one could fix
[the recently disclosed vulnerability](https://medium.com/@irsl/sneaky-write-hook-git-clone-to-root-on-k8s-node-e38236205d54)
in the
[gitRepo volume driver](https://kubernetes.io/docs/concepts/storage/volumes/#gitrepo).
The policy below enforces the original recommendation of the Kubernetes
maintainers to use _initContainers_ to populate the volume:

```
policies:
- name: securing gitRepo volumes
  code: |
    for(var i = 0; i < object.spec.volumes.length; i++) {
        var volume = object.spec.volumes[i]
        if(!volume.gitRepo) continue
        var gitRepoCfg = volume.gitRepo
        var gitCmd = [\
              "git",\
              "clone",\
        ]
        if (gitRepoCfg.revision) {
            gitCmd.push("--branch", gitRepoCfg.revision)
        }
        gitCmd.push("--", gitRepoCfg.repository)
        if (gitRepoCfg.directory) {
          gitCmd.push(gitRepoCfg.directory)
        }
        object.spec.initContainers = [\
          ...(object.spec.initContainers || []),\
          {\
              name: "gitrepo-init-"+i,\
              image: "bitnami/git",\
              workingDir: "/repo-volume",\
              command: gitCmd,\
              volumeMounts: [{\
                  mountPath: "/repo-volume",\
                  name: volume.name\
              }]\
          }\
        ]
        volume.emptyDir = {}
        delete volume.gitRepo
    }
    return true
```

Using this acjs policy, a cluster administrator could fix this security issue in
a way that is completely transparent to the users.

For detailed setup instructions and more examples, please refer to the
documentation provided in the respective GitHub repositories:

- [ctrdac Repository](https://github.com/google/ctrdac)
- [acjs Repository](https://github.com/google/acjs)

## Conclusion

Google's release of ctrdac and acjs provides flexible, dynamic, and robust tools
for admission control. These projects can help your organization enforce
consistent security policies across diverse environments. Whether operating
within a Kubernetes cluster or a standalone containerized environment, ctrdac
and acjs offer the tools you need to ensure that only trusted and compliant
images are executed, enhancing overall security and compliance.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab