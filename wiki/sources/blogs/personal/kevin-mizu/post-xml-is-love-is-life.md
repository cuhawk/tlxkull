---
source: kevin-mizu
source_url: https://mizu.re/post/xml-is-love-is-life
title: "XML is love, XML is life | mizu.re"
description: "XML is love, XML is life"
---

_keyboard\_arrow\_up_

title: XML is love, XML is life

date: Nov 27, 2021

tags: [Writeup](https://mizu.re/tag/Writeup) [DgHack](https://mizu.re/tag/DgHack) [Web](https://mizu.re/tag/Web)

# XML is love, XML is life

```
13 solves / 200 points
difficulty: Medium

Un administrateur du site a voulu jouer au développeur et a introduit une vulnérabilité dans le CMS ultra sécurisé WordPress.

Pouvez-vous retrouver cette vulnérabilité et exfiltrer le flag ?

url: http://web-vxslkw.inst.malicecyber.com/
```

For this challenge, as the name suggests, we have to exploit an XXE to get our way. With a first recon on the website, we could find several details that's indicating us where to go.

![accueil](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/accueil.png)

![commentaire](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/commentaire.png)

With those screens, It made obvious that we have to exploit the xmlrpc.php endpoint on the WordPress website. At this point, we can think about a lot of common WordPress exploits, but keep in mind that it's must be an implementation error as the post says. So, trying a simple XXE on xmlrpc.php gives us the following output:

![postman](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/postman.png)

![http_server](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/http_server.png)

Decoding the output:

![etc_passwd](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/etc_passwd.png)

Nice! We have exfiltrate /etc/passwd file using Error based XXE. Now, we need to dump more specific file to find what to do next. However, several issues make it very complicated:

- Maximum output for php ERROR
- Maximum size of an URL in the HTTP protocol

Yes, in fact, as you probably already see on the previous screen, we haven't exfiltrated the whole /etc/passwd file. Obviously, we need to be able to bypass this security to continue. After searching and reading a lot of docs, I found a way to exfiltrate files using FTP. The problem ? No one tool makes it easy to exploit and it would be very long to dump the whole site if needed. So, I decided to create a tool to do exactly this! (I won't explain much more about it on this writeups, I will release it on github and write an article about FTP exfiltration in a few days)

Exemple of usage:

![XXEfiltrator](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/xxefiltrator.png)

Well, now that we can dump everything, let's try to get the home page.

/var/www/html/index.php

![index_php](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/index_php.png)

As we can see, it uses /startup.sh file at startup.

/startup.sh

![startup_sh](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/startup_sh.png)

The script seems to add WordPress plugin using a zip file.

/admin-logs.zip

![admin_logs_zip](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/admin_logs_zip.png)

Now that we have the vulnerable plugin in local, we need to find a way to exploit it. Navigating inside all files, we could find those information.

/includes/utils.php

![utils_php](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/utils_php.png)

/public/class-admin-logs-public.php

![public_class_php](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/public_class_php.png)

As we can see, the plugin contains a read\_system\_logs function which can be used to interact with the fs. Moreover, the function seems to be very vulnerable to injection using ..././ instead of ../ to path transversal. The only problem that we face now, is that wordpress plugins can't be called directly.

![secu_wp_plug](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/secu_wp_plug.png)

Continue reading admin-logs plugin files, we can fin something very interesting. The read\_system\_logs function as been added to 'wp\_ajax\_nopriv' hook which permit us to call it directly using admin-ajax.php endpoint. (More information: [https://developer.wordpress.org/reference/hooks/wp\_ajax\_nopriv\_action/](https://developer.wordpress.org/reference/hooks/wp_ajax_nopriv_action/))

/includes/class-admin-logs.php

![class_php](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/class_php.png)

Going to " [http://web-vxslkw.inst.malicecyber.com/wp-admin/admin-ajax.php?action=read\_system\_logs&dir](http://web-vxslkw.inst.malicecyber.com/wp-admin/admin-ajax.php?action=read_system_logs&dir) =."

![localhost](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/localhost.png)

Obviously, we need can't use it without having localhost address, but using the XXE won't be difficult to pass.

Well, now that we have everything, let's use our XXE to flag this challenge.

ls /

![ls](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/ls.png)

cat /flag-103083938c29ed3d630e

![flag](https://mizu.re/articles/writeups/DgHack/web/xml-is-love-xml-is-life/images/flag.png)

Congratzzz!!

```
Flag: DGA{5d15975aabc37d088c6f594d927155d93ae57cdd}
```

[_keyboard\_arrow\_left_ How I was able to rick roll every users on root-me.org](https://mizu.re/post/how-i-was-able-to-rick-roll-every-users-on-root-me.org)

[Panid _keyboard\_arrow\_right_](https://mizu.re/post/panid)