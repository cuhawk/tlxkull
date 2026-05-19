---
source: oversecured
source_url: https://oversecured.com/blog/content-providers-and-the-potential-weak-spots-they-can-have
title: "Content Providers and the potential weak spots they can have | Oversecured Blog"
author: "HubSpot, Inc."
description: "Android security checklist: Content Providers"
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

## Android security checklist: Content Providers

Today, let’s dive deeper into Content Providers and the potential weak spots they can have. ​ Before we jump into the details, we want to stress how important it is to keep your users’ data safe. Nowadays, security is a big deal, and you definitely want to protect your users against problems like those that can come from Content Providers. ​ If you’re curious about how Oversecured can help your team watch over every bit of your code, sending you automatic reports about any vulnerabilities and telling you how to fix them, [just get in touch with us](https://app.oversecured.com/contact-us). We’ve got more information about securing your apps and users’ data that we’d love to share.

Content Providers are a fundamental component of the Android platform, extensively used for sharing data among different applications. Often, they provide access to sensitive content. However, due to common errors in their implementation and protection mechanisms, they are susceptible to various vulnerabilities. This article will explore the most prevalent issues in their operation and potential methods to exploit them.

Before delving into demonstrating the errors, it is essential to comprehend the concept of providers and their intended tasks. Broadly, providers can be categorized into three primary groups:

1. ### Sharing and Modifying Content


Applications frequently employ an SQLite database to store and manipulate content. This approach is effective until the need arises to share data with other applications. For instance, in Android, built-in default providers allow access to [user contacts](https://android.googlesource.com/platform/packages/providers/ContactsProvider/) and [SMS messages](https://android.googlesource.com/platform/packages/providers/TelephonyProvider/). In such cases, queries from the `ContentProvider` implementation are generally proxied to the database using methods like `query()`, `update()`, `delete()`, `insert()`, and `bulkInsert()`. The application that accesses the content invokes corresponding methods in `ContentResolver`.

2. ### Providing read/write Access to Files


Providers are also used to create `ParcelFileDescriptor` objects (file descriptors for the requested files) with read and/or write access. In such scenarios, developers implement methods like `openFile()`, `openAssetFile()`, `openTypedAssetFile()`, and/or `openFileHelper()`. The recipient of content files must call methods such as `ContentResolver.openFile()`, `ContentResolver.openAssetFile()`, `ContentResolver.openInputStream()`, `ContentResolver.openOutputStream()`, `ContentResolver.openFileDescriptor()`, `ContentResolver.openAssetFileDescriptor()`, `ContentResolver.openTypedAssetFile()`, and/or `ContentResolver.openTypedAssetFileDescriptor()`. While the diverse range of return values might seem overwhelming, it’s important to note that `AssetFileDescriptor` wraps `ParcelFileDescriptor`, and `ParcelFileDescriptor` wraps `FileDescriptor`. Methods like `ContentResolver.openInputStream()` and `ContentResolver.openOutputStream()` simply employ the file descriptor to open streams for reading or writing.

3. ### Executing Commands


The `call()` method serves this purpose. It takes the name of an action and its arguments as input, returning the result encapsulated in a `Bundle` object. Executed actions can encompass a wide range of functionalities. For instance, in Android, a [provider for device settings](https://android.googlesource.com/platform/frameworks/base/+/a680cb9/packages/SettingsProvider/src/com/android/providers/settings/SettingsProvider.java#415) exists, enabling reading and editing of settings via the `call()` method.

All the common errors described can impact both directly exported providers and those declared with the `android:grantUriPermissions="true"` flag. Attackers can exploit various pathways to gain access, as elaborated in the article [Gaining access to arbitrary\* Content Providers](https://blog.oversecured.com/Gaining-access-to-arbitrary-Content-Providers/).

## Insecure `FileProvider`

In recent Android versions, obtaining content files directly from other apps is restricted due to SELinux limitations, even if file access mode is set to `777`. To address the issue of file exchange between different applications while enhancing security, apps can grant access to specific files or folders. This task is so common that Android developers introduced the [FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider) class, which greatly simplifies this process. In the `AndroidManifest.xml`, such providers cannot be exported, but they are always declared with the `android:grantUriPermissions="true"` flag. They also always refer to an XML resource file that describes paths to shareable files. The following possible entries with paths exist:

- `root-path`: arbitrary files (`/`)

- `files-path`: files in the private `files` directory (`/data/user/0/com.victim/files/`)

- `cache-path`: files in the private `cache` directory (`/data/user/0/com.victim/cache/`)

- `external-path`: arbitrary files on the SD card (`/sdcard/`)

- `external-files-path`: files in the `files` folder on the SD card within the app’s directory (`/sdcard/Android/data/com.victim/files/`)

- `external-cache-path`: files in the `cache` folder on the SD card within the app’s directory (`/sdcard/Android/data/com.victim/cache/`)

- `external-media-path`: media files on the SD card within the app’s directory (`/sdcard/Android/media/com.victim/`)


The issue arises when such a provider grants access to too many files. This impacts security and could lead to unauthorized access to unintended files when combined with other vulnerabilities.

For instance, [on Samsung devices, this allowed gaining read/write access to arbitrary files with system privileges](https://blog.oversecured.com/Two-weeks-of-securing-Samsung-devices-Part-2/#file-theft-and-write-from-uid-1000-in-factorycamerafb):

![](https://framerusercontent.com/images/KvIltyNA2y1c4cyw6O9ALv0BbM.png?width=2252&height=704)

A common attack chain involves [intent redirection](https://blog.oversecured.com/Android-Access-to-app-protected-components/) followed by gaining access to arbitrary providers with the `android:grantUriPermissions="true"` flag. The third link in this attack is an insecure `FileProvider` that, for example, grants access either to all files or entire directories like `files` or `cache`.

> Remediation: Each `FileProvider` should be responsible for a specific action, such as sharing images. Providers for general tasks should not be created. Additionally, each provider should only grant access to a specific subfolder (e.g., `/data/user/0/com.victim/cache/my_image_cache/` instead of the entire `/data/user/0/com.victim/cache/`).

## Path-traversal when using data from `Uri`

The most common mistake when working with files in providers is using data obtained from methods like `Uri.getLastPathSegment()`, `Uri.getPathSegments()`, and others that return specific parts of a URI. Developers need to remember that these methods also decode values. Hence, an attacker can perform URL-encoding on expected values, successfully executing a path-traversal attack.

Oversecured has already described such errors. For instance, in the case of Google, this led to arbitrary code execution, where using a decoded value allowed gaining read+write access to arbitrary files. Another documented example allowed read-only access to arbitrary files with system privileges on Samsung devices:

![](https://framerusercontent.com/images/uzi0HFs8zUpteQPI79JrfkP3cFE.png?width=2262&height=1764)

Example of vulnerable code:

File `AndroidManifest.xml`:

<provider

android:name="com.victim.PathTraversalProvider"

android:authorities="com.victim.path\_traversal"

android:exported="true"/>

File `PathTraversalProvider.java`:

public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException {

File file = newFile(getContext().getFilesDir(),uri.getLastPathSegment());

returnParcelFileDescriptor.open(file,ParcelFileDescriptor.parseMode(mode));

}

As per the developer’s intention, the app should return file descriptors for files in the files directory. However, the following attack can be used to retrieve content from arbitrary `files`:

Uri uri = Uri.parse("content://com.victim.path\_traversal/..%2Fshared\_prefs%2Fsecrets.xml");

try(InputStream inputStream = getContentResolver().openInputStream(uri)){

Log.d("evil",newString(inputStream.readAllBytes()));

}catch(IOException e){

//...

}

> Remediation: It’s necessary to either validate the resulting path by calculating the canonical path or re-encode the value: `Uri.encode(Uri.getLastPathSegment())`.

## Errors in `android:readPermission` and `android:writePermission`declarations

In addition to the `android:permission` attribute, providers have two more attributes: `android:readPermission` and `android:writePermission`. The former sets the permission for read methods like `query()`. The latter applies to write methods including `insert()`, `update()`, `delete()`, and `bulkInsert()`. The `call()`method requires the caller to have either `android:readPermission` or `android:writePermission`. Methods for reading files check the access mode (read-only, write-only, or read+write).

### Example 1

<provider

android:name="com.victim.ProtectedProvider"

android:authorities="com.victim.protected"

android:readPermission="com.victim.SIGNATURE\_LEVEL"

android:exported="true"/>

In this case, read operations will require the `com.victim.SIGNATURE_LEVEL` permission, but no permission will be needed for write operations.

### Example 2

<provider

android:name="com.victim.ProtectedProvider"

android:authorities="com.victim.protected"

android:permission="com.victim.NORMAL\_LEVEL"

android:readPermission="com.victim.SIGNATURE\_LEVEL"

android:exported="true"/>

Here, read operations will require the `com.victim.SIGNATURE_LEVEL`permission, and write operations will need the `com.victim.NORMAL_LEVEL` permission.

Now, let’s consider a vulnerable application example. Code similar to this has been encountered by the Oversecured team multiple times:

File `AndroidManifest.xml`:

<provider

android:name="com.victim.ProtectedProvider"

android:authorities="com.victim.protected"

android:readPermission="com.victim.SIGNATURE\_LEVEL"

android:exported="true"/>

File `ProtectedProvider.java`:

public ParcelFileDescriptor openFile(Uri uri,String mode)throws FileNotFoundException {

returnParcelFileDescriptor.open(newFile(uri.getPath()),ParcelFileDescriptor.MODE\_READ\_ONLY);

}

In this case, the `ContentResolver` will only check the `mode` value during access rights verification, which is ignored in the `openFile()`method’s code. Exploiting the read access to arbitrary files would look like this:

try{

Uri uri = Uri.parse("content://com.victim.protected/data/user/0/com.victim/shared\_prefs/secrets.xml");

ParcelFileDescriptor pfd = getContentResolver().openFile(uri,"w",null);

try(InputStream inputStream = newFileInputStream(pfd.getFileDescriptor())){

Log.d("evil",newString(inputStream.readAllBytes()));

}

}catch(IOException e){

//...

}

> Remediation: In addition to the obvious advice of verifying access mode, it’s crucial not to leave read/write access without the required permissions. If a developer is unsure whether to demand read or write permission, it’s recommended to set the permission to the `android:permission` attribute.

## Proxying requests to more secure providers

One typical mistake developers make is combining different providers’ functionality into one with a decreased level of security. Let’s consider the following example:

File `AndroidManifest.xml`:

<permissionandroid:name="com.victim.NORMAL\_PERMISSION"android:protectionLevel="normal"/>

<uses-permission android:name="com.victim.NORMAL\_PERMISSION" />

<provider

android:name="oversecured.test.CommonContentProvider"

android:authorities="com.victim.common"

android:permission="com.victim.NORMAL\_PERMISSION"

android:exported="true"/>

File `CommonContentProvider.java`:

public class CommonContentProvider extendsContentProvider{

privatestaticfinalUriMatcherMATCHER = newUriMatcher(UriMatcher.NO\_MATCH);

privatestaticfinalintCONTACTS\_CODE = 1;

static{

MATCHER.addURI("com.victim.common","contacts",CONTACTS\_CODE);

//...

}

@Override

publicCursorquery(Uri uri,String\[\]projection,String selection,String\[\]selectionArgs,

StringsortOrder) {

switch(MATCHER.match(uri)){

caseCONTACTS\_CODE:{

Uri newUri = ContactsContract.CommonDataKinds.Phone.CONTENT\_URI;

returngetContext().getContentResolver().query(newUri,projection,selection,

selectionArgs,sortOrder);

}

//...

}

}

In this case, a vulnerable application accesses the system provider that stores user contacts. However, the provider is protected by the `com.victim.NORMAL_PERMISSION` permission with the `normal`protection level, while the system provider is declared with the `dangerous` protection level. This allows an attacker to obtain the `com.victim.NORMAL_PERMISSION` permission and use the application with legitimate but vulnerable functionality to read user contacts and potentially abuse the entire system.

Oversecured also considers a vulnerability when requests are proxied from a non-exported provider with the `android:grantUriPermissions="true"` flag to a non-exported provider without this flag. With other vulnerabilities in place, the attacker can gain access, resulting in a reduction of the application’s security level and user protection.

Furthermore, one of the most severe security mistakes is using dynamic URIs, where an attacker can control the provider to which the request is directed, like in the following example:

private static final UriMatcher MATCHER = newUriMatcher(UriMatcher.NO\_MATCH);

private static final int PROXY\_CODE = 1;

static {

MATCHER.addURI("com.victim.proxy","proxy",PROXY\_CODE);

//...

}

@Override

public Cursor query(Uri uri,String\[\]projection,String selection,String\[\] selectionArgs,

String sortOrder){

switch(MATCHER.match(uri)){

casePROXY\_CODE:{

Uri newUri = Uri.parse(uri.getQueryParameter("uri"));

returngetContext().getContentResolver().query(newUri,projection,selection,

selectionArgs,sortOrder);

}

//...

}

}

Such an error can allow an attacker to access all the providers that the vulnerable application has access to (including ecosystem apps and system providers accessible through requested permissions).

> Remediation: Developers should avoid proxying requests to other providers within their implementations.

## Mixing sensitive and non-sensitive data in one database

Let’s examine a vulnerable application fragment with two content providers that use different access permissions but share the same database.

File `AndroidManifest.xml`:

<permission

android:name="com.victim.SECURE\_PERMISSION"

android:protectionLevel="signature"/>

<provider

android:name="com.victim.SensitiveContentProvider"

android:authorities="com.victim.sensitive"

android:exported="true"

android:permission="com.victim.SECURE\_PERMISSION"/>

<provider

android:name="com.victim.InsensitiveContentProvider"

android:authorities="com.victim.insensitive"

android:exported="true" />

File `SensitiveContentProvider.java`:

public class SensitiveContentProvider extendsContentProvider{

privateDatabaseHelperhelper;

@Override

publicbooleanonCreate(){

helper = newDatabaseHelper(getContext());

returntrue;

}

@Override

publicStringgetType(Uri uri){

returnnull;

}

@Override

publicCursorquery(Uri uri,String\[\]projection,String selection,String\[\]selectionArgs,

StringsortOrder) {

returnhelper.getReadableDatabase().query(DatabaseHelper.SENSITIVE\_TABLE\_NAME,projection,

selection,selectionArgs,null,null,sortOrder);

}

@Override

public Uri insert(Uri uri,ContentValues values){

long id = helper.getWritableDatabase().insert(DatabaseHelper.SENSITIVE\_TABLE\_NAME,null,values);

returnContentUris.withAppendedId(uri,id);

}

@Override

public int update(Uri uri,ContentValues values,String selection,String\[\]selectionArgs){

returnhelper.getWritableDatabase().update(DatabaseHelper.SENSITIVE\_TABLE\_NAME,values,

selection,selectionArgs);

}

@Override

public int delete(Uri uri,String selection,String\[\]selectionArgs){

returnhelper.getWritableDatabase().delete(DatabaseHelper.SENSITIVE\_TABLE\_NAME,selection,

selectionArgs);

}

}

File `InsensitiveContentProvider.java`:

public class InsensitiveContentProvider extendsContentProvider{

privateDatabaseHelperhelper;

@Override

publicbooleanonCreate(){

helper = newDatabaseHelper(getContext());

returntrue;

}

@Override

publicStringgetType(Uri uri){

returnnull;

}

@Override

publicCursorquery(Uri uri,String\[\]projection,String selection,String\[\]selectionArgs,

StringsortOrder) {

returnhelper.getReadableDatabase().query(DatabaseHelper.INSENSITIVE\_TABLE\_NAME,projection,

selection,selectionArgs,null,null,sortOrder);

}

@Override

public Uri insert(Uri uri,ContentValues values){

long id = helper.getWritableDatabase().insert(DatabaseHelper.INSENSITIVE\_TABLE\_NAME,null,values);

returnContentUris.withAppendedId(uri,id);

}

@Override

public int update(Uri uri,ContentValues values,String selection,String\[\]selectionArgs){

returnhelper.getWritableDatabase().update(DatabaseHelper.INSENSITIVE\_TABLE\_NAME,values,

selection,selectionArgs);

}

@Override

public int delete(Uri uri,String selection,String\[\]selectionArgs){

returnhelper.getWritableDatabase().delete(DatabaseHelper.INSENSITIVE\_TABLE\_NAME,selection,

selectionArgs);

}

}

File `DatabaseHelper.java`:

public class DatabaseHelper extendsSQLiteOpenHelper{

privatestaticfinalStringDATABASE\_NAME = "data.db";

privatestaticfinalintDATABASE\_VERSION = 1;

publicstaticfinalStringSENSITIVE\_TABLE\_NAME = "Sensitive";

privatestaticfinalStringCREATE\_SENSITIVE\_TABLE =

"CREATE TABLE " \+ SENSITIVE\_TABLE\_NAME \+ " (" +

"\_id INTEGER PRIMARY KEY AUTOINCREMENT, " +

"sensitiveData TEXT NOT NULL)";

publicstaticfinalStringINSENSITIVE\_TABLE\_NAME = "Insensitive";

privatestaticfinalStringCREATE\_INSENSITIVE\_TABLE =

"CREATE TABLE " \+ INSENSITIVE\_TABLE\_NAME \+ " (" +

"\_id INTEGER PRIMARY KEY AUTOINCREMENT, " +

"staticData TEXT NOT NULL)";

publicDatabaseHelper(Context context){

super(context,DATABASE\_NAME,null,DATABASE\_VERSION);

}

@Override

publicvoidonCreate(SQLiteDatabase db){

db.execSQL(CREATE\_SENSITIVE\_TABLE);

db.execSQL(CREATE\_INSENSITIVE\_TABLE);

}

@Override

public voidonUpgrade(SQLiteDatabase db,int i,int i1){

db.execSQL("DROP TABLE IF EXISTS " \+ SENSITIVE\_TABLE\_NAME);

db.execSQL("DROP TABLE IF EXISTS " \+ INSENSITIVE\_TABLE\_NAME);

onCreate(db);

}

}

In this example, the application has adequately separated access at the Android level; only trusted apps can access the `SensitiveContentProvider`. However, at the database level, an attacker can exploit SQL injection to access sensitive data. For example, like this:

Uri insensitiveUri = Uri.parse("content://com.victim.insensitive/");

String whereSqli = "1=2 UNION SELECT \* FROM Sensitive -- ";

Cursor cursor = getContentResolver().query(insensitiveUri,null,whereSqli,null,null);

if(cursor != null && cursor.moveToFirst()){

do{

Log.d("evil","Leakged entry: " \+ cursor.getString(1));

}while(cursor.moveToNext());

}

> Remediation: Developers should use separate database files for each content provider. Additionally, ensure that content providers of different security levels do not communicate with each other based on the passed URI.

## Executing sensitive actions in Content Provider

Sometimes developers add complex logic to a Content Provider in addition to content sharing. For example, debug actions, automatic data encryption or decryption, creation/modification of files outside defined directories, and so on. Such overloading of functionality in one place often leads to vulnerabilities. Let’s consider an example that security experts at Oversecured found in a very popular application.

File `AndroidManifest.xml`:

<provider

android:name="com.victim.InternalContentProvider"

android:authorities="com.victim.internal"

android:exported="false"/>

File `InternalContentProvider.java`:

private static final UriMatcher MATCHER = newUriMatcher(UriMatcher.NO\_MATCH);

private static final int DEBUG\_CODE = 1;

static {

MATCHER.addURI("com.victim.internal","debug",DEBUG\_CODE);

//...

}

@Override

public String getType(Uri uri){

returnnull;

}

@Override

public Cursor query(Uri uri,String\[\]projection,String selection,String\[\] selectionArgs,

String sortOrder){

switch(MATCHER.match(uri)){

caseDEBUG\_CODE:{

debug();

returnnull;

}

//...

}

//...

}

private voiddebug(){

File dbFile = getContext().getDatabasePath("internal.db");

File outputFile = newFile(Environment.DIRECTORY\_DOWNLOADS,dbFile.getName());

try(InputStream inputStream = newFileInputStream(dbFile)){

try(OutputStream outputStream = newFileOutputStream(outputFile)){

inputStream.transferTo(outputStream);

}

}catch(IOException e){

//...

}

}

The logic of this code was such that for development purposes, a way to view the database content was added. This was not considered a vulnerability because the content provider was not exported, meaning it was protected. The code review passed.

However, the application contained dozens of places where it accepted URIs from outside and called `ContentResolver.query()`. Thus, an attacker could create a URI like `content://com.victim.internal/debug` and make the application execute dangerous functionality.

> Remediation: Developers should avoid complex logic in Content Providers and use them only as proxies for internal files or database data. They should not modify, create, or move internal data or files except for specifically defined functions like `insert()`, `delete()`, and others.

## Make your mobile apps stronger against all the vulnerabilities that Content Providers might have.

Schedule a demonstration of Oversecured Automated Vulnerability Scanning Solution to see how it operates and how it can assist your company in stopping vulnerabilities in your code at any stage of development.

- Get an in-depth look into how our integration can optimize your security processes.

- Learn how our solution fits effortlessly into your CI/CD pipeline.

- Benefit from insights shared by our security specialists during the demo.


Ready to enhance your app’s security? Fill out the form below to take the first step!

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

[go up ↑](https://oversecured.com/blog/content-providers-and-the-potential-weak-spots-they-can-have#header)

Chat Widget