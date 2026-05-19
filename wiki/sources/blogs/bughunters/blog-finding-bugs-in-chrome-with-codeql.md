---
source: bughunters
source_url: https://bughunters.google.com/blog/finding-bugs-in-chrome-with-codeql
title: "Finding Bugs in Chrome with CodeQL - Google Bug Hunters"
description: "Want to learn about using a static analysis tool called CodeQL to search for vulnerabilities in Google Chrome? Then this blog post is for you!"
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/finding-bugs-in-chrome-with-codeql#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Finding Bugs in Chrome with CodeQL

![](https://storage.googleapis.com/bughunters-article-images/blogs/flowerhack.jpg)

Julia Hansbrough

Software Engineer, Chrome Security

Published: Nov 21, 2024

Vulnerability Reward Program  Chrome

[RSS Feed](https://bughunters.google.com/feed/en)

# Finding Bugs in Chrome with CodeQL

This blog post discusses how to use a static analysis tool called CodeQL to
search for vulnerabilities in Chrome.

**Tip:** You can download Chromium CodeQL databases
[here](https://console.cloud.google.com/storage/browser/chrome-codeql-databases);
send any feedback to
[codeql-discuss@chromium.org](mailto:codeql-discuss@chromium.org)!

## What is CodeQL? And why CodeQL?

[CodeQL](https://codeql.github.com/) is a query language for source code, which
can be used for searching for bugs in your codebase.

To enable CodeQL for your codebase, first, you would need to generate a CodeQL
_database_, which contains _semantic information_ about your code. Doing so
would then allow you to perform a far more sophisticated analysis of your
codebase than would be possible using a simple `grep`.

This characteristic makes CodeQL an excellent tool for performing **variant**
**analysis** — that is, if you already know about _one_ instance of a security bug
(say, one that was
[recently disclosed](https://bugs-chromium.bentkowski.info/)), you may suspect
that other bugs of a similar type still exist in the codebase.

However, searching for those other bugs, either by manually paging through the
code, or by grepping for particular string patterns, often isn't as reliable as
one would like. The kind of query we'd _really_ like to run would require a
deeper understanding of the program's abstract syntax tree and syntactic data:
"show all instantiations of a class with a particular property," for instance.

And this is precisely the sort of analysis that can be done by a simple CodeQL
query. As an example, a simple query to find all POD (Plain Old Data) classes in
a C++ codebase might look like:

```
import cpp

from Class targetclass
where targetclass.isPod()
select targetclass, targetclass.getQualifiedName()
```

Or, for something more specific to Chrome, you could write a query to return all
[Mojo](https://chromium.googlesource.com/chromium/src/+/master/mojo/README.md)
interfaces:

```
import cpp

class MojoCppInterface extends Class {
   MojoCppInterface() {
     this.getQualifiedName().matches("%::mojom::%") and
     this.getAMember().hasName("Proxy_")
   }
 }

from MojoCppInterface mci
select mci, mci.getQualifiedName()
```

For more sophisticated examples, you can use CodeQL to perform tasks like:

- [Interactively exploring the abstract syntax tree for your source code](https://codeql.github.com/docs/codeql-for-visual-studio-code/exploring-the-structure-of-your-source-code/)
- Finding all calls to a function that lack a particular check prior to use,
or do not immediately return after use
( [example](https://source.chromium.org/chromium/chromium/src/+/main:tools/codeql/queries/bad_message_no_return.ql;l=1))
- Performing **taint analysis**, such as finding everywhere that a
user-controlled data source is able to "flow" to an array-offset or
pointer-arithmetic expression
( [Finding Gadgets for CPU Side-Channels with Static Analysis Tools](https://github.com/google/security-research/blob/master/pocs/cpus/spectre-gadgets/README.md))

## Chrome and CodeQL

Compiling a CodeQL database for a codebase as large and complex as Chrome is
somewhat time- and computationally-intensive, so we've made it easier for
researchers to dive in by building the databases for you. See here for the
[available CodeQL databases](https://console.cloud.google.com/storage/browser/chrome-codeql-databases)
(starting with the most recent).

In the course of building these databases, we noticed that these databases were
frequently _incomplete_. This is perhaps not surprising: Chrome is a massive
codebase, comprising over 85 million lines of code, compiled using a version of
Clang that closely follows upstream tip-of-tree, and making use of many of C++'s
newest language features. Off-the-shelf tooling often isn't designed to handle
codebases with Chrome's size and complexity.

Fortunately, the CodeQL team has
[a very active presence on GitHub](https://github.com/github/codeql/), and we've
been working with them to create standalone reproductions of these errors as we
find them & provide detailed reports to their team. Our teamwork has already
borne fruit: since CodeQL version 2.17.4, their team has landed over a dozen
fixes for issues reported by Chrome (for example, see
[here](https://github.com/github/codeql/issues/16782) and
[here](https://github.com/github/codeql/issues/16783)). These fixes have already
greatly increased the space of what's queryable in Chrome, and there's still
more fixes on the way on the way, with an ultimate goal of compiling a database
that can flawlessly query all of Chrome source.

To assist others in writing their own CodeQL queries, some queries that we've
already found useful for Chrome currently
[live in the source tree](https://source.chromium.org/chromium/chromium/src/+/main:tools/codeql/queries/;l=1),
and we're adding more all the time. Feel free to either reference them for your
own work, or extend them to write more powerful queries.

## How to Play

1. Download the
[most recent build](https://console.cloud.google.com/storage/browser/chrome-codeql-databases)
of the Chromium CodeQL database.

2. Import that database into VSCode via the CodeQL extension
( [detailed instructions](https://source.chromium.org/chromium/chromium/src/+/main:tools/codeql/README.md)).

3. Run an initial query. For example, here's one that leverages the `Ipc`
library provided by Chromium, and returns all methods on Mojo interface
implementations within Chromium:


```
import cpp
import lib.Ipc

from MojoImpl impl
select impl, impl.getAMethod()
```


See the
[detailed instructions](https://source.chromium.org/chromium/chromium/src/+/main:tools/codeql/README.md)
for more guidance on where to write your query, how to run a query, and so
forth.

You should see a result in the "CodeQL Query Results" pane after a few
minutes.

4. From there on out: happy querying! Check
[other queries used in the Chrome source tree](https://source.chromium.org/chromium/chromium/src/+/main:tools/codeql/queries/;l=1)
if you'd like some other ideas or more concrete examples.


## Wrapping Up

If you encounter any issues using the Chromium CodeQL databases, you can email
[codeql-discuss@chromium.org](mailto:codeql-discuss@chromium.org) and we'll get
back to you.

Vulnerabilities you discover using CodeQL _may_ be eligible for a reward through
Chrome’s Vulnerability Reward Program – with a strong emphasis on “may.” Why?
The Chrome Security and Engineering teams are only able to triage and
investigate reports of security issues that contain
[actionable information](https://g.co/chrome/vrp#update-to-policy-regarding-unactionable-reports-and-duplicates).
Speculative or theoretical reports of security issues based solely on code
analysis are _**not**_ generally eligible for a Chrome VRP reward.

Please ensure any security bug reports based on findings from CodeQL consist of
the expected and actionable characteristics of a Chrome security bug report,
such as:

- Proof of concept (PoC) / test case
- Symbolized ASAN stack trace
- Clear and concise steps to reproduce

Please see the [Chrome VRP rules and policies page](https://g.co/chrome/vrp) for
full information, and review the
[Report Quality](https://g.co/chrome/vrp#report-quality) section to ensure your
report meets eligibility criteria.

Happy bug hunting!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab