---
source: spaceraccoon
source_url: https://spaceraccoon.dev/embedding-payloads-bypassing-controls-microsoft-infopath/
title: "Embedding Payloads and Bypassing Controls in Microsoft InfoPath | Spaceraccoon's Blog"
published: 2022-06-18T10:00:00+00:00
description: "While browsing a SharePoint instance recently, I came across an interesting URL. The page itself displayed a web form that submitted data to SharePoint. Intrigued by the .xsn extension, I downloaded the file and started investigating what turned out to be Microsoft InfoPath’s template format. Along the way, I discovered parts of the specification that enabled loading remote payloads, bypassing war"
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Embedding Payloads and Bypassing Controls in Microsoft InfoPath

Jun 18, 2022
·

1158 words

·

6 minute read


While browsing a SharePoint instance recently, I came across an interesting URL in the form `https://<server>/_layouts/FormServer.aspx?XsnLocation=https://<server>/resource/Forms/template.xsn`. The page itself displayed a web form that submitted data to SharePoint. Intrigued by the `.xsn` extension, I downloaded the file and started investigating what turned out to be [Microsoft InfoPath’s](https://www.microsoft.com/en-us/download/details.aspx?id=48734) template format. Along the way, I discovered parts of the specification that enabled loading remote payloads, bypassing warning dialogs, and other interesting behaviour.

# Microsoft InfoWhat? [🔗](https://spaceraccoon.dev/embedding-payloads-bypassing-controls-microsoft-infopath/\#microsoft-infowhat)

You probably haven’t heard from InfoPath in a while - it was last bundled in Microsoft Office 2013, but continues to be available for Office 365 subscribers and is also embedded into SharePoint as a service. It has since been deprecated in favour of [PowerApps](https://powerapps.microsoft.com/en-us/), but thanks to Microsoft’s famous backward compatibility, continues to enjoy extended support up till 2026. In short, expect to see InfoPath continue popping up, especially in large enterprise environments.

InfoPath allows users to both design (saved as `.xsn` files) and fill forms. Additionally, as per Wikipedia, InfoPath supports a vast array of interactivity:

- Rules for event handlers
- Data validation
- Conditional formatting
- ActiveX Controls
- XPath expressions and functions
- External datasources such as SQL, Microsoft Access, and SharePoint
- JScript, VBScript, Visual Basic, C#, and other languages
- Custom HTML taskpanes
- SharePoint integration
- User roles

All this functionality creates a warren of rabbit holes to hide in and exploit, but InfoPath implements a fairly robust [three-tier security level model](https://docs.microsoft.com/en-us/office/client-developer/infopath/form-templates/about-the-security-model-for-form-templates-with-code#infopath-domain-access-security-levels): Restricted, Domain, and Full Trust. Each level has varying degrees of permissions, with Restricted forms unable to execute any managed code (C#, VBA) while Full Trust is able to execute any code. Meanwhile, Domain-level forms are limited to a defined publication domain for that form (e.g. a form published to a specific SharePoint URL) and security zones defined by Microsoft Internet Explorer.

Furthermore, typical workarounds like P/Invoke and loading unmanaged code are blocked; dangerous ActiveX controls and managed code assemblies without the `AllowPartiallyTrustedCallersAttribute` require either fully-trusted forms or cannot be loaded at all. This is problematic for Red Teamers because Full Trust forms need to be signed and create a warning prompt. [Obscurity Labs’ InfoPath phishing article](https://malware.news/t/the-phishing-path-to-info-we-missed/16605) did not bypass this and instead relied on spoofing the self-signed certificate’s author name.

![Self-Signed Certificate Warning](https://spaceraccoon.dev/images/21/self_signed_certificate_warning.png)

However, I was more interested in finding bypasses to the security model.

# Bypassing Managed Code Warning [🔗](https://spaceraccoon.dev/embedding-payloads-bypassing-controls-microsoft-infopath/\#bypassing-managed-code-warning)

One interesting bypass I discovered was related to the managed code warning dialog. Whenever a form includes managed code (C#, VBA), the following dialog pops up and must be accepted before executing the code:

![Managed Code Warning](https://spaceraccoon.dev/images/21/managed_code_warning.png)

Domain-level forms can still execute managed code without dangerous assemblies like `System.Diagnostics.Process`, but can still leak information like the username and computer name through the `Microsoft.Office.InfoPath.LoginName` property. As such, it would be nice to do this without triggering the pesky dialog. To do so, it’s necessary to dive into the structure of the `.xsn` formats.

Unlike other Microsoft Office formats like `.docx`, which are essentially ZIP files containing XML manifests and resources, `.xsn` files are CAB compressed files. The CAB extracts to the following:

1. `manifest.xsf`: Manifest file describing the form.
2. `myschema.xsd`: Data sources and fields schema
3. `template.xml`: Sample of form template
4. `sampledata.xml`: Sample of form data
5. Resource files: Other resource files included in the form

When managed code is added to the form, `manifest.xsf` refers to the compiled DLL as a `rootAssembly` file type:

```xml
			<xsf:file name="Form_Calc.dll">
				<xsf:fileProperties>
					<xsf:property name="fileType" type="string" value="rootAssembly"></xsf:property>
				</xsf:fileProperties>
			</xsf:file>
```

In turn, `Form_Calc.dll` is bundled into the CAB as-is.

The manifest also explicitly declares the existence of managed code in the form:

```xml
		<xsf:extension name="SolutionDefinitionExtensions">
			<xsf2:solutionDefinition runtimeCompatibility="client server" allowClientOnlyCode="no">
				<xsf2:offline openIfQueryFails="yes" cacheQueries="yes"></xsf2:offline>
				<xsf2:managedCode projectPath="C:\Users\IEUser\Documents\InfoPath Projects\Form-Calc1\Form-Calc.csproj" language="CSharp" version="15.0" enabled="yes"></xsf2:managedCode>
				<xsf2:server formLocale="en-US" isPreSubmitPostBackEnabled="no" isMobileEnabled="no"></xsf2:server>
			</xsf2:solutionDefinition>
		</xsf:extension>
```

Interestingly, by flipping the `enabled` property in the `xsf2:managedCode` node to `no`, the code now executes without having to click through the warning dialog! Not sure if this is a business logic error or a delayed popup…

# No Publish Location [🔗](https://spaceraccoon.dev/embedding-payloads-bypassing-controls-microsoft-infopath/\#no-publish-location)

When creating Domain-level form templates, InfoPath specifies the `publishUrl` property in the manifest:

```xml
<xsf:xDocumentClass solutionFormatVersion="15.0.0.0" solutionVersion="1.0.0.3" productVersion="15.0.0" requireFullTrust="yes" publishUrl="C:\Users\IEUser\Desktop\Form-Calc.xsn" name="urn:schemas-microsoft-com:office:infopath:Form-Calc:-myXSD-2022-05-25T14-32-18" ...>
```

This is used as part of the Domain security control, which restricts the form to the location specified at `publishUrl`. For example, if a Domain-level form is opened outside of the specified location, the following error will occur.

![Changed Publish Location Error](https://spaceraccoon.dev/images/21/changed_published_location_error.png)

Weirdly enough, for certain classes of forms (e.g. without managed code but with included scripts like JScript), simply removing the entire `publishUrl` property in the manifest allows Domain-level forms to still be opened without triggering this error. This makes it easier to deliver higher-privileged Domain-level forms without falling back to the low-privileged Restricted forms.

# Opening Arbitrary Files in Custom Taskpanes [🔗](https://spaceraccoon.dev/embedding-payloads-bypassing-controls-microsoft-infopath/\#opening-arbitrary-files-in-custom-taskpanes)

One really interesting feature of InfoPath filler-mode forms (i.e. those meant to be filled on desktops rather than published to SharePoint or the web) is their support for custom task panes. Those are ostensibly custom HTML files users can embed into a side panel in InfoPath that opens automatically with the form. Both remote and embedded URLs can be used. For example, setting the task pane location to [https://evil.com](https://evil.com/):

![Custom Taskpane Options](https://spaceraccoon.dev/images/21/custom_taskpane_options.png)

Will display the site as-is in the Filler view.

![Custom Taskpane Remote](https://spaceraccoon.dev/images/21/custom_taskpane_remote.png)

However, for remote URLs, this also triggers a remote connection warning.

![Remote Connection Warning](https://spaceraccoon.dev/images/21/remote_connection_warning.png)

This can be easily avoided by referencing an embedded resource file instead.

Interestingly, even though the GUI and documentation only allows you to embed `.html` files, I could directly edit the `href` value of the `xsf:taskpane` node in the manifest to reference non-HTML files! Custom URIs were also supported.

```xml
<xsf:taskpane caption="test" href="calc.exe"></xsf:taskpane>
```

Since the taskpane was opened in Internet Explorer Engine (RIP), I could also run `.hta` and JScript, as well as executables. For non-default IE files, this would prompt a typical Run/Save dialog. This works even in Windows 11 because the taskpane uses the Internet Explorer engine rather than the browser itself, which is still retained for exactly such compatibility scenarios. As Internet Explorer rides into the sunset, this increases the likelihood of old-school memory corruption bugs in the JScript engine or similar cropping up. As such, other than serving as a convenient way to deliver executable payloads, there’s the potential to deliver a no-click exploit.

# What About Follina? [🔗](https://spaceraccoon.dev/embedding-payloads-bypassing-controls-microsoft-infopath/\#what-about-follina)

With all this talk about embedding custom URL and HTML files, you might be wondering whether the [`ms-msdt` custom URI/Follina vulnerability](https://msrc-blog.microsoft.com/2022/05/30/guidance-for-cve-2022-30190-microsoft-support-diagnostic-tool-vulnerability/) could be used here. Unfortunately, by the time I tested it, it no longer worked - perhaps because InfoPath does not bake in the same custom URI whitelist for `ms-msdt` as the other Office applications like Word. Nevertheless, the door remains open for similar attacks given the ability to embed custom URIs and HTML files using custom taskpanes.

# Yet Another Payload Delivery Mechanism [🔗](https://spaceraccoon.dev/embedding-payloads-bypassing-controls-microsoft-infopath/\#yet-another-payload-delivery-mechanism)

Experimenting with InfoPath turned up a few ways I could exploit to deliver payloads or execute code. While the three-tier security model resisted naive attacks, I found ways to tweak the manifest directly to trigger interesting behaviour. Given how embedded resources like OLEs and [backward compatibilities](https://spaceraccoon.dev/all-your-d-base-are-belong-to-us-part-2-code-execution-in-microsoft-office/) continue to plague Microsoft Office products, I think it’s useful to experiment with seemingly-deprecated products to discover zombie bugs and gadgets.

[desktop](https://spaceraccoon.dev/tags/desktop) [red team](https://spaceraccoon.dev/tags/red-team)