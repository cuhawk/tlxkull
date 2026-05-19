---
source: daniel-miessler
source_url: https://danielmiessler.com/blog/windowsfilesharing
title: "Windows File Sharing: Facing the Mystery | Daniel Miessler"
description: "For one reason or another, there is quite a bit of confusion surrounding the technologies that allow File Sharing to take place on a Windows machine. The hodgep"
---

Of course, nearly everyone is familiar with one main concept — the well-worn and widely known view that Windows file sharing services are potentially very dangerous. Steve Gibson and [his website](https://www.grc.com/intro.htm?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=windows-file-sharing-facing-the-mystery) > can be credited mostly for this becoming largely common knowledge. Unfortunately, however, the fact that "it’s bad" is about the extent of most people’s knowledge of the subject. As a friendly test, see if you know the answers to the questions below:

What’s the difference between using Windows 9x and Windows 2000/XP file sharing?

Which port(s) handle(s) file transfers on Windows 2000/XP systems?

Does Windows XP use NetBIOS to transfer files?

If you disable NetBIOS over TCP/IP on a 2000/XP box, can people still connect to your shares?

What happens if you block access to port TCP/139 on an XP machine?

These should be simple questions for anyone who deals with Windows in an administrator role, but unfortunately they are not. In fact, I’d be willing to bet that less than a quarter of Windows admins can confidently answer all five questions. In this short article, I intend to get readers up to speed on the basics of this highly critical area of knowledge. Often times, knowing the *how and why* makes all the difference when it comes to making sound security decisions.

As with many disciplines, the best way to start is with a bit of history. Before going into how file sharing is handled on the current generation of Windows operating systems, let’s take a look at how it was handled previously.

The beginning starts with a protocol called [NetBIOS](https://en.wikipedia.org/wiki/Netbios?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=windows-file-sharing-facing-the-mystery) >. Originally pushed by IBM, it was put together for the purpose of sharing information between a very limited number of machines on a LAN. Early on, NetBIOS ran on a number of protocols, to include DECnet, and it’s important to note that it was *not* designed to scale to large organizations. Unfortunately, once Microsoft released its products based on it, and computers became a crucial part of the business world, NetBIOS became the backbone of file sharing on business networks everywhere.

In Windows 9x (Windows 95, 98, and ME), the primary ports for sharing resources were 135, 137, 138, and 139. Below we take a look at each:

*TCP/135 – RPC*: This port is potentially quite dangerous due to what "RPC" actually stands for. [Remote Procedure Calls](https://en.wikipedia.org/wiki/RPC?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=windows-file-sharing-facing-the-mystery) > are requests from one machine to another for service. The RPC service acts as something of a facilitator, or go-between, between the client making the request and the machine being asked for service, i.e. a request is made to this "end-point mapper service" and then a port is allocated dynamically to the service being requested. This is similar to the RPC functionality found in the Unix world, and although it’s not technically a "file sharing" port, it ties heavily into Windows networking in general.

*UDP/137 – Netbios Name Service*: This port is used to attain name resolution for Netbios. Think of it as Netbios’s version of [DNS](https://en.wikipedia.org/wiki/Dns?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=windows-file-sharing-facing-the-mystery) > or [ARP](https://en.wikipedia.org/wiki/Address_Resolution_Protocol?utm_source=danielmiessler.com&utm_medium=newsletter&utm_campaign=windows-file-sharing-facing-the-mystery) >. It’s simply a way to use something you have, make a query, and get something you want in return. For NetBIOS it’s from a NetBIOS name to an IP, for DNS it’s a DNS name to IP, and for ARP it’s from IP to hardware address.

*UDP/138 – NetBIOS Datagram Service*: This port primarily allows the SMB browser service to populate the browse lists seen when using "Network Neighborhood".

*TCP/139 – NetBIOS Session Service*: This is perhaps the most known Windows port of all, as it is used to transfer files over TCP. This is both the port that NULL Sessions are established over and the port that file and printer sharing takes place on. If you are considering restricting access to ports on your Windows machine, this one needs to be on the top of the list.

NetBIOS was benign enough initially because they were bound to a protocol called Netbeui. NetBIOS was somewhat harmless when it ran over Netbeui because the protocol is limited to local networks. It couldn’t cross routers, and therefore couldn’t cross the Internet. For this reason, any problems associated with file sharing while running Netbeui were relatively limited.

This all changed when Microsoft started binding NetBIOS to TCP/IP — a system referred to as NBT. What this did was take a potentially dangerous but hobbled system (NetBIOS) and gave it wings. Now, instead of just having to worry about someone in the next cube gaining information about your system and/or connecting to your file shares, you now have to worry about someone in New Jersey, Russia, or China doing the same thing.

Essentially, if the interface that connected you to the Internet had both TCP/IP and File and Print sharing on it, and you didn’t have a decent password configured, you were in line to get scanned and pillaged at will by anyone on the Internet.

Ok, so what’s File and Print Sharing? Where does that fit in? Good question. File and Print Sharing is little more than a service that enables file/folder and print shares to be made available to clients. It’s that simple. Think of it as a daemon that runs on a machine — similar to a web or mail server.

Remember, daemons aren’t useful unless requests can make it to them. That’s where SMB over TCP (or in the 9x world — NetBIOS over Netbeui or TCP/IP) come in. They are the means of getting requests over the network to the "server" machine, i.e. the box that has a folder or a printer shared out.

Basically, two things are needed in order for there to be a successful file transfer, 1) a transport allowing a client to make it to the machine in question, and 2) the machine to be listening for requests while it has shares available. It’s important to understand these two pieces of the puzzle and where each technology fits.

Steve Gibson’s site, while quite informative, sensationalized the risk to some degree. All one needed to do to keep from sharing files over the Internet is unbind File and Print sharing from the TCP/IP protocol within network properties for the adapter that faces the outside. This could be done while leaving the binding intact for the *internal* adapter(s) so that you could benefit from file sharing on the internal, trusted network while having it disabled for the untrusted one(s).

The bits about disabling the Client For Microsoft Networks and such were simply over the top. Aptly enough, the "**Client** For Microsoft Networks" is nothing more than a *client* (hence the name). Disabling it had nothing to do with whether or not the *server* portion of File Sharing was enabled (File and Print Sharing).

For most of us, Windows 9x is thankfully ancient history. The vast majority of us deal with Windows 2000 and XP these days, and the way these versions of Windows handle File Sharing is significantly different.

First off, the big difference that many notice is the use of port TCP/445 vs. the ports in the 130 range. This change was part of a new Microsoft paradigm designed to eliminate the dependency on NetBIOS. In fact, one can completely disable NetBIOS over TCP/IP on a Windows 2000/XP machine since these new operating systems (via TCP/445) have SMB riding *directly* on top of TCP rather than on NetBIOS. Microsoft calls this the "direct hosting" of SMB. This enhancement allowed for a few benefits, such as less clutter in the protocol stack, a lack of NetBIOS broadcasts, and the ability standardize on DNS entirely for name resolution.

As can be expected, most of the functions taken care of by ports 135-139 when NetBIOS was used are now taken care of by the single port 445. This means that not only file and print sharing take place over 445, but also network browsing functionality and RPC.

*Old vs. New*

When connecting to a Windows 2000/XP machine that has both NetBIOS over TCP *and* direct hosting enabled (from a client machine that’s also using them), *both* types of connectivity will be attempted. The service responding first will be accepted and continued, i.e. if NetBIOS responds first then an RST will be sent to TCP/445, and vice versa.

Ok, now that we’ve covered a few different topics here, let’s touch on some key points:

File and Print Sharing is a completely different beast than NetBIOS or NetBIOS over TCP/IP. To be clear, you can disable the latter and still use the former if you have it bound to a protocol such as Netbeui. If you disable File and Print Sharing, however, then it doesn’t matter what transport gets you to the box, you still won’t be able to access shares on it.

Windows 9x used NetBIOS (via ports 137, 138, and 139) to resolve resource names and facilitate connecting to them — whether that was via the local network only (Netbeui) or WAN-wide (NBT).

Windows 2000/XP supports the NetBIOS system as well, but prefers the new method which uses TCP/445 to implement SMB directly over TCP. You can disable NBT for these platforms and still maintain virtually identical functionality using this "direct hosting" paradigm.

One of the major advantages of going to the "direct hosting" system instead of NetBIOS is the standardization on DNS for name resolution. Resolving resource names using NetBIOS names was chatty (broadcast-based) and lacked scalability. DNS is a universally accepted, hierarchical standard that scales all the way to networks the size of the Internet.

Due to the consolidation of many of the NetBIOS functions into a single port (445), this port is critical to many Windows 2000/XP operations. It’s imperative that access to this port is limited to trusted hosts and/or networks.

Well, that about sums it up. The goal here was to either refresh or bring up to speed anyone who deals with Windows networking on a daily basis. In the event that I’ve made an error, or you’d just like to comment, please feel free to contact me at [daniel@danielmiessler.com](mailto:daniel@danielmiessler.com) >.: