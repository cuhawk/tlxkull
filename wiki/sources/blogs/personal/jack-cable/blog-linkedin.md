---
source: jack-cable
source_url: https://cablej.io/blog/linkedin
title: "LinkedIn AutoFill Exposed Visitor Name, Email to Third-Party Websites"
description: "LinkedIn AutoFill Exposed Visitor Name, Email to Third-Party Websites"
---

**Update:** LinkedIn has issued a patch for the vulnerability and released the following statement:

> We immediately prevented unauthorized use of this feature, once we were made aware of the issue. We are now pushing another fix that will address potential additional abuse cases and it will be in place shortly. While we’ve seen no signs of abuse, we’re constantly working to ensure our members’ data stays protected. We appreciate the researcher responsibly reporting this and our security team will continue to stay in touch with them.
>
> For clarity, LinkedIn AutoFill is not broadly available and only works on whitelisted domains for approved advertisers. It allows visitors to a website to choose to pre-populate a form with information from their LinkedIn profile.

See LinkedIn's full response on [TechCrunch](https://techcrunch.com/2018/04/19/linkedin-autofill-leak/).

LinkedIn offers an [AutoFill button](https://www.linkedin.com/help/lms/answer/65688/linkedin-autofill-setup-guide?lang=en) to websites to autofill information such as a LinkedIn user's name, email address, phone number, location, and job in a website's form. This feature has been offered for several years to paying customers of LinkedIn's Marketing Solutions.

LinkedIn states that this functionality is restricted to whitelisted websites; however, until my report, any website could abuse this functionality. In a report to LinkedIn, I demonstrated that a user's information can be unwillingly exposed to any website simply by clicking somewhere on the page. This is because the AutoFill button could be made invisible and span the entire page, causing a user clicking anywhere to send the user's information to the website.

**Update:** LinkedIn has issued a patch for the vulnerability, mitigating the risk for exploitation.

### Proof of Concept

I created the following Proof of Concept in my initial report to LinkedIn. As they have fixed the regression allowing non-whitelisted websites to access information, the PoC no longer functions in its original design. You can play with how the PoC had worked when reporting it to LinkedIn at the following link: [https://cablej.github.io/LinkedInDemo.html](https://cablej.github.io/LinkedInDemo.html).

The potential for exploitation existed until being patched 04/19/18, as any whitelisted website can access this information with a single click.

The exploit flowed as follows:

1. The user visits the malicious site, which loads the LinkedIn AutoFill button iframe.
2. The iframe is styled so it takes up the entire page and is invisible to the user.
3. The user clicks anywhere on the page. LinkedIn interprets this as the AutoFill button being pressed, and sends the information via `postMessage` to the malicious site.
4. The site harvests the user's information via the following code:

```
window.addEventListener("message", receiveMessage, false);

function receiveMessage(event)
{
  if (event.origin == 'https://www.linkedin.com') {
    let data = JSON.parse(event.data).data;
    if (data.email) {
      alert('Hi, ' + data.firstname + ' ' + data.lastname + '! Your email is ' + data.email + '. You work at ' + data.company + ' and you live in ' + data.city + ', ' + data.state + '.');
      console.log(data);
    }
  }
  console.log(event)
}
```

### Bottom Line

This exposed the information of a visiting LinkedIn user to any website (until 04/10/18) and now exposed the information of any LinkedIn user to whitelisted websites paying for LinkedIn's Marketing Solutions until patched on 04/19/18. This had entrusted the privacy of LinkedIn users in the security of third-party websites. A compromise in any of the whitelisted websites would have exposed the information of LinkedIn users to malicious hackers.

LinkedIn released a fix shortly after this was published, mitigating the risk to users.

This directly violated LinkedIn's privacy policies, as stated in the [AutoFill FAQ](https://www.linkedin.com/help/lms/answer/65699):

> Can AutoFill "blind" submit form fields?
>
> This is strictly against LinkedIn's privacy policies. Some platforms enable form field data to be "blind" submitted without being seen by the visitor. AutoFill does not enable this.

Additionally, this exposed a user's information regardless of their privacy settings. For instance, if a user had set their privacy settings to not display their last name, email address, or location, LinkedIn still returned the user's full name, email address, and zip code.

This went against LinkedIn's documentation for AutoFill, which states:

> If information for a field is not available on your public profile, LinkedIn AutoFill will not pre-populate any data for that field. Any data that is pre-populated with information from your public profile will be explicitly shown in the form.

Thanks to [Amit Elazari](https://twitter.com/AmitElazari) for pointing this out in LinkedIn's documentation.

### Timeline

04/09/18 - Issue discovered and reported to LinkedIn

04/10/18 - Patch deployed by LinkedIn to restrict to whitelisted websites

04/10/18 - Asked for clarification if any fix was planned to prevent whitelisted websites from abusing this

04/19/18 - Additional patch from LinkedIn

I can be contacted at jackhcable (at) gmail.com or on Twitter at [@jackhcable](https://www.twitter.com/jackhcable).

X Follow Button

[Jack Cable - Blog](https://cablej.io/)

Twitter Widget Iframe