---
source: bughunters
source_url: https://bughunters.google.com/blog/celebrating-one-year-of-ai-bug-bounties-at-alphabet
title: "Celebrating One Year of AI Bug Bounties at Alphabet - Google Bug Hunters"
description: "This blog discusses what one year of AI bug bounties has taught us and where we're planning to go from here."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/celebrating-one-year-of-ai-bug-bounties-at-alphabet#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Celebrating One Year of AI Bug Bounties at Alphabet

![](https://storage.googleapis.com/bughunters-article-images/blogs/aaronmb.jpg)

Aaron Brown

Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/jaycox.jpg)

Mark M. Jaycox

Policy Counsel

Published: Dec 17, 2024

Vulnerability Reward Program

[RSS Feed](https://bughunters.google.com/feed/en)

# Celebrating One Year of AI Bug Bounties at Alphabet

In October of last year,
[we announced rewards for bugs in Generative Artificial Intelligence (Gen AI)](https://security.googleblog.com/2023/10/googles-reward-criteria-for-reporting.html)
products. In this post, we'll be discussing some of the things we've learned in
the past year and how those lessons are going to inform our VRP program going
forward.

## Our Successes

First, we wanted to take this chance to celebrate how far we've come in the past
year: we've received over 140 bug reports regarding our Gen AI products. Of
these reports, approximately one in six resulted in product team mitigations,
which is similar to the rate seen across the broader VRP program at Google. So
far, we've paid out more than $50,000 in bug rewards for Gen AI reports. We're
proud of the work we've done so far on the program and grateful to all of the
bug hunters and researchers who have taken the time to report issues to us and
help us make Google's Gen AI products safer.

Our thanks to each and every one of you.

## Our Lessons Learned

With the introduction of Gen AI, several new classes of bugs have emerged, such
as training data exfiltration and prompt injection attacks. In addition, the
fact that inputs to Gen AI and much of its operational configuration are
performed through natural human language makes it harder to define what is or
isn't a valid "bug". Reproducibility is key to being able to provide actionable
report details to product teams. Large language models are probabilistic in
nature and outputs differ depending on contexts, which makes it even harder to
reproduce and assess the validity of reports. Model tuning, differences in
initial system prompts, and multi-turn attacks all further complicate this.

Due to these factors, we were careful in defining
[the scope for our program](https://bughunters.google.com/about/rules/google-friends/5238081279623168/abuse-vulnerability-reward-program-rules#qualifying-vulnerabilities-in-ai-products)
when we launched. We've learned over the past year that many researchers are
interested in and are discovering bugs in areas that are out of scope for our
current program. In particular, there's been a great deal of research done
regarding "jailbreaks", or ways to convince AI systems (in particular large
language models) to engage in behavior not normally permitted by their
guardrails. When we launched the program, we determined that these types of
jailbreaks would be out of scope for our program for a few reasons:

- They typically impact a user's own session. This makes it hard to assess the
user impact of a particular jailbreak.
- It's hard to deduplicate different jailbreaks and come up with specific
rules around duplicates that respect our "first reporter wins" approach for
assessing rewards.
- There may, in fact, be an infinite number of possible jailbreaks for any
particular model and
[fully mitigating them](https://arxiv.org/pdf/2304.11082) [may be completely infeasible](https://arxiv.org/pdf/2307.10719).

None of these facts change that jailbreaks have real, negative effects on Gen AI
systems and we are constantly working to provide better mitigations for them.
Given that it's also an area of interest and concerted research by the broader
community, we've consistently heard that we need to do more to include
jailbreaks in the VRP program. While we can't make any promises regarding future
scope, the team is aware of the community interest and continues to reassess our
program scope around these issues.

Another lesson that we've learned is that reproducibility can provide specific
challenges in the context of AI. Even a well-written report accompanied by a
clear screen-captured video of bad behavior sometimes isn't enough for us to
reproduce a particular report. There's a few reasons for this. First, even
closely related models in the same family can respond to queries differently in
subtle, non-obvious ways. Add to this that there can be differences in fine
tuning between contexts or over time, and an issue may disappear and reappear as
training context changes. In the future, we will be exploring ways to safely
gather the metadata required to reproduce these bugs while maintaining user
privacy.

Additionally, the nature of generative AI means that even under the same
conditions of request, model, tuning, and configuration, a particular input may
not reliably produce the same response. For VRP staff trying to reproduce an
issue or generate logs before passing a report to a product team, the challenge
is that we can't know if we're doing something wrong, if the report is in error,
or if it just happens about once every hundred times and we need to keep trying.

## What We've Heard From Bug Hunters

In short, what we're hearing is: "do more." We've consistently gotten the
message from academics, bug hunters, and bug reporters that they want more scope
and more opportunities to find issues in our Gen AI products. As described in
the preceding section regarding jailbreaks, there are good reasons why certain
areas of Gen AI research are currently out of scope for our program. However, we
are constantly reevaluating our criteria and the technical landscape to see if
and how our current scoping could change.

We've also had a lot of questions about the coordination of disclosure(s) in AI
products. We'd like to take this opportunity to clarify that our
[coordinated disclosure stance](https://about.google/appsecurity/) applies to
Gen AI issues the same as it does to any other bugs reported through any of our
VRP programs. In other words, we ask for reasonable notice before any disclosure
on your part. Giving us time to remediate an issue before public disclosure is a
requirement for being eligible for a reward through the VRP program. But, as we
like to say, "we buy bugs, not silence". We do not try to control which issues
are disclosed or how, and we value the service that disclosure plays for the
broader security ecosystem. In fact, we regularly comment on and help clarify
the disclosures of reporters who share their draft disclosures with us ahead of
time.

Finally, researchers have also asked us how
[Google's Gen AI Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy?e=IdentityBoqPoliciesUiAITestKitchenSSAT::Launch,-IdentityBoqPoliciesUiBardSSAT::Launch,-IdentityBoqPoliciesUiGoodallSSAT::Launch,IdentityBoqPoliciesUiAdditionalAup::Launch)
relates to our
[VRP Rules](https://bughunters.google.com/about/rules/google-friends/5238081279623168/abuse-vulnerability-reward-program-rules#qualifying-vulnerabilities-in-ai-products).
These policies are complementary. The Generative AI Prohibited Use Policy –
similar to many other Google product policies – includes an educational,
documentary, scientific, or artistic (“EDSA”) exceptions clause. We always
encourage users to submit detailed reports through our Bug Hunters program
first; however, EDSA exceptions allow for journalists, academics, and security
researchers to also report vulnerabilities through product feedback buttons.

Gen AI is novel and industry norms haven't had a chance to be created around
bugs in those systems. Google's existing norms around collaborating with
researchers in good faith and respecting coordinated disclosure practices are
unchanged.

For more about how we're thinking about AI security policy, you can also
[read the new essay published by Google DeepMind on AI Policy Perspectives.](https://www.aipolicyperspectives.com/p/securing-ai)

## Where We're Going From Here

In general, we at the Abuse VRP team are curious and excited to see how our
second year with Gen AI-related reports will develop. We expect to see
significant growth in the number of issues reported and the kinds of Gen AI
reports we see. We also expect that new Gen AI launches and new research from
the community will help us adapt and adjust to changes in the field.

Going forward, we plan to leverage targeted grants for specific researchers to
explore some out-of-scope families of Gen AI bugs, including jailbreaks. This
will allow us to learn more about classes of issues such as jailbreaks, and help
us develop ways to objectively assess these issues, including how to classify
their impact and deduplicate them.

And, of course, we will continue to be an active part of the Google VRP
community. Just like you could find us at 0x0G in Las Vegas and
[Escal8 in Malaga](https://bughunters.google.com/blog/4846227460325376/google-s-escal8-conference-where-esports-bug-hunting-and-inspiring-new-talent-come-together)
in 2024, you can expect to see us at similar events around the world in 2025.

Thank you for a great first year and we look forward to receiving your bug
reports!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab