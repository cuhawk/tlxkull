---
source: oversecured
source_url: https://oversecured.com/blog/android-security-checklist-theft-of-arbitrary-files
title: "Android security checklist: theft of arbitrary files | Oversecured Blog"
author: "HubSpot, Inc."
description: "Developers for Android do a lot of work with files and exchange them with other apps, for example, to get photos, images, or user data."
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

Developers for Android do a lot of work with files and exchange them with other apps, for example, to get photos, images, or user data. Developers often make typical mistakes that allow an attacker to gain access to the app’s internal files, which store sensitive data. This article describes the most typical mistakes developers make and gives the best advice on how to fix them. We will also show how Oversecured can discover all these types of errors.

Do you want to check your mobile apps for these types of vulnerabilities? Oversecured’s mobile app scanner provides an automatic solution that helps to detect vulnerabilities in Android and iOS mobile apps. You can integrate Oversecured into your development process and check every new line of your code to ensure your users are always protected.

Start securing your apps by starting a free 2-week trial from [Quick Start](https://app.oversecured.com/docs/quick-start/), or you can [book a call](https://calendly.com/oversecured/30min) with our team or [contact us](https://app.oversecured.com/contact-us) to explore further.

We also give all new users two free scans, so they can check any apps for vulnerabilities! You can do this on the [New Scan](https://app.oversecured.com/scan/create) page.

## Types of files

It’s well known that from the point of view of an Android app, there are two basic types of file storage: public and private.

**Private** is located at the file path `/data/user/0/{package_name}`, where `0` is the ID of the Android user. Only the app itself and system users like `root` have access to it. Android’s security model allows you to store secret information like tokens and user data there. **Public** is located at `/storage/emulated/0` (or just `/sdcard`). A specific app’s public data is stored at `/storage/emulated/0/Android/data/{package_name}`. New versions of Android (SDK 29 and up) do introduce restrictions on access to certain directories, but, all the same, every file that is stored here should still be regarded as public. They can be read by any third-party app installed on the same device.

Apps having the same `android:sharedUserId` have access to one another’s files. So an attacker can also exploit one app by way of another.

This means that when we are talking about the theft of arbitrary files on Android, what we usually mean is the ability to steal any files from an app’s private directories.

A large number of file theft attacks rely on app functionality where the attacker can copy private files into public directories and then read them.

## Implicit intents

We discuss types of intents, and interception of implicit intents in particular, in a separate [article](https://blog.oversecured.com/Interception-of-Android-implicit-intents/). This section looks at widespread problems when working with standard actions such as

- `"android.intent.action.GET_CONTENT"`

- `"android.media.action.IMAGE_CAPTURE"`

- `"android.media.action.VIDEO_CAPTURE"`

- `"android.intent.action.PICK"`

- `"com.android.camera.action.CROP"`

- and many others.


The idea of these intents is that the app tells the system, “I don’t know or care which file manager, photography app, or media file editor the user may have installed, but get one of them to do the job I need and give me a link to the resulting file”. And apps launch implicit intents to obtain content very frequently. An example might be choosing a file to attach to a message in a chat or an avatar for a user profile.

On Android, all these actions have a unified API:

1. The app we are analyzing launches an implicit intent `startActivityForResult(new Intent("android.intent.action.PICK"), ANY_REQUEST_CODE)`

2. The handling or attacking app performs the action and puts a `Uri` in the data value `setResult(-1, new Intent().setData(contentUri))`

3. The app we are analyzing receives the result in `onActivityResult(requestCode, responseCode, resultIntent)`and usually caches the content from this `contentUri` somewhere in its local file system.


In reality, the code of the vulnerable app might look something like this:

private static final int PICK\_CODE = 1337;

protected voidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

startActivityForResult(newIntent(Intent.ACTION\_PICK),PICK\_CODE);

}

protected voidonActivityResult(int requestCode,int resultCode,Intent data){

super.onActivityResult(requestCode,resultCode,data);

if(resultCode != Activity.RESULT\_OK){

// Handle error

return;

}

switch(requestCode){

casePICK\_CODE:{

Uri pickedUri = data.getData();

processPickedUri(pickedUri);

return;

}

// Handle other cases

}

}

private voidprocessPickedUri(Uri uri){

File cacheFile = newFile(getExternalCacheDir(),"temp");

copy(uri,cacheFile);

// Do normal stuff

}

private voidcopy(Uri uri,File toFile){

try(InputStream inputStream = getContentResolver().openInputStream(uri)){// openInputStream() handles both file, and content schemes

try(OutputStream outputStream = newFileOutputStream(toFile)){

byte\[\]bytes = new byte\[65536\];

while(true){

int read = inputStream.read(bytes);

if(read == -1){

break;

}

outputStream.write(bytes,0,read);

}

}

}catch(IOException e){

// Handle error

}

}

An example of a similar vulnerability is provided in the [Oversecured Vulnerable Android App](https://github.com/oversecured/ovaa). The Oversecured Android vulnerability scanner discovers vulnerabilities of this type:

![](https://framerusercontent.com/images/eeGsysNmelROtSLIp4Fbx5iiciE.png?width=2254&height=3908)

As you see from the screenshot of the scan report, all lines of code responsible for the vulnerability are highlighted:

1. Launching an implicit intent

2. Receiving a result in `onActivityResult()`, where the URI could be controlled by an attacker

3. Copying data to public storage where it’s accessible to an attacker


## Exploiting URI attacks via `file`scheme

The most obvious technique is to return a `file://` URI with an absolute path to the file. Example attacking app:

File `AndroidManifest.xml`:

<activityandroid:name=".PickerActivity"android:enabled="true"android:exported="true">

<intent-filterandroid:priority="999">

<actionandroid:name="android.intent.action.PICK"/>

<categoryandroid:name="android.intent.category.DEFAULT"/>

<dataandroid:mimeType="image/\*"/>

<dataandroid:mimeType="\*/\*"/>

</intent-filter>

</activity>

File `PickerActivity.java`:

public class PickerActivity extendsActivity{

protectedvoidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

StrictMode.setVmPolicy(StrictMode.VmPolicy.LAX);

Uri uri = Uri.parse("file:///data/user/0/com.victim/shared\_prefs/secrets.xml");

setResult(-1,newIntent().setData(uri));

finish();

}

}

By default, an app throws a `FileUriExposedException` if a `file`scheme is used and the `targetSdkVersion` is 18 or higher, which could make an attack much more difficult; but these (local) checks can be circumvented by pre-setting a configuration:

StrictMode.setVmPolicy(StrictMode.VmPolicy.LAX);

> Remediation: Oversecured recommends that you avoid using public file storage, not only for caching files but also for any other operation.

## Exploiting URI attacks via `content` scheme

Another promising avenue for exploitation is to use a `content`scheme and the vulnerable app’s local content providers. It’s important to note that **they do not necessarily need to be exported**. Android only checks rights when an attempt is made to access data, but the vulnerable app will be receiving access to one of its resources, and no restrictions will come into play.

The first step is to check all [FileProviders](https://developer.android.com/reference/androidx/core/content/FileProvider) for access to `root-path` or shared private storage directories (such as `files-path` or `cache-path`). Non-exported providers should then be checked. Oversecured has found examples of these vulnerabilities in [Google](https://blog.oversecured.com/Why-dynamic-code-loading-could-be-dangerous-for-your-apps-a-Google-example/), [TikTok](https://blog.oversecured.com/Oversecured-detects-dangerous-vulnerabilities-in-the-TikTok-Android-app/), and many others apps. According to internal stats, more than 90% of the apps we analyze contain errors of varying criticality levels relating to the implementation of providers.

### Remediation

Each FileProvider should be properly protected: an ideal solution would be to use separate folders for each operation. For example, we regard `<files-path name="files" path="." />` as unsafe: you should use `<files-path name="files" path="my_saved_files" />` instead. This will help significantly reduce the impact of a potential attack.

- All other providers should be checked to make sure they do not contain path-traversal errors or share “broad” folders like `files`or `cache`. For example, the most widespread kind of attack is to use `Uri.getLastPathSegments()` when constructing a file path, because this call (and many others!) automatically decodes the segment and turns `%2F` into `/`.

- In addition, you should check external URIs (from a `file` or `content` scheme) to make sure they do not point to local files:


private static final int PICK\_CODE = 1337;

protected voidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

startActivityForResult(newIntent(Intent.ACTION\_PICK),PICK\_CODE);

}

protected voidonActivityResult(int requestCode,int resultCode,Intent data){

super.onActivityResult(requestCode,resultCode,data);

if(resultCode != Activity.RESULT\_OK){

// Handle error

return;

}

switch(requestCode){

casePICK\_CODE:{

Uri pickedUri = data.getData();

processPickedUri(pickedUri);

return;

}

//...

}

}

private voidprocessPickedUri(Uri uri){

try{

if(isInternalUri(this,uri)){

// Attack prevented

return;

}

}catch(IOException e){

// Handle error

return;

}

// Do normal stuff

}

private static boolean isInternalUri(Context context,Uri uri)throws IOException {

ParcelFileDescriptor fd = context.getContentResolver().openFileDescriptor(uri,"r");

returnisInternalFile(context,fd);

}

private static boolean isInternalFile(Context context,ParcelFileDescriptor fileDescriptor)throws IOException {

int fd = fileDescriptor.getFd();

Path fdPath = Paths.get("/proc/self/fd/" \+ fd);

Path filePath = Files.readSymbolicLink(fdPath);

Path internalPath = Paths.get(context.getApplicationInfo().dataDir);

returnfilePath.startsWith(internalPath);

}

## Sharing activities

Almost all apps that work with user content, such as messaging apps or email clients, can receive it from outside. Special actions exist on Android for this purpose:

- `"android.intent.action.SEND"`

- `"android.intent.action.SEND_MULTIPLE"`


The handling activities take a URI parameter `Intent.EXTRA_STREAM`(`"android.intent.extra.STREAM"`) from the intent they receive, usually cache it, and then do something with the content. For example:

File `AndroidManifest.xml`:

<activityandroid:name=".ShareActivity"android:enabled="true"android:exported="true">

<intent-filter>

<actionandroid:name="android.intent.action.SEND"/>

<actionandroid:name="android.intent.action.SEND\_MULTIPLE"/>

<categoryandroid:name="android.intent.category.DEFAULT"/>

<dataandroid:mimeType="image/\*"/>

<dataandroid:mimeType="\*/\*"/>

</intent-filter>

</activity>

File `ShareActivity.java`:

public class ShareActivity extendsActivity{

protectedvoidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

Intent intent = getIntent();

String action = intent.getAction();

if(Intent.ACTION\_SEND.equals(action)){

Uri uri = intent.getParcelableExtra(Intent.EXTRA\_STREAM);

processUri(uri);

}elseif(Intent.ACTION\_SEND\_MULTIPLE.equals(action)){

List<Uri\> uris = intent.getParcelableArrayListExtra(Intent.EXTRA\_STREAM);

processUris(uris);

}

}

private voidprocessUris(List<Uri\> uris){

for(Uri uri :uris){

processUri(uri);

}

}

private voidprocessUri(Uri uri){

File cacheFile = newFile(getExternalCacheDir(),"temp");

copy(uri,cacheFile);

// Do normal stuff

}

}

An attack might look like this:

StrictMode.setVmPolicy(StrictMode.VmPolicy.LAX);

Intent intent = newIntent(Intent.ACTION\_SEND);

intent.setClassName("com.victim","com.victim.ShareActivity");

intent.putExtra(Intent.EXTRA\_STREAM,Uri.parse("file:///data/user/0/com.victim/shared\_prefs/secrets.xml"));

startActivity(intent);

> Remediation: The advice for protection is just the same as in the previous section. Following it allows you to prevent not just the theft of files by copying them to public storage, but also sending them e.g. to a chat.

## Exported providers

On the one hand, this is the simplest and most obvious way of stealing files. But it’s still encountered in numerous apps. For example, Oversecured [found](https://blog.oversecured.com/Two-weeks-of-securing-Samsung-devices-Part-2/#file-theft-from-uid-1001-in-callbgprovider) a vulnerability of this kind in a pre-installed Samsung system app. The provider there was exported but was only protected with a weak permission, allowing an attacker to gain access to arbitrary files.

Example of a vulnerable app:

File `AndroidManifest.xml`:

<providerandroid:name=".MyContentProvider"android:authorities="com.victim.myprovider"android:exported="true"/>

File `MyContentProvider.java`:

public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException {

File root = newFile(getContext().getFilesDir(),"my\_files");

File file = newFile(root,uri.getPath());

returnParcelFileDescriptor.open(file,ParcelFileDescriptor.MODE\_READ\_ONLY);

}

Attack to gain access to the file `/data/user/0/com.victim/shared_prefs/secrets.xml`:

Uri uri = Uri.parse("content://com.victim.myprovider/../../shared\_prefs/secrets.xml");

try(InputStream inputStream = getContentResolver().openInputStream(uri)){

Log.d("evil",IOUtils.toString(inputStream));

}catch(Throwable th){

thrownewRuntimeException(th);

}

Our intentionally vulnerable Android app, OVAA, provides another example of a similar vulnerability:

![](https://framerusercontent.com/images/QdCSobMSk3pw8cEIwF5YwtUmIfs.png?width=2252&height=888)

The scan report shows:

1. A snippet from the `AndroidManifest.xml` file with the declaration of the exported provider

2. Call to `Uri.getLastPathSegment()` with a URI that an attacker could control, leading to path traversal on the path to the file

3. Creation of a `ParcelFileDescriptor` object which is returned from the `openFile()` method, leading to access to arbitrary files


### Remediation

Avoid exporting a provider if it’s intended for sharing files within the app. If the provider is intended to work with other apps, good protection would be to add a `signature` permission for access; but there must be no mistakes when working with it of the kind we discuss in a [separate article](https://blog.oversecured.com/Common-mistakes-when-using-permissions-in-Android/). It’s also possible to make the provider non-exported but set the flag `android:grantUriPermissions="true"`, which allows the app itself to grant access only to specific URIs.

Follow the advice described above for avoiding attacks using other vectors.

## WebView

File theft attacks via WebView are described more fully and in more detail in separate articles:

- via [insecure implementation of WebResourceResponse](https://blog.oversecured.com/Android-Exploring-vulnerabilities-in-WebResourceResponse/). The article describes the attack itself and gives an example of this vulnerability in Amazon apps

- via [XHR queries](https://blog.oversecured.com/Android-security-checklist-webview/#attacks-where-universal-file-access-from-file-urls-is-enabled). This attack is possible when universal/file access from file URLs is enabled в WebView

- via [file choosers](https://blog.oversecured.com/Android-security-checklist-webview/#theft-of-arbitrary-files-via-file-choosers). This attack is possible when an attacker can intercept implicit intents and gain access to files in WebView


## Gaining access to arbitrary\* content providers

Developer mistakes allowing access to providers with the flag `android:grantUriPermissions="true"` are described in a [separate article](https://blog.oversecured.com/Gaining-access-to-arbitrary-Content-Providers/). If an attacker can make the app pass them an intent with custom Data, ClipData, and certain other fields and with custom flags (or with a pre-set `Intent.FLAG_GRANT_READ_URI_PERMISSION`and/or `Intent.FLAG_GRANT_WRITE_URI_PERMISSION`), they can obtain access to arbitrary providers belonging to the app.

An example of this mistake is included in OVAA:

![](https://framerusercontent.com/images/ejzNy6Sb2MMs1pknrZbtKrieug.png?width=2256&height=1940)

## Local web servers

It may seem strange and surprising, but more than a few Android apps run local web servers internally for their purposes. [NanoHTTPD](https://github.com/NanoHttpd/nanohttpd) works on Android too. Developers should remember that these servers become available from the local network while the app is running, which makes a possible vulnerability even more dangerous.

Since the majority of such vulnerabilities we have discovered in Android apps did use this library, we provide a typical example of a vulnerability featuring it:

public class App extendsNanoHTTPD{

privateContextcontext;

publicApp(Context context)throwsIOException{

super(8080);

this.context = context;

start(NanoHTTPD.SOCKET\_READ\_TIMEOUT,false);

}

private static final String CACHE\_PREFIX = "/cache/";

@Override

public Response serve(IHTTPSession session){

final String requestUri = session.getUri();

if(requestUri.startsWith(CACHE\_PREFIX)){

String path = requestUri.substring(CACHE\_PREFIX.length());

File requestedFile = newFile(context.getCacheDir(),path);

String mimeType = NanoHTTPD.getMimeTypeForFile(path);

try{

InputStream inputStream = newFileInputStream(requestedFile);

returnnewFixedLengthResponse(Response.Status.OK,mimeType,inputStream,requestedFile.length());

}catch(IOException e){

e.printStackTrace();

}

}

returnnewFixedLengthResponse("");

}

}

public class MainActivity extendsActivity{

privateAppapp;

protectedvoidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

try{

app = newApp(this);

}catch(IOException e){

thrownewRuntimeException(e);

}

}

}

As you see from the example, vulnerability is a typical example of path traversal.

### Remediation

- You should re-examine the architecture of your app and make sure a local web server is really necessary.

- You should treat the code for that web server like a typical web app and check it for the same errors.

- In the case of the example we have given, we would recommend validating the file path and preventing path traversal attacks, and avoiding using the “broad” `cache` directory for file storage: instead we would use, for example, `cache/web_cache`.


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

[![](https://framerusercontent.com/images/pzmPwb8meXTvehy3juezcWM86w.png?width=1424&height=828)\\
\\
Android security checklist: WebView\\
\\
WebView is a web browser that can be built into an app, and represents the most widely used component of the Android ecosystem; it is also subject to the largest number of potential\\
\\
Android Security\\
\\
Oct 29, 2021\\
\\
13\\
\\
min read](https://oversecured.com/blog/android-security-checklist-webview)

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

[go up ↑](https://oversecured.com/blog/android-security-checklist-theft-of-arbitrary-files#header)

Chat Widget