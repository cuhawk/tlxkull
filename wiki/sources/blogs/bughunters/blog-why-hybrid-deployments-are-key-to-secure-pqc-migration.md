---
source: bughunters
source_url: https://bughunters.google.com/blog/why-hybrid-deployments-are-key-to-secure-pqc-migration
title: "Why Hybrid Deployments Are Key to Secure PQC Migration - Google Bug Hunters"
description: "This blog post explores the advantages of hybrid deployments in a world of post-quantum cryptography, looks at the reasons behind our recommendation, and offers implementation guidance."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/why-hybrid-deployments-are-key-to-secure-pqc-migration#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Why Hybrid Deployments Are Key to Secure PQC Migration

![](https://storage.googleapis.com/bughunters-article-images/blogs/kste.jpg)

Stefan Kölbl

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/sschmieg.jpg)

Sophie Schmieg

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/guillaumee.jpg)

Guillaume Endignoux

Software Engineer

Published: May 21, 2024

Post-Quantum Cryptography

[RSS Feed](https://bughunters.google.com/feed/en)

# Why Hybrid Deployments Are Key to Secure PQC Migration

In our
[last blog post](https://bughunters.google.com/blog/5108747984306176/google-s-threat-model-for-post-quantum-cryptography)
we discussed Google's threat model and how it is driving our response to the
post-quantum cryptography (PQC) transition, including how we prioritize the
risks. In addition, we shared our recommendations for adapting to the risks
quantum computing poses for your data. One of these recommendations was to use a
hybrid deployment approach. In this blog post we’ll explore the advantages of a
hybrid deployment in a world of post-quantum cryptography, take a deep dive into
the reasons behind our recommendation, and offer guidance on how to implement
hybrid schemes.

## What is a hybrid deployment?

In this context, the concept of hybrid deployment \[1\] is relatively
straightforward. It is a combination of two public key algorithms drawing from:

- **Classical cryptography:** An algorithm we currently rely on like ECDH or
ECDSA.
- **Post-quantum cryptography (PQC)**: A new algorithm specifically designed
to be resistant to attacks powered by quantum computers.

Hybrids employ both families of algorithms simultaneously, providing layered
defense against both classical and potential quantum adversaries. Any secure
hybrid construction must guarantee that the overall system is at least as secure
as the strongest algorithm used in the hybrid. In other words: Combining schemes
in a hybrid must never weaken the security of the individual underlying
cryptographic algorithms.

## The rationale for hybrids

Let's dive into why hybrid constructions offer distinct advantages during this
complex transitional period:

- **Mitigating risks associated with new algorithms:** Post-quantum
algorithms, while promising, haven't undergone the decades of scrutiny and
real-world testing that our current systems have. This applies both to
algorithmic scrutiny, but especially to the implementation side as well. For
this reason, it's prudent to avoid complete reliance on these newer
algorithms. By retaining our well-understood cryptography while gradually
integrating PQC, we hedge our bets, ensuring that unexpected flaws in a
post-quantum algorithm or implementation do not introduce new
vulnerabilities.
- **A safe transition:** Migrating entire cryptographic infrastructures to new
post-quantum algorithms is an enormous undertaking. Hybrid constructions
create a gradual, flexible path to adoption. Organizations can more quickly
introduce and test PQC while maintaining operational security based on the
robust systems they already have in place.

The efficacy of hybrids has been validated by tests we’ve run in the past: By
deploying PQC in a hybrid fashion, we ran experiments in Chrome
( [2016](https://security.googleblog.com/2016/07/experimenting-with-post-quantum.html),
[2019](https://blog.cloudflare.com/towards-post-quantum-cryptography-in-tls/))
on real traffic without putting user data at risk. These experiments showed that
it is practical to protect user data against a quantum adversary, while ensuring
that in the worst case, it was still as secure as classical protections without
using PQC. This was not a theoretical scenario. The PQC portion of CECPQ2b using
[SIKE](https://sike.org/) we employed turned out to be broken, but all data in
that experiment was still protected by the classical X25519 algorithm.

It’s important to note that while a cryptographically relevant quantum computer
(CRQC) could break classical cryptographic algorithms, it is very unlikely that

1. access to a CRQC will be available immediately to all adversaries and 2) the
costs for carrying out an attack will be low. We expect that if and when CRQC
first become available, in many cases the additional layer of the classical
algorithms will still provide a worthwhile security benefit.

## The cost debate

Hybrid deployments do not come for free. They can have a negative performance
impact and add complexity.

- **Protocol complexity:** Hybrid constructions may lead to additional
complexity for protocol designers. Designers will have to decide how to
combine schemes. If too many schemes are available, it could quickly lead to
a combinatorial explosion of options that need to be supported by all
implementations.
- **Implementation complexity:** Implementing two cryptographic algorithms
increases engineering costs and leads to a larger attack surface. However,
in most cases there are already vetted implementations of classical crypto
systems available and deployed, and the main costs and risks come from the
addition of the new PQC algorithm. The hybrid constructions we recommend
here are simple and easy to implement, while more complex constructions
could introduce additional risks for implementations.
- **Computational cost:** Hybrid solutions have a negative performance impact,
however, in many cases the overhead caused by the PQC algorithm already
dominates, especially in terms of parameter sizes. For example, if a
Kyber768 ciphertext is 1088 bytes and you include an additional 32-byte
X25519 shared secret, the impact is negligible. Similarly a Dilithium3
signature is 3309 bytes, whereas an Ed25519 signature only requires 64
additional bytes.
- **It’s not a permanent solution:** Deploying a hybrid solution may mean
having to do two PQC migrations. First to introduce a hybrid scheme, and
later a second migration when cryptographically relevant quantum computers
become available and reduce / remove the benefit of the classical algorithm
and mean it should be removed.

## Our recommendations

To simplify integration and minimize security risks, we strongly recommend
encapsulating hybrid constructions within a single, well-defined type. For
instance, a hybrid KEM combining X25519 and Kyber768 should be presented as a
new, standalone algorithm. This approach hides implementation details, making
the hybrid scheme indistinguishable from any other algorithm for the end user.

This strategy comes with several advantages. It simplifies usage, making the
hybrid scheme as straightforward to implement as any other algorithm on a higher
level. Additionally, it prevents accidental key material reuse between hybrid
and traditional systems. While a hybrid signature compatible with legacy
protocols might seem convenient, it introduces complexity and enables potential
downgrade attacks.

We strictly recommend not using hybrids as a means to ease the legacy transition
or provide backward compatibility. Always use distinct key material for hybrid
and non-hybrid schemes.

Our main recommendations for actual constructions are:

- For KEMs using the [X-Wing](https://eprint.iacr.org/2024/039) combiner.
- For signatures simply using two signature schemes in parallel.

## A deeper dive into hybrid constructions

In the following two sections, we will discuss in detail what approaches have
been proposed so far to deploy PQC in a hybrid way. In particular, we want to
highlight that there have been many competing proposals, with subtle differences
which can make the space of hybrid constructions confusing.

### Key encapsulation mechanisms (KEMs)

The goal of a hybrid KEM is to have a single shared secret between two parties,
which is derived from a key encapsulation (or key agreement) combining a PQC and
a classical algorithm like ECDH. A good implementation should be guaranteed to
be as strong as the stronger of the two algorithms.

Recent efforts have proposed numerous candidates for KEM combiners defined in
IETF drafts including:

- [Hybrid key exchange in TLS 1.3](https://datatracker.ietf.org/doc/html/draft-ietf-tls-hybrid-design-06)
- [Combiner function for hybrid key encapsulation mechanisms (Hybrid KEMs)](https://datatracker.ietf.org/doc/html/draft-ounsworth-cfrg-kem-combiners-05)
- [Chempat: Generic Instantiated PQ/T Hybrid Key Encapsulation Mechanisms](https://datatracker.ietf.org/doc/html/draft-josefsson-chempat-00)
- [X25519Kyber768Draft00 hybrid post-quantum key agreement](https://datatracker.ietf.org/doc/draft-tls-westerbaan-xyber768d00/)
- [X-Wing: general-purpose hybrid post-quantum KEM](https://datatracker.ietf.org/doc/draft-connolly-cfrg-xwing-kem/)
- [Composite ML-KEM for Use in the Internet X.509 Public Key Infrastructure\\
and\\
CMS](https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-kem/)

Each of these candidates proposes a different approach to KEM combiners.
[NIST SP 800-56C](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-56Cr2.pdf)
allows generating a hybrid shared secret via the concatenation: `Z’ = Z || T`.
NIST is working toward an additional special publication providing further
guidance on KEMs (see [NIST FIPS 203](https://csrc.nist.gov/pubs/fips/203/ipd)
referencing “Special Publication 800-227: Recommendations for key-encapsulation
mechanisms'').

In Chrome we’ve used different hybrid options in the past:

- In 2016:
[CECPQ1](https://security.googleblog.com/2016/07/experimenting-with-post-quantum.html),
which used X25519 and NewHope.
- In 2019:
[CECPQ2](https://blog.cloudflare.com/the-tls-post-quantum-experiment/) (and
CECPQ2b), which used X25519+HRSS and X25519+SIKE and `HKDF(shared_secret_A || shared_secret_B)` to derive the shared secret. At Google, we’ve also
been using the CECPQ2 hybrid in
[ALTS](https://cloud.google.com/blog/products/identity-security/why-google-now-uses-post-quantum-cryptography-for-internal-comms).
- In 2023:
[X25519+Kyber768](https://blog.chromium.org/2023/08/protecting-chrome-traffic-with-hybrid.html),
which uses `secret_A || secret_B`, and the result in the TLS 1.3 key
derivation.

Note that these “simple” concatenation-based KEM combiners are only effective
due to the nature of TLS key derivation (as you already include a hash of the
full transcript in the KDF).

For most applications, a single well-defined hybrid combiner like X-Wing would
be preferable. The main benefits of this construction are that it is simple,
efficient, and comes with a security proof.

While generic combiners may be desirable for some use cases, they come with
several drawbacks. First, implementers need to be careful how to construct the
combiner. For example, a simple KDF (`secret_A || secret_B`) combiner may not
achieve [IND-CCA](https://en.wikipedia.org/wiki/Ciphertext_indistinguishability)
for all possible KEM choices. A generic combiner (e.g.
[https://eprint.iacr.org/2018/024.pdf](https://eprint.iacr.org/2018/024.pdf)) providing security for all possible
instantiations would introduce additional overhead (like including all
ciphertexts in the KDF part), which may not be necessary for particular choices
of KEM.

### Signatures

For general use, we recommend using signatures in parallel, ideally in a
to-be-defined standard way, fixing two signature schemes like X-Wing does in the
case of KEMs.

The goal of a hybrid signature is to have a single signature for a message,
which only verifies if a valid signature for both underlying signature schemes
has been created. A good implementation should be guaranteed to be as strong as
the stronger of the two algorithms.

Similar to KEMs, there are many options to consider regarding how signatures
could be combined. Fortunately, simply producing the two signatures in parallel
and only accepting the signature if both of them are verified is sufficient to
have a hybrid scheme which provides unforgeability and is very simple to
implement:

```
HybridKeyGen() -> (secret_hybrid, public_hybrid)
  secret_classic, public_classic <- ClassicalKeyGen()
  secret_pqc, public_pqc <- PQCKeyGen()
  return ((secret_classic, secret_pqc), (public_classic, public_pqc))

HybridSign(secret_hybrid, message) -> (signature_hybrid)
  secret_classic, secret_pqc <- secret_hybrid
  signature_classic <- ClassicalSign(secret_classic, message)
  signature_pqc <- PQCSign(secret_pqc, message)
  return (signature_classic, signature_pqc)

HybridVerify(public_hybrid, Message, signature_hybrid) -> Accept / Reject
  public_classic, public_pqc <- public_hybrid
  signature_classic, signature_pqc <- signature
  return ClassicalVerify(public_classic, message, signature_classic) == Accept &&
         PQCVerify(public_pqc, message, signature_pqc) == Accept
```

Other combiners can provide additional properties: In
[security keys](https://security.googleblog.com/2023/08/toward-quantum-resilient-security-keys.html),
we opted to nest signatures to eliminate the malleability of ECDSA when combined
in a Dilithium+ECDSA hybrid signature. Properties like non-separability (see
[https://eprint.iacr.org/2023/423](https://eprint.iacr.org/2023/423), or
[https://datatracker.ietf.org/doc/draft-hale-pquip-hybrid-signature-spectrums/](https://datatracker.ietf.org/doc/draft-hale-pquip-hybrid-signature-spectrums/))
have been studied, which can prevent stripping or reusing parts of the
signature, to create a valid non-hybrid signature for one of the underlying
keys. However, these combiners come with additional complexity and if the key
material is strictly separated between hybrid and non-hybrid keys, we see a very
limited benefit in aiming for these additional separability properties.

## Conclusion

We hope this post has helped make a case for our initial recommendation
regarding cryptographic protections against post-quantum computing, the adoption
of hybrid deployments, and what to consider when following this approach.

Look out for our next posts on PQC – as the state of the art evolves, so will
our guidance and recommended best practices!

## Notes

\[1\] The term hybrid is unfortunately also used to describe the concept of
combining a public key encryption scheme with a symmetric key encryption scheme
to encrypt data, like for instance in
[HPKE](https://datatracker.ietf.org/doc/rfc9180/).

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab