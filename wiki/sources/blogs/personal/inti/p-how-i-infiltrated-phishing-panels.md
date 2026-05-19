---
source: inti
source_url: https://inti.io/p/how-i-infiltrated-phishing-panels
title: "How I infiltrated phishing panels targeting European banks and tracked down their operators"
description: "Good phishers clearly aren't always good programmers."
---

# How I infiltrated phishing panels targeting European banks and tracked down their operators

### Good phishers clearly aren't always good programmers.

I live in the most lucrative country for phishing scams in the EU. Every month, millions of euros are lost, and according to recent reporting, nearly two-thirds of complaints to banks are ignored.[1](#footnote-1)

After hearing too many personal stories of hard-working individuals losing their life savings in a matter of minutes, I decided it’s time to take action.

In the past few weeks, I’ve tracked down the scammers responsible for dozens of phishing operations targeting several banks in Europe.

I took down their panels, gathered evidence and hunted down their identities.

Despite knowing who they are and multiple attempts to report them to the respective banks, these folks are still on the loose, and I will need your help bringing them to justice.

**If you are a victim of phishing and recognize some of the phishing panels below, or know someone who does, please contact me at phishing [at] inti.io with your story and evidence.**

Here’s how it unfolded:

### Becoming the phisher to reveal their identity

End of January, a scammer sent me a phishing e-mail impersonating Belgian bank Argenta to let me know that my banking card reader needs an update:

I got curious, so decided to inspect the website using Chrome’s devtools to see what’s going on

Once I had entered some fake card details, the page made a request to the pages `check-action.php`

and `loading.php`

.

I decided to take a look at the HTML source code of loading.php to see if I could get any clues about the phishing framework used.

I immediately spotted some *terrible* code that would fetch text document from the administration area containing a list of IP’s that aren’t welcome, redirecting them to an arbitrary website:

Many amateur phishing panels store their data in plain text files rather than databases, likely because they are simpler to deploy.

Now that I had located the administration panel, I tried navigating to it directly. I was presented with a login page:

Two things struck me here:

Scammers still like outdated h4ck0r visuals for their phishing page

“Or your IP Address is Change” indicates that login sessions are likely tied to the users’ IP address


Now I had a problem, because I didn’t know the username and password, and I did not know the scammers IP address either.

Then it hit me: the scammers likely tested the panel locally on their own machine before deploying it. If the software trusted requests coming from `127.0.0.1`

(localhost), there was a chance the original session file had been uploaded along with the panel.

So I used a proxy tool called [Burp Suite](https://portswigger.net/burp) to make the website believe I’m accessing the website locally on my computer (with IP address 127.0.0.1)

Then I refreshed and boom goes the dynamite 💥:

On behalf of the scammer, I could now access the session of the visitors:

This page allowed the scammer to control what the victim would see on their screen and would allow them to copy/paste their banking token once obtained. From looking at the source code, every action I would take here would be logged to the attackers telegram account by sending a request to **telegramclick.php**.

At this point, I wanted to ensure to stop this scam as soon as possible so that the users currently on the phishers’ page wouldn’t lose their money.

My first job was to ensure that the attacker wouldn’t be alerted.

Luckily, the admin panel had a delete file functionality that allowed me to traverse paths, so I started with deleting the telegram integration so my actions would be silent for the scammer:

The site would now appear broken for new visitors and no more banking details could be sent to the scammer that was still unaware at this point.

Now that the phish was no longer functional, I looked for ways to gain access to the files on the server to look for clues of the scammers’ identity.

The scammer had set up a Wordpress blog on the domain as a fake facade for the panel:

He probably should not have done that, as Wordpress allows whoever sets it up to execute their own code and plugins.

But since I didn’t set it up, I had to make Wordpress think it wasn’t installed already first. That turned out to be extremely easy, as I just had to locate a file called **wp-config.php** on the server, **delete** it using the same technique I used to delete **telegramclick.php **earlier, and refresh the page.

WordPress stores its installation state in a file called

`wp-config.php`

. If that file disappears, WordPress assumes it hasn’t been installed yet and launches the setup wizard:

After linking it to a mock database and setting a new username and password, I was now running a Wordpress blog on the same page the scammer had used to host their phishing panel:

I could now see all the files of the server, including the **argg.zip** backup that the phisher had created and could technically be downloaded by anyone.

Interestingly, that backup contained the scammers’ personal access logs with **multiple residential IP addresses from Morocco and one from a university in France** accessing the panel months before it went live.

Since Argenta does not operate in Morocco or France, these early logins were unlikely to be victims.

These IP addresses matched the hardcoded IP addresses that I found in the admin panel

What kind of criminals leave their own IP addresses hardcoded in their source code? We’re about to find out, but not before I changed the source code of the phishing framework to only work from Morocco, and display this message to the rest of the world:

Phishing attempt blocked! Do NOT enter your information. You can safely close this page.


Watch it in action:

The **telegramclick.php** file that I deleted earlier was also present in the backup and contained the telegram bot API token that would inform the scammers when a visitor had entered a valid bank card to start collecting the banking codes on their end.

The backup also contained the Telegram bot API token used by the panel. With that token, I could inspect the bot configuration and identify the usernames of the administrators receiving the stolen banking details.

According to the group metadata, there were four members involved:

Now that the scammer think their code works perfectly while not getting any new clients, let’s get back to unmasking them.

I put the IP address in the data breach lookup service [osintleak.com](http://osintleak.com) and found a gmail linked to this residential IP address from 2024. Unfortunately the e-mail address did not contain the full name, but I had something new to work with:

Then unexpectedly, Google+ came to the rescue. Who thought I’d be using Google+ in 2026?! I used EPIEOS Google+ reverse search to find out the Google profile once linked to this e-mail address:

I will not disclose the full identity of this person of interest as this does not prove that he was the one to publish the phishing panel from that IP address.

This person, as well as the some other profiles I found linked to the early logins from Morocco, all fit the description of technical university students in their early 20’s, some of them boasting with cars and jewelry on social media.

### What happened in the next few days

After a few hours, the scammers finally found out that something was wrong and decided to relocate the website to a different domain.

For days, they kept on re-uploading my hacked backdoor version, so every time they uploaded a new version I attempted to disable it again.

In total, I was able to take down seven campaigns with thousands of users targeted.

After that, the scammers had found and fixed the vulnerability.

Luckily for me, I had downloaded the source code and have found multiple vulnerabilities that would allow me to regain access. Since these vulnerabilities haven’t been fixed, I will not disclose them in this blogpost.

However, for the past few weeks it’s been quiet and I’d assume this group either got tired of me messing with them, or their attempts have gone off my radar.

But we have to bring them to justice as these aren’t one-off criminals. A quick reverse domain search has revealed this group would reupload the campaigns almost daily:

After discovering logo’s of other banks in the phishing panel, I got suspicious that this wasn’t a one-off for this particular group:

A quick Google search confirmed that the same platform had been used for other European banks as well.

At this point, I felt this was something I needed to report as soon as possible. Unsure where to go as someone who isn’t really a victim, I decided to report it to Argenta.

**Responsible disclosure timeline**

Jan 25th > Called Argenta phishing desk, was asked to write an e-mail

Jan 25th > Wrote an e-mail with the details & plan for blogpost

Jan 26th > Informed SafeOnWeb on [[email protected]](/cdn-cgi/l/email-protection) (which is an automated inbox as it turns out, if you need a human best to inform [[email protected]](/cdn-cgi/l/email-protection) instead)

Feb 25th < First e-mail acknowledgement of disclosure received from Argenta

Mar 9th > Blogpost published

It is unclear whether this evidence will be passed on to law enforcement as I’m not entirely sure whether that would be within the banks’ scope of responsibilities. For this reason, police officers working on this case specifically may contact me to obtain the evidence.

Let’s start bringing these criminals to justice.

### Disclaimer

Technically, hacking back phishing panels can be illegal in under certain jurisdictions and I would not recommend doing so without fully understanding and acknowledging the risk.

The examples in this blogpost have been thoroughly planned, weighed and precautions have been taken to minimize collateral damage or interference with existing investigations.

The actions described in this article were taken solely to disrupt an active phishing operation and prevent victims from entering sensitive information.**A note on the role of banks**

This post is not meant to dunk on banks. Phishing is a complex and constantly evolving problem, and many financial institutions are actively investing in tools and partnerships to better protect their customers.

Initiatives such as KBC’s

, which allows customers to involve a trusted person when suspicious payments occur, are examples of steps being taken to reduce fraud. Argenta is also working with partners to combat phishing and online scams, and other banks have similar initiatives.[Engelbewaarder]At the same time, hunting down hundreds of phishing campaigns uploaded every month is not an easy task for any organization.

Combating phishing ultimately requires banks, law enforcement, and the security community to work together, ideally within frameworks that make it easier for everyone to contribute. Let this post be another step towards that future!