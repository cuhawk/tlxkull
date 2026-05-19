---
source: spaceraccoon
source_url: https://spaceraccoon.dev/applying-offensive-reverse-engineering-to-facebook-gameroom/
title: "Applying Offensive Reverse Engineering to Facebook Gameroom | Spaceraccoon's Blog"
published: 2021-02-02T17:03:30+00:00
description: "Late last year, I was invited to Facebook’s Bountycon event, which is an invitation-only application security conference with a live-hacking segment. Although participants could submit vulnerabilities for any Facebook asset, Facebook invited us to focus on Facebook Gaming. Having previously tested Facebook’s assets, I knew it was going to be a tough challenge."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Applying Offensive Reverse Engineering to Facebook Gameroom

Feb 2, 2021
·

1898 words

·

9 minute read


# Applying Offensive Reverse Engineering to Facebook Gameroom [🔗](https://spaceraccoon.dev/applying-offensive-reverse-engineering-to-facebook-gameroom/\#applying-offensive-reverse-engineering-to-facebook-gameroom)

Late last year, I was invited to Facebook’s Bountycon event, which is an invitation-only application security conference with a live-hacking segment. Although participants could submit vulnerabilities for any Facebook asset, Facebook invited us to focus on Facebook Gaming. Having previously tested Facebook’s assets, I knew it was going to be a tough challenge. Their security controls have only gotten tougher over the years - even simple vulnerabilities such as cross-site scripting are hard to come by, which is why they pay out so much for [those](https://portswigger.net/daily-swig/facebook-pays-out-25k-bug-bounty-for-chained-dom-based-xss). As such, top white hat hackers tend to approach Facebook from a third-party software angle, such as Orange Tsai’s well-known [MobileIron MDM exploits](https://blog.orange.tw/2020/09/how-i-hacked-facebook-again-mobileiron-mdm-rce.html).

Given my limited time (I also started late due to an administrative issue), I decided to stay away from full-scale vulnerability research and focussed on simple audits of Facebook Gaming’s access controls. However, both the mobile and web applications were well-secured, as one would expect. After a bit of digging, I came across [Facebook Gameroom](https://www.facebook.com/gameroom/download/), a Windows-native client for playing Facebook games. I embarked on an illuminating journey of applying offensive reverse engineering to a native desktop application.

# Facebook Gameroom, Who Dis? [🔗](https://spaceraccoon.dev/applying-offensive-reverse-engineering-to-facebook-gameroom/\#facebook-gameroom-who-dis)

If you haven’t heard about Facebook Gameroom, you’re probably not alone. Released in November 2016, Gameroom was touted as a Steam competitor that supports Unity, Flash, and more recently HTML5 games. However, in recent years Facebook has turned its attention to its mobile and web platforms, especially with the rise of streaming. In fact, Gameroom is scheduled to be decommissioned in June this year. Fortunately for me, it was still alive and kicking at the time of the event.

![Facebook Gameroom](https://spaceraccoon.dev/images/11/facebook_gameroom.png)

The first thing I noticed was that Gameroom did not require any elevated permissions to install. It appeared to be a staged installer, where a minimal installer pulls additional files from the web instead of a monolithic installer. Indeed, I quickly found the installation directory at `C:\Users\<USERNAME>\AppData\Local\Facebook\Games`, since most user-level applications are placed in the `C:\Users\<USERNAME>\AppData` folder. The folder contained lots of `.dll` files as well as several executables. A few things stood out to me:

1. Gameroom came with its own bundled 7zip executable (`7z.exe` and `7z.dll`), which was possibly outdated and vulnerable.
2. Gameroom stored user session data in `Cookies` SQLite database, which presented an attractive target for attackers.
3. Gameroom included the CefSharp library (`CefSharp.dll`), which after further research turned out to be an embedded Chromium-based browser for C#.

The third point suggested to me that Gameroom was written in the .NET framework. The .NET framework allows programmes to be compiled into Common Intermediate Language (CIL) code instead of machine code, which can run in a Common Language Runtime application virtual machine. There are several benefits to this, including greater interoperability and portability of .NET applications. However, it is also a lot easier to decompile these applications back into near-source code since they are compiled as CIL rather than pure machine code.

For .NET assemblies, [DNSpy](https://github.com/dnSpy/dnSpy) is the de-facto standard. Reverse engineers can easily debug and analyze .NET applications with DNSpy, including patching them live. I popped `FacebookGameroom.exe` into DNSpy and got to work.

# A Wild Goose Chase: Searching for Vulnerable Functions [🔗](https://spaceraccoon.dev/applying-offensive-reverse-engineering-to-facebook-gameroom/\#a-wild-goose-chase-searching-for-vulnerable-functions)

I began by searching for vulnerable or dangerous functions such as unsafe deserializations. If you’ve done the Offensive Security Advanced Web Attacks and Exploitation course, you would be intimately familiar with [deserialization attacks](https://www.blackhat.com/docs/us-17/thursday/us-17-Munoz-Friday-The-13th-JSON-Attacks-wp.pdf). I won’t go into detail about them here, but just know that it involves converting data types into easily-transportable formats and back, which can lead to critical vulnerabilities if handled badly. For example, Microsoft warns against using BinaryFormatter in its [code quality analyzer](https://docs.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2300) with a pretty stark `BinaryFormatter is insecure and can't be made secure.`

Unfortunately, BinaryFormatter popped up in my search for the “Deserialize” string.

![BinaryFormatter](https://spaceraccoon.dev/images/11/binaryformatter.png)

However, I needed to find the vulnerable code path. I right-clicked the search result, selected “Analyze”, then worked up the “Used By” chain to locate where Gameroom used `BinaryFormatter.Deserialize`.

![Used By Chain](https://spaceraccoon.dev/images/11/used_by_chain.png)

Eventually, this led me to the `System.Configuration.ApplicationSettingsBase.GetPreviousVersion(string)` and `	System.Configuration.ApplicationSettingsBase.GetPropertyValue(string)` functions. Gameroom used the deserialization function to retrieve its application settings at startup - but from where? Looking back at the installation folder, I found `fbgames.settings`, which turned out to be a serialized blob. As such, if I injected a malicious deserialization payload into this file, I could obtain code execution. Before that, however, I needed to find a deserialization gadget. With a bit more searching based on a list of known deserialization gadgets, I discovered that Gameroom used the `WindowsIdentity` class.

With that, I worked out a code execution proof-of-concept:

1. Using the [`ysoserial`](https://github.com/pwntester/ysoserial.net) deserialization attack tool, I generated my code execution payload with `ysoserial.exe -f BinaryFormatter -g WindowsIdentity -o raw -c "calc" -t > fbgames.settings`.
2. Next, I copied `fbgames.settings` to `C:\Users\<YOUR USERNAME>\AppData\Local\Facebook` and replaced the original file. No admin privileges were required since it was located in a user directory.
3. Finally, I opened Facebook Gameroom and calculator popped!

Although it was exciting to get code execution, upon further discussion with the Facebook team we agreed that this did not fit their threat model. Since Gameroom executes as a user-level applications, there’s no opportunity to escalate privileges. Additionally, since overwriting the file required some level of access (e.g. via a malicious Facebook game that would require approval to be listed publicly), there was no viable remote attack vector.

I learned an important lesson in the different threat landscape posed by native applications - search for a viable remote attack vector first before diving into the code-level vulnerabilities.

# Scheming My Way to Success [🔗](https://spaceraccoon.dev/applying-offensive-reverse-engineering-to-facebook-gameroom/\#scheming-my-way-to-success)

Have you ever clicked on a link from an email and magically started Zoom? What exactly happened behind the scenes? You just used a custom URI scheme, which allows you to open applications like any other link on the web. For example, Zoom registers the `zoommtg:` URI scheme and parses links like `zoommtg:zoom.us/join?confno=123456789&pwd=xxxx&zc=0&browser=chrome&uname=Betty`.

Similarly, I noticed that Gameroom used a custom URI scheme to automatically open Gameroom after clicking a link from the web browser. After searching through the code, I realized that Gameroom checked for the `fbgames:` URI scheme in `FacebookGames\Program.cs`:

```csharp
private static void OnInstanceAlreadyRunning()
{
    Uri uri = ArgumentHelper.GetLaunchScheme() ?? new Uri("fbgames://");
    if (SchemeHelper.GetSchemeType(uri) == SchemeHelper.SchemeType.WindowsStartup)
    {
        return;
    }
    NativeHelpers.BroadcastArcadeScheme(uri);
}
```

If Gameroom had been opened with the `fbgames://` URI, it would proceed to parse it in the `SchemeHelper` class:

```csharp
public static SchemeHelper.SchemeType GetSchemeType(Uri uri)
{
if (uri == (Uri) null)
return SchemeHelper.SchemeType.None;
string host = uri.Host;
if (host == "gameid")
return SchemeHelper.SchemeType.Game;
if (host == "launch_local")
return SchemeHelper.SchemeType.LaunchLocal;
return host == "windows_startup" ? SchemeHelper.SchemeType.WindowsStartup : SchemeHelper.SchemeType.None;
}

public static string GetGameSchemeId(Uri uri)
{
if (SchemeHelper.GetSchemeType(uri) != SchemeHelper.SchemeType.Game)
return (string) null;
string str = uri.AbsolutePath.Substring(1);
int num = str.IndexOf('/');
int length = num == -1 ? str.Length : num;
return str.Substring(0, length);
}
```

If the URI had the `gameid` host, it would parse it with `SchemeHelper.SchemeType.Game`. If it used the `launch_local` host, it would parse it with `SchemeHelper.SchemeType.LaunchLocal`. I started with the promising `launch_local` path, tracing it to `FacebookGames.SchemeHelper.GenLocalLaunchFile(Uri)`:

```csharp
public static async Task<string> GenLocalLaunchFile(Uri uri)
{
    string result;
    if (SchemeHelper.GetSchemeType(uri) != SchemeHelper.SchemeType.LaunchLocal || uri.LocalPath.Length <= 1)
    {
        result = null;
    }
    else if (!(await new XGameroomCanUserUseLocalLaunchController().GenResponse()).CanUse)
    {
        result = null;
    }
    else
    {
        string text = uri.LocalPath.Substring(1);
        result = ((MessageBox.Show(string.Format("Are you sure you want to run file\n\"{0}\"?", text), "Confirm File Launch", MessageBoxButtons.YesNo) == DialogResult.Yes) ? text : null);
    }
    return result;
}
```

Unfortunately, it appeared that even though I could launch any arbitrary file in the system through a URI like `fbgames://launch_local/C:/evilapp.exe` (as [documented](https://developers.facebook.com/docs/games/gameroom/build/) by Facebook), this would be blocked by a confirmation dialog. I tried to bypass this dialog with format strings and non-standard inputs, but couldn’t find a way past it.

I returned to the `gameid` path, which opened a Facebook URL based on the game ID in the URI. For example, if you wanted to launch Words With Friends in Gameroom, you would visit `fbgame://gameid/168378113211268` in a browser and Gameroom would open `https://apps.facebook.com/168378113211268` in the native application window.

However, I realized that `GetGameSchemeId`, which extracted the ID from the URI that would be added to the `apps.facebook.com` URL, did not actually validate that the slug was a valid ID. As such, an attacker could redirect the native application window to any other page on Facebook.

```csharp
public static string GetGameSchemeId(Uri uri)
{
if (SchemeHelper.GetSchemeType(uri) != SchemeHelper.SchemeType.Game)
return (string) null;
string str = uri.AbsolutePath.Substring(1);
int num = str.IndexOf('/');
int length = num == -1 ? str.Length : num;
return str.Substring(0, length);
}
```

For example, `fbgame://gameid/evilPage` would redirect the Gameroom window to `https://apps.facebook.com/evilPage`.

But how could I redirect to attacker-controlled code in Gameroom? There were a few options, including abusing an open redirect on `apps.facebook.com`. Unfortunately, I did not have one on hand at that time. Another way was to redirect to a Facebook Page or ad that allowed embedded iframes with custom code.

At this point, I hit a roadblock. Revisting the code of `GetGameSchemeId`, it took only the first slug in the URI path, so `fbgame://gameid/evilPage/app/123456` would direct the native application window to `https://apps.facebook.com/evilPage` and discard `/app/123456`.

Fortunately, there were additional code gadgets I could use. The version of Chrome used in Gameroom was really outdated: `63.0.3239.132` \- the current version at the time was `86.0.4240.75`. As such, it did not support the new version of Facebook Pages. The classic Facebook Pages version accepted a `sk` parameter such that `https://apps.facebook.com/evilPage?sk=app_123456` led to the custom tab with the attacker-controlled code at `https://apps.facebook.com/evilPage/app/123456`!

But how could I inject the additional query parameter in my custom scheme? Remember that Gameroom discards anything after the first URL slug, including query parameters. Or does it? Looking back at `FacebookGames/SchemeHelper.cs`, I found `GetCanvasParamsFromQuery`:

```csharp
public static IDictionary<string, string> GetCanvasParamsFromQuery(Uri uri)
{
if (uri == (Uri) null)
return (IDictionary<string, string>) null;
string stringToUnescape;
if (!UriHelper.GetUrlParamsFromQuery(uri.ToString()).TryGetValue("canvas_params", out stringToUnescape))
return (IDictionary<string, string>) null;
string str = Uri.UnescapeDataString(stringToUnescape);
try
{
return JsonConvert.DeserializeObject<IDictionary<string, string>>(str);
}
catch
{
return (IDictionary<string, string>) null;
}
}
```

Before passing on the custom URI, `GetCanvasParamsFromQuery` would look for the `canvas_params` query parameter, serialize it as a JSON dictionary, and convert it into the new URL as query parameters.

This led me to my final payload scheme. `fbgames://gameid/evilPage?canvas_params={"sk":"app_123456"}` would be parsed by Gameroom into `https://apps.facebook.com/evilPage/app/123456` in the native application browser window, which would then execute my custom JavaScript code.

As mentioned earlier, the threat landscape for a native application is very different from a web application. By redirecting the embedded Chrome native window to attacker-controlled Javascript, an attacker could proceed to perform known exploits on the 3-year-old embedded Chromium browser. Although a full exploit had not been publicly released, I was able to leverage the [CVE-2018-6056 proof-of-concept code](https://github.com/tunz/js-vuln-db/blob/master/v8/CVE-2018-6056.md) to crash the Chrome engine via a type confusion vulnerability.

Alternatively, an attacker could create pop up boxes that were essentially legitimate native MessageBoxes to perform phishing attacks, or attempt to read the cached credentials file. Fortunately, unlike [Electron applications](https://spaceraccoon.dev/open-sesame-escalating-open-redirect-to-rce-with-electron-code-review) that integrate Node.JS APIs, `CefSharp` limits API access. However, it still remains vulnerable to [Chromium and third-party library vulnerabilities](https://github.com/cefsharp/CefSharp/security/advisories).

# Summing Up [🔗](https://spaceraccoon.dev/applying-offensive-reverse-engineering-to-facebook-gameroom/\#summing-up)

Facebook awarded it as High and subsequently patched the vulnerability, pushing me into the top-10 leaderboard for Bountycon. Although Gameroom will be shut down soon, it definitely left me with some fond memories (and practice) in basic offensive reverse engineering. For newcomers to application reverse engineering, Electron, CefSharp, and other browser-based frameworks are a good starting place to test for web-adjacent weaknesses like cross-site scripting and open redirects, while exploiting desktop-only code execution vectors.

[desktop](https://spaceraccoon.dev/tags/desktop) [reverse engineering](https://spaceraccoon.dev/tags/reverse-engineering)