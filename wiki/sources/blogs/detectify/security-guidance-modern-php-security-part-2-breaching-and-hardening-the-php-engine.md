---
source: detectify
source_url: https://labs.detectify.com/security-guidance/modern-php-security-part-2-breaching-and-hardening-the-php-engine/
title: "Breaching and hardening the PHP engine - Labs Detectify"
author: "Detectify"
published: 2020-08-20T09:37:21+00:00
description: "Bugs that can get around the PHP engine's security, and tips on additional security layers that will lessen the damage when breached."
---

[Home](https://labs.detectify.com/)/ [Security guidance](https://labs.detectify.com/category/security-guidance/)/ [Modern PHP Security Part 2: Breaching and hardening the PHP engine](https://labs.detectify.com/security-guidance/modern-php-security-part-2-breaching-and-hardening-the-php-engine/)

[Security guidance](https://labs.detectify.com/category/security-guidance/ "Security guidance")

# Modern PHP Security Part 2: Breaching and hardening the PHP engine

**Lena David & Thomas Chauchefoin** Aug 20, 2020

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/modern-php-security-part-2-breaching-and-hardening-the-php-engine/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/modern-php-security-part-2-breaching-and-hardening-the-php-engine/ "Share on LinkedIn")

![Modern PHP Security Part 2:  Breaching and hardening the PHP engine](https://labs.detectify.com/_next/image/?url=https%3A%2F%2Flabsadmin.detectify.com%2Fapp%2Fuploads%2F2023%2F08%2Fthumbnail.png&w=3840&q=75)

**On to Part 2 of modern PHP security. Security researcher and Detectify Crowdsource hacker Thomas Chauchefoin (@swapgs) and fellow Synacktiv security researcher Lena David (@\_lemeda) discuss modern PHP security.**

We go into specific bugs that can get around the PHP engine’s security boundaries, and tips on additional security layers that will lessen the damage when breached.

If you missed part 1, [find it here.](https://labs.detectify.com/2020/08/13/modern-php-security-part-1-bug-classes/)

## Engine bugs

Let’s put ourselves in the scenario where a site on a shared hosting is vulnerable to CVE-2017-9841 (`/phpunit/phpunit/src/Util/PHP/eval-stdin.php`):

```
'.file_get_contents('php://stdin'));
```

Even if this primitive may look really great at first, the PHP engine can be configured to disallow the call of functions (except `eval`, being a language keyword), restrict access to some folders (like a chroot), etc. Even if we can execute arbitrary PHP code, the Zend virtual machine won’t let us execute arbitrary native code to easily circumvent it. Native code execution is limited to C modules, which can not be loaded at runtime after engine’s initialization.

**Numerous engine bugs can exist:**

- memory safety issues (all kind of buffer / heap \*flows)
- reference counting issues and garbage collection leading to use-after-free conditions
- command or parameter injection
- logic issues

These bugs can allow getting around the engine’s boundary and security measures, as presented in the following examples. None of the methods described below are new, they were described on various websites—we tried to reference the oldest occurrence of an article mentioning it but it is always hard to give the proper attribution.

### Bug \#76428 (imap\_open, duplicated to \#77153), CVE-2018-19518

[CVE-2012-19518 was opened by c.r.l.f](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-19518) regarding `imap_open`’s behavior on PHP < 5.6.39 / < 7.2.13. Internally the third-party IMAP library uses `rsh` (often linked to `ssh`) to connect to the server. The name of the server was not enclosed by quotes when creating the command string and could contain spaces to add arguments to `ssh`’s invocation. Arguments injection on `ssh` can be easily exploited by passing –`oProxyCommand`.

### Bug \#46741 (putenv)

This bug by gat3way is based on the fact that, when executing external commands through `system()` or `popen()` (the libc functions, not their PHP counterparts), environment variables are inherited by the child process. Environment variables such as `LD_PRELOAD` or `LD_LIBRARY_PATH` will influence the operations of the system’s dynamic linker and allow loading an arbitrary shared library in the child process’ memory space (eg. executing native code).

Engine’s environment variables can be affected by a call to `putenv()` and functions like `mail()`, `mb_send_mail()`, `error_log()`, imap\_open() and `imap_email()` will spawn external processes to accomplish their tasks.

TarLogic made a tool named [Chankro](https://github.com/TarlogicSecurity/Chankro/) to spawn a meterpreter using this technique.

### mail() _(again!)_

The last parameter of `mail()` is known to allow parameter injection when `sendmail` is called, resulting in the ability to create mail’s contents on an arbitrary destination on the server. Depending on the server’s configuration, this could allow executing arbitrary commands. This trick is not new but was recently [highlighted by RIPSTech](https://blog.ripstech.com/2017/why-mail-is-dangerous-in-php/).

### Bug \#76047 (getBacktrace)

This bug was finally patched after two years in 7.2.28 / 7.3.15 / 7.4.3 (7.0 and 7.1 are obsolete), and was found unexpectedly by [@kenashkov](https://twitter.com/kenashkov). An issue in the backtraces mechanism allows accessing the argument of a parent function, while this memory backing this value may have been already liberated by the engine. It allows obtaining two distinct references (as in, two distinct PHP variables) to the same memory area, which is not supposed to happen. These variables can even be of different types, thus with a different native representation, allowing to manipulate the internal fields of an object B if they overlap with a controlled memory used to represent A.

We originally wanted to describe this bug in our talk but it was not easy to stay relevant without describing its exploitation in detail, which was not the goal of our submission. Last month, [@0x\_shaq](https://twitter.com/0x_shaq) published a very nice article about [this same bug and its exploitation](https://github.com/0xbigshaq/php7-internals/tree/master/0x08%20%5Bbug%20%2376047%5D%20Bypassing%20disable_functions), you should read it!

### Your own bug!

As we already stated, bugs that are likely to be only locally triggered (eg. it requires to plant a file on the server beforehand, an uncommon sequence of function calls) are not part of the maintainer’s threat model, but that’s what we need in this case. Browsing [https://bugs.php.net](https://bugs.php.net/) may be a great source of potentially exploitable issues and inspire you before reading the engine’s source code.

## Hardening tips

Despite your best efforts and will, it is safe to assume that your application will get compromised. This does not mean that you will be the one at fault when that occurs, as security issues may have origins as diverse as third-party code you don’t control, legacy code that ended up still being present in your application and that you cannot git blame because it comes from who-knows-where, or even your favorite CMS or one of its modules.

Thus, it appears relevant to think of additional security layers that will limit the damage when an attacker manages to break into your application. This can be achieved by hardening the configuration of the underlying system on the one part, and that of the engine itself on the other part, as we will describe in the following sections.

## System configuration

Regarding system configuration, several leads can be considered.

The first one comes from the observation that getting persistence on a filesystem is much harder if it is read-only. A key drawback to keep in mind here is that relying on a read-only filesystem will also make updates and other legitimate modifications more painful.

Another option, which may be easier to implement, would consist of storing uploads in a location that is not under the web root; for instance, on a different volume, an external service, or a dedicated host. This will help reduce the potential impact if a security issue leads to direct uploading of PHP files.

Further pathways involve the pool mechanism of PHP-FPM, which provides UID separation and a chroot mechanism. Systemd can also be used to restrict the available address families and syscalls and to enforce mount namespaces.

More broadly speaking, ensuring the language engine and the related libraries are kept up-to-date also contributes to hardening one’s system.

## Engine configuration

Even if the following steps are likely to only slow down an attacker, it is a good security practice to enforce them. It will make the initial compromise (eg. gaining code execution) harder without creating any extra complexity during your deployments.

The following configuration directives are exposed by the engine and will allow to improve its security:

- `error_reporting / display_startup_errors / display_errors`: set them to `Off`, but keep `log_errors / error_log` to still be able to identify issues
- `open_basedir`: limit reachable paths
- `disable_functions / disable_classes`: limit callable / instantiable symbols. Not that `eval` is a language’s construct and can’t be disabled.
- `allow_url_fopen / allow_url_include`: limit risks of remote file inclusion (but does not prevent it over SMB, see [https://bugs.php.net/bug.php?id=78005](https://bugs.php.net/bug.php?id=78005)).

The tool [PCC](https://github.com/sektioneins/pcc/blob/master/phpconfigcheck.php) is still regularly updated and will scan your `php.ini` and tell you how to improve it.

We mentioned `disable_functions`, but how to craft a good list of exclusions? Numerous websites try to establish a viable list but it is not an easy task and will directly depend on your environment. For instance, we showed in section Public bypasses of `disable_function` that `putenv` can be dangerous if you left access to `mail` or `error_log`. By itself, `mail` (and its `buddy mb_send_mail()`) is dangerous but you most likely will need it if you don’t want to introduce a new dependency like PHPMailer.

## Third-party modules

Third-party modules can be used to extend PHP and to provide additional security measures. Suhosin was  commonly used “back in the day” and offered interesting functionalities (some of them could only be implemented through a patch, not only a module):

- “true” URL inclusion protection (disallow all schemes, writable files, …)
- Zend Memory Manager hardening
- Cookie encryption
- Custom POST / multipart handler
- Pledge support (OpenBSD only)

However, it has no PHP 7 (and furthermore PHP 8) support and was slowly deserted. A new project, named [suhosin-ng](https://github.com/sektioneins/suhosin-ng) and also supported by SektionEins was announced last year. Instead of starting everything from scratch again or porting their old code, the idea is to review and add relevant functionalities to [Snuffleupagus](https://github.com/jvoisin/snuffleupagus).

The idea behind Snuffleupagus is smart, and their slogan makes it easy to understand what they are doing: _Killing bugclasses and virtual-patching the rest!_

This module introduces several application-level hardening features :

- apply callbacks when performing file uploads
  - VLD pass to detect valid PHP opcodes in a file
  - further custom sanitations?
- block calls when parameters are matching a given regex
  - allows dealing with software requiring dangerous functions (eg. mail)
- signature of serialized strings to prevent their tempering
- prevent the execution of writable PHP files
- and much more…

Using it will definitely require some tuning if you are not using a common CMS (eg. [https://github.com/jvoisin/snuffleupagus/blob/master/config/typo3.rules](https://github.com/jvoisin/snuffleupagus/blob/master/config/typo3.rules) v) but it’s a good investment.

## Conclusion

As often advised, enforcing good security practices can be considered as a relevant first line of defense: validating all external data, including but not limited to user input, will make it way harder for a potential attacker to trigger a behavior they may successfully exploit. What is important to bear in mind is that once an attacker obtains code execution through a security issue affecting the application, they have won and are able to do what they want with it.

Applying the principle of in-depth security can be deemed as the right way to proceed, as it will definitely help curb the consequences of a potential security breach and prevent this point from being reached!

**If you missed part 1, [find it here.](https://labs.detectify.com/2020/08/13/modern-php-security-part-1-bug-classes/) This article is a transcription of the content we presented at [Sec4Dev 2020](https://sec4dev.io/) and [Detectify Hacker School Online #9](https://detectify.com/events/detectify-hacker-school).**

* * *

Do you have what it takes to join the Detectify Crowdsource ethical hacker community? [Send us your application and try the challenge to find out!](https://cs.detectify.com/apply?utm_source=labs&utm_campaign=enginebugsharden)

[Detectify](https://detectify.com/?utm_source=labs&utm_campaign=enginebugsharden) automates the knowledge of the best ethical hackers in the world to secure websites against 2000+ known vulnerabilities beyond OWASP Top 10. With Detectify, users monitor subdomains for potential takeovers and remediate security bugs in staging and production as soon as they are known, to stay on top of threats _._ [Start a free 14-day trial today.](https://detectify.com/createaccount?utm_source=labs&utm_campaign=enginebugsharden)

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/security-guidance/modern-php-security-part-2-breaching-and-hardening-the-php-engine/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/security-guidance/modern-php-security-part-2-breaching-and-hardening-the-php-engine/ "Share on LinkedIn")

**Lena David & Thomas Chauchefoin**

Security Researchers

## Check out more content

The smaller our attack surface, the fewer things we need to worry about. An excellent way of reducing the attack surface (and our cognitive load) is using AWS Service Control Policies (SCPs.) In this post, I’ll describe how we approached it.

March 26, 2024

It’s no secret that cloud architectures have several characteristics that make SSRF attacks challenging to defend against. While SSRFs are not a new threat vector, …

September 23, 2022

TL/DR: AWS QuickSight makes it easy to build visualizations, perform ad-hoc analysis, and quickly get business insights from their data, anytime, on any device. Hacker …

May 30, 2022

TL/DR: On December 2, open-source analytics solution Grafana released an emergency security patch for critical zero-day Path Traversal vulnerability CVE-2021-43798, after proof-of-concept code to exploit …

December 15, 2021