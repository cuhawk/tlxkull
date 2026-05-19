---
source: msrc
source_url: https://www.microsoft.com/en-us/msrc/blog/2025/08/postmessaged-and-compromised/
title: "postmessaged-and-compromised"
---

This is the Trace Id: 97c9d1a5c45136ca447bcb9e0c0e4d04




[Skip to main content](https://www.microsoft.com/en-us/msrc/blog/2025/08/postmessaged-and-compromised/#mainContent)

# postMessaged and Compromised

[MSRC](https://www.microsoft.com/msrc/blog/category?cat=MSRC "MSRC")

/
By Jhilakshi Sharma/
August 25, 2025


At Microsoft, securing the ecosystem means more than just fixing bugs—it means proactively hunting for variant classes, identifying systemic weaknesses, and working across teams to protect customers before attackers ever get the chance. This blog highlights one such effort: a deep dive into the risks of misconfigured postMessage handlers across Microsoft services and how MSRC worked with engineering teams to mitigate them.

This research was part of MSRC’s ongoing initiative to identify and eliminate token exfiltration vectors across shared domains, i.e. broadly validated domains used for trust relationships. It led to the discovery of multiple high-impact vulnerabilities—some cross-tenant, some involving token forwarding, and all rooted in overly permissive trust models. The good news: we’ve implemented mitigations and taken steps to reduce risk, with protections now in place for customers.

## Understanding postMessage and why it matters

Modern web applications rely on postMessage for secure cross-origin communication—between parent pages and iframes, or between pop-ups and their openers. When implemented correctly, it enables rich, interactive experiences across services like Teams, Power BI, and Dynamics 365. But when origin validation is missing or misconfigured, postMessage becomes a powerful vector for token theft, cross-site scripting (XSS), and privilege escalation.

The postMessage API allows secure cross-origin communication between different Window objects, such as between a web page and an iframe embedded within it, or between a page and a pop-up window it spawned. This is achieved by specifying the target window and the origin that the target window must have to receive the message:

## Syntax overview

`targetWindow.postMessage(message, targetOrigin);`

- **targetWindow**: The reference to the window you want to send the message to (e.g., an iframe’s contentWindow or a pop-up’s window object).

- **message**: The data you want to send (can be a string or a structured object).

- **targetOrigin**: A critical security parameter that specifies the expected origin of the receiving window. This ensures that the message is only delivered if the target window matches the specified origin.


## The hidden dangers of insecure origin checks

One of the most common missteps in implementing postMessage is failing to validate the origin of the message sender or receiver. This can manifest in two critical ways:

- **Insecure Senders**: Applications that send sensitive data (like authentication tokens) without verifying the recipient’s origin risk leaking that data to malicious frames.

- `targetWindow.postMessage(message,’*’);`

- **Insecure Listeners:** Listeners that accept messages without validating the sender’s origin (event.origin) are vulnerable to spoofed messages, which can trigger unauthorized actions or data manipulation.


For example, insecure regex validation:

```js
window.addEventListener('message', (event) => {

    const regex = /^https:\/\/.*\.example\.com$/;

    if (regex.test(event.origin)) {

        // Process message

    }

});
```

Later in this blog, we’ll explore several of the vulnerabilities we discovered and reported through MSRC.

**Window object validation: A false sense of security**

```js
window.addEventListener("message", function (event) {
    // Insecure: trusts the iframe reference, not the origin
    if (event.source === trustedIframeWindow) {
        const message = event.data;
```

A particularly dangerous anti-pattern is validating the event.source (the window object) instead of event.origin. While it may seem intuitive to trust the window object, this approach is flawed. Take, for example, a web application that embeds a component (e.g., a data visualization frame) inside an iframe. This component communicates with the parent application using postMessage. The parent registers a message handler and attempts to validate the sender by checking event.source against a known iframe window object—but it does not validate event.origin.

This creates a vulnerability. An attacker can embed the entire application in their own page, hijack the iframe by replacing its src with a malicious URL, and gain control over the iframe’s window object. Because the parent application only checks event.source, it mistakenly trusts the attacker’s message.

## postMessage vulnerabilities through Missing Origin Validation (targetOrigin ‘\*’)

**MSRC case study I: Auth token exposure through postMessage at Bing Travel**

We found the following code in a JS file at Bing Travel:





![A screenshot of a computer code Description automatically generated](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__ed35c0c8?scl=1)

The script is checking if this.recorderModalIframe and its contentWindow property exist. If they do, it sends a message to the contentWindow of this.recorderModalIframe using the postMessage method. The message being sent is an object {accessToken:this.userAuthJwt}.

The “\*” argument in the postMessage call means that the message will be sent to any window, regardless of its origin. By embedding a malicious iframe in a page that loads that script, the iframe will be able to intercept the access token whenever the postMessage interaction gets triggered.

### Mitigation

To address the token exposure risk caused by an insecure postMessage implementation, the Engineering Team removed the affected package dependency from their repository and coordinated with the upstream package owners to eliminate the vulnerable code. This ensured the issue was resolved both locally and at the source, preventing recurrence across dependent services.

**MSRC case study II: Auth token exposure through postMessage at web.kusto.windows.net**

![A screenshot of a computer AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__d8de3fbb?scl=1)

A postMessage implementation in web.kusto.windows.net was found to send an object containing a sensitive access token—scoped for user\_impersonation—to an Azure Marketplace iframe using a wildcard targetOrigin ("\*"). This insecure configuration could allow a malicious iframe to intercept the message and extract both the token and the associated clusterUrl, enabling unauthorized access to user resources. To mitigate this, the postMessage call should specify the exact trusted origin derived from the clusterUrl.

If we analyze the code in the response more closely:

![A screenshot of a computer code AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__489145b7?scl=1)

The code retrieves an access token by calling getToken on the authProvider object from l.dependencies, requesting the scope \[“dc78932e-f9b5-489b-b50a-f49d5831d9df/user\_impersonation”\]. This scope grants the token the ability to impersonate the user for the specified resource, identified by the GUID. Once obtained, the token is embedded in a message object—along with a clusterUrl—and sent via postMessage to an Azure Marketplace iframe.

The token carries the user\_impersonation scope, which could allow an attacker to act on behalf of the user across services that accept this token. This opens the door to unauthorized data access, privilege escalation, and lateral movement within the environment.

### Mitigation

![](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__9d2ca160?scl=1)

In this case, the strict, trusted origin for the postMessage call should be `https://${e}.kusto.windows.net/`. This value is already being used to construct the clusterUrl in the message payload, as we can see in line 18 in the code snippet above. By using the same origin in the targetOrigin parameter of postMessage, you ensure that the message—containing the sensitive access token—is only delivered to the intended Azure Marketplace iframe hosted at that specific Kusto cluster endpoint.

To fully mitigate the issue, the Engineering Team removed the now-obsolete Marketplace feature from the codebase. This included deleting the MarketplacePage component, associated routes, menu items, feature flags, and localization strings across multiple files. By eliminating all related code paths, they ensured the vulnerable logic could no longer be triggered or reintroduced.

## When trusted isn’t safe: The risk of loose origin validation in postMessage

In modern cloud environments, cross-origin communication is essential—but when origin validation is too broad, it opens the door to serious security risks. A recurring pattern across Microsoft 365, Azure, and Dynamics 365 is the use of service-level origin validation (e.g., \*.domain.com) instead of tenant-specific or app-specific validation. While this simplifies integration, it also creates a wide attack surface.

### The problem: Overly broad trust boundaries

Loose origin validation allows any subdomain within a trusted service to send messages via postMessage(). If one of those subdomains is compromised, it can be used to send malicious messages to trusted applications, potentially leading to token theft, unauthorized actions, or data exfiltration.

### Real-world examples

![A green and white cloud with a recycle symbol AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__315d06c1?scl=1)

**Microsoft 365**

- SharePoint Online: Accepting messages from any \*.sharepoint.com domain means a compromised site could inject malicious scripts into trusted apps.

- Teams Integrations: Both first-party and third-party apps often allow messages from any \*.teams.microsoft.com domain, risking unauthorized access if a subdomain is compromised.


**Azure**

- Azure App Services: Allowing postMessage() from any \*.azurewebsites.net domain can lead to XSS or data theft if an attacker controls a subdomain.

- Azure Functions: Similar risks arise when functions communicate across \*.azurefunctions.net without strict origin checks.


**Dynamics 365**

- Portals: Trusting all \*.dynamics.com domains can expose internal apps to malicious messages from compromised portals.

- Power Apps: Integrations that accept messages from any \*.powerapps.com domain are vulnerable to abuse by compromised or overly permissive apps.


**Why it happens**

This pattern often emerges from a desire to support dynamic, scalable integrations without constantly updating origin lists. But the trade-off is a weakened security boundary that attackers can exploit.

## The 3 exploitation techniques for postMessage vulnerabilities through trusted domains

While postMessage is a powerful tool for cross-window communication, its misuse—especially in the context of overly trusted domains—can lead to serious security vulnerabilities. MSRC has identified three primary exploitation techniques that attackers can use when postMessage is enabled across broadly trusted domains:

1. **XSS in a trusted domain**

If a trusted domain (e.g., \*.contoso.com) is vulnerable to cross-site scripting (XSS), an attacker can inject malicious scripts that exploit postMessage channels to exfiltrate tokens or impersonate users.

2. **Taking over dangling domains**

Domains that were once valid but are no longer maintained (dangling) can be re-registered or hijacked. If these domains remain in the validDomains list of a Teams app manifest, they become a silent backdoor for message interception or injection.

3. **Custom code by design**

Some platforms, like Power Apps, intentionally allow users to embed custom JavaScript. If these apps are included in validDomains, they can be abused to run malicious code that leverages postMessage to interact with privileged Teams contexts.

## postMessage Vulnerabilities in Trusted Microsoft Teams 1P apps

The MSRC Vulnerabilities & Mitigations (V&M) team uncovered multiple high-impact security issues stemming from overly permissive postMessage configurations in Microsoft Teams apps. These issues often arise from a combination of two factors: loose domain validation and overprivileged app manifest settings.

#### Real-world findings from variant hunting

- MSRC case study III: A 1-click XSS vulnerability was discovered in the FileBrowser component of Teams, triggered via deep links.

- MSRC case study IV: A 0-click XSS was identified in Power Virtual Agents during Teams Meetings, requiring no user interaction (that we study below).

- In both cases, the root cause involved Teams apps with isFullTrust set to true, allowing them to communicate with the main Teams window using postMessage().

- These apps also had overly broad validDomains lists, enabling cross-window communication with domains that could be compromised or misused.


## MSRC case study III – 0-click XSS through Power Virtual Agents in Teams

#### App manifest settings that matter

![A close up of a website Description automatically generated](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__6466fbf4?scl=1)![A close up of a white background Description automatically generated](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__d3b2fc39?scl=1)

Every Teams app includes a manifest—a JSON file that defines its capabilities and trusted domains. Two fields are especially relevant for postMessage security:

- validDomains: Lists the domains trusted for postMessage, iframe embedding, and API calls. If this list includes wildcards like \*.microsoft.com or \*.powerapps.com, it dramatically increases the attack surface.

- Cross-window Communication: Apps can only use postMessage() between the main Teams window, meeting window, and pop-ups if the target domain is listed in validDomains.


#### Attack vector: Manifest misconfiguration

The attack vector hinges on two key manifest settings in Microsoft Teams apps:

- isFullTrust: true: Grants the app permission to communicate with the main Teams window and access authentication tokens.

- validDomains: Lists the domains the app trusts for postMessage, iframe embedding, and API calls.


If a malicious actor can host code on a domain listed in validDomains, they can exploit this trust to:

- Intercept or inject postMessage traffic.

- Retrieve authentication tokens.

- Execute actions on behalf of the user—potentially across tenants.


This vector is especially dangerous when combined with XSS, dangling domains, or platforms that allow user-authored scripts.

#### Visualizing the exploit

The exploit leverages the window hierarchy in Teams, where embedded apps can communicate with the main window if trust is granted via the manifest. By injecting a malicious iframe or script into a trusted domain, the attacker can initiate a message exchange that results in the host window sending back an access token.

![](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__7c0edd8b?scl=1)

The payload was hosted at:

![A screenshot of a computer program AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__9aac91b7?scl=1)

This URL is considered trusted because it falls under \*.microsoft.com, which is listed in the validDomains of the Copilot Studio app manifest. The hosted script (teamsExploit\_fullTrust\_FilesandDocs\_graph.js) initiates a postMessage request to the Teams host window, triggering the return of an authentication token.

![A screen shot of a computer AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__bdf8f319?scl=1)

#### Exploitation setup: App share manipulation

To trigger the exploit, the attacker captures a legitimate App Share request during a Teams Meeting and replaces the Identifier field in the contentSharing payload with a base64-encoded malicious JSON object:

![A computer code with numbers and letters AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__2f78a1ad?scl=1)

Here, the appId corresponds to that of Power Virtual Agent’s. By updating the request method from PUT to POST and the API path from updateEndpointMetadata to addModality, base64 encoding this payload and replacing the identifier value in the addModality request, it is possible to get a 202 Accepted Response code:

![A screenshot of a computer AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__7db88d64?scl=1)

We see that there is an XSS alert in the victim user’s session without any interaction required on their part:

![A screenshot of a computer AI-generated content may be incorrect.](https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/2025__08__84e36451?scl=1)

###### 0-click XSS achieved

The result is a zero-click cross-site scripting (XSS) vulnerability that:

- Executes attacker-controlled code without any user interaction.

- Works across tenants, meaning a guest user from another organization can exploit the vulnerability.

- Bypasses UI-based restrictions—while the UI may prevent guest users from initiating App Share, the backend logic does not enforce this restriction, allowing the exploit to succeed.


#### Mitigation

A few simple but impactful changes can significantly reduce the attack surface:

- App-Level Hardening:

- Tighten Domain Restrictions: Avoid overly broad patterns like \*.sharepoint.com or \*.powerapps.com. These wildcard entries can inadvertently trust malicious or compromised subdomains.


#### Teams-specific controls:

- Limit Full Trust: Restrict the use of isFullTrust in Teams app manifests unless absolutely necessary.

- Adopt Nested AAD Auth: Transitioning to nested Azure Active Directory authentication flows can help isolate and contain token access.


Security tip: Consider leveraging Content Security Policy (CSP) headers—particularly iframe-src—to further constrain where your app can be embedded.

## CVE-2024-49038: A critical moment for secure design

This vulnerability, documented as [CVE-2024-49038](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-49038), was rated Critical with a CVSS score of 9.3/8.1. It highlights how even small oversights in origin validation can lead to serious security risks. The incident served as a clear reminder of why secure defaults and proactive validation are essential in modern app development.

### Microsoft’s swift response

Microsoft acted quickly to mitigate the issue in the affected application—now known as Microsoft Copilot Studio. The following changes were implemented:

- The app name was updated from “Power Virtual Agents” to “Microsoft Copilot Studio,” and chatbots were renamed to agents.

- The validDomains list was revised to remove wildcard entries that previously allowed overly broad trust relationships

- Developer URLs and supported languages were updated.

- The isFullTrust setting was reviewed and approved by privacy and security teams.

- Additional manifest hygiene was enforced, including setting IsTeamsOwned to true and ensuring showLoadingIndicator was configured for apps with tabs.


These changes were reviewed as part of Microsoft’s internal publishing process, reinforcing the importance of secure-by-default configurations and rapid response protocols.

### Customer recommendations: Reducing attack surface

To help customers proactively secure their applications and reduce risk from postMessage vulnerabilities, we recommend the following actions:

- Audit app manifests: Restrict validDomains to only those domains that are absolutely necessary. Avoid wildcards like \*.powerapps.com or \*.sharepoint.com, which can unintentionally broaden the attack surface.

- Limit privileges: Only use isFullTrust: true in Teams app manifests when essential for your scenario.

- Enforce CSP headers: Use frame-ancestors and iframe-src directives in your Content Security Policy to prevent unauthorized embedding and framing.

- Validate origins: Ensure all postMessage listeners check event.origin against a strict allowlist, never relying solely on window object references.

- Remove unused or dangling domains: Regularly review and remove any obsolete domains from your configurations to prevent them from becoming silent backdoors.

- Leverage CodeQL and dynamic analysis: Use CodeQL queries to detect insecure postMessage patterns (such as wildcard targetOrigin values or missing origin validation) and integrate dynamic analysis tools into your build pipeline to catch vulnerabilities early.


### Example CodeQL queries for customer guidance

1. **Finding postMessage Calls with Wildcard Origin**

This query flags uses of postMessage where the targetOrigin is set to “\*"—a common anti-pattern.

```
// Find postMessage calls with wildcard targetOrigin
postMessageCall
    where postMessageCall.getArgument(1).getStringValue() = "*"
```

2. **Detect Missing Origin Validation in postMessage Handlers**

This query identifies JavaScript handlers that use postMessage without validating event.origin.

```sql
import javascript

from EventHandler eh, Function f
where eh.getEventName() = "message" and
    eh.getAFunction() = f and
    not exists(f.getAChild().(IfStmt).getCondition().(BinaryExpr).getAnOperand().(PropertyAccess).getPropertyName() = "origin")
select f, "This message handler does not validate the origin of incoming messages."
```

For more advanced queries and guidance, see the [https://codeql.github.com/docs/](https://codeql.github.com/docs/).

By following these recommendations, customers can significantly reduce their exposure to postMessage-related vulnerabilities and help ensure their applications are secure by default. Security is a shared responsibility, and proactive measures—combined with Microsoft’s own mitigations—are key to protecting users at scale.

## Approaching secure by default

Securing modern cloud applications requires more than patching individual bugs—it demands a systemic shift toward secure-by-default design. The vulnerabilities uncovered in Microsoft’s postMessage implementations underscore how even well-intentioned features can become attack vectors when trust boundaries are too broad or origin validation is misapplied.

While Microsoft engineering teams (EG) bear the primary responsibility for eliminating insecure patterns—such as wildcard targetOrigin values or overly permissive validDomains—customers can take some steps to protect themselves. In scenarios where customers host their own applications or portals, such as custom Teams apps, Power Apps portals, or embedded Microsoft services, they can enforce strict Content Security Policy (CSP) headers like frame-ancestors and iframe-src to prevent unauthorized embedding and framing. They can also audit their own app manifests to avoid using isFullTrust: true unless absolutely necessary and ensure that all postMessage listeners validate event.origin. Some pre-emptive measures also include checking for the existence of XSS vulnerabilities as part of SDL practices and removing unused subdomains.

However, for Microsoft-hosted 1P apps — such as Teams, SharePoint Online, or Copilot Studio—customers do not have control over CSP headers or manifest configurations. In these cases, the responsibility lies with Microsoft to enforce secure defaults including removing wildcard domain entries, tightening origin validation, and minimizing the use of overprivileged manifest settings. While building secure defaults into our [SDL process](https://www.microsoft.com/en-us/securityengineering/sdl?msockid=0282104a6c206223010405396d0d630c), it is possible for mistakes to happen. As a best practice, security testing should be performed, and response processes followed when a security bug is found. A portion of MSRC’s team, specifically the Vulnerability and Mitigations team, conducts this sort of testing research to find and mitigate these vulnerabilities before harm comes to customers. The team regularly opens internal MSRC cases to address vulnerabilities we find. The swift mitigation of CVE-2024-49038, which involved removing wildcard domains and revising app manifest settings in Microsoft Copilot Studio, exemplifies the kind of decisive action required to protect users at scale.

Ultimately, approaching secure by default means embedding security into the architecture of every app and service—not as an afterthought, but as a foundational principle. It requires collaboration across engineering, security, and customer teams to ensure that trust is earned, not assumed, and that every message, token, and origin is treated with the scrutiny it deserves.

## Acknowledgements

Special thanks to Michael Hendrickx, Rebecca Pattee, Jeremy Tinder, and Evan Grant (@stargravy) for their contributions to this blog, and to the various Microsoft teams whose work is described in this blog.

_Jhilakshi Sharma_

_Security Researcher, MSRC_