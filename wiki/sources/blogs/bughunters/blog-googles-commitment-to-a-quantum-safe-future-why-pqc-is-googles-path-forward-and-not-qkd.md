---
source: bughunters
source_url: https://bughunters.google.com/blog/googles-commitment-to-a-quantum-safe-future-why-pqc-is-googles-path-forward-and-not-qkd
title: "Google's Commitment to a Quantum-Safe Future: Why PQC is Google's Path forward and not QKD - Google Bug Hunters"
description: "In this post, we're sharing our assessment of the Quantum Key Distribution (QKD) technology and explaining why we believe PQC is the more mature and scalable solution for Google's needs."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/googles-commitment-to-a-quantum-safe-future-why-pqc-is-googles-path-forward-and-not-qkd#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Google's Commitment to a Quantum-Safe Future: Why PQC is Google's Path forward and not QKD

![](https://storage.googleapis.com/bughunters-article-images/blogs/kste.jpg)

Stefan Kölbl

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/chrpet.jpg)

Christiane Peters

Security Architect

Published: Dec 1, 2025

Post-Quantum Cryptography

[RSS Feed](https://bughunters.google.com/feed/en)

# Google's Commitment to a Quantum-Safe Future: Why PQC is Google's Path forward and not QKD

At Google, we are committed to research and innovation, and that includes
proactively addressing future security threats. In accordance with this
principle, we have been a strong proponent of post-quantum cryptography (PQC)
for years, starting with our
[early experiments](https://security.googleblog.com/2016/07/experimenting-with-post-quantum.html)
in Chrome in 2016. At present, we are
[actively](https://security.googleblog.com/2024/08/post-quantum-cryptography-standards.html)
rolling out the
[PQC algorithms standardized](https://csrc.nist.gov/projects/post-quantum-cryptography/post-quantum-cryptography-standardization)
by the U.S. National Institute of Standards and Technology (NIST) as our primary
quantum-safe technology. Our focus is on solutions that are secure, scalable,
and ready for both today's and tomorrow's challenges.

While PQC is our chosen path forward, it is not the only technology being
discussed for a quantum-resistant future. Another approach that has gained
attention is Quantum Key Distribution (QKD). As part of our commitment to
thorough research and providing the best security for our users, we have closely
evaluated QKD. In this post, we will share our assessment of the QKD technology
and explain why we believe PQC is the more mature and scalable solution for our
needs.

## Understanding Quantum Key Distribution (QKD)

Quantum key distribution (QKD) is a method based on principles of quantum
mechanics that allows two parties to produce a shared random secret key. In
contrast to “classic” solutions like public-key cryptography, QKD offers the
theoretical advantages of being able to detect eavesdropping and not relying on
mathematical hardness assumptions.

### Differentiators to current solutions

The following two sections describe the main differentiators between QKD and
“classic” solutions like public-key cryptography.

#### Detection of eavesdropping

Theoretical QKD protocols have the following property: if a third-party attempts
to eavesdrop on the communication channel between two parties (Alice and Bob),
this can be detected by Alice and Bob with high probability. This is easy to
detect because if a third-party wants to learn anything about the information
communicated between Alice and Bob, it needs to measure the state of the photon
being transmitted (which will collapse to the measured result), and then forward
the result to the other party. It is not possible for a third-party to copy the
quantum state of the photon being transmitted and replay it to the other party.
This is due to the no-cloning theorem \[WZ82\], which states that it is impossible
to create an independent and identical copy of an unknown quantum state.

#### No mathematical hardness assumptions required

Most cryptographic algorithms that we use in practice are only _computationally_
secure constructions and rely on the hardness of certain mathematical problems.
Computational security means that an adversary can break these schemes with a
finite amount of resources. However, this finite amount can be scaled to an
arbitrary number such as > 10^50 times the energy output of the Sun, as long as
the hardness assumption holds.

In contrast, there are also _information theoretic_ secure constructions, which
can not be broken by an adversary even with an infinite amount of resources,
making mathematical hardness assumptions irrelevant. Examples include the
one-time pad, various secret sharing schemes, or certain message authentication
codes \[WC81\].

Pivoting back to computational security: There is no guarantee that the
mathematical problems we base our cryptosystems on will be secure forever. For
example, an “efficient” solution to the P=NP problem would break most currently
used cryptosystems (however, most experts assume that P≠NP).

QKD, in theory and when its preconditions are met, provides information
theoretic security and does not require any mathematical hardness assumptions,
which is one of the main advantages of this type of protocol. However, there are
concrete and practical disadvantages and limitations, which we cover in the
following sections.

### Disadvantages and Limitations of QKD

#### Authentication

In order to deploy QKD, one has to ensure that Alice and Bob already have an
authenticated channel available (for instance \[BB84\] requires the communication
of some information over such a classic channel). QKD does not provide any
authentication mechanisms, which means that you will either need to use
asymmetric cryptography (which voids the previously mentioned advantage of not
needing any hardness assumptions) or rely on a pre-shared symmetric key (which
comes with operational complexity). Note that if you have a pre-shared secret,
then information theoretic secure message authentication codes could be used to
avoid the need of relying on hardness assumptions \[WC81\].

#### Costs and Scalability

QKD always happens between two parties. A migration to QKD would require a
complete replacement of all networking hardware, as each link you are securing
needs to have the corresponding QKD hardware on both ends. Adding any new device
would again require physically connecting it with every other device, which is
not scalable. For a global network at Google's scale, replacing existing
hardware with specialized QKD equipment in our data centers is not a practical
or scalable solution. Finally, providing end-user security would require the
user device to have a direct link to every server it connects to, which is
operationally infeasible.

#### Range Limitations

All commercial QKD solutions have a limited range (~100km), and security is only
guaranteed between two endpoints. Extending the range would require a repeater,
which has to be trusted and therefore introduces a high-risk of interception or
backdooring the QKD network. In particular for networks with a highly
distributed nature, migration to QKD infrastructure seems infeasible at the
moment. Free space key agreement and _quantum repeaters_ may address some of
these issues, but will not be available commercially for the foreseeable future.
This range limitation is further complicated when wireless data transmission is
desired, which currently does not have any commercial solutions at all.

#### Low-Throughput / Key Generation Rate

Currently available commercial solutions achieve a throughput of kilobits per
second, which makes them unusable for most practical applications. It would be
easy to extend this key material using symmetric key cryptography and obtain a
more efficient solution. However, in this case it’s unclear why you would want
to use QKD in the first place, as you again would need to rely on additional
security assumptions. In this case, having a pre-shared key between two parties
and deriving additional key material would provide comparable security
guarantees.

With the current throughput rates and requirement of distributing hardware, one
could alternatively consider just exchanging a storage medium with random bits.
A disk with 5TB (<100$) of storage, from which one would extract random bits
at the rate of a current QKD device, would last for 1000 years.

#### Partial Solution

QKD only addresses the key agreement problem, hence the reliance on
cryptographic assumptions is still required to construct other ubiquitous and
frequently used cryptographic primitives, such as hash functions or digital
signature schemes. In any large-scale infrastructure you will therefore not be
able to achieve security against an unbounded adversary by deploying QKD, which
makes the actual risk reduction questionable.

#### Implementation Security

The security properties of QKD are solely guaranteed for the theoretical
protocols. In practice, the security of QKD has very strict requirements on the
hardware used to implement it. If these requirements are not met, the resulting
implementation can be considered completely insecure. An overview of practical
challenges can be found in \[BLMS00\]. For example, side-channel resistance is not
well understood for these devices. Furthermore, testing and certification
processes for this type of hardware are still immature. In the real world, many
attacks have been demonstrated which break these commercial systems (see
\[LWWESM10\], \[GLLSKM11\]).

## Our Path to a Quantum-Resistant Future: PQC and Cryptographic Agility

As a conclusion of the above assessment, we believe that the best way to achieve
a quantum-resistant future is through a combination of post-quantum cryptography
and cryptographic agility, and not through the implementation of QKD. PQC offers
a scalable and secure solution that can be implemented on classic hardware.
Cryptographic agility, i.e. the ability to change algorithms or parameter sets
without major engineering effort, is our strategy for future-proofing Google’s
infrastructure.

As we've detailed in our previous
[blog post on Cryptographic Agility and Key Rotation](https://bughunters.google.com/blog/6182336647790592/cryptographic-agility-and-key-rotation),
a system that can rotate its keys is also able to support cryptographic agility
for its algorithms. This allows us to be prepared for future threats and to
update our cryptographic primitives as needed.

## Our Position on QKD

We currently see very limited value in QKD for Google’s infrastructure. The
problems QKD addresses are narrow and all practical implementations have severe
limitations. The main benefit of QKD would be to minimize the impact of a
mathematical breakthrough that threatens our current cryptographic algorithms.
However, the risk of such a breakthrough is small, and due to its many
limitations, it is highly unlikely that deploying QKD would adequately address
this risk.

For these reasons, we are neither rolling out QKD in production at Google, nor
are we exploring a side-by-side coexistence of QKD with our current systems. We
believe that QKD is a technology that may become useful for a narrow set of use
cases in the future, and we will continue to monitor its development. However,
for now, our focus is on the widespread adoption of PQC and the implementation
of cryptographic agility.

Our position is in line with the recommendations of several national security
agencies, including the NSA (USA), NCSC (UK), and BSI (Germany), all of which
have advised prioritizing the adoption of PQC over QKD (see the
[Other Positions](https://bughunters.google.com/blog/4625466008862720/google-s-commitment-to-a-quantum-safe-future-why-pqc-is-google-s-path-forward-and-not-qkd#other-positions)
section for details).

## Conclusion

Google is committed to ensuring the security of our users and customers, both
today and in the future. We believe that the combination of post-quantum
cryptography and cryptographic agility is the most effective and scalable way to
address the threat of quantum computers. While we will continue to follow
research on QKD, our efforts are focused on the practical and robust solutions
offered by PQC.

## Other Positions

- NSA view on QKD
( [link](https://www.nsa.gov/Cybersecurity/Quantum-Key-Distribution-QKD-and-Quantum-Cryptography-QC/))
- NCSC position on QKD
( [link](https://www.ncsc.gov.uk/whitepaper/quantum-security-technologies))
- ANSSI, NLNCSA, NCSA, BSI joint position paper
( [link](https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/Crypto/Quantum_Positionspapier.html))
- ANSSI view on QKD
( [link](https://cyber.gouv.fr/en/publications/should-quantum-key-distribution-be-used-secure-communications))
- BSI view on QKD
( [link](https://www.bsi.bund.de/EN/Themen/Unternehmen-und-Organisationen/Informationen-und-Empfehlungen/Quantentechnologien-und-Post-Quanten-Kryptografie/Quantenkryptografie/quantenkryptografie.html))
- Rebuttal by ETH authors on the NSA criticism of QKD
( [link](https://arxiv.org/pdf/2307.15116.pdf))

## References

\[BB84\] Bennett, C.H. and Brassard, G., 2014. Quantum cryptography: Public key
distribution and coin tossing. Theoretical computer science, 560, pp.7-11.
( [Link](https://pdf.sciencedirectassets.com/271538/1-s2.0-S0304397514X00411/1-s2.0-S0304397514004241/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEEsaCXVzLWVhc3QtMSJHMEUCIQDjTgNZFynREsU8Yb6f0TV4twlVpVbBf5Xdn1Fe22uqMgIgWuGRV6gIF142L7j6vgezvyCgILJn4j5OVMs14qTkaHMqvAUIo%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAFGgwwNTkwMDM1NDY4NjUiDMm96qSYn8JYoR9VBSqQBZfCLEWBfVAXazmPW%2FTdHd74jS90Vt2JNg1YGAPtVLNYv0wemE0UiDR5x8%2FNDuSodcTRRcLHgSXAcCu41p10oKHpm9HhpbRy0xZcnG8cQ2TPySNwGm6xRX6QdXWC3EiIHchZ2ivjMNc818kAsttpeAd7DifB%2FgFW%2FHB70okfVs11uuGp5IgxrJQ3JEZ%2FYRpc%2BT2lW8TEwGyZsUQYv7QRjOojze%2Ffj6SMhhgxuA7ne%2F6ThKPH%2FkyMXXK9XvgqMXuwgl%2B4ix3QTZqBUeI2uuL7tGrBtylyI4p48%2BbruxiThgESnF41phYf0ItS1Y7b5wfXlu2KlYr%2FABY5bMcTNF0K2a5Mf9LpWttD%2BkO7XMHJRt3lJh4m5ooeOmF5lRkeljCf79UxdzwOuCKKG3tcrqgAfYMbLpeJyzeoBCxX3%2BVj3oBjtsp3tDgcgBwJZmy7mr%2BAGV05LHiIAq5CkLmN1Vs3vzSvfFp1AzObvIbFvLYMshbfhqrld0pIBvin0llAwwepH4qaLLTB%2FAIedg%2Fj8nym6JozNLDKGt4m85BBXfEr%2FgQt%2B01MugI2Jsz%2Fd5P5sSmhMNjibK7SwAYHtZ2qOJ5U3MHwG7wC5oQMBjkDvY%2B4Z8tNkDh8gakBhksM42aP4Hf%2B5bJ2He%2FjjMm%2B%2BEnXyCcj2ucWltZq79DNqLC9JXU%2BOeMyla8kdjNaFkFaCyCpDONfh2psqgqYcT3pmzadSl4WGR0TzZ7IDNa%2BhMrxzIvLExa7cBrMdTpDszHjuG%2BVYQ8cOc0gDTlnrJRg7568ZvsCpBzONk0CloQmvX02IseQYitzdEBrSCsiLaZ2F9wAqbQBOaVMC9mJEzMG6kt3ODR4Gb8gWIAlQuVZ3o32oG%2BpDoQBMNXUkasGOrEBrLMR%2BYZKeIv9JWnGTKEyBo%2Bjwk%2BRQGOmPTKBgyOuWZ2paWV0jNWPo7vdvn%2FyaxMwffshI8auL47Da2799ghpPjSyZQyowC6RLpCboeRGJGW7vzfX%2FXrkLvrq25v51pBZ1B0Vx21S9mIfRGMxTcGT4qc5kBpfWCkDnols6g97Tbi67ushJrLYi201S6JJGGr0xEjVX4m7aY7VMJOLr2nSx8XqJNL1x6PdVon4XomYPGf0&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20231127T102953Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYRXNJCPXD%2F20231127%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=e04c1c4b6bc78055489cf9fdce8c702f2a4010a74527b4d6caacfb6f80395333&hash=2bfff9032758d7f605c104baefc936dfc9666b7bb1d58ef4536d0042b5d56135&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0304397514004241&tid=spdf-547db162-66c4-4a56-9924-d4c98ad5e9bf&sid=67c6398546e3e247c1581ce-8d96315ac8dbgxrqb&type=client&tsoh=d3d3LnNjaWVuY2VkaXJlY3QuY29t&ua=050f5a51045f03565a01&rr=82c9b14eec350e6d&cc=ch))

\[WC81\] Wegman, M.N. and Carter, J.L., 1981. New hash functions and their use in
authentication and set equality. Journal of computer and system sciences, 22(3),
pp.265-279.
( [Link](https://www.sciencedirect.com/science/article/pii/0022000081900337))

\[WZ82\] Wootters, W.K. and Zurek, W.H., 1982. A single quantum cannot be cloned.
Nature, 299(5886), pp.802-803.
( [Link](https://www.nature.com/articles/299802a0))

\[BLMS00\] Brassard, G., Lütkenhaus, N., Mor, T. and Sanders, B.C., 2000, May.
Security aspects of practical quantum cryptography. In International conference
on the theory and applications of cryptographic techniques (pp. 289-299).
Berlin, Heidelberg: Springer Berlin Heidelberg.
( [Link](https://arxiv.org/abs/quant-ph/9911054))

\[LWWESM10\] Lydersen, L., Wiechers, C., Wittmann, C., Elser, D., Skaar, J. and
Makarov, V., 2010. Hacking commercial quantum cryptography systems by tailored
bright illumination. Nature photonics, 4(10), pp.686-689.
( [Link](https://arxiv.org/pdf/1008.4593v2.pdf))

\[GLLSKM11\] Gerhardt, I., Liu, Q., Lamas-Linares, A., Skaar, J., Kurtsiefer, C.
and Makarov, V., 2011. Full-field implementation of a perfect eavesdropper on a
quantum cryptography system. Nature communications, 2(1), p.349.
( [Link](https://arxiv.org/pdf/1011.0105v2.pdf))

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab