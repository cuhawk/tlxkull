---
source: detectify
source_url: https://labs.detectify.com/how-to/tutorial-php-webshell-de-obfuscation/
title: "How-to Tutorial: PHP Webshell De-Obfuscation - Labs Detectify"
author: "Detectify"
published: 2019-05-24T13:56:12+00:00
description: "A tutorial to help readers understand manual de-obfuscation and the steps to manually de-obfuscate when needed."
---

[Home](https://labs.detectify.com/)/ [How to](https://labs.detectify.com/category/how-to/)/ [How-to Tutorial: PHP Webshell De-Obfuscation](https://labs.detectify.com/how-to/tutorial-php-webshell-de-obfuscation/)

[How to](https://labs.detectify.com/category/how-to/ "How to")

# How-to Tutorial: PHP Webshell De-Obfuscation

**5w0rdFish** May 24, 2019

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/tutorial-php-webshell-de-obfuscation/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/tutorial-php-webshell-de-obfuscation/ "Share on LinkedIn")

**I would like to introduce you to some obfuscated malicious PHP files that I had recently found on a WordPress website. I’ve written a detailed report on the [research and analysis process for the PHP Web Shell Hexedglobals.3793 variants](https://labs.detectify.com/2019/05/24/investigation-of-php-web-shell-hexedglobals-3793-variants), while this post is a how-to tutorial on the de-obfuscation.**

In this article I will be covering the following:

1. DeObfuscation Tutorial for the $GLOBALS family of malware.
2. Automated tool for Deobfuscation

## De-obfuscation tutorial

This tutorial will cover the malware know as: hexedglobals.3793 \| Kidslug \| php.obfuscated! \| [php.malware.GLOBALS.003](https://kb.sucuri.net/malware/signatures/php.malware.GLOBALS.003) \| [php.malware.GLOBALS.004](https://kb.sucuri.net/malware/signatures/php.malware.GLOBALS.004)

I have uploaded a [sample](https://github.com/Chrissy-Morgan/PHP-Webshell-DeObfuscator/blob/master/Sample.php) to my Github repository where you can use to follow along.

## **1\. Un-minify the code**

First, we need to try and make the code more understandable, well at least so it was readable to a degree, it was horrendous in its current form. We can do this via [Php Beautifier](https://www.tutorialspoint.com/online_php_formatter.htm)

![](https://labsadmin.detectify.com/app/uploads/2019/05/image8.png)

Before and after code beautification.

**Initial Analysis:**

As you can see in the picture the structure of the code is now quite prominent. As well as some other pieces of key information I will get to later.

We can see that **$GLOBALS \[‘tf7ebf’\]**  is an **Array ()** on the next line **tf7ebf** is defined as a global variable, then it states $GLOBALS being the value of $tf7ebf.

GLOBALS is used within PHP for specific reasons. If you would like to know more about GLOBALS you can find out more information in this video here [Different superglobals in PHP](https://www.youtube.com/watch?v=MsgJc2Uy-BY)

Basically, it is being used so it can interact with a predefined variable which is defined outside of the scope of the function. It’s normally only used in special circumstances so if you do see it appear in code it might warrant further investigation. $GLOBALS is used more than once within the malware.

`<?php

$u9eee3f = 896;

$GLOBALS['tf7ebf'] = Array();

global $tf7ebf;

$tf7ebf = $GLOBALS;

{

"x47x4cx4fBx41x4cx53"

}`

## **2\. De-obfuscation part 1 – Converting the Hex**

My next step was to convert the hex strings to find its value.  You can convert the hex string in an online decoder or echo out the value using php as shown below. This confirmed that it was another GLOBALS.

### ![](https://labsadmin.detectify.com/app/uploads/2019/05/PHP_Webshell_Deobfuscation_Tutorial_-_Google_Docs-768x129-1.png)

## **3\. De-obfuscation part 2 – Translating its alphabet**

Moving down into the main block, we can see in the code the **l94b537e** is repeated as well as **tf7ebf**.

What I initially saw was the pattern of variables being repeatedly used. In addition to this, the use of numbers.

We have the long string of hex being assign to l94b537e. Taking this into account, my initial thoughts were that the numbers must represent some value in the long hex string (like a key or alphabet to be used) and that each value would be called into the code and included.

So we will need to convert the long hex to ASCII to see what was being represented by the numbers:

`['l94b537e'] = "x5ex71x7cx43x7ax6ax23x6dx26x2dx44x3cx34x27x66x52x38x4

``ax29x6fx63x35x59xax51x7ex22x3fx6bx2cx65x68x61x37x4ex9

x73x3bx76x4dx42x7dx7bx55x79x4bx56x39x2fx77x6cx75x6ex2b

x78x3dx49x4cx24x62x21x46x31x3ax2ax54x70x74x45x4fx47x64

x28x5cx2ex30x5dx5bx5fx60x3ex67x53x32x36x69x40x5ax20x41

x57x25x58x48xdx50x33x72";

$tf7ebf[$tf7ebf['l94b537e'][81] . $tf7ebf['l94b537e'][96] . $tf7ebf['l94b537e'][62] . $tf7ebf['l94b537e'][62] .\
\
continues ...`\
\
Once again we can echo this out.\
\
![](https://labsadmin.detectify.com/app/uploads/2019/05/PHP_Webshell_Deobfuscation_Tutorial_-_Google_Docs-2-768x110-1.png)\
\
This then gives us a long line of characters.\
\
![](https://labsadmin.detectify.com/app/uploads/2019/05/PHP_Webshell_Deobfuscation_Tutorial_-_Google_Docs-3-768x122-1.png)\
\
An alternative is to use a site such as [UnPHP](https://www.unphp.net/) which will  give us the same output.\
\
![](https://labsadmin.detectify.com/app/uploads/2019/05/decodedoutput.png)\
\
**Alphabet Obfuscation breakdown:** Our alphabet is completely random, but I assumed that once called in the right order they would become readable variables.\
\
``['l94b537e'] = "^q|Czj#m&-D<4'fR8J)oc5YxaQ~" ? k, eha7Nx9s;vMB} {    UyKV9 / wlun + x = IL $b!F1 : *TptEOGd(.0][_`>gS26i@Z AW%XHxdP3r";``\
\
I would need to do a string replace, so for every number it would look up the corresponding character.\
\
I wrote a very basic PHP script which just printed out the values of each hex value given in the array as ASCII values and give it an index. _Sidenote_ _– I had to do some basic tinkering adding quotation marks for it to work._\
\
`\
\
<?php $array = array ("x5e","x71","x7c","x43","x7a","x6a","x23","x6d","x26","x2d","\
\
x44","x3c","x34","x27","x66","x52","x38","x4a","x29","x6f","x\
\
63","x35","x59","xa","x51","x7e","x22","x3f","x6b","x2c","x65"\
\
,"x68","x61","x37","x4e","x9","x73","x3b","x76","x4d","x42","\
\
x7d","x7b","x55","x79","x4b","x56","x39","x2f","x77","x6c","x7\
\
5","x6e","x2b","x78","x3d","x49","x4c","x24","x62","x21","x46"\
\
,"x31","x3a","x2a","x54","x70","x74","x45","x4f","x47","x64","\
\
x28","x5c","x2e","x30","x5d","x5b","x5f","x60","x3e","x67","x\
\
53","x32","x36","x69","x40","x5a","x20","x41","x57","x25","x58\
\
","x48","xd","x50","x33","x72");\
\
print_r($array);\
\
?>`\
\
**_This gave me the result:_**\
\
`Array\
\
(\
\
    [0] => ^\
\
    [1] => q\
\
    [2] => |\
\
    [3] => C\
\
    [4] => z\
\
    [5] => j\
\
    [6] => #\
\
    [7] => m\
\
    [8] => &\
\
    [9] => -\
\
    [10] => D\
\
    [11] => <\
\
    [12] => 4   continues to ...    [97] => r`\
\
We now have our alphabet coming together and corresponding number.\
\
So, what you can do now is manually go through the script and update each number with its corresponding letter or you can write a script to help! Manually de-obfuscating is a simple process but can be a time intensive. To help aid you through to de-obfuscation process and save you time I have created a script which automates for this malware family.\
\
**Automated Method – Variable Names Alphabet Soup Script! – Python** The fantastic @iamrasting helped me put together a python script which takes the hex and replaces our alphabet correctly to the right numbered variable. This takes a lot of pain away from the process. It’s called [Alphabet Key](https://github.com/Chrissy-Morgan/PHP-Webshell-DeObfuscator/blob/master/Alphabet-Key.py) and will print to console the numbers replaced by letters.\
\
I have then built upon this to create [Alphabet Soup](https://github.com/Chrissy-Morgan/PHP-Webshell-DeObfuscator) to take in a webshell PHP file, de-obfuscates and outputs a text file where everything has been de-obfuscated and ready for viewing in its altered state.   Depending on what version you use you may need to still do an iteration of find and replace with the now viewable variables defined at the start of the code.\
\
![](https://labsadmin.detectify.com/app/uploads/2019/05/Screenshot-2019-05-24-at-14.06.33-768x398-1.png)\
\
The script can be found on Github [here.](https://github.com/Chrissy-Morgan/PHP-Webshell-DeObfuscator)\
\
For the purpose of the tutorial and so you can understand what is happening under the hood I will show how to progress manually with the find and the replace. This shows you how to do it without the tool. If you use the above tool it will help cut down the time spent by creating the list of variables required to be further used for find and replace iteration.  You may want to take a look at the Sample-GLOBALS which has the Sample file with all the variables converted to $GLOBALS required in order to run the script alphabet key script.\
\
**Manual Method – Variable names** With the use of the alphabet created from the array we need to look at the first section of code and repeat with each section.\
\
|     |     |\
| --- | --- |\
| $tf7ebf\[$GLOBALS\[‘l94b537e’\]\[81\] . | $GLOBALS\[$GLOBALS\[‘alph’\]\[g\] |\
| $tf7ebf\[‘l94b537e’\]\[96\] . | . $GLOBALS\[‘alph ‘\]\[3\] |\
| $tf7ebf\[‘l94b537e’\]\[62\] . | . $GLOBALS\[‘alph’\]\[1\] |\
| $tf7ebf\[‘l94b537e’\]\[62\] . | . $GLOBALS\[‘alph’\]\[1\] |\
| $tf7ebf\[‘l94b537e’\]\[20\] . | . $GLOBALS\[‘alph’\]\[c\] |\
| $tf7ebf\[‘l94b537e’\]\[12\]\] | . $GLOBALS\[‘alph’\]\[4\]\] |\
| = | = |\
| $tf7ebf\[‘l94b537e’\]\[20\] . | $GLOBALS\[‘alph’\]\[c\] |\
| $tf7ebf\[‘l94b537e’\]\[31\] . | . $GLOBALS\[‘alph’\]\[h\] |\
| $tf7ebf\[‘l94b537e’\]\[97\]; | . $GLOBALS\[‘alph’\]\[r\]; |\
\
We know that $GLOBALS = $GLOBALS so I have replaced all instances of this in the table also.\
\
We know that ‘l94b537e’ is refers to the alphabet so I have replaced that with alph.\
\
Now looking at this code it now starting to make a bit more sense. The next iteration of changes is to remove the references of $GLOBALS and alpha that are not required. Because from looking at the code, it has become apparent that these were only needed to reference the alphabet, look up the value and append. Now we know the value we can remove.\
\
|     |     |\
| --- | --- |\
| $GLOBALS\[$GLOBALS\[‘alph’\]\[g\] | $GLOBALS\[g\] |\
| . $GLOBALS\[‘alph ‘\]\[3\] | \[3\] |\
| . $GLOBALS\[‘alph’\]\[1\] | \[1\] |\
| . $GLOBALS\[‘alph’\]\[1\] | \[1\] |\
| . $GLOBALS\[‘alph’\]\[c\] | \[c\] |\
| . $GLOBALS\[‘alph’\]\[4\]\] | \[4\]\] |
| = | = |
| $GLOBALS\[‘alph’\]\[c\] | \[c\] |
| . $GLOBALS\[‘alph’\]\[h\] | \[h\] |
| . $GLOBALS\[‘alph’\]\[r\] | \[r\] |

It should start looking a little bit like this below. We will need to continue stripping the spaces and the “\[‘  ‘\]” characters away. It will start to come together as you start removing the characters not required.

![](https://labsadmin.detectify.com/app/uploads/2019/05/PHP_Webshell_Deobfuscation_Tutorial_-_Google_Docs-5-768x127-1.png)

Once we have done this our first line converts to:

$GLOBALS g311c4=chr;

## **4\. De-obfuscation part 3 – Find and Replace**

There are many replacements to make throughout the file.

I would suggest doing the next part in sections to save you removing or replacing code that could be needed. Best way I have found to do this is in notepadd++ and select the code that needs to be edited and then go through removing all the unneeded such as the ‘ and brackets \[ \] .

![](https://labsadmin.detectify.com/app/uploads/2019/05/image5.png)

You will then be able to do a find and replace with the deobfuscated variable names defined at the top of the code.

So where we had $GLOBALS g311c4 = chr; We can now search through the code for g311c4 and replace with “chr”. There will still be some variables with odd names, but you can replace with meaningful names to help you read the code better.

![](https://labsadmin.detectify.com/app/uploads/2019/05/image4.png)

You should then start to see what the code is doing and being able to make sense of the behaviour.

## **Conclusion**

What has been covered in the tutorial section should give you some understanding towards manual de-obfuscation and give you a good grounding on the steps to take the next time you come up against some obfuscated malware which you may need to manually de-obfuscate.  A tool has been created to help with this process and to check your obfuscated code against.

The analysis of this code and it’s overall behaviour is covered in the Investigation of the $GLOBALS PHP Malware.  (link to next article)

**If you are reading this because you have found similar on your server here are some handy links to help remove and prevent in the future**

[https://codex.wordpress.org/FAQ\_My\_site\_was\_hacked](https://codex.wordpress.org/FAQ_My_site_was_hacked)

[https://codex.wordpress.org/Hardening\_WordPress](https://codex.wordpress.org/Hardening_WordPress)

**Shoutouts:**

Tall Panda, @timmehwhimmey @duniel\_pls @bufferofStyx for giving thoughts and suggestions during early stages.

@iamrasting – For reviewing original script created and contributing to the  script that can be used to assist in de-obfuscating this type of malware Alphabet Key.

[Twitter](https://twitter.com/intent/tweet?url=https://labs.detectify.com/how-to/tutorial-php-webshell-de-obfuscation/ "Share on Twitter") [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://labs.detectify.com/how-to/tutorial-php-webshell-de-obfuscation/ "Share on LinkedIn")

**5w0rdFish**

Security Researcher

## Check out more content

External Attack Surface Management (EASM) is the continuous discovery, analysis, and monitoring of an organization’s public facing assets. A substantial part of EASM is the …

January 13, 2023

TL/DR: Web applications have both authentication and authorization as key concepts and if bypassed by an attacker, it can compromise sensitive data. With threats such …

August 05, 2022

TL/DR: It’s becoming increasingly easy to compromise sensitive information for attackers to take advantage of. In this post, Detectify security researcher Alfred Berg wrote about …

June 16, 2022

TL/DR: Web applications can be exploited to gain unauthorized access to sensitive data and web servers. Threats include SQL Injection, Code Injection, XSS, Defacement, and …

May 16, 2022