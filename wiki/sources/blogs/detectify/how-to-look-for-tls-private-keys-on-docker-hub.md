---
source: detectify
source_url: https://labs.detectify.com/how-to/look-for-tls-private-keys-on-docker-hub/
title: "How to: Look for TLS private keys on Docker Hub - Labs Detectify"
author: "Detectify"
published: 2022-06-16T07:44:17+00:00
description: "Detectify security researcher Alfred Berg wrote about how one can hunt for secrets over the whole docker hub."
---

[Home](https://labs.detectify.com/)/ [How to](https://labs.detectify.com/category/how-to/)/ [How to: Look for TLS private keys on Docker Hub](https://labs.detectify.com/how-to/look-for-tls-private-keys-on-docker-hub/)

[How to](https://labs.detectify.com/category/how-to/ "How to")

# How to: Look for TLS private keys on Docker Hub

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2022%2F06%2Falfred-berg.jpg&w=128&q=75)

**Alfred Berg** Jun 16, 2022

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/look-for-tls-private-keys-on-docker-hub/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/look-for-tls-private-keys-on-docker-hub/ "Share on LinkedIn")

![How to: Look for TLS private keys on Docker Hub](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2022%2F06%2Fdoker.png&w=3840&q=75)

**TL/DR: It’s becoming increasingly easy to compromise sensitive information for attackers to take advantage of. In this post, Detectify security researcher [Alfred Berg](https://twitter.com/berg0x00) wrote about how one can hunt for secrets over the whole docker hub.**

For a while I have been interested in docker images and containers. While using the docker CLI to pull a docker image from docker hub and inspecting all the HTTP requests that it makes, I saw that there was one response body that looked something like this (an NGINX image taken as an example):

![](https://labsadmin.detectify.com/app/uploads/2022/06/image4-1536x1195-1.png)

This file contains among other things the environment variables for the docker image and the commands used to create the docker image. This seemed like an interesting place to look for secrets. I built a program to download this file for as many docker images on docker hub as I could. This file was successfully downloaded for 3 million docker images, one tag for each image.

There have been some similar [writeups/blogs](https://blog.gitguardian.com/hunting-for-secrets-in-docker-hub/) before about looking for secrets at docker hub, but this blog post will focus on hunting for secrets more broadly over the whole docker hub, instead of deep diving into a few docker images.

## **What does a docker image consist of?**

A docker image consists of JSON files and multiple compressed archives, where each archive corresponds to a layer of the docker image, and the combination of the layers corresponds to the filesystem of the image. A new layer is created for every command or instruction that changes the filesystem when creating the image. For example, the lines ADD nginx.conf /etc/nginx/conf.d/default.conf and RUN touch testfile in a Dockerfile would create one layer each.

The full process of pulling an image is documented [here](https://docs.docker.com/registry/spec/api/#pulling-an-image), but first, we need to get a list of potential manifests to use, then fetch one. A manifests looks something like this:

![](https://labsadmin.detectify.com/app/uploads/2022/06/manifest-1.png)

Each digest here corresponds to a blob, in practice either a JSON file or a compressed archive that can be downloaded.

In the \`layers\` json array each json object corresponds to one layer of the image that can be fetched. The order of the items in the json array is the same as the order the commands that created the layers were run. The commands that created the layers can be fetched from the digest that corresponds to the config. That configuration file looks something like this:

![](https://labsadmin.detectify.com/app/uploads/2022/06/config.png)

This file contains what the actual running container should have for environment variables, entrypoint, and so on. Additionally, each JSON object under the key \`history\` that doesn’t have the “empty\_layer”: true set corresponds to one of the six layers seen in the manifest. This means that it is possible to do a selection of what image layers to download by looking at the command in the “created\_by”, and then only downloading the layers that seem interesting.

## **TLS certificate private keys**

From looking over the name of the files that were being added to docker images, it could be seen that a lot of file extensions commonly associated with certificates were being added, for example, .pem, .cer, .key e.t.c. TLS certificates (used e.g. for https) have a public key that intentionally anyone can get and a private key that should not be public. If the private key would become public it could lead to anyone that is in the network path of the traffic being able to intercept and potentially modify the traffic, defeating the purpose of HTTPS. I decided to take a look if any of these files contained any private keys.

A few regular expression like “(etc/ssl\|.pem\|.crt\|.key\|.cer\|etc/letsencrypt\|etc/pki\|usr/local/share/certs\|var/ssl/)” were written to match each command or file/directory that was added to the docker image that seemed to be certificate related. These regular expressions were run over the commands in the images config file that was shown before. The corresponding image layer for each command that was matched was then downloaded and extracted. To extract the private keys from all of the files we look for various private key headers and footers, like “—–BEGIN RSA PRIVATE KEY—–” and “—–END RSA PRIVATE KEY—–” and extract everything between them.

Once all the private keys are extracted the challenge is to now find any private key that has a matching certificate. To do this we can calculate a SubjectPublicKeyInfo (SPKI) hash from the private key, this can be done in openssl with the following command

```
openssl pkey -outform DER -in [path-to-private-key] -pubout | openssl sha256
```

The output from this will be a sha256 hash, looking something like this “9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08” (this is just sha256(“test”)). This hash can then be searched for on the certificate transparency logs with https://crt.sh/?spkisha256=9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08, any certificate that has the same SPKI hash makes use of the private key.

In total 1551 certificates that I had a matching private key were found in the certificate transparency logs. Out of these 223 had not expired and were sent to the certificate authorities to be revoked.

## **AWS access keys**

Another common occurrence was leaking various kinds of secrets in the environment variables of the docker images. One particular example of this is [AWS access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html). These keys are used to programmatically control the AWS organization/user that they belong to. Depending on the permissions granted to the keys it can range from full control of the whole AWS account to limited access to some small part of it.

In total 671 unique access keys with potential secret keys were found. It was not tested how many of these keys were valid and actually worked, instead they were sent over to AWS’s security team that took actions to protect their customers.

To see if there were other people already looking for AWS keys in the environment variables and command history of docker images on docker hub [two images containing canary AWS keys](https://canarytokens.org/generate) were uploaded. Neither of the keys have been used yet, and they were published about a month before writing this blog post.

## **Prevention process**

From looking at the usernames of the images that had the exposed data, the majority seemed to be various developers’ own accounts instead of the company’s official docker hub accounts. This could be from the employee using docker hub instead of their company’s internal registry, another potential is that they intended to use private docker hub images but accidentally have made them public.

The secrets should arguably never have been in the images to begin with. Sensitive environment variables should be supplied to the running containers instead of being baked into the images, and sensitive files can be supplied to the container by using volumes. If the secrets are required when building the container it should be made sure that they don’t end up in the final image.

Another thing to consider is to inspect what the image actually contains if it will be made public. To see what the layers of the image contain the tool [wagoodman/dive](https://github.com/wagoodman/dive) can be used, it is important to note that if a file is added in one layer but then removed in another layer that file can still be recovered, similarly to how removed files in a git repository can still be recovered. To view the environment variables of a docker image \`docker inspect \[image:tag\]\` can be used.

![](https://labsadmin.detectify.com/app/uploads/2022/06/image1-2.png)

To show the commands used to create the image \`docker history –no-trunc –format “{{.CreatedBy}}” \[image:tag\]\` can be used.

![](https://labsadmin.detectify.com/app/uploads/2022/06/image3-1.png)

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/look-for-tls-private-keys-on-docker-hub/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/look-for-tls-private-keys-on-docker-hub/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2022%2F06%2Falfred-berg.jpg&w=128&q=75)

**Alfred Berg**

Security Researcher, Detectify

## Check out more content

External Attack Surface Management (EASM) is the continuous discovery, analysis, and monitoring of an organization’s public facing assets. A substantial part of EASM is the …

January 13, 2023

TL/DR: Web applications have both authentication and authorization as key concepts and if bypassed by an attacker, it can compromise sensitive data. With threats such …

August 05, 2022

TL/DR: Web applications can be exploited to gain unauthorized access to sensitive data and web servers. Threats include SQL Injection, Code Injection, XSS, Defacement, and …

May 16, 2022

If you don’t know about HTTP/2 request smuggling then what are you hacking? Alfred Berg, Security Researcher at Detectify, shows you how to set up …

August 26, 2021