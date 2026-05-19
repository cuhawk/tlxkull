---
source: bughunters
source_url: https://bughunters.google.com/blog/fixing-debug-log-leakage-with-safe-coding
title: "Fixing Debug Log Leakage with Safe Coding - Google Bug Hunters"
description: "Logs are essential tools that help developers debug errors, but they can be problematic when developers don't know the data structure that they're logging. This can lead to unintentional logging of data such as cryptographic keys. Check out this blog to understand how Google prevents such logging errors by design, using safe-by-default APIs."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/fixing-debug-log-leakage-with-safe-coding#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Fixing Debug Log Leakage with Safe Coding

![](https://storage.googleapis.com/bughunters-article-images/blogs/tanxengineer.jpg)

Xufei Tan

Information Security Engineer

Published: Jan 15, 2024

Security Engineering

[RSS Feed](https://bughunters.google.com/feed/en)

# Fixing Debug Log Leakage with Safe Coding

Debug logs are instrumental for developers to understand what went wrong with
their programs. To provide the necessary debugging context, developers often log
complex data structures used in their programs (e.g. a request for a backend
service). However, developers may not _always_ know or remember exactly what the
data structure contains. This can lead to unintentional logging of information
that should not be accessible in debug logs (referred to below as "non-debug
info"), such as
[cryptographic keys](https://github.com/envoyproxy/envoy/issues/4757). While
Google has strict access control in place to limit log access for legitimate
debugging purposes, we would like to prevent such data from ever entering the
logs.

## Background

At Google, [Protocol Buffers](https://protobuf.dev/) (aka protobuf) is the
primary format to store and transmit structured data, and naturally many
protobuf objects contain fields that should not be in debug logs. DebugString is
the default debug API in C++, which prints out _**every**_ field within a proto
in an unredacted, human-readable format. It's quite common for developers to log
the entire DebugString representation of a proto, especially under error
conditions. This makes it easy to unintentionally overlog information. With
Google generating logs across massive infrastructure every day, how does Google
mitigate this risk systematically?

Google marks certain fields with
[protobuf annotations](https://protobuf.dev/programming-guides/proto2/#options),
and some teams write additional protobuf sanitizers to enforce that such fields
get redacted. Individual log sanitization is burdensome, easily forgotten, and
difficult to enforce. Nobody wants to accidentally log data that shouldn't be
logged, but **when the go-to API is unsafe by default, mistakes are almost**
**inevitable:**

```
message RequestContext {
  optional string name = 1;
  optional string value = 2 [(security.type) = SECURITY_KEY];
  ...
}

// In a different file owned by a different team...
message WebRequestData {
  optional string payload = 1;
  optional RequestContext context = 2;
  ...
}
```

_Protobuf message definitions_

```
// A straightforward example of mislogging
absl::Status HandleLogins(const RequestContext context, ...) {
...
LOG(INFO) << context.DebugString(); // Oops!
}

// ... and an example of a non-obvious mistake.
absl::Status HandleWebRequest(const WebRequestData data, ...) {
...
LOG(ERR) << data.DebugString(); // Oops!
}

// ... What if the logging function is also owned by a different team?
absl::Status PassToHandler(const WebRequestData data, ...) {
...
// Sometimes otherLib doesn't know it's touching non-debug info!
return otherLib::HandleWebRequest(data);
}
```

_Possible logging mistakes_

How can we prevent developers from accidentally logging these fields in protos?
In our experience, it is difficult to consistently avoid such logging errors
in basic scenarios by simply defining policies and ensuring developer education.
And it is practically impossible to avoid such bugs in any sufficiently complex
application, unless we **prevent logging errors by design with safe-by-default**
**APIs**.

Over the past years, we have used this _safe coding_ approach to eliminate
entire classes of security vulnerabilities. If we enforce that developers use
safe APIs by default, then we can prevent
[issues like XSS](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/42934.pdf)
and other difficult problems from ever occurring. What if we could apply the
same approach and make protobuf logging redact these fields automatically?

## Hyrum and Goping Dependencies

```
  // Generates a human readable form of this message, useful for debugging
  // and other purposes.
  std::string DebugString() const;
```

We would love to simply change the DebugString API to start redacting such
fields—a straightforward change that would address the problem immediately.
Unfortunately, changing the behavior of widely-used public APIs is complicated
by [Hyrum’s Law](https://www.hyrumslaw.com/). It states that _with a sufficient_
_number of users of an API, all observable behaviors of the API, whether intended_
_or not, will be depended on by somebody_. This is consistent with what we have
seen with DebugString, one of the most commonly used C++ API at Google.

We can categorize DebugString dependencies into two types, following Hyrum’s
Law:

- A **Hyrum dependency**, which depends on the unintended observable behaviors
of underlying APIs that they call upon.
- A **Goping dependency** \[1\], which follows the written contract and does not
depend on these unintended behaviors.

Hyrum’s Law applies to DebugString because developers often use it for
serialization, even though DebugString is an API designed for debugging. Users
rely on the API's observable behavior that the debug output is the same as
TextFormat, a human-readable serialization format. For applications that
deserialize DebugString output as if it was TextFormat, redacting proto fields
can lead to data loss. The following code snippet is an example:

```
// A proto could be serialized in one file..
absl::Status WriteToASCII(const RequestContext context, ...) {
...
  return file::SetContents(file, context.DebugString(), options); // Oops!
}
...
// And deserialization can take place in a totally different file!

absl::Status ReadContextAndDoSomething(std::string context, ...) {
  security::web::RequestContext c;
  TextFormat::ParseFromString(context, &c); // If redacted, parse error!
  return DoSomething(c);
}
```

In the above example, the `WriteToASCII` and `ReadContextAndDoSomething`
binaries don’t necessarily have to be owned by the same team - the developers
may not know each other's implementations even exist!

Another form of Hyrum dependency comes in the form of overly strict tests bound
to the existing DebugString output format.

```
std::string FooResult(Message m) {
  ...
  return m.DebugString();
}

// In a separate test file:
TEST_F(FooSuite, BarTest) {
  EXPECT_THAT(bar_proto, EqualsProto(expected)); // Straightforward comparison.
   ...
   EXPECT_THAT(
     FooResult(foo), HasSubstr("qux_field: fred")); // Breaks on format change!
}
```

In the above example, `BarTest` will break if we change the DebugString output
format.

If we want to modify the DebugString API to redact output, we would need to fix
all the Hyrum dependencies _first_, which would take a significant amount of
time for such a widely-used API. In the meantime, all Goping dependencies would
have to wait and continue to use unsafe DebugString. For these reasons, we
decided to create a set of new redaction-by-default APIs, and roll over users to
a new API one callsite at a time, which is much easier to roll back in case of
failure.

## Safe-by-default APIs

We believe that training developers to make correct security decisions isn't
sufficient to prevent security bugs from occurring. Instead, we change standard
APIs to be safe by default, so that users simply cannot write unsafe code.
Therefore, **automatic redaction** is the most important feature of the new
DebugString APIs.

Users may forget to redact data (that should not be accessible in debug logs) in
their own proto fields, or in deeply nested fields from other teams. We designed
the output of the new API to redact fields marked with a
[specific protobuf option](https://github.com/protocolbuffers/protobuf/blob/9af27995e92032fc0f79e0700b2c34db4e4f4038/src/google/protobuf/text_format.cc#L2931).
Protobuf is a low-level abstraction layer; we didn’t want to make judgment calls
on what specifically needed to be redacted. Each protobuf definition owner
determines which protobuf fields require redaction.

We want to avoid the previously mentioned Hyrum dependencies when designing this
new API; it should never be used as a serialization API to generate TextFormat.
This is even more important with redaction-by-default, because deserializing
redacted protos may cause tricky bugs where redaction causes unexpected data
loss. To achieve this, we add an unparseable, randomized URL prefix to the debug
output as well as a random number of spaces between the URL and the proto
representation. All URLs link users to the same documentation explaining the
deserialization problem and a FAQ. This prevents users from accidentally
deserializing this output, and makes it obvious to avoid depending on the format
in other ways. Here’s a visual comparison between the old and new formats:

```
text_field: "foo"
account_credential: "bar"
```

_Before_

```
[debug_FAQ_link]␣␣␣
text_field: "foo"
account_credential: [redaction_FAQ_link]
```

_After_ \[2\]

So what does this new API look like? We took advantage of the new
[Abseil Stringify feature](https://abseil.io/blog/11152022-stringify) and
implemented the interface in
[protobuf](https://github.com/protocolbuffers/protobuf/blob/9af27995e92032fc0f79e0700b2c34db4e4f4038/src/google/protobuf/message.h#L325),
which has a nice side effect of making the API more ergonomic as well. We also
implemented ShortDebugString and Utf8DebugString equivalents directly in
protobuf.

| Old | New |
| :-- | :-- |
| `proto.DebugString();` | `absl::StrCat(proto);` |
| `proto.ShortDebugString();` | `proto2::ShortFormat(proto);` |
| `proto.Utf8DebugString();` | `proto2::Utf8Format(proto);` |
| `LOG(INFO) << proto.DebugString();` | `LOG(INFO) << proto;` |
| `absl::StrFormat("%s", proto.DebugString());` | `absl::StrFormat("%v", proto);` |
| `absl::StrCat("foo: ", proto.DebugString());` | `absl::StrCat("foo: ", proto);` |
| `absl::Substitute("$0", proto.DebugString());` | `absl::Substitute("$0", proto);` |
| `absl::StrAppend(&str, proto.DebugString());` | `absl::StrAppend(&str, proto);` |

## Monitoring the Deserialization Problem

To discover the scale of the existing deserialization problem, we needed to
monitor this issue. Tracing these situations down via static analysis (e.g.
[Kythe](https://kythe.io/)) is impossible: If a protobuf is serialized by
DebugString in one process, and is indirectly passed to another process, static
analysis can't realistically determine that it's the same protobuf being passed
in. Therefore, we turned to **runtime monitoring** to find and fix these cases.

We decided to insert a
“ [silent marker](https://github.com/protocolbuffers/protobuf/blob/2e5e2783cc8e41bf84263de11b147dcd36cedb83/src/google/protobuf/text_format.cc#L93)”
into the output of DebugString. This is a canary sequence that is parseable and
ignored by TextFormat parsers, which allows us to add monitoring in the parsing
APIs to track locations where DebugStrings have been deserialized: \[3\]

```
foo.DebugString() => "{field: value}" // Preexisting output
bar.DebugString() => "{field \t : value}" // After adding the silent marker
```

You might be wondering – isn’t this going to break unit tests as well?

```
EXPECT_EQ(foo.DebugString(), "foo: bar");
EXPECT_EQ(foo.DebugString(), expected_foo.DebugString());
```

Using the structure presented above, we refactored failing tests in a couple of
different ways. For example, we were able to refactor the most common test
patterns by writing custom ClangTidy checks \[4\] and running them in parallel
across Google3 with Flume \[5\]:

```
EXPECT_EQ(IgnoringProtoDebugStringFormat(foo.DebugString(), "foo: bar");
EXPECT_THAT(EqualsProto(foo, expected_foo));
```

What about tests that didn’t match any of the patterns we targeted? We ran
global tests using TAP (a feature of our highly-scalable CI/CD infrastructure
that can run _all_ tests affected by a pending code change, across _all_
_projects_ in our entire monorepo) \[6\], which gave us a list of all remaining
failures. Subsequently, we refactored the remaining patterns to use a legacy,
unchanged variant of DebugString. This legacy API acts as a burndown list of
DebugString calls that will eventually get phased out through code churn or
other manual future efforts:

```
EXPECT_CONTAINS(foo.LegacyUnredactedDebugString(), "message foo: bar");
```

After fixing test failures across Google, we were able to flip our flag to
enable the silent marker globally. We instrumented the protobuf library to
detect these markers and send reports via two separate data collection channels
(an aggregated counter, as well as specific data via syslog). With this, our
runtime monitoring was in place, allowing us to see the locations where
DebugString was being used incorrectly.

## Large-scale Changes in Google3

Given our list of known deserialized types, we knew we could safely convert over
all other types without breaking any real production systems.

We followed up our monitoring by deploying another ClangTidy check to find
DebugString call locations. Importantly, we logged the different string outputs
as well as the sink of the call. \[7\] This allowed us to prioritize simple
conversions, which cover a vast majority of cases where credentials were likely
to be logged.

```
// These patterns are unlikely to cause any test failures or deserialization
// issues, since they go directly into a known sink.
LOG(INFO) << foo_proto.DebugString();
VLOG(1) << bar_proto.DebugString();
// We don't know what this output is going to be used for.
contents = baz_proto.DebugString();
```

By using this strategy, we generated low-risk fixes and applied them using
[Rosie](https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext),
a Google tool used to apply large-scale changes across Google3. This allows for
automated fix grouping, testing, and submission for several pull requests. After
gaining confidence that we wouldn’t break anything, we began refactoring
additional DebugString calls that were not on the list of known deserialized
types (previously generated via runtime monitoring).

Over the past year, our 3-person engineering team submitted around 26k pull
requests implementing our changes, with an approximately 500k-line diff.

![](https://storage.googleapis.com/bughunters-article-images/blogs/debug_log_01.png)

_Number goes up_

Fun fact: Since we've fixed the majority of the Goping dependencies, and marked
a portion of the Hyrum dependencies with legacy/test-only apis, we can estimate
that the ratio of Hyrum:Goping deps is around 1:5.

Moving forward, we plan to deprecate and/or delete DebugString, and turn on
pre-submit checks that will guide developers to using new APIs. These efforts,
combined with natural code churn, should further reduce the use of legacy APIs
and decrease our risk.

## Smoke Test: Did it work?

You may be wondering: How do we know that there was non-debug info in logs
anyways? Are individual teams able to avoid these errors through standard
security practices? How successful was this effort in actually redacting data?

We used the existing ClangTidy checks we had to look for LOG calls where these
proto fields were being passed in as an argument \[8\]. Of course, this is prone
to false positives, such as test-only code, custom protobuf sanitizers, and dead
code. How can we check that these are actually logged anywhere? Google generates
far too many logs per day for a manual search!

To narrow down our search, we updated our monitoring within the protobuf library
to log [Borg jobs](https://en.wikipedia.org/wiki/Borg_(cluster_manager)),
stack traces, and names of the proto/fields that were being redacted by our new
APIs. Using this specific data, we contacted the logs team to confirm whether
the field name was actually being printed out in those specific locations.

Using this combination of static analysis and runtime monitoring, we merged
results based on proto names. Now we were able to say with high confidence that
a specific proto logged at a specific line contained non-debug info and was
successfully redacted by our API! After narrowing down the results to this
point, we finally manually triaged the findings and were able to confirm these
findings. So, the answer is a resounding yes: **Globally redacting logs is**
**impactful in preventing such data in logs, even with many other mitigations in**
**place!**

## Empathy for the Developer

We place a strong emphasis on making these large-scale changes as smooth and
transparent as possible for all teams. By applying runtime monitoring and
measuring actual impact on redacting code, we were able to avoid costly
breakages. We automatically refactored vast chunks of our codebase to seamlessly
adopt safe-by-default APIs, which give us clearly defined security guarantees.
We create safety hatches with test-only APIs and legacy exemptions for
developers who have use cases that fall outside of the primary APIs.

We design our security mitigations by focusing on minimizing the burden on the
developer and creating safe-by-default APIs. Our goal is that the average
Googler should not have to worry about redaction or sanitization when writing
code; using the default well-lit path should always be safe and low-friction. We
believe that this safe coding approach is effective at creating sustainable
security changes at scale.

## References

\[1\] Justin Goping became the second most productive engineer at Google after
Hyrum Wright (as measured in pull requests/week) over the course of
refactoring many non-Hyrum dependencies ;)

\[2\] This is the internal version, which looks different than the public
version that has no prefix. Note that there are a variable number of
spaces immediately after the \[debug\_FAQ\_link\] link, shown as ␣.

\[3\] Think of this as a way to mildly break the API without actually causing
production issues.

\[4\] ClangTidy allows us to examine the AST of different source code files and
generate fixes based on certain patterns. See
[https://clang.llvm.org/extra/clang-tidy/checks/list.html](https://clang.llvm.org/extra/clang-tidy/checks/list.html)

\[5\] [https://research.google/pubs/pub35650/](https://research.google/pubs/pub35650/)

\[6\] [https://abseil.io/resources/swe-book/html/ch23.html#ci\_at\_google](https://abseil.io/resources/swe-book/html/ch23.html#ci_at_google)

\[7\] Examples of a sink: log statements and stream statements.

\[8\] We narrowed down our search to specific redacted field names like
“raw\_key\_bytes”, which has fewer false positive results than “key”.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab