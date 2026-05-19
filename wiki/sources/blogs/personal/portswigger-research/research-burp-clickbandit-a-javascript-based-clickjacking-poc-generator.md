---
source: portswigger-research
source_url: https://portswigger.net/research/burp-clickbandit-a-javascript-based-clickjacking-poc-generator
title: "Burp Clickbandit: A JavaScript based clickjacking PoC generator | PortSwigger Research"
published: 2015-12-09T16:23:00
description: "Clickjacking vulnerabilities are endemic throughout the web and really quite serious in the right circumstances. Manually crafting a proof of concept attack can mean laborious hours of offset-tweaking"
---

# Burp Clickbandit: A JavaScript based clickjacking PoC generator

![Gareth Heyes](https://portswigger.net/content/images/profiles/callout_gareth_heyes_114px.png)

### [Gareth Heyes](https://portswigger.net/research/gareth-heyes)

Researcher

[@garethheyes](https://twitter.com/garethheyes)

- **Published:** Wednesday, 9 December 2015 at 16:23 UTC

- **Updated:** Monday, 30 April 2018 at 13:13 UTC


![Burp Suite Click Bandit](https://portswigger.net/cms/images/1b/5b/0e606999296e-article-burp-clickbandit.png)

[Clickjacking](https://www.owasp.org/index.php/Clickjacking) vulnerabilities are endemic throughout the web and [really quite serious](https://web.archive.org/web/20081029064822/http://www.sectheory.com/clickjacking.htm) in the right circumstances. Manually crafting a proof of concept attack can mean laborious hours of offset-tweaking, so we’ve just released [Burp Clickbandit](https://portswigger.net/burp/help/suite_functions_clickbandit), a point-and-click tool for generating clickjacking attacks. When you have found a web page that may be vulnerable to clickjacking, you can use Burp Clickbandit to quickly craft an attack, to prove that the vulnerability can be successfully exploited. A few related tools already exist, but Burp Clickbandit has an array of features that hopefully make it stand out:

- Supports multi-click attacks
- Written in pure JavaScript, and trivial to deploy
- Supports transparency, clearly showing the attack mechanics
- Works on most websites!

As of [today's Burp release](https://portswigger.net/burp/releases/1-6-32), you can grab a copy of Clickbandit from within Burp, via the Burp menu. To deploy it, install it as a bookmarklet or simply paste it into your browser's developer console. It works by detecting the HTML elements you click and using their dimensions and position to generate the relevant click area. If the click lands in an iframe or flash object, it instead uses the x and y coordinates of the mouse, and zooms into the object to provide the click area. This is because the DOM element will be the entire frame and so the position will be incorrect.

In order to launch multi-click attacks, it’s critical to be able to detect when the user has clicked so you know when to move the iframe to the next clicktarget. To detect clicks cross domain we use the blur event on the current window; this fires when you click inside the iframe. We use an onmouseover event on the iframe and a flag to ensure the click happens inside the frame boundary. This isn’t perfect because a right click on the iframe will also trigger the blur event but there is no way around that due to same origin policy. Here is the relevant code snippet:

`window.addEventListener("blur", function() {
    if (window.clickbandit.mouseover) {
        hideButton();
        setTimeout(function() {
            generateClickArea(++window.clickbandit.config.currentPosition);
            document.getElementById("clickjack_focus").focus();
        }, 1000);
    }
}, false);
document.getElementById("parentFrame").addEventListener("mouseover", function() {
    window.clickbandit.mouseover = true;
}, false);
document.getElementById("parentFrame").addEventListener("mouseout", function() {
    window.clickbandit.mouseover = false;
}, false);`

We use a timeout because the click won’t be accurately detected unless there is a delay, and we also focus a hidden input field after each click to enable multi-click detection since the blur event won’t be fired unless the focus is switched from the iframe to the parent document.

## Using Clickbandit

![](https://portswigger.net/cms/images/migration/blog/screenshot001.png)

Record mode

Burp Clickbandit runs in your browser using JavaScript. It works on all modern browsers except for Internet Explorer and Microsoft Edge. To run Clickbandit, use the following steps or refer to the [Burp documentation](https://portswigger.net/burp/help/suite_functions_clickbandit).

1. In Burp, go to the Burp menu and select "Burp Clickbandit".
2. On the dialog that opens, click the "Copy Clickbandit to clipboard" button. This will copy the Clickbandit script to your clipboard.
3. In your browser, visit the web page that you want to test, in the usual way.
4. In your browser, open the web developer console. This might also be called "developer tools" or "JavaScript console".
5. Paste the Clickbandit script into the web developer console, and press enter.

The Burp Clickbandit banner will appear at the top of the browser window and the original page will be reloaded within a frame, ready for the attack to be performed. Then simply execute the sequence of clicks you want your victim to perform. If you want to prevent the action being performed during recording, use the "disable click actions" checkbox. When you’ve finished recording, click the "finish" button. This will then display your attack for review.

![](https://portswigger.net/cms/images/migration/blog/screenshot002.png)

Review mode

In this view you can adjust the zoom factor using the plus and minus buttons. You can toggle transparency allowing you to see the site underneath the button. You can also change the iframe position using the arrow keys. Reset allows you to restore the original attack removing any modifications you may have made to the zoom factor or position. Click the "save" button to download your proof of concept attack and save it locally. When the [clickjacking attack](https://portswigger.net/web-security/clickjacking) is complete (after the victim has clicked the last link) the message “you’ve been clickjacked” appears. You can alter this message in the code to suit your needs.

![](https://portswigger.net/cms/images/migration/blog/screenshot003.png)

You've been clickjacked message

[clickjacking](https://portswigger.net/research/clickjacking)

[Back to all articles](https://portswigger.net/research/articles)