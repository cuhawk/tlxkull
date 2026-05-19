---
source: detectify
source_url: https://labs.detectify.com/ethical-hacking/scaling-security-automation-with-docker/
title: "Scaling security automation with Docker - Labs Detectify"
author: "Detectify"
published: 2022-11-21T15:34:11+00:00
description: "Docker automation is possible. Gunnar Andrews discusses how ethical hackers can scale their automation workflow by using Docker."
---

[Home](https://labs.detectify.com/)/ [Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/)/ [Scaling security automation with Docker](https://labs.detectify.com/ethical-hacking/scaling-security-automation-with-docker/)

[Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/ "Ethical Hacking")

# Scaling security automation with Docker

**Gunnar Andrews** Nov 21, 2022

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/scaling-security-automation-with-docker/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/scaling-security-automation-with-docker/ "Share on LinkedIn")

![Scaling security automation with Docker](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F08%2Fdocker-automation.png&w=3840&q=75)

## **What is Docker?**

[Docker](https://www.docker.com/) is an open-source platform that allows you to develop, deploy, and manage multiple applications across one operating system. Instead of having many separate servers all configured and dedicated to a specific application, you can run all of your applications from one server, with each application in its own container. For more information on what Docker is, and how it works, check out their [technical documentation](https://docs.docker.com/).

## **How hackers currently scale automation**

Currently, many hackers deploy scripts and applications to virtual private servers (VPSs). As you can probably imagine, running multiple scripts on multiple VPSs quickly leads to a very difficult automation workflow. As an example, you may have three small servers running subdomain enumeration, three running port scans, three running nuclei, and one running a central database. This leaves 10 servers in total.

The only way you can scale up is by adding more servers. Every server adds more operational overheads.

## **Docker automation scaling**

Automation for ethical hacking is a great use case for microservices. Scaling automation with Docker is approaching automation scaling with microservice architecture. Microservice architecture is building a system of small services that operate independently to achieve a common goal. Each step of your workflow can be an isolated microservice with its own Docker image and container. Multiple Docker containers can be deployed onto a single VPS which makes scaling as easy as deploying more containers.

Let’s look at an example of building a microservice architecture using Docker.

![](https://labsadmin.detectify.com/app/uploads/2022/11/example-docker-recon-workflow.png)

For this example, we have a database to store our data, a Redis queue for distributing tasks, and a VPS to host our Docker containers. Cron jobs push tasks to the queue until a container is available to run them. We have 3 containers: one for passive subdomain enumeration, one for domain resolving, and one for discovering HTTP servers. The number of containers can be scaled up or down to meet the needs of the Redis queue. When the tasks are completed, results are stored in the database. To scale up, we simply add more containers.

## **Making things even easier with Docker Compose**

Docker Compose is a tool for running multi-container applications. It uses YAML files to define the configuration of the containers. Once the file is created, all you will need to do is run “docker-compose up”. To scale up, just increase the number of containers in the YAML file, and Docker Compose does the rest. Here’s what the Docker Compose file looks like.

![](https://labsadmin.detectify.com/app/uploads/2022/11/example_docker_compose.png)

## **How to scale automation**

To show how you can scale automation, let’s make a single container environment and install some tools within that container. We will use the following:

- A Redis server from Digital Ocean.
- A VPS to run containers.
- A server with hakscale configured to push subfinder commands.

[Hakscale](https://github.com/hakluke/hakscale) pushes commands to our Redis queue and pops them to [subfinder](https://github.com/projectdiscovery/subfinder). You need three files in a directory to get set up:

- Dockerfile
- docker-compose.yaml
- hakscale-config.yaml

### **Dockerfile**

FROM golang:1.19.2-alpine

\# Adding git to install tools!

RUN apk update && apk add bash git

\# Copy hakscale config file with Redis queue info!

COPY hakscale-config.yaml /root/.config/haktools/hakscale-config.yml

\# Install hakscale from hakluke!

RUN go install github.com/hakluke/hakscale@latest

\# Install subfinder from project discovery!

RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

ENTRYPOINT hakscale pop -q blogDemo

### **docker-compose.yaml**

version: “3.9”

services:

     subdomain\_worker:

         image: subdomain\_worker

         build:

           context: .

           dockerfile: Dockerfile

      network\_mode: host

### **hakscale-config.yaml**

redis:

host: <your-redis-host>

port: <your-redis-port>

password: <your-redis-password>

Once you have your Redis queue deployed, the three files created in a directory, and hakscale configured, you can spin up your example worker by running \`docker-compose up\`. Once the build is complete you can push commands to it.

![](https://labsadmin.detectify.com/app/uploads/2022/11/container_built.png)

Next, create a file of domains you would like to test, for example:

$ cat testdomains.txt

bugcrowd.com

hackerone.com

Run \`hakscale push -p “host:./testdomains.txt” -c “subfinder -d \_host\_” -t 20 -q blogDemo\`. This will push two commands to the queue. The worker will pick them up and start processing them. When it finishes it should print the output back to the queue, similar to below:

### **Worker output**

![](https://labsadmin.detectify.com/app/uploads/2022/11/subdomain_worker_out.png)

### **Queue ouput**

![](https://labsadmin.detectify.com/app/uploads/2022/11/queue_output.png)

The worker will continue to run jobs from the queue until none are left. It will then poll until there are more to run. To scale the automation quickly and efficiently using this containerized method, you can easily spin up as many of these containers as required.

## **Conclusion**

I hope this guide has convinced you to give Docker a shot when setting up your automation infrastructure. Docker can initially seem intimidating, but I promise that this will improve your automation’s development and deployment. I use this architecture personally for my automation, so feel free to reach out to me personally for advice.

* * *

#### **Written by:**  **Gunnar Andrews**

My online alias is G0lden. I am a hacker out of the midwest United States. I came into the hacking world through corporate jobs out of college, and I also do bug bounties. I enjoy finding new ways to hunt bugs and cutting-edge new tools. Making new connections with fellow hackers is the best part of this community for me!

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/scaling-security-automation-with-docker/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/scaling-security-automation-with-docker/ "Share on LinkedIn")

**Gunnar Andrews**

Ethical Hacker

## Check out more content

Why picking targets is so important Many ethical hackers struggle because they are hacking the “wrong” types of targets for them. This is especially true …

December 07, 2022

You will find a common pattern if you read blog posts or watch interviews with some of today’s top ethical hackers. When asked if coding …

November 30, 2022

Approaching a target to hack can feel like climbing a mountain. You may face large scopes, confusing applications, complex user hierarchies…the list goes on. The …

October 28, 2022

TL/DR: In this world of rapid digitization, companies are moving from traditional on-premise deployments to cloud service providers for handling their infrastructure. In this article, …

July 25, 2022