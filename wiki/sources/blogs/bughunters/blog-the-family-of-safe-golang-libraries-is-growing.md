---
source: bughunters
source_url: https://bughunters.google.com/blog/the-family-of-safe-golang-libraries-is-growing
title: "The Family of Safe Golang Libraries is Growing! - Google Bug Hunters"
description: "Introducing three new open-source libraries in Go that provide secure and efficient solutions: SafeText, SafeOpen, and SafeArchive."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/the-family-of-safe-golang-libraries-is-growing#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# The Family of Safe Golang Libraries is Growing!

![](https://storage.googleapis.com/bughunters-article-images/blogs/imrer.jpg)

Imre Rad

Information Security Engineer

Published: Feb 26, 2024

Security Engineering

[RSS Feed](https://bughunters.google.com/feed/en)

# The Family of Safe Golang Libraries is Growing!

We are thrilled to introduce three new open-source libraries in Go that provide
secure and efficient solutions:

- [SafeText](https://github.com/google/safetext) for YAML and shell command
templating
- [SafeOpen](https://github.com/google/safeopen) for opening files in a base
directory
- [SafeArchive](https://github.com/google/safearchive) for processing archive
files

These libraries have been meticulously crafted to address common secure coding
challenges, protecting against the following weaknesses from the
[CWE Top 25](https://cwe.mitre.org/top25/archive/2023/2023_stubborn_weaknesses.html):

- #5 [CWE-78](https://cwe.mitre.org/data/definitions/78.html): Improper
Neutralization of Special Elements used in an OS Command ('OS Command
Injection')
- #6 [CWE-20](https://cwe.mitre.org/data/definitions/20.html) (special cases
of) Improper Input Validation
- #8 [CWE-22](https://cwe.mitre.org/data/definitions/22.html) Improper
Limitation of a Pathname to a Restricted Directory (‘Path Traversal’)

The Safe libraries offer robust protection mechanisms. By leveraging them, you
can perform these primitive operations in a vulnerability-free manner – even if
the input is attacker-controlled.

## SafeText

[SafeText](https://pkg.go.dev/github.com/google/safetext) was the first member
of the "safe family" that we published at the beginning of 2023, and GitHub is
already tracking hundreds of integrations. So what is SafeText? And what is it
useful for?

The story started with identifying a number of applications that constructed
YAML documents with the help of Golang’s
[text/template](https://pkg.go.dev/text/template). This approach is vulnerable
to YAML injection unless all inputs are validated carefully. Expecting all users
to do this properly is error prone and hard to scale: we prefer solutions that
are safe-by-default.

### YAML

SafeText was designed to be a drop-in replacement of `text/template`; you can
use it to process your YAML template in the same way that you used
`text/template`. The difference is that the SafeText library returns an error
when an injection attempt is detected.

Let’s see an example! Given the following template:

```
---
sensitive: data
innocent: "{{ .input}}"
```

If an attacker controls the value of `.input`, they could inject newline
characters and override other fields or change the structure of the document.
Depending on the use-case, the impact could be critical, for example when the
result is used as a configuration file for a production system.

Switching to SafeText is as easy as adjusting the corresponding import line:

`text/template` becomes `template "safetext/yamltemplate"`

When the same attack is attempted again, SafeText would return the error: `YAML Injection Detected`, and prevent the attack.

### Shell commands

Building on the original YAML feature of the library, we decided to also add
support for templating shell commands. `shsprintf` was designed to ensure that
none of the input data strings would be able to inject additional commands or
flags regardless of potentially incorrect escaping.

Consider the following (vulnerable) example:

```
result := fmt.Sprintf("git commit -m %s", message)
```

If the `message` variable is attacker-controlled and the concatenated string is
executed at some point, then this is a vulnerability. Depending on the exact
execution of the attack, either OS commands or parameters to the executable (git
cli in this example) could be injected.

This is where `shsprintf` comes to the rescue! Two different syntaxes are
supported:

```
message := "`whoami`"
result, err := shsprintf.Sprintf("git commit -m %s", message)
```

Or

```
message := "`whoami`"
result := shsprintf.MustSprintf("git commit -m %s", shsprintf.EscapeDefaultContext(message))
```

Both variants detect injection attempts. The first one returns an error, the
second one panics. In addition, there is a third option: you can use the
`shtemplate` feature of SafeText and build your shell commands with the help of
templates (similar to `text/template`).

## SafeOpen

[SafeOpen](https://pkg.go.dev/github.com/google/safeopen) was designed to
protect against path traversal attacks – it does so by providing functions to
open files within a base directory. The idea is simple: you specify a trusted
root directory and the library enforces that file operations cannot break out of
this directory. This offers robust protection in cases where the pathname of the
file to open is attacker-controlled (meaning it may include `../ path`
components) or the root directory is “dirty” (e.g. it contains symbolic links).

The SafeOpen library leverages the best available OS-level primitives (e.g.
openat2 + RESOLVE\_BENEATH, falling back to openat for Linux kernel < 5.6.0).
Thanks to this construct, SafeOpen is safe to use even in shared environments
where an attacker could mount race condition attacks
( [TOCTOU](https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use)). The
Windows operating system is also supported.

Two modes are supported:

- _At_ ensures that the file to open is located directly in the root directory
(and not in a subdirectory)
- _Beneath_ specifies that the file to open may be located in a subdirectory
of the root directory

The wrapper functions are implemented for the following OS-level primitives:

- `os.Open`
- `os.OpenFile`
- `os.Create`
- `os.ReadFile`
- `os.WriteFile`

An example open would look like this:

```
rootDir:= "/data"
f, err := safeopen.OpenBeneath(rootDir, userInput)
if err != nil {
	t.Fatalf("OpenBeneath(%q, %q) error: %v", rootDir, userInput, err)
}
// ... use f as an *os.File just like before
```

SafeOpen is part of a larger engineering effort to address path traversal issues
– we’ll be publishing a dedicated blog post about that in the near future.

## SafeArchive

[SafeArchive](https://pkg.go.dev/github.com/google/safearchive) is a set of
safe-by-construction libraries designed to prevent path traversal attacks (aka
zip slip) as well as various attacks related to the handling of archive files.
This library was designed as a drop-in replacement of Golang core’s
[archive/tar](https://pkg.go.dev/archive/tar) and
[archive/zip](https://pkg.go.dev/archive/zip), so switching to SafeArchive is as
easy as adjusting the import line:

`import "archive/tar"` becomes `import "safearchive/tar"`

By using SafeArchive, malicious entries in crafted archives are sanitized. For
example, if the library encounters a `.zip` file with a rogue
`../../../etc/cron.daily/cronjob` entry, it sanitizes the name and returns it as
`etc/cron.daily/cronjob` instead. In addition, the following extra protection
measures are implemented:

- Skipping special files (e.g. device nodes)
- Sanitizing file modes (e.g. clear the setuid bit)
- Sanitizing file name (to prevent path traversal attacks)
- DropXattrs (to prevent abusing extra filesystem ACLs or capabilities)
- Preventing traversal via symbolic links

This functionality can be fine-tuned using the `SetSecurityMode` method of the
reader. The default settings are both secure and non-breaking.

## Summary

The three Golang libraries showcased in this blog post offer safe-by-design
solutions that address the root causes of entire vulnerability classes. They are
widely used inside Google: we encourage our developers to adopt them with the
help of linters :).

Now that these libraries are also open to the public, we recommend you adopt
them and hope they will eventually save the day for your applications as well.
For more information, including detailed documentation and usage examples,
please visit the following links:

- [SafeText](https://pkg.go.dev/github.com/google/safetext)
- [SafeOpen](https://pkg.go.dev/github.com/google/safeopen)
- [SafeArchive](https://pkg.go.dev/github.com/google/safearchive)

And join us in welcoming them to the "safe family"!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab