---
source: p0
source_url: https://projectzero.google/2026/02/gphfh-deep-dive.html
title: "A Deep Dive into the GetProcessHandleFromHwnd API - Project Zero"
description: "In my previous blog post I mentioned the GetProcessHandleFromHwnd API. This was an API I didn’t k..."
---

In my previous blog post I mentioned the [`GetProcessHandleFromHwnd`](https://learn.microsoft.com/en-us/windows/win32/winauto/getprocesshandlefromhwnd) API. This was an API I didn’t know existed until I found a publicly disclosed [UAC bypass](https://github.com/R41N3RZUF477/QuickAssist_UAC_Bypass) using the Quick Assist UI Access application. This API looked interesting so I thought I should take a closer look.

I typically start by reading the documentation for an API I don’t know about, assuming it’s documented at all. It can give you an idea of how long the API has existed as well as its security properties. The documentation’s remarks contain the following three statements that I thought were interesting:

_If the caller has UIAccess, however, they can use a windows hook to inject code into the target process, and from within the target process, send a handle back to the caller._

_GetProcessHandleFromHwnd is a convenience function that uses this technique to obtain the handle of the process that owns the specified HWND._

_Note that it only succeeds in cases where the caller and target process are running as the same user._

The interesting thing about these statements is none of them are completely true. Firstly as the previous blog post outlined it’s not sufficient to have UI Access enabled to use windows hooks, you need to have the same or greater integrity level as the target process. Secondly, if you go and look at how `GetProcessHandleFromHwnd` is implemented in Windows 11 it’s a Win32k kernel function which opens the process directly, not using windows hooks. And finally, the fact that the Quick Assist bypass which uses the API still works with Administrator Protection means the processes can be running as different users.

Of course some of the factual inaccuracies might be changes made to UAC and UI Access over the years since Vista was released. Therefore I thought it’d be interesting to do a quick bit of code archaeology to see how this API has changed over the years and perhaps find some interesting behaviors.

## The First Version

The first version of the API exists in Vista, implemented in the `oleacc.dll` library. The documentation claims it was supported back in Windows XP, but that makes little sense for what the API was designed for. Checking a copy of the library from XP SP3 doesn’t show the API, so we can assume the documentation is incorrect. The API first tries to open the process directly, but if that fails it’ll use a windows hook exactly as the documentation described.

The `oleacc.dll` library with the hook will be loaded into the process associated with the window using the `SetWindowsHookEx` API and specifying the thread ID parameter. However it still won’t do anything until a custom window message, `WM_OLEACC_HOOK` is sent to the window. The hook function is roughly as follows (I’ve removed error checking):

```
void HandleHookMessage(CWPSTRUCT *cwp) {
  UINT msg = RegisterWindowMessage(L"WM_OLEACC_HOOK");
  if (cwp->message != msg)
	return;
  WCHAR name[64];
  wParam = cwp->wParam;
  StringCchPrintf(name, _countof(name),
                   L"OLEACC_HOOK_SHMEM_%d_%d", wParam,
                   cwp->lParam);
  HANDLE mapping = OpenFileMapping(FILE_MAP_READ |
                                   FILE_MAP_WRITE, FALSE,
                                   name);
  DWORD* buffer = (DWORD*)MapViewOfFile(mapping,
           FILE_MAP_READ | FILE_MAP_WRITE,
		0, 0, sizeof(DWORD));
  HANDLE caller = OpenProcess(PROCESS_DUP_HANDLE, FALSE,
                              cwp->wParam);
  HANDLE current = OpenProcess(PROCESS_DUP_HANDLE |
			  PROCESS_VM_OPERATION | PROCESS_VM_READ |
			  PROCESS_VM_WRITE | SYNCHRONIZE,
                   FALSE, GetCurrentProcessId());
  HANDLE dup;
  DuplicateHandle(CurrentProcess, current, caller, &dup,
                  0, 0, DUPLICATE_SAME_ACCESS);
  InterlockedExchange(buffer, (DWORD)dup);
  // Cleanup handles etc.
}
```

The message parameters are the process ID of the caller, who wants to open the process handle and an incrementing counter. These parameters are used to open a named memory section to transfer the duplicated handle value back to the caller. A copy of the current process handle is then opened with a limited set of access rights and duplicated to the caller. Finally the handle value is copied into the shared memory and the message handler returns. The caller of the API can now pick up the duplicated handle and use it as desired.

This code might explain a few additional things about the API documentation. If the two processes are running as different users it’s possible that the target process won’t be able to open the caller for `PROCESS_DUP_HANDLE` access and the transfer will fail. While the API does set the integrity level of the shared memory it doesn’t set the DACL so that will also prevent it being opened by a different user. Of course if the target process was running as an administrator, like in the UAC case, it almost certainly will have access to both the caller process as well as the shared memory making this a moot point.

One minor change was made in Windows 7, the hook function was moved out of the main `oleacc.dll` library into its own binary, `oleacchooks.dll`. The hook function is exposed as ordinal 1 in the export table with no name. This DLL still exists on the latest version of Windows 11 even though the API has since moved into the kernel and there’s no longer any users.

## The Second Version

The second version of the API doesn’t appear until well into Windows 10’s lifetime, in version 1803. This version is where the API was moved into a Win32k kernel function. The kernel API is exposed as `NtUserGetWindowProcessHandle` from `win32kfull.sys`. It’s roughly implemented as follows:

```
HANDLE NtUserGetWindowProcessHandle(HWND hWnd,
                                    ACCESS_MASK DesiredAccess) {
  WND* wnd = ValidateHwnd(Wnd);
  if (!wnd) {
    return NULL;
  }
  THREADINFO* curr_thread =
                W32GetThreadWin32Thread(KeGetCurrentThread());
  THREADINFO* win_thread = wnd->Thread;;
  if (curr_thread->Desktop != win_thread->Desktop) {
     goto access_denied;
  }

  PROCESSINFO* win_process = win_thread->ppi;
  PROCESSINFO* curr_process = curr_thread->ppi;
  if (gbEnforceUIPI) {
    if (!CheckAccess(curr_process->UIPIInfo,
                     win_process->UIPIInfo)) {
      if (!curr_process->HasUiAccessFlag) {
        goto access_denied;
      }
    }
  }
  else if (win_thread->AuthId != curr_thread->AuthId) {
    goto access_denied;
  }
  if (win_thread->TIF_flags & (TIF_SYSTEMTHREAD |
                                TIF_CSRSSTHREAD)) {
    goto access_denied;
  }

  KPROCESS process = NULL;
  DWORD process_id = PsGetThreadProcessId(win_thread->KThread);
  PsLookupProcessByProcessId(process_id, &process);
  HANDLE handle = NULL;
  ObOpenObjectByPointer(process, 0, NULL, DesiredAccess,
    PsProcessType, KernelMode, &handle);
  return handle;

access_denied:
  UserSetLastError(ERROR_ACCESS_DENIED);
  return NULL;
}
```

One thing to note with the new API is it takes an `ACCESS_MASK` to specify what access the caller wants on the process handle. This is different from the old implementation where the access desired was a fixed value. The window handle is validated and used to lookup the Win32k `THREADINFO` structure for the associated thread and a check is made to ensure both the caller’s thread and the target window are on the same desktop.

We then get to the UIPI enforcement checks, first it checks the `gbEnforceUIPI` global variable. If UIPI is enabled it’ll call a `CheckAccess` method to see if the caller is permitted to access the process for the target window. If the check fails it’ll test if the caller has the UI Access flag enabled, if not the function will deny access, otherwise it’ll be allowed to continue. The access check is quite simple:

```
BOOLEAN CheckAccess(UIPI_INFO *Current, UIPI_INFO* Target) {
  if (Current->IntegrityLevel > Target->IntegrityLevel) {
    return TRUE;
  }

  if (Current->IntegrityLevel != Target->IntegrityLevel) {
    return FALSE;
  }

  if (Current->AppContainerNo != Target->AppContainerNo &&
      Current->AppContainerNo != -1 &&
      Target->AppContainerNo != -1) {
    return FALSE;
  }

  return TRUE:
}
```

If the caller’s integrity level is greater than the target’s, the check is passed immediately. If it’s less than the target’s then it fails immediately. However if the integrity level is the same it does a check to make sure if the processes are in an AppContainer sandbox and that they’re in the same one. If a process is not in an AppContainer sandbox the `AppContainerNo` value is set to -1. The check also ensures that this doesn’t allow a low integrity process access to an AppContainer process as there’s an existing check to prevent this happening via `OpenProcess`. If everything passes the check returns TRUE.

If UIPI is not enforced then the authentication IDs are compared. The function will only permit access if the caller is in the same logon session, which would mean if UIPI was disabled this wouldn’t permit accessing elevated UAC processes. The final check is whether the target thread is in the system (i.e. kernel) process or a CSRSS process. If they are then access is denied.

Finally, the target process is opened by its process ID by looking up the `KPROCESS` pointer then using `ObOpenObjectByPointer` to open a handle with the desired access. Crucially the access mode is set to `KernelMode`. This means that no access checks are performed on the process object.

One glaring security issue with this function is that the target process is opened without access checking for any access rights the caller wants. This is a problem as it allows any process with the same or higher integrity level to open any other process as long as it has at least one window.

This is a special problem for two process types, first is restricted token sandbox processes. While you might assume this wouldn’t be a big deal if two restricted token sandboxed processes running at the same integrity could access each other, that isn’t always the case. For example Chromium doesn’t allow renderers to open each other, and some renderers have more privilege that others for example if they’re rendering WebUI content. Fortunately at least in this case renderers run under win32k lockdown meaning they can’t create a window even if they wanted to.

The second is protected processes. If you open a handle to a protected process with the access mode set to `KernelMode` then it’ll be permitted completely bypassing the protection. You might not think a protected process would create a window, but it could be a message-only window such as to support COM which the code might not even realize it created.

However, even if the caller doesn’t have a suitable integrity level it’s sufficient to just have the UI Access flag enabled. This means that tricks such as my [token stealing attack](https://www.tiraniddo.dev/2019/02/accessing-access-tokens-for-uiaccess.html) would be sufficient to open any other process on the same desktop which created a window. This issue was reported to MSRC and fixed as [CVE-2023-41772](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-41772). The reporter was the same researcher [Sascha Mayer](https://github.com/R41N3RZUF477) who found the Quick Assist UI Access bypass that I mentioned earlier.

## The Third Version

This version’s goal was to fix CVE-2023-41772 and there are two major changes. First and most importantly, if the UIPI check fails, the function will still check for the UI Access flag being enabled. However, rather than permitting it to continue, it’ll force the call to `ObOpenObjectByPointer` to open a handle with the access mode set to `UserMode` rather than `KernelMode`.

Passing `UserMode` ensures that access checking is enabled. The end result is having the UI Access flag enabled doesn’t grant any additional privileges over calling the `NtOpenProcess` system call directly. Presumably it was left this way for compatibility reasons. However, this didn’t change the behavior when the caller’s integrity level is greater or equal to the target’s, the process object will still be opened with the access mode set to `KernelMode`. This means that when it comes to restricted token sandboxes or protected processes nothing has changed.

The second, less important change is that the desired access is now restricted to a limited set of access rights matching the original hook based implementation. The caller can only pass the following access to the function, `PROCESS_DUP_HANDLE`, `PROCESS_VM_OPERATION`, `PROCESS_VM_READ` and `PROCESS_VM_WRITE` otherwise access is denied. However this amount of access is more than sufficient to completely compromise the target process.

## The Latest Version

Windows 11 24H2 introduced two major changes to the behavior of `NtUserGetWindowProcessHandle`. First there is a change to the UIPI access check, let’s look at a code snippet:

```
BOOLEAN UIPrivilegeIsolation::CheckAccess(UIPI_INFO *Current, UIPI_INFO* Target) {
  if (!Feature_UIPIAlwaysOn_IsEnabled() &&
      !UIPrivilegeIsolation::fEnforceUIPI) {
    return TRUE;
  }

  if (Target->ProcessProtection != 0 &&
     (Target->ProcessProtection != Current->Protection)) {
    return FALSE;
  }

  if (Current->IntegrityLevel > Target->IntegrityLevel) {
    return TRUE;
  }
...
}
```

The change introduces a Window feature flag to force UIPI on all the time, previously it was possible to disable UIPI using a system configuration change. A feature flag allows Microsoft to run A/B testing on Windows systems; it likely means that they want to enable UIPI permanently in the future.

The kernel driver also captures the process protection as part of the UIPI information and does a check that either the target is unprotected or the caller has a matching protection level. This stops the previous attack that allows `NtUserGetWindowProcessHandle` from opening a protected process.

One weakness in this check is it doesn’t use the comparison that the kernel uses to determine whether a protected level supersedes another. While that’s good in a way, there is a slight mistake. There’s a PPL App level that’s designed so that other processes at the same level can’t open one another. This behavior is presumably because the PPL App level was designed to be used by third party applications from the Windows Store. The implemented check would allow one PPL App process to open another, of course you’d still need to get code execution in a PPL App process to begin with so this doesn’t seem a major issue.

It’s important to note that the protection check is ignored if UIPI is disabled at a system level. Therefore if you’re willing to reboot the system and have administrator access you can disable UIPI by setting an `EnforceUIPI` DWORD registry value with the value of 0 inside the key `HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System`. You might also need to disable the `UIPIAlwaysOn` feature flag, you can do that using a tool like [ViVe](https://github.com/thebookisclosed/ViVe) and running the command `ViveTool.exe /disable /id:56625134` as an administrator and rebooting the machine.

The second major change is in `NtUserGetWindowProcessHandle`. The function now has two paths controlled by a feature flag `ResponsiblePid`. If the feature flag is disabled it takes the old path, but if it’s enabled it calls a new function `GetWindowProcessHandleUnsafe`. Ironically, contrary to the name this seems to be a safer version of the API.

The big change here is that to open a process the caller must have the UI Access flag enabled. Calling the API without the UI Access flag will give an access denied error. Also if you disable UIPI at the system level the API will also return access denied, it won’t fall back to an insecure mode of operation. At least on my 25H2 VM the `ResponsiblePid` feature flag is always enabled, but I could just be subject to A/B testing.

To open the process with `KernelMode` access you’ll still need to pass the UIPI check. As you can’t short circuit the check by disabling enforcement; this blocks opening protected processes. Therefore on the latest versions of Windows 11 to access a protected process, not only do you need to disable UIPI, and the `UIPIAlwaysOn` feature flag but also the `ResponsiblePid` feature flag to access the old implementation. The `ResponsiblePid` feature flag ID is `56032228` if you want to disable it with ViVe. This of course requires administrator access and rebooting the machine, it might just be easier to load a kernel driver.

## Hijacking a TCB level Protected Process

Assuming you’re still running Windows 10 (where this will likely be a forever bug), a pre-24H2 Windows 11 (23H2 Enterprise/Education is still supported until November 2026) or have fully disabled UIPI, we can now `GetProcessHandleFromHwnd` to compromise a protected process.

Ideally we want to get the highest level, `Protected TCB` to allow us to then open any other user process on the system regardless of the protection state. How do we get a process running at `Protected TCB` level to create a window we can use to open the process handle? I’ve already described how to do this in a previous [blog post](https://googleprojectzero.blogspot.com/2018/11/) back in 2018 on hijacking a protected process through the use of the COM `IRundown` interface.

Specifically it was possible to force `WerFaultSecure.exe` running at `Protected TCB` level to initialize a COM [single-threaded apartment (STA)](https://learn.microsoft.com/en-us/windows/win32/com/single-threaded-apartments). This allowed access to the `IRundown` interface, but more importantly for our purposes a STA also sets up a message only window with the `OleMainThreadWndClass` class, which is used for posting calls back to the apartment thread.

However it turns out even easier if we no longer need to force COM to initialize. `WerSecureFault.exe` will create a number of windows automatically during normal operation. First you need to run the process at the protected level in “upload” mode. Using the following command line:

`WerFaultSecure.exe -u -p {PID} -ip {PARENT_PID} -s {SECTION_HANDLE}`

Replace `PID` with the process ID of a dummy process to debug, `PARENT_PID` with your current process ID and `SECTION_HANDLE` is a handle to a shared memory section containing the following 32 bit integers, `0xF8`, `PID` and `TID` where PID and TID are the process ID and thread ID of the dummy debug process. This section handle must be inherited into the new process at creation time.

Next you need to find the created window, but that’s easy. Just enumerate windows using the [FindWindowEx](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-findwindowexw) API. For each window you can lookup the PID using [GetWindowThreadProcessId](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindowthreadprocessid) and match it against the created protected process.You might need to use something like an opportunistic lock to suspend the `WerFaultSecure.exe` process after it has created the window to give you time to enumerate them.

The final step is to call `GetProcessHandleFromHwnd` with the found window handle and you should get a process handle back with `PROCESS_DUP_HANDLE, PROCESS_VM_OPERATION, PROCESS_VM_READ, PROCESS_VM_WRITE, PROCESS_QUERY_LIMITED_INFORMATION` access. Typically with this access I’d duplicate a copy of the current process pseudo handle to get a full access handle. However due to the way protected processes work this will fail, as the protection checks cover both opening the process directly and duplicating the handle.

Therefore, this is all the access you’re going to get. While you can’t just create a new thread in the process, it gives you sufficient access to the process to allocate and modify executable memory so a simple attack would be to write some shell code into the process and modify an existing jump to execute the code. I’ll leave the final exploitation as an exercise for the reader. Alternatively Sascha Mayer has [published a PoC](https://github.com/R41N3RZUF477/PPLwindow) after I had [posted a screenshot](https://infosec.exchange/@tiraniddo/115539156769921108) of my version’s console output that you can play with instead.

## Conclusions

In conclusion the `GetProcessHandleFromHwnd` function is quite interesting in how it’s evolved over the years. The first version using windows hooks was actually secure against accessing protected processes as you can’t duplicate a process handle with access rights such as `PROCESS_VM_READ` from a protected process to a non-protected process. However it was decided it’d be better to do it all in kernel mode, but the check for protected processes was forgotten.

Finally in Windows 11 24H2, along with a general shake up of UIPI this seems to be fixed and the function is also no longer quite so dangerous. Time will tell if at least some of the changes, like making UIPI permanent, come to pass.