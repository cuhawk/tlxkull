---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2011/12/phrack-ebook.html
title: "Skeleton Scribe: Phrack ebook"
description: "I've converted all 25 years of Phrack magazine into an ebook suitable for viewing on e-readers: phrack.mobi (Kindles) phrack.epub (Ot..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Tuesday, 20 December 2011

### Phrack ebook

I've converted all 25 years of [Phrack magazine](http://phrack.org/) into an ebook suitable for viewing on e-readers:

[phrack.mobi](https://docs.google.com/open?id=0B3sIoUHUjjthTDZfSjlSdmdicUE&browserok=true) (Kindles)

[phrack.epub](https://docs.google.com/open?id=0B3sIoUHUjjthaFhSemJuUU4wZ3M&browserok=true) (Other e-readers)

The conversion wasn't perfect; text and code are fine but some of the ascii diagrams have been horribly mangled. I outright stripped base64-encoded tgz/png. This **is** a work in progess; I will update it whenever I feel like some heart-withering text-processing.

If you would like to roll your own version, [download the epub generation code](https://docs.google.com/file/d/0B3sIoUHUjjthZFBDaW54NGloSTA/view) or the [mobi version](https://docs.google.com/open?id=0B3sIoUHUjjthMTJlZDg1ODEtZGY4OC00YzQwLTg2M2EtYjJlMjUwMWMwOGIx). They should run on all \*nix distros with the requisite Perl modules. Both versions actually generate epubs, but the second can be easily converted into a .mobi using [Kindlegen](http://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000234621).

Redistributed with permission. Rights remain with Phrack.org

update #1: I have manually added issue 68 to the download. The generation code should work once Phrack updates p68.tar.gz

update #2: Fixed a zip layout mistake that broke compatibility with Stanza

update #3: [eridius](http://kevin.sb.org/) restructured the .epub so it should genuinely work in all e-readers now.

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[13:57](https://www.skeletonscribe.net/2011/12/phrack-ebook.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5324958918467725635&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5324958918467725635&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5324958918467725635&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5324958918467725635&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5324958918467725635&target=pinterest "Share to Pinterest")

#### 15 comments:

01. ![](https://resources.blogblog.com/img/blank.gif)



    spanish user[16 January 2012 at 16:38](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1326731939301#c2826982705140304997)



    the links aren't working :(

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/2826982705140304997)



    Replies







    Reply

02. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[17 January 2012 at 20:40](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1326832834388#c8632067948920330888)



    Damn, it works fine for me. I appended &browserok=true, maybe that will fix it.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8632067948920330888)



    Replies







    Reply

03. ![](https://resources.blogblog.com/img/blank.gif)



    Eric[28 January 2012 at 03:39](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1327721998581#c7373107217819114844)



    I can't access the files either even after logging in to google.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/7373107217819114844)



    Replies







    Reply

04. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[28 January 2012 at 14:53](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1327762416559#c8346470281868815315)



    I've uploaded the generation code to http://albinowax.users.sourceforge.net/phrackgen.zip



    You should be able to use that to create the book directly.



    Any suggestions for where to upload the mobi/epub to?

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8346470281868815315)



    Replies







    Reply

05. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[14 April 2012 at 22:28](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1334438922887#c2356288298476012640)



    Have you tried out Calibre?

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/2356288298476012640)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[14 April 2012 at 22:31](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1334439118643#c1365272258772725613)



    Yes! This was my original approach. I had to do a fair bit of preprocessing to get calibre to run on it at all, then it ran for 10 hours then crashed :) I don't think it likes the scale.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/1365272258772725613)



    Replies







    Reply





    Reply

06. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[20 April 2012 at 15:02](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1334930530697#c466372983145653311)



    Just like to say thanks for doing this - now have them all on my Kindle, brilliant result! Cheers.

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/466372983145653311)



    Replies







    Reply

07. ![](https://resources.blogblog.com/img/blank.gif)



    [Venture37](http://www.geeklan.co.uk/)[24 April 2012 at 09:23](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1335255808526#c8149567366200664378)



    The epub doesn't work, stanza says 'phrack': Unknown file format for 'phrack': Required container.xml file missing from zip download-2

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8149567366200664378)



    Replies



    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[24 April 2012 at 10:17](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1335259055828#c6443892403260097870)



    Thanks for the report, it should be fixed now.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/6443892403260097870)



    Replies







    Reply

    ![](https://resources.blogblog.com/img/blank.gif)



    [Venture37](http://www.geeklan.co.uk/)[2 May 2012 at 09:47](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1335948440373#c3337463779617955151)



    Thanks for the update, stanza now hangs on opening the epub & eventually crashes out, the crash happens much sooner on ibooks upon opening

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/3337463779617955151)



    Replies







    Reply

    ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [James Kettle](https://www.blogger.com/profile/03270155456684307605)[15 June 2012 at 14:33](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1339767202202#c6209609040397667226)



    Ack. This is probably just caused by the immense size of the ebook. Not much I can do about that other than split it into several smaller ones, which would be less convenient.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/6209609040397667226)



    Replies







    Reply

    ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[30 July 2012 at 20:49](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1343677797532#c6455085965645792202)



    Instead of splitting it into multiple EPUBs, you could try using separate .xhtml files, one per issue, instead of one monolithic .html file. You've already got a separate navPoint for each issue, just make each one of those the start of a new .xhtml file.

    [Delete](https://www.blogger.com/comment/delete/8601133831815091251/6455085965645792202)



    Replies







    Reply





    Reply

08. ![](https://resources.blogblog.com/img/blank.gif)



    [Mike](http://www.thediamondringcompany.co.uk/)[15 August 2012 at 17:13](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1345047194965#c8113312773890246477)



    Works great here :)

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8113312773890246477)



    Replies







    Reply

09. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



    [vmguy](https://www.blogger.com/profile/12145386796858576217)[17 September 2012 at 09:39](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1347871145342#c2718871066385248326)



    Thanks for posting this. epub reader handles it on Win7 without crashing, but many of the chars turn into ice-blocks \[ \]



    http://epubreader.info/



    ( epubreader installer pumps a lot of stuff into Windows ).

    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/2718871066385248326)



    Replies







    Reply

10. ![](https://resources.blogblog.com/img/blank.gif)



    Anonymous[24 July 2013 at 11:58](https://www.skeletonscribe.net/2011/12/phrack-ebook.html?showComment=1374663490749#c3374264361208840634)



    thanks bro



    Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/3374264361208840634)



    Replies







    Reply


Add comment

Post a comment

Comment with your Google Account if you’d like to be able to manage your comments in the future. If you comment anonymously, you won’t be able to edit or delete your comment. [Learn more](https://www.blogger.com/go/anonymouscommentshelp)

![User Avatar](https://resources.blogblog.com/img/anon36.png)

Comment as:

Select profile:

Google Account

Anonymous

Name/URL



Edit

Enter comment

Publish

This site is protected by reCAPTCHA and the Google [privacy policy](https://policies.google.com/privacy) and [Terms of Service](https://policies.google.com/terms) apply.

Load more...

[Newer Post](https://www.skeletonscribe.net/2012/06/x-frame-options-sameorigin-warning.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2011/07/sparse-bruteforce-addon-scanner.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/5324958918467725635/comments/default)

**Who**

- [James Kettle](http://skeletonscribe.net/)

**Contact**

- [@albinowax](https://twitter.com/albinowax)
- xawonibla@gmail.com (personal)

- elttek.semaj@portswigger.net (work)

- albinowax on [freenode](https://webchat.freenode.net/?randomnick=0&channels=#slackers)

## Quality content

- [magic mac's blog](https://www.brokenbrowser.com/)
- [lcamtuf's blog](http://lcamtuf.blogspot.co.uk/)
- [.mario's slides](http://www.slideshare.net/x00mario/presentations)
- [sirdarckcat's blog](https://sirdarckcat.blogspot.co.uk/)
- [irsdl's blog](https://soroush.secproject.com/blog/)
- [Gareth Heyes' blog](http://www.thespanner.co.uk/)
- [kuza's blog](http://kuza55.blogspot.co.uk/)
- [Shared Fuzzer](http://shazzer.co.uk/)
- [HTML5 Security Cheat Sheet](http://html5sec.org/)
- [unexpected theology](http://davidkettle.org.uk/)

## Archive

- [Practical HTTP Host header attacks](https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)
- [Phrack ebook](https://www.skeletonscribe.net/2011/12/phrack-ebook.html)
- [Reviewing bug bounties - a hacker's perspective](https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html)
- [h1-212 CTF Writeup](https://www.skeletonscribe.net/2017/11/h1-212-ctf-writeup.html)
- [Abusing OWASP with 'Insufficient Attack Protection'](https://www.skeletonscribe.net/2017/04/abusing-owasp.html)
- [X-Frame-Options gotcha](https://www.skeletonscribe.net/2012/06/x-frame-options-sameorigin-warning.html)
- [Hackxor hacking game beta](https://www.skeletonscribe.net/2011/02/hackxor-hacking-game-beta.html)
- [Simulating targets for XSS/CSRF attacks in hacking games](https://www.skeletonscribe.net/2011/05/simulating-targets-for-xsscsrf-attacks.html)
- [Sparse Bruteforce Addon Detection](https://www.skeletonscribe.net/2011/07/sparse-bruteforce-addon-scanner.html)
- [Chronofeit Phishing](https://www.skeletonscribe.net/2010/12/chronofeit-phishing.html)

|     |     |
| --- | --- |
|  |  |

|     |     |
| --- | --- |
|  |  |

Powered by [Blogger](https://www.blogger.com/).