---
source: spaceraccoon
source_url: https://spaceraccoon.dev/supply-chain-pollution-hunting-a-16-million-download-week-npm-package/
title: "Supply Chain Pollution: Hunting a 16 Million Download/Week npm Package Vulnerability for a CTF Challenge | Spaceraccoon's Blog"
published: 2020-12-23T15:29:57+00:00
description: "GovTech’s Cyber Security Group recently organised the STACK the Flags Cybersecurity Capture-the-Flag (CTF) competition from 4th to 6th December 2020. For the web domain, my team wanted to build challenges that addressed real-world issues we have encountered during penetration testing of government web applications and commercial off-the-shelf products."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Supply Chain Pollution: Hunting a 16 Million Download/Week npm Package Vulnerability for a CTF Challenge

Dec 23, 2020
·

1527 words

·

8 minute read


# Background [🔗](https://spaceraccoon.dev/supply-chain-pollution-hunting-a-16-million-download-week-npm-package/\#background)

GovTech’s Cyber Security Group recently organised the [STACK the Flags Cybersecurity Capture-the-Flag (CTF) competition](https://ctf.tech.gov.sg/) from 4th to 6th December 2020. For the web domain, my team wanted to build challenges that addressed real-world issues we have encountered during penetration testing of government web applications and commercial off-the-shelf products.

From my experience, a significant number of vulnerabilities arise from developers’ lack of familiarity with third-party libraries that they use in their code. If these libraries are compromised by malicious actors or applied in an insecure manner, developers can unknowingly introduce devastating weaknesses in their applications. The SolarWinds supply chain attack is a prime example of this.

As one of the most popular programming languages for web developers, the Node.js ecosystem has had its fair share of issues with third-party libraries. The Node package manager, better known as npm, serves more than **one hundred billion** packages per month and hosts close to one-and-a-half million packages. Part of what makes package managers so huge is the tree-like dependency structure. Every time you install a package in your project, you also install that package’s dependencies, and their dependencies, and so on - sometimes ending up with dozens of packages!

![npm&rsquo;s recent statistics.](https://spaceraccoon.dev/images/10/npms_recent_statistics.png)

If a single dependency in this chain is compromised or vulnerable, it can lead to cascading effects on the entire ecosystem. In 2018, a widely-used npm package, `event-stream`, was taken over by a malicious author who added bitcoin-stealing code [targeting the Copay bitcoin wallet](https://blog.npmjs.org/post/180565383195/details-about-the-event-stream-incident). Even though the attacker had a single target in mind, the popular `event-stream` package was [downloaded nearly 8 million times in 2.5 months](https://snyk.io/blog/malicious-code-found-in-npm-package-event-stream/) before the malicious code was discovered. In 2019, I presented a tool called [`npm-scan`](https://www.blackhat.com/asia-19/arsenal/schedule/index.html#npm-scan-an-extensible-heuristic-based-vulnerability-scanning-tool-for-installed-npm-packages-14396) at Black Hat Asia that sought to identify malicious packages, but it was clear that npm needed to resolve this systematically. Thankfully, the npm ecosystem has improved significantly since then, including the release of the `npm audit` feature and more active monitoring.

# Hunting NPM Package Vulnerabilities [🔗](https://spaceraccoon.dev/supply-chain-pollution-hunting-a-16-million-download-week-npm-package/\#hunting-npm-package-vulnerabilities)

With this context in mind, I set out to design a challenge that used a vulnerable npm package. Additionally, I wanted to exploit a [prototype pollution vulnerability](https://portswigger.net/daily-swig/prototype-pollution-the-dangerous-and-underrated-vulnerability-impacting-javascript-applications). To put it simply, prototype pollution involves overwriting the properties of Javascript objects in an application by polluting the objects’ prototypes. For example, if I overwrote the `toString` property of an object and printed that object with `console.log`, it would output my overwritten value instead of the actual string representation of that object. This can lead to critical issues depending on the application - imagine what would happen if I overwrote the `isAdmin` property of a `user` object to always be `true`! Nevertheless, as the impact of prototype pollution remains dependent on the application context, few know how to properly exploit it.

Next, I applied two tactics to find npm packages that were vulnerable to prototype pollution: pattern matching and functionality grouping.

## Pattern Matching [🔗](https://spaceraccoon.dev/supply-chain-pollution-hunting-a-16-million-download-week-npm-package/\#pattern-matching)

When vulnerable code is written, it often falls into recognisable patterns that can be captured by static scanners. This forms the basis of many tools such as GitHub’s [CodeQL](https://securitylab.github.com/tools/codeql), which scans open source codebases for unsafe code patterns. While scanners are used defensively to discover vulnerabilities ahead of time, attackers can also perform their own pattern matching to discover unreported vulnerabilities in open source code.

My tool of choice was [`grep.app`](https://grep.app/), a speedy regex search engine that trawls over half a million public repositories on GitHub. Since most npm packages host their code on GitHub, I felt confident that it would uncover at least a few vulnerable packages. The next step was to identify a useful regex pattern. I looked up previously-disclosed prototype pollution vulnerabilities in npm packages and [found a January 2020 Snyk advisory for the `dot-prop` package](https://snyk.io/vuln/SNYK-JS-DOTPROP-543489). Next, I checked the GitHub commit that patched the vulnerability.

![dot-prop&rsquo;s code diff.](https://spaceraccoon.dev/images/10/dot-props_code_diff.png)

`dot-prop` patched the prototype pollution vulnerability by blacklisting the following keys:

```javascript
const disallowedKeys = [\
	'__proto__',\
	'prototype',\
	'constructor'\
];
```

Here, there was no obvious code pattern that was inherently vulnerable; it was the **lack** of a blacklist that made it vulnerable. I decided to zoom out a little and focus on what `dot-prop` did that required a blacklist in the first place. According to the package description, `dot-prop` is a package to get, set, or delete a property from a nested object using a dot path.

For example, I could set a propety like so:

```javascript
// Setter
const object = {foo: {bar: 'a'}};
dotProp.set(object, 'foo.bar', 'b');
console.log(object); // {foo: {bar: 'b'}}
```

However, the following proof-of-concept would trigger a prototype pollution using `dot-prop`’s `set` function:

```javascript
const object = {};
console.log("Before " + object.b); // Undefined
dotProp.set(object, '__proto__.b', true);
console.log("After " + {}.b); // true
```

This worked because the **function** of `dot-prop` was to parse a dotted path string as keys in an object and set the values of those keys. Based on what we know about prototype pollution, this is inherently dangerous unless certain keys are blacklisted.

After considering this, I decided to search for patterns that matched other dotted path parsers. `dot-prop` used `path.split('.')` to split up dotted paths, although I later discovered that `key.split('.')` was commonly used by other packages as well. With this approach, I discovered several vulnerable packages, but this required me to manually inspect each package’s code to verify if a blacklist was used. Additionally, not all dotted path parsers used `key` or `path` to denote the dotted path string, so I probably missed out on many more.

![grep.app search with JavaScript filter.](https://spaceraccoon.dev/images/10/grep_app_search_with_javascript_filter.png)

## Functionality Grouping [🔗](https://spaceraccoon.dev/supply-chain-pollution-hunting-a-16-million-download-week-npm-package/\#functionality-grouping)

I realised that a better approach would be to group npm packages based on their functionality - in the previous case, dotted path parsers. This is because such functionality is unsafe by default unless appropriate blacklists or safeguards are put in place. After looking through the dotted path parsers, I stumbled on a far more prolific group of packages - configuration file parsers.

Configuration files come in various formats such as YAML, JSON, and more. Out of these, TOML and INI are very similar and match this format:

```ini
[foo]
bar = "baz"
```

A typical INI parser would parse this file into the following object:

```javascript
iniParser.parse(fs.readFileSync('./config.ini', 'utf-8')) // { foo: { bar: 'baz' } }
```

However, unless the parser sets up a blacklist, the following config file would lead to prototype pollution:

```ini
[__proto__]
polluted = "polluted"
```

However, unless the parser uses a blacklist, the following configuration file would lead to prototype pollution:

```javascript
iniParser.parse(fs.readFileSync('./payload.ini', 'utf-8')) // { }
console.log(parsed.__proto__) // { polluted: 'polluted' }
console.log({}.polluted) // polluted
console.log(polluted) // polluted
```

Indeed, prototype pollution vulnerabilities have been reported in [such parsers](https://snyk.io/vuln/SNYK-JS-INIPARSER-564122) previously, but only on an ad-hoc basis. I built my proof-of-concept code to quickly test packages at scale, then used npm’s search function to discover other parsers. The search function supports searching by tags such as `keywords:toml` or `keywords:toml-parser`, allowing me to quickly discover multiple vulnerable packages.

One of these was `ini`, a simple INI parser with a staggering **sixteen million** downloads per week:

![ini downloads statistics.](https://spaceraccoon.dev/images/10/ini_downloads_statistics.png)

This is because almost 2000 dependent packages use `ini`, including the npm CLI itself! Since `npm` comes packaged with each default Node.js installation, this means that **every user of Node.js** was downloading the vulnerable `ini` package as well. Other notable dependents include the Angular CLI and `sodium-native`, a wrapper around the `libsodium` cryptography library. While these packages included `ini` as a dependency, their risk depended on how `ini` was used; if they did not call the vulnerable function, the vulnerability would not be triggered.

![Packages that depend on ini.](https://spaceraccoon.dev/images/10/packages_that_depend_on_ini.png)

Although I did not use `ini` for the challenge, I made sure to responsibly disclose the list of vulnerable packages to npm.

# Responsible Disclosure [🔗](https://spaceraccoon.dev/supply-chain-pollution-hunting-a-16-million-download-week-npm-package/\#responsible-disclosure)

npm supports a robust responsible disclosure process, including a currently-on-hold [vulnerability disclosure program](https://hackerone.com/nodejs-ecosystem?type=team). The open source security company Snyk also provides a simple [vulnerability disclosure form](https://snyk.io/vulnerability-disclosure/), which I used to coordinate the disclosures. Fortunately, the disclosure process for `ini` went smoothly, with the developer patching the vulnerability in two ddays.

- December 6, 2020: Initial disclosure to Snyk
- December 7, 2020: First response from Snyk
- December 8, 2020: Disclosure to Developer
- December 10, 2020: Patch issued
- December 10, 2020: Disclosure [published](https://snyk.io/vuln/SNYK-JS-INI-1048974)
- December 11, 2020: CVE-2020–7788 assigned

Other packages are undergoing responsible disclosure or have been disclosed, such as `multi-ini`.

The vulnerability-hunting process highlighted both the strengths and weaknesses of open source packages. Although open source packages written by third parties can be analysed for vulnerabilities or compromised by malicious actors, developers can also quickly find, report, and patch the vulnerabilities. It remains the responsibility of the organisations and developers to vet packages before using them. While not everyone can afford the resources needed to inspect the code directly, there are free tools such as [Snyk Advisor](https://snyk.io/advisor/npm-package/ini#readme) that use metrics such as update frequency and contribution history to estimate a package’s health. Developers should also vet new versions of packages, especially if they were written by a different author or published at an irregular timing.

In the long run, there are no easy answers to open source package security. Nevertheless, organisations can apply sensible measures to effectively secure their projects.

P.S. One of our participants, Yeo Quan Yang, posted an excellent write-up on the challenge that illustrated the intended solution to chain a prototype pollution in a package with a remote code execution gadget in a templating engine. Check it out [here](https://quanyang.github.io/stack-2020-final-countdown)!

[web](https://spaceraccoon.dev/tags/web) [code review](https://spaceraccoon.dev/tags/code-review)