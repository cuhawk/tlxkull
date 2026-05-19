---
source: spaceraccoon
source_url: https://spaceraccoon.dev/low-hanging-apples-hunting-credentials-and-secrets-in-ios-apps/
title: "Low-Hanging Apples: Hunting Credentials and Secrets in iOS Apps | Spaceraccoon's Blog"
published: 2019-12-29T14:58:40+00:00
description: "Diving straight into reverse-engineering iOS apps can be daunting and time-consuming. While wading into the binary can pay off greatly in the long run, it’s also useful to start off with the easy wins, especially when you have limited time and resources. One such easy win is hunting login credentials and API keys in iOS applications."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Low-Hanging Apples: Hunting Credentials and Secrets in iOS Apps

Dec 29, 2019
·

1247 words

·

6 minute read


# Motivation [🔗](https://spaceraccoon.dev/low-hanging-apples-hunting-credentials-and-secrets-in-ios-apps/\#motivation)

Diving straight into reverse-engineering iOS apps can be daunting and time-consuming. While wading into the binary can pay off greatly in the long run, it’s also useful to start off with the easy wins, especially when you have limited time and resources. One such easy win is hunting login credentials and API keys in iOS applications.

Most iOS applications use third-party APIs and SDKs such as Twitter, Amazon Web Services, and so on. Interacting with these APIs require API keys which are used (and thus stored) in the app itself. A careless developer could easily leak keys with too many privileges or keys that were never meant to be stored on the client-side in the first place.

