---
source: bughunters
source_url: https://bughunters.google.com/blog/externalizing-the-google-domain-tiers-concept
title: "Externalizing the Google Domain Tiers Concept - Google Bug Hunters"
description: "Do you want to know more about the concept of domain tiers, understand how they are applied at Google, and view a list of Google's highest sensitivity domains? Take a look at this blog post to find out more."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/externalizing-the-google-domain-tiers-concept#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Externalizing the Google Domain Tiers Concept

![](https://storage.googleapis.com/bughunters-article-images/blogs/sneuner.png)

Sebastian Neuner

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/mikispag.jpg)

Michele Spagnuolo

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/koto.jpg)

Krzysztof Kotowicz

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/hupan.jpg)

Anna Hupa

Technical Program Manager

![](https://storage.googleapis.com/bughunters-article-images/blogs/aaj.jpg)

Artur Janc

Information Security Engineer

Published: Jan 30, 2024

Vulnerability Reward Program  Web Security

[RSS Feed](https://bughunters.google.com/feed/en)

# Externalizing the Google Domain Tiers Concept

In this post, we'll discuss the concept of domain tiers, explain how they are
applied at Google, and share an accompanying list of Google's highest
sensitivity domains. Understanding this concept will assist bug hunters and
researchers with finding new targets, and clarifies how tiers influence Google
Vulnerability Reward payouts.

## Why do we need domain tiers?

Google maintains **~10,000** different domains (not taking country-specific TLDs
into account), each one potentially containing a distinct software or product,
including acquired products, services, and offerings by Alphabet-owned entities.
Some of these domains are used to host major applications managing our users'
sensitive data; others might only display simple webpages and do not have any
special privileges.

To focus our security efforts on the right applications, we at the Google
Security Team introduced the internal concept of _domain tiers_ in 2019, which
assigns a sensitivity factor to each domain.

## The domain tier concept

The primary use case of the domain tiers concept is to assign a sensitivity
factor/score to each domain that is hosting a web application. However, domain
tiers offer additional benefits such as enabling the discoverability of
applications with a given sensitivity score. For example, by reviewing services
hosted on a sensitive domain, a security team may learn about legacy
applications which share a web origin with a sensitive service, but do not
enable web security features to prevent common web bugs, such as XSS.

The decision of which tier a given domain belongs to is influenced by the
sensitivity metrics of the product(s) served on that domain. Ultimately, this
leads to a classification into one of 5 different tiers – where tier 0
represents the highest sensitivity. While this is true for all classified
domains, there are distinctions made between domains from acquired products and
Bets on the one hand, and Google domains on the other. The following table
illustrates the differences:

|  | Google classification | Acquisition / Bet classification |
| :-- | :-- | :-- |
| **Tier0** | Domains where a critical vulnerability (e.g. XSS or authorization bypass) could lead to a compromise of a user's account or execution of code on their system. | Domains where a compromise may lead to extended access of highly sensitive information on other systems. |
| **Tier1** | Domains where a vulnerability could disclose particularly sensitive user data. | Domains where a compromise may lead to access of highly-sensitive information on a single system or service. |
| **Tier2** | Subdomains where the impact of a vulnerability may be damaging, but is less likely to lead to the disclosure of highly sensitive data. | Domains where a compromise may lead to potential disclosure of sensitive, but not highly-sensitive information. |
| **Tier3** | Lower-sensitivity domains where a vulnerability is unlikely to affect sensitive data. | If this domain is compromised, no sensitive user data is affected. |
| **Tier4** | Sandboxed domains explicitly meant to host untrusted user-controlled content, or domains controlled by third parties. | The domain is hosted and operated by a third party or contains only user-curated, maintained, or public content. |

### Domain tier distribution

The following graph depicts the distribution of domains to tiers at Google:

![](https://storage.googleapis.com/bughunters-article-images/blogs/externalizing_domain_tiers_01.png)

## What does domain tiering mean for products?

Depending on the assigned domain tier, a product is in scope for different
levels of security guidelines.

All Google products/domains with a classification between Tier 0 to Tier 2 are
in scope for our internal web security guidelines which aim to protect sensitive
products from common web vulnerabilities such as
[XSS](https://portswigger.net/web-security/cross-site-scripting),
[CSRF](https://portswigger.net/web-security/csrf), or
[cross-site leaks](https://xsleaks.dev/). These guidelines specify an array of
security controls, often enabled by setting
[web security headers](https://web.dev/articles/security-headers) such as
[strict Content Security Policy](https://web.dev/articles/strict-csp),
[Trusted Types](https://research.google/pubs/pub50513/),
[Cross-Origin Opener Policy](https://web.dev/articles/security-headers#coop)/ [Cross-Origin\\
Embedder\\
Policy](https://web.dev/articles/security-headers#coep)/ [CORP](https://web.dev/articles/security-headers#corp),
or
[HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security),
and various other important web security controls. Our internal stacks include
and enable these security controls by default; however, it is important that
individual products/domains do not deviate from this baseline by disabling any
of the security controls. Domain tiers help us consistently ensure that these
protections are in place on sensitive domains and prevent security regressions.

We instrumented application frameworks and libraries to centrally report
telemetry on enabled security controls; this is used to continuously monitor the
deployment and status of security controls within a domain. Additionally, once
the tier is defined and assigned to a domain, the domain is regularly scanned by
our internal scanning infrastructure. When scanning detects deviations and
regressions from the aforementioned security guidelines, we inform the owning
team and suggest further remediation efforts.

In the past, the process of assigning a domain tier was mainly a manual task,
requiring a security engineer to review the tier proposed by the product owner.
However, to deal with the growing list of domains, we have developed internal
heuristics to automatically tier new, incoming domains. An example of such a
heuristic is the presence of login functionality within a product. Although this
is not perfect, the presence of login functionality is generally an indicator
that more sensitive data is available behind the login. That being said, in
addition to the automatic tiering, it is always possible to maintain a manual
tier mapping approach, allowing the domain owner to reevaluate the assigned tier
if needed.

## List of domains and tiers

In the spirit of transparency and in order to help security researchers validate
their knowledge of Google services and find new targets, respectively, we are
publishing a list of high sensitivity domains and their tiers
[on GitHub](https://github.com/google/bughunters/tree/main/domain-tiers). These
lists contain a full set of Tier 0 and Tier 1 domains split by Google domains
and acquisition/Bet domains, as per the definition above. Whenever there are
changes to the tiers of those domains, the lists will be updated by our internal
automation system. For the sake of completeness: domains that are not included
in the list should be considered lower tier, or not tiered at all.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab