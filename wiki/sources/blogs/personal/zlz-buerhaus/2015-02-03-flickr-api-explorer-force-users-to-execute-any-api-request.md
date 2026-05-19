---
source: zlz-buerhaus
source_url: https://buer.haus/2015/02/03/flickr-api-explorer-force-users-to-execute-any-api-request/
title: "Flickr API Explorer – Force users to execute any API request. | ziot"
---

[< Back](https://buer.haus/)

Flickr has a developer application section called [The App Garden](https://www.flickr.com/services/api/ "The App Garden"). Developers are able to create apps that make API calls to Flickr as an authenticated user via OAuth. I discovered a Cross-Site Request Forgery (CSRF) attack vector that allowed you to attack any user on Flickr.

**API Explorer**

Part of the App Garden is a feature called the API Explorer. You are able to use their forms to fill in arguments for the API call to test it out. When you do this, you can select to sign the API call as the current logged in account with full permissions.

Here's a list of all the API calls available on the API Explorer:

[https://www.google.com/?gws\_rd=ssl#q=site:flickr.com%2Fservices%2Fapi%2Fexplore%2F](https://www.google.com/?gws_rd=ssl#q=site:flickr.com%2Fservices%2Fapi%2Fexplore%2F)

\> About 445 results!

Examples of state-changing API calls on Flickr:

- Add, modifying, and deleting comments.
- Add and removing photosets, including photos inside of photosets.
- Add and removing galleries, including photos inside of galleries.
- Adding people and tags to photos.
- Posting photos to blogs.
- Joining/leaving groups.
- Setting a photo as a "favorite."
- etc.

**Making an API call in the Explorer**

When you make an API call using the API Explorer, it sends the API request as POST inside of an iframe with everything needed to execute it. The endpoint for the POST request differs from the one your application would normally use. These are the requests sent INSIDE of the iframe and not the request sent while using the Explorer.

Normal usage

> https://api.flickr.com/services/rest/?method=flickr.photos.comments.addComment&api\_key=\[redacted\]&photo\_id=14369938517&comment\_text=test&format=php\_serial&auth\_token=\[redacted\]&api\_sig=\[redacted\]

API Explorer

> https://www.flickr.com/services/api/render?method=flickr.photos.comments.addComment&api\_key=\[redacted\]&photo\_id=14369938517&comment\_text=test&format=json&nojsoncallback=1&auth\_token=\[redacted\]&api\_sig=\[redacted\]

The render endpoint uses syntax highlighting to "beautify" the return to help the developer understand it.

![image](https://31.media.tumblr.com/dbb5f2f991725d6ed6fba0311d58d1ee/tumblr_inline_n8q2fyIWVi1svukax.png)

So you need to have API\_Key, Auth\_Token, and Api\_Sig in order to make the API call. If you try to remove them, you get the appropriate errors saying invalid or missing token, key, or signature. This is how their developer API works and is working as intended.

Now let us take a look at the request the API Explorer is making:

![image](https://31.media.tumblr.com/f0eeeae9bc521924a604f8118fa4b400/tumblr_inline_n8q2tliI8U1svukax.png)

When you make an API explorer request, you're selecting what level of permission the API call should have. This is the sign\_call request variable and the **full** value means to send the request as the current logged in user with full permission.

If you look at the magic\_cookie request variable (henceforth noted as csrftoken), you'll notice a random hash value. This is their [Cross-Site Request Forgery (CSRF)](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_%28CSRF%29) protection and is intended to prevent the API explorer requests from being forced on unsuspected users. The idea is that you should not be able to send these requests without a valid csrftoken.

Something I have learned in my years of security is that websites are typically using a csrftoken blacklist instead of a whitelist. This means requests do not require csrftoken validation unless specifically listed. It's easier to make mistakes resulting in security vulnerabilities with a blacklist because requests will execute without crsftoken validation where with a whitelist they will not execute at all.

... you can see where I am going with this: sure enough, the API explorer requests did not actually validate or require the magic\_cookie.

**Example Exploit**

How do you exploit this? Without CSRF protection, you can create a POST form that automatically executes. Because the API call is executed inside of an iframe, you are not able to retrieve information from the API call. That means this exploit is limited to state-changing API requests.

If the following code is hidden on a website that you load while you are logged into Flickr, it will force you to comment on the param\_photo\_id specified.

```
<form method="POST" action="https://www.flickr.com/services/api/explore/flickr.photos.comments.addComment" id="csrf">
 <input type="hidden" name="method" value="flickr.photos.comments.addComment" />
 <input type="hidden" name="magic_cookie" value="" />
 <input type="hidden" name="enable_photo_id" value="on" />
 <input type="hidden" name="param_photo_id" value="14369938517" />
 <input type="hidden" name="enable_comment_text" value="on" />
 <input type="hidden" name="param_comment_text" value="test csrf 123" />
 <input type="hidden" name="format" value="rest" />
 <input type="hidden" name="sign_call" value="full" />
 <input type="submit" value="Submit" />
 </form>
 <script>
 document.getElementById("csrf").submit();
 </script>
```

**Lessons**

Developers

- Move your CSRF protection to a blacklist to make sure all of your state-changing/POST requests are covered by default. You'll be more secure and your users will happily let you know if a feature is not executing.
- Add logging for all failed csrftoken requests and monitor for spikes to discover broken requests before your users report it.
- If you are going to let developers test API calls, be careful about how much information you're filling in for them. As you can see, this circumvented some of Flickr's API security measures.

Security Researchers

- When you're testing a site, locate the CSRF protection as soon as possible.
- All state-changing requests on a website should be POST and be covered by CSRF protection.
- Validate CSRF protection by:
  - Remove the csrftoken request variable completely. It may only validate it when it is present in the request.
  - Put an invalid csrftoken value, i.e. &csrftoken=asdf. This is the fastest way to test what happens with a valid/invalid token.
  - Have the csrftoken request variable present but do not set a value, i.e. &csrftoken=
  - Try old csrftoken values that should have expired.
  - See if a valid csrftoken for a user is valid for other users.
- Even on a website like Facebook where there are thousands of requests, always test the csrftoken. Just because it's protected on the first 1000 requests you discovered, you may find that it's not protected on the 1001st request.

**Timeline**

- Reported on: 7/1/2014
- Validated the fix: 7/14/2014

**Bounty Reward**

$100