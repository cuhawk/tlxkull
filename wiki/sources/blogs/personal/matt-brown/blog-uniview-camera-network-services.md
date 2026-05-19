---
source: matt-brown
source_url: https://brownfinesecurity.com/blog/uniview-camera-network-services
title: "Enterprise IoT Pentesting: Network Service Analysis - Brown Fine Security"
---

# Enterprise IoT Pentesting: Network Service Analysis

In the [last segment](/blog/cleartext-communications-to-univew-cloud-servers) of our Enterprise IoT Pentesting series, we analyzed the *data in transit* security on our Uniview SC-3243 commercial security camera.

Now we will look at the Network Services on our Enterprise IoT device for vulnerabilities.

## Network Service Enumeration

To discover what network services are running and accessible on our IoT device, we will use `nmap`

. `nmap`

is a popular network port scanning tool that allows us to enumerate all services that are running on a system which are accessible on the interface in question.

```
[nmatt@arch-dtop ~]$ sudo nmap -p- 192.168.100.26
Starting Nmap 7.97 ( https://nmap.org ) at 2025-09-14 23:29 -0400
Nmap scan report for 192.168.100.26
Host is up (0.00038s latency).
Not shown: 65533 closed tcp ports (reset)
PORT STATE SERVICE
80/tcp open http
554/tcp open rtsp
MAC Address: E4:F1:4C:77:66:08 (Private)
```


Above, we can see the use of `nmap`

with the `-p-`

flag which tells `nmap`

to scan all 65536 TCP ports. Since our Uniview device is on our local network this full port scan is feasible whereas if it were over a public network we might want to scan a more limited range.

Our port scan reveals that an HTTP web server is running on port 80 and a RTSP video streaming service is running on port 554.

But wait! We have a [UART root shell](/blog/bypassing-restricted-shell-on-uniview-security-camera) on the device! We have another way to discover what services are running on the device: `netstat`

.

Let's run `netstat`

to find out what network services are listening on TCP and UDP ports:

```
root@root:~$ netstat -antlp
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address Foreign Address State PID/Program name
tcp 0 0 127.0.0.1:54321 0.0.0.0:* LISTEN 936/mwareserver
tcp 0 0 127.0.0.1:41482 127.0.0.1:54053 ESTABLISHED 936/mwareserver
tcp 0 0 127.0.0.1:54053 127.0.0.1:41482 ESTABLISHED 936/mwareserver
tcp 0 0 :::554 :::* LISTEN 936/mwareserver
tcp 0 0 :::80 :::* LISTEN 936/mwareserver
root@root:~$ netstat -anulp
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address Foreign Address State PID/Program name
udp 0 0 127.0.0.1:2048 0.0.0.0:* 936/mwareserver
udp 0 0 192.168.1.13:39682 8.8.4.4:53 ESTABLISHED 936/mwareserver
udp 0 0 127.0.0.1:7001 0.0.0.0:* 936/mwareserver
udp 0 0 0.0.0.0:3702 0.0.0.0:* 936/mwareserver
udp 0 1408 192.168.1.13:55193 8.8.8.8:53 ESTABLISHED 936/mwareserver
```


Notice that `netstat`

gives us insights into UDP services that our `nmap`

scan did not. Now of course our `nmap`

scan didn't try to look for UDP services because by default it only scans for TCP ports. This has a lot to do with how TCP and UDP function. Because of the 3-way handshake that begins any TCP connection, enumerating TCP services over the network is inherently easier than UDP. UDP services generally do not respond unless a valid UDP payload is used.

Let's explicitly tell `nmap`

to look for that UDP service running on port 3702. We will also scan some other nearby UDP ports for comparison.

```
$ sudo nmap -p 3702-3710 -sU 192.168.100.26
Starting Nmap 7.97 ( https://nmap.org ) at 2025-09-19 09:53 -0400
Nmap scan report for 192.168.100.26
Host is up (0.00039s latency).
PORT STATE SERVICE
3702/udp open|filtered ws-discovery
3703/udp closed adobeserver-3
3704/udp closed adobeserver-4
3705/udp closed adobeserver-5
3706/udp closed rt-event
3707/udp closed rt-event-s
3708/udp closed sun-as-iiops
3709/udp closed ca-idms
3710/udp closed portgate-auth
MAC Address: E4:F1:4C:77:66:08 (Private)
Nmap done: 1 IP address (1 host up) scanned in 4.03 seconds
```


