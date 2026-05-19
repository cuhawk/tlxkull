---
source: bughunters
source_url: https://bughunters.google.com/blog/formally-verified-post-quantum-algorithms
title: "Formally Verified Post-Quantum Algorithms - Google Bug Hunters"
description: "In our latest post on PQC, we discuss how we are partnering with Cryspen to produce formally verified implementations of the NIST-selected post-quantum algorithms."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/formally-verified-post-quantum-algorithms#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Formally Verified Post-Quantum Algorithms

![](https://storage.googleapis.com/bughunters-article-images/blogs/tvdmerwe.jpg)

Thyla van der Merwe

Software Engineering Manager

![](https://storage.googleapis.com/bughunters-article-images/blogs/andreser.jpg)

Andres Erbsen

Software Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/Franziskus.jpg)

Franziskus Kiefer

CEO – Cryspen

![](https://storage.googleapis.com/bughunters-article-images/blogs/Karthik.jpg)

Karthikeyan Bhargavan

Chief Research Scientist – Cryspen

Published: Aug 19, 2024

Post-Quantum Cryptography

[RSS Feed](https://bughunters.google.com/feed/en)

# Formally Verified Post-Quantum Algorithms

The
[official release of Post-Quantum Cryptography (PQC) standards](https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards)
by the National Institute of Standards and Technology (NIST) represents a
significant step forward in securing the Internet, and organizations across the
globe, against the threat of quantum computers. In a world where large-scale
quantum computers exist, the classical public-key cryptography algorithms that
currently secure data on devices, or as it moves across the Web, are rendered
obsolete. Google has been at the forefront of the post-quantum evolution,
[experimenting with post-quantum algorithms](https://security.googleblog.com/2016/07/experimenting-with-post-quantum.html)
in 2016,
[enabling post-quantum protection for internal communications](https://cloud.google.com/blog/products/identity-security/why-google-now-uses-post-quantum-cryptography-for-internal-comms?e=48754805)
in 2022, and more recently,
[expanding protection to Chrome Desktop](https://blog.chromium.org/2024/05/advancing-our-amazing-bet-on-asymmetric.html).

As part of the next chapter in our post-quantum progression, we are partnering
with [Cryspen](https://cryspen.com/) to produce **formally verified**
implementations of the NIST-selected post-quantum algorithms. These
high-performance, open source implementations will come with formal guarantees
surrounding security, functional correctness, and memory safety, and will be
available for use by Google, and beyond. Implementation of the new post-quantum
algorithms is non-trivial – these algorithms rely on complex mathematical
structures and formal verification is the only way to ensure that the new
algorithm code is free from critical implementation bugs. Upon completion of the
project, Rust implementations of the new PQC algorithms will be included in the
[libcrux](https://github.com/cryspen/libcrux/) open source library. These
implementations will be AVX2-optimized, verified in F\* and translated into C.
The implementations will be self-contained such that they can be easily
incorporated into other cryptographic libraries.

## The Advent of Post-Quantum Cryptography

The age of quantum computers poses a threat to cryptography as we know it:
[Shor’s factoring algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm)
puts the public-key mainstays of modern-day cryptography – the RSA cryptosystem
and Diffie-Hellman key exchange – in jeopardy. Although quantum computers aren't
capable of breaking these schemes today, an adversary’s ability to _store_
_encrypted data now, and decrypt it later_ makes safeguarding data against
quantum computers
[an urgent endeavor](https://en.wikipedia.org/wiki/Grover%27s_algorithm).
Fortunately, NIST took action in 2016 to
[standardize PQC algorithms](https://csrc.nist.gov/projects/post-quantum-cryptography/post-quantum-cryptography-standardization),
and the recent culmination of this initiative has resulted in three approved
schemes: [ML-KEM](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf),
[ML-DSA](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.204.pdf), and
[SLH-DSA](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.205.pdf). The official
release of these schemes on 13 August 2024 unequivocally green-lights the
cryptographic transition to PQC, and given the historical precedent of
[long transition periods](https://chromestatus.com/feature/5759116003770368),
proactive measures are essential to ensure that digital infrastructure remains
secure, and that safe and bug-free PQC implementations are adopted from the
onset.

## Why Formal Verification Matters

Unlike conventional testing, formal verification provides mathematical proof of
a cryptographic implementation's correctness for all inputs, even unexpected and
malicious ones. This ensures enhanced security and reliability by detecting
potential vulnerabilities early in the development process. Recognizing the
value of formal verification, a number of cryptographic libraries, such as
[BoringSSL](https://boringssl.googlesource.com/boringssl/+/HEAD/third_party/fiat)
and [NSS](https://bugzilla.mozilla.org/show_bug.cgi?id=1387183), started
integrating formally verified implementations of cryptographic primitives,
leading to more secure and efficient implementations. Formally verifying an
implementation allows optimization without the fear of introducing bugs – every
possible optimization is formally verified, and the presence of this safety net
allows for the addition of even further optimizations.

The PQC collaboration between Cryspen and Google started with verification of
ML-KEM. While lattice-based algorithms like ML-KEM and ML-DSA might seem simpler
than traditional asymmetric cryptography, their parallelizable nature introduces
a unique set of challenges. This increased complexity makes it difficult to
identify potential bugs through traditional testing alone. During the
verification process, Cryspen found a timing side-channel bug in the ML-KEM
reference implementation that even the algorithm designers had been unaware of.
This bug and its variants, sometimes called
[KyberSlash](https://cryspen.com/post/ml-kem-implementation/?#timing-attacks-on-kyber-aka-kyberslash),
were then discovered in a number of Kyber implementations. Formal verification
of PQC algorithms will catch bugs like these, leading to deployment of highly
secure, highly optimized code.

## The Path Forward

We are actively integrating the latest updates from the finalized ML-KEM and
ML-DSA specifications into our implementations. Once verification is complete,
we plan to release the implementation as a Rust crate, and also to extract C
code that can easily be included in other cryptography libraries. We will then
focus our attention on the other NIST specifications, with the eventual goal of
developing production-ready, formally verified PQC implementations that can be
consumed not only by organizations like Google, but by anyone needing to embrace
the imminent PQC transition.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab