---
source: matt-brown
source_url: https://brownfinesecurity.com/blog/police-bodycam-data-to-china
title: "Intercepting Traffic from Police Bodycam App Sending Data to China - Brown Fine Security"
---

# Intercepting Traffic from Police Bodycam App Sending Data to China

Police body cameras are worn everyday by officers across America. These devices are used to gather evidence and provide accountability to all parties to a police encounter. The security and integrity of video data on these devices is critical to providing evidence that will stand up in a court of law.

For this reason, I decided to look into a cheap bodycam and see how it handles its data and where it sends it.

This particular camera only has an onboard WiFi hotspot in order to transfer data from the bodycam device to the Viidure mobile application. This mobile application then communicates to the cloud in various ways. We will explore some of those cloud communications and detail the kind of data being sent as well as the security of these communications.

## Wireshark Packet Capture

First I wanted to see what data is being transmitted by the mobile app back to its cloud servers.

I noticed TLS traffic going to the following domains:

- app-api.lufengzhe.com:9091
- api.map.baidu.com:443
- loc.map.baidu.com:443

The following information was obtained from the whois query on the `115.175.147.124`

IP address which was resolved from the `app-api.lufengzhe.com`

subdomain:

```
route: 115.175.128.0/19
descr: HUAWEI INTERNATIONAL PTE. LTD.
country: CN
origin: AS55990
mnt-by: MAINT-CNNIC-AP
last-modified: 2025-05-23T00:02:04Z
source: APNIC
```


So we have found that all the core communications from the mobile application are going to cloud servers hosted in China. We also notice the odd TLS port 9091 of the api domain.

## Performing the Man-in-the-Middle Attack

To perform a mitm attack on the TLS communications between the Viidure mobile application and its cloud servers we will use [mitmrouter](https://github.com/nmatt0/mitmrouter). This is a toolset I created to streamline testing of mitm-style attacks on network communications.

Other than the default mitmrouter config I set the following iptables rules:

```
sudo iptables -t nat -A PREROUTING -i $BR_IFACE -p tcp --dport 443 -j REDIRECT --to-ports 8081
sudo iptables -t nat -A PREROUTING -i $BR_IFACE -p tcp --dport 9091 -j REDIRECT --to-ports 8081
```


Then I ran [mitmdump](https://www.mitmproxy.org/) on port 8081 in upstream mode with it forwarding to Caido running on port 8080.

```
mitmdump --mode upstream:http://127.0.0.1:8080 --showhost -p 8081 -k
```


This chain of tools will attempt to forge a server certificate to look like the Chinese cloud server to the Viidure mobile application. Because the mobile app is not properly validating the TLS server certificate, it insecurely connects to our mitmproxy setup and we see the content of the HTTP communications in Caido.

Probably one of the more concerning HTTP messages is this one logging my phone IMEI (used to identify and track devices on mobile networks) and email address:

```
POST /iot/api/v1/version/check HTTP/1.1
Accept-Encoding: gzip
srapi_imei: 17562212185897060
srapi_time: 1757047550015
srapi_sver: 1
srapi_sign: 1139c08067a452f23fae03c800690eec
Content-Type: application/json
User-Agent: Dalvik/2.1.0 (Linux; U; Android 16; Pixel 7 Build/BP2A.250605.031.A2)
Host: app-api.lufengzhe.com:9091
Connection: Keep-Alive
Content-Length: 228
{
"data": [
{
"model": "6zhentan_android",
"region": "other",
"version": "v2.7.1.250712",
"useType": 1,
"imei": "17562212185897060"
}
],
"language": "en_US",
"appmodel": "6zhentan",
"osmodel": "android",
"country": "US",
"username": "<redacted>"
}
```


This traffic interception would be concerning for any mobile application, but its especially worrying given the sensitive nature of the video data being handled in this case.

### Need IoT Security Expertise?

Brown Fine Security provides expert IoT penetration testing to help secure your connected devices. From hardware analysis to cloud API testing, we uncover vulnerabilities before attackers do.

[Get a Free Consultation](/contact)

### Want to Learn IoT Hacking?

Ready to break into IoT security? Our hands-on training courses teach real-world hardware hacking, firmware analysis, and IoT exploitation techniques used by professional pentesters.

[Explore Training Courses](https://training.brownfinesecurity.com/)