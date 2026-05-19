---
source: bughunters
source_url: https://bughunters.google.com/blog/certificate-error-mishandling-misuse-and-abuse-of-the-sslerrorhandler-class
title: "Certificate Error Mishandling: Misuse and Abuse of the SslErrorHandler Class - Google Bug Hunters"
description: "This blog post looks at a few examples of how the `SslErrorHandler` class has been (mis)used, and then highlights how the class is actually meant to be implemented."
---

[Skip to Content (Press Enter)](https://bughunters.google.com/blog/certificate-error-mishandling-misuse-and-abuse-of-the-sslerrorhandler-class#main-content)

[**Google Bug Hunters**](https://bughunters.google.com/)

1blog enterBlog

# Certificate Error Mishandling: Misuse and Abuse of the SslErrorHandler Class

![](https://storage.googleapis.com/bughunters-article-images/blogs/julianyates.jpg)

Julian Yates

Security Analyst - NCC Group (on assignment at Google at time of publishing)

![](https://storage.googleapis.com/bughunters-article-images/blogs/torne.jpg)

Richard (Torne) Coles

Software Engineer

Published: Oct 28, 2024

Security Engineering  Android  Vulnerability Research

[RSS Feed](https://bughunters.google.com/feed/en)

# Certificate Error Mishandling: Misuse and Abuse of the SslErrorHandler Class

This post is about what happens when developers want to do the right thing, but
use the wrong approach to achieve their goal. It’s fair to say that developers
want their applications to be safe to use by their users while sometimes making
choices that align with the pressures of just getting the app to work. We will
look at a few examples of how the `SslErrorHandler` class has been used, and
then highlight how the class is actually meant to be implemented.

## What is the SslErrorHandler class?

Before getting into the issues of misuse of this class, let’s take a closer look
and see what it was created to do, and what a good implementation of the class
would look like. For the sake of clarity, although the name refers to SSL, an
old protocol that has been thoroughly deprecated and replaced by TLS, the API
works in the same way. Throughout this article the term SSL is used because of
the class’ name but we are talking about TLS functionality.

`SslErrorHandler` is a class within `android.webkit` that provides tools for
apps to add web browsing capabilities. When applications loading web content
encounter an SSL error, this class can be used to handle it, as the name
suggests. The instance of `SslErrorHandler` that is created within the WebView
is passed to `onReceivedSslError`, which will then notify the application that
an SSL error has occurred. This notification is presented along with a choice to
either proceed past the error, or cancel, ending all communication between the
WebView and the server. The default implementation of `onReceivedSslError`
always calls `cancel`, to ensure it does not proceed.

## Common Misuses of SslErrorHandler

Based on the many vulnerability reviews we've performed on applications over the
years, we have identified three recurring patterns of misuse of
`SslErrorHandler` in the wild:

1. Prompting the user to decide whether or not to proceed past SSL errors.
2. Custom SSL certificate validation without user input.
3. Lazy workaround to SSL certificate problems so the application works.

### Prompting for a user decision about SSL errors

WebViews are quite safe if the application is showing web content that the
developers control, either sites they own or have a business relationship with.
In this case the developers have the most control over the SSL certificates, and
there should be no reason to burden the user with the decision about whether or
not it is safe to continue.

If an app is allowed to load arbitrary, third-party web content, developers
cannot ensure there aren't any SSL errors. This puts developers in a position
where they can refuse to load content from sites with SSL errors, which could
lead to user complaints about the application failing to load content. The
workaround to this would be to present the user with the error notification and
prompt for a decision to proceed or not. Since users are not necessarily
equipped to make an informed decision about the safety of proceeding past the
error and the class doesn’t provide enough information about the error for a
good decision to be made anyway, this is an unsafe practice that could lead to
problems for the user.

When it was originally implemented in pre-Chrome Android browsers, the
`SslErrorHandler` class was intended to handle SSL errors by prompting the user
with a choice about how to continue. When ported to the WebView API, no
distinction was made between what was intended for use to embed web content in
your app and what was intended for use in creating a browser. Consequently, the
API is ill-equipped to provide the kind of UI that would be found in a full
browser in order to handle alerting users about errors in a meaningful way.

Although it is not recent, the following is an example of an **unsafe**
implementation of this use case, which can still be found on the internet.
Similar implementations have been found in applications.

```
    public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
            AlertDialog.Builder builder = new AlertDialog.Builder(ctx);
            AlertDialog alertDialog = builder.create();
            String message;
            switch (error.getPrimaryError()) {
            //Just looking at getPrimaryError doesn't present enough information since
            //there may be more errors than just the primary
                case SslError.SSL_UNTRUSTED:
                    message = "The certificate authority is not trusted.";
                    break;
                case SslError.SSL_EXPIRED:
                    message = "The certificate has expired.";
                    break;
                case SslError.SSL_IDMISMATCH:
                    message = "The certificate Hostname mismatch.";
                    break;
                case SslError.SSL_NOTYETVALID:
                    message = "The certificate is not yet valid.";
                    break;
                case SslError.SSL_DATE_INVALID:
                    message = "The date of the certificate is invalid.";
                    break;
            //The set of error codes was defined a long time ago, and there are
            //no codes for specific, modern security developments such as
            //Certificate Transparency, deprecation of outdated protocols and
            //hash/key types, for example, which end up reported as SSL_INVALID.
            //Further, these do not tell the user anything about what the
            //presented choice is for, whether it's an ad, an image, or some
            //other subresource, that a full browser wouldn't prompt the user about.
                default:
                    message = "A generic error occurred.";
                    break;

            }
            message += " Do you want to continue anyway?";
            alertDialog.setTitle("SSL Certificate Error");
            alertDialog.setMessage(message);
            alertDialog.setButton(DialogInterface.BUTTON_POSITIVE, "OK", (dialog, which) -> handler.proceed());
            alertDialog.setButton(DialogInterface.BUTTON_NEGATIVE, "Cancel", (dialog, which) -> handler.cancel());
            //Since modern browser UX design leads users to cancel anything
            //security related, or obscures or even hides from the user the
            //ability to proceed past the error, the standard Android alert makes it
            //easy for users to just hit "ok" without reading what it's for.
            alertDialog.show();
        }
```

### Creating a custom SSL certificate validator

This is a use case that is not as common but still arises since it seems a
reasonable way to use the class, considering that it is now implemented in a
WebView within an app rather than a browser where it would be necessary to have
a trusted CA certificate. The documentation for the class clearly outlines the
usage as follows: invoke `proceed()` when the certificate meets expectations,
and `cancel()`if it does not.

Consider the following **unsafe** code example:

```
// the developer's own public key, hardcoded into the app
private static final PublicKey MY_TRUSTED_KEY = /* whatever */;

public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
    // get the actual certificate object that has methods to see the detailed info
       X509Certificate cert = error.getCertificate().getX509Certificate();

// use some particular security provider implementation (retrieved.. from
// somewhere) to see if the cert is properly signed by the given key
    if (cert.verify(MY_TRUSTED_KEY, securityProvider)) {
    // this cert is signed by the developer's own trustworthy key, hooray

        // THIS IS NOT AN EXAMPLE OF GOOD PRACTICE
        // THIS MAY LOOK REASONABLE BUT IT IS NOT SAFE
        // SEE DISCUSSION BELOW
        handler.proceed();
        return;
    }

    // otherwise assume it's bad
    handler.cancel();
}
```

The above seems like a reasonable implementation which has all the right parts,
such as checking the certificate, using key verification with a trusted key
hardcoded in the binary, and calls to `cancel` and `proceed` that are correct
according to the documentation. However, what makes this implementation **not**
**safe** has nothing to do with correctly following the documentation. The class
is just not built to handle this use case. Any error that is encountered isn't
actually identified, and even if `getPrimaryError` was used to identify the
error, there may have been more than one. Using `getPrimaryError` only returns
whatever is identified as the most important problem, and there is no
consideration for complexity – where multiple errors may occur. More broadly,
the error checks in this class are too generic to communicate anything detailed
enough for this specific scenario. In the end this use case would require
implementing the entire certificate verification process.

A safer option would be to simply implement a standard certificate signed by a
trusted Certificate Authority (CA). Or, in the case where a custom certificate
is desired, the best practice would be to configure a custom CA in the
application’s `network_security_config.xml`. This way, when certificate handling
errors occur further problems can be avoided, since the certificate has already
been accepted. The following example is pulled from official
[documentation](https://developer.android.com/privacy-and-security/security-config#CustomTrust)
for configuring a custom CA:

```
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="true">example.com</domain>
        <trust-anchors>
            <certificates src="@raw/my_ca"/>
        </trust-anchors>
    </domain-config>
</network-security-config>
```

### Just getting the application to work

While doing vulnerability assessments of applications, this use case,
unfortunately, is the most prevalent. Developers seem to encounter some kind of
SSL issue during development and add some code to ignore the error and proceed
anyway.

Below is a simple, but accurate example of a **bad implementation** that can be
found in the wild:

```
public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
    // my boss told me that his last startup went out of business because they
    // forgot to renew their server's certificate in time and it expired on the
    // same day that they had their big public launch and everyone made fun of them
    // on the internet, so we have to be EXTRA CAREFUL!!!

    // only do this for our own website, we don't want to accidentally ignore
    // errors on some ad!
    if (Uri.parse(error.getUrl()).getHost().equals("www.example.com")) {
    // only do this if the certificate has expired, we don't want to
    // accidentally ignore serious problems!
if (error.getPrimaryError() == SslError.SSL_EXPIRED) {
    // Report this to our analytics backend so that we get paged!
    Analytics.silentReport("OMG our cert has expired everyone panic");
    // proceed past the error so users aren't impacted
    handler.proceed();
    return;
}
    }

    // otherwise just fail
    handler.cancel();
}
```

This is only ever going to trigger if `getPrimaryError` shows that the
certificate has expired, and will just proceed past it anyway. There seems to be
little use to this code aside from creating something that looks like it is
handling errors, which it does, in a way, but badly.

## How to proceed?

The existing documentation underscores that either `cancel()` or `proceed()`
must be called and that `cancel()` is called by default. Further, it states that
`cancel()` should always be called when SSL errors arise, that users should not
be prompted about them, and finally to never proceed past them. This article was
born out of the observation that the documentation is not always followed, and
this class is used in ways that it should not be. We want to reiterate that the
only real advice we can give for use cases like the above is “ **DON’T**”.

The big takeaway that we hope is evident from this post is that this class
should be used cautiously, perhaps, at most, for simply logging SSL errors
somewhere. If you are a developer and are considering using this class for any
of the problematic implementations we discussed above, please don't.

[Back to overview](https://bughunters.google.com/blog)

Sign In - Google Accounts

Sign inSign in with Google. Opens in new tab