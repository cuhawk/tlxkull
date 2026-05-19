---
source: bughunters
source_url: https://bughunters.google.com/blog/googles-threat-model-for-post-quantum-cryptography
title: "Google's Threat model for Post-Quantum Cryptography - Google Bug Hunters"
description: "Read on to understand how Google currently evaluates the threat landscape related to post-quantum cryptography, and what implications this has for migrating from classical cryptographic algorithms to PQC."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/googles-threat-model-for-post-quantum-cryptography#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Google's Threat model for Post-Quantum Cryptography

![](https://storage.googleapis.com/bughunters-article-images/blogs/sschmieg.jpg)

Sophie Schmieg

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/kste.jpg)

Stefan Kölbl

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/guillaumee.jpg)

Guillaume Endignoux

Software Engineer

Published: Mar 11, 2024

Post-Quantum Cryptography

[RSS Feed](https://bughunters.google.com/feed/en)

# Google's Threat model for Post-Quantum Cryptography

If we do not encrypt our data with a quantum-secure algorithm right now, an
attacker who is able to store current communication will be able to decrypt it
in as soon as a decade. This store-now-decrypt-later attack is the main
motivator behind the current adoption of post-quantum cryptography (PQC), but
other future quantum computing threats also require a well-thought out plan for
migrating our current, classical cryptographic algorithms to PQC.

This is the first of a series of blog posts in the Bug Hunters blog, dedicated
to the topic of PQC, where we in Google's Cryptography team share our latest
thoughts and reasons about the PQC migration, starting with the threat model we
are working with.

Given the long timelines, our stances may evolve over time, with this blog post
reflecting our understanding at the beginning of 2024.

## Prioritization Considerations

The main considerations for prioritizing quantum threats that we will explore
more deeply in this post are:

- Feasibility of the quantum attack in question.
- Existence of store-now-decrypt-later attacks.
- Use cases that require fixed public keys with decades of lifetime.
- Need for exploratory research on systems that might require substantial
redesign to work with post-quantum algorithms, especially where wider
industry collaboration is required.

## Background

Quantum computers threaten cryptography mainly through two algorithms:
[Shor's algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm) for
factoring integers and solving discrete logarithms and
[Grover's search](https://en.wikipedia.org/wiki/Grover%27s_algorithm), which can
invert a black-box function. As mentioned, a major consideration for
prioritization is whether a system **today** is already at risk if an adversary
will get access to a quantum computer in the **future**. Storing ciphertexts now
and decrypting them later is a prime example for this, requiring a PQC
deployment well before the advent of quantum computers.

Based on this we can roughly group cryptography into four different
technologies:

- **Asymmetric encryption and key agreement**, using a private/public key pair
to establish a key that can then be used for symmetric cryptography.
Impacted by Shor's algorithm, and vulnerable to store-now-decrypt-later
attacks.
- **Digital signatures**, using a private/public key pair to authenticate data
and provide non-repudiation. Impacted by Shor's algorithm, but not
vulnerable to store-now-decrypt-later attacks.
- **"Fancy" cryptography**: This category depends on the specific algorithm
and use case, but many privacy preserving techniques (e.g.
[blind signatures](https://en.wikipedia.org/wiki/Blind_signature),
[ORPF](https://en.wikipedia.org/wiki/Oblivious_pseudorandom_function),
…),will be impacted by Shor's algorithm, and are partially vulnerable to
store-now-decrypt-later. Many of these techniques require further research.
We recommend a careful assessment of the impact of quantum threats on these
schemes.
- **Symmetric cryptography**, using a single secret key to encrypt and
authenticate data: In our current understanding, symmetric cryptography is
not impacted by quantum computers for all practical purposes. Grover's
algorithm could be used as an attack here, but is currently considered
infeasible for even medium-term quantum computers. (See
" [Reassessing Grover's Algorithm, 2017](https://eprint.iacr.org/2017/811)")

### Algorithms

Thankfully, [NIST](https://csrc.nist.gov/Projects/Post-Quantum-Cryptography) has
been working on standardizing new, quantum-safe algorithms that will address
asymmetric encryption and key agreement, as well as digital signatures. As a
quick overview, the algorithms look as follows, for our chosen security level.

| **Algorithm** | **Type** | **Public Key Size** | **Ciphertext/Signature Size** |
| --- | --- | --- | --- |
| ECDH (classical algorithm) | Key Agreement | 32 bytes | 32 bytes |
| ECDSA (classical algorithm) | Digital Signature | 32 bytes | 64 bytes |
| [Kyber-768/ML-KEM-768](https://csrc.nist.gov/pubs/fips/203/ipd) | Key Agreement | 1184 bytes | 1088 bytes |
| [Dilithium3/ML-DSA-65](https://csrc.nist.gov/pubs/fips/204/ipd) | Digital Signature | 1952 bytes | 3309 bytes |
| [SPHINCS+-128s/SLH-DSA-128s](https://csrc.nist.gov/pubs/fips/205/ipd) | Digital Signature | 32 bytes | 7856 bytes |

NIST is planning to release more standards (see
[here](https://csrc.nist.gov/Projects/post-quantum-cryptography/round-4-submissions)
and [here](https://csrc.nist.gov/Projects/pqc-dig-sig/standardization)), both
for key agreement and signatures in order to have schemes based on a wider set
of mathematical assumptions and allowing different trade-offs between public key
size and ciphertext/signature size. Note that any such future standards will
take multiple years to be finalized.

### Hybrid deployment

While the currently proposed PQC algorithms have received a lot of cryptanalysis
over the last decade, they are still somewhat less mature than classical
cryptography, and our recommendation is to use them in a hybrid fashion, which
requires an attacker to break both the classical and the post-quantum algorithm.
There are some caveats on this topic that we will explore in a future blog post.

## Use Cases

Classical Cryptography is pervasively used in modern software and
infrastructure. Post-quantum cryptography will impact many existing deployments.
With the information from the _Background_ section above in mind, the following
use cases are primary concerns and each comes with its own difficulties. While
we give our recommendations for the different use cases, please note that
standards are still being developed and will be the more definitive guidance for
which algorithms to use.

### Encryption in Transit

Encryption in transit primarily includes TLS, SSH, secure messaging (like
Signal, which is used in
[RCS](https://www.gstatic.com/messages/papers/messages_e2ee.pdf), and MLS), and,
for Google,
[ALTS](https://cloud.google.com/docs/security/encryption-in-transit/application-layer-transport-security).
The main threat here is store-now-decrypt-later. As such, deployment of PQC key
encapsulation schemes like Kyber (ML-KEM, FIPS 203) is urgent. In order to
mitigate this threat, we only need to add an ephemeral PQC key to the initial
key agreement. Long-term PQC keys (e.g. public or private CAs) fall under Public
Key Infrastructure and will require community consensus before meaningful
deployments can happen.

The good news with encryption in transit is that there are a limited number of
stacks. Most relevant to Google are, as mentioned above,
[TLS](https://blog.chromium.org/2023/08/protecting-chrome-traffic-with-hybrid.html),
[SSH](https://www.ietf.org/archive/id/draft-josefsson-ntruprime-ssh-02.html),
[Signal](https://signal.org/docs/specifications/pqxdh/), and
[ALTS](https://cloud.google.com/blog/products/identity-security/why-google-now-uses-post-quantum-cryptography-for-internal-comms),
which at the time of writing all have started to roll out PQC algorithms. The
ephemeral nature of the keys needed for encryption in transit further works in
our favor, making this use case, while the most urgent, also the comparatively
easiest for both technical and social reasons.

Our current recommendation for encryption in transit is to use Kyber768 for key
agreement in hybrid with X25519 or P256.

### Firmware Signatures

Firmware signatures are used to secure the root of the
[secure boot trust chain](https://cloud.google.com/docs/security/boot-integrity).
The public key for these signatures usually has to be burned into silicon or is
otherwise protected from being changed and tampered with. This makes changing
the signature scheme for this use case impossible in most cases. For devices
with a decade or longer lifespan, we end up in a similar situation as with
store-now-decrypt-later attacks, where we need to implement the quantum-safe
algorithms now, since we will not be able to change them at a later date. This
is further complicated by the long production timelines often involved with
hardware implementations of cryptographic algorithms.

Our current recommendation for firmware signature is to use the stateless
hash-based signature scheme SPHINCS+ (FIPS 205, SLH-DSA).

### Software Signatures

Software signatures are similar to firmware signatures and are needed to
guarantee secure boot and make deployments resistant to tampering with binaries
and source code. Unlike firmware signatures, the public key for software
signature can usually be updated and rely on the lower level signatures for
authenticity. On top of that, both binaries and source code are usually fairly
large, and both signing and verification are not particularly resource
constrained. This gives this use case the most flexibility and a relatively
relaxed timeline.

This use case is seeing a lot of development, and even though the timeline is
relatively relaxed, it might make sense to already include PQ signatures in the
standards that are currently being written.

Our current recommendation is to use either Dilithium3 (FIPS 204, ML-DSA) in
hybrid with ECDSA/EdDSA/RSA, or SPHINCS+ (FIPS 205, SLH-DSA) for this use case.

### Public Key Infrastructure

Public key infrastructure is the infrastructure used to provide authenticity for
encryption in transit, as well as reliable identities for machines and people.

PKI usually relies on chains of certificates, i.e. public keys with an attached
signature verifiable by a key higher in the chain. This makes PKI in its current
form extremely susceptible to size increases from post-quantum schemes. A single
Dilithium3 signature + public key is larger than 5kB, making any PKI deployment
with intermediaries very expensive. For the Web PKI in particular, we know some
devices start
[failing when packets grow beyond 10 - 30 kB](https://blog.cloudflare.com/sizing-up-post-quantum-signatures).
This problem might be fixable, but a severe performance penalty remains in any
case.

There are several alternatives to simply replacing classical signatures with
quantum-safe signatures, which could address the performance issues when it
comes to PKI. We are currently looking to experiment in this space to gather
data for more solid recommendations, which we will share in a future blog post.

### Tokens

Another widespread use of digital signatures is stateless asymmetric tokens,
such as [JSON Web Tokens](https://datatracker.ietf.org/doc/html/rfc7519) (JWT).
Tokens that use symmetric cryptography, or that use stateful techniques as a
defense-in-depth measure are not affected by quantum threats. For asymmetric
tokens, the main difficulty is the size constraints that they often come with.
For example, a token that is supposed to be saved as a cookie has an upper limit
of 4096 bytes available for the entire token. A Dilithium3 signature would take
up 3309 of those bytes, if encoded in binary, and at 4412 bytes would not fit
with this requirement when base64 encoded.

Stateless tokens come with independent security concerns, and moving towards
stateful tokens is prudent just to ensure more robust systems. Some of the
schemes in the second onramp of the NIST competition have very small signatures,
but large public keys; this approach could be another tool to address this use
case.

Our main recommendation is to use stateful tokens where possible, given their
additional security benefits. Additionally, we want to experiment in this space
to gather data for more solid recommendations.

### Other

There are some other use cases that do not fit into any of these categories. For
example, in some cases, documents have to be encrypted asymmetrically;
separately from encryption in transit. This use case mainly includes emails
encrypted and signed via S/MIME, but also various protocols using HPKE or PGP,
or using digital signatures directly.

Another one of the more important asymmetric encryption protocols is key import
for HSMs.

These use cases are less sensitive to ciphertext size, so using Kyber (FIPS
203/ML-KEM) in hybrid with ECDH/X25519 should not pose many challenges. For
S/MIME in particular, additional difficulties might arise from the multi
recipient setting.

Another use case that is related to, but not equal to the HSMs discussed above
are hardware roots of trust such as security keys or TPMs, which face their own
difficulties regarding their hardware constraints.

Privacy preserving and other fancier schemes will require additional research to
safely deploy. We plan to give an overview and a call to action in a future blog
post.

## Threat actors and Timelines

Both lack of quantum-safe confidentiality and lack of quantum-safe authenticity
can be exploited by threat actors. While the threats to confidentiality are more
direct, the threats to authenticity are often far more wide-reaching and
devastating.

### Threat Actors

#### Nation States

Nation states are the most likely to first arrive at a cryptographically
relevant quantum computer. They will most likely try to deploy the quantum
computer in a deniable fashion, in order to avoid tipping off adversaries of
their capabilities. Nation states are most likely to target the Cloud
deployments of other nation state customers, and may target political dissidents
and other targets for surveillance. Nation states might also target Google or
other infrastructure providers for military or economic reasons.

While building a cryptographically relevant quantum computer is hard, once the
machine is built, it should not be very expensive to break any given public key.
Given the ephemeral nature of encryption in transit keys, the most likely first
targets would be more static keys as required for e.g. PKI, as well as breaking
stored communication that is considered of high interest. As quantum computers
get cheaper, they might target wider and wider sets of victims.

Some have raised concerns that nation states might try to backdoor or weaken the
algorithms NIST releases, as has been done in the past in the case of
[Dual\_EC\_DRBG](https://eprint.iacr.org/2015/767.pdf). To preempt such
concerns, the NIST standards were designed in
[a public competition](https://csrc.nist.gov/projects/post-quantum-cryptography).
In addition, if most deployments are in a hybrid fashion, being able to break
the PQC algorithm by itself would not help until a quantum computer is
available, giving the public several years to discover any potential backdoors.

#### Insider Threats

[Google](https://quantumai.google/) and other companies are working to build a
quantum computer, which eventually might become cryptographically relevant. As
with other prized technologies, insider threats remain a vector. To that end,
companies will need to take necessary precautions to protect their crown jewels
to avoid theft or exploitation by a nation state threat and other motivated
attackers.

#### Ransomware and other financially motivated threat actors

For financially motivated threat actors, the main consideration will be the
availability of quantum computers. If use cases for quantum computers remain
limited, access to them might be too difficult for a financially motivated
threat actor to obtain. If they are available for relatively cheap prices,
either directly, or via Cloud deployments, we are likely to see them used to
extract ransoms, or commit industrial espionage, by exploiting areas that have
not migrated to quantum-safe protocols.

#### Regulatory Landscape

PQC has become a hot topic with various executive orders in the US, requiring
the US government to work towards deploying quantum-safe cryptography.
Regulatory frameworks such as
[CNSA 2.0](https://media.defense.gov/2022/Sep/07/2003071834/-1/-1/0/CSA_CNSA_2.0_ALGORITHMS_.PDF)
outright require the use of PQC on fairly short timelines, with other compliance
frameworks such as FIPS being soon to follow. Beyond the US,
[BSI](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Quantentechnologien-und-Post-Quanten-Kryptografie/quantentechnologien-und-post-quanten-kryptografie_node.html)
and
[ANSSI](https://cyber.gouv.fr/en/publications/follow-position-paper-post-quantum-cryptography)
have also been active in this space and have been starting to ask for PQC
roadmaps for longer term deployments.

### Timelines

The best aggregate timeline estimates for the risk from quantum computers we
have can be summed up in this graphic by the
[global risk institute](https://globalriskinstitute.org/publication/2023-quantum-threat-timeline-report/).

![](https://storage.googleapis.com/bughunters-article-images/blogs/pqc_estimate_01.png)

_Fig. 1._
_[Global Risk Institute](https://globalriskinstitute.org/publication/2023-quantum-threat-timeline-report/)_
_expert estimates for cryptographically relevant quantum computers_

Based on this timeline, and corroborated by Google’s quantum computing team,
[Google Quantum AI](https://quantumai.google/), the main risk for a
cryptographically relevant quantum computer is within a ten to 15 year
timeframe. We expect significant improvements in the field by 2030, which should
serve as a good midpoint check on the timeline.

## Conclusion

Despite the long timelines until the prevalence of cryptographically relevant
quantum computers can be expected, we hope that the overview given in this blog
post will help you understand which areas are most at risk, and where you should
start focusing your attention at the present time.

Look out for more posts on PQC in the future. As the state of the art is
evolving, so will the guidance and best practices we recommend!

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab