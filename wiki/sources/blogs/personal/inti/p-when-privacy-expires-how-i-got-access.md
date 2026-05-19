---
source: inti
source_url: https://inti.io/p/when-privacy-expires-how-i-got-access
title: "When privacy expires: how I got access to tons of sensitive citizen data after buying cheap domains"
description: "As part of a large-scale privacy investigation, I have bought more than 100 domain names previously belonging to social welfare and justice institutions in Belgium. What I observed was unsettling."
---

# When privacy expires: how I got access to tons of sensitive citizen data after buying cheap domains

### As part of a large-scale privacy investigation, I have bought more than 100 domain names previously belonging to social welfare and justice institutions in Belgium. What I observed was unsettling.

Cybersecurity has always been transient: what is deemed to be secure today, may be considered easily hackable tomorrow. Domain names in web and e-mail addresses, such as info [at ] inti.io, are leased in time. This means that if nobody thinks of renewing them after they expire, they will be put up for sale. It made me wonder what would happen to the graveyard of cloud accounts attached to the e-mail addresses that once belonged to these expired domains.

Concerned about my data and that of my fellow citizens, I decided to start an investigation: **is it possible to revive old cloud accounts that were once used to store our sensitive data?**

First, I needed a list of companies or institutions whose e-mail addresses either ceased to exist due to bankruptcy or changed as part of a merger, split, or rebranding operation. This wasn’t particularly hard to do, as organizations typically announce these changes to the public.

I immediately thought of the fusion of the Belgian municipalities, where entire towns and cities with thousands of inhabitants were merged under a new name. The old domain names containing the previous name were simply rerouted to the new name, e.g., puurs.be will take you to puurs-sint-amands.be. This was the case for all domain names, except one: somebody had already bought overpelt.be (which became Pelt after merging with Neerpelt).

The administration of Pelt housed about 15,000 residents upon their merger in 2018. Since 2022, their website has hosted a “blog” that is actually a fake facade for dubious purposes. In this case, it looks like the new owner is merely using it to artificially increase the Google ranking of other websites, but one can never be sure.

The same is happening with former publicly listed companies that went bankrupt, such as alfacamgroup.com (bankrupt in 2013), Thrombogenics (bankrupt in 2019), and fng.eu (bankrupt in 2022), which once had hundreds of employees on their payroll. These are now bought up and swapped out for dubious websites that still accept incoming e-mail:

Except for search ranking hacks, nobody can really know for sure what the intentions of their new owners are.

Moving further down my list of recently expired domains, I started seeing patterns—and not ones I was pleased to see. A considerable number of the recently expired domains contained abbreviations of Belgian social welfare institutions:

OCMW (44 expired domains)

Institutions that help the most vulnerable people in our society with financial issues, crisis situations, social housing, legal and medical assistance, and disability assistance.


CAW (12 expired domains)

Similar responsibilities as OCMW, but more directed toward a general audience (including youth), providing psychosocial support for individuals and families, and more aimed toward prevention.


CLB (12 expired domains)

Social institutions focused on providing support to students and pupils with school-related learning or family difficulties.



In addition to identifying 68 domains related to the Belgian social welfare system, I concluded that multiple domains associated with certain psychiatric hospitals (4 expired domains), as well as the Belgian justice system, were also affected, from police zones (32 expired domains), which migrated to a @police.belgium.eu e-mail address in 2018, to local courts and tribunals (3 expired domains).

As a responsible citizen, I wanted to avoid these sensitive domains ending up in the wrong hands, so I bought all of the more than 100 domains for around €850. As the legal and rightful owner of these domains, I now had insights into how they were still used.

Once I bought the domains, I started receiving e-mails for these e-mail addresses:

I started making a list of various e-mail addresses that once belonged to these domains, which I obtained from public sources. Then, I used the ‘Forgot password’ functionality on popular cloud services to check whether these e-mail addresses were still linked to an active account and whether I could receive the password reset links sent to these e-mail addresses that would theoretically allow me to log in to these sensitive cloud accounts:

For the 848 e-mail addresses I was able to identify within a week, I successfully obtained the password reset e-mails for 80 Dropbox accounts, 142 Google Drive accounts, 57 Microsoft / OneDrive / SharePoint accounts, and a dozen Smartschool and Doccle accounts. I realized that by buying these domains, I had gained access to tons of sensitive citizen information stored in the cloud accounts linked to these e-mail addresses.

I did not have to log in to any of these accounts to check whether they actually contained files, as I started receiving e-mails like this:

These weren’t the only e-mails I started receiving. Shockingly, years after these e-mail addresses were abandoned, they still received extremely sensitive information. To respect the sender’s privacy as much as possible, I avoided opening the e-mails. Based on the titles, the sending authority, and the recipient, I was able to classify the e-mails into the following categories. In the list below, I’ve selected 2 - 3 example e-mails per category.

Confidential justice information Information regarding released detainees, public defenders, …

Payment reminders for people in debt

E-mails related to vulnerable people’s health or social situation

Meeting invites to special committees:

Official copies of attestation documents, as well as Doccle / bank documents for people in debt management

Questions or information from or regarding vulnerable people in difficult situations

*(no reproduction or screenshot here as it is considered too personal/sensitive to even refer to)*Insurance claim documents directed to the police

Smartschool announcements and document references directed to CLB (pupil counseling institution)

Technical access invitations and reports for firewall, antivirus,

Other: personal employee-related e-mails

Tax-on-web messages

Payroll information

Linkedin updates, personal accounts (strava running app, e-commerce orders, payments with apple pay, …)



…And hundreds of other e-mails. In merely a few days.

Some emails that came in looked as if they came from vulnerable people themselves, asking for help. It may be that they haven’t received or understood the message to update their address book.

I did not interfere with any of the e-mails, as this would go beyond the objectives of this investigation, but it is concerning, to say the least, that these individuals will never receive a reply. They would not have received a response anyway, but it makes me wonder how many cries for help get lost in abandoned e-mail inboxes.

After the short duration of this experiment, I disabled incoming e-mails for these domains. Prior to publication, the CCB (Centre for Cybersecurity Belgium) has briefed their previous owners and informed them about the risks of expired domains.

With hundreds of new domain names set to expire in the coming year, structural changes will be needed to prevent this from happening again. I am publishing this blog today to raise awareness about this threat to society that goes far beyond the borders of Belgium and is relevant to all governmental institutions around the world. We should collectively look into a better strategy for managing the lifecycle of domain names, especially those tied to sensitive or critical services. This could include creating policies for the secure handling and proper decommissioning of expired domains and their associated cloud accounts, ensuring they don't fall into the wrong hands, and maintaining continuity for important communications. Enforcing two-factor authentication on cloud accounts could also greatly reduce the risks associated with these attacks. At least, that’s what I’m trying to do for my own inti.io domain, because undoubtedly, it may belong to someone else one day - and that idea shouldn’t be as scary as it sounds right now.

**FAQ**

**As a company owner or system administrator, how can I prevent against this?**Everything starts with awareness: anyone can create rules, but if employees do not understand the ‘why’, they may not follow them. This blog post can serve as a tangible example of what can go wrong if we start storing, sharing, and receiving sensitive data on non-approved cloud storage providers.. The use of multifactor authentication (MFA) is a must, as well as implementing proper change management procedures and communications. If you’re changing e-mail addresses, make sure everyone knows and has a reasonable amount of time to adapt their address book. Set an out-of-office response for anyone e-mailing to the old e-mail address, reminding them that you are phasing the e-mail domain out. Enable auto-renewal for expired domain names, or renew them for a minimum period of ten years. Search Google for references to the old e-mail domain and ensure they’re updated. Some cloud services, such as[Google](https://support.google.com/a/answer/1668854?hl=en), also allow domain administrators to limit registration for certain e-mail domains.**Why didn’t you just report the expired domain names?**

Expired domain names themselves do not constitute a threat to citizen privacy: organizations may have legitimate reasons for letting domain names expire. I needed to prove the existence of the actual threats to make a case.**Why didn’t you report this issue to all affected parties prior to publishing this?**

By taking all sensitive domain names I could find off the market, I was able to mitigate the majority of the risk for the time being. Tracking down their owners is trickier, as I am now the sole recipient of the only e-mail address I had on file for them. By raising public awareness, I am hoping to inform all system administrators that may be affected by this issue, now or in the future. Prior to publication, I made multiple authorities aware of this issue. Special thanks in particular to the Centre for Cybersecurity Belgium (CCB) for providing swift and effective support into handling this case with the highest priority.**Is buying a domain name and receiving their e-mails legal?**

It depends. The act of buying an expired domain name is completely legal; however, buying a trademarked domain name (cybersquatting) may violate copyright laws, especially when done with malicious intentions. Some countries have laws that prevent you from opening physical mail directed to someone else, however there is debate whether this also affects e-mails, as they may be considered as opened (“downloaded”) the moment you receive them. The laws that do talk about electronic communication typically forbid the interception of communication between two or more non-consenting or unaware participants through the means of any device (such as a secret listening device or a man-in-the-middle attack), but in this case, one could argue that the recipient is the actual addressee in the conversation as they are the legitimate owner of the domain name - the intended receiver was never part of the conversation. Then there’s also privacy laws that prohibit sharing and processing data of subjects without their consent, but by sharing content with an expired e-mail address, the sender may be the one violating the data subject's privacy rights by not conducting due diligence on the e-mail address.

The act of actually taking over and logging into the expired cloud accounts, such as Dropbox, would likely fall under the definition of illegal hacking. Just by buying the domain, you do not become the owner of the related accounts. During this research, no actual passwords were reset.

There isn’t much to find on this internet regarding this particular case, but I did find an[interesting StackExchange conversation](https://law.stackexchange.com/questions/35917/legal-protections-for-an-expired-email-domain)related to this scenario.**Is this limited to Belgium?**No, not at all. In fact, during my research, I found that someone reported a similar issue[for a single domain with police related e-mail addresses in the Netherlands](https://www.rijnmond.nl/nieuws/150868/vertrouwelijke-mails-aan-politie-rijnmond-in-handen-van-hacker). In Australia, someone did the same with[six expired e-mail addresses](https://blog.ironbastion.com.au/hacking-law-firms-abandoned-domain-name-attack/)belonging to law firms.**How long did the experiment take?**

A little over a week. I deemed this to be enough to get a decent understanding about which e-mail domains were still active, as it would cover all days of the week and potentially automated e-mails scheduled on a certain day. After the experiment was over, I started explicitly blocking e-mails to my domain.**What steps did you take to mitigate risk, if any?**

Since the domain names I have purchased were already expired, their previous owners should not have experienced any negative side effects. The e-mails sent to my addresses would have never reached them in the first place. Additionally, I had embedded my personal details in both the DNS name records and the websites belonging to them, so that anyone noticing something strange could immediately contact me to reclaim their domain at no cost.

During the testing period, nobody reached out despite leaving my contact details.

As far as data privacy goes, I tried to limit myself from any excessive sensitive data exposure by mainly looking at an e-mails’ subject, its sender and recipient to determine the class of its content. I proved the ability to take over the cloud accounts, but never actually completed the password reset in order to preserve the integrity of these accounts. The e-mails are stored in a separate and secure environment in the cloud, and will be deleted shortly.


Subscribe to my blog!

This piece of research was made possible thanks to my subscribers! [You can subscribe today for free](https://inti.io/p/why-subscribe) to be the first to hear about future disclosures. You can also decide to sponsor me on the same page. Last year, I received $200 in sponsorships through this blog, which helped me pay (partially) for the domains in this experiment.