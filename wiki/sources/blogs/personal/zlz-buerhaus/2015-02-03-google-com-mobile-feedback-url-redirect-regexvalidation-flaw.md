---
source: zlz-buerhaus
source_url: https://buer.haus/2015/02/03/google-com-mobile-feedback-url-redirect-regexvalidation-flaw/
title: "Google.com – Mobile Feedback URL Redirect Regex/Validation Flaw | ziot"
---

[< Back](https://buer.haus/)

Back in October of last year I discovered a JavaScript flaw on Google.com that bypassed protocol validation by abusing an if check against a URL parsed by regex. I was unable to find a way to attack this vector, but was still rewarded a bounty of $500 due to Google knowing of an active browser vulnerability that allowed them to exploit it successfully.

**Details**

I apologize in advance as this article will require a bit more of a technical understanding than my previous articles because it goes into details of Regex.

I was investigating mobile versions of the Google.com services hoping to find pages that may have been less explored by security researchers. In the past I have seen that mobile versions of websites can sometimes be more vulnerable than their desktop counterpart due to less customer traffic/visibility and maintenance from engineers.

I discovered a mobile feedback page ( [google.com/tools/feedback/mobile\_feedback](https://www.google.com/tools/feedback/mobile_feedback)) that had the browser pass a url inside of a request variable. This was similar to a [vulnerability](http://potatohatsecurity.tumblr.com/post/108756906604/admin-google-com-reflected-cross-site-scripting) I had at the time recently discovered on Google, so this warranted further investigation.

The normal flow of the application:

1. Load this URL: [https://www.google.com/tools/feedback/mobile\_feedback?hl=en&url=http://www.apple.com/&redirect=true&authuser=0&pi=17&hl=en](https://www.google.com/tools/feedback/mobile_feedback?hl=en&url=http://www.apple.com/&redirect=true&authuser=0&pi=17&hl=en)
2. Write in some feedback and click the submit button.
3. Click the close button.
4. ---\> You are redirected to apple.com.

I quickly noted that the logic was being handled by JavaScript and had to dive into the obfuscated script [mobile\_submitter\_\_en.js](https://www.gstatic.com/feedback/js/uog71sae5wft/mobile_submitter__en.js) to get a better understanding of how it worked. After using a [beautifier](http://jsbeautifier.org/) and using breakpoints in Firebug, I was able to discover two important bits of information:

1. They were parsing the URL you sent in the url request var with regex.
2. It was checking if the protocol section was null, http, or https before redirecting you using window.location.href.

This was important to know because:

- If the protocol is null, it assumes that you are being redirected to a relative path.
- window.location.href can be vulnerable to Cross-Site Scripting if redirected to "javascript:".

This is what the code looked like:

Regex

```
var Tb = /^(?:([^:/?#.]+):)?(?:\/\/(?:([^/?#]*)@)?([^/#?]*?)(?::([0-9]+))?(?=[/#?]|$))?([^?#]+)?(?:\?([^#]*))?(?:#(.*))?$/;
```

Redirect logic

```
if ("http" == a || "https" == a || "" == a) {
	window.location.href = this.d;
	return
}
```

**The Flaw**

After the URL gets parsed and right before redirecting it will validate that the URL's protocol is either http, https, or blank. Where "http" == a, a is the second position in the array. In the window.location script, d is the first position of the array, which is the original unparsed URI.

Example:

https://www.google.com/tools/feedback/mobile\_feedback?hl=en&url=http://login:pass@www.google.com:80/1/2%3F3=4&5=6%237=8&redirect=true&authuser=0&pi=17&hl=en

Redirect URI:

[http://login:pass@www.google.com:80/1/2?3=4&5=6#7=8](http://login:pass@www.google.com/1/2?3=4&5=6#7=8)

Regex results:

```
0: "http://login:pass@www.google.com:80/1/2?3=4&5=6#7=8" [0, 51]
1: "http" [0, 4]
2: "login:pass" [7, 17]
3: "www.google.com" [18, 32]
4: "80" [33, 35]
5: "/1/2" [35, 39]
6: "3=4&5=6" [40, 47]
7: "7=8" [48, 51]
```

As you can see, there are a lot of parts in the URL that the regex is looking for. Not every URL is going to have this data, so they are using question marks to state that the capture group is optional. This is the initial flaw.

The second position in the array (which is 1, because the array starts at index 0) is parsed out as http. If you look closely at the Regex parsing the URL, you can see the first thing they are checking for is any character except for :, /, ?, #, and . up until the first : character.

However if you look at the last part of the regex, there is a greedy check for any characters up until the first # or ?. By placing a period before the first :, the first capture group is ignored and the match is instead encapsulated in index position 5. Interestingly, you can put # or ? in place of the . to better illustrate the capture match.

Here's a picture showing index 1 empty due to a # character in the URL protocol:

![](http://imageshar.es/54d169902d9b63044f000001/file)

Because of this flaw in the regex, you are able to circumvent the if logic prior to the window.location redirect. If you remember, the code is checking if the protocol is set to http, https, or null. Because it is null, it is allowing the browser to redirect.

This is as close as I could get to a malicious payload:

[https://www.google.com/tools/feedback/mobile\_feedback?hl=en&url=javascript.:alert(1);&redirect=true&authuser=0&pi=17&hl=en](https://www.google.com/tools/feedback/mobile_feedback?hl=en&url=javascript.://alert(1);&redirect=true&authuser=0&pi=17&hl=en)

Regex Match Results

```
Successful match! Groups:
0: "javascript.:alert(1);" [0, 23]
1: undefined
2: undefined
3: undefined
4: undefined
5: "javascript.:alert(1);" [0, 23]
6: undefined
7: undefined
```

This redirects your browser to:

```
javascript.:alert(1);
```

**The Fix**

The new version of mobile\_submitter\_\_en.js with the changes:

https://www.gstatic.com/feedback/js/asil0m973whx/mobile\_submitter\_\_en.js

Changes:

```
if ("http" == a || "https" == a) {
	window.location.href = this.d;
	return
}
```

This did not change the regex flaw, but it requires that the request variable that you send contain a full path URL with a protocol of http or https.

**Some thoughts**

- I couldn't find a way to exploit this because I'm unaware of any protocol that has a period in it or a way to get the browser to ignore the period in the protocol.
- Using regex to parse the URL is not unheard of and is done commonly, but one might wonder if this was the best way to handle URL validation in this flow. Google has plenty of endpoints where they have secure methods of validating URLs on their backend. Mobile sites need to be faster and simpler, but this can lead to convenience over security which may result in insecure practices.
- Many researchers may opt out of deep diving into Google's JavaScript because of their heavy obfuscation and optimization. This could be an ideal location for hackers or security researchers to find undiscovered DOM based vulnerabilities.

**Update (2/4/15)**

Eduardo Vela ( [@sirdarckcat](https://twitter.com/sirdarckcat)) noted that the URL validation regex used here is from the Closure Library developed by Google. There's more information on the code in the [utils.js](http://docs.closure-library.googlecode.com/git/local_closure_goog_uri_utils.js.source.html#line126) file if you're interested!

**Timeline**

- Reported: 10/6/14
- Fixed: 11/26/14

**Bounty Reward**

$500

After writing this article, I have decided to donate the $500 to St. Jude Children's Research Hospital.