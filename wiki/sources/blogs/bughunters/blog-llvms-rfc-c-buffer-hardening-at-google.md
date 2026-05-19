---
source: bughunters
source_url: https://bughunters.google.com/blog/llvms-rfc-c-buffer-hardening-at-google
title: "LLVM's 'RFC: C++ Buffer Hardening' at Google - Google Bug Hunters"
description: "In this blog post, we're sharing how we evaluated LLVM's proposed approach at Google, outlining our initial conclusions from this process, sharing useful adoption tips, and pointing to the next steps we plan to take on this journey."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/llvms-rfc-c-buffer-hardening-at-google#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# LLVM's 'RFC: C++ Buffer Hardening' at Google

![](https://storage.googleapis.com/bughunters-article-images/blogs/juvazq.jpg)

Juan Vazquez

Information Security Engineer

Published: Feb 12, 2024

Security Engineering

[RSS Feed](https://bughunters.google.com/feed/en)

# LLVM's 'RFC: C++ Buffer Hardening' at Google

Memory safety bugs are responsible for the
[majority (~70%) of severe vulnerabilities](https://www.memorysafety.org/docs/memory-safety/#how-common-are-memory-safety-vulnerabilities)
in large C/C++ code bases. According to
[Chromium](https://www.chromium.org/Home/chromium-security/memory-safety/),
“around 70% of their serious vulnerabilities are memory safety problems”. The
Google Project Zero 2021
[annual report](https://googleprojectzero.blogspot.com/2022/04/the-more-you-know-more-you-know-you.html)
of 0-days exploited in-the-wild indicates that 39 out of 58 (67%) in-the-wild
0-days were memory corruption vulnerabilities. Finally, Google’s internal
analysis reveals that 25% of all in-the-wild exploits target spatial safety
bugs.

Clearly, this class of vulnerabilities is very widespread, making several
entries in the
[CWE 2023 Top 10 Known Exploited Vulnerabilities](https://cwe.mitre.org/top25/archive/2023/2023_kev_list.html)
list. This is what prompted LLVM to share ideas on how to systematically address
and mitigate threats of this type. In this blog post, we'll share how we
evaluated LLVM’s proposed approach at Google, outline our initial conclusions
from this process, share useful adoption tips, and point to the next steps we
plan to take on this journey.

## LLVM’s C++ Buffer Hardening Proposal

In October 2022, ISE (Information Security Engineering) at Google was
investigating and evaluating different approaches for mitigating spatial safety
sub-classes and their tradeoffs, when Apple introduced
[RFC: C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
to LLVM, which presented two ideas to prevent spatial memory safety issues:

1. A
[Hardened C++ Standard Library](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734#hardened-c-standard-library-2)
, in this case
[hardened libc++](https://discourse.llvm.org/t/rfc-hardening-in-libc/73925),
where facilities such as `std::array`, `std::vector`, and `std::span` are
bounds-checked at runtime and potential exploits are turned into aborts.
2. The
[C++ Safe Buffers Programming Model](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734#programming-model-4)
where pointer arithmetic is considered unsafe and Clang warns about it. This
enables transforming C-style code to use the hardened libc++.

On a high level, the C++ Buffer Hardening proposal is aligned with Google’s
perspective on tackling memory safety bugs, and fits within the model of
**prevention through**
**[Safe Coding](https://github.com/google/safe-html-types/blob/main/doc/index.md#introduction-to-safe-coding)**.
More concretely, in this case the proposal means that C-style arrays/buffers and
pointer arithmetic are considered unsafe coding constructs that need to be
replaced with safe C++ utilities, where the hardened libc++ can provide runtime
error detection.

Based on this initial insight, we evaluated what it would take to apply the
[C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
proposal to a fleet-wide representative workload,
[Andromeda](https://www.usenix.org/system/files/conference/nsdi18/nsdi18-dalton.pdf),
Google Cloud Platform’s network virtualization stack. Doing so allowed us to
assess the impact from different perspectives, such as cost of adoption,
performance, safety coverage, and gaps. This approach resulted in **hardening**
**the GCP network virtualization stack against spatial safety vulnerabilities,**
**while upholding Andromeda’s hard performance constraints**. The next sections
provide more insight into this process.

## Andromeda: GCP Network Virtualization Stack

Andromeda is Google Cloud Platform’s network virtualization stack which aims to
provide bandwidth and latency largely indistinguishable from the underlying
hardware. Andromeda is the workload we used to pilot adoption of the
[C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
proposal.

The Andromeda VM host dataplane is a user space process that performs all
on-host VM packet processing, hence security of the workload is critical to
guarantee VM isolation.

Among the characteristics of the dataplane, there is an on-host fast path, used
for performance-critical flows with a 300ns per-packet CPU budget. This budget
limits both the complexity and state required by the fast path, where
high-performance, latency-critical flows are processed end to end.

The security and performance requirements of the Andromeda workload made it a
perfect match for evaluating the viability of C++ Buffer Hardening. If we could
apply the model while preserving the hard throughput and latency constraints of
Andromeda, we'd have strong evidence that the model can be applied widely.

## Hardened C++ Standard Library

Implementing the
[C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
proposal requires deploying a
[Hardened C++ Standard Library](https://discourse.llvm.org/t/rfc-hardening-in-libc/73925)
which can catch several cases of undefined behavior, including out-of-bounds
access, and will terminate the process upon violation. LLVM’s
[libc++ 18.0.0](https://libcxx.llvm.org/ReleaseNotes/18.html) should provide
[this hardening](https://discourse.llvm.org/t/rfc-hardening-in-libc/73925),
which is also available in
[GitHub’s main (dev) LLVM branch](https://github.com/llvm/llvm-project). The
`fast` hardening
[mode](https://libcxx.llvm.org/Hardening.html#using-hardening-modes) enables a
set of security-critical checks with minimal runtime overhead. Those
security-critical checks include the ones needed to mitigate spatial safety
vulnerabilities when using libc++ containers and utilities:

- Valid Input Range: checks that a range passed to a standard library function
as input is valid and does not incur an out-of-bounds access.
- Valid Element Access: checks that any attempt to access a container element
is valid and does not go out of bounds.

### Performance

While these new runtime safety checks improve security, they add additional
runtime overhead and can negatively impact performance. We studied the
performance degradation for Google workloads and
[Feedback Direct Optimization](https://arxiv.org/abs/1411.6361) (FDO) proved to
be effective in minimizing it. As an example, enabling the hardened libc++,
without any FDO, in a representative Google fleet workload added a ~0.9% queries
per second (QPS) regression and a ~2.5% latency regression. When properly using
FDO, we measured a ~65% reduction in QPS overhead and a ~75% reduction in
latency overhead.

For performance sensitive services like Andromeda, we also used
[pprof](https://github.com/google/pprof) to visualize and analyze profiling
data. This helped us find a noticeable increase of CPU cycles spent in
`std::vector::operator[]`. Moreover, it allowed us to collect a list of hot
paths where this was degrading performance.

This discovery was not all too surprising, because `std::vector` is used by
Andromeda to operate on batches of packets, including the fast path.

One strategy to reduce the overhead is to manually avoid redundant bound checks
in cases where the optimizer doesn't seem to be enough. To do so, we used 2 main
techniques:

1. Loop over containers using iterators, instead of using indexes and
`operator[]`. Note that iterators are not bound-checked by default by the
`fast` mode, so they should be used with caution.
2. Store references to container elements that are accessed repeatedly in local
variables. Another piece of warning: be careful to not use outdated
references after a vector is modified/resized, as this would introduce
lifetime issues.

In hot paths where these techniques cannot be used, bound checks can be disabled
by using the `data()` method, provided by several C++ sequence containers. This
bypass can be useful in situations where code review concludes that the access
is safe.

Our recommendation is to use the techniques explained above with caution, and
only when performance is an issue. Otherwise, allow the hardened libc++ to do
its job. Compiler optimizations and FDO should help mitigate performance
regressions due to bound checks.

### Diagnosability

When monitoring (or debugging) production crashes, be sure to take the new
behavior of the hardened libc++ into account; this will help avoid some typical
pitfalls:

1. As a result of an out-of-bound access, the libc++ will terminate the process
via a call to `std::abort`, generating a `SIGABRT` signal. The same signal
(`SIGABRT`) may be the result of other reasons for terminating the program
and may be discarded prematurely.
2. Inlining may also make it impossible to tell, by just looking at the
crashing stack, which libc++ method call (aka path) generated the abort, as
the compiler merges multiple basic blocks containing the trap.

## C++ Safe Buffers Programming Model

The hardened libc++ allows mitigating spatial safety vulnerabilities in libc++
containers. But there are some remaining gaps, the biggest of which is that
accessing C-Style arrays/buffers won’t go through the hardened libc++ and will
remain a threat to spatial safety. The goal of the
[C++ Safe Buffers Programming Model](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734#c-safe-buffers-3)
is to address this gap.

Under this model, any pointer arithmetic is considered unsafe and must be
transformed to use hardened facilities such as `std::array`, `std::vector,` or
`std::span`, effectively migrating away from C-style arrays/buffers.

To find instances of pointer arithmetic, you can use Clang’s
`-Wunsafe-buffer-usage` diagnostic, which was added in version 16. When
required, entire methods can be opted-out with the
[`[[clang::unsafe_buffer_usage]]`](https://clang.llvm.org/docs/AttributeReference.html#unsafe-buffer-usage)
annotation. A block of code can be opted-out with a pair of `clang unsafe_buffer_usage` pragma begin/end labels.

For new targets or components adopting the model, it’s advisable to make an
initial migration, solving all the pre-existing instances.

Depending on the type of C-style construction being ported, different strategies
can be used for migration:

- For static C-style arrays whose size is known at compile time, we used
`std::array`, similar in performance to a C-style array but with the
benefits of a C++ container.
- For dynamic C-style arrays whose size is known only at runtime, we used
`std::vector`. When the conversion to `std::vector` isn’t possible,
`std::span` can be used to refer to the underlying contiguous sequence of
objects, with the benefits of a C++ container. Note that using `std::span`
requires C++20.

LLVM is working on suggestions (fixits) to adopt these strategies. To the best
of our knowledge this is work in progress, only available in
[LLVM’s main branch](https://github.com/llvm/llvm-project/tree/main)
(development) and, at the moment of writing, the only strategy with support is
`std::span`. If you’d like to try them, the suggestions become available with
the option `-fsafe-buffer-usage-suggestions`.

## Conclusion and next steps

After enabling
[C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
in Andromeda, we identified and fixed 3 bugs violating spatial safety. While
root causing is still challenging, we have concluded that adopting the
[C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
proposal is a valid strategy for mitigating spatial safety risk in complex C++
codebases, and fits into our
[Safe Coding](https://github.com/google/safe-html-types/blob/main/doc/index.md#introduction-to-safe-coding)
approach which is designed to drastically reduce the occurrence of common
classes of vulnerabilities, and build assurance that vulnerabilities are absent.

We plan to work on further adoption of
[C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
at Google. The next challenges for us are:

**Work to address known gaps**

So far, we have identified 2 gaps when it comes to
[C++ Buffer Hardening](https://discourse.llvm.org/t/rfc-c-buffer-hardening/65734)
that we would like to address or mitigate:

1. The hardened libc++ (`fast` mode) doesn’t guarantee assurance of container
iterators. Bounded iterators for supported containers are available in the
libc++ via the macro `_LIBCPP_ABI_BOUNDED_ITERATORS`, but the change is
ABI-breaking. Enabling this change would require: first, making our codebase
compatible and, second, evaluating for potential extra performance
degradation.
2. Smart pointers’ `operator[]`, as `std::unique_ptr::operator[]`, does not
enforce valid-element-access on the managed array. The warning
`-Wunsafe-buffer-usage` also does not report such access. At the moment of
writing, this gap has been
[reported](https://github.com/llvm/llvm-project/issues/73452).

**Improve diagnosability**

As discussed, [diagnosing](https://bughunters.google.com/blog/6368559657254912/#diagnosability) program
terminations due to the hardened libc++ can be far from easy. Inlining and other
optimizations can make it hard and time consuming (if not impossible) to root
cause production aborts. We are evaluating options to improve the situation, as
proposed by the new LLVM
[RFC: adding `__builtin_verbose_trap(string-literal)`](https://discourse.llvm.org/t/rfc-adding-builtin-verbose-trap-string-literal/75845).

**Hardened Abseil**

[Abseil](https://abseil.io/about/) is an open source collection of C++ libraries
used at Google to augment libc++. It includes its own collection of containers
and its own
[hardened mode](https://github.com/abseil/abseil-cpp/blob/d5a2cec006d14c6801ddeb768bf2574a1cf4fa7f/absl/base/options.h#L231C14-L231C14),
that we have to enable to have comprehensive spatial safety. Enabling it has its
own, albeit similar, performance and usability challenges.

**Adoption at Scale**

As a first challenge, adopting the hardened libc++ requires mitigating the
[performance](https://bughunters.google.com/blog/6368559657254912/#performance) overhead incurred, even in
the presence of FDO. At Google’s scale, measurable regressions, even below 1%,
have a noticeable impact on computing resources. We plan to further explore ways
to mitigate the performance regression, potentially auto-eliminating redundant
bound checks. The ultimate goal is to enable the hardened libc++ by default in
production.

Adopting the C++ Safe Buffers Programming Model at scale presents another
challenge. Over the past decades, Google has developed and accumulated 100s of
millions of lines of C++ code that is in active use and under active, ongoing
development. Transitioning to the model manually is not feasible, even with the
help of `-Wunsafe-buffer-usage`. The plan for us now is to leverage our
[existing infrastructure and tools for large-scale changes](https://cacm.acm.org/magazines/2016/7/204032-why-google-stores-billions-of-lines-of-code-in-a-single-repository/fulltext)
to adopt the model.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab