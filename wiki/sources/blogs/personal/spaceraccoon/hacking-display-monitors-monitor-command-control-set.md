---
source: spaceraccoon
source_url: https://spaceraccoon.dev/hacking-display-monitors-monitor-command-control-set/
title: "Hacking HP Display Monitors via Monitor Control Command Set (CVE-2023-5449) | Spaceraccoon's Blog"
published: 2023-10-31T05:01:06+00:00
description: "Have you ever wondered how display monitor software can change various settings like brightness over a simple display cable? As it turns out, this relies on a standard protocol that can lead to interesting vulnerabilities. Here’s how I found and exploited CVE-2023-5449 in dozens of HP display monitors."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Hacking HP Display Monitors via Monitor Control Command Set (CVE-2023-5449)

Oct 31, 2023
·

1702 words

·

8 minute read


Have you ever wondered how display monitor software can change various settings like brightness over a simple display cable? As it turns out, this relies on a standard protocol that can lead to interesting vulnerabilities. Here’s how I found and exploited CVE-2023-5449 in dozens of HP display monitors.

# Display Monitor Software [🔗](https://spaceraccoon.dev/hacking-display-monitors-monitor-command-control-set/\#display-monitor-software)

One day, I connected my computer to a HP display. Annoyingly, I noticed that Windows auto-installed the HP Display Center software without any prompts, likely because it was a trusted Windows Store application. Later, I noticed that even when I was using a monitor from a different manufacturer, HP Display Center could still interact and control certain basic settings like brightness.

Curious, I decided to take a look at the internals of the software. Fortunately, it was a .NET Framework application that could be easily reversed into close-to-original C# code. Within the code, I noticed a few interesting functions that were called whenever a display setting was changed, like `ExecuteSetVcp`. In turn, these functions called lower-level Windows APIs that presumably handled the actually hardware-level communication.

A few searches later, I found out that `Vcp` referred to Virtual Control Panel. Within the Monitor Control Command Set (MCCS) protocol, each VCP corresponds to a specific monitor setting, such as a brightness VCP, contrast VCP, and so on. But first, I needed to understand MCCS better.

# Monitor Control Command Set (MCCS) [🔗](https://spaceraccoon.dev/hacking-display-monitors-monitor-command-control-set/\#monitor-control-command-set-mccs)

The reason why we can use display monitors fairly interchangeably without having to change cables, drivers, and so on is because of various standards developed by the Video Electronics Standards Association (VESA). Yes, that VESA is behind the VESA mount, but beyond physical standards VESA also specifies firmware and software standards like MCCS.

As the name suggests, MCCS specifies how hosts connected to a display monitor can control the monitor through various commands. MCCS runs over the lower-level Display Data Channel Command Interface (DDC/CI) standard, which can be implemented on various cables like HDMI.

In particular, MCCS defines three types of VCP controls:

1. Continuous: Values from 0 to a specified maximum, such as brightness (0 to 100).
2. Non-continuous: Values within a limited set (in other words an enum/boolean), such as color preset.
3. Table: Blocks of data (custom structs). For example, the “Source Timing Mode” VCP has a 5 byte data structure: flags for DMT timing modes (0), flags for CEA DTV timing modes (1), CVT descriptor bytes (2-4). Yes, that’s a lot of acronyms I did not bother to look up.

In addition, these controls can be read-only, write-only, or read-write (this will be important later). You can check published MCCS documents to get the full list of VCP codes.

To set a writeable VCP control, Windows provides the following API:

```csharp
_BOOL SetVCPFeature(
  [in] HANDLE hMonitor,     // handle to display monitor instance
  [in] BYTE   bVCPCode,     // VCP control code
  [in] DWORD  dwNewValue    // New VCP control code value
);
```

Although MCCS already pre-defines many common VCP controls from control code 0x00 to 0xDF, it also leaves the door open for manufacturer-specific controls:

> The 32 control codes E0h through FFh have been allocated to allow manufacturers to issue their own specific controls either where the defined VCP codes do not provide a required function or where the added function is considered proprietary.

> Caution: Use of these codes has the risk of causing incompatibility and / or unpredictable behavior. Example: Consider the case when two display manufacturers choose to use the same ‘manufacturer VCP code’ for different functions (or different implementations of the same function) but the user chooses not to use the specific software support supplied or recommended for his particular display – he may use a general purpose MCCS support application, native support built into the operating system or a MCCS support application intended for a different display model. In this case, the resulting behavior is unpredictable, ranging from no support for the function which uses a ‘manufacturer VCP code’ to incorrect control and adjustment of the function. In all cases this will likely result in an annoyed user and a service call, in extreme cases it may result in a situation where the user cannot return the display to normal operation.

> **It is recommended that these codes are used with caution and only when strictly necessary.**

Despite this dire warning, as I found out with the [iCalendar standard](https://spaceraccoon.dev/exploiting-icalendar-properties-enterprise-applications/), vendors tend to err on the other side of caution in order to differentiate their products built on a common standard. For example, you will find display monitors that go far beyond simply showing nice pictures - they can include integrated webcams, microphones, and more.

Some of this information supported by a monitor is sent via a **capability string** during initialization that allows software to understand which VCP controls are supported by that monitor.

# HP’s Proprietary VCP Codes [🔗](https://spaceraccoon.dev/hacking-display-monitors-monitor-command-control-set/\#hps-proprietary-vcp-codes)

You may notice that with only 16 different VCP codes allocated to manufacturer-specific controls, there is not actually a lot of space to add new controls.

However, HP had an ingenious solution for this.

For continuous controls, their codes followed the usual paradigm of `<VCP CODE> <VALUE>`.

However, this is a waste of bytes for non-continuous controls, since the enum typically only takes a handful of possible values. For example, there may be a few color profiles that correspond to specific byte values: Gaming (0), Movie (1), Warm (2), Cool (3). However, a byte can take up to 256 values.

Instead, for proprietary non-continuous controls, HP created sub-VCP codes contained within a catch-all VCP code. When setting this VCP control, the values could then range from `SetColorProfileGaming` (0), `SetColorProfileMovie` (1), `SetColorProfileWarm` (2), `SetColorProfileCool` (3), then include **additional** non-continuous controls like `SetScreenOrientation0` (4), `SetScreenOrientation90` (5), `SetScreenOrientation180` (6), and so on. This way, rather than X number of non-continuous controls taking up X precious proprietary control codes, they can take up only 1.

## Theft Deterrence [🔗](https://spaceraccoon.dev/hacking-display-monitors-monitor-command-control-set/\#theft-deterrence)

It was difficult to reverse these codes from the firmware, which largely contained monitor chipset-specific (Genesis) instructions. Some [research](https://github.com/RedBalloonShenanigans/MonitorDarkly) by Red Balloon Security has been done previously on a proprietary “GProbe” protocol that ran over DDC as well that convinced me not to take that route.

Instead, thanks to the ready availability of display monitor control software, it was far easier to reverse the clients and figure out the functionality of VCP control codes from the function names, dynamic debugging while using the GUI, and logging messages.

One of the interesting features I noticed from the GUI was HP’s theft deterrence mechanism. Users can set a 4-to-6 digit PIN on the monitor such that if the monitor is stolen and connected to a new computer without entering the PIN, after 5 minutes the screen will dim and show a message “Theft Mode is Enabled”.

To support this feature, HP implements the following control commands:

1. TheftTimeOut (251): Continuous value that denotes the time in minutes before the anti-theft mechanism is triggered if no PIN is entered.
2. TheftLowPin (252): Continuous value that denotes the low 3 digits of the PIN
3. TheftHighPin (253): Continuous value that denotes the high 3 digits of the PIN.
4. TheftDeterrence (250): Non-continuous value that denotes the status of the theft deterrence mechanism. Can be TheftDisabled (0), TheftEnabledConsumer (1), or TheftEnabledEnterPrise (2).

When turning on anti-theft deterrence, the HP Display Center software takes in user input for the PIN, then sends the following write MCCS commands:

1. TheftLowPin = LowPin: Monitor sets LowPin.
2. TheftHighPin = HighPin: Monitor sets HighPin.
3. TheftDeterrence = TheftEnabledConsumer: Monitor turns on anti-theft deterrence.

When turning off anti-theft deterrence, it sends the following write MCCS commands:

1. TheftLowPin = LowPin: Monitor checks LowPin.
2. TheftHighPin = HighPin: Monitor checks HighPin.
3. TheftDeterrence = TheftDisabled: If previous 2 steps were correctly checked, monitor turns off anti-theft deterrence.

On the firmware side, TheftDeterrence is correctly configured such that it is read-only (RO) when the monitor has not yet received correct TheftLowPin and TheftHighPin commands. Unfortunately, the TheftLowPin and TheftHighPin control command values are not set to write-only (WO) but are actually read and write (RW). This allows an attacker to actually read the values of the pin even when anti-theft deterrence has been triggered.

It is important to note that HP’s implementation interprets read and write rather loosely. For example, when attempting to unlock the monitor, pin values are sent using a write command, but these values do not actually overwrite the stored PIN values. It is simply that in order to send values over MCCS, a write command must be sent.

# MCCS Fuzzing and Exploitation [🔗](https://spaceraccoon.dev/hacking-display-monitors-monitor-command-control-set/\#mccs-fuzzing-and-exploitation)

Of course, in order to actually send the malicious series of control commands, you still need to use the low-level APIs to communicate with the monitor. It can be quite a hassle to custom code this in C++. Fortunately, some work has already been done in Rust via the `ddcset` project ( [https://github.com/arcnmx/ddcset-rs](https://github.com/arcnmx/ddcset-rs)) to make it easy to manipulate messages sent over DDC/CI. This is a good base to developer your own custom tooling and fuzzers as well.

For a simple bug like theft deterrence, this can be exploited by sending the messages directly.

1. Using HP Display Center software, go to Advanced tab and set the PIN to `123123` and enable anti-theft deterrence.
2. Plug the monitor into another computer. You have 5 minutes before the anti-theft deterrence is triggered.
3. Run `ddcset -b winapi getvcp 252` to read the TheftLowPin. It should return:

```fallback
Display on winapi:
        ID: Generic PnP Monitor
        Feature 0xfc = 123 / 65535
```

4. Run `ddcset -b winapi getvcp 253` to read the TheftHighPin. It should also return the same values.
5. This demonstrates that you have successfully read the PIN from a “stolen” monitor. If anti-theft deterrence is triggered, simply enter the leaked PIN using HP Display Center.

# Conclusion [🔗](https://spaceraccoon.dev/hacking-display-monitors-monitor-command-control-set/\#conclusion)

I coordinated disclosure with HP on [CVE-2023-5449](https://support.hp.com/us-en/document/ish_9438665-9438794-16/hpsbhf03871). It was interesting to observe how much more difficult patching hardware, especially specialized ones like display monitors, can be.

This simple vulnerability only scratches the surface of more interesting bugs that can be found in proprietary MCCS VCP controls, especially if table type values are used which are likelier to trigger memory corruption issues. As VESA warns, this can lead to permanent damage of monitors.

As display monitors add more features in both hardware and software like integrated webcams, I suspect we may begin to see more serious vulnerabilities emerge in this space.

[binary](https://spaceraccoon.dev/tags/binary) [desktop](https://spaceraccoon.dev/tags/desktop) [reverse engineering](https://spaceraccoon.dev/tags/reverse-engineering) [hardware](https://spaceraccoon.dev/tags/hardware)