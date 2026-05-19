---
source: bughunters
source_url: https://bughunters.google.com/blog/a-recipe-for-scaling-security
title: "A Recipe for Scaling Security - Google Bug Hunters"
description: "There are vastly more engineers at Google dedicated to creating and maintaining new products than there are security engineers working to secure products. For this reason, Google security has to focus on operating at scale and find ways to make meaningful security improvements across Google’s vast portfolio of services. Curious? See this blog post for details!"
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/a-recipe-for-scaling-security#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# A Recipe for Scaling Security

![](https://storage.googleapis.com/bughunters-article-images/blogs/dworken.jpg)

David Dworken

Information Security Engineer

Published: Jan 22, 2024

[RSS Feed](https://bughunters.google.com/feed/en)

# A Recipe for Scaling Security

For a long time now, Google’s security superpower has been uplifting security at
scale. There are vastly more engineers at Google dedicated to creating and
maintaining new products, than there are security engineers working to secure
products. This means that from the start, Google security has had to focus on
operating at scale and finding ways to make meaningful security improvements
across Google’s vast portfolio of services.

In the past, we've talked about our
[_safe coding_ approach](https://github.com/google/safe-html-types/blob/main/doc/index.md)
where we prevent vulnerabilities at scale by baking security invariants directly
into the platform. Safe coding undoubtedly works and we’ve seen a significant
reduction of vulnerabilities in numerous large-scale applications that have
adopted this methodology. For more information on our safe coding approach,
check out
[this paper](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/42934.pdf)
or [this talk](https://www.youtube.com/watch?v=ccfEu-Jj0as).

But, as we ratchet our safe coding platform to be more and more secure, we
always run the risk that some existing services are left behind. If we ban an
unsafe API, what happens to the code that is already using it? An optimist might
say that it is ok to leave the potentially vulnerable code as-is (in a way,
creating security [tech debt](https://ieeexplore.ieee.org/document/10109339)),
since it will soon be outnumbered by the ever-growing quantity of _new_ safe
code. But, this brings us to the second half of Google’s _safe coding_
superpower: Not only do we make the development platform _safe-by-default_, we
continually work to modernize old code and bring it up to modern security
standards.

Google has gotten continually better at this, and in 2023 we had some huge
accomplishments in terms of modernizing and improving our code at scale. This
blog post will explore what it takes to achieve this, the ways it has improved
Google’s security for all of our users, and provide a blueprint for other
companies interested in adopting this strategy.

## A brief history of backporting security features

Our approach to scaling security has evolved over time, and to learn from that,
it is interesting to look at how we approached rolling out
[Strict CSPs](https://web.dev/articles/strict-csp) across Google's web
applications (a project dating back to ~2016). We started with a question: How
can we mitigate XSS vulnerabilities at scale? We did security research, worked
with browser vendors to support new CSP directives, and built complex
integrations across frameworks, templating systems, and custom infrastructure to
collect reports. We then worked hands on with specific partner teams to roll out
CSP for critical services. We proved that CSP could be deployed, and that it was
an effective defense against XSS. We then changed the defaults so that newly
launched services enforced CSP by default, ensuring that all newly created
services are _safe-by-default_. This alone is an extremely important step, and
achieving this safe-by-default state is why new Google products (like Bard)
launch with many web mitigations enabled from the very start (at this point,
including [CSP](https://web.dev/strict-csp),
[Trusted Types](https://web.dev/trusted-types), and many more).

But then we had to figure out: How do we scale this? We could see that there
were tons of Google services that weren’t enforcing CSP! For this step, we built
custom tooling to find services that lacked CSP, and we filed bugs with service
owners asking them to adopt CSP. All in all, we filed almost ~800 distinct bugs
as part of the CSP adoption efforts and this enabled CSP to become a core
defense. Nowadays, CSP blocks a large fraction of XSS vulnerabilities reported
to us by external security researchers through our
[Vulnerability Rewards Program](https://bughunters.google.com/about) (though if
you’re a security researcher, and CSP is spoiling your fun, please do still send
us a report—we’re still interested in finding, fixing, and rewarding these!).

Looking back, we can do some napkin math to estimate the costs of this: If we
assume that each fixed bug took at least 5 days of effort (a generous assumption
for a service owner to learn about CSP, roll out report-only, refactor some
blockers, and roll out enforcement) and that each bug that was marked as “Won’t
Fix” took at least a half day to investigate and triage, we come up with an
estimate that this took at least 4 engineering years of effort across Google.
And it took a massive amount of our own team’s resources since we had to have
individual conversations with tons of product teams, often explaining the same
pieces of knowledge to many distinct teams.

## The magical tools and techniques that enable security at scale

We learned a lot from our experience of rolling out CSP at scale, and our
primary learning was that we didn’t want to repeat that same process for every
security feature. **We needed to scale**. The non-scalability of our previous
approach is especially obvious when looking at what it would mean to take that
approach for every security feature. Looking at our roadmaps, we had at least
three different critical web security features we wanted to roll out in the next
couple years. And assuming the same ratios, **this would consume another 12**
**engineering years of effort across Google**! And that was just for the web
security features that we already had in the pipeline, so it didn’t count the
many different mitigations being developed across Google’s large security team,
or future projects. So it was obvious that we needed to scale.

To scale, we realized that we needed a mindset shift, more data, and more
tooling. We needed to shift to thinking of ourselves as responsible for the full
lifecycle of a security feature, not just the development. More data so that we
could precisely determine when a change was safe to make. And more tooling so
that we could safely make these changes.

### A mindset shift

Once we committed to the idea of owning the rollouts for our security features,
we needed to understand what this means. At Google, there are thousands of
distinct services, so this is by definition operating at a huge scale. This is
generally made easier thanks to
[Google’s monorepo](https://research.google/pubs/pub45424/), but having a
monorepo isn’t necessarily required to make large-scale rollouts work.

Then we had to consider what mindset shifts this requires. One of the largest
ones is that as owners of large changes, we needed to think very critically
about reliability. Every change has a risk of breaking something, which harms
users and makes engineers just a little bit more skeptical of the security team.
We needed to have empathy for our users, and for the many engineers at Google
working to develop great products, so we needed to prioritize reliability. We
came up with an internal checklist to ensure that we prioritize reliability
every step of the way—by focusing on proper documentation/communication (e.g.
clear error messages with links to the relevant documentation and announcing
changes internally), technical validation (e.g. thorough cross-browser testing),
and clear rollback plans (e.g. ensuring that changes can be rolled back quickly
and centrally). We also developed custom data sources and tooling to help avoid
breakages.

### More data

When approaching large-scale rollouts, there are two broad classes of data that
we came to rely on:

1. Horizontal data that covers wide swathes of our infrastructure. This allows
broad measurements to understand the scope of a rollout (because you can’t
measure the impact of a rollout if you don’t know what you’re covering and
what gaps you have!) and broad information on compatibility.
   - We’ve built a highly custom framework to collect and process aggregated
     and anonymized traffic logs across all Alphabet web properties called
     _Security Signals_. With Security Signals, it becomes trivial to answer
     complex questions like “Give me the list of services that serve HTML
     files without CSP, on sensitive domains, grouped by serving framework,
     and sorted by traffic count”.
   - A more standard solution is to use metrics (like Prometheus or StatsD)
     to increment a counter (often associated with various tags). This makes
     it possible to query a counter across all Google services, for example
     to count how often an event is occurring and where.
2. Precision-focused data that precisely collects information about specific
noteworthy events. This allows gathering more specific information and
metadata, for example gathering a stack trace or the exact server-side
endpoint that caused a problem. This is often used to inform the design of
new security features since it makes it possible to understand what real
behavior is happening at runtime, which informs what mitigations are likely
to be widely compatible. And then, once a feature has been designed,
precision-focused data makes it possible to confirm with a high degree of
certainty that a feature is safe from a reliability perspective.
   - We’ve built a highly custom set of infrastructure to consume “reports”
     (e.g. from the
     [Reporting API](https://developer.mozilla.org/en-US/docs/Web/API/Reporting_API)),
     process them (e.g. deduplication and custom integrations to allow
     linking one report directly to the code that triggered it), and make
     them easily queryable. This central telemetry-collection infrastructure
     has come in handy for all kinds of remediations, ranging from CSP to
     log4shell.
   - A more standard solution is to use application logging, likely combined
     with emitting information to a globally shared log destination that can
     be globally queried.

### More tools

In addition to the custom data tools mentioned above, there are other tools that
are key to making large-scale changes in a reliable manner. Just to mention a
few:

1. [Rosie](https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext#:~:text=A%20Google%20tool,the%20appropriate%20reviewers.)
makes it possible to send out hundreds of changes for review,
[run all automated tests](https://abseil.io/resources/swe-book/html/ch22.html#:~:text=riding%20the%20tap%20train),
and easily manage feedback and submission. Rosie also has the ability to
send changes to special global approvers who bulk approve the changes,
enabling us to submit known-safe changes across Google without bothering
product teams to ask them for individual reviews.
2. A set of custom compile-time checks make up a system we call _conformance_
that makes it possible to restrict certain “bad” types of changes at compile
time. One extremely key part of this is preventing backsliding, so that once
a security improvement has been landed, it can't be rolled back without the
security team being looped in. Conformance is also key to encouraging
convergence, where we want to guide newly built services to be built on
secure frameworks from the start. We’ve open sourced
[Error Prone](https://github.com/google/error-prone) and
[tsec](https://github.com/google/tsec) which make these sorts of rules easy
to enforce for Java and TypeScript.
3. Experiment systems make it possible to
[gradually ramp up a change at runtime](https://sre.google/sre-book/service-best-practices/#:~:text=Progressive%20Rollouts).
We've built custom experiment systems that make it possible to ramp up a
change gradually across large swaths of Google’s services, and easily roll
it back if we detect any issues. When combined with the above data sources,
this increases reliability and velocity.

## 2023’s landings

With that introduction, we can now talk about some of what we've accomplished in
the last year of security rollouts at Google! This is a small subset of the
security rollouts we've done in the past year, focusing just on web security
features that landed:

- **166** services are newly enforcing
[Strict CSP](https://web.dev/articles/strict-csp)
- **176** services are newly enforcing
[Trusted Types](https://web.dev/articles/trusted-types)
- **347** services are newly enforcing
[Resource Isolation Policy](https://web.dev/articles/fetch-metadata#implementing_a_resource_isolation_policy)
- **1079** JavaScript builds have new
[static guarantees](https://github.com/google/tsec) that all transitive
dependencies satisfy our safe coding conformance checks
- **438** legacy DOM XSS sink assignments were removed
- **160** services are newly enforcing
[SameSite cookies](https://web.dev/articles/samesite-cookies-explained)

Some more napkin math comes up with an estimate that these 6 rollouts alone
would have taken Google at least 20 engineering years of work if done in the
traditional manner. By having the security team take on these rollouts
centrally, we were able to land all these security features with a tiny fraction
of that effort. This increases velocity for both the security team (leading to
more secure products!) and for product teams (enabling product teams to ship
better products!) and is a huge win for the user. All of this demonstrates what
we see as **the full _safe coding_ approach, where we uplift security at scale,**
**for everyone**. To understand the full impact of this, we can also look at our
overall security feature coverage, where we can see amazing statistics such as
96% of our most sensitive services enforcing CSP, and 80% of our most sensitive
services enforcing Trusted Types. Across hundreds of web apps built on top of
our secure frameworks that comprehensively enable these and other security
mechanisms (such as safe server-side HTML templating), we have seen zero XSS
vulnerabilities since the features were enforced.

If you're interested in a more detailed description of what this sort of project
looks like end-to-end, check out
[this blog post on fixing debug log leakage with Safe Coding](https://bughunters.google.com/blog/6405366705946624).
This highlights many of the complexities inherent to doing large-scale rollouts,
but is also a great story of a massively scalable security improvement across
Google. Also, watch out for future blog posts in this series where we'll talk
more about these rollouts and the tools and techniques that power them!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab