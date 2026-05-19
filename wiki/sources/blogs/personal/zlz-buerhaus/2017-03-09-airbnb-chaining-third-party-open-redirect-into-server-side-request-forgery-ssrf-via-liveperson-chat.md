---
source: zlz-buerhaus
source_url: https://buer.haus/2017/03/09/airbnb-chaining-third-party-open-redirect-into-server-side-request-forgery-ssrf-via-liveperson-chat/
title: "Airbnb – Chaining Third-Party Open Redirect into Server-Side Request Forgery (SSRF) via LivePerson Chat | ziot"
---

[< Back](https://buer.haus/)

![airbnb_horizontal_lockup_print](https://buer.haus/wp-content/uploads/2016/05/airbnb_horizontal_lockup_print.jpg)

**Update (3/15/2017)**:

- LivePerson reached out to me (3/9/17) after this write-up was posted and pushed out changes to patch the open redirect vulnerability. Props to their security team for following up on that!

Authors:

- [![image](https://abs.twimg.com/errors/logo23x19.png) Ben Sadeghipour](https://twitter.com/nahamsec)
- [![image](https://abs.twimg.com/errors/logo23x19.png) Brett Buerhaus](https://twitter.com/bbuerhaus)

Ben and I spent more time on Airbnb the past few months and discovered a new endpoint that we had never seen before. After spending a year or so on the program, we were at the point of trying to find a new approach looking for vulnerabilities.

We had the idea of going through all of the js files on Airbnb looking for new endpoints. We were already doing this manually to some degree, but decided to try and automate it. So we built a new tool that grabs js files and looks for relative URLs:

[![](https://buer.haus/wp-content/uploads/2017/03/chat-1024x660.png)](https://buer.haus/wp-content/uploads/2017/03/chat.png)

Doing this we quickly found new endpoints that we had missed and found a few new vulnerabilities to report. One of the new endpoints discovered led to finding a Server-Side Request Forgery vulnerability on Airbnb.

**Airbnb Live Chat**

[https://www.airbnb.com/chat](https://www.airbnb.com/chat)

We couldn't actually find the chat implemented anywhere, but we noticed the endpoint was in a JS file on the support page. Looking at the JavaScript code, we found a few AJAX requests relative to the /chat endpoint:

- /chat/availability
- /chat/estimatedWaitTime
- /chat/request
- /chat/events
- /chat/info/visitorTyping
- /chat/preSurvey

After a little bit of fuzzing, we discovered this error message on [https://www.airbnb.com/chat.asdf](https://www.airbnb.com/chat.asdf):

```
{"error":{"time":"2017-02-20T20:41:13.916-05:00","message":"null for uri: /api/account/33963583/chat.asdf?v=1&param=6114639610801186","internalCode":28}}
```

I have spent some time looking at LivePerson in the past, so I recognized that they were making API requests to the LivePerson REST API. It also appeared that the user input path is being put in the API request. Being able to specify a URL here wouldn't matter if it's hitting the LivePerson server, but it's possible that whatever is making the API request allows redirects.

I reported an open redirect vulnerability to LivePerson in the past, but I never received a response regarding it. I knew it probably still exist and spent some time trying to find it. After going through the API docs a bit, I discovered that the **visitorWantsToChat** action would cause a header redirect with request parameter **onlineURL**.

**Open Redirect**

[http://sales.liveperson.net/hc/5198728/?cmd=file&file=visitorWantsToChat&onlineURL=//xss.buer.haus/ssrftest&site=5198728](http://sales.liveperson.net/hc/5198728/?cmd=file&file=visitorWantsToChat&onlineURL=//xss.buer.haus/ssrftest&site=5198728)

**SSRF Payload**

Once we found the open redirect, we were able to make the API request to LivePerson redirect for full URL SSRF.

[https://www.airbnb.com/chat?cmd=file&file=visitorWantsToChat&onlineURL=https://xss.buer.haus/ssrf&site=5198728](https://www.airbnb.com/chat?cmd=file&file=visitorWantsToChat&onlineURL=https://xss.buer.haus/ssrf&site=5198728)

**Relative Path Traversal in Path Parameter**

Another interesting discovery is that you are able to traverse the LivePerson API request backwards with an encoded %5C in the path parameters. This allowed you to make calls to other endpoints on the LivePerson domain other than /api/ such as admin.

Example:

```
https://www.airbnb.com/chat.html/a..%5C..%5C..%5C..%5C..%5Casdfhc/5198728/?cmd=file&file=visitorWantsToChat&onlineURL=https://xss.buer.haus/ssrf&site=5198728
```

**Timeline:**

\- 2/16/17: Reported and fixed within 30 minutes