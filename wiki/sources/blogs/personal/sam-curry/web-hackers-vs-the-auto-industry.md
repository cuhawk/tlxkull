---
source: sam-curry
source_url: https://samcurry.net/web-hackers-vs-the-auto-industry
title: "Web Hackers vs. The Auto Industry: Critical Vulnerabilities in Ferrari, BMW, Rolls Royce, Porsche, and More"
author: "Sam Curry"
published: 2023-01-03T00:00:00.000Z
description: "While we were visiting the University of Maryland, we came across a fleet of electric scooters scattered across the campus and couldn't resist poking at the scooter's mobile app. To our surprise, our actions caused the horns and headlights on all of the scooters to turn on and stay on for 15 minutes straight."
---

[Back to blog](https://samcurry.net/)

# Web Hackers vs. The Auto Industry: Critical Vulnerabilities in Ferrari, BMW, Rolls Royce, Porsche, and More

January 3, 2023

![Web Hackers vs. The Auto Industry: Critical Vulnerabilities in Ferrari, BMW, Rolls Royce, Porsche, and More](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fo2WUB2y.png&w=3840&q=75)

During the fall of 2022, a few friends and I took a road trip from Chicago, IL to Washington, DC to attend a cybersecurity conference and (try) to take a break from our usual computer work.

While we were visiting the University of Maryland, we came across a fleet of electric scooters scattered across the campus and couldn't resist poking at the scooter's mobile app. To our surprise, our actions caused the horns and headlights on all of the scooters to turn on and stay on for 15 minutes straight.

Oops - YouTube

Tap to unmute

[Oops](https://www.youtube.com/watch?v=YRAy3wv5SCk) [Sam Curry](https://www.youtube.com/channel/UC3raaHRLbOIG6r-TEKyVa_g)

![thumbnail-image](https://yt3.ggpht.com/ytc/AIdro_n3zSO5hY0Ih0hGiswPyvVeiObravzACVXkQ6CVSkpARbM=s68-c-k-c0x00ffffff-no-rj)

Sam Curry760 subscribers

When everything eventually settled down, we sent a report over to the scooter manufacturer and became super interested in trying to more ways to make more things honk. We brainstormed for a while, and then realized that nearly every automobile manufactured in the last 5 years had nearly identical functionality. If an attacker were able to find vulnerabilities in the API endpoints that vehicle telematics systems used, they could honk the horn, flash the lights, remotely track, lock/unlock, and start/stop vehicles, completely remotely.

At this point, we started a group chat and all began to work with the goal of finding vulnerabilities affecting the automotive industry. Over the next few months, we found as many car-related vulnerabilities as we could. The following writeup details our work exploring the security of telematic systems, automotive APIs, and the infrastructure that supports it.

## Findings Summary

During our engagement, we found the following vulnerabilities in the companies listed below:

- **Kia, Honda, Infiniti, Nissan, Acura**
  - Fully remote lock, unlock, engine start, engine stop, precision locate, flash headlights, and honk vehicles using only the VIN number
  - Fully remote account takeover and PII disclosure via VIN number (name, phone number, email address, physical address)
  - Ability to lock users out of remotely managing their vehicle, change ownership
    - For Kia's specifically, we could remotely access the 360-view camera and view live images from the car
- **Mercedes-Benz**
  - Access to hundreds of mission-critical internal applications via improperly configured SSO, including…
    - Multiple Github instances behind SSO
    - Company-wide internal chat tool, ability to join nearly any channel
    - SonarQube, Jenkins, misc. build servers
    - Internal cloud deployment services for managing AWS instances
    - Internal Vehicle related APIs
  - Remote Code Execution on multiple systems
  - Memory leaks leading to employee/customer PII disclosure, account access
- **Hyundai, Genesis**
  - Fully remote lock, unlock, engine start, engine stop, precision locate, flash headlights, and honk vehicles using only the victim email address
  - Fully remote account takeover and PII disclosure via victim email address (name, phone number, email address, physical address)
  - Ability to lock users out of remotely managing their vehicle, change ownership
- **BMW, Rolls Royce**
  - Company-wide core SSO vulnerabilities which allowed us to access any employee application as any employee, allowed us to…
    - Access to internal dealer portals where you can query any VIN number to retrieve sales documents for BMW
    - Access any application locked behind SSO on behalf of any employee, including applications used by remote workers and dealerships
- **Ferrari**
  - Full zero-interaction account takeover for any Ferrari customer account
  - IDOR to access all Ferrari customer records
  - Lack of access control allowing an attacker to create, modify, delete employee "back office" administrator user accounts and all user accounts with capabilities to modify Ferrari owned web pages through the CMS system
  - Ability to add HTTP routes on api.ferrari.com (rest-connectors) and view all existing rest-connectors and secrets associated with them (authorization headers)
- **Spireon**
  - Multiple vulnerabilities, including:
    - Full administrator access to a company-wide administration panel with ability to send arbitrary commands to an estimated 15.5 million vehicles (unlock, start engine, disable starter, etc.), read any device location, and flash/update device firmware
    - Remote code execution on core systems for managing user accounts, devices, and fleets. Ability to access and manage all data across all of Spireon
    - Ability to fully takeover any fleet (this would've allowed us to track & shut off starters for police, ambulances, and law enforcement vehicles for a number of different large cities and dispatch commands to those vehicles, e.g. "navigate to this location")
    - Full administrative access to all Spireon products, including the following…
      - GoldStar - [https://www.spireon.com/products/goldstar/](https://www.spireon.com/products/goldstar/)
      - LoJack - [https://www.spireon.com/products/goldstar/lojackgo/](https://www.spireon.com/products/goldstar/lojackgo/)
      - FleetLocate - [https://www.spireon.com/products/fleetlocate-for-fleet-managers/](https://www.spireon.com/products/fleetlocate-for-fleet-managers/)
      - NSpire - [https://www.spireon.com/spireon-nspire-platform/](https://www.spireon.com/spireon-nspire-platform/)
      - Trailer & Asset - [https://www.spireon.com/solutions/trailer-asset-managers/](https://www.spireon.com/solutions/trailer-asset-managers/)
    - In total, there were…
      - 15.5 million devices (mostly vehicles)
      - 1.2 million user accounts (end user accounts, fleet managers, etc.)
- **Ford**
  - Full memory disclosure on production vehicle Telematics API discloses
    - Discloses customer PII and access tokens for tracking and executing commands on vehicles
    - Discloses configuration credentials used for internal services related to Telematics
    - Ability to authenticate into customer account and access all PII and perform actions against vehicles
  - Customer account takeover via improper URL parsing, allows an attacker to completely access victim account including vehicle portal
- **Reviver**
  - Full super administrative access to manage all user accounts and vehicles for all Reviver connected vehicles. An attacker could perform the following:
    - Track the physical GPS location and manage the license plate for all Reviver customers (e.g. changing the slogan at the bottom of the license plate to arbitrary text)
    - Update any vehicle status to "STOLEN" which updates the license plate and informs authorities
    - Access all user records, including what vehicles people owned, their physical address, phone number, and email address
    - Access the fleet management functionality for any company, locate and manage all vehicles in a fleet
- **Porsche**
  - Ability to send retrieve vehicle location, send vehicle commands, and retrieve customer information via vulnerabilities affecting the vehicle Telematics service
- **Toyota**
  - IDOR on Toyota Financial that discloses the name, phone number, email address, and loan status of any Toyota financial customers
- **Jaguar, Land Rover**
  - User account IDOR disclosing password hash, name, phone number, physical address, and vehicle information
- **SiriusXM Connected Vehicle Services**
  - Leaked AWS keys with full organizational read/write S3 access, ability to retrieve all files including (what appeared to be) user databases, source code, and config files for SiriusXM Connected Vehicle Services

## Vulnerability Writeups

### (1) Full Account Takeover on BMW and Rolls Royce via Misconfigured SSO

While testing BMW assets, we identified a custom SSO portal for employees and contractors of BMW. This was super interesting to us, as any vulnerabilities identified here could potentially allow an attacker to compromise any account connected to all of BMWs assets.

For instance, if a dealer wanted to access the dealer portal at a physical BMW dealership, they would have to authenticate through this portal. Additionally, this SSO portal was used to access internal tools and related devops infrastructure.

The first thing we did was fingerprint the host using OSINT tools like gau and ffuf. After a few hours of fuzzing, we identified a WADL file which exposed API endpoints on the host via sending the following HTTP request:

```http
GET /rest/api/application.wadl HTTP/1.1
Host: xpita.bmwgroup.com
```

The HTTP response contained all available REST endpoints on the xpita host. We began enumerating the endpoints and sending mock HTTP requests to see what functionality was available.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage-one.png&w=3840&q=75)

One immediate finding was that we were able to query all BMW user accounts via sending asterisk queries in the user field API endpoint. This allowed us to enter something like "sam\*" and retrieve the user information for a user named "sam.curry" without having to guess the actual username.

**HTTP Request**

```http
GET /reset/api/users/example* HTTP/1.1
Host: xpita.bmwgroup.com
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-type: application/json

{"id":"redacted","firstName":"Example","lastName":"User","userName":"example.user"}
```

Once we found this vulnerability, we continued testing the other accessible API endpoints. One particularly interesting one which stood out immediately was the "/rest/api/chains/accounts/:user\_id/totp" endpoint. We noticed the word "totp" which usually stood for one-time password generation.

When we sent an HTTP request to this endpoint using the SSO user ID gained from the wildcard query paired with the TOTP endpoint, it returned a random 7-digit number. The following HTTP request and response demonstrate this behavior:

**HTTP Request**

```http
GET /rest/api/chains/accounts/unique_account_id/totp HTTP/1.1
Host: xpita.bmwgroup.com
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-type: text/plain

9373958
```

For whatever reason, it appeared that this HTTP request would generate a TOTP for the user's account. We guessed that this interaction worked with the "forgot password" functionality, so we found an example user account by querying "example\*" using our original wildcard finding and retrieving the victim user ID. After retrieving this ID, we initiated a reset password attempt for the user account until we got to the point where the system requested a TOTP code from the user's 2FA device (e.g. email or phone).

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage12-1.png&w=3840&q=75)

At this point, we retrieved the TOTP code generated from the API endpoint and entered it into the reset password confirmation field.

It worked! We had reset a user account, gaining full account takeover on any BMW employee and contractor user.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage17.png&w=3840&q=75)

At this point, it was possible to completely take over any BMW or Rolls Royce employee account and access tools used by those employees.

To demonstrate the impact of the vulnerability, we simply Googled "BMW dealer portal" and used our account to access the dealer portal used by sales associates working at physical BMW and Rolls Royce dealerships.

After logging in, we observed that the demo account we took over was tied to an actual dealership, and we could access all of the functionality that the dealers themselves had access to. This included the ability to query a specific VIN number and retrieve sales documents for the vehicle.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage5.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Ffixed.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage21.png&w=3840&q=75)

With our level of access, there was a huge amount of functionality we could've performed against BMW and Rolls Royce customer accounts and customer vehicles. We stopped testing at this point and reported the vulnerability.

The vulnerabilities reported to BMW and Rolls Royce have since been fixed.

### (2) Remote Code Execution and Access to Hundreds of Internal Tools on Mercedes-Benz and Rolls Royce via Misconfigured SSO

Early in our testing, someone in our group had purchased a Mercedes-Benz vehicle and so we began auditing the Mercedes-Benz infrastructure. We took the same approach as BMW and began testing the Mercedes-Benz employee SSO.

We weren't able to find any vulnerabilities affecting the SSO portal itself, but by exploring the SSO website we observed that they were running some form of LDAP for the employee accounts. Based on our high level understanding of their infrastructure, we guessed that the individual employee applications used a centralized LDAP system to authenticate users. We began exploring each of these websites in an attempt to find a public registration so we could gain SSO credentials to access, even at a limited level, the employee applications.

After fuzzing random sites for a while, we eventually found the "umas.mercedes-benz.com" website which was built for vehicle repair shops to request specific tools access from Mercedes-Benz. The website had public registration enabled as it was built for repair shops and appeared to write to the same database as the core employee LDAP system.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage33.png&w=3840&q=75)

We filled out all the required fields for registration, created a user account, then used our recon data to identify sites which redirected to the Mercedes-Benz SSO. The first one we attempted was a pretty obvious employee tool, it was "git.mercedes-benz.com", short for Github. We attempted to use our user credentials to sign in to the Mercedes-Benz Github and saw that we were able to login. Success!

The Mercedes-Benz Github, after authenticating, asked us to set up 2FA on our account so we could access the app. We installed the 2FA app and added it to our account, entered our code, then saw that we were in. We had access to "git.mercedes-benz.com" and began looking around.

After a few minutes, we saw that the Github instance had internal documentation and source code for various Mercedes-Benz projects including the Mercedes Me Connect app which was used by customers to remotely connect to their vehicles. The internal documentation gave detailed instructions for employees to follow if they wanted to build an application for Mercedes-Benz themselves to talk to customer vehicles and the specific steps one would have to take to talk to customer vehicles.

At this point, we reported the vulnerability, but got some pushback after a few days of waiting on an email response. The team seemed to misunderstand the impact, so they asked us to demonstrate further impact.

We used our employee account to login to numerous applications which contained sensitive information and achieved remote code execution via exposed actuators, spring boot consoles, and dozens of sensitive internal applications used by Mercedes-Benz employees. One of these applications was the Mercedes-Benz Mattermost (basically Slack). We had permission to join any channel, including security channels, and could pose as a Mercedes-Benz employee who could ask whatever questions necessary for an actual attacker to elevate their privileges across the Benz infrastructure.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage32.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage15.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage26.png&w=3840&q=75)

To give an overview, we could access the following services:

- Multiple employee-only Githubs with sensitive information containing documentation and configuration files for multiple applications across the Mercedes-Benz infrastructure
- Spring boot actuators which lead to remote code execution, information disclosure, on sensitive employee and customer facing applications


Jenkins instances
- AWS and cloud-computing control panels where we could request, manage, and access various internal systems
- XENTRY systems used to communicate with customer vehicles
- Internal OAuth and application-management related functionality for configuring and managing internal apps
- Hundreds of miscellaneous internal services

### (3) Full Account Takeover on Ferrari and Arbitrary Account Creation allows Attacker to Access, Modify, and Delete All Customer Information and Access Administrative CMS Functionality to Manage Ferrari Websites

When we began targeting Ferrari, we mapped out all domains under the publicly available domains like "ferrari.com" and browsed around to see what was accessible. One target we found was "api.ferrari.com", a domain which offered both customer facing and internal APIs for Ferrari systems. Our goal was to get the highest level of access possible for this API.

We analyzed the JavaScript present on several Ferrari subdomains that looked like they were for use by Ferrari dealers. These subdomains included \`cms-dealer.ferrari.com\`, \`cms-new.ferrari.com\` and \`cms-dealer.test.ferrari.com\`.

One of the patterns we notice when testing web applications is poorly implemented single sign on functionality which does not restrict access to the underlying application. This was the case for the above subdomains. It was possible to extract the JavaScript present for these applications, allowing us to understand the backend API routes in use.

When reverse engineering JavaScript bundles, it is important to check what constants have been defined for the application. Often these constants contain sensitive credentials or at the very least, tell you where the backend API is, that the application talks to.

For this application, we noticed the following constants were set:

```js
const i = {
    production: !0,
    envName: "production",
    version: "0.0.0",
    build: "20221223T162641363Z",
    name: "ferrari.dws-preowned.backoffice",
    formattedName: "CMS SPINDOX",
    feBaseUrl: "https://{{domain}}.ferraridealers.com/",
    fePreownedBaseUrl: "https://{{domain}}.ferrari.com/",
    apiUrl: "https://api.ferrari.com/cms/dws/back-office/",
    apiKey: "REDACTED",
    s3Bucket: "ferrari-dws-preowned-pro",
    cdnBaseUrl: "https://cdn.ferrari.com/cms/dws/media/",
    thronAdvUrl: "https://ferrari-app-gestioneautousate.thron.com/?fromSAML#/ad/"
}
```

From the above constants we can understand that the base API URL is \` [https://api.ferrari.com/cms/dws/back-office/\\\`](https://api.ferrari.com/cms/dws/back-office/%5C%60) and a potential API key for this API is \`REDACTED\`.

Digging further into the JavaScript we can look for references to \`apiUrl\` which will inform us as to how this API is called and how the API key is being used. For example, the following JavaScript sets certain headers if the API URL is being called:

```js
})).url.startsWith(x.a.apiUrl) && !["/back-office/dealers", "/back-office/dealer-settings", "/back-office/locales", "/back-office/currencies", "/back-office/dealer-groups"].some(t => !!e.url.match(t)) && (e = (e = e.clone({
    headers: e.headers.set("Authorization", "" + (s || void 0))
})).clone({
    headers: e.headers.set("x-api-key", "" + a)
}));
```

All the elements needed for this discovery were conveniently tucked away in this JavaScript file. We knew what backend API to talk to and its routes, as well as the API key we needed to authenticate to the API.

Within the JavaScript, we noticed an API call to \`/cms/dws/back-office/auth/bo-users\`. When requesting this API through Burp Suite, it leaked all of the users registered for the Ferrari Dealers application. Furthermore, it was possible to send a POST request to this endpoint to add ourselves as a super admin user.

While impactful, we were still looking for a vulnerability that affected the broader Ferrari ecosystem and every end user. Spending more time deconstructing the JavaScript, we found some API calls were being made to \`rest-connectors\`:

```js
return t.prototype.getConnectors = function() {
    return this.httpClient.get("rest-connectors")
}, t.prototype.getConnectorById = function(t) {
    return this.httpClient.get("rest-connectors/" + t)
}, t.prototype.createConnector = function(t) {
    return this.httpClient.post("rest-connectors", t)
}, t.prototype.updateConnector = function(t, e) {
    return this.httpClient.put("rest-connectors/" + t, e)
}, t.prototype.deleteConnector = function(t) {
    return this.httpClient.delete("rest-connectors/" + t)
}, t.prototype.getItems = function() {
    return this.httpClient.get("rest-connector-models")
}, t.prototype.getItemById = function(t) {
    return this.httpClient.get("rest-connector-models/" + t)
}, t.prototype.createItem = function(t) {
    return this.httpClient.post("rest-connector-models", t)
}, t.prototype.updateItem = function(t, e) {
    return this.httpClient.put("rest-connector-models/" + t, e)
}, t.prototype.deleteItem = function(t) {
    return this.httpClient.delete("rest-connector-models/" + t)
}, t
```

The following request unlocked the final piece in the puzzle. Sending the following request revealed a treasure trove of API credentials for Ferrari: :

```http
GET /cms/dws/back-office/rest-connector-models HTTP/1.1
```

To explain what this endpoint's purpose was: Ferrari had configured a number of backend APIs that could be communicated with by hitting specific paths. When hitting this API endpoint, it returned this list of API endpoints, hosts and authorization headers (in plain text).

This information disclosure allowed us to query Ferrari's production API to access the personal information of any Ferrari customer. In addition to being able to view these API endpoints, we could also register new rest connectors or modify existing ones.

**HTTP Request**

```http
GET /core/api/v1/Users?email=ian@ian.sh HTTP/1.1
Host: fcd.services.ferrari.com
```

**HTTP Response**

```http
HTTP/1.1 200 OK Content-type: application/json

