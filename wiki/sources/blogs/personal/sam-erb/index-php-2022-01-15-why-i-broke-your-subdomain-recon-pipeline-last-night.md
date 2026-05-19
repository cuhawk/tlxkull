---
source: sam-erb
source_url: https://blog.erbbysam.com/index.php/2022/01/15/why-i-broke-your-subdomain-recon-pipeline-last-night
title: "Why I broke your subdomain recon pipeline last night – blog.erbbysam.com"
---

### (or why tls.bufferover.run is moving from free to free*)

## TLDR

I’m moving [https://tls.bufferover.run/](https://tls.bufferover.run/) to a freemium model as I’ve identified numerous businesses profiting off of my non-commercial free service.

## Background

Over the past few years I have been running a couple of services hosting DNS data sources which have been widely shared and used:

Rapid7 publishes DNS data for public use here: [https://opendata.rapid7.com/](https://opendata.rapid7.com/) (note the license restrictions). I index this monthly when a new public dataset is published and host it to allow for easy lookups. Without this online tool, 1 second lookups can take 10+ minutes to grep over the entire dataset. I wrote about this in more detail here: [https://blog.erbbysam.com/index.php/2019/02/09/dnsgrep/](https://blog.erbbysam.com/index.php/2019/02/09/dnsgrep/)

I created a system to quickly scan all of IPv4 space for TLS certificates and index the DNS values found in the CN and SAN fields. I gave a talk on this at DEFCON 27 PHV: [https://www.youtube.com/watch?v=1pqCqz3JzXE](https://www.youtube.com/watch?v=1pqCqz3JzXE) ([slides](https://github.com/erbbysam/Hunting-Certificates-And-Servers/blob/master/Hunting%20Certificates%20%26%20Servers.pdf))

These two endpoints are very widely used as shown on the graph below:

(this is roughly 20 requests per second over a 30 day period)

## Commercial Use

I host both of these endpoints to give back to the security community that I have benefited so much from. On [https://tls.bufferover.run](https://tls.bufferover.run) I made a simple Terms of Service (TOS) returned with every response:

`"TOS": "Use of this data available on this website is subject to the following terms. By accessing or using this data, you accept these terms of service. The data may not be used: 1) To do anything illegal or in violation of the rights of others, including unlawful access or damage to computers. 2) To facilitate or encourage illegal activity. `

**3) To be resold or repackaged for any commercial offering.**",

Over the past few months I have been alerted to multiple companies reselling access to both of these endpoints or otherwise ignoring license restrictions.

For example, on one website selling a subdomain discovery service linked to other tools:

(the *.bufferover.run endpoints above are pulled in via 3 of the “passive” subdomain finding tools listed)

## What should I do?

I’m left with a choice for [https://tls.bufferover.run](https://tls.bufferover.run) as I own this data and run the service:

- Ignore that others profit from reselling my free work
- Pursue legal action
- Take the service offline
- Create a paid service

I don’t want to take the service offline. I can’t easily pursue legal action (cost-prohibitive and jurisdiction issues). I could continue ignoring this problem but it is getting increasingly annoying with every cloud bill I receive and every new “subdomain discovery” reseller I see advertised online. That leaves option #4.

## Option #4

In order to meet my original goal of giving back to the security community, I am leaving a free endpoint hosted with old data (will vary in age, approximately 90 days… this is still very useful for subdomain discovery). For commercial use and access to the latest scan, I’m going to start charging to:

- Recoup service costs
- Allow commercial use (which is clearly happening already)

**Checkout the options for data access here:**[https://tls.bufferover.run](https://tls.bufferover.run/)

## Epilogue — Who in the industry is handling DNS dataset licenses correctly?

To date, only 2 companies have reached out to me with licensing questions: