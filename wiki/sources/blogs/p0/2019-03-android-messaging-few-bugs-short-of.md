---
source: p0
source_url: https://projectzero.google/2019/03/android-messaging-few-bugs-short-of.html
title: "Android Messaging: A Few Bugs Short of a Chain - Project Zero"
description: "Posted by Natalie Silvanovich, Project ZeroAbout a year and a half ago, I did some research into ..."
---

Posted by Natalie Silvanovich, Project Zero

About a year and a half ago, I did some research into Android messaging and mail clients. At the time, I didn’t blog about it, because though I found bugs, I wasn’t able to assemble them into a credible attack. However, in the spirit of writing about [research](https://projectzero.google/2018/12/adventures-in-video-conferencing-part-4.html) that didn’t go as expected, I have decided to share it now. I think there is something interesting to learn about the impact of design choices on security from this research.

Applications Reviewed

I reviewed the following applications: Messages (the default Android SMS application), Gmail for Android, Microsoft Outlook, Facebook Messenger, WhatsApp, Signal and Telegram, which represent some of the most popular messaging and mail apps on Google Play.

Architecture, Attack Surface and Test Set-up

At a high level, messaging clients have a similar architecture. They communicate with a server that is responsible for locating the recipient that a user wants to communicate with and generally maintains the messaging session. Messages are also transmitted through the server, and clients that support end-to-end encryption can include some sort of encrypted envelope in these messages, that are passed directly to the recipient.

Though their protocols differ substantially, Facebook Messenger, WhatsApp and Telegram all use a layered approach, where messages can contain fields of different types with a hierarchy.  Telegram’s protocol is [documented](https://core.telegram.org/schema) publicly. A single message can include pieces for both the server and the receiving client.

I started by looking at how unencrypted messages were handled by Facebook messenger, but this turned out to be a challenging attack surface. There were many protocols that could be used to send messages (such as mobile and web APIs), but then they were processed substantially before the message was received by the target device. This made it difficult to know whether any attack surface in the client was reachable. Therefore, I decided to focus on encrypted messages, as the server is not able to filter those.

I did not have the source for Facebook Messenger or WhatsApp, so I was only able to analyze the smali extracted from the APKs for these applications with [apktool](https://ibotpeaches.github.io/Apktool/). The popularity of signal protocol simplified finding the encryption portion of these applications, as I was able to search for strings in libsignal. I then added a function that sent each message to a server I control and gave me the option to alter it before encrypting it. This gave me the ability to test malformed encrypted  messages.

Testing the mail and SMS clients were easier. For the Messaging app, I sent raw SMS messages using the [sendDataMessage](https://developer.android.com/reference/android/telephony/SmsManager.html#sendDataMessage(java.lang.String,%20java.lang.String,%20short,%20byte[],%20android.app.PendingIntent,%20android.app.PendingIntent)) API from an app I wrote for an Android device. For the mail clients, I sent MIME messages directly using an SMTP server.

Results Overview

Please note that these results are over a year old, and messaging clients have high code churn, so the clients may be different now. All the vulnerabilities discussed in this section have been fixed.

### Messages

The default Android Messages app is largely written in Java, and uses the AOSP SMS and MMS processing to parse messages. It has a fairly low risk of memory corruption vulnerabilities due to this. Android processes some special SMS messages differently, which increases the risk of receiving these messages. Some messages are interpreted as [OMTP](http://www.omtp.org/OMTP_VVM_Specification_v1_3_Final.pdf) for Visual Voicemail messages, but the processing of these messages, as well as the IMAP functionality used by Visual Voicemail are implemented in Java and contain the minimum necessary functionality. Android once supported SUPL (an SMS protocol for GPS ephemeris updates) parsing in the user space as well, and the intent handlers for it are still in the SMS stack. However, Qualcomm’s baseband handles these messages directly now, so they will not make it to the user space on newer devices. The main risk of vulnerabilities in the Messages app is the libraries used to process incoming media files. Many vulnerabilities have been discovered in these components in the past, though fewer have been reported recently, and media is processed by a low-privileged process. I did not find any vulnerabilities in Messages.

### Gmail

The Gmail app processes MIME messages provided by an IMAP, POP or other server. The contents of the MIME message usually comes directly from another user, though mail servers sometimes do some filtering. Gmail uses some underlying mail APIs in AOSP, and both the application and the underlying APIs are implemented entirely in Java. I reported one directory traversal [issue](https://bugs.chromium.org/p/project-zero/issues/detail?id=1342) in Gmail due to attachment downloads.

### Outlook

The Microsoft Outlook app is similar to the Gmail app in functionality. It also processes MIME provided by another server, however all of its protocol processing is done by code within the app. The application is written mostly in Java, and the existing native functionality is used for metrics and other features not related to mail. I reported a directory traversal [issue](https://bugs.chromium.org/p/project-zero/issues/detail?id=1356) similar to the one in Gmail in Outlook.

### Facebook Messenger

Facebook Messenger is a large application compared to the other messaging applications I reviewed, and it was difficult to determine the functionality of a lot of the code. It contains a large number of native libraries, which are updated dynamically from the Facebook server on a nearly daily basis. Few of them seemed to be directly involved processing messages, though.

Facebook messenger communicates with the server using a protocol called Messaging Queue Telemetry Transport ( [MQTT](http://mqtt.org/)). Underneath the MQTT is the thrift protocol, which is open [source](https://github.com/facebook/fbthrift/tree/master/thrift/lib/java/thrift/src/main/java/com/facebook/thrift/protocol). The application contains both the Java and C++ version of the library, but only the Java one appears to be used. I reviewed these protocols, but did not find any vulnerabilities affecting Facebook Messenger.

### WhatsApp

WhatsApp uses a layered protocol that is mostly implemented in Java. A small amount of message handling code used to process voice and video call requests is implemented in native code, which I discussed in this [post](https://projectzero.google/2018/12/adventures-in-video-conferencing-part-4.html). I did not find any vulnerabilities in WhatsApp messaging

### Telegram

Telegram is [open source](https://github.com/DrKLO/Telegram) and its APIs are publicly documented. It contains a fair amount of native code, but the code is mostly used to process device-to-server messages, as opposed to device-to-device messages. The attack surface available to a remote attacker is almost entirely in Java. I found one [vulnerability](https://bugs.chromium.org/p/project-zero/issues/detail?id=1470) in Telegram, which was also a directory traversal vulnerability related to attachments.

### Signal

Signal is largely implemented in Java, and has a fairly small attack surface. Its protocols are well documented. I did not find any vulnerabilities in Signal.

Do These Bugs Matter?

Overall, I found three directory traversal vulnerabilities in these clients. They were surprisingly similar, all related to attachment names being allowed to contain special characters when they are downloaded. Directory traversal issues are fairly common in Android applications, likely in part due to how forgiving Java APIs are with regards to file names.

These bugs had some limitations though. To start, the bugs in the Gmail and Outlook mail clients only work when the client is being used with non-standard email addresses (i.e. Gmail is being used with a non-Gmail account or Outlook is being used with a non-Outlook email address). Both of these clients are widely used for this purpose, but this does mean these bugs will not impact every user. The bugs also require the user to download an attachment.

But there are also some limitations that affect exploitability. To start, none of these issues can overwrite a file that exists, they can only write a new file. So there needs to be somewhere an attacker can place a file that is processed by the system, but does not already exist. Secondly, applications on Android have limited permissions, and typically cannot write outside of their application directory.

The Telegram issue probably is exploitable, as there happened to be a configuration file that did not exist by default, but Telegram would process it if it existed, and the processing code had a memory corruption vulnerability in it. I couldn’t find anything like this for the mail clients, though.

One idea I had was to look for a vulnerability in SQLite, as Gmail and Outlook use SQLite databases to store a variety of data. SQLite supports journaling, which means that when a SQLite database is changed, a journal file is written first, so that if the system crashes or loses power during the write, the database is not corrupted. If this occurs, the journal file will exist the next time the database is accessed, and SQLite knows to restore it. Otherwise, the journal file will be deleted when the write is completed successfully. This means that a SQLite database can be altered by writing a journal file with a specific name in the same directory, and this file does not generally already exist.

I tried this, and was able to alter databases, but none of them seemed to allow me to escalate privileges or perform unpermitted operations other than altering what mail a user sees in the app. Looking for something more generic, I considered the possibility of finding a bug in how SQLite parses journal files or database files.

I fuzzed both database loading and journal handling using AFL. [I](https://sqlite.org/src/info/04925dee41a21ffc) [found](https://sqlite.org/src/info/02828d717e2d97b1) [four](https://sqlite.org/src/info/cf5bf42cad6e019a) [bugs](https://sqlite.org/src/info/378afa16381a222a), three of which I think are unexploitable, and one which is very borderline in terms of exploitability.

I could not find any more ways to exploit a directory traversal that cannot overwrite a file in an Android application, so I’m not convinced that these directory traversal attacks would be especially valuable to attackers.

Conclusion

I reviewed several Android messaging and mail applications. I found three directory traversal bugs, but these bugs had some limitations, and it is not clear if this type of bug is exploitable in the generic case.

These bugs were very similar, and point to challenges in correctly handling file paths in Android Java. The two bugs in the mail clients only occurred when the application was used with an email address which is not managed by the maker of the application, despite it being a common use case,  which suggests this could be an under-tested or under-reviewed feature of mail clients. For the most part, these clients were implemented in Java, which made it more difficult to find bugs in them, as memory corruption attacks were not available.

This research focused on the portions of mail and messages that are not processed by an intermediary server, and therefore allow an attacker to send any data to be processed without filtering. While the easiest to attack, these features are only a part of the attack surface of a messaging or mail client. I will likely investigate the server-mediated features of messaging clients in the future.