What makes finding them an easy win? As described by [top iOS developer Mattt Thompson](https://nshipster.com/secrets/):

> There’s no way to secure secrets stored on the client. Once someone can run your software on their own device, it’s game over.
>
> And maintaining a secure, closed communications channel between client and server incurs an immense amount of operational complexity — assuming it’s possible in the first place.

He also tells us that:

> Another paper published in 2018 found SDK credential misuse in 68 out of a sample of 100 popular iOS apps. (Wen, Li, Zhang, & Gu, 2018)

Until APIs and developers come round to the fact that client secrets are insecure by design, there will always be these low-hanging vulnerabilities in iOS apps.

# Techniques [🔗](https://spaceraccoon.dev/low-hanging-apples-hunting-credentials-and-secrets-in-ios-apps/\#techniques)

Mattt Thompson shared three ways developers can (insecurely) store client secrets in their apps:

1. Hard-code secrets in source code
2. Store secrets in `Info.plist`
3. Obfuscate secrets using code generation

For the first two methods, we can simply expose these secrets using static analysis and grepping through the decrypted app files as covered by [Ivan Rodriguez](https://github.com/ivRodriguezCA/RE-iOS-Apps/blob/master/Module-3/README.md). For obfuscated secrets, we can short-circuit the obfuscation and save ourselves hours of reverse-engineering through the magic of Frida’s dynamic analysis. This was how I extracted AWS client and secret keys for a bug bounty program.

The following walkthrough assume that you have set up your iOS testing environment according to my [iOS app pentesting quickstart post](https://spaceraccoon.dev/from-checkra1n-to-frida-ios-app-pentesting-quickstart-on-ios-13).

## Static Analysis [🔗](https://spaceraccoon.dev/low-hanging-apples-hunting-credentials-and-secrets-in-ios-apps/\#static-analysis)

Static analysis begins with extracting your target `.ipa` file. Make sure that you have installed `iproxy` and [frida-ios-dump](https://github.com/AloneMonkey/frida-ios-dump.git).

1. In one terminal, run `iproxy 2222 22`
2. Open the target app on your iDevice
3. In another terminal, run `./dump.py <APP DISPLAY NAME OR BUNDLE IDENTIFIER>`
4. You should now have a `<APPNAME>.ipa` file in your current directory
5. `mv <APPNAME>.ipa <APPNAME>.zip`
6. `unzip <APPNAME>.zip`
7. The files are now unzipped to a `Payload` folder; open it up and check that an `<APPNAME>.app` file has been created (`<APPNAME>` might differ between the `.ipa` and `.app` files)
8. `mkdir AppFiles`
9. `mv Payload/<APPNAME>.app/* AppFiles/`

At this point, you should see a bunch of files in the `AppFiles` directory. While the files obviously differ from app to app, here are a few keys files to look into.

`Info.plist` and other `*.plist` files: `Info.plist` functions similarly to `manifest.json` for Android apps. It contains app metadata and can point out weaknesses or new attack surfaces such as custom scheme URLs. Of course, it can also contain stored credentials. You can use macOS’ built-in `plutil` command to lay out the data nicely in JSON with `plutil -p Info.plist`.

Some `plist` files can be stored in binary rather than XML, which makes it harder to parse directly. Run `plutil -convert xml1 Info.plist` to convert them back to XML.

Quick tip: while `GoogleService-Info.plist` exists on many apps and includes an extremely juicy-looking `API_KEY` value, [this is not a sensitive credential](https://stackoverflow.com/questions/37482366/is-it-safe-to-expose-firebase-apikey-to-the-public). It needs to be paired with a custom token to have any impact. Not all API keys are created equal; some have proper access controls and can be exposed without risk. Check out [keyhacks](https://github.com/streaak/keyhacks) to quickly identify and validate sensitive API keys.

You also want to begin grepping and parsing through the various files; `grep "API_KEY" -r *` or similar is a quick and dirty solution.

At this point, you should also poke at interesting files that hint at vulnerable functionality. Check `html` files (maybe an internal URL scheme vulnerable to DOM XSS?), templates, and third-party frameworks that could have known vulnerabilities.

With luck, you might walk away with a straightforward credential exposure.

## Dynamic Analysis [🔗](https://spaceraccoon.dev/low-hanging-apples-hunting-credentials-and-secrets-in-ios-apps/\#dynamic-analysis)

Most times, it won’t be that straightforward. Nevertheless, there are clues that might point you towards obfuscated credentials.

In one bug bounty program, I noticed that the app I was testing uploaded profile pictures to an S3 bucket, but the request was hidden from interception and the credentials were not stored in plaintext in the app files. Nevertheless, given that the upload was occurring, it was a safe bet to assume that credentials were being exchanged.

At this point, I could dive into the binary with Ghidra and attempt to walk through the obfuscated code to decrypt the credentials, but there is a way to short-circuit this whole process.

Think of it this way: at the end of the day, no matter how much obfuscation is used, the credentials need to be sent in plaintext (for insecure implementations) to the server. For that to happen, a method needs to be invoked somewhere in the code using these credentials.

This is where Frida and Objection comes in. You want to hook onto the method that makes that call, and dump the arguments to that method - which should hopefully be the credentials you are looking for.

First, you need to identify the method. Fire up Objection with `objection --gadget <APPNAME> explore`. Next, run `ios hooking list classes` to dump all available classes in the app. This is a huge list. Grep through the list and identify interesting classes. For example, I looked for the classes with `AWS` or `Amazon` in the name. As luck would have it, there was an `AWSCredentials` class, among other interesting class names.

![Objection console](https://spaceraccoon.dev/images/2/objection-console.png)

Next, you want to begin watching these classes. Run `ios hooking watch class <CLASSNAME>` in the Objection console for each class. Now, perform the action in the app where the potentially vulnerable credentials could be exposed. In this case, I performed the profile picture upload function in the app, which triggered the following response:

```console
(agent) Watching method: - initKey:
(agent) Watching method: - initSDK:
(agent) Registering job gk6i5disc88. Type: watch-class-methods for: AWSCredentials
myApp on (iPhone: 13.1.2) [usb] # (agent) [gk6i5disc88] Called: [AWSS3Client initKey:] (Kind: instance) (Super: AWSClient)
```

Awesome. So it looks like Frida successfully hooked onto the `AWSCredentials` class which includes the `initKey` and `initSDK` methods. When I performed the profile picture upload, the `initKey` method was called.

Now, we want to dump the arguments passed into the `initKey` class method. In objection, run `ios hooking watch method "-[AWSCredentials initKey:]" --dump-args`. Note that the format here for the class method is `"-[<CLASSNAME> <METHOD>:]"`. Once again, I performed the profile picture upload in the app.

```console
(agent) [gk6i5disc88] Called: -[AWSCredentials initKey:] 1 argument(Kind: instance) (Super: NSObject)
(agent) [gk6i5disc88] Argument dump: [AWSCredentials initKey: <AWS CLIENT KEY>:<AWS SECRET KEY>]
```

Success! Using dynamic analysis, I exposed the AWS keys used by the application. Of course, this meant that the app was using an insecure communication protocol with S3 as there are credential-less ways of implementing S3 uploads.

# Conclusion [🔗](https://spaceraccoon.dev/low-hanging-apples-hunting-credentials-and-secrets-in-ios-apps/\#conclusion)

Hunting for secrets in iOS apps is a low-effort, high-payoff task that can help ease you into pentesting an application. (Un)fortunately, secrets management remains a hard problem especially for less-experienced developers, and continues to crop up as a recurring vulnerability. It’s easy to forget that credentials are still exposed even when compiled into an app binary.

[ios](https://spaceraccoon.dev/tags/ios)