---
source: daniel-miessler
source_url: https://danielmiessler.com/blog/when-will-windows-be-ready-for-the-desktop
title: "When Will Windows Be Ready For The Desktop? | Daniel Miessler"
description: "You’d think certain things would come second nature to a major OS — things like network connection handling or returning to full functionality when"
---

You’d think certain things would come second nature to a major OS — things like network connection handling or returning to full functionality when coming out of standby. Well, with Windows XP these things haven’t quite happened yet.

I connect to a lot of network shares and FTP sites in my line of work, and while doing so yesterday I had an epiphany — *Windows sucks horribly at both.* Sure, if you happen to connect when the resource is working perfectly and there’s nothing wrong with the network, you have a decent chance of success. But if you make the mistake of trying to connect to a resource that has issues, or while the network is acting funky…

For anyone who doesn’t have experience with this, let me tell you what happens. You get the hourglass cursor of death and you lose all control of the explorer window you’re working in. All of it. It’s gone. The window just freezes. This could go on for minutes, hours, or days, by the way. And I understand — I really do. It’s only been **10 %&@#*! years** since Windows 95 came out, so I can’t expect Microsoft, a company with mere **billions** to spend on R&D, to to be able to hash this out just yet. Oh, and god forbid you do the logical thing and close the window. What happens then?

*Explorer.exe eats itself.* Yeah, that’s over a decade of Windows development being raped by an unresponsive network resource. It [makes me sad](http://www.mwscomp.com/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=when-will-windows-be-ready-for-the-desktop) >.

Look, I’m a novice when it comes to programming, but I do understand a key concept called exception handling. It basically means anticipating bad things happening and perparing for them. An example of bad exception handling would be a person who tries to buy an ice cream cone, finds out the store is closed, and commits Sepuku in a fit of frustration. That’s not a good way to handle a lack of ice cream, and restarting the GUI is not a good way to handle someone clicking the close button in an explorer window.

Then you have the standby and hibernate functions. They’re pretty standard — you are in the middle of something and want to stop for a bit and resume your work later without completely shuting down. Unfortunately, in Windows I find it actually **saves** time if you just go ahead and restart the damn computer. Opening your laptop’s screen only to find that your apps are laughing at you is *not* my idea of a good time.

So here’s the thing — I’m actually an MCSE and I do like a lot of what XP offers. I am not upset about these things because they existed; I’m upset because they **still exist**. It’s been 10 years guys…can we have windows not freeze when network resources aren’t available? Can we get a standby function that works properly? Apple/OS X figured it out on the first try. I’m left wondering why is this stuff is still a problem for Microsoft’s flagship OS.

Anyway, until they can get it all sorted I’m going to have to recommend [OS X](https://www.apple.com/macos/catalina/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=when-will-windows-be-ready-for-the-desktop) > for the desktop. Windows just doesn’t seem ready for the bigtime yet. But who knows, another 10 years and they might have it all ironed out. I hear they’re getting [tabbed browsing](https://www.mozilla.org/en-US/firefox/?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=when-will-windows-be-ready-for-the-desktop) > and virtual folders in 2006.