…"guid":"2d32922a-28c4-483e-8486-7c2222b7b59c","email":"ian@ian.sh","nickName":"ian@ian.sh","firstName":"Ian","lastName":"Carroll","birthdate":"1963-12-11T00:00:00"…
```

The API key and production endpoints that were disclosed using the previous staging API key allowed an attacker to access, create, modify, and delete any production user account. It additionally allowed an attacker to query users via email address or nickname.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage30.png&w=3840&q=75)

Additionally, an attacker could POST to the "/core/api/v1/Users/:id/Roles" endpoint to edit their user roles, setting themselves to have super-user permissions or become a Ferrari owner.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage31.png&w=3840&q=75)

This vulnerability would allow an attacker to access, modify, and delete any Ferrari customer account with access to manage their vehicle profile.

### (4) SQL Injection and Regex Authorization Bypass on Spireon Systems allows Attacker to Access, Track, and Send Arbitrary Commands to 15 million Telematics systems and Additionally Fully Takeover Fleet Management Systems for Police Departments, Ambulance Services, Truckers, and Many Business Fleet Systems

When identifying car-related targets to hack on, we found the company Spireon. In the early 90s and 2000s, there were a few companies like OnStar, Goldstar, and FleetLocate which were standalone devices which were put into vehicles to track and manage them. The devices have the capabilities to be tracked and receive arbitrary commands, e.g. locking the starter so the vehicle cannot start.

Sometime in the past, Spireon had acquired many GPS Vehicle Tracking and Management Companies and put them under the Spireon parent company.

We read through the Spireon marketing and saw that they claimed to have over 15 million connected vehicles. They offered services directly to customers and additionally many services through their subsidiary companies like OnStar.

We decided to research them as, if an attacker were able to compromise the administration functionality for these devices and fleets, they would be able to perform actions against over 15 million vehicles with very interesting functionalities like sending a cities police officers a dispatch location, disabling vehicle starters, and accessing financial loan information for dealers.

Our first target for this was very obvious: admin.spireon.com

The website appeared to be a very out of date global administration portal for Spireon employees to authenticate and perform some sort of action. We attempted to identify interesting endpoints which were accessible without authorization, but kept getting redirected back to the login.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage29.png&w=3840&q=75)

Since the website was so old, we tried the trusted manual SQL injection payloads but were kicked out by a WAF that was installed on the system

We switched to a much simpler payload: sending an apostrophe, seeing if we got an error, then sending two apostrophes and seeing if we did not get an error. This worked! The system appeared to be reacting to sending an odd versus even number of apostrophes. This indicated that our input in both the username and password field was being passed to a system which could likely be vulnerable to some sort of SQL injection attack.

For the username field, we came up with a very simple payload:

```text
victim' #
```

The above payload was designed to simply cut off the password check from the SQL query. We sent this HTTP request to Burp Suite's intruder with a common username list and observed that we received various 301 redirects to "/dashboard" for the username "administrator" and "admin".

After manually sending the HTTP request using the admin username, we observed that we were authenticated into the Spireon administrator portal as an administrator user. At this point, we browsed around the application and saw many interesting endpoints.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage18.png&w=3840&q=75)

The functionality was designed to manage Spireon devices remotely. The administrator user had access to all Spireon devices, including those of OnStar, GoldStar, and FleetLocate. We could query these devices and retrieve the live location of whatever the devices were installed on, and additionally send arbitrary commands to these devices. There was additional functionality to overwrite the device configuration including what servers it reached out to download updated firmware.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage27.png&w=3840&q=75)

Using this portal, an attacker could create a malicious Spireon package, update the vehicle configuration to call out to the modified package, then download and install the modified Spireon software.

At this point, an attacker could backdoor the Spireon device and run arbitrary commands against the device.

Since these devices were very ubiquitous and were installed on things like tractors, golf carts, police cars, and ambulances, the impact of each device differed. For some, we could only access the live GPS location of the device, but for others we could disable the starter and send police and ambulance dispatch locations.

We reported the vulnerability immediately, but during testing, we observed an HTTP 500 error which disclosed the API URL of the backend API endpoint that the "admin.spireon.com" service reached out to. Initially, we dismissed this as we assumed it was internal, but after circling back we observed that we could hit the endpoint and it would trigger an HTTP 403 forbidden error.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage13.png&w=3840&q=75)

Our goal now was seeing if we could find some sort of authorization bypass on the host and what endpoints were accessible. By bypassing the administrator UI, we could directly reach out to each device and have direct queries for vehicles and user accounts via the backend API calls.

We fuzzed the host and eventually observed some weird behavior:

By sending any string with "admin" or "dashboard", the system would trigger an HTTP 403 forbidden response, but would return 404 if we didn't include this string. As an example, if we attempted to load "/anything-admin-anything" we'd receive 403 forbidden, while if we attempted to load "/anything-anything" it would return a 404.

We took the blacklisted strings, put them in a list, then attempted to enumerate the specific endpoints with fuzzing characters (%00 to %FF) stuck behind the first and last characters.

During scanning, we saw that the following HTTP requests would return a 200 OK response:

GET /%0dadmin GET /%0ddashboard

Through Burp Suite, we sent the HTTP response to our browser and observed the response: it was a full administrative portal for the core Spireon app. We quickly set up a match and replace rule to modify GET /admin and GET /dashboard to the endpoints with the %0d prefix.

After setting up this rule, we could browse to "/admin" or "/dashboard" and explore the website without having to perform any additional steps. We observed that there were dozens of endpoints which were used to query all connected vehicles, send arbitrary commands to connected vehicles, and view all customer tenant accounts, fleet accounts, and customer accounts. We had access to everything.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage1.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage3.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fdevice-search-1.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage6.png&w=3840&q=75)

At this point, a malicious actor could backdoor the 15 million devices, query what ownership information was associated with a specific VIN, retrieve the full user information for all customer accounts, and invite themselves to manage any fleet which was connected to the app.

For our proof of concept, we invited ourselves to a random fleet account and saw that we received an invitation to administrate a US Police Department where we could track the entire police fleet.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Ffleetlocate.png&w=3840&q=75)

### (5) Mass Assignment on Reviver allows an Attacker to Remotely Track and Overwrite the Virtual License Plates for All Reviver Customers, Track and Administrate Reviver Fleets, and Access, Modify, and Delete All User Information

In October, 2022, California announced that it had legalized digital license plates. We researched this for a while and found that most, if not all of the digital license plates, were done through a company called Reviver.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage28.png&w=3840&q=75)

If someone wanted a digital license plate, they'd buy the virtual Reviver license plate which included a SIM card for remotely tracking and updating the license plate. Customers who uses Reviver could remotely update their license plates slogan, background, and additionally report if the car had been stolen via setting the plate tag to "STOLEN".

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage8.png&w=3840&q=75)

Since the license plate could be used to track vehicles, we were super interested in Reviver and began auditing the mobile app. We proxied the HTTP traffic and saw that all API functionality was done on the "pr-api.rplate.com" website. After creating a user account, our user account was assigned to a unique "company" JSON object which allowed us to add other sub-users to our account.

The company JSON object was super interesting as we could update many of the JSON fields within the object. One of these fields was called "type" and was default set to "CONSUMER". After noticing this, we dug through the app source code in hopes that we could find another value to set it to, but were unsuccessful.

At this point, we took a step back and wondered if there was an actual website we could talk to versus proxying traffic through the mobile app. We looked online for a while before getting the idea to perform a reset password on our account which gave us a URL to navigate to.

Once we opened the password reset URL, we observed that the website had tons of functionality including the ability to administer vehicles, fleets, and user accounts. This was super interesting as we now had a lot more API endpoints and functionality to access. Additionally, the JavaScript on the website appeared to have the names of the other roles that our user account could be (e.g. specialized names for user, moderator, admin, etc.)

We queried the "CONSUMER" string in the JavaScript and saw that there were other roles that were defined in the JavaScript. After attempting to update our "role" parameter to the disclosed "CORPORATE" role, we refreshed out profile metadata, then saw that it was successful! We were able to change our roles to ones other than the default user account, opening the door to potential privilige escalation vulnerabilities.

It appeared that, even though we had updated our account to the "CORPORATE" role, we were still receiving authorization vulnerabilities when logging into the website. We thought for a while until realizing that we could invite users to our modified account which had the elevated role, which may then grant the invited users the required permissions since they were invited via an intended way versus mass assigning an account to an elevated role.

After inviting a new account, accepting the invitation, and logging into the account, we observed that we no longer received authorization errors and could access fleet management functionality. This meant that we could likely (1) mass assign our account to an even higher elevated role (e.g. admin), then (2) invite a user to our account which would be assigned the appropriate permissions.

This perplexed us as there was likely some administration group which existed in the system but that we had not yet identified. We brute forced the "type" parameter using wordlists until we noticed that setting our group to the number "4" had updated our role to "REVIVER\_ROLE". It appeared that the roles were indexed to numbers, and we could simply run through the numbers 0-100 and find all the roles on the website.

The "0" role was the string "REVIVER", and after setting this on our account and re-inviting a new user, we logged into the website normally and observed that the UI was completely broken and we couldn't click any buttons. From what we could guess, we had the administrator role but were accessing the account using the customer facing frontend website and not the appropriate administrator frontend website. We would have to find the endpoints used by administrators ourselves.

Since our administrator account theoretically had elevated permissions, our first test was simply querying a user account and seeing if we could access someone else's data: this worked!

We could take any of the normal API calls (viewing vehicle location, updating vehicle plates, adding new users to accounts) and perform the action using our super administrator account with full authorization.

At this point, we reported the vulnerability and observed that it was patched in under 24 hours. An actual attacker could remotely update, track, or delete anyone's REVIVER plate. We could additionally access any dealer (e.g. Mercedes-Benz dealerships will often package REVIVER plates) and update the default image used by the dealer when the newly purchased vehicle still had DEALER tags.

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage22.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage9.png&w=3840&q=75)

![](https://samcurry.net/_next/image?url=%2Fimages%2Fweb-hackers-vs-the-auto-industry%2Fimage10.png&w=3840&q=75)

The Reviver website also offered fleet management functionality which we had full access to.

### (6) Full Remote Vehicle Access and Full Account Takeover affecting Hyundai and Genesis

This vulnerability was written up on Twitter and can be accessed on the following thread:

> We recently found a vulnerability affecting Hyundai and Genesis vehicles where we could remotely control the locks, engine, horn, headlights, and trunk of vehicles made after 2012.
>
> To explain how it worked and how we found it, we have [@\_specters\_](https://twitter.com/_specters_?ref_src=twsrc%5Etfw) as our mock car thief: [pic.twitter.com/WWyY6vFoAF](https://t.co/WWyY6vFoAF)
>
> — Sam Curry (@samwcyo) [November 29, 2022](https://twitter.com/samwcyo/status/1597695281881296897?ref_src=twsrc%5Etfw)

### (7) Full Remote Vehicle Access and Full Account Takeover affecting Honda, Nissan, Infiniti, Acura

This vulnerability was written up on Twitter and can be accessed on the following thread:

> More car hacking!
>
> Earlier this year, we were able to remotely unlock, start, locate, flash, and honk any remotely connected Honda, Nissan, Infiniti, and Acura vehicles, completely unauthorized, knowing only the VIN number of the car.
>
> Here's how we found it, and how it works: [pic.twitter.com/ul3A4sT47k](https://t.co/ul3A4sT47k)
>
> — Sam Curry (@samwcyo) [November 30, 2022](https://twitter.com/samwcyo/status/1597792097175674880?ref_src=twsrc%5Etfw)

### (8) Full Vehicle Takeover on Nissan via Mass Assignment

This vulnerability was written up on Twitter and can be accessed on the following thread:

> Good Morning, I feel like we need more car haxs. So here is another vulnerability we found that got us remote commands on every internet connected Nissan & Infiniti. Bug was fixed.
>
> shout out to [@samwcyo](https://twitter.com/samwcyo?ref_src=twsrc%5Etfw) [@bbuerhaus](https://twitter.com/bbuerhaus?ref_src=twsrc%5Etfw) [@sshell\_](https://twitter.com/sshell_?ref_src=twsrc%5Etfw) [@d0nutptr](https://twitter.com/d0nutptr?ref_src=twsrc%5Etfw) [@xEHLE\_](https://twitter.com/xEHLE_?ref_src=twsrc%5Etfw) [@iangcarroll](https://twitter.com/iangcarroll?ref_src=twsrc%5Etfw) [@sshell\_](https://twitter.com/sshell_?ref_src=twsrc%5Etfw) [@infosec\_au](https://twitter.com/infosec_au?ref_src=twsrc%5Etfw) [pic.twitter.com/5TbC9G1Oxk](https://t.co/5TbC9G1Oxk)
>
> — ꙅɿɘƚɔɘqꙅ (@\_specters\_) [November 30, 2022](https://twitter.com/_specters_/status/1597984481511903234?ref_src=twsrc%5Etfw)

## Credits

The following people contributed towards this project:

- Sam Curry ( [https://twitter.com/samwcyo](https://twitter.com/samwcyo))
- Neiko Rivera ( [https://twitter.com/ _specters_](https://twitter.com/_specters_))
- Brett Buerhaus ( [https://twitter.com/bbuerhaus](https://twitter.com/bbuerhaus))
- Maik Robert ( [https://twitter.com/xEHLE\_](https://twitter.com/xEHLE_))
- Ian Carroll ( [https://twitter.com/iangcarroll](https://twitter.com/iangcarroll))
- Justin Rhinehart ( [https://twitter.com/sshell\_](https://twitter.com/sshell_))
- Shubham Shah ( [https://twitter.com/infosec\_au](https://twitter.com/infosec_au))

Special thanks to the following people who helped create this blog post:

- Ben Sadeghipour ( [https://twitter.com/nahamsec](https://twitter.com/nahamsec))
- Joseph Thacker ( [https://twitter.com/rez0\_\_](https://twitter.com/rez0__))