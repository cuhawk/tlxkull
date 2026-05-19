---
source: bughunters
source_url: https://bughunters.google.com/blog/cryptographic-agility-and-key-rotation
title: "Cryptographic Agility and Key Rotation - Google Bug Hunters"
description: "In the 3rd post in our series on PQC, we discuss how to actually migrate to PQC and explore the role cryptographic agility and key rotation play in this process."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/cryptographic-agility-and-key-rotation#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Cryptographic Agility and Key Rotation

![](https://storage.googleapis.com/bughunters-article-images/blogs/sschmieg.jpg)

Sophie Schmieg

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/kste.jpg)

Stefan Kölbl

Information Security Engineer

![](https://storage.googleapis.com/bughunters-article-images/blogs/guillaumee.jpg)

Guillaume Endignoux

Software Engineer

Published: Jun 24, 2024

Post-Quantum Cryptography

[RSS Feed](https://bughunters.google.com/feed/en)

# Cryptographic Agility and Key Rotation

Continuing our blog post series on PQC \[1\], today we will discuss how one can
actually migrate to PQC. Let's assume we have a system that can easily handle
the increased public key, ciphertext, and signature sizes for PQC without
requiring major changes in design \[2\]. While this is not a trivial assumption in
itself, it is the best case scenario. How do we then migrate a system like this
from its current classical cryptography to PQC?

## Defining Cryptographic Agility

This is usually when the term _cryptographic agility_ is mentioned, often used
as a near magical solution that will not only solve the PQC transition, but also
make any later migrations easier. While frequently mentioned, it is relatively
hard to precisely define the term. Different definitions have been proposed, for
example by [Alnahawi et al.](https://eprint.iacr.org/2023/487) For our purposes,
let's start with the intended goal and work towards more concrete requirements.
For this, we will use the following definition:

> Crypto agility means the ability to change algorithms or parameter sets
> without major engineering effort

Armed with this working definition, we can look at various protocols such as
TLS, SSH, and ALTS. In each of these cases, we see that algorithms and
parameters are usually dynamically negotiated between participants in a secure
fashion. Normally, one side sends its supported algorithms, and the other side
selects the algorithm to use. As long as both sides authenticate the full
exchange, including which algorithms were proposed, this is a secure mechanism
which is robust against downgrade attacks, i.e. an adversary cannot force two
parties to use a weaker algorithm than the one the parties agreed on, and it can
easily be
[extended to include PQC algorithms](https://datatracker.ietf.org/doc/draft-westerbaan-cfrg-hpke-xyber768d00/).
Certificate signatures also include algorithm information for their public keys,
allowing implementations to support different algorithms as well.

## Challenges with cryptographic agility

If standardized protocols already provide cryptographic agility, why is
migration to PQC still considered hard? Furthermore, if past protocols already
have inbuilt agility, why are some cryptographers
[advocating against](https://words.filippo.io/dispatches/registries-considered-harmful/)
this approach when designing new protocols?

### Cryptographic agility can lead to absurd complexity and technical debt

One problem often observed when crypto agility is overemphasized is an
accumulation of complexity and technical debt. The more parameters get
negotiated independently from one another, the more complex a protocol becomes.
Often, there are only a few heavily used algorithms and parameter sets, making
support for others a nightmare in maintenance and ripe for vulnerabilities. As
an example, explicit elliptic curves have been a
[frequent](https://www.openssl.org/news/secadv/20220315.txt) [source](https://blog.trailofbits.com/2020/01/16/exploiting-the-windows-cryptoapi-vulnerability/)
of [security](https://www.openssl.org/news/secadv/20190910.txt) vulnerabilities,
leading to them being forbidden in
[RFC 5480](https://www.rfc-editor.org/rfc/rfc5480#section-2.1.1). The lesson
here is not that cryptographic agility is harmful per se, but that it needs to
be used appropriately.

### Negotiation is a synchronized operation

The algorithm negotiation described above is an inherently synchronous
operation, requiring a full roundtrip in order for the client to know which
ciphers to use. This is a problem both in asynchronous environments, where it
can lead to implementations being
[unable to interoperate](https://www.latacora.com/blog/2019/07/16/the-pgp-problem/#negotiation),
as well as in synchronous environments that try to minimize round trips. As an
example, TLS 1.3 needs the client to predict the correct key agreement method in
its first message for the best performance, as it tries to include the right
keyshare (including multiple PQ keyshares is cost prohibitive) in ClientHello.
If the prediction is wrong, the server will send a HelloRetryRequest, resulting
in an extra roundtrip and a slower handshake. So while TLS supports
cryptographic agility, actively using this agility comes at a cost and is
especially impactful for PQC with larger keys.

### Common agility design and implementation mistakes lead to insecure systems

Like many things in cryptography, it is unfortunately very easy to create an
insecure system through misuse of secure primitives. Cryptographic agility can
quickly become a source of such vulnerabilities, if performed incorrectly.
Agility allows changing an algorithm on the fly, so care must be taken that
whatever algorithm is chosen is agreed upon by all legitimate parties involved,
and was actually intended to be chosen. The poster child of vulnerabilities
stemming from incorrectly supporting agility is JSON Web Tokens (JWT), where the
token itself has a field determining the algorithm used for its verification.
Besides an attacker being able to simply choose
" [none](https://www.howmanydayssinceajwtalgnonevuln.com/)" as the verification
algorithm, it also allows the attacker to switch from asymmetric signatures to
symmetric MACs, or, in the case of PQC, allows downgrading from a quantum-safe
signature scheme to one that is not, if the implementation honors the value of
the algorithm field. In the case of JWT, this led to the creation of
[RFC 8725](https://datatracker.ietf.org/doc/html/rfc8725#name-validate-all-cryptographic-),
explicitly instructing implementers to discard the algorithm provided in the
token for the purpose of algorithm choice and to use application-provided
algorithm choices instead, with the algorithm field having to agree with the
separately provided input.

For synchronous protocols, there are similar pitfalls. If the protocol is not
using the transcript of the entire exchange as input for the Key Derivation
Function (KDF), an adversary can manipulate the cipher negotiation messages in a
way that will result in the client and server both believing the other one is to
blame for the choice of a weak cipher, and continuing with the connection,
leading to a downgrade attack.

## How cryptographic agility relates to key rotation

With all this in mind, we can design a system that is agile, while avoiding the
vulnerabilities mentioned. In the case of synchronous protocols, cryptographic
agility is fairly well established, so we will focus on the asynchronous cases
including tokens and certificates in a PKI. The main avenue for vulnerabilities
in these cases is that the algorithm information could be taken from an
untrusted, unauthenticated source, instead of an authenticated one. Thankfully,
all cryptographic operations already have an input that by construction has to
be authentic: the key itself. Storing authentic metainformation like the
algorithm or the used parameters in the same place as the raw key material is
stored allows us to enable agility without letting the attacker choose the
algorithm we use.

It also shows us an important corollary to our initial definition of
cryptographic agility: If the key determines the algorithm used, then in order
to be able to change the algorithm, we need to be able to change the key.
Moreover, if the algorithm information is seen as part of the key, changing the
algorithm and changing the key become the same operation. Assuming that our
system is able to support the new algorithm – a somewhat bold assumption in
light of PQC's signature sizes – any system that is able to rotate its keys is
able to support cryptographic agility for its algorithms, and being able to
rotate keys is a best practice in any case.

## Rotating cryptographic keys without causing outages

One of the main benefits of an automatic key rotation pipeline is ensuring the
process of replacing key material is well exercised, so it can be relied upon
when a key rotation is necessary, such as after a compromise. Key rotation also
provides some amount of passive recovery in the case of undetected compromises.

This being said, key rotation, while simple in theory, is notoriously difficult
in practice, creating substantial reliability risks if a key is introduced or
deleted at the wrong time. If the system tries to just swap an old key with a
new key, this becomes a strict consistency problem, which is extremely
challenging to handle. Instead, we need a way to rotate keys in an eventually
consistent way.

In the following, we will discuss how to do this using
[Tink](https://developers.google.com/tink), our Open Source cryptographic
library, as an example. For this example, it is helpful to consider a set of
keys instead of a single key as our basic object. Importantly, all keys in this
keyset need to be able to perform the same cryptographic operation, (called
"primitive" in
[Tink's case](https://developers.google.com/tink/design/primitives_and_interfaces)).
In contrast to hybrid constructions, the keys in a set are not used in
conjunction, but in disjunction. This means that every key in the keyset is
fully trusted, and the system is only as secure as the least secure key in the
set.

![](https://storage.googleapis.com/bughunters-article-images/blogs/crypto_agility_01.png)

_Fig. 1. Visualization of a Tink keyset with four keys, including their_
_algorithm information and parameters_

Of these keys, one has to be marked as the primary key (called "active" in NIST
SP 800-57 Part 1), which is used to perform the active operation such as signing
or encrypting. As a performance optimization, Tink can optionally
[prefix the identifier](https://developers.google.com/tink/wire-format) of this
primary key when creating ciphertexts and signatures in the case of most
primitives. This identifier allows the passive operation, such as verifying or
decrypting, to jump directly to the corresponding key. Similar to hybrid
constructions, this keyset construction can be seen as a separate implementation
of the same primitive that the constituent keys implement.

With this keyset construction, we can now attempt to rotate keys. This rotation
happens in three steps:

1. We remove the oldest key in our keyset, in our example the RSA-PKCS1 key
with the ID `da3c`.
2. We promote the newest key of the keyset, the ECDSA key with the ID `34ae`,
to be the new primary key.
3. As a last step, we add a freshly generated new key to the keyset, to be
activated in the next rotation. In the example, this is a hybrid
ECDSA+Dilithium key with ID `fe71`. The fact that this key is hybrid is not
a special consideration here, and it is treated just like any individual
signature key would. Importantly, both the PQC and the classical portions
are generated at the same time.

![](https://storage.googleapis.com/bughunters-article-images/blogs/crypto_agility_02.png)

_Fig. 2. Visualization of the keyset after rotation has been performed_

It is easy to see that this approach to key rotation will allow both the signer
and the verifier to be one version out-of-date without causing any problems. If
the signer has the newer keyset, they will create signatures using the key
`34ae`, which is present even in the verifier's outdated version. The other way
around, since we did not remove the key `a25f` yet, an updated verifier can
still verify signatures produced by a signer that is yet to update.

There are some further improvements one can make to this basic flow. For
example, we use [monitoring](https://www.youtube.com/watch?v=IAOWRO9Qn10&t=107s)
to inform our key management system if there are still ciphertexts/signatures
being decrypted/verified with an old version before removing them automatically.
In an asynchronous setting, the lifetime of these objects might be longer than
the active period of the keys. Further, for an asymmetric primitive, the full
key material does not have to be available to the active side, and only the
primary key needs to be accessible.

## Conclusions

In the case of asynchronous communication, cryptographic agility is closely
related to key rotation. While PQC algorithms have additional constraints that
might strain a system, designing a system with key rotation in mind is necessary
to allow for cryptographic agility. There are further concerns such as
implementation support to consider for individual cases, but a system that
stores key metadata with the key and allows for automatic key rotation is a
necessary condition for cryptographic agility and the PQC transition. If you are
using a keyset construction similar to the one used with Tink, keep in mind that
the keyset is only as secure as its least secure key – in other words, the
migration to PQC is only completed once the last purely classical key has been
rotated out of the keyset.

## Notes

\[1\] See
[Google's Threat model for Post-Quantum Cryptography](https://bughunters.google.com/blog/5108747984306176/google-s-threat-model-for-post-quantum-cryptography)
and
[Why Hybrid Deployments Are Key to Secure PQC Migration](https://bughunters.google.com/blog/5266882047639552/why-hybrid-deployments-are-key-to-secure-pqc-migration)

\[2\] An example would be desktop Chrome platforms, see
[Advancing Our Amazing Bet on Asymmetric Cryptography](https://blog.chromium.org/2024/05/advancing-our-amazing-bet-on-asymmetric.html)
for details

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab