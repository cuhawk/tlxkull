---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/
title: "Hacking Jenkins Part 1 - Play with Dynamic Routing | Orange Tsai"
author: "Orange Tsai"
published: 2019-01-15T16:00:00.000Z
description: "📌 [ 繁體中文 | English ] In software engineering, the Continuous Integration and Continuous Delivery is a best practice for developers to reduce routine works. In the CI/CD, the most well-known to"
---

* * *

📌 \[ [繁體中文](https://devco.re/blog/2019/01/16/hacking-Jenkins-part1-play-with-dynamic-routing/) \| [English](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/#) \]

![preview](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/efb3e254bd8bee78-01.jpg)

* * *

In software engineering, the [Continuous Integration](https://en.wikipedia.org/wiki/Continuous_integration) and [Continuous Delivery](https://en.wikipedia.org/wiki/Continuous_delivery) is a best practice for developers to reduce routine works. In the CI/CD, the most well-known tool is Jenkins. Due to its ease of use, awesome Pipeline system and integration of Container, Jenkins is also the most widely used CI/CD application in the world. According to the [JVM Ecosystem Report](https://snyk.io/blog/jvm-ecosystem-report-2018-tools) by Snyk in 2018, Jenkins held about 60% market share on the survey of CI/CD server.

For Red Teamers, Jenkins is also the battlefield that every hacker would like to control. If someone takes control of the Jenkins server, he can gain amounts of source code and credential, or even control the Jenkins node! In our [DEVCORE](https://devco.re/) Red Team cases, there are also several cases that compromised whole the corporation just from a Jenkins server as the entry point!

This article is mainly about a brief security review on Jenkins in the last year. During this review, we found 7 vulnerabilities including:

- [CVE-2018-1999002 - Arbitrary file read vulnerability](https://jenkins.io/security/advisory/2018-07-18/#SECURITY-914)
- [CVE-2018-1000600 - CSRF and missing permission checks in GitHub Plugin](https://jenkins.io/security/advisory/2018-06-25/#SECURITY-915)
- [CVE-2018-1999046 - Unauthorized users could access agent logs](https://jenkins.io/security/advisory/2018-08-15/#SECURITY-1071)
- [CVE-2018-1000861 - Code execution through crafted URLs](https://jenkins.io/security/advisory/2018-12-05/#SECURITY-595)
- [CVE-2019-1003000 - Sandbox Bypass in Script Security and Pipeline Plugins](https://jenkins.io/security/advisory/2019-01-08/#jenkins-security-advisory-2019-01-08)
- [CVE-2019-1003001 - Sandbox Bypass in Script Security and Pipeline Plugins](https://jenkins.io/security/advisory/2019-01-08/#jenkins-security-advisory-2019-01-08)
- [CVE-2019-1003002 - Sandbox Bypass in Script Security and Pipeline Plugins](https://jenkins.io/security/advisory/2019-01-08/#jenkins-security-advisory-2019-01-08)

Among them, the more discussed one is the vulnerability CVE-2018-1999002. This is an arbitrary file read vulnerability through an unusual attack vector! Tencent YunDing security lab has written a [detailed advisory](https://cloud.tencent.com/developer/article/1165414) about that, and also demonstrated how to exploit this vulnerability from arbitrary file reading to RCE on a real Jenkins site which found from [Shodan](https://www.shodan.io/search?query=jenkins)!

However, we are not going to discuss that in this blogs post. Instead, this post is about another vulnerability found while digging into Stapler framework in order to find a way to bypass the least privilege requirement `ANONYMOUS_READ=True` of CVE-2018-1999002! If you merely take a look at the advisory description, you may be curious – Is it reality to gain code execution with just a crafted URL?

From my own perspective, this vulnerability is just an Access Control List(ACL) bypass, but because this is a problem of the architecture rather than a single program, there are various ways to exploit this bug! In order to pay off the design debt, Jenkins team also takes lots of efforts (patches in [Jenkins side](https://github.com/jenkinsci/jenkins/commit/47f38d714c99e1841fb737ad1005618eb26ed852) and [Stapler side](https://github.com/stapler/stapler/commit/28e8eba822a0df9dcd64d20eb63d8ab5f6ee2980)) to fix that. The patch not only introduces a new routing blacklist and whitelist but also extends the original [Service Provider Interface (SPI)](https://wiki.jenkins.io/display/JENKINS/Plugins+affected+by+the+SECURITY-595+fix) to protect Jenkins’ routing. Now let’s figure out why Jenkins need to make such a huge code modification!

# [Review Scope](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#Review-Scope "Review Scope") Review Scope

This is not a complete code review (An overall security review takes lots of time…), so this review just aims at high impact bugs. The review scope includes:

- Jenkins Core
- Stapler Web Framework
- Suggested Plugins

During the installation, Jenkins asks whether you want to install suggested plugins such as Git, GitHub, SVN and Pipeline. Basically, most people choose yes, or they will get an inconvenient and hard-to-use Jenkins.

![](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/46396887771084cd-02.png)

![](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/2d0578459d99d63d-03.png)

# [Privilege Levels](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#Privilege-Levels "Privilege Levels") Privilege Levels

Because the vulnerability is an ACL bypass, we need to introduce the privilege level in Jenkins first! In Jenkins, there are different kinds of ACL roles, Jenkins even has a specialized plugin [Matrix Authorization Strategy Plugin](https://plugins.jenkins.io/matrix-auth)(also in the suggested plugin list) to configure the detailed permission per project. From an attacker’s view, we roughly classify the ACL into 3 types:

## [1. Full Access](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#1-Full-Access "1. Full Access") 1\. Full Access

You can fully control Jenkins. Once the attacker gets this permission, he can execute arbitrary Groovy code via [Script Console](http://jenkins.local/script)!

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>print "uname -a".execute().text<br>``` |

This is the most hacker-friendly scenario, but it’s hard to see this configuration publicly now due to the increase of security awareness and lots of bots scanning all the IPv4.

## [2. Read-only Mode](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#2-Read-only-Mode "2. Read-only Mode") 2\. Read-only Mode

This can be enabled from the [Configure Global Security](http://jenkins.local/configureSecurity) and check the radio box:

> Allow anonymous read access

Under this mode, all contents are visible and readable. Such as agent logs and job/node information. For attackers, the best benefit of this mode is the accessibility of a bunch of private source codes! However, the attacker cannot do anything further or execute Groovy scripts!

Although this is not the default setting, for DevOps, they may still open this option for automations. According to a little survey on [Shodan](https://www.shodan.io/search?query=jenkins), there are about 12% servers enabled this mode! We will call this mode `ANONYMOUS_READ=True` in the following sections.

## [3. Authenticated Mode](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#3-Authenticated-Mode "3. Authenticated Mode") 3\. Authenticated Mode

This is the default mode. Without a valid credential, you can’t see any information! We will use `ANONYMOUS_READ=False` to call this mode in following sections.

# [Vulnerability Analysis](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#Vulnerability-Analysis "Vulnerability Analysis") Vulnerability Analysis

To explain this vulnerability, we will start with Jenkins’ [Dynamic Routing](https://jenkins.io/doc/developer/handling-requests/routing/). In order to provide developers more flexibilities, Jenkins uses a naming convention to resolve the URL and invoke the method dynamically.

Jenkins first tokenizes all the URL by `/`, and begins from [jenkins.model.Jenkins](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/jenkins/model/Jenkins.java) as the entry point to match the token one by one. If the token matches (1)public class member or (2)public class method correspond to following naming conventions, Jenkins invokes recursively!

> 01. get()
> 02. get(String)
> 03. get(Int)
> 04. get(Long)
> 05. get(StaplerRequest)
> 06. getDynamic(String, …)
> 07. doDynamic(…)
> 08. do(…)
> 09. js(…)
> 10. Class method with @WebMethod annotation
> 11. Class method with @JavaScriptMethod annotation

It looks like Jenkins provides developers a lot of flexibility. However, too much freedom is not always a good thing. There are two problems based on this naming convention!

## [1. Everything is the Subclass of java.lang.Object](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#1-Everything-is-the-Subclass-of-java-lang-Object "1. Everything is the Subclass of java.lang.Object") 1\. Everything is the Subclass of `java.lang.Object`

In Java, everything is a subclass of [java.lang.Object](https://docs.oracle.com/javase/7/docs/api/java/lang/Object.html). Therefore, all objects must exist the method - `getClass()`, and the name of `getClass()` just matches the naming convention rule `#1`! So the method `getClass()` can be also invoked during Jenkins dynamic routing!

## [2. Whitelist Bypass](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#2-Whitelist-Bypass "2. Whitelist Bypass") 2\. Whitelist Bypass

As mentioned before, the biggest difference between `ANONYMOUS_READ=True` and `ANONYMOUS_READ=False` is, if the flag set to `False`, the entry point will do one more check in [jenkins.model.Jenkins#getTarget()](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/jenkins/model/Jenkins.java#L4682). The check is a white-list based URL prefix check and here is the list:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>``` | ```<br>private static final ImmutableSet<String> ALWAYS_READABLE_PATHS = ImmutableSet.of(<br>"/login",<br>"/logout",<br>"/accessDenied",<br>"/adjuncts/",<br>"/error",<br>"/oops",<br>"/signup",<br>"/tcpSlaveAgentListener",<br>"/federatedLoginService/",<br>"/securityRealm",<br>"/instance-identity"<br>);<br>``` |

That means you are restricted to those entrances, but if you can find a cross reference from the white-list entrance jump to other objects, you can still bypass this URL prefix check! It seems a little bit hard to understand. Let’s give a simple example to demonstrate the dynamic routing:

> http://jenkin.local/adjuncts/whatever/class/classLoader/resource/index.jsp/content

The above URL will invoke following methods in sequence!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>jenkins.model.Jenkins.getAdjuncts("whatever") <br>.getClass()<br>.getClassLoader()<br>.getResource("index.jsp")<br>.getContent()<br>``` |

This execution chain seems smooth, but sadly, it can not retrieve the result. Therefore, this is not a potential risk, but it’s still a good case to understand the mechanism!

Once we realize the principle, the remaining part is like solving a maze. [jenkins.model.Jenkins](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/jenkins/model/Jenkins.java) is the entry point. Every member in this object can references to a new object, so our work is to chain the object layer by layer till the exit door, that is, the dangerous method invocation!

By the way, the saddest thing is that this vulnerability cannot invoke the SETTER, otherwise this would definitely be another interesting classLoader manipulation bug just like [Struts2 RCE](https://cwiki.apache.org/confluence/display/WW/S2-020) and [Spring Framework RCE](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2010-1622)!!

# [How to Exploit?](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#How-to-Exploit "How to Exploit?") How to Exploit?

How to exploit? In brief, the whole thing this bug can achieve is to use cross reference objects to bypass ACL policy. To leverage it, we need to find a proper gadget so that we can invoke the object we prefer in this object-forest more conveniently! Here we choose the gadget:

> /securityRealm/user/\[username\]/descriptorByName/\[descriptor\_name\]/

The gadget will invoke following methods sequencely.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br>jenkins.model.Jenkins.getSecurityRealm()<br>.getUser([username])<br>.getDescriptorByName([descriptor_name])<br>``` |

In Jenkins, all configurable objects will extend the type [hudson.model.Descriptor](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/Descriptor.java). And, any class who extends the `Descriptor` type is accessible by method [hudson.model.DescriptorByNameOwner#getDescriptorByName(String)](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/DescriptorByNameOwner.java#L51). In general, there are totally about 500 class types can be accessed! But due to the architecture of Jenkins. Most developers will check the permission before the dangerous action again. So even we can find a object reference to the [Script Console](http://jenkins.local/script), without the permission `Jenkins.RUN_SCRIPTS`, we still can’t do anything :(

Even so, this vulnerability can still be considered as a stepping stone to bypass the first ACL restriction and to chain other bugs. We will show 3 vulnerability-chains as our case study! (Although we just show 3 cases, there are more than 3! If you are intersted, it’s highly recommended to find others by yourself :P )

P.S. It should be noted that in the method `getUser([username])`, it will invoke `getOrCreateById(...)` with `create` flag set to `True`. This result to the creation of a temporary user in memory(which will be listed in the user list but can’t sign in). Although it’s harmless, it is still recognized as a security issue in [SECURITY-1128](https://jenkins.io/security/advisory/2018-10-10/).

## [1. Pre-auth User Information Leakage](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#1-Pre-auth-User-Information-Leakage "1. Pre-auth User Information Leakage") 1\. Pre-auth User Information Leakage

While testing Jenkins, it’s a common scenario that you want to perform a brute-force attack but you don’t know which account you can try(a valid credential can read the source at least so it’s worth to be the first attempt).

In this situation, this vulnerability is useful!

Due to the lack of permission check on search functionality. By modifying the `keyword` from a to z, an attacker can list all users on Jenkins!

### [PoC:](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#PoC "PoC:") PoC:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>http://jenkins.local/securityRealm/user/admin/search/index?q=[keyword]<br>``` |

![](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/e5a65f6f70c9919d-04.png)

Also, this vulnerability can be also chained with [SECURITY-514](https://jenkins.io/security/advisory/2017-10-11/#user-remote-api-disclosed-users-email-addresses) which reported by `Ananthapadmanabhan S R` to leak user’s email address! Such as:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>http://jenkins.local/securityRealm/user/admin/api/xml<br>``` |

## [2. Chained with CVE-2018-1000600 to a Pre-auth Fully-responded SSRF](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#2-Chained-with-CVE-2018-1000600-to-a-Pre-auth-Fully-responded-SSRF "2. Chained with CVE-2018-1000600 to a Pre-auth Fully-responded SSRF") 2\. Chained with CVE-2018-1000600 to a Pre-auth Fully-responded SSRF

The next bug is [CVE-2018-1000600](https://jenkins.io/security/advisory/2018-06-25/#SECURITY-915), this bug is reported by [Orange Tsai](https://twitter.com/orange_8361)(Yes, it’s me :P). About this vulnerability, the official description is:

> CSRF vulnerability and missing permission checks in GitHub Plugin allowed capturing credentials

It can extract any stored credentials with known credentials ID in Jenkins. But the credentials ID is a random UUID if there is no user-supplied value provided. So it seems impossible to exploit this?(Or if someone know how to obtain credentials ID, please tell me!)

Although it can’t extract any credentials without known credentials ID, there is still another attack primitive - a fully-response SSRF! We all know how hard it is to exploit a Blind SSRF, so that’s why a fully-responded SSRF is so valuable!

### [PoC:](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#PoC-1 "PoC:") PoC:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>http://jenkins.local/securityRealm/user/admin/descriptorByName/org.jenkinsci.plugins.github.config.GitHubTokenCredentialsCreator/createTokenByPassword<br>?apiUrl=http://169.254.169.254/%23<br>&login=orange<br>&password=tsai<br>``` |

![](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/23238cd39a889cf1-05.png)

## [3. Pre-auth Remote Code Execution](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#3-Pre-auth-Remote-Code-Execution "3. Pre-auth Remote Code Execution") 3\. Pre-auth Remote Code Execution

> PLEASE DON’T BULLSHIT, WHERE IS THE RCE!!!

In order to maximize the impact, I also find an **INTERESTING** remote code execution can be chained with this vulnerability to a well-deserved pre-auth RCE! But it’s still on the responsible disclosure process. Please wait and see the Part 2! (Will be published on Mid-February :P)

# [TODO](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#TODO "TODO") TODO

Here is my todo list which can make this vulnerability more perfect. If you find any of them please tell me, really appreciate it :P

- Get the `Plugin` object reference under `ANONYMOUS_READ=False`. If this can be done, it can bypass the ACL restriction of [CVE-2018-1999002](https://jenkins.io/security/advisory/2018-07-18/#SECURITY-914) and [CVE-2018-6356](https://jenkins.io/security/advisory/2018-02-14/#SECURITY-705) to a indeed pre-auth arbitrary file reading!
- Find another gadget to invoke the method `getDescriptorByName(String)` under `ANONYMOUS_READ=False`. In order to fix [SECURITY-672](https://jenkins.io/security/advisory/2018-08-15/#SECURITY-672), Jenkins applies a [check](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/User.java#L1026) on [hudson.model.User](https://github.com/jenkinsci/jenkins/blob/master/core/src/main/java/hudson/model/User.java) to ensure the least privilege `Jenkins.READ`. So the original gadget will fail after Jenkins version 2.138.

# [Acknowledgement](https://blog.orange.tw/posts/2019-01-hacking-jenkins-part-1-play-with-dynamic-routing/\#Acknowledgement "Acknowledgement") Acknowledgement

Thanks Jenkins Security team especially Daniel Beck for the coordination and bug fixing! Here is the brief timeline:

- May 30, 2018 - Report vulnerabilities to Jenkins
- Jun 15, 2018 - Jenkins patched the bug and assigned CVE-2018-1000600
- Jul 18, 2018 - Jenkins patched the bug and assigned CVE-2018-1999002
- Aug 15, 2018 - Jenkins patched the bug and assigned CVE-2018-1999046
- Dec 05, 2018 - Jenkins patched the bug and assigned CVE-2018-1000861
- Dec 20, 2018 - Report Groovy vulnerability to Jenkins
- Jan 08, 2019 - Jenkins patched Groovy vulnerability and assigned CVE-2019-1003000, CVE-2019-1003001 and CVE-2019-1003002