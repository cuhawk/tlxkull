---
source: jack-cable
source_url: https://cablej.io/blog/k-anonymity
title: "Attacks on Have I Been Pwned?'s model of k-anonymity"
description: "Attacks on Have I Been Pwned?'s model of k-anonymity"
---

Last year, Troy Hunt and Cloudflare launched the _Have I Been Pwned?_ Pwned Passwords database, which allows searching a database of over 500,000,000 passwords to check if a given password has been compromised in a data breach. The service has been widely adopted, and now ships with password managers including 1Password and Bitwarden. The security model of this scheme relies on the concept of k-anonymity, which has been promoted as protecting user passwords sent to the service. However, such protection is limited: in this post, we exhibit attacks for learning user passwords under certain assumptions, demonstrating that this model of k-anonymity does not protect password privacy even when a user's password has not previously been compromised.

The basis for the Pwned Password models relies on a proposal by Cloudflare to apply k-anonymity to search compromised passwords[1](https://cablej.io/blog/k-anonymity/#dfref-footnote-1). In short, the idea is to prevent the server from outright learning a user's password by reducing the probability a server can identify a user's password to  for some large . This is accomplished by truncating hashes of passwords and only sending the first few characters of the hash to the database, which then returns all hashes which begin with those characters. Thus, if the server returns 500 possible hashes, then the probability that the user's password is any one of the returned hashes is , assuming a uniform distribution of passwords and that the user's password is indeed a compromised password.

It should be immediately clear that the server does learn information about a user's password. Given that the first 5 characters of a user's hashed password are sent to the server, an adversary learns that a user's password belongs to a subset of passwords beginning with the truncated hash, representing  of all possible passwords. In practice, as passwords are not randomly distributed, an adversary gains a 12 times advantage in guessing a user's password, as detailed by Li, Pal et al. in related work[2](https://cablej.io/blog/k-anonymity/#dfref-footnote-2). Under perfect privacy, the server should be no better off in knowing a user's password.

### Attack Model

We begin by defining an attack model for a password lookup database. We assume a lookup server operating maliciously, whether due to malicious intent by the operator or server compromise. This is expressly the attack model used by HIBP and Cloudflare when designing the model: passwords should be protected "even if you _don't_ trust the service or you think logs may be leaked and abused"[3](https://cablej.io/blog/k-anonymity/#dfref-footnote-3). The server wishes to learn a user's password(s) given hashes sent by the user to the server, and exploit them to gain access to user accounts.

Indeed, this can only be exploited if the adversary has knowledge of the user's username or email address. Such an attack is feasible as Have I Been Pwned also allows users to search if their email address was compromised. Thus, a server acting maliciously could collect user IP addresses from both email and password lookups and correlate learned passwords with email addresses to compromise user accounts.

In order to further evaluate this model, we consider an attack game as follows. An adversary  aims to predict some password of a user, who has  passwords . With equal probability, the adversary is given either a list of truncated hashes  of each of the user's passwords or a list of truncated hashes  chosen uniformly at random. The advantage of the adversary is then the difference , where  denotes the set of the user's passwords. Intuitively, this conveys that the system is secure if the attacker performs no better at guessing user passwords given truncated hashes compared to having no prior information.

Formally, we would consider the attacker to win the attack game if they have a non-negligible advantage. However, as revealing a small amount of information may be acceptable for practical use, we consider scenarios where an attacker has significant advantage in identifying user passwords. We demonstrate that this is indeed possible and is a risk for current implementations.

### Current Applications

As of now, there exist two large-scale implementations of k-anonymity for protecting password lookups. Have I Been Pwned offers the [Pwned Passwords](https://haveibeenpwned.com/Passwords) service to check passwords against a list of 500 million passwords, which utilizes Cloudflare's model of k-anonymity. Google's Password Checkup tool [was launched](https://security.googleblog.com/2019/02/protect-your-accounts-from-data.html) earlier this year, and also utilizes k-anonymity by sending a partial hash of username-password combinations to a server. As there exists less public information about Google's scheme, we focus on the HIBP implementation, although it is likely Google's model also exposes information to a similar extent.

Integrations with the HIBP service present the most tangible risk to users. In particular, several password managers, notably 1Password and Bitwarden, directly utilize the Pwned Passwords API to notify users of breached passwords. 1Password, for instance, offers its [Watchtower](https://support.1password.com/watchtower/) service to notify users of compromised passwords. Among other actions, Watchtower repeatedly queries all of a user's passwords against the HIBP database. As we will see, looking up multiple passwords further enables attacks as user passwords are often not chosen independently, which increases the ability of a server to learn user passwords.

### Similar Password Re-use

It is well known that users often reuse passwords across sites (indeed, this is what led to the creation of services like HIBP). Beyond this, users will often modify passwords slightly across different websites. In an empirical study of over 28 million passwords, Wang, Chun et al. show that 19.3% of password pairs (i.e. combinations of two passwords used by a user) can be derived by modifying one of the passwords, while 34.3% of pairs are identical[4](https://cablej.io/blog/k-anonymity/#dfref-footnote-4). Further, the majority of password modifications are simple: most users simply append a digit at the end, and 24.2% of the time that digit is a 1.

The fact that users reuse passwords is of little use in this attack game, as a server will receive identical hashes and not gain additional information besides the fact that a user reuses passwords. However, the usage of modified passwords does allow an adversary to learn significant information. If a server is aware that a user uses multiple modified passwords (which is likely based on the empirical research), the server now has not one, but multiple hashes from which to learn information.

We generalize password modification to the notion of neighboring passwords, which encapsulates two passwords that are similar to eachother. We consider the number of possible neighbors a password may have under different models of similarity. For instance, passwords may be considered neighbors if the passwords match after appending a character to one password, in which case each password would have  neighbors, given an alphanumeric keyspace. Other models, such as a Levenshtein edit distance of 1 yield  possible neighbors, where  is the length of the password. For this post, we let  define the number of neighbors possessed by any given password.

### Attack 1: Password Already Compromised

We first consider the scenario where user looks up a password that has already been compromised. Consider a scenario where a password lookup server returns an average of  hashes for each lookup. Assuming that the user's password is already breached, the server knows that the password is one of these  hashes, giving the server a  chance of correctly identifying a user's password in the attack game. Given that implementations such as HIBP return an average of 500 passwords per bucket, this is already non-negligible and leaves the attacker significantly better off at identifying a user's password.

We then consider the case of password modification, where a user makes a small change to their original password, resulting in two neighboring passwords. The user submits two different requests with hashes of the modified passwords. The server again responds with  hashes for both requests. As we assume both submitted passwords are in the breached database, the server knows that each password is one of the  hashes. Given the plaintext version of all hashes, the server may compare the plaintext passwords across the two lists. With high probability, the only two neighboring passwords across both lists will be the passwords submitted by the user. Thus, the server learns the user's plaintext password given only two partial hashes given compromise of both passwords.

While it is clear that this model does not protect privacy when passwords are already compromised, a user should change their password if they know it is compromised. This could pose a problem, however, if an attacker is active and lies to users that their password is safe. This is another concern, though it relies on a stronger assumption of malicious activity by the server. We now transition to the perhaps more interesting case where none of the user's original passwords have appeared in a breach before.

### Attack 2: Randomly Generated Modified Passwords

In the second attack, we consider the case where a user chooses a password that has not been breached. The user then proceeds to use neighboring password on other websites, or otherwise store it in a password manager. We let the  be the number of bits of entropy of the user's password. Using the HIBP service, the user then sends the first 5 characters of each password's hash to the password lookup server.

The initial keyspace is  bits. With the first partial hash, the attacker can narrow the number of possible passwords by a factor of , as there are  possible 5-character hex strings and the attacker knows the user's password must fall into the bucket of hashes beginning with those 5 characters. Even with just one hash, this is a significant reduction on the possible range of passwords.

We then consider the effects of sending multiple neighboring passwords. Given each additional hash, an attacker further reduces the possible range of passwords by a factor of . For example, using a password of 56 bits of entropy (as suggested by 1Password [here](https://blog.1password.com/how-long-should-my-passwords-be/)) and given the appended character model of neighboring passwords, an attacker needs only 3 modified passwords to reduce the range by a factor of , i.e. with high likelihood there is only one possible password that belongs to the original bucket of hashes and has neighbors in each of the other three buckets. Thus, given a small number modifications to a user's password, the space of possible passwords is vastly reduced.

Furthermore, depending on the complexity of the password, it is feasible for a server to compute the user's original password. As when cracking hashed passwords, the attack is exponential in the size of the password space, since every possible hash must be attempted. Rainbow tables can aid when targeting many users by first precomputing a lookup table in exponential time, allowing both subexponential storage and subexpoential time lookups once the table has been generated. This is possible in practice, as there exist readily available rainbow tables for 9 digit alphanumeric passwords with a keyspace of [5](https://cablej.io/blog/k-anonymity/#dfref-footnote-5), which captures the majority of user passwords today. In an attack, such rainbow tables could be adjusted to search for all passwords that match the first 5 characters of a hash.

### Demo

To demonstrate this attack, I have constructed a mock server that guesses original passwords based only on partial hash information, as would occur using HIBP. Given limited computing resources, this demo considers a toy example where a user's password keyspace is  and users send 3-character, 12-bit hashes to the server.

[Launch demo](http://pws.cablej.io/)

### Defenses

Certain changes to the design of this API can make it more difficult for a malicious server to learn user passwords, though under this model the fundamental risk will always be present. For instance, sending a smaller number of characters of the hashed password requires only a linear amount of additional information (in the form of similar passwords) in order to learn user passwords. Other possible adjustments include adding noise to queries in the form of additional randomly generated passwords, which also increases the K-value at the cost of more communication. However, as demonstrated, seemingly benign usage facts can be used to break the privacy of these systems, so such modifications should not be implemented without in-depth review of possible attacks.

In order to prevent the specific attack described in this post, a client may perform checks on passwords being sent, such as computing Levenshtein edit distance, in order to prevent sending hashes of similar passwords. This would make it more difficult for a server to construct attacks on dependent passwords, and is currently being evaluated by 1Password as a possible mitigation.

Other models exist that completely preserve the privacy of password lookups, although the implementation is likely not currently feasible. This is an instance of the Private Information Retrieval problem, where a user seeks to look up a key in a database without revealing the key to the server. And while PIR schemes with sublinear communication do exist[6](https://cablej.io/blog/k-anonymity/#dfref-footnote-6), computation linear in the size of the database is likely to prevent any efficient implementations for the time being. [Google's implementation](https://security.googleblog.com/2019/02/protect-your-accounts-from-data.html) does utilize Private Set Intersection, a related problem, in addition to k-anonymity, so it may be possible to combine these methods to reduce risk. I welcome additional details on Google's implementation and further research in this area.

### Conclusion

We have demonstrated that under certain assumptions, a third-party server implementing this model of k-anonymity can learn user passwords. As a result, this model does not preserve password privacy, despite claims of the contrary by Cloudflare, Have I Been Pwned, and 1Password (for instance, see 1Password's statement that "Their server never receives enough information to reconstruct my password"[7](https://cablej.io/blog/k-anonymity/#dfref-footnote-7) ).

Under the current scheme, password managers must decide whether the benefits in alerting users of compromised passwords outweigh the risks of revealing password information to a third-party server. It goes without saying that preventing password reuse is extremely valuable, as more and more attacks occur every day. With that being said, for users who do not have compromised passwords, this only adds a risk of a third party learning their passwords from these lookups. Fundamental to the design of both 1Password and Bitwarden is that a user's password never leaves their device unencrypted, and that the password manager's server can never recover a user's account — to the extent that if a user loses their master password, they must restart their account from scratch[8](https://cablej.io/blog/k-anonymity/#dfref-footnote-8)[9](https://cablej.io/blog/k-anonymity/#dfref-footnote-9). Allowing a third-party server to learn user passwords breaks a fundamental component of the password manager security model. Due to these concerns, it is my recommendation that password managers such as 1Password and Bitwarden stop using this model of k-anonymity until the model is redesigned and analyzed rigorously. At minimum, password managers should notify users that password information is revealed to a third party server, which if acting maliciously could learn passwords.

* * *

### Disclosure Timeline

June 16 - Initial report to 1Password

June 16 - Initial report to Bitwarden

June 17 - Considered "out of scope" by Bitwarden as it relies on Pwned Passwords, an "upstream dependency". In order to keep the integration, Bitwarden is considering adding a notice to users warning them that a third-party server may learn information about their passwords.

June 17 - Disclosed to Troy Hunt

June 21 - Troy Hunt responds not planning to make any changes, stating "we’re aware of mathematics, the present model was the best trade-off of performance, usability and privacy" and "It’s a lot of long bows to draw for there to be any tangible risk, not least of which is for there to be malicious intent on my behalf"

June 26 - Response by 1Password that they are evaluating tradeoffs in the usage of HIBP. For the time being, 1Password plans to add an alert to users explaining the risks and is evaluating further mitigations.

* * *

#### References

1 Ali, Junade. “Validating Leaked Passwords with k-Anonymity.” _The Cloudflare Blog_, Cloudflare, 13 Dec. 2018, blog.cloudflare.com/validating-leaked-passwords-with-k-anonymity. [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-1 "back to document")

2 Li, Lucy, Bijeeta Pal, Junade Ali, Nick Sullivan, Rahul Chatterjee, and Thomas Ristenpart. "Protocols for Checking Compromised Credentials." arXiv preprint arXiv:1905.13737 (2019). [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-2 "back to document")

3 Hunt, Troy. “I've Just Launched ‘Pwned Passwords’ V2 With Half a Billion Passwords for Download.” _Troy Hunt_, Troy Hunt, 11 June 2018, www.troyhunt.com/ive-just-launched-pwned-passwords-version-2/#cloudflareprivacyandkanonymity. [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-3 "back to document")

4 Wang, Chun et al. “The Next Domino to Fall: Empirical Analysis of User Passwords across Online Services.” _CODASPY_ (2018). [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-4 "back to document")

5 _List of Rainbow Tables_, Project RainbowCrack, project-rainbowcrack.com/table.htm. [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-5 "back to document")

6 Gasarch, William. (2004). A survey on private information retrieval. Bulletin of the European Association for Theoretical Computer Science EATCS. 82. [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-6 "back to document")

7 Shiner, Jeff. “Finding Pwned Passwords with 1Password: 1Password.” _1Password Blog_, 28 Aug. 2018, blog.1password.com/finding-pwned-passwords-with-1password/. [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-7 "back to document")

8 _Find Your Secret Key or Setup Code_, 1Password, support.1password.com/secret-key/#get-more-help. [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-8 "back to document")

9 _I Forgot My Master Password_, Bitwarden, help.bitwarden.com/article/forgot-master-password/. [↩](https://cablej.io/blog/k-anonymity/#ref-footnote-9 "back to document")

X Follow Button

[Jack Cable - Blog](https://cablej.io/)

Twitter Widget Iframe