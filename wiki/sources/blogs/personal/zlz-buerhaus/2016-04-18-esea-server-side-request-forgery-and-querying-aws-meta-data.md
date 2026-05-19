---
source: zlz-buerhaus
source_url: https://buer.haus/2016/04/18/esea-server-side-request-forgery-and-querying-aws-meta-data/
title: "ESEA Server-Side Request Forgery and Querying AWS Meta Data | ziot"
---

[< Back](https://buer.haus/)

![esea](https://buer.haus/wp-content/uploads/2016/04/esea.png)

For anyone familiar with the Counter-Strike competitive scene, you know about [ESEA](https://play.esea.net/). They just recently launched a [bounty program](https://play.esea.net/index.php?s=content&d=bugbounty) that puts their website, game client, and game servers in scope for security research.

I spent a night taking a look over the website and found a few vulnerabilities. The most interesting discovery was a Server-Side Request Forgery vulnerability. Using a cool trick that [Ben Sadeghipour (@NahamSec)](https://twitter.com/NahamSec) showed me, I was able to pull private information from ESEA's AWS metadata.

The first thing I did with ESEA was perform initial recon by Google dorking my way through all the endpoints on their play.esea.net website. As an example, go to Google.com and search for this:

```
site:https://play.esea.net/ ext:php
```

There was one endpoint that caught my eye:

```
https://play.esea.net/global/media_preview.php?url=
```

It looks like an endpoint for loading external images and displaying it back to the client. That means there is a good chance they are taking user input (url param), loading the response content, and rendering it back to the user.

I tried a typical attack of supplying my own server and checked my access logs to see if they loaded it.

```
https://play.esea.net/global/media_preview.php?url=http://ziot.org/
```

No luck.

Looking through the Google search results again, I realized that all the results were for images. It makes sense, right? The file's name is "media\_preview", so we can make an assumption this was built specifically for rendering only images. We can also guess that they may have implemented some form of URL/file validation to prevent file inclusion or rendering dangerous URLs.

Next, I tried to load two different image endpoints to see if I could load any image and also determine if they were whitelisting domains.

First up, my go-to remote image (Google logo):

```
https://play.esea.net/global/media_preview.php?url=http://www.google.com/images/logo.png
```

It worked!

Next, try it on my own server:

```
https://play.esea.net/global/media_preview.php?url=http://ziot.org/1.png
```

It works! So we at least know we can make the server render files from a server that I control.

My initial guess was that it's checking file extensions and maybe going a bit farther by validating the file type on their server. The first thing to check is file extension. Some typical tricks in the past have been null-byte (%00), additional forward slashes, and question marks. We can only guess what they are using to parse file extension from the URL. It could be something fairly secure such as Python's urlparse (not likely, they're using PHP) or they might just be checking for text after the last . in the URL.

https://play.esea.net/global/media\_preview.php?url=http://ziot.org/?.png

[![img1](https://buer.haus/wp-content/uploads/2016/04/img1-300x168.png)](https://buer.haus/wp-content/uploads/2016/04/img1.png)

Cool, it loads the entirety of the contents of the URL you give it. Now we know it's not restricted to just image files. We can bypass their extension check by putting it after a question mark making it a request variable.

As a researcher, a few things should come to mind at this point. There's definitely server-side request forgery here, but how limited is it? Can I call other protocols such as file:// or php:// and get local file contents? Is it restricted to http? Are they blacklisting domains?

The first obvious thing to demonstrate is that this is vulnerable to XSS. We can force it to load an html file with a JavaScript payload. Because it's play.esea.net delivering the content and it's not in an iframe or anything, it'll execute within the context of esea's domain.

[![img2](https://buer.haus/wp-content/uploads/2016/04/img2-300x207.png)](https://buer.haus/wp-content/uploads/2016/04/img2.png)

The next thing we want to try is other protocols. Here are a few things I tried, but I didn't have any success with them:

- https://play.esea.net/global/media\_preview.php?url=file://\\etc\\passwd?.png
- https://play.esea.net/global/media\_preview.php?url=php://filter/resource=http://www.mrzioto.com?.png
- A couple other wrappers specific to PHP: http://php.net/manual/en/wrappers.php

I made an assumption that this was restricted to http. I talked to NahamSec trying to get ideas for any SSRF/file inclusion tricks I may have forgotten about. He showed me a cool trick that he learned about AWS instances. Any AWS instance has the ability to query an IP address and pull metadata related to that AWS instance and some information about the AWS account that owns it. Just my luck, ESEA is hosting their website with AWS!

http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html

By querying http://169.254.169.254/ you are able to pull information about the AWS instance such as the private address, hostname, public keys, subnet ids, and more. Probably the most shocking data you can pull is [IAM role secret keys](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html#instance-metadata-security-credentials) giving you API access to that AWS account.

Example:

```
URL: http://169.254.169.254/latest/meta-data/hostname
Response: ec2-203-0-113-25.compute-1.amazonaws.com
```

For obvious reasons, I'm not going to show any examples of this on ESEA because it would contain sensitive data.

I felt this was enough evidence of a high impact issue and decided to stop there.

**Thoughts**

- ESEA is awesome. They've done a great job trying to keep hackers out of CS. I do a lot of offensive security work and I know people who write hacks for video games. I still think you're scum if you cheat in a competitive FPS game.
- The ESEA bounty program probably isn't going to get a lot of attention initially because they're a niche in gaming and not running their bounty program on the popular platforms HackerOne or Bugcrowd. If you want an interesting target with decent payouts that hasn't been hit by the wrath of the bounty hunting community, this is a good target to spend some time on.
- AWS is taking over the world. Seriously, so many companies are using AWS now. I think it's a good time for the security community to dive into AWS and share more knowledge on it.

**Timeline**

- Discovery/Reported: April 11, 2016
- Triaged/Verified: April 12, 2016
- Fixed: April 14, 2016 (Based on email response, I think they had fixed it earlier)
- Rewarded: April 18, 2016 - ($1,000 USD, 1,000 ESEA points, profile badge)

[![reward](https://buer.haus/wp-content/uploads/2016/04/reward-300x70.png)](https://buer.haus/wp-content/uploads/2016/04/reward.png)