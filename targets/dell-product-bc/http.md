# Dell Technologies Products Bug Bounty

## Target
- program: dell-product (Bugcrowd)
- category: bbp
- started: Oct 19, 2021
- nondisclosure: true
- partial_safe_harbor: true
- note: No collaboration

## Scope
- in: Dell-branded or currently supported PRODUCTS (hardware + software) listed below
- out: Dell Technologies web apps → submit to Dell Technologies Application Bug Bounty instead
- out: Dell Enterprise Hub (including third-party hosted models via Hugging Face)

## Bounties
### Reward Eligible Products (product list below)
- P1: $5,000
- P2: $3,000
- P3: $1,500
- P4: $200

### Non-Reward Eligible Targets
- Supported Dell products NOT on the product list: in scope but no bounty payment (points only)

## Triage Requirements
- REQUIRED: Enter Product Name and Version Number in the "URL / Location of vulnerability" field
- Reports without product name+version will be REJECTED
- Submissions with Blockers for >5 business days → closed as Not Applicable
- Must test against currently Generally Available (GA) version
- Severity via CVSS v3.1 (Dell's scoring overrides VRT)

## Product List (bounty-eligible)
### Client Solutions — Hardware
- Consumer Platforms: Inspiron, Alienware, XPS
- Commercial Platforms: Latitude, OptiPlex, Precision, Rugged, Latitude Education, Chrome, Dell Thin Client
- Dell-branded client peripherals

### Client Solutions — Software
- Alienware Command Center, OC Controls, Update
- Dell Command Configure/Integration Suite/Intel vPro/Monitor/PowerShell Provider/Repository Manager/Update
- Dell Core Services Cloud, Customer Connect, Hybrid Client, OS Recovery Tool, Optimizer
- Dell Performance Manager, Display and Peripheral Manager, Power Manager, Pro AI Studio
- Dell Remediation Platform, Rugged Control Center, SupportAssist OS Recovery
- Dell SupportAssist for Home PCs, SupportAssist for Business PCs
- Dell Telemetry Platform Service, Trusted Device, Update, Web Services
- Wyse Management Suite, Wyse Proprietary OS (Modern ThinOS)

### Infrastructure — Servers, Storage, Networking
- Common Event Enabler (CEE), Data Protection Central, Dell AppSync, Dell BSAFE
- Dell Cloud Disaster Recovery, CloudLink, Container Storage Modules, ECS
- Dell Enterprise Storage Analytics for vRealize Operations
- Dell Networking C/H/X-Series Switches
- Dell OpenManage Enterprise (Modular, Network Integration, ServiceNow, Power Manager Plugin, Server Administrator, Enterprise Services, Connections)
- Dell OpenManage Integration with Microsoft Windows Admin Center
- Dell PowerEdge 16th/17th generation servers
- Dell PowerFlex, PowerMax, PowerProtect Cyber Recovery, PowerProtect Data Manager
- Dell PowerProtect DD Series, DP Series Appliances, PowerScale, PowerStore, PowerSwitch
- Dell Repository Manager (DRM), SC Series Fibre Channel/iSCSI Drivers
- Dell SCOM SNMP Management Pack Suite, SD-WAN Edge, Secure Connect Gateway (SCG)
- Dell Server Update Utility (SUU), Storage Manager, System Update (DSU), Unity
- Dell Update Manager Plugin (UMP), Virtual Storage Integrator for VMware vSphere
- Dell VxRail HCI, Enterprise SONiC Distribution
- PowerEdge M-Series Blade Switch, SmartFabric OS10, SmartFabric Storage Software
- Transparent Snapshot Data Mover (TSDM)

### Mobile Applications
- CloudIQ, E-Lab Navigator, OpenManage Mobile

## Focus Areas
- Remote code execution as root
- Remote root login, remote configuration injection
- Local privilege escalation
- Unauthorized access to sensitive data
- Device secrets, cryptographic keys, customer credentials/PII exposure
- XSS, CSRF, SSRF, SQLi, RCE, XXE (significant impact)
- Access control, auth bypass, auth flaws, privilege escalation
- Directory traversal, sensitive info disclosure

## OOS Findings
- Application installation to insecure user-controlled path
- Out of date software versions
- CVEs/0-days <30 days since initial publication (eligible only if Dell acts on the report)
- No rate limiting or CAPTCHA
- 3rd party code (Dell not responsible)
- Physical or administrative access required
- Physical hardware tampering
- Code execution requiring full admin privileges
- Public file/directory disclosure (robots.txt)
- Clickjacking
- Login/forgot password brute force / account lockout
- API keys with no security impact
- Stack traces / component technology disclosure
- Username/email enumeration
- Malicious file uploads not affecting app server
- Cookies without HttpOnly/secure flags
- Missing defense-in-depth without exploitable weakness
- DoS attacks
- Reports from automated tools without analysis
- Open ports without PoC
- Bugs only affecting outdated browsers

## Auth
- Dell does NOT provide products for testing
- Only test Dell products you have authorized access to

## Rules
- Automated scanning: STRICTLY PROHIBITED
- DoS/DDoS: STRICTLY PROHIBITED
- Do not exploit beyond what's needed for PoC
- If inadvertently accessing others' data: report to secure@dell.com immediately

## Notes
- Same vulnerability on different products = duplicate
- CVE may be assigned; Dell Security Advisories may credit researcher with permission
- No reward for publicly disclosed vulnerabilities
- Eligibility excludes Dell employees, contractors, former employees who worked on tested products
