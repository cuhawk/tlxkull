---
source: bughunters
source_url: https://bughunters.google.com/blog/the-great-google-password-heist-15-years-of-hacking-passwords-to-test-our-security-and-build-team-culture
title: "The Great Google Password Heist: 15 years of hacking passwords to test our security (and build team culture!) - Google Bug Hunters"
description: "The Leaving Tradition in Google's security team, which could be described as a type of small-scale offensive security exercise, is a great (and fun) example of team culture. Curious? See this blog post for details."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/the-great-google-password-heist-15-years-of-hacking-passwords-to-test-our-security-and-build-team-culture#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# The Great Google Password Heist: 15 years of hacking passwords to test our security (and build team culture!)

![](https://storage.googleapis.com/bughunters-article-images/blogs/ail.jpg)

Alexis Imperial-Legrand

Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/dworken.jpg)

David Dworken

Software Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/scrinzi.jpg)

Federico Scrinzi

Software Engineer

Published: Dec 4, 2024

Security Engineering

[RSS Feed](https://bughunters.google.com/feed/en)

# The Great Google Password Heist: 15 years of hacking passwords to test our security (and build team culture!)

At Google, we take security very seriously and we continuously invest in efforts
to assess and to improve our security. This includes a wide variety of research
and engineering to ensure Google's infrastructure is hardened against all types
of attackers. Among other things, we routinely test our security posture through
[Red Team exercises](https://blog.google/technology/safety-security/meet-the-team-responsible-for-hacking-google/)
that aim to simulate external adversaries who are hacking Google. These
offensive security exercises allow us to scrutinize our detection and response
capabilities and identify gaps in our defenses to motivate future security
engineering work. They are meticulously planned out to simulate real threat
actors as closely as possible. To accomplish predefined goals, they often take
months to execute.

## Leaving Traditions

Google's security teams strive to be agile and impact focused, and have some fun
along the way. A key part of our culture that complements day-to-day engineering
work is our _Leaving Tradition_, which could be described as a type of
small-scale offensive security exercise. The tradition is that when a security
engineer transfers to a different team or location, or leaves Google, they can
_opt-in_ to participate in an exercise where their coworkers will attempt to get
their hands on their password. To add to the fun, before opting in, they
typically change their password to something fun to discover and memorable.

> A quick note about internal passwords: At Google all logins
> [require multi-factor authentication using a security key](https://static.googleusercontent.com/media/publicpolicy.google/en//resources/google_commitment_secure_by_design_overview.pdf#page=5).
> This greatly mitigates the risk posed by a misappropriated password, as a
> password alone is never enough to fully compromise an account—a key security
> benefit of adopting multi-factor authentication. We also take precautions to
> ensure that the victim is notified to change their password right after the
> exercise goal is reached and each exercise is coordinated with the Detection &
> Response teams.

These lightweight offensive security exercises have a number of benefits:

1. Leaving Traditions are generally executed by direct colleagues of the
leaving Googler, typically a small group of Google engineers who may not
normally work on offensive security, allowing engineers to explore
vulnerabilities outside of their day-to-day job duties, but related to their
specific domain of expertise. This fresh perspective often leads to novel
discoveries.

2. Leaving Traditions are great avenues for exploration and research. For
example, sometimes it may not be clear whether or not a newly discovered bug
actually has a real-life security impact. What better way to verify security
impact than by building an exploit and demonstrating its relevance by
grabbing a fellow Googler's password? At that point, it's obvious that this
is a security-relevant vulnerability that needs to be fixed! This can result
in anything from a small tactical patch to a long-term remediation project,
ensuring that the vulnerability is appropriately mitigated.

3. Leaving Traditions build a fun team culture! If a Leaving Tradition
retrieves a departing Googler's password, they are notified of this—and
given a lasting memento—by gifting them an object with their password
engraved on it. Given that the tradition started in Zurich, the obvious
choice for the gift is a Swiss Army Knife! But Googlers are creative, and
throughout the years some Leaving Tradition gifts included self-made
artwork, swords, boomerangs for fellow engineers in Australia, and many
other custom gifts—giving something that is individually special makes it
that much more memorable!
![](https://storage.googleapis.com/bughunters-article-images/blogs/leaving-tradition_01.png)
_Fig. 1. The symbol of the Leaving Tradition: A Swiss Army Knife_


Of course, all of this is done very carefully to ensure it doesn't negatively
impact Google's security or reliability. Leaving Traditions have a strict set of
rules to ensure that this practice remains a safe way to identify opportunities
to improve defenses, and for engineers to demonstrate their offensive security
skills. These rules are aligned with best practices and procedures in place for
all offensive security exercises at Google This includes:

1. Strict rules about targeting – It is only allowed to target Googlers that
have explicitly opted in to the Leaving Tradition. No opt-in, no hacking! No
other personal information of the targeted Googler apart from their password
can be accessed as part of the exercise.

2. Strict rules about documentation – Just like in our Red Team exercises,
everything done as part of a Leaving Tradition is documented and shared with
the relevant Detection & Response teams. This helps keep things safe, and
ensures that these exercises help improve our detection capabilities.

3. Supervision – A group of senior engineers with experience in offensive
security helps oversee the program and ensures it is performed in a safe and
respectful manner.


## Leaving Tradition Tales

One of our personal favorite parts of Leaving Traditions are the “Tales of
Ownages”. Not only do we hack each other to make Google more secure, but after
the identified vulnerabilities are fixed, we also share all of the details about
the exploit internally! These reports tell fascinating stories of clever
engineers exploiting subtle gaps to get their hands on each other's passwords.
This ensures that we all can benefit from the high educational value of these
security exercises: whether or not you're working in security, these stories
help ignite a flame for security awareness in every engineer, and make everyone
a better (security-minded) engineer.

The first exercises started 15 years ago, in 2009. Initially, exploitation
attempts were mostly based on social engineering, physical keyloggers, or
cameras hidden in the ceiling above the keyboard. But these quickly got boring!
Soon, the techniques evolved into zero-day hunting in Google's infrastructure.
The results proved fruitful, complementing the security research work that is
done every day to keep Google and our users safe and to mitigate serious
vulnerabilities. To summarize a few attack vectors used in Leaving Traditions
and the results that came out of them:

1. USB keyloggers can be inserted in between someone's keyboard and their
computer, and log every keystroke to internal storage.

→ Result: Deployed defenses to auto-block new USB devices the first time
they're plugged into a computer.

2. HTTP downgrade attacks to serve phishing pages on http://

→ Result: Accelerated the roll-out of
[HSTS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)
along with many other efforts to spur the adoption of TLS.

3. Physically accessing a workstation to backdoor the OS image

→ Result: Hardened Secure Boot to ensure that even physical attackers can't
put a backdoor into a workstation.

4. Exploiting N-day vulnerabilities, that have already been patched in
browsers, to attack users with out-of-date browsers.

→ Result: Centrally enforce strict policies to ensure all Googlers use
up-to-date browsers, and accelerate Chrome's patch cycle to reduce the
window of opportunity for attackers leveraging N-day vulnerabilities.

5. Attacking source code storage and review tools to bypass code review
requirements

→ Result: Harden code review tooling to fix the exploited vulnerabilities.


These are just a few of the attack vectors from 15 years of Leaving Traditions.
But even just from these examples, we can conclusively say that Leaving
Traditions have made Google more secure.

## Conclusion

All of what we described in this post is why Leaving Traditions are a cherished
part of Google's security culture and something we believe is valuable to share
with the industry. They enable us to:

1. Discover and fix critical vulnerabilities, making Google more secure
2. Demonstrate the importance of multi-factor authentication as a key defense,
ensuring that getting hold of a password isn't enough to compromise an
account
3. Have some fun with coworkers leaving Google, and give them a lasting memento
of their time at Google

Speaking of lasting mementos, to round off this post, we'd like to share a few
of the more unique Leaving Tradition gifts handed out in the past:

![](https://storage.googleapis.com/bughunters-article-images/blogs/leaving-tradition_02.jpg)

_Fig. 2. A chainsaw presented to our Director, Michal Zalewski (he was moving to_
_Montana and we knew he would need one). Pwned via a Chrome n-day, which_
_reinforced the already well understood need for_
_[reducing the patch gap](https://security.googleblog.com/2023/08/an-update-on-chrome-security-updates.html)._

![](https://storage.googleapis.com/bughunters-article-images/blogs/leaving-tradition_03.jpg)

_Fig. 3. A custom Japanese sword given to our VP of security, Eric Grosse, who_
_left Google in 2017. Pwned via the combination of an XSS and a CSRF_
_vulnerability discovered in an internal service, and fixed afterwards._

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab