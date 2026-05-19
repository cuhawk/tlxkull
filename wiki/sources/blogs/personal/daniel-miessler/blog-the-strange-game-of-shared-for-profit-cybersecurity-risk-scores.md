---
source: daniel-miessler
source_url: https://danielmiessler.com/blog/the-strange-game-of-shared-for-profit-cybersecurity-risk-scores
title: "The Strange Game of Shared, For-profit Cybersecurity Risk Scores | Daniel Miessler"
description: "Brian Krebs ran a story recently about how FICO has a new service for rating the Cybersecurity risk level of various companies. Problem is, in one of their mark"
---

Brian Krebs [ran a story recently](https://krebsonsecurity.com/2018/12/scanning-for-flaws-scoring-for-security/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=the-strange-game-of-shared-for-profit-cybersecurity-risk-scores) > about how FICO has a new service for rating the Cybersecurity risk level of various companies. Problem is, in one of their marketing communications about the new offering, they leaked the actual report data for a little company called ExxonMobil.

I find this space both strange and fascinating.

On one hand I like the idea of people looking out for each other by evaluating how risky companies are and then sharing that knowledge with others. This type of thing is basically necessary given how many entities a given company has to do business with. It’s virtually impossible to do risk assessments on all of them yourself. So that’d be nice if there was good data out there, being shared for the benefit of everyone.

Unfortunately, I’ve seen a number of these companies and their reports over the years, and the product seldom matches the packaging. Here are a few of the problems I’ve seen.

**You have to pay to get access to the data that’s supposedly for the greater good**. I’m obviously pro-business, and pro-innovation, and pro-all-those-things-you-like. But if I had to pay a micropayment to read an FDA label I’d be pretty pissed. And that’s where we’re getting with supply chain security and complex products (all of them) today. If something is made out of 100 different components, how do you trust the final branded version?

**It’s really hard to keep data updated on companies, so these risk scores are often wildly inaccurate**. Heck, most companies can’t even keep their own asset data up to date, and they have full access to the data. So the idea that a private company is going to do it well is a pretty hard sell. It’s possible, of course, but I’ve not seen it from any of the players so far. Continuous asset management is hard.

**It’s also not trivial to get your own data updated in these systems**. So let’s say your sales team calls you up and invents some new cuss words because your WIZBANG score is too low, you might look at the data and see that it’s really bad. Not your domains. Not your IPs. Not your systems. Strange risk calculations. The ports were faked, not really open. Whatever. The processes that I’ve seen so far for getting that data updated, with each side exchanging contradictory evidence isn’t great. And in the meantime, you could be losing market share, deals, and reputation.

What I see from all this is a lot of externalities, which are basically unintended consequences of a well-meaning policy or action. Like, at what point are you liable for damage that results from your ratings? What if you lose business because of an incorrect and low rating? Or what if a low rating puts you on the radar of attackers, and results in a breach that wouldn’t have happened otherwise?

I think once you start making claims about the security of thousands of very important entities, in any way that’s meant to be consumed by others, you take on a huge amount of responsibility.

I’m not willing to damn the entire space, though. The work needs to be done, and this space in the industry seems to be the only one that’s managing a thrust. It reminds me a lot of the conference scene, actually.

Everyone wants more conference speakers, but they also want fewer vendors trying to sell their wares. Yet most of the talks submitted are by people working at companies—many of which are at the conference paid for by a sales or marketing budget. It’s kind of gross, but the alternative seems to be having conferences with no speakers.

If you’re a company, go to all these services (FICO, Security Scorecard, Bitsight, etc.) and find out what you’ve been rated at. If you see anything inaccurate, work with them to fix it.

If you’re a vendor who’s considering not doing business with a company because they have a low score on one of these services, look at the specific markers and contact someone at the company directly. You might find that the score is inaccurate enough that you’re more comfortable moving forward.

If you’re a vendor in this space, do your absolute best to balance the public good with the need to make money as a business. And consider adding an accuracy and freshness rating to the data you have on your portfolio companies.

No need to run away, but proceed with caution.