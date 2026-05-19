---
source: zlz-buerhaus
source_url: https://buer.haus/2017/03/31/airbnb-web-to-app-phone-notification-idor-to-view-everyones-airbnb-messages/
title: "Airbnb – Web to App Phone Notification IDOR to view Everyone’s Airbnb Messages | ziot"
---

[< Back](https://buer.haus/)

![airbnb_horizontal_lockup_print](https://buer.haus/wp-content/uploads/2016/05/airbnb_horizontal_lockup_print.jpg)

Authors:

- [![image](https://abs.twimg.com/errors/logo23x19.png) Ben Sadeghipour](https://twitter.com/nahamsec)
- [![image](https://abs.twimg.com/errors/logo23x19.png) Brett Buerhaus](https://twitter.com/bbuerhaus)

Airbnb recently created a new feature called [Experiences](https://www.airbnb.com/experiences/) which allows you to book things to do rather than places to stay. With the new code changes that came along with Experiences, we discovered a page that allowed you to send yourself a text message with a link to download the Airbnb app. This sent a POST request to an API endpoint we had never seen before. Using the JS Parser tool we built we discovered another API call associated with it. We found that these API calls were vulnerable to Insecure Direct Object Reference (IDOR) and allowed you to view all messages on Airbnb by ID.

The API request we discovered was the **/api/v2/air\_sms\_notifications** endpoint. Digging through the JS files on Airbnb we discovered there was also an API call named **/api/v2/air\_push\_notification**.

![](https://buer.haus/wp-content/uploads/2017/03/api.png)

Trying to send these API requests manually kept throwing generic errors and we couldn't figure out where it was actually implemented on the website. It took us awhile to eventually figure out there were some requirements that needed to be met before you could send the request. We eventually found two locations on Airbnb where it was integrated. Both of these were for sending yourself a text with a link to install the Airbnb phone app.

[![](https://buer.haus/wp-content/uploads/2017/03/screenshot_20170219-184740_1024-169x300.png)](https://buer.haus/wp-content/uploads/2017/03/screenshot_20170219-184740_1024.png)

**API Requests**

https://www.airbnb.com/api/v2/air\_sms\_notifications

- Requires that you have a verified phone number in your profile.
- This API request allowed you to send yourself SMS texts.
- There is a length limit on the SMS messages (160)
- Throttling restrictions on SMS only allowed you to send this API request a handful of times every hour

https://www.airbnb.com/api/v2/air\_push\_notifications

- Requires that you have a verified phone number, the Airbnb app installed on your phone (with that phone number), and you are logged into the app with that account. (This one took awhile to figure out)
- Instead of sending SMS, it pushed notifications to your phone through the phone app.
- There is no length restriction on the output.
- No throttling which made testing a lot easier compared to SMS

**POST data**

This API POST data was comprised of the following:

```
{"_format":"for_visitor","country":"USA","phone_number":"","template":"message","user_id":,"title":"","body":"","metadata":{},"object_id":"","status":"","role":"","photo_url":""}
```

The JSON attribute **template** turned out to be interesting. If you passed in an invalid template it would give you a list of all the valid templates that you could send.

[![](https://buer.haus/wp-content/uploads/2017/03/templates-1024x484.png)](https://buer.haus/wp-content/uploads/2017/03/templates.png)

**Templates**

|     |     |
| --- | --- |
| /api/v2/air\_sms\_notifications | /api/v2/air\_push\_notifications |
| content\_framework, custom, host\_banner\_app\_install, host\_never\_actives\_just\_raw\_listing, host\_never\_actives\_on\_description, host\_never\_actives\_on\_photo, host\_never\_actives\_on\_price\_or\_booking\_setting, message, mobile\_photo\_upload\_app\_install, identity\_verifications, identity\_verifications\_booking, p2\_p3\_abandon\_sms, reservation\_alteration\_approved, reservation\_alteration\_declined, reservation\_guest\_accepted, reservation\_guest\_cancelled, reservation\_guest\_declined, reservation\_host\_accepted, reservation\_host\_cancelled, reservation\_host\_declined, verified\_id\_app\_install, review\_final\_reminder\_message, mt\_pdp\_handoff, mt\_native\_handoff\_generic, message\_image\_attachment, guidebook\_landing\_page, wish\_lists\_native\_handoff | checkpoint, cn\_blackout\_g20\_hangzhou\_2016, custom, host\_never\_actives\_just\_raw\_listing, host\_never\_actives\_on\_description, host\_never\_actives\_on\_photo, host\_never\_actives\_on\_price\_or\_booking\_setting, identity\_verifications, identity\_verifications\_booking, message\_image\_attachment, message, midtrip\_host\_checkup\_reminder, mobile\_photo\_upload, paid\_amenity\_accepted, paid\_amenity\_canceled\_by\_guest, paid\_amenity\_canceled\_by\_host, paid\_amenity\_declined, paid\_amenity\_request, paid\_amenity\_shop\_services, preapproval\_guest\_sent, preapproval\_guest\_withdrawn, reservation\_alteration\_approved, reservation\_alteration\_request\_automatically\_accepted, reservation\_alteration\_declined, reservation\_alteration\_request, reservation\_guest\_accepted, reservation\_guest\_cancelled, reservation\_guest\_declined, reservation\_host\_accepted, reservation\_host\_cancelled, reservation\_host\_declined, reservation\_host\_request, reservation\_payment\_pending, reservation\_host\_first\_reminder, reservation\_host\_last\_reminder, review\_final\_reminder\_message, risk\_email\_updated, risk\_password\_updated, risk\_payout\_method\_updated, risk\_phone\_number\_updated, share\_your\_trip\_prompt, special\_offer\_guest, special\_offer\_guest\_expired, special\_offer\_guest\_withdrawn, special\_offer\_host\_expired, support\_message |

There are 27 possible SMS templates and 46 possible Push templates that you can send. This is a fairly big attack surface and there are some interesting template names in those lists that seem like potential targets.

We decided to start with the **custom** template. Trying to send the POST request, we get the following response:

```
{"error_code":400,"error_type":"validation","error_message":"There was an error processing the request.","error_id":"fd9fba9bc18538d7ae93ba6867c1be0a","error_details":"title is required."}
```

If you sent the POST request to a template with a missing attribute, it would tell you what attributes you were missing. This verbosity gave us everything we needed to start gathering information and seeing what functionality exist.

We discovered that the **custom** template accepted parameters title and body. This template allowed you to send yourself a custom SMS or notification.

```
{"_format":"for_visitor","country":"USA","phone_number":"","template":"custom","user_id":109764261,"status":"test","title":"test","body:"test"}
```

[![](https://buer.haus/wp-content/uploads/2017/03/screenshot_20170219-125058_1024-576x1024.png)](https://buer.haus/wp-content/uploads/2017/03/screenshot_20170219-125058_1024.png)

We spent probably a good 10-12 hours going through all of these templates. Towards the end it came down to waiting hour intervals to send 4-5 requests each against the SMS API due to the throttle on it. It was some effort to slowly grab the attributes for each template and eventually test to see if they were vulnerable. In the end we discovered a handful of vulnerable templates, but the most interesting template ended up being **message**.

Most of the templates required that you send the attribute **object\_id**. Given that this API is a fairly broad service that has a lot of features behind it, our guess was that object\_id was the data that the template wanted to reference by the database entry id. When you come across an id like that, getting an IDOR can be immensely useful if it's a simple sequential numeric ID. Not having an object\_id for testing, we threw in a random number. Looking at the phone we sent the notification to, we immediately knew we had something real bad.

Enumerating on the object\_id by one we could see that we had access to every private message on Airbnb by ID. What was neat is that you could do this with SMS as well, as the templates seemed to share a lot of the same core code. With the SMS throttle and truncation, it wasn't really a viable attack vector. With Push you could enumerate through the full messages without any restrictions.

|     |     |
| --- | --- |
| Push | SMS |
| [![](https://buer.haus/wp-content/uploads/2017/03/message-169x300.jpg)](https://buer.haus/wp-content/uploads/2017/03/message.jpg) | [![](https://buer.haus/wp-content/uploads/2017/03/screenshot_20170220-080621_1024-169x300.png)](https://buer.haus/wp-content/uploads/2017/03/screenshot_20170220-080621_1024.png) |

This vulnerability turned out to be a fun exercise because of all the moving pieces and research required to figure out the impact. The object\_id IDOR was vulnerable on most of the templates which led to several different data leaks, but nothing as high impact as messages. We were unable to get some of the templates to work as they would always throw 500 errors with the data we were sending.

**Timeline:**

This was sent in along with the [Remote Code Execution report](https://buer.haus/2017/03/13/airbnb-ruby-on-rails-string-interpolation-led-to-remote-code-execution/), so they were probably focused on fixing that first.

- 2/19/2017: Reported
- 2/21/2017: Triaged
- 2/23/2017: Fixed