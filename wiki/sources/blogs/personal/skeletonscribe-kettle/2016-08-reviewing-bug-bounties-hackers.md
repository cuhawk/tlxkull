---
source: skeletonscribe-kettle
source_url: https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html
title: "Skeleton Scribe: Reviewing bug bounties - a hacker's perspective"
description: "A prospective bug bounty hunter today has very little information on which to base his or her decision about which programs to participate ..."
---

|     |     |     |     |
| --- | --- | --- | --- |
| [Go to Blogger.com](https://www.blogger.com/ "Go to Blogger.com") | |     |     |
| --- | --- |
|  |  | | MoreShare by emailShare with FacebookShare with TwitterReport Abuse | [Create Blog](https://www.blogger.com/onboarding) [Sign In](https://www.blogger.com/) |

# [Skeleton Scribe](http://skeletonscribe.net/)

## Thursday, 11 August 2016

### Reviewing bug bounties - a hacker's perspective

A prospective bug bounty hunter today has very little information on which to base his or her decision about which programs to participate in. There's a dramatic horror story every few months and that's about it. This is unfortunate because bounty hunting is founded on mutual trust; nobody wants to spend hours auditing a target only to find out that the client is disrespectful, incompetent, or likes to avoid paying out. I thought it might be helpful to write up reviews of the different bounty programs and platforms that I've dealt with.

You might be wondering exactly how much bug bounty hunting I've done in order to feel qualified to write this, particularly as I only bother writing up bounties if I [consider them highly notable](http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html). I've been doing this in my spare time for roughly five years - my first bounty from Google was [back in 2011](https://www.google.co.uk/about/appsecurity/hall-of-fame/archive/) and I reported enough issues to [star in their 0x0A list](https://www.nilsjuenemann.de/2012/10/01/googles-0x0a-list/) when it was first created in 2012. Over the years I've also reported a bunch of issues to Mozilla, [a few of which are public](https://bugzilla.mozilla.org/buglist.cgi?emailreporter1=1&list_id=1978661&field0-0-0=bug_status&type0-0-1=equals&field0-0-1=reporter&emailtype1=exact&emailassigned_to1=1&query_format=advanced&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&email1=albinowax%40eml.cc&value0-0-1=albinowax%40eml.cc&type0-0-0=notequals&value0-0-0=UNCONFIRMED) (side note: the [SQLi on addons.mozilla.org](https://bugzilla.mozilla.org/show_bug.cgi?id=622749) is hilarious).  Other activity is visible on [Hacker One](https://hackerone.com/albinowax), [Cobalt](https://cobalt.io/albinowax), [Bugcrowd](https://bugcrowd.com/albinowax), and in a [few](http://blog.portswigger.net/2016/04/adapting-angularjs-payloads-to-exploit.html) blog [posts](http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html). I've received maybe 50 separate bounties in total. I view this as a decent sample.

I’ll try to provide the evidence and reasoning behind my conclusions, particularly when I had a poor experience with a program. Due to trust being critical to the bounty process, if my first experience with a bounty program was bad I would never use it again. So, if I give somewhere a bad review it’s always possible I was just unlucky. If you strongly agree or disagree with any of these reviews, do drop a comment or write up your own experience.

To keep things competitive, I’ve sorted the reviews by how good the overall experience is. Scroll down for the dirt.

### Program Reviews

### [Google](https://www.google.co.uk/about/appsecurity/reward-program/)

Google is consistently a pleasure to work with. They have a highly skilled, responsive and respectful security team, and offer healthy payouts. They also offer to double bounties if you donate them to charity, which is pretty cool. And they sometimes send shiny gifts to their top researchers, and there's the awesome party in Vegas... The only ‘downside’ is that these days, actually finding a decent vulnerability in one of their core products can be tricky relative to other targets.

We do have a disagreement about who bears responsibility for preventing [CSV Injection](http://www.contextis.com/resources/blog/comma-separated-vulnerabilities/) attacks but they're going to change their minds soon so that's ok ;)

##### [Uber (hackerone)](https://hackerone.com/uber)

Uber is my current focus for bounty hunting because their scope is huge, they pay exceptionally well, and they don’t try to wriggle out of paying rewards. My last three bounties from Uber were $3000,  $7500 and $5000 for reflected and stored XSS respectively. As their bounty program is much younger than Google’s, it takes significantly less effort to find decent vulnerabilities in their websites.

Uber’s commitment to putting everything in scope is exceptional - Uber and Bugcrowd both use the same third party to host their documentation, and while Bugcrowd declared their documentation out of scope Uber worked with the third party to keep their documentation in scope. The somewhat amusing result is that if it wasn’t for Uber’s bug bounty program, it would be trivial to get administrative access to https://docs.bugcrowd.com/

That said, I’ve found their triage team a little frustrating at times. For example, I provided [a detailed writeup](https://hackerone.com/reports/125027) clearly explaining how to replicate some reflected XSS, and they responded by asking me submit a video. I get the impression that they sometimes skim read reports and miss critical details such as “It's designed to work in Internet Explorer 11”.

#### [Mozilla](https://www.mozilla.org/en-US/security/web-bug-bounty/)

Mozilla is interesting in that you often get to interact directly with the developers responsible for fixing your vulnerabilities, via bugzilla. This can be a blessing and a curse - it’s important to remember you can always summon the security team to mediate. I did have one bad experience with them early on - I reported a stored XSS bug where I couldn’t provide a poc due to a length limitation, and the developer fixed it within a few hours then argued it wasn’t a security issue. However, other times I’ve been paid $3k for vulnerabilities I thought were pretty lame - they certainly aren’t stingy with payouts.

Mozilla are another example of where diligent bounty scoping improves the security of the entire web ecosystem. While many bounty programs refuse to pay up for exploits in third party code, Mozilla happily pay for any exploits for the Django framework that you can replicate on addons.mozilla.org, and everyone using Django is [undoubtedly more secure as a result](http://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html).

Another benefit of Mozilla is that if you request it, they’re happy to publicly disclose most bugs after they’ve been fixed. I view this as significantly better than being placed in a generic hall of fame, particularly if you’re early in your career - potential employers can see the technical details of your bugs. Overall I enjoy working with Mozilla even if the process isn’t always as slick as Google.

#### [Facebook](https://www.facebook.com/whitehat)

Shortly after their program opened, I reported CSRF via form-action-hijacking to them and got $1,000 on one of their [highly 1337 debit cards](https://scontent-lhr3-1.xx.fbcdn.net/t31.0-8/191170_507010585979839_1399479649_o.jpg) for my troubles. It took quite a few emails before their security team fully understood the vulnerability, but they were cordial the whole time and the vulnerability is pretty esoteric so that’s understandable.

#### [Piwik](https://piwik.org/security/)

As you might expect from a free open source project the bounties aren’t massive - I got $242 for [unauthenticated stored XSS](http://blog.portswigger.net/2016/04/adapting-angularjs-payloads-to-exploit.html) \- but they’re friendly and highly responsive. The main thing to beware of is that although they’ll give public credit, they prefer that critical vulnerability details aren’t disclosed even after patches have been released, to mitigate poor patch uptake.

I don't think this is a great policy, but it helps understand the context behind it. Piwik is the only program where I’ve personally seen clear evidence of black market interest in high quality exploits. I think this is because it’s deployable and widely used - you could probably get a foothold in all sorts of organisations with an exploit for it.

#### [CodePen  (bugcrowd)](https://bugcrowd.com/codepen)

Codepen are the coolest program I’ve dealt with that doesn’t pay cash bounties. I got remote code execution on their site a few times, had a nice chat with them and they graciously agreed to let me disclose the full details [at BlackHat USA last year](http://www.skeletonscribe.net/2015/08/server-side-template-injection.html).

#### [Prezi](https://bugbounty.prezi.com/)

I reported stored XSS on prezi.com to them on April 20th, and they replied within 2 days but didn’t actually confirm it until June 6th which is pretty slow. The reward was $500 and I have yet to be paid but I have confidence it’ll arrive one of these months.

The most notable thing about Prezi’s program is that they  go to extraordinary lengths to prove that they aren’t cheating people by fraudulently marking issues as duplicates, using secret gists on github. It’s cool that they make this effort but I think it’s unnecessary really; if you view a company as dishonest you should stay well clear of their bounty program. There are plenty of other ways they can screw you over if they want to.

#### AwardWallet, Blockchain.info, Zendesk, Informatica, WP-API, Fastmail, unnamed others

I’ve reported issues to them without issue or anything of note happening, other than Zendesk claiming the dubious achievement of awarding me the lowest non-zero bounty I've ever received for XSS - $50, with which I could just about buy lunch out after tax.

#### [Cloudflare (hackerone)](https://hackerone.com/cloudflare)

Their program appears to be under-resourced. I reported an XSS to them on April 16th and they took over two weeks to first respond to it, and still have yet to fix it. This is sadly a frequent occurrence with programs that don’t pay cash bounties. Even if you’re bounty hunting for recognition rather than income, I’d recommend focusing on programs that pay a token cash bounty because at least you can be reasonably sure they take it seriously.

#### [Freelancer.com  (bugcrowd)](https://bugcrowd.com/freelancer)

I reported a fairly serious vulnerability to these guys and they fixed the issue and changed the status to resolved without saying a word. While I admire their efficiency, I've had better interactions with vending machines.

#### [Ebay](http://pages.ebay.com/securitycenter/Researchers.html)

I reported a serious CSRF issue to Ebay several years ago and despite numerous emails back and forth, they failed to understand it. As far as I know the issue remains unpatched to this day.

#### [Dropbox (hackerone)](https://hackerone.com/dropbox)

Dropbox state that they pay $5000 for XSS, so when I reported a vulnerability that could be used to gain read/write access to users’ dropbox folders given a small amount of user interaction, I was a bit puzzled to get $0. The exploit is a bit unusual, so instead of trusting my reasoning you might want to [take a look at the report](https://hackerone.com/reports/139099) and come to your own conclusion. I’m not surprised that they protested when I requested public disclosure of the issue. On the bright side, I found the vulnerability by accident so I only wasted about half an hour on them.

#### [Western Union (bugcrowd)](https://bugcrowd.com/westernunion)

Western Union appears to be a glaring exception to the concept that companies that pay cash bounties take their programs seriously.

I reported two vulnerabilities to them. Both were (in my professional opinion) fairly serious, and distinctly obvious. The first was marked as a duplicate of an issue reported over a year prior. Failing to patch an obvious vulnerability for over a year shows disrespect towards the numerous researchers who inevitably waste their time reporting it. The second received a $100 reward. When a company claims they pay $100-$5000 per vulnerability, I find it somewhat surprising to receive $100 for a bug that could probably be used to steal money.

[Zomato (hackerone)](https://hackerone.com/zomato/)

Zomato have provided my worst bounty experience so far. I generally have low expectations for commercial companies that don't pay cash bounties, but I was still surprised when they refused to reply to my issue, even after I used HackerOne's apparently ineffective 'request remediation' feature.

After 90 days I decided to publicly disclose the issue, only to discover they had silently patched it. I'm still waiting for them to reply to my submission, or mark it as resolved. Here's the entire thrilling report:

[![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhp4I7Uq2ZWOp-abFZdhee-FRbFDIuFP-D3YSZF-v_5ocgJpwR5_unIepJ7E0qrNQ_oWqYLvf9BqZZ_GgtdzclK1JhDfGX32RvJOJ_3m0sgdSV6NBSEQR8QRPN89Xza5jfMrINlp6PDswnu/s400/zomato.PNG)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhp4I7Uq2ZWOp-abFZdhee-FRbFDIuFP-D3YSZF-v_5ocgJpwR5_unIepJ7E0qrNQ_oWqYLvf9BqZZ_GgtdzclK1JhDfGX32RvJOJ_3m0sgdSV6NBSEQR8QRPN89Xza5jfMrINlp6PDswnu/s1600/zomato.PNG)

I wrote up the associated research over at [https://portswigger.net/blog/exploiting-cors-misconfigurations-for-bitcoins-and-bounties](https://portswigger.net/blog/exploiting-cors-misconfigurations-for-bitcoins-and-bounties)

### Platform Reviews

#### [HackerOne platform](https://hackerone.com/)

Of all the bug bounty platforms, HackerOne comes across as the best developed from a hacker’s perspective. I particularly appreciate the heavily integrated support for full disclosure and overall transparency. You can easily identify the payout range of many programs using publicly disclosed vulnerabilities, and spare yourself unpleasant surprises. The reputation/signal system also makes it stand out. Yet another cool hackerone feature I'd like to see in other platforms is that if the hacker requests it, vulnerabilities are automatically disclosed after a fixed time length without the company having to manually approve it.

One problem I've encountered on HackerOne is vendors not noticing reports. I had to use a personal contact to get WP-API to respond to a serious access control bypass, and an issue I reported to BitHunt 6 months ago still hasn't been replied to. I invoked HackerOne's 'request mediation' function on BitHunt and they failed to respond too. Inactive companies should really be clearly marked as such to prevent researchers wasting their time.

I’ve found companies that offer larger bounties are less likely to have this issue - sizeable rewards is a good indicator that the company is actually committed to the bounty program.

#### [Cobalt platform](https://cobalt.io/)

Cobalt (formerly crowdcurity) has a whole bunch of bitcoin related websites which are really fun to hack, although the bounties aren’t the biggest. Regardless of the bounty size, I like the warm fuzzy feeling of knowing I could have stolen a huge number of bitcoins if I felt like it. Unfortunately I can’t name the specific sites, but will be disclosing technical details of many of these vulnerabilities in my " [Exploiting CORS Misconfigurations for Bitcoins and Bounties](https://appsecusa2016.sched.org/event/7tAO/exploiting-cors-misconfigurations-for-bitcoins-and-bounties)" presentation at OWASP AppSecUSA.

Cobalt's platform isn't dripping with as many features as HackerOne's but it does the job. It also lets hackers score bug bounty programs and provide feedback, which is frankly awesome - reputation shouldn't just apply to hackers. I don't know if this is directly related, but on the whole I've had good experiences with programs on Cobalt, and definitely recommend giving them a shout. The main thing to beware of is that payouts can take a while - someone [found a race condition](https://cobalt.io/cobalt/cobalt/reports/587) in the bitcoin withdrawal function and I think they're all manually reviewed now.

[Bugcrowd platform](https://bugcrowd.com/)

After a few poor experiences in a row with programs on Bugcrowd I mostly avoid them and therefore don't have much to say. I think they've been around the longest, and they don't deliver payments in bitcoins (subjecting all non-US users to Paypal’s awful exchange rates), but they evidently put effort into engaging with the community by presenting at conferences and [releasing tools](https://blog.bugcrowd.com/discovering-subdomains).

I’m sure there are good programs on there but I'll leave hunting them down to someone else.

#### About Payouts

Posts on bug bounties are frequently visited by commenters suggesting that the bug hunter could have got more cash by selling the vulnerability on ‘the black market’. My last payout was $5000 from Uber for an issue that took me six hours to find and write up. Do I feel shortchanged? No, and I wouldn’t have felt shortchanged with $500 either. I’m always happy to receive a large payout but I don’t feel entitled to it unless there’s a clear precedent. Could I have used that vulnerability to hijack a bunch of Uber developer accounts and cause well over $30k of carnage? Probably, but why would I want to do that? I honestly hope I won’t feel compelled to revisit this topic later. We’ll see.

#### That was it?

If you believe what some people write, you might conclude that every bug bounty program is out to exploit testers, wriggle out of paying rewards, pretend issues are duplicates and generally acting in bad faith. As you've hopefully gathered by reading this far, this does not reflect my own experience at all, and it would be a shame if this misconception put anyone off bounty hunting. The primary causes of drama seem to be broken expectations about payout size and program scope. Companies can mitigate these by writing clearly defined bounty briefings and encouraging publicly disclosed reports. Hackers can mitigate these by reading the briefs, using available information like publicly disclosed reports to set their expectations, and providing feedback on both good and bad experiences.

Hope that's helpful! Feel free to drop your own reviews in the comments or on your own site.

\- [@albinowax](https://twitter.com/albinowax)

Posted by
[James Kettle](https://www.blogger.com/profile/03270155456684307605 "author profile")
at
[14:28](https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html "permanent link")

[Email This](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5064009220353205757&target=email "Email This") [BlogThis!](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5064009220353205757&target=blog "BlogThis!") [Share to X](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5064009220353205757&target=twitter "Share to X") [Share to Facebook](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5064009220353205757&target=facebook "Share to Facebook") [Share to Pinterest](https://www.blogger.com/share-post.g?blogID=8601133831815091251&postID=5064009220353205757&target=pinterest "Share to Pinterest")

#### 4 comments:

1. ![](https://resources.blogblog.com/img/blank.gif)



[yaworsk](https://twitter.com/yaworsk)[11 August 2016 at 18:59](https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html?showComment=1470938358585#c4707716222540102892)



Hey James,

just wanted to reiterate my thanks for the article, really appreciate the insights! I reached out on Twitter about your thoughts on Cobalt.io taking a percentage from the bounty hunter, which sparked a mini conversation between you, myself, Jobert Abma and Mongo.



My original question was how do you feel about Cobalt taking a percentage of bounties paid from a researcher. I agree with your response that taking a percentage is fine as long as the platforms provide value and there is enough left over for the hackers. You also flagged that HackerOne collects 20% of the bounty paid which Jobert clarified is on top of the bounty paid to the hacker (i.e., $500 bounty paid to a hacker is taken home by that hacker, HackerOne then charges the program $100, or 20%).



To that end, either way, bug bounty platforms are collecting money from the programs / sites who are inviting hackers (i.e., Uber, Dropbox Codepen, etc) which arguably would go into the hands of hackers if they didn't. The difference between the approaches is where that money comes from (i.e., bounty paid or additional charge to the program) and how that is perceived. Now, that said, without the platforms, it's likely there would not be as many bounty programs for people to work on. This isn't meant to imply programs are hurting hackers. I think they are a fundamental piece of the broader bug bounty ecosystem.



Additionally, Mongo did suggest the possibility of alternatives to a percentage charged. To that, Jobert made a great point that that process incentivizes HackerOne to support and encourage the hacking community. However, in my opinion, that might be a bit of a slippery slope as, if it were a flat fee and hackers took home more, that additional money earned would also incentivize hackers to improve/learn/etc.



In contrast, I think the argument for maintaining a percentage earned by HackerOne is the value added to the community. Lowering the 20% or competing on fees may encourage a race to the bottom among platforms, which I think would have more severe, negative impacts on the bounty ecosystem that hackers sharing some of the revenue.



Anyways, hope others find this convo as interesting as I did. Additional thanks to Mongo / Jobert for a thought provoking convo. If I got any of it wrong, would be open to corrections :)



pete





Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/4707716222540102892)



Replies



![](https://resources.blogblog.com/img/blank.gif)



[Morty](https://twitter.com/morty_albanna)[12 August 2016 at 18:02](https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html?showComment=1471021378115#c8474582641362315755)



Hi, great follow up...in my opinion given that the company managed the program itself it will then have some overhead to manage the program, maintain contact with community for reporting and payouts, provide the platform to do that and hence they might spend more than the 20% charged by the platform. Each company has a budget when launching bug bounties so what they award to the security researchers + running costs is considered. Indeed there might be some cases where companies are excellent in managing the bug bounty program and they save money which would go in the hands of the security researchers but I think the most likely scenario that they will hire in-house staff and invest in infrastructure which is more costy.

So in conclusion, until we get to the point where there is enough maturity in this field, the current approach is the most plausible approach to maintain engagement for security researchers, platforms, and vendors.



Morty

[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8474582641362315755)



Replies







Reply





Reply

2. ![](https://www.blogger.com/img/blogger_logo_round_35.png)



[fREW](https://www.blogger.com/profile/13153816435895384947)[14 August 2016 at 06:17](https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html?showComment=1471151828762#c8950198135156418940)



I work at ZipRecruiter and we use HackerOne. As one of the people who receives vulnerability reports, I can say that maybe the reason HackerOne companies are sometimes black holes is that everything is done by email, and EVERY EVENT (comment, change in status, new report, etc) creates a new email, which ends up meaning they get filtered or ignored. Just my experience.

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/8950198135156418940)



Replies







Reply

3. ![](https://resources.blogblog.com/img/blank.gif)



Anonymous[3 March 2018 at 05:45](https://www.skeletonscribe.net/2016/08/reviewing-bug-bounties-hackers.html?showComment=1520055932516#c2302064375344833003)



Just saying thanks wouldn’t just be enough, for the fantastic fluency in your writing.

Reply[Delete](https://www.blogger.com/comment/delete/8601133831815091251/2302064375344833003)



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

[Newer Post](https://www.skeletonscribe.net/2017/04/abusing-owasp.html "Newer Post")[Older Post](https://www.skeletonscribe.net/2016/04/exploiting-uber-and-piwik-with-adapted.html "Older Post")[Home](https://www.skeletonscribe.net/)

Subscribe to:
[Post Comments (Atom)](https://www.skeletonscribe.net/feeds/5064009220353205757/comments/default)

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