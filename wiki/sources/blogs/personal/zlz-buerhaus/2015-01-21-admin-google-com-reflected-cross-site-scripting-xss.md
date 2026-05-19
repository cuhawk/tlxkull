---
source: zlz-buerhaus
source_url: https://buer.haus/2015/01/21/admin-google-com-reflected-cross-site-scripting-xss/
title: "admin.google.com Reflected Cross-Site Scripting (XSS) | ziot"
---

[< Back](https://buer.haus/)

![](https://31.media.tumblr.com/58344ab9adbde058749534bc8fea60cf/tumblr_inline_ni8qv1wy2U1svukax.png)

After learning about [Google's bug bounty program](http://www.google.com/intl/EN-US/about/appsecurity/reward-program/index.html), I decided to look for vulnerabilities on their most sensitive services. Finding a vulnerability on admin.google.com was challenging; I managed to find a simple, but interesting form of [Cross-Site Scripting](https://www.owasp.org/index.php/Cross-site_Scripting_%28XSS%29).

**Details:**

URL: https://admin.google.com/

Proof of Concept:

```
 https://admin.google.com/mrzioto.com/ServiceNotAllowed?service=grandcentral&continue=javascript:alert(document.cookie);//
```

admin.google.com is a part of Google Apps service where you are able to configure permissions, users, and Google Services for your domain. This is a feature primarily used by businesses, especially ones that are using Gmail as the e-mail service for their domain.

The ServiceNotAllowed page appears when you are attempting to access a Google app service that has not been configured for your domain. It requires that you are logged into at least two accounts and will give you a form to switch accounts to continue to the service you were trying to load. When you select an account via the bullet on the page, it executes JavaScript to redirect your browser. The URL used in this JavaScript is supplied by the user in the _continue_ request parameter.

The continue request parameter is fairly common request variable in the Google login flow. This is the only page that I could find that did not validate the URL passed into it. This allowed you to craft Cross-Site Scripting attacks by using _"javascript:"_ as part of the URL and it would execute when the browser location is redirected.

**Attack:**

[![](https://31.media.tumblr.com/5112c777fa166d9e7b791cbc0bbd189d/tumblr_inline_ni8r6g5wwG1svukax.png)](http://imageshar.es/54b8faea75f3c91c7f000009/file)

**Impact:**

This attack allows you to force a Google Apps admin to execute any request on the admin.google.com domain. Some things that are possible:

Forcing the admin to ...

- Create new users with any permission level that you want, such as a super admin.
- Disable security settings for individual accounts or for multiple domains. This includes removing two-factor authentication (2FA) from accounts.
- Modifying domain settings so they point to your domain/dns, therefore all incoming emails to that domain are redirected to you instead.
- Hijack an account/email by resetting the password, disabling 2FA, and also removing login challenges temporarily for 10 minutes.

To demonstrate this, I built a proof-of-concept that shows a JavaScript payload pulling information from the Admin console, grabbing a list of users, changing the password and removing security settings from the first user in the list.

[![](https://31.media.tumblr.com/09fc889f63b54b257f732336ff4c1fd1/tumblr_inline_niiqei9vDe1svukax.png)](http://imageshar.es/54bf6370e5f5146f78000001/file)

**Source:**

[http://imageshar.es/54b8489989b9403e17000006/file](http://imageshar.es/54b8489989b9403e17000006/file)

```

<form action="" onsubmit="return onContinueClick(2);">
<ul>
	<li><input type="radio" value="javascript:alert(document.cookie);//?authuser=0" checked name="radioChoices" id="radioid0"><label for="radio0">email1@gmail.com</label></li>
	<li><input type="radio" value="javascript:alert(document.cookie);//?authuser=0" checked name="radioChoices" id="radioid1"><label for="radio1">email2@mrzioto.com</label></li>
</ul>
</form>

<script>
	function onContinueClick(accountCount) {
		var href;
		for (var i = 0; i < accountCount; i++) {
			if (document.getElementById('radioid' + i).checked) {
				href = document.getElementById('radioid' + i).value;
			}
		window.location.href = href;
		return false;
	}
	window.addEventListener("load", function() {
		document.getElementById("radioid0").focus();
	});
</script>
```

**Timeline:**

- Discovered and reported: 9/1/14
- Acknowledged: 9/5/14
- Fixed: 9/18/14

**Bounty Reward:**

[![](https://31.media.tumblr.com/95ce307591510347010b9572f57556f8/tumblr_inline_niiqhtsFGp1svukax.png)](http://imageshar.es/54bf6412e5f5146f78000008/file)