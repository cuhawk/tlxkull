---
source: zlz-buerhaus
source_url: https://buer.haus/2024/01/16/reversing-and-tooling-a-signed-request-hash-in-obfuscated-javascript/
title: "Reversing and Tooling a Signed Request Hash in Obfuscated JavaScript | ziot"
---

[< Back](https://buer.haus/)

![](http://buer.haus/wp-content/uploads/2024/01/blog-1024x423.png)

![](http://buer.haus/wp-content/uploads/2024/01/hub.png)

Test out this concept with a lab I helped develop at [https://app.hackinghub.io/surl](https://app.hackinghub.io/surl)

I was hacking on a bug bounty program recently and discovered that the website is signing every request, preventing you from modifying the URL, including GET parameter values. I wanted to discover how they were doing this and find a way around it. If it requires a bit of effort, it is likely that not many people have tested around it. Not wanting to diminish the company’s security, I will redact information to protect their identity.

Initially while testing the target, I received generic error messages in the response when modifying the URL and GET parameter values. Eventually, I realized I was only seeing these errors when modifying GET params and not the POST params. There are two headers sent to the server and the server validates it to ensure that they match.

[![](http://buer.haus/wp-content/uploads/2024/01/1-1024x244.png)](http://buer.haus/wp-content/uploads/2024/01/1.png)

Headers:

- Time: 1703010077113
- Sign: 16428:088d7f8c3eaa175c94d1ab016be9a0c1132e329f:7a5:6581a7f6

Trying to modify the URL without updating those headers results in this error:

```
{"error":{"code":401,"message":"Please refresh the page"}}
```

From looking at requests, we don’t see these header values anywhere being sent from the server. We know the client has to generate them, so they likely exist in JavaScript. The first thing we do is bust open browser dev tools and search for the headers.

![](http://buer.haus/wp-content/uploads/2023/12/2.png)

Using Ctrl+Shift+F in Firefox under Search, we can search every JavaScript resource loaded in the DOM at that time. The terms Sign and Time are fairly generic, so there are a lot of results. Unfortunately, after going through all the results, I still could not find it. That suggests that these values are obfuscated.

After searching through all of the JavaScript libraries, I eventually stumbled on a heavily obfuscated file:

https://\[cdn\]/\[path\]/33415.js?rev=5d210e7-2023-11-29

[![](http://buer.haus/wp-content/uploads/2023/12/3-1024x250.png)](http://buer.haus/wp-content/uploads/2023/12/3.png)

There are quite a few JavaScript deobfuscation tools and libraries online, each having their own techniques and having different results depending on how the code was obfuscated.

Examples:

- [https://deobfuscate.io/](https://deobfuscate.io/)
- [https://deobfuscate.relative.im/](https://deobfuscate.relative.im/)
- [http://jsnice.org/](https://jsnice.org/)

Unfortunately, even with running the code through deobfuscation tools, it ended up still being highly obfuscated. Maybe there is a specific tool that can get cleaner output, but I decided to move on and try to tackle it myself. It can be important to learn how to do so if you are stuck in situations where the tools cannot help.

One of the methods I have found to work best when trying to navigate obfuscated code is to first try to understand the pseudo code as much as possible and start placing breakpoints. We know that it is signing these requests and we are looking for two things initially:

- There are no core JavaScript function strings in the code, so they obfuscated all the string values. Finding where they are stored in the obfuscated code and how they are calling them will be a major first step to figuring out what is going on in the code.
- We know that the string values _Sign_ and _Time_ are also obfuscated, so possibly in the same location.
- It needs information from the request in order to sign it, we know that it should also be using the URL string somewhere in the code too.

So how do we place a breakpoint in the browser and what does it do? There are good videos explaining this in-depth on YouTube, but to put it simply:

1. Press F12 (or equivalent keybind) to open your browsers' Developer Tools
2. In Firefox, head over to "Debugger". In Chrome, it is the "Sources" tab.
3. From here, things will be browser specific, but they mostly operate the same
4. For Firefox, go to the Sources tab and select one of the JavaScript resource files.
5. Click the " **{}**"button to beautify the source if it is minified.
6. Hovering over the numbers on the left side of each line of code, you will see that you can click on them.
7. Clicking on one of those numbers will set a breakpoint.
8. Whenever the browser executes this code, it will pause all execution.

This is helpful for engineers to understand issues occurring with their code in real-time. It is helpful for hackers when reverse engineering code to better understand how it works.

After beautifying the obfuscated JavaScript, placing a few breakpoints, and triggering requests, we eventually see that these variables at the end of the code are related to the request signer:

[![](http://buer.haus/wp-content/uploads/2023/12/4-1024x317.png)](http://buer.haus/wp-content/uploads/2023/12/4.png)

The breakpoint will trigger when it hits the code execution and the dev tools will display the variable values stored in the DOM at the time of the breakpoint. So now we know this part of the code is related to what we are looking for.

So now that we discovered the general area of our code via breakpoints, we are left with figuring out how this part works:

```

        t = n[o( - 570, 'nY58')](u(), W, n[o( - 555, 'U[zo')], '');\
        function o(W, n) {\
          return d(W - - 774, n)\
        }\
        const c = n[o( - 467, 'lMAW')](u(), window, n[o( - 557, 'EJC^')], null),\
        i = {};\
        i[o( - 444, 'BF4)')] = + new Date;\
        const f = n[o( - 493, 'jUU[')](u(), e.default, n[o( - 565, '2tt4')], null),\
        k = n[o( - 579, 'FRHE')](\
          r(),\
          [\
            n[o( - 501, 'We4x')],\
            i[o( - 444, 'BF4)')],\
            t,\
            f ||\
            0\
          ][o( - 519, 'r83A')]('\n')\
        );\
```\
\
This is a useful trick when starting to convert your obfuscated code into something easier to read. Given this piece of code, we can set a breakpoint on the first line (variable k):\
\
```\
\
        k = n[o( - 579, 'FRHE')](\
          r(),\
          [\
            n[o( - 501, 'We4x')],\
            i[o( - 444, 'BF4)')],\
            t,\
            f ||\
            0\
          ][o( - 519, 'r83A')]('\n')\
        );\
```\
\
When the browser pauses on that line, we can copy values and send them to the console:\
\
![](http://buer.haus/wp-content/uploads/2023/12/5.png)\
\
This can be useful when the obfuscation is trying to hide string values or function names.\
\
Setting a breakpoint, we can start to figure out what these obfuscated values are. We can see that the **w variable** is an object with information about the request. This is then used to assign the current URL path to the **const t**.\
\
[![](http://buer.haus/wp-content/uploads/2023/12/6-1024x293.png)](http://buer.haus/wp-content/uploads/2023/12/6.png)\
\
Moving along, we can see that the **const c** is storing our requests’ User-Agent:\
\
![](http://buer.haus/wp-content/uploads/2023/12/7.png)\
\
We can see that the **i variable** is an object that is storing “time”, a unix timestamp, likely used for the Time header in the request.\
\
![](http://buer.haus/wp-content/uploads/2023/12/7.png)\
\
We can see **f variable** is storing the value 379578839:\
\
![](http://buer.haus/wp-content/uploads/2023/12/8.png)\
\
The **k variable** is a hash value, but we don’t know how it is generated. The code that generates the hash:\
\
```\
\
        k = n[o( - 579, 'FRHE')](\
          r(),\
          [\
            n[o( - 501, 'We4x')],\
            i[o( - 444, 'BF4)')],\
            t,\
            f ||\
            0\
          ][o( - 519, 'r83A')]('\n')\
        );\
```\
\
Setting a breakpoint on **k**, we can then start to use “Step In” (F11 in Firefox). This will take us through the code execution one step at a time. This helps us to understand what the obfuscated code is doing, but eventually we will see what they are hashing. After stepping through about 25 times, we eventually see in the following image that it is calling a function named createOutputMethod with a string containing some of our suspected strings.\
\
[![](http://buer.haus/wp-content/uploads/2023/12/10-1024x296.png)](http://buer.haus/wp-content/uploads/2023/12/10.png)\
\
The value **n** is:\
\
```\
"NQ4UQIjeSeFbaORiNgZEt0AVXvwYYGQP\n1703012009162\n/api2/v2/users/notifications/count\n379578839"\
```\
\
The **variable** **W** is a function named“createOutputMethod” from another library:\
\
https://\[cdn\]/\[path\]/chunk-vendors-b49fab05.js\
\
Going through that JavaScript file, we can see that function is part of an external library named [js-sha1](https://github.com/emn178/js-sha1):\
\
```\
\
 /*\
 * [js-sha1]{@link https://github.com/emn178/js-sha1}\
 *\
 * @version 0.6.0\
 * @author Chen, Yi-Cyuan [emn178@gmail.com]\
 * @copyright Chen, Yi-Cyuan 2014-2017\
 * @license MIT\
 */\
```\
\
So now we know that the hash is the following:\
\
```\
js-sha1([string]\ntimestamp\npath\n[number])\
```\
\
We can check these values against the request to get a better idea of what they might be:\
\
![](http://buer.haus/wp-content/uploads/2023/12/11.png)\
\
We can see that the number at the end of the hash (379578839) is the User\_Id of the request.\
\
Given what information we have now, we can rewrite the obfuscated code to something easier to understand:\
\
```\
\
	const c = W["url"];\
\
	// const d = window.navigator.userAgent;\
	const d = userAgent;\
\
  	  f["time"] = +new Date;\
\
	const i = W["headers"]["user-id"];\
\
	const k = sha1(\
		[\
			n["frWIg"], // pE5CRmAhC8fvaWy6u58tKDTEKCZyTKLA\
			f["time"], // time\
			c, // url\
			i || // user-id\
			0\
		]["join"]('\n')\
	);\
```\
\
We are not done yet though, we understand a bit about how the code works now, but the Sign header still has additional values in it that we have not determined yet. At the end of the class, there is this giant return with nested function calls. To keep it short, I’ve removed the nested functions.\
\
```\
\
  return i[o( - 442, 'WQdV')] = [\
          o( - 560, 'r83A'),\
          k,\
          function (W) {\
            function t(W, n) {\
              return o(W - 583, n)\
            }\
            return Math[t(89, 'BF4)')](\
…\
}(k),\
          n[o( - 483, 'Trv&')]\
        ][o( - 458, '$LL1')](':'),\
        i\
      }\
    }\
  }\
```\
\
We can see in one of the functions it is passing in ‘:’, given that the Sign header has values separated by :, we can assume this is joining values. We can check this with our breakpoint and console trick to see that is indeed the **join** function.\
\
![](http://buer.haus/wp-content/uploads/2023/12/12.png)\
\
Checking the values that get joined:\
\
![](http://buer.haus/wp-content/uploads/2023/12/13.png)\
\
Remember that the Sign header value looks like this:\
\
```\
Sign: 16428:b866803f2316ba4682c03cf401039bc1abc068c9:770:6581a7f6\
```\
\
The huge nest of function calls are likely math operations manipulating the hash value to come up with that final number (e.g. 770).\
\
At this point we have a few options to consider:\
\
- Do we finish reversing this entirely, do we need to? We probably have to if we want to convert it to another language.\
- Have we identified enough about how the code works in order to manipulate the values we want?\
- We don’t want to run code manually to sign requests, it’ll slow down our testing. How can we make this work automatically?\
\
One option we have is to use a browser extension like Resource Override ( [Firefox](https://addons.mozilla.org/en-US/firefox/addon/resourceoverride/), [Chrome](https://chromewebstore.google.com/detail/resource-override/pkoacgokdfckfpndoffpifphamojphii?pli=1)) or the browser built-in script overrides, which can be accessed by right-clicking sources in the Debugger.\
\
![](http://buer.haus/wp-content/uploads/2023/12/14.png)\
\
This is not super efficient though, if we want to manipulate the requests in Burp Suite then we either need to rewrite the code for Python or Java. It would take a lot more effort to continue reversing the obfuscated code and rewrite it in another language. A quicker option is to copy the code, make the modifications we want, set it up as a NodeJS server, and utilize that service during requests in Burp as a plugin.\
\
Here is a diagram of the concept:\
\
[![](http://buer.haus/wp-content/uploads/2023/12/diagram2-1024x741.png)](http://buer.haus/wp-content/uploads/2023/12/diagram2.png)\
\
**server.js**\
\
- [https://gist.github.com/ziot/3bf579aa1d27b5cf07de4e7a4a859c45](https://gist.github.com/ziot/3bf579aa1d27b5cf07de4e7a4a859c45)\
\
Now that we verified that we can manipulate the URL and generate the correct hashes, we need to find a way to pass this data to Burp automatically. I have never written a Burp plugin before, so I was unfamiliar with the extension API. Thankfully in the year 2023, we have ChatGPT to speed things up.\
\
![](http://buer.haus/wp-content/uploads/2023/12/15.png)\
\
To my surprise, it generated fairly accurate code that was about 60% functional and needed small adjustments due to API changes made to the Burp extender.\
\
[![](http://buer.haus/wp-content/uploads/2023/12/16-651x1024.png)](http://buer.haus/wp-content/uploads/2023/12/16.png)\
\
The final redacted plugin code can be found here, **reqsigner.py**:\
\
- [https://gist.github.com/ziot/3d5002bcb239591290f22003c6c029de](https://gist.github.com/ziot/3d5002bcb239591290f22003c6c029de)\
\
To use the plugin, we have to ensure we have a Jython jar and our module folder for our installed Python modules:\
\
![](http://buer.haus/wp-content/uploads/2023/12/17.png)\
\
With the extension loaded, we can then go ahead and start manipulating requests in Burp Suite:\
\
[![](http://buer.haus/wp-content/uploads/2023/12/18-1024x547.png)](http://buer.haus/wp-content/uploads/2023/12/18.png)\
\
I was able to modify the GET “limit” parameter value and I am no longer receiving the 401 error code.\
\
This was a fun obstacle to overcome that did eventually lead to finding one vulnerability in a GET parameter of an API call. The issue was low-hanging, but you first had to put in some effort to test for it. A key takeaway from this is that you should always be willing to put in the effort to test something that no one else wants to. Consider the following idea:\
\
- If there is an unauthenticated vulnerability, someone probably found it while scanning.\
- If the vuln. requires an account but is low-hanging, someone probably found it without a scanner.\
- If it requires additional barriers to entry such as setting up payments, acquiring additional access, or reading obfuscated code, there is a good chance there are undiscovered vulnerabilities lingering that people just never put in the effort to find.\
\
Going the extra mile is where you will strike gold while doing security testing and research.\
\
Although reversing obfuscated code can sometimes be daunting, the tooling that exists today makes it easier than ever. With a little bit of practice learning how to use the debugger and read the DOM, you can navigate convoluted code and understand it with ease.\
\
Check out " [DEFCON 29 CTF Qualifier: 3FACTOOORX Write-up](https://buer.haus/2021/05/03/defcon-29-ctf-qualifier-3factooorx-write-up/)" for more JavaScript reversing.\
\
![](http://buer.haus/wp-content/uploads/2024/01/hub.png)\
\
Test out this concept with a lab I helped develop at [https://app.hackinghub.io/surl](https://app.hackinghub.io/surl)