---
source: detectify
source_url: https://labs.detectify.com/ethical-hacking/hakluke-creating-the-perfect-bug-bounty-automation/
title: "Hakluke: Creating the perfect bug bounty automation - Labs Detectify"
author: "Detectify"
published: 2021-11-30T09:58:44+00:00
description: "Bug Bounty Automation is the key to success for many expert bug bounty hunters including Hakluke. He walks through how he does it."
---

[Home](https://labs.detectify.com/)/ [Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/)/ [Hakluke: Creating the perfect bug bounty automation](https://labs.detectify.com/ethical-hacking/hakluke-creating-the-perfect-bug-bounty-automation/)

[Ethical Hacking](https://labs.detectify.com/category/ethical-hacking/ "Ethical Hacking")

# Hakluke: Creating the perfect bug bounty automation

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2021%2F08%2Fhakluke.jpg&w=128&q=75)

**Hakluke** Nov 30, 2021

[hakluke](https://labs.detectify.com/tag/hakluke/ "hakluke")

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/hakluke-creating-the-perfect-bug-bounty-automation/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/hakluke-creating-the-perfect-bug-bounty-automation/ "Share on LinkedIn")

![Hakluke: Creating the perfect bug bounty automation](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F08%2FScreenshot-2021-11-30-at-10.09.37.png&w=3840&q=75)

**I think I have a problem. I’m addicted to building bug bounty automation. I’ve built a full bug bounty automation framework from the ground up 3 times now. It has become better every time, but I’m still not happy. I’m about to start building my 4th iteration.**

Every time I build something I refine the process. In this article, I am going to walk you through every attempt I have made to build a bug bounty automation framework including the wins and failures. Then I’m going to tell you exactly how I plan to build my next one.

# Attempt \#1: Bash

This is how a lot of my tools start. I come up with an idea that sounds fairly simple in theory, drastically underestimate the amount of work involved, and then try to make it happen in a bash script. My bug bounty automation project was no different.

The result ended up being a 100 line bash file that followed a pattern like this.

```
#!/bin/bash

# Get subdomains and check for HTTP responses
cat rootdomains.txt | subfinder | tee subdomains.txt | httpx | tee httpx.txt

# Brute force all subdomains
cat httpx.txt | while read url; do
  dirsearch.py -e php,aspx,asp,txt,bak -u $url | tee ./bruteforce/$url-dirsearch.txt;
done

# Check all domains for open git repositories
cat httpx.txt | while read url; do
  if curl $url/.git/config | grep -q "[core]"
    then echo "Open .git repository at $url" | ./notify.sh
  fi
done

# Do another thing
cat httpx.txt | while read url; do
  # do another thing
done

Etc…
```

I ran the script overnight and struggled to sleep. I was excited to wake up and see the results! I had high hopes that I would be retiring in a week, maybe two, due to the piles of cash bounties that would be waiting for me in my vulns.txt file the next morning. Once the bounty payments came in I could finally spend all of my waking hours eating ramen and binging Antique Roadshow with my cats.

In reality I woke up the following morning to find that my bash script had errored out somewhere along the line and found zero bugs. I quickly realized that this approach had a couple of systemic issues.

- It was too slow
- Storing data in text files is not ideal
- Any failure in any tool killed the whole script

Back to the drawing board…

# Attempt \#2: Django

To solve the issues I faced with the bash script, I decided to start again using a proper framework. At this stage, the framework that I was most comfortable with was Laravel PHP, but I ended up going with Django because most of the hacking tools that I was using at that time were written in Python.

## Data Storage

The first problem to solve was how to structure the data storage. I ended up storing everything in a relational database (PostgreSQL), utilizing the Django ORM. I set up relationships between the objects to mimic how they work in real life. It looked something like this:

![](https://labsadmin.detectify.com/app/uploads/2021/11/Screenshot-2021-11-30-at-10.10.01.png)

With the relationships set up this way, it would be easy to query the database to answer questions such as:

- Which program does this URL belong to?
- Which subdomains have port 3389 open?
- What vulnerabilities have been discovered on sub.domain.com?

By default, Django’s ORM also stores the created and modified dates for each instance that is persisted to the database, so you can ask time-based questions such as:

- What new subdomains have been discovered in the last hour?
- What new open ports have been discovered this week?

## Code Structure

Django is typically considered to be a _web_ framework. My original intention was to build out a frontend web application to manage the automation tasks, but I quickly realized that Django actually works very well as a modular framework for command-line applications by utilizing Django’s [custom management commands](https://docs.djangoproject.com/en/3.2/howto/custom-management-commands/). Instead of writing a whole web frontend, I ended up writing each functionality of the automation into custom management commands so that it could be easily executed from the command line, scheduled with cron, wrapped into a bash script, etc.

For example, I wrote a management command called “subfinder”, which would pull all of the root domains out of the database, run project discovery’s “subfinder” against them, and store the resulting subdomains back into the database. To run it I could just type something like this into the terminal:

```
# run against all root domains in the database
django-admin subfinder

# run against all of Tesla's domains from the database
django-admin subfinder -program tesla

# run against example.com
django-admin subfinder -rootdomain example.com
```

I wrote a couple of basic modules in this way, but quickly realized that the real value would be developing a huge set of modules to discover many different types of vulnerabilities. Keep in mind that this was years before Project Discovery’s [Nuclei](https://github.com/projectdiscovery/nuclei) tool was released, so at this time there were not many people bug hunting at scale, and there was no awesome open-source central repository of vulnerability detection signatures that I knew about.

This was when I started collaborating with [codingo\_](https://twitter.com/codingo_) and [sml555\_](https://twitter.com/sml555_) to build out a stack of vulnerability detection modules. Finally we started seeing the bounties rolling in!

But we had hit another issue… It was slow.

## Speed and Scaling

The problem was that we were performing multiple scans against _millions_ of subdomains. Let’s say that for each subdomain, I want to run some scans that take a total of 1 minute. This would be very minimal scanning on each host, but it would still take 1 minute per host. At 2 million subdomains, it would take nearly 4 years to complete. We really wanted to bring this down to under 1 hour.

The first thing we tried was using multiple threads. For example, instead of just running this command, which would run subfinder against every root domain in consecutive order:

`django-admin subfinder`

We could use something like [GNU parallel](https://www.gnu.org/software/parallel/) which would allow us to run subfinder against multiple domains concurrently. For example:

`cat root-domains.txt | parallel -j 20 "django-admin subfinder -rootdomain "`

This is also where the idea for [Interlace](https://github.com/codingo/Interlace) was born. Multithreading in this manner drastically reduced the amount of time taken to complete tasks, but it created a new problem. Now that we were running 20 instances of subfinder concurrently, the VPS we were using was running out of RAM and CPU. We could solve this temporarily by using a more powerful VPS (vertical scaling), but even an extremely powerful VPS was not powerful enough to perform all of the tasks that we needed within the timeframe that we were expecting.

This is when we had the idea to spin up lots of low-powered instances to perform tasks, and they’d all report their results back to a central data source. This is called horizontal scaling, although I didn’t know that at the time.

In our first attempt to implement this, we (naively) created a “Job” object that sat in a PostgreSQL database. We then created a worker client that would continuously retrieve a job, execute the job, then return the output back to the database. As soon as we kicked it off, we realised that there were race conditions everywhere. Most of the workers ended up executing the same jobs at the same time, and every job was being executed 10+ times. To counteract this, we tried to introduce database locking, but this made the process so slow that we might as well have gone back to our vertical scaling method.

In my frustration, I ended up joining a Django community online and explaining the dilemma to a group of total strangers. One of them introduced me to the concept of queues and message brokers, and said that [RabbitMQ](https://www.rabbitmq.com/) might solve our problems.

I implemented the same queue concept utilising RabbitMQ instead of PostgreSQL, and it worked! We scaled up to 100 workers and suddenly we were able to perform recon and vulnerability scanning of all bug bounty assets in a fraction of the time. Together, we found a lot of bugs this way because we were among the first to implement bug bounty hunting at scale. Even scanning for low-hanging fruit was profitable because we were always one of the first parties to discover when hosts fell into a vulnerable state. All of the workers were $5 VPSs and we had a few more powerful servers for the core functionalities. The infrastructure ended up looking something like this.

![](https://labsadmin.detectify.com/app/uploads/2021/11/Screenshot-2021-11-30-at-10.09.49.png)

Our system wasn’t perfect though:

- The code base was monolithic and time consuming to set up
- The tool did not integrate well with other tools without developing custom modules, which was time consuming
- It was difficult to detect and monitor when workers were failing to complete jobs

Ultimately, the three of us all ended up working at Bugcrowd, so our bug hunting and automation took a back seat, and we ended up pulling it offline when we had no time to focus on it anymore.

# Attempt \#3: Golang and the Unix Philosophy

By this point, automating the discovery of low-hanging fruit had become a _very_ common tactic among bug bounty hunters. Suddenly every man and his dog had their own bug bounty automation. Due to this, my focus moved to either manual hacking or researching popular services to uncover misconfigurations that might result in widespread vulnerabilities. In the latter, a good scalable system was still necessary for discovering all hosts running a particular technology. For example, say you find a common misconfiguration in a particular WordPress plugin – having good automation was very useful because:

- I already had a dynamic, up-to-date list of in-scope targets on hand at all times in the database
- It was trivial to develop a new module to detect the presence of the WordPress plugin on all targets

Scanning for low-hanging fruit was no longer very profitable for me, but I still found automation extremely useful for testing custom payloads and maintaining an up-to-date list of targets including open ports, utilized technologies, etc. The problem was, the existing Django setup was quite clunky, especially when I wanted to do something _custom_ and _quickly_. Rather than having a bunch of separate tools to quickly perform custom tasks, I had one gigantic tool that did everything, and didn’t integrate nicely with other tools.

I found myself often reverting back to using manual tools that followed the Unix philosophy more closely like [httpx](https://github.com/projectdiscovery/httpx) and [nuclei](https://github.com/projectdiscovery/nuclei). This made it easy to build a custom workflow by simply piping tools into one another. Unfortunately, hacking in this way meant that I lost the ability to organize my data into a relational database and scale out over multiple hosts.

This is when I started forming a plan for a new bug bounty automation setup. I wanted to combine the power of the Unix philosophy with the power of horizontal scaling and relational databases. The new system would consist of four completely independent parts. Each part could be used on it’s own, or as part of the larger system by chaining tools together.

1. A system to store and retrieve data from the database
2. A system to manage scaling out jobs
3. A system to scan for vulnerabilities
4. A system to send notifications when something is discovered

Thankfully, good solutions for number 3 and 4 already existed (Project Discovery’s Nuclei and Notify). I just needed to build out a custom solution for 1 and 2 – so that’s what I did!

## Hakstore

First I built “Hakstore”, a REST API server and corresponding client in Golang to interact with the database. This allows you to quickly create/edit/delete data from the relational database. For example, this command would list all subdomains associated with the Tesla program.

hakstore subdomains list -program tesla

This command would take all subdomains from a file and add them to the database, and associate them with the root domain “tesla.com”.

`hakstore subdomains import -f subs.txt -rootdomain tesla.com`

This command would delete a program from the database

`hakstore programs delete -id tesla`

## Hakscale

Next I built out a command line tool designed to scale out shell commands to many systems, I called it “hakscale”. If you’re familiar with [Interlace](https://github.com/codingo/Interlace), it basically works the same as that except it distributes the command over multiple systems instead of multiple threads on one system. I wrote it in Golang and used Redis as the message broker to distribute the commands.

Executing the following command would get a list of URLs from `urls.txt`, then create a command for each URL, replacing the `_url_` placeholder with the actual URL. All of these commands are then sent to a queue on the Redis server.

`hakscale push -p "url:./urls.txt" -c "echo _url_ | nuclei -nc --config /opt/config.yml" -t 600`

Then, we have a bunch of “worker” VPSs each running the following command:

`hakscale pop -t 20`

This command will create 20 threads, each thread constantly pulls jobs from the “jobs” Redis queue, executes them, and then sends the results back to a “results” queue. This results queue is monitored by the original VPS that pushed the job – when it sees a result in the queue, it will print it to the terminal. For the visual learners, here’s a diagram:

![](https://labsadmin.detectify.com/app/uploads/2021/11/Screenshot-2021-11-30-at-10.09.37.png)

The coolest thing about this tool is that it _feels_ like you are executing commands on your local machine, but you’re actually executing those commands on hundreds of workers which makes it _extremely_ fast.

## Putting the Components Together

Now that I have decoupled each component of the automation, I have a lot more flexibility. Rather than being confined to the functionality of the custom Django management commands, I can now generate literally any set bash commands in seconds, and they will be executed at scale.

Still though, it isn’t a perfect setup – in fact I recently pulled all of the infrastructure offline.

- I had 100 worker VPSs running 24/7, costing me $500+ per month even though I only used them for a fraction of that time.
- It was difficult to tell when commands were failing.
- If anything went wrong (for example, if one result was never pushed back to the queue due to a temporary network failure) I was never alerted, and I had no way of troubleshooting what happened.

\*sigh\*

# Attempt \#4: Cloud Native

Recently, I got my AWS Cloud Practitioner and Solutions Architect Associate certifications. While I was studying for the exams, I learned about a lot of AWS offerings that I wish I had known about sooner. It would have saved me **_so_** much time and frustration. If there are any solutions architects reading this, I bet you have been cringing constantly for the last ten minutes, reading about my dodgy solutions.

Now I feel as though I have a decent grasp on how to set up a much better automation system utilizing AWS. I haven’t actually set this automation system up yet, but I plan to do it as a weekend project sometime soon, and I’ve got it planned out in my head. Here’s my game plan.

- Workers are built as Docker containers, managed by AWS Fargate and AWS Elastic Container Service (ECS).
- Workers scale automatically based on the number of items in the job queue. This will ensure that a large amount of workers are available when I need them, but they all die when I don’t need them anymore. This could potentially be set up very quickly by utilizing an Elastic Beanstalk worker environment.
- EFS will be used to share files to all containers (config files, tools, etc.)
- Amazon Simple Queue Service (SQS) is used to manage jobs. A request-response system is used to send jobs and receive results. A dead letter queue (DLQ) is utilized to discover jobs that are failing.
- Amazon Aurora is used to store relational data.

My hakstore tool should already play nicely with Amazon Aurora since it is PostgreSQL compatible. Now I just need to modify hakscale to work with SQS instead of Redis which shouldn’t be too hard.

Once I set this up, I think that I finally will have hit my peak in bug bounty automation. It will be cost effective, flexible, reliable, and performant.

I’ll let you know how it goes in a future article, wish me luck!

# Conclusion

If you are thinking about building your own bug bounty automation, I would highly recommend first educating yourself with what technologies are already available either as open source projects or cloud services. This will save you a lot of money along with months of crippling frustration and imposter syndrome.

Also – planning ahead (both infrastructure and code) is important. When you’re working on a personal project, it’s easy to just jump in and start coding, but more often than not this results in roadblocks and unmaintainable code.

Lastly, I’m always keen to chat about bug bounty automation. If you have any questions feel free to hit me up on [Twitter](https://twitter.com/hakluke), [YouTube](https://youtube.com/hakluke), [Instagram](https://www.instagram.com/hakluke_/) or on my [website](https://hakluke.com/).

# Detectify?

At this stage, [Detectify](https://www.detectify.com/) does not sell to bug bounty hunters, but they’ve combined bug bounty and automation into an attack surface management tool. If you are an organization looking to perform this type of scanning to protect your organization, Detectify will be of interest to you. Detectify is an automated External Attack Surface Management solution powered by a [world-leading ethical hacker community](https://www.detectify.com/crowdsource). They enable security teams to map out their entire attack surface and take a proactive approach in resolving vulnerabilities within their whole IT ecosystem, including those impacting third-party software.

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/ethical-hacking/hakluke-creating-the-perfect-bug-bounty-automation/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/ethical-hacking/hakluke-creating-the-perfect-bug-bounty-automation/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2021%2F08%2Fhakluke.jpg&w=128&q=75)

**Hakluke**

Bug bounty hunter and Detectify Crowdsource hacker

## Check out more content

Why picking targets is so important Many ethical hackers struggle because they are hacking the “wrong” types of targets for them. This is especially true …

December 07, 2022

You will find a common pattern if you read blog posts or watch interviews with some of today’s top ethical hackers. When asked if coding …

November 30, 2022

Docker is an open-source platform that allows you to develop, deploy, and manage multiple applications across one operating system

November 21, 2022

Approaching a target to hack can feel like climbing a mountain. You may face large scopes, confusing applications, complex user hierarchies…the list goes on. The …

October 28, 2022