Notice that our open UDP port is declared to be "open|filtered". Why is that?

Let's take a look at a Wireshark capture to see what `nmap`

is doing under the hood.

We can see that for each UDP message sent to a port that is not open, our IoT device responds with an ICMP destination unreachable packet.

We don't receive such a packet for the message to port 3702 which is how `nmap`

determines that it *might* be open. But it could also be filtered by some firewall which is why `nmap`

is unable to be confident.

## ONVIF Enumeration

A quick Google search reveals that UDP port 3702 is used for the [WS-Discovery protocol](https://en.wikipedia.org/wiki/WS-Discovery). WS-Discovery is a multicast protocol that helps devices and applications discovery devices on a local network.

ONVIF, the Open Network Video Interface Forum, is an open industry standard that ensures interoperability among IP-based security products. ONVIF uses WS-Discovery as a method to allow client applications to automatically discovery ONVIF compadible devices on a local network.

Using the following python script, we can send a WS-Discovery Probe request to our Uniview device and observe the response:

```
#!/usr/bin/env python3
import socket
import time
import struct
import uuid
# WS-Discovery 1.0 Probe message
probe_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<soap-env:Envelope xmlns:soap-env="http://www.w3.org/2003/05/soap-envelope"
xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing">
<soap-env:Header>
<a:Action mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</a:Action>
<a:MessageID>{message_id}</a:MessageID>
<a:ReplyTo>
<a:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</a:Address>
</a:ReplyTo>
<a:To mustUnderstand="1">urn:schemas-xmlsoap-org:ws:2005:04:discovery</a:To>
</soap-env:Header>
<soap-env:Body>
<Probe xmlns="http://schemas.xmlsoap.org/ws/2005/04/discovery" />
</soap-env:Body>
</soap-env:Envelope>'''
# Hardcoded target
target_ip = "192.168.100.26"
target_port = 3702
# Generate unique message ID
message_id = f"urn:uuid:{uuid.uuid4()}"
message_xml = probe_xml.format(message_id=message_id)
message = message_xml.encode('utf-8')
print(f"Sending WS-Discovery Probe to {target_ip}:{target_port}")
print(f"Message ID: {message_id}")
# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to port 3702 to receive multicast responses
sock.bind(('', 3702))
# Join multicast group for responses
multicast_group = '239.255.255.250'
mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
# Send the probe message
sock.sendto(message, (target_ip, target_port))
print("Probe sent successfully")
# Set timeout and listen for responses
sock.settimeout(5)
start_time = time.time()
print("Listening for responses...")
responses_received = 0
while time.time() - start_time < 5:
data, addr = sock.recvfrom(4096)
responses_received += 1
print(f"\n--- Response {responses_received} from {addr[0]}:{addr[1]} ---")
response_str = data.decode('utf-8', errors='ignore')
print(response_str)
sock.close()
print(f"Received {responses_received} response(s) total")
```


The following output was received:

```
Sending WS-Discovery Probe to 192.168.100.26:3702
Message ID: urn:uuid:a6ab1bb7-7d49-418d-ba2a-a7f930a7dce7
Probe sent successfully
Listening for responses...
--- Response 1 from 192.168.100.26:44949 ---
<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope"
xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xop="http://www.w3.org/2004/08/xop/include"
xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing"
xmlns:tns="http://schemas.xmlsoap.org/ws/2005/04/discovery"
xmlns:dn="http://www.onvif.org/ver10/network/wsdl"
xmlns:tds="http://www.onvif.org/ver10/device/wsdl"
xmlns:wsa5="http://www.w3.org/2005/08/addressing">
<SOAP-ENV:Header>
<tns:AppSequence MessageNumber="10002" InstanceId="1"></tns:AppSequence>
<wsa:MessageID>10002</wsa:MessageID>
<wsa:RelatesTo>urn:uuid:a6ab1bb7-7d49-418d-ba2a-a7f930a7dce7</wsa:RelatesTo>
<wsa:To SOAP-ENV:mustUnderstand="true">http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:To>
<wsa:Action SOAP-ENV:mustUnderstand="true">http://schemas.xmlsoap.org/ws/2005/04/discovery/ProbeMatches</wsa:Action>
</SOAP-ENV:Header>
<SOAP-ENV:Body>
<tns:ProbeMatches>
<tns:ProbeMatch>
<wsa:EndpointReference>
<wsa:Address>urn:uuid:00010010-0001-1020-8000-e4f14c776608</wsa:Address>
</wsa:EndpointReference>
<tns:Types>dn:NetworkVideoTransmitter tds:Device</tns:Types>
<tns:Scopes>onvif://www.onvif.org/Profile/G onvif://www.onvif.org/Profile/Streaming onvif://www.onvif.org/Profile/T onvif://www.onvif.org/type/video_encoder onvif://www.onvif.org/type/audio_encoder onvif://www.onvif.org/max_resolution/2688*1520 onvif://www.onvif.org/register_status/offline onvif://www.onvif.org/register_server/0.0.0.0:5060 onvif://www.onvif.org/regist_id/34020000001320000001 onvif://www.onvif.org/type/IPC onvif://www.onvif.org/manufacturer/NONE onvif://www.onvif.org/VideoSourceNumber/1 onvif://www.onvif.org/version/GIPC-B6215.1.68.NB.240617 onvif://www.onvif.org/serial/210235UEDW3247000013 onvif://www.onvif.org/macaddr/e4f14c776608 onvif://www.onvif.org/hardware/SC-3243-IWPS-F28 onvif://www.onvif.org/location/ onvif://www.onvif.org/name/SC-3243-IWPS-F28 </tns:Scopes>
<tns:XAddrs>http://192.168.100.26:80/onvif/device_service</tns:XAddrs>
<tns:MetadataVersion>1</tns:MetadataVersion>
</tns:ProbeMatch>
</tns:ProbeMatches>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
```


This gives away a bunch of information about our device without authentication!

Information Gathered:

- Firmware Version: GIPC-B6215.1.68.NB.240617
- Device Serial Number: 210235UEDW3247000013
- Device MAC Address: e4f14c776608
- Device Model Number: SC-3243-IWPS-F28

We also get the ONVIF endpoint: http://192.168.100.26:80/onvif/device_service. This is the endpoint that we can attempt to send operation requests to in order to test the ONVIF interfaces.

## Embedded Web Application Testing

Now we will turn to the embedded HTTP application running on port 80.

This webserver on port 80 contains a GUI for local network management of the video device. This service was tested for various standard web vulnerabilities without any major findings. However, we will talk about a unique aspect of testing web applications hosted by IoT devices.

Most web pentests are black box assessments where the pentester does not have source code or access to the web server. But when a web application is hosted on an IoT device that all changes. With our [UART root shell](/blog/bypassing-restricted-shell-on-uniview-security-camera), we can see all files in the webroot and we can examine the web server and/or web application binary (they are often the same thing).

Let's use our root shell to see what files are in the webroot:

```
root@root:/www$ ls -l /www/
total 188
drwxrwxr-x 2 1001 1001 448 Jun 17 2024 ActiveX
drwxrwxr-x 2 1001 1001 1944 Jun 17 2024 LANG
-rw-rw-r-- 1 1001 1001 95473 Jun 17 2024 SoftwareLicense.txt
lrwxrwxrwx 1 root root 17 Dec 1 2011 Version.html -> /tmp/Version.html
drwxrwxr-x 2 1001 1001 232 Jun 17 2024 cgi-bin
-rw-rw-r-- 1 1001 1001 100 Jun 17 2024 config.xml
-rwxrwxr-x 1 1001 1001 1304 Jun 17 2024 daemon.cfg
lrwxrwxrwx 1 1001 1001 22 Jun 17 2024 device_cap.xml -> /config/device_cap.xml
lrwxrwxrwx 1 1001 1001 25 Jun 17 2024 fingerprint.htm -> ../../tmp/fingerprint.htm
-rw-rw-rw- 1 1001 1001 561 Jun 17 2024 index.htm
-rw-rw-r-- 1 1001 1001 709 Jun 17 2024 index_debugger.html
-rw-rw-rw- 1 1001 1001 1210 Jun 17 2024 index_error.htm
-rw-rw-r-- 1 1001 1001 2087 Jun 17 2024 index_skip.html
-rw-rw-rw- 1 1001 1001 1284 Jun 17 2024 index_softap.htm
-rw-rw-r-- 1 1001 1001 335 Jun 17 2024 lang_conversion.txt
lrwxrwxrwx 1 root root 19 Dec 1 2011 map_ports.html -> /tmp/map_ports.html
-rw-rw-r-- 1 1001 1001 70 Jun 17 2024 mongoose_http.conf
-rw-rw-r-- 1 1001 1001 112 Jun 17 2024 mongoose_https.conf
drwxrwxr-x 4 1001 1001 288 Jun 17 2024 page
drwxrwxr-x 6 1001 1001 416 Jun 17 2024 script
drwxrwxr-x 11 1001 1001 760 Jun 17 2024 skin
-rw-rw-r-- 1 1001 1001 51664 Jun 17 2024 static.tgz
```


With the following bash script we can confirm that all of these files can be accessed without authentication:

```
#!/bin/bash
BASE_URL="http://192.168.100.26"
FILES=(
"SoftwareLicense.txt"
"config.xml"
"daemon.cfg"
"index.htm"
"index_debugger.html"
"index_error.htm"
"index_skip.html"
"index_softap.htm"
"lang_conversion.txt"
"mongoose_http.conf"
"mongoose_https.conf"
"static.tgz"
)
for FILE in "${FILES[@]}"; do
curl -s -o /dev/null -w "Status: %{http_code} URL: %{url_effective}\n" "$BASE_URL/$FILE"
done
```


Script output:

```
Status: 200 URL: http://192.168.100.26/SoftwareLicense.txt
Status: 200 URL: http://192.168.100.26/config.xml
Status: 200 URL: http://192.168.100.26/daemon.cfg
Status: 200 URL: http://192.168.100.26/index.htm
Status: 200 URL: http://192.168.100.26/index_debugger.html
Status: 200 URL: http://192.168.100.26/index_error.htm
Status: 200 URL: http://192.168.100.26/index_skip.html
Status: 200 URL: http://192.168.100.26/index_softap.htm
Status: 200 URL: http://192.168.100.26/lang_conversion.txt
Status: 200 URL: http://192.168.100.26/mongoose_http.conf
Status: 200 URL: http://192.168.100.26/mongoose_https.conf
Status: 200 URL: http://192.168.100.26/static.tgz
```


One example of data leaks from these files are path disclosures:

```
root@root:/www$ cat daemon.cfg
...
mwareserver
{
.exec = reboot.sh
.path = "/tmp/bin/"
}
maintain
{
.exec = maintain &
.path = "/program/bin/"
}
root@root:/www$ cat mongoose_http.conf
# config mongoose WEB server
document_root /www/
listening_port 80
root@root:/www$ cat mongoose_https.conf
# config mongoose WEB server
document_root /www/
ssl_certificate /program/www/ssl_cert.pem
```


This is just a taste of the attack surface that exists on Enterprise IoT device network services!

### Need IoT Security Expertise?

Brown Fine Security provides expert IoT penetration testing to help secure your connected devices. From hardware analysis to cloud API testing, we uncover vulnerabilities before attackers do.

[Get a Free Consultation](/contact)

### Want to Learn IoT Hacking?

Ready to break into IoT security? Our hands-on training courses teach real-world hardware hacking, firmware analysis, and IoT exploitation techniques used by professional pentesters.

[Explore Training Courses](https://training.brownfinesecurity.com/)