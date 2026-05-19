---
source: portswigger-research
source_url: https://portswigger.net/research/detecting-web-message-misconfigurations-for-cross-domain-credential-theft
title: "Detecting web message misconfigurations for cross-domain credential theft | PortSwigger Research"
published: 2022-11-09T14:13:00
description: "We released a new version of Burp recently on the Early Adopter channel that updates DOM Invader to help find cross-domain secrets. In this post we are going to show you how to use DOM Invader to dete"
---

# Detecting web message misconfigurations for cross-domain credential theft

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 9 November 2022 at 14:13 UTC

- **Updated:** Wednesday, 9 November 2022 at 14:13 UTC


![A message in a bottle with characters in the sea and data flowing around it](https://portswigger.net/cms/images/12/10/1019-article-detecting-web-message-misconfigurations-article.jpg)

We [released a new version of Burp recently](https://portswigger.net/burp/releases/professional-community-2022-11) on the Early Adopter channel that updates DOM Invader to help find cross-domain secrets. In this post we are going to show you how to use DOM Invader to detect URL tokens in misconfigured cross-domain web messages.

We noticed an excellent post by [Frans Rosén](https://twitter.com/fransrosen) on [exploiting OAuth-Flows](https://labs.detectify.com/2022/07/06/account-hijacking-using-dirty-dancing-in-sign-in-oauth-flows/), and immediately started thinking about how to automate detection of such vulnerabilities. The main problem with auditing web messages is that it's a laborious task - they aren't sent over the wire, and you have to use the JavaScript debugger and add breakpoints and manually edit the message data. So we decided to make things easy by updating DOM Invader to inspect the message data, and notify you if a message contains data from the URL and is being sent to a different origin. This isn't foolproof, of course, and requires manual inspection to see if it is possible to embed the iframe and use this secret information in some way.

To start detecting cross-domain leaks, we need to enable the new option in DOM Invader. To do this, simply enable post message interception and click **Detect cross-domain leaks:**

![Screen shot showing how to enable cross-domain data checks in DOM Invader](https://portswigger.net/cms/images/eb/4d/0e62-article-dom-invader-screenshot-crossdomain-leaks.png)

### Putting it to the test

We've prepared some test cases that can demonstrate this issue. Please visit the [cross-domain secrets](https://portswigger-labs.net/dom-invader/testcases/postmessage-cross-domain-secrets/) test case to try out this feature. When you have loaded the test case you should see some messages, and you'll notice that DOM Invader has found a "low" issue. If you click the message with a blue exclamation mark, you'll be able to see the full detail of the message:

![DOM Invader screenshot showing a web message vulnerable to cross-domain secrets theft](https://portswigger.net/cms/images/7d/06/65b0-article-dom-invader-message-screenshot.png)

In the message data above you should see a URL, along with a GET parameter called secret with a value of "supersecret". This test case demonstrates that you could embed the URL as an iframe, and then steal the "supersecret" value with a message event listener. To exploit the test case, you need to create a web message event listener that will read the data and use an iframe and point it to the target URL:

`<script>
window.addEventListener('message',function(e){
console.log(e.data);//this should contain "supersecret"
})
</script>
<iframe src="https://subdomain1.portswigger-labs.net/dom-invader/testcases/postmessage-cross-domain-secrets/external.html"></iframe>`

### Summary

This post demonstrates how to use DOM Invader's new cross-domain leak feature to find secrets inside web messages. We've shown you how to enable the feature and find a vulnerable web message with just a couple of clicks. We'd love to hear of any findings you've got with this new feature, [let us know](https://twitter.com/PortSwiggerRes) and we'll RT the best blog posts.

[DOM Invader](https://portswigger.net/research/dom-invader) [Credential Theft](https://portswigger.net/research/credential-theft) [Cross Domain](https://portswigger.net/research/cross-domain)

[Back to all articles](https://portswigger.net/research/articles)

## Related Research

[**Widespread prototype pollution gadgets** 22 June 2022Widespread prototype pollution gadgets](https://portswigger.net/research/widespread-prototype-pollution-gadgets)