---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/
title: "A New Attack Surface on MS Exchange Part 2 - ProxyOracle! | Orange Tsai"
author: "Orange Tsai"
published: 2021-08-06T16:00:00.000Z
description: "Hi, this is the part 2 of the New MS Exchange Attack Surface. Because this article refers to several architecture introductions and attack surface concepts in the previous article, you could find the"
---

* * *

![preview](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/7070a738a7bbb7f4-01.png)

Hi, this is the part 2 of the New MS Exchange Attack Surface. Because this article refers to several architecture introductions and attack surface concepts in the previous article, you could find the first piece here:

- [A New Attack Surface on MS Exchange Part 1 - ProxyLogon!](https://blog.orange.tw/2021/08/proxylogon-a-new-attack-surface-on-ms-exchange-part-1.html)

This time, we will be introducing ProxyOracle. Compared with ProxyLogon, ProxyOracle is an interesting exploit with a different approach. By simply leading a user to visit a malicious link, ProxyOracle allows an attacker to recover the user’s password in plaintext format completely. ProxyOracle consists of two vulnerabilities:

- [CVE-2021-31195](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-31195) \- Reflected Cross-Site Scripting
- [CVE-2021-31196](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-31196) \- Padding Oracle Attack on Exchange Cookies Parsing

# [Where is ProxyOracle](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/\#Where-is-ProxyOracle "Where is ProxyOracle") Where is ProxyOracle

So where is ProxyOracle? Based on the CAS architecture we introduced before, the Frontend of CAS will first serialize the User Identity to a string and put it in the header of `X-CommonAccessToken`. The header will be merged into the client’s HTTP request and sent to the Backend later. Once the Backend receives, it deserializes the header back to the original User Identity in Frontend.

We now know how the Frontend and Backend synchronize the User Identity. The next is to explain how the Frontend knows who you are and processes your credentials. The Outlook Web Access (OWA) uses a fancy interface to handle the whole login mechanism, which is called Form-Based Authentication (FBA). The FBA is a special IIS module that inherits the `ProxyModule` and is responsible for executing the transformation between the credentials and cookies before entering the proxy logic.

![](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/594b85a3fe49a0a8-02.png)

# [The FBA Mechanism](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/\#The-FBA-Mechanism "The FBA Mechanism") The FBA Mechanism

HTTP is a stateless protocol. To keep your login state, FBA saves the username and password in cookies. Every time you visit the OWA, Exchange will parse the cookies, retrieve the credential and try to log in with that. If the login succeed, Exchange will serialize your User Identity into a string, put it into the header of `X-CommonAccessToken`, and forward it to the Backend.

**HttpProxy\\FbaModule.cs**

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>``` | ```<br>protected override void OnBeginRequestInternal(HttpApplication httpApplication) {<br>    httpApplication.Context.Items["AuthType"] = "FBA";<br>    if (!this.HandleFbaAuthFormPost(httpApplication)) {<br>        try {<br>            this.ParseCadataCookies(httpApplication);<br>        } catch (MissingSslCertificateException) {<br>            NameValueCollection nameValueCollection = new NameValueCollection();<br>            nameValueCollection.Add("CafeError", ErrorFE.FEErrorCodes.SSLCertificateProblem.ToString());<br>            throw new HttpException(302, AspNetHelper.GetCafeErrorPageRedirectUrl(httpApplication.Context, nameValueCollection));<br>        }<br>    }<br>    base.OnBeginRequestInternal(httpApplication);<br>}<br>``` |

All the cookies are encrypted to ensure even if an attacker can hijack the HTTP request, he/she still couldn’t get your credential in plaintext format. FBA leverages 5 special cookies to accomplish the whole de/encryption process:

- `cadata` \- The encrypted username and password
- `cadataTTL` \- The Time-To-Live timestamp
- `cadataKey` \- The KEY for encryption
- `cadataIV` \- The IV for encryption
- `cadataSig` \- The signature to prevent tampering

![](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/236d9aec7a0f2fc7-03.png)

The encryption logic will first generate two 16 bytes random strings as the IV and KEY for the current session. The username and password will then be encoded with Base64, encrypted by the algorithm AES and sent back to the client within cookies. Meanwhile, the IV and KEY will be sent to the user, too. To prevent the client from decrypting the credential by the known IV and KEY directly, Exchange will once again use the algorithm RSA to encrypt the IV and KEY via its SSL certificate private key before sending out!

Here is a Pseudo Code for the encryption logic:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>``` | ```<br>@key = GetServerSSLCert().GetPrivateKey()<br>cadataSig = RSA(@key).Encrypt("Fba Rocks!")<br>cadataIV  = RSA(@key).Encrypt(GetRandomBytes(16))<br>cadataKey = RSA(@key).Encrypt(GetRandomBytes(16))<br>@timestamp = GetCurrentTimestamp()<br>cadataTTL  = AES_CBC(cadataKey, cadataIV).Encrypt(@timestamp)<br>@blob  = "Basic " + ToBase64String(UserName + ":" + Password)<br>cadata = AES_CBC(cadataKey, cadataIV).Encrypt(@blob)<br>``` |

The Exchange takes CBC as its padding mode. If you are familiar with Cryptography, you might be wondering whether the CBC mode here is vulnerable to the Padding Oracle Attack? Bingo! As a matter of fact, Padding Oracle Attack is still existing in such essential software like Exchange in 2021!

![](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/09282ddf111bae56-04.gif)

# [CVE-2021-31196 - The Padding Oracle](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/\#CVE-2021-31196-The-Padding-Oracle "CVE-2021-31196 - The Padding Oracle") CVE-2021-31196 - The Padding Oracle

When there is something wrong with the FBA, Exchange attaches an error code and redirects the HTTP request back to the original login page. So where is the Oracle? In the cookie decryption, Exchange uses an exception to catch the Padding Error, and because of the exception, the program returned immediately so that error code number is `0`, which means `None`:

> Location: /OWA/logon.aspx?url=…&reason=0

In contrast with the Padding Error, if the decryption is good, Exchange will continue the authentication process and try to login with the corrupted username and password. At this moment, the result must be a failure and the error code number is `2`, which represents `InvalidCredntials`:

> Location: /OWA/logon.aspx?url=…&reason=2

The diagram looks like:

![](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/593c155dbdf44f84-05.png)

With the difference, we now have an Oracle to identify whether the decryption process is successful or not.

**HttpProxy\\FbaModule.cs**

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>``` | ```<br>private void ParseCadataCookies(HttpApplication httpApplication)<br>{<br>    HttpContext context = httpApplication.Context;<br>    HttpRequest request = context.Request;<br>    HttpResponse response = context.Response;<br>    <br>    string text = request.Cookies["cadata"].Value;    <br>    string text2 = request.Cookies["cadataKey"].Value;    <br>    string text3 = request.Cookies["cadataIV"].Value;    <br>    string text4 = request.Cookies["cadataSig"].Value;    <br>    string text5 = request.Cookies["cadataTTL"].Value;<br>    <br>    // ...<br>    RSACryptoServiceProvider rsacryptoServiceProvider = (x509Certificate.PrivateKey as RSACryptoServiceProvider);<br>    <br>    byte[] array = null;<br>    byte[] array2 = null;<br>    byte[] rgb2 = Convert.FromBase64String(text2);<br>    byte[] rgb3 = Convert.FromBase64String(text3);<br>    array = rsacryptoServiceProvider.Decrypt(rgb2, true);<br>    array2 = rsacryptoServiceProvider.Decrypt(rgb3, true);<br>    <br>    // ...<br>    <br>    using (AesCryptoServiceProvider aesCryptoServiceProvider = new AesCryptoServiceProvider()) {<br>        aesCryptoServiceProvider.Key = array;<br>        aesCryptoServiceProvider.IV = array2;<br>        <br>        using (ICryptoTransform cryptoTransform2 = aesCryptoServiceProvider.CreateDecryptor()) {<br>            byte[] bytes2 = null;<br>            try {<br>                byte[] array5 = Convert.FromBase64String(text);<br>                bytes2 = cryptoTransform2.TransformFinalBlock(array5, 0, array5.Length);<br>            } catch (CryptographicException ex8) {<br>                if (ExTraceGlobals.VerboseTracer.IsTraceEnabled(1)) {<br>                    ExTraceGlobals.VerboseTracer.TraceDebug<CryptographicException>((long)this.GetHashCode(), "[FbaModule::ParseCadataCookies] Received CryptographicException {0} transforming auth", ex8);<br>                }<br>                httpApplication.Response.AppendToLog("&CryptoError=PossibleSSLCertrolloverMismatch");<br>                return;<br>            } catch (FormatException ex9) {<br>                if (ExTraceGlobals.VerboseTracer.IsTraceEnabled(1)) {<br>                    ExTraceGlobals.VerboseTracer.TraceDebug<FormatException>((long)this.GetHashCode(), "[FbaModule::ParseCadataCookies] Received FormatException {0} decoding caData auth", ex9);<br>                }<br>                httpApplication.Response.AppendToLog("&DecodeError=InvalidCaDataAuthCookie");<br>                return;<br>            }<br>            string @string = Encoding.Unicode.GetString(bytes2);<br>            request.Headers["Authorization"] = @string;<br>        }<br>    }<br>}<br>``` |

It should be noted that since the IV is encrypted with the SSL certificate private key, we can’t recover the first block of the ciphertext through XOR. But it wouldn’t cause any problem for us because the C# internally processes the strings as UTF-16, so the first 12 bytes of the ciphertext must be `B\x00a\x00s\x00i\x00c\x00 \x00`. With one more Base64 encoding applied, we will only lose the first 1.5 bytes in the username field.

> (16−6×2) ÷ 2 × (3/4) = 1.5

# [The Exploit](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/\#The-Exploit "The Exploit") The Exploit

As of now, we have a Padding Oracle that allows us to decrypt any user’s cookie. BUT, how can we get the client cookies? Here we find another vulnerability to chain them together.

## [XSS to Steal Client Cookies](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/\#XSS-to-Steal-Client-Cookies "XSS to Steal Client Cookies") XSS to Steal Client Cookies

We discover an XSS (CVE-2021-31195) in the CAS Frontend (Yeah, CAS again) to chain together, the root cause of this XSS is relatively easy: Exchange forgets to sanitize the data before printing it out so that we can use the `\` to escape from the JSON format and inject arbitrary JavaScript code.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>https://exchange/owa/auth/frowny.aspx<br>?app=people<br>&et=ServerError<br>&esrc=MasterPage<br>&te=\<br>&refurl=}}};alert(document.domain)//<br>``` |

![](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/7d510dfd776aae8e-06.png)

But here comes another question: all the sensitive cookies are protected by the HttpOnly flag, which makes us unable to access the cookies by JavaScript. WHAT SHOULD WE DO?

## [Bypass the HttpOnly](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/\#Bypass-the-HttpOnly "Bypass the HttpOnly") Bypass the HttpOnly

As we could execute arbitrary JavaScript on browsers, why don’t we just insert the SSRF cookie we used in ProxyLogon? Once we add this cookie and assign the Backend target value as our malicious server, Exchange will become a proxy between the victims and us. We can then take over all the client’s HTTP static resources and get the protected HttpOnly cookies!

![](https://blog.orange.tw/posts/2021-08-proxyoracle-a-new-attack-surface-on-ms-exchange-part-2/a3bcbfc2df83c04e-07.png)

By chaining bugs together, we have an elegant exploit that can steal any user’s cookies by just sending him/her a malicious link. What’s noteworthy is that the XSS here is only helping us to steal the cookie, which means all the decryption processes wouldn’t require any authentication and user interaction. Even if the user closes the browser, it wouldn’t affect our Padding Oracle Attack!

Here is the [demonstration video](https://www.youtube.com/watch?v=VuJvmJZxogc) showing how we recover the victim’s password:

ProxyOracle - A New Attack Surface on Microsoft Exchange Server! - YouTube

Tap to unmute

[ProxyOracle - A New Attack Surface on Microsoft Exchange Server!](https://www.youtube.com/watch?v=VuJvmJZxogc) [Orange Tsai](https://www.youtube.com/channel/UCnweRFxfA-xpTbkb83yfBog)

Orange Tsai3.75K subscribers

[Watch on](https://www.youtube.com/watch?v=VuJvmJZxogc)