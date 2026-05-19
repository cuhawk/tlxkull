---
source: oversecured
source_url: https://oversecured.com/blog/introducing-mavengate-a-supply-chain-attack-method-for-java-and-android-applications
title: "Introducing MavenGate: a supply chain attack method for Java and Android applications | Oversecured Blog"
author: "HubSpot, Inc."
description: "This article introduces MavenGate, a supply chain attack method that can let attackers hijack Java and Android dependencies by taking over abandoned domains or project identities. It explains how this weakness appears in common Maven and Gradle workflows, why default dependency resolution can make projects vulnerable, and how malicious code could be injected into apps or build pipelines. The piece"
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

## Introduction

Oversecured is a security company providing vulnerability protection for iOS and Android mobile apps. We help our customers keep threats at bay while enabling secure and reliable mobile apps. Our products are built into the CI/CD process and monitor code security before release to end users. Our mission is to help developers build secure and reliable mobile apps by offering innovative and best-in-class security tools underpinned by industry-leading research on the latest vulnerabilities. As trusted leaders in mobile security, we have garnered significant media coverage on major vulnerabilities that we identified in [Google](https://blog.oversecured.com/Why-dynamic-code-loading-could-be-dangerous-for-your-apps-a-Google-example/), [TikTok](https://blog.oversecured.com/Oversecured-detects-dangerous-vulnerabilities-in-the-TikTok-Android-app/), [PayPal](https://blog.oversecured.com/Exploiting-memory-corruption-vulnerabilities-on-Android/) and many other apps. By sharing our detailed analysis with not only our customers but also the wider public, we have helped educate industry peers and developers and minimized the risk of exploitation by nefarious hackers.

Given the recent supply chain attacks in the “web world”, we have conducted a study on the possibility of supply chain attacks in the mobile application world.

In the course of our research, we found utter chaos that extends far beyond the Android world. Many public and popular libraries that have long been abandoned are still being used in huge projects. Access to projects can be hijacked through domain name purchases and since most default build configurations are vulnerable, it would be difficult or even impossible to know whether an attack was being performed.

As a result, all Maven-based technologies, including Gradle, are vulnerable to MavenGate.

More than 18% of dependencies can be intercepted by attackers, which for a typical project with many direct and transitive dependencies dramatically increases the probabilities of a vulnerability. As a result, we sent reports to over 200 companies, including Google, Facebook, Signal, Amazon, and others. If successfully exploited, attackers will be able to inject their code into the application by attacking its dependencies. There is also the risk of injecting into the build process and accessing a company’s infrastructure through a plugin attack.

Oversecured customers were given exclusive access to this research and assistance in patching vulnerabilities in advance of public release so they can significantly reduce the risk of potential attacks on their Android applications and Java-backend. To become our customer, please fill out the [contact form](https://app.oversecured.com/contact-us).

## Maven philosophy

If we look at the project structure of any Gradle-based project in terms of dependency declaration, it will typically contain:

1. Dependency repositories, such as `google()`, `mavenCentral()`, `jcenter()`, and a host of others available via direct links. They describe where the builder should look for the specified dependencies.


![](https://framerusercontent.com/images/aWtUyXK3Noa1X2VjAiDJ4LYZQGE.png?width=1296&height=848)

2. Dependencies typically use the format `groupId:artifactId:version`, for example `com.google.code.gson:gson:2.10.1`. The builder goes through the list of available repositories and looks for the specified dependency in it.


![](https://framerusercontent.com/images/W8t8xXrz6Q9dzOQMQFlRuQw746k.png?width=1402&height=394)

Repositories come in two types:

- Private. These include the [Google repository](https://maven.google.com/web/index.html), because it only hosts dependencies created and maintained by that company.

- Public. For example, `mavenCentral()`. Anyone can add their projects and libraries to it and distribute them publicly.


An important question arises: “What prevents an attacker from hijacking dependencies from public Maven repositories, replacing them with malicious code, and thus infecting millions of projects?”.

Public repository pages such as [Maven Central](https://central.sonatype.org/faq/verify-ownership/) and [JitPack](https://jitpack.io/docs/#custom-domain-name) describe that `groupId` registration is done using a domain name. For example, to publish something to `com.google.code.gson`, you need to create a DNS TXT record for the domain `gson.code.google.com`. This identity confirmation prevents dependency substitution, allowing developers to safely use dependencies and plugins in their projects if they trust their creators.

## Method of attacks

As we mentioned above, the main defense mechanism depends on the ability to add DNS records for a particular domain. However, what happens if a developer abandons their project and does not renew the domain name registration?

Our attack strategy envisioned the following:

1. Search for abandoned dependencies added to known repositories.

2. Buying the appropriate domain.


3.1. In most cases, developers publish their artifacts in only one repository. Dependencies are searched and downloaded in the order of repository declaration, although Android Studio suggests upgrading to the newest version of a dependency and warns when new versions are available. An attacker can gain access to a vulnerable `groupId` by asserting their rights to it via a DNS TXT record in a repository where no account managing the vulnerable `groupId` exists.

3.2. If a `groupId` is already registered with the repository, an attacker can attempt to gain access to that `groupId` by contacting the repository's support team. The attacker has a reason to transfer access, such as owning the domain name or having an official email account on that domain. However, we have no information about the procedures for transferring permissions for `groupId`, and they may differ from repository to repository as they do not have a common standard.

## Verifying the theory

We don’t think it’s ethical to put tests on real dependencies, because it may lead to failures in CI/CD builds of many developers and the introduction of our test code into many projects. Instead, we did our research on the `groupId` set to `com.oversecured`.

For our research, we used the `mavenCentral` and `jitpack` repositories to understand their processes for onboarding new projects. We created an Android library `hello-world` that outputs `Hello world!`:

![](https://framerusercontent.com/images/sQWNfndVDHvC1PO6HdQgD28LwG4.png?width=1296&height=386)

Next, we uploaded the `com.oversecured:hello-world:1.0` dependency into `mavenCentral()`. The process was as follows:

1. Claiming the `groupId`, confirmation of which required creating a DNS TXT record with a randomly generated value. Confirmation took a few seconds


![](https://framerusercontent.com/images/9VpbTFwPlEoOJ2S9XkLIXZFAysA.png?width=3134&height=706)

2. Creating a deployment via Android Studio and uploading it


![](https://framerusercontent.com/images/CtODI3bOP5S7snzpLvXUYqp7Ow.png?width=3092&height=1064)

3. Dependency made available in [repository](https://repo.maven.apache.org/maven2/com/oversecured/hello-world/)


![](https://framerusercontent.com/images/SBumdli1Om0Ee4VEwrl2fTL6s6A.png?width=1210&height=1034)

4. With default Android project settings, it also became available in Android Studio


![](https://framerusercontent.com/images/y0o7fIpDWNlE0G0ARCU9lbwrac.png?width=1630&height=660)

![](https://framerusercontent.com/images/8CHSORi2HNfXD2kJxL0O2OFfmHk.png?width=1724&height=1054)

We then uploaded the same dependency into the `jitpack` repository with versions `1.0` and `1.1`. Version `1.0` was a copy of what was uploaded to `mavenCentral()`. `1.1` was an edited copy. The process was as follows:

1. Binding the `jitpack` account to the test GitHub repository

2. Granting access to private GitHub repositories

3. Claiming the `com.oversecured``groupId` via adding a DNS TXT record to reference the GitHub username


![](https://framerusercontent.com/images/6OGq3678fGbi0fpUh5oynS6C4F0.png?width=1304&height=350)

4. Submitting version `1.0` to the repository


![](https://framerusercontent.com/images/IaFKzC0YIRUJFoxitj2ui56uU.png?width=866&height=340)

5. Changing code and submitting version `1.1`, versions also made available at [https://jitpack.io/com/oversecured/hello-world/1.1/](https://jitpack.io/com/oversecured/hello-world/1.1/)


![](https://framerusercontent.com/images/sQWNfndVDHvC1PO6HdQgD28LwG4.png?width=1296&height=386)

![](https://framerusercontent.com/images/4voqV0rzOcRzNsxxvLzUNQicLuY.png?width=2352&height=2414)

After we added `https://jitpack.io` to the list of repositories for Gradle

![](https://framerusercontent.com/images/Ok1jxbps2Ka8BR6Fotm3QbUc8vk.png?width=1698&height=744)

Android Studio started urging us to update the `hello-world` version of the library

![](https://framerusercontent.com/images/0sWgPOhmyGulaTpG9BBf9gvSiV8.png?width=1706&height=1146)

We got the following results:

1. When we moved the `jitpack` repository above `mavenCentral`, version `1.0` was downloaded from `jitpack`

2. Changing the library version to `1.1` resulted in using the `jitpack`version regardless of the position of `jitpack` in the repository list


## Attack vectors for different project types

Types of attacks against web and mobile applications:

1. Attack against existing versions of a library. If the attacker’s repository is higher on the attacked project’s list than the legitimate one, the attacker can write existing copies of the library with embedded malicious code. With default settings, most libraries are vulnerable to this type of attack (see [Existing Defenses](https://blog.oversecured.com/Introducing-MavenGate-a-supply-chain-attack-method-for-Java-and-Android-applications/#existing-defenses)).

2. Attack against new versions. As shown, the attack is also possible when the attacker’s repository is lower on the list than the legitimate one. Most applications do not check the digital signature of dependencies, and many libraries do not even publish it. If the attacker wants to remain undetected for as long as possible, it makes sense to release a new version of the library with the malicious code embedded, and wait for the developer to upgrade to it.


### Types of attacks against libraries:

1. The `groupId` of the library should be checked for hijackability, because projects using it may be vulnerable.

2. Library dependencies are checked not in the library, but in the project that uses it. They will be transitive dependencies for that project, but they will be searched according to the repository declarations in that project.


## Existing defenses

Developers should remember that the default configuration does not validate dependencies in any way. This immediately makes it possible to intercept artifacts in dependencies and inject malicious code into the application.

Currently, there are only two options to protect Gradle projects from this type of attack:

1. [Checking the hash sums of files](https://docs.gradle.org/current/userguide/dependency_verification.html#sec:checksum-verification) injected into the project. This can be considered a good defense if the developer does not update the library versions and uses the same one. When updated, it does not protect against artifact spoofing in any way. This protection can be compared to the use of static `jar` libraries in the `libs` folder

2. [Checking digital signatures of dependencies](https://docs.gradle.org/current/userguide/dependency_verification.html#sec:understanding-signature-verification) via `.asc` files. Such files are requested by many repositories when publishing artifacts, but there is no efficient way to verify these signatures. First, to verify the signature, the dependency must publish its public key in advance and the developer using the dependency must specify it in its `gradle/verification-metadata.xml` file. This is the best existing defense against the attacks described in this article, but the big problem is that a minority of dependencies publish it in their manuals. There is a way to figure out the dependency signature through the digital signature verification command. To do this, load the `file` and `file.asc` files and run the `gpg --verify file.asc`command. Since there is no public key, it will always give an error, but it will also output the value of `keyid`. Next, the developer can try to find the specified key in public key repositories as follows: `gpg --keyserver keyserver.ubuntu.com --recv-keys {key_value}` (other public repositories are `keys.openpgp.org` and `pgp.mit.edu`). For example, `mavenCentral` [documentation](https://central.sonatype.org/publish/requirements/gpg/#distributing-your-public-key) says that publishing the public key is mandatory, but in our testing we were able to successfully upload a signed dependency without publishing a public key and use it in our application.


## Problems in implementing defenses against dependency hijacking

To understand the scale of the problem of dependencies not having signatures or dependency developers not publishing their public keys, we can recommend running

./gradlew --write-verification-metadata pgp,sha256 --export-keys

which will automatically create the `gradle/verification-metadata.xml`file to validate the public keys of current dependencies.

When we ran the command, we noticed a huge number of unsigned dependencies from Google

![](https://framerusercontent.com/images/yagxMLvwP28toQnq2TfgP7i8Rs.png?width=2688&height=1720)

But after checking numerous dependencies in [their official repository](https://maven.google.com/web/index.html), it turns out that they don’t sign any artifacts at all. We contacted Google regarding this issue and are awaiting their response.

Many Apache dependencies weren’t validated either because Gradle didn’t find their public key on any server. Probably because they forgot to publish it.

![](https://framerusercontent.com/images/3BmRAI3GA4S4c6V7zYUXfuHmE.png?width=2724&height=1692)

## Total number of vulnerable dependencies

We really wanted to understand the scale of the problem. It is impossible to know the final numbers objectively, because many public repositories do not disclose all the dependencies they host that could be checked for possible attacks. But `mavenCentral`, the largest and default repository for Android and many Java projects, discloses all the statistics, so we did the following research:

1. Took all the `groupId` values from `mavenCentral` and converted them to domains.

2. Checked these domains to see if they could be immediately purchased or auctioned using the [GoDaddy Bulk Domain Search tool.](https://www.godaddy.com/domains/bulk-domain-search/) GoDaddy does not register some national domains, so we had to check them through their national registrars.


We got the following data:

1. Total number of domains: 26,163 (`MavenCentral_all.txt`)

2. Number of vulnerable: 3,710 or 14.18% (`MavenCentral_vulnerable.txt`)


Many public repositories, including `mavenCentral`, allow private developers to use their GitHub accounts. But the issue is, when a user changes their GitHub username, it becomes available for registration. So we also checked them (`io.github.*` values) and got the following statistics:

1. Total number of GitHub projects: 7,523 (`MavenCentral_github_all.txt`)

2. Number of vulnerable: 291 or 3.86% (`MavenCentral_github_vulnerable.txt`)


To identify vulnerable companies, we scanned the private repositories we were able to find as well. Therefore, the overall statistics are as follows:

1. Total number of domains: 33,938 (`all.txt`)

2. Number of vulnerable: 6,170 or 18.18% (`vulnerable.txt`)


[Download all files](https://blog.oversecured.com/Introducing-MavenGate-a-supply-chain-attack-method-for-Java-and-Android-applications/#)

We should also note that we believe publishing the lists is not only an ethical action, but also necessary for the following reasons:

1. Anyone can get lists of vulnerable domains/projects, as we did, in a short period of time by writing a few simple scripts

2. This can help both library developers to quickly find out if their project is vulnerable, and dependency users to quickly check their dependencies.

3. Ultimately, it will help detect new attacks, as registering domains or GitHub accounts from the list and publishing artifacts under them should be an alert to the community


## Vulnerable dependencies in real projects

We have checked popular open-source Android applications, POM files of publicly distributed and open-source libraries for this vulnerability. As it turned out, many Android and Java projects are affected by the described problem. Although we can’t give real examples right now, because by the time this article was published we either haven’t had time to coordinate vulnerability disclosure with high-profile companies, or they haven’t had time to fix them. However, we can say that we have sent vulnerability disclosures to Google, Facebook, Amazon, Microsoft, Adobe, LinkedIn, Netflix, and over two hundred other companies.

Here’s what the top 20 statistics on abandoned and vulnerable dependencies look like:

| GROUP ID | % (AMONG VULNERABLE) |
| --- | --- |
| co.fs2 | 10.6305 |
| net.jpountz.lz4 | 4.2146 |
| org.mvel | 3.6001 |
| org.tpolecat | 3.288 |
| com.opencsv | 3.1148 |
| io.repaint.maven | 2.3336 |
| com.coderplus.maven.plugins | 2.3042 |
| com.agilejava.docbkx | 1.9839 |
| org.scalaj | 1.8499 |
| org.picketbox | 1.5558 |
| io.argonaut | 1.5231 |
| org.spire-math | 1.4152 |
| com.boundary | 1.273 |
| org.tmatesoft.svnkit | 1.1636 |
| org.cassandraunit | 1.1292 |
| org.ini4j | 0.9887 |
| tk.mybatis | 0.9004 |
| com.keyboardsamurais.maven | 0.8024 |
| org.derive4j | 0.7877 |

## Recommendations from Oversecured

**For all developers**. First, you need to make sure that there are no abandoned direct or transitive dependencies in your project whose domain attackers can buy and then either re-release all existing versions or release only new ones (which, as we have seen, in the current state of affairs will make it almost impossible to detect an attack). Second, you need to generate a `verification-metadata.xml` file and gradually update it when dependency developers fix bugs in their signature or public key distribution. Third, make sure that all your used repositories are trusted.

### For library developers

You have a big responsibility to protect your users. Therefore, you need to make sure that the project domain does not expire or get bought out by threat-actors. Next, make sure that all versions are properly signed and the key can be found on one of the servers listed.

### For repositories

You may want to require library developers to properly configure the deploy and not accept incorrectly configured releases.

### For security researchers

You may want to start checking for open-source libraries and notify repositories and affected developers that a particular dependency may be under attack. To detect existing attacks, it is worth checking artifact signatures among all versions and on all public repositories where possible.

### For the whole community

The current system with PGP signing is probably outdated, because it adds an extra step of uploading the public key to third-party services. If Apache, the developer of Maven, gets this step wrong in some cases, what does this say about everyone else? Moreover, the PGP-based signature verification system is very centralized and if these three servers are offline, it can break many builds. Thus, we want to raise the issue of implementing a new signing and verification system. Right now, all security relies on what repositories a developer has added to their project. We believe that the public key should be uploaded along with the artifacts so that their author can be immediately verified regardless of the repository used. An additional security improvement should be a declaration of the public key hash together with a dependency declaration, e.g., `implementation 'groupId:artifactId:version:sha256signature'`. The last important improvement, from our point of view, should be the change of responsibility. Nowadays the library developer declares dependencies in the `pom.xml` file, which are searched for in projects that use these libraries. The end developer is responsible for security not only for direct dependencies, but also for transitive dependencies. We believe that library developers should be responsible for the dependencies they declare and also write public key hashes for their dependencies, while the end developer should be responsible only for their direct dependencies.

## Timeline

- 01/19. Sonatype, owner of the `mavenCentral` repository, [gave their comment](https://www.sonatype.com/sonatypes-ongoing-commitment-to-maven-central). We were happy to assist them in blocking vulnerable dependencies and finding bugs with the lack of public key verification of uploaded artifacts, which should make the Java ecosystem a safer place.

- 02/23. We noticed that Sonatype’s comment confused some readers. However, we want to point out that Sonatype has not fixed this vulnerability and cannot fix it because the attack becomes possible when multiple public repositories are used. For example, if an abandoned dependency is uploaded to JCenter, but the first repository on the list is Maven Central, then hijacking the dependency becomes possible through the Maven Central repository as well. The only thing any public repository owner can do in this case is to prohibit automatic claiming of vulnerable `groupId` values.


##### Keep reading

[View all](https://oversecured.com/blog)

[![](https://framerusercontent.com/images/OnN0UKCOhnnXin2eBts9J3SaUQ.png?width=5592&height=3259)\\
\\
20 Security Issues Found in Xiaomi Devices\\
\\
Oversecured found and resolved significant mobile security vulnerabilities in Xiaomi devices. Our team discovered 20 dangerous vulnerabilities across various applications and system components that pose a threat to all Xiaomi users. The vulnerabilities\\
\\
Case Study\\
\\
May 2, 2024\\
\\
15\\
\\
min read\\
\\
TOp article](https://oversecured.com/blog/20-security-issues-found-in-xiaomi-devices)

[![](https://framerusercontent.com/images/W9Wn9vbZPPJFNH7MN7Zx6QXches.png?width=2048&height=1194)\\
\\
Android deep link vulnerabilities: how intent filters lead to account takeover\\
\\
A technical guide to Android deep link security. Learn how intent filter misconfigurations lead to account takeover, and how mobile application security testing with SAST and DAST finds these vulnerability chains.\\
\\
Android Security\\
\\
Apr 27, 2026\\
\\
8\\
\\
min read](https://oversecured.com/blog/android-deep-link-vulnerabilities)

[![](https://framerusercontent.com/images/xSiSLs1y7y6Mzr4lWYWCpFoYmM4.png?width=2848&height=1656)\\
\\
Android security checklist: theft of arbitrary files\\
\\
Developers for Android do a lot of work with files and exchange them with other apps, for example, to get photos, images, or user data. \\
\\
Android Security\\
\\
May 20, 2022\\
\\
11\\
\\
min read\\
\\
TOp article](https://oversecured.com/blog/android-security-checklist-theft-of-arbitrary-files)

Book a personalized demo

During the demo with our cybersecurity experts you will get:

A free trial scan of your app

An analysis of your SAST and DAST findings

Practical insights on mobile security of your app

First name

Business email

How did you hear about us?

Book a demo

2026 © Oversecured

follow us

### [LinkedIn](https://www.linkedin.com/company/oversecured/)

### [Twitter (X)](https://x.com/oversecuredinc)

[Privacy Policy](https://oversecured.com/privacy)

[Terms of use](https://oversecured.com/terms)

[go up ↑](https://oversecured.com/blog/introducing-mavengate-a-supply-chain-attack-method-for-java-and-android-applications#header)

Chat Widget