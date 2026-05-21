---
title: Privileged Docker Container Escape
slug: privileged-docker-container-escape
created_utc: 2026-05-21T00:00:00Z
updated_utc: 2026-05-21T00:00:00Z
tags: [technique/server-side, technique/container-escape, technique/rce, technique/linux]
inbound: []
---

# Privileged Docker Container Escape

## Pattern

Docker containers run as isolated processes sharing the host kernel. When a
container is launched with `--privileged` or specific capabilities
(`CAP_SYS_ADMIN`, `CAP_NET_ADMIN`), isolation is significantly reduced.
A container with `--privileged` has access to all host devices and can mount
the host filesystem, effectively providing full host access.

Common escape techniques:

1. **`--privileged` + host disk mount**: The container can mount `/dev/sda1`
   (or similar host block device) to `/mnt`, then `chroot /mnt` to access the
   host filesystem. Write cron jobs, SSH keys, or modify `/etc/passwd`.

2. **`CAP_SYS_ADMIN` + cgroup release_agent**: Mount a cgroup filesystem, set
   a `release_agent` to a script on the container filesystem, then trigger
   it by creating and removing a cgroup. The release agent executes on the host.

3. **`CAP_SYS_ADMIN` + runc/Docker socket**: If the Docker socket
   (`/var/run/docker.sock`) is mounted inside the container, the container
   can control the Docker daemon, create new privileged containers, and escape.

4. **Writable host path mount**: If a sensitive host path is mounted inside
   the container writable (e.g., `/etc`, `/home`, `/var`), writing to it
   directly modifies the host.

## Preconditions

- Container running with `--privileged`, `CAP_SYS_ADMIN`, or Docker socket mounted.
- Attacker has code execution inside the container (via RCE in the containerized app).

## Detection

- `cat /proc/self/status | grep CapEff` — high effective capabilities indicate privilege.
- `ls -la /var/run/docker.sock` — Docker socket mounted.
- `fdisk -l` — can list host block devices if `--privileged`.

## Triggering

Cgroup release_agent escape (requires `CAP_SYS_ADMIN`):
```bash
mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
echo "$host_path/cmd" > /tmp/cgrp/release_agent
echo '#!/bin/sh' > /cmd && echo "id > $host_path/output" >> /cmd && chmod a+x /cmd
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
cat /output  # runs on host
```

## Seen in the wild

- Educational/case study coverage on BBRE. The technique was covered as part
  of explaining escalation paths after gaining container RCE in bug bounty
  reports (e.g., Azure Health Bot VM2 sandbox escape → container → host).
  [BBRE](https://www.youtube.com/watch?v=_dhONyAk4es)

## References

- Trail of Bits blog post on privileged container escapes
- Felix Wilhelm (@_fel1x) — cgroup release_agent PoC
- See also: [bIO3PSblExI — Azure Health Bot VM2 sandbox escape](../supply-chain/vm2-sandbox-escape.md)
