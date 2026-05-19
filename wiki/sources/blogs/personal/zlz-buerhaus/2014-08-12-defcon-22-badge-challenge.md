---
source: zlz-buerhaus
source_url: https://buer.haus/2014/08/12/defcon-22-badge-challenge/
title: "DEFCON 22 Badge Challenge | ziot"
---

[< Back](https://buer.haus/)

Authors: [![image](https://blog.twitter.com/sites/all/themes/gazebo/img/ios_homescreen_icon.png) Brett Buerhaus](https://twitter.com/bbuerhaus), [![image](https://blog.twitter.com/sites/all/themes/gazebo/img/ios_homescreen_icon.png) Jason Thor Hall](https://twitter.com/PotatoSec)

Original Post: http://potatohatsecurity.tumblr.com/post/94565729529/defcon-22-badge-challenge-walkthrough

Brett, Jon, and I recently went to DEFCON and completed the Badge Challenge put together by 1o57.  Here is the entire adventure as we experienced it with all of the puzzles, their solutions, and the steps to solve them.  Understand that this document contains MASSIVE spoilers so if you do not want to ruin it for yourself please stop reading now.

Still here?

Alright, lets go!

## Step\_1

* * *

Taken from page 4 of the DEFCON Pamphlet

```
07-21-18-03-18-05-05-22-01-03-14-20-18-06
10-22-25-25-21-18-25-03-12-02-08-19-22-01
17-12-02-08-05-16-14-25-25-22-01-20-15-08
07-17-02-01-07-15-18-17-08-03-18-17-16-08
07-17-02-10-01-07-21-18-10-02-02-17-06-07
21-18-12-15-18-18-05-17-02-06-10-57-10-57
```

Digit to Alphabet Replacement

1=A 2=B etc…

```
G-U-R-C-R-E-E-V-A-C-N-T-R-F
J-V-Y-Y-U-R-Y-C-L-B-H-S-V-A
Q-L-B-H-E-P-N-Y-Y-V-A-T-O-H
G-Q-B-A-G-O-R-Q-H-C-R-Q-P-H
G-Q-B-J-A-G-U-R-J-B-B-Q-F-G
U-R-L-O-R-R-E-Q-B-F-J-57-J-57
```

Cleaned up the dashes and removed 1o57’s handle.

```
GURCREEVACNTRF
JVYYURYCLBHSVA
QLBHEPNYYVATOH
GQBAGORQHCRQPH
GQBJAGURJBBQFG
URLORREQBF
```

ROT 13

[http://rumkin.com/tools/cipher/rot13.php](http://t.umblr.com/redirect?z=http%3A%2F%2Frumkin.com%2Ftools%2Fcipher%2Frot13.php&t=NWYwNDIzMzFlM2ViMGU2M2IyMDk4YTEzNDI2MDM5YzU5NGFhZmY3YSxacUcwcENnNA%3D%3D)

```
THEPERRINPAGES
WILLHELPYOUFIN
DYOURCALLINGBU
TDONTBEDUPEDCU
TDOWNTHEWOODST
HEYBEERDOS
```

Cleaned up the spacing

```
THE PERRIN PAGES
WILL HELP YOU FIND
YOUR CALLING BUT
DONT BE DUPED CUT
DOWN THE WOODS
THEY BE ERDOS
```

Open the DEFCON disc provided

This contains an image of a man.

[![](http://i.imgur.com/sKWQv8g.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%232&t=OTgxZmY2NDFkNGU2OGNjYjU4OTUwZDUzNDZmYjM4ZWYzZWJkOTRhZCxacUcwcENnNA%3D%3D)

Search for Erdos on google and find a picture of that man.

[http://en.wikipedia.org/wiki/Paul\_Erd%C5%91s](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FPaul_Erd%25C5%2591s&t=ZTdjYzcwMzc1MzZkYjI3YWFkODEyMGRhYmM2ZjhhNmVkZTY3NjQzZixacUcwcENnNA%3D%3D)

[http://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93Woods\_number](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FErd%25C5%2591s%25E2%2580%2593Woods_number&t=NjNlZTVmYzM4MjcyZTZhY2M1NzdiOGI4OWNlMmE3ZDkzNjY3Y2E4YSxacUcwcENnNA%3D%3D)

Flipping through the DEFCON pamphlet.

Many pages have a vertical number above them.

|     |     |
| --- | --- |
| Page | Vertical |
| 2 | 32 |
| 3 | 35 |
| 5 | 31 |
| 7 | 41 |
| 10 | 53 |
| 12 | 45 |
| 16 | 41 |
| 17 | 43 |
| 22 | 52 |
| 29 | 45 |
| 33 | 45 |
| 34 | 4D |
| 36 | 41 |
| 39 | 54 |
| 46 | 45 |
| 51 | 21 |
| 56 | 21 |

Take the Erdos Woods numbered pages and cut them from the set.

16, 22, 34, 36, 46, 56 (CUT DOWN THE WOODS)

|     |     |
| --- | --- |
| Page | Vertical |
| 2 | 32 |
| 3 | 35 |
| 5 | 31 |
| 7 | 41 |
| 10 | 53 |
| 12 | 45 |
| 17 | 43 |
| 29 | 45 |
| 33 | 45 |
| 39 | 54 |
| 51 | 21 |

Now for the Perrin pages.

[http://www.mathpages.com/home/kmath345/kmath345.htm](http://t.umblr.com/redirect?z=http%3A%2F%2Fwww.mathpages.com%2Fhome%2Fkmath345%2Fkmath345.htm&t=ZjQyODNkYzg0NWZmMzcxNjYzYjQ5MTFhMGFjZDhiYThlNWExYzIxYyxacUcwcENnNA%3D%3D)

(THE PERRIN PAGES WILL HELP YOU)

32:35:31:41:53:45:43:45:45:54:21

Now to cut the nearby duplicate values.

(DONT BE DUPED)

32:35:31:41:53:45:43:52:45:54

This translates to ASCII cleanly from HEX

251ASECRET

Which is the following phone number.

(FIND YOUR CALLING)

(251) 273-2738

**Calling this number leads to Step\_2.**

* * *

## Step\_2

* * *

Calling the phone number from Step\_1.

(251) 273-2738

This results in 5 rings and then a sequence of 109 piano notes.

I recorded this using some call recording software.

[http://www.speedyshare.com/SsNaU/Piano.wav](http://t.umblr.com/redirect?z=http%3A%2F%2Fwww.speedyshare.com%2FSsNaU%2FPiano.wav&t=N2NiMzFlYmQ5MWFmOTEzZGJhZTkyN2FjY2JiMmQ5ZjFjZjRhMjJhYyxacUcwcENnNA%3D%3D "http://www.speedyshare.com/SsNaU/Piano.wav")

Writing down these sounds as notes gives the following set.

```
DGGBGBGGDGBDGDGBDDDBDGEGDGDGDBDDDBGDGBDDGEDGGDGBGDDDDBDDDDDBGGGGGBDDGGGEDGGDGBGGGBGDBGDGBGDBDGBDDGBGGGGBGDBGE
```

Converting the B’s and E’s into spaces gives us the following.

```
DGG G GGDG DGDG DDD DG GDGDGD DDD GDG DDG DGGDG GDDDD DDDDD GGGGG DDGGG DGGDG GGG GD GDG GD DG DDG GGGG GD G
```

This is starting to look promising.

Converting the D’s into dashes and the G’s into dots we get the following.

```
-.. . ..-. -.-. --- -. .-.-.- --- .-. --. -..-. .---- ----- ..... --... -..-. ... .- .-. .- -. --. .... .- .
```

This is morse code and decodes into a URL.

[http://rumkin.com/tools/cipher/morse.php](http://t.umblr.com/redirect?z=http%3A%2F%2Frumkin.com%2Ftools%2Fcipher%2Fmorse.php&t=NWUxYTg5MTk2ZjhhMWVkNzkyMzFkMDdmYTY0MmQzOWRmMmY4ZjdiNSxacUcwcENnNA%3D%3D)

DEFCON.ORG/1057/SARANGHAE

Fixing the capitalization we are able to connect.

[http://defcon.org/1057/SarangHae/](http://t.umblr.com/redirect?z=http%3A%2F%2Fdefcon.org%2F1057%2FSarangHae%2F&t=OGE2Yjg1MWFkNWE1MzNmYzg3YzJkYzhhZWE5MDkwNTBiOGUyZGRmMCxacUcwcENnNA%3D%3D)

**Going to this URL leads to Step\_3a.**

* * *

## Step\_3a

* * *

Going to the URL from Step\_2.

[http://defcon.org/1057/SarangHae/](http://t.umblr.com/redirect?z=http%3A%2F%2Fdefcon.org%2F1057%2FSarangHae%2F&t=OGE2Yjg1MWFkNWE1MzNmYzg3YzJkYzhhZWE5MDkwNTBiOGUyZGRmMCxacUcwcENnNA%3D%3D)

Page source:

[Step\_3a\_Source.txt (pastebin)](http://t.umblr.com/redirect?z=http%3A%2F%2Fpastebin.com%2FDHg6fTew&t=ZWU3OTRkY2FjMzk0Njg2MmIwNDQ0NGJiZjlmN2E5YzU3OTNhNTZkNixacUcwcENnNA%3D%3D)

Picture of the page.

[![](http://i.imgur.com/2BdKetg.png)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%231&t=NjhlZjhkNDgyMzIwNjViMzliNjlmNDZmNmIyNDMyNzAxMmU1YmIwNyxacUcwcENnNA%3D%3D)

This page contains an image.

[![](http://i.imgur.com/OpXbUCL.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%230&t=Mjg2ZDk0NTBiZjgzNjQxZGZkYzk2MGUyMzU5NWVkYjk4MmU5NjY5MixacUcwcENnNA%3D%3D)

The page has a hint shown here.

```
Who we gave free love to
at
1o57
Are you being served?
```

Since we do not know who we gave free love to we have reached a dead end.

**Move on to Step\_3b**

* * *

## Step\_3b

* * *

Continue from dead end on Step\_3a

We have found a large pattern on the floor near the 1o57 room.

[![](http://i.imgur.com/x0x8cxk.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%234&t=YzY4NGEwODU0OGViZjIxNzlkODMzMTA0MDY1ZWZiYjk2NTZiZmRmNSxacUcwcENnNA%3D%3D)

[![](http://i.imgur.com/q9f5K4e.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%233&t=YzQ1ZDEwY2VkNTIxNWM0ODdlM2RhZWY4NjI2ZjFkMWJlMmFlMmU2ZCxacUcwcENnNA%3D%3D)

There are other symbols around DEFCON with different numbers and characters.

(No Images)

Taking all of the numbers we get the following list.

We also have a number of Korean symbols associated.

|     |     |     |
| --- | --- | --- |
| 전 | 화 | 기 |
| 1.23 | 0.12 | 1.13 |
| 2.23 | 0.01 | 6.12 |
| 3.23 | 0.20 | 5.23 |
| 3.13 | 6.23 | 9.12 |
| 3.22 | 3.02 | 5.11 |
| 2.22 | 4.01 | 6.13 |
| 0.00 | 8.01 | 12.02 |
| 6.22 | 6.02 | 4.23 |
| 3.01 | 3.12 | 4.13 |
| 1.02 | 9.02 | 1.11 |
| 0.20 | 5.22 | 15.02 |
| 0.03 | 4.02 | 9.22 |
| 0.10 | 2.11 | 8.22 |

Taking the Korean symbols and mixing them around we eventually come to.

전화기

This translates to Phone.

We now have a hint as to how this puzzle works.

Taking a modern phone we can see that it is laid out as follows.

```
1    2    3
4    5    6
7    8    9
*    0    #
```

Adding 0 based rows to this we get the following layout.

```
3    1    2    3
2    4    5    6
1    7    8    9
0    *    0    #
    0    1    2
```

Taking the numbers from the floor and dropping the first number.

|     |     |     |
| --- | --- | --- |
| 23 | 12 | 13 |
| 23 | 01 | 12 |
| 23 | 20 | 23 |
| 13 | 23 | 12 |
| 22 | 02 | 11 |
| 22 | 01 | 13 |
| 00 | 01 | 02 |
| 22 | 02 | 23 |
| 01 | 12 | 13 |
| 02 | 02 | 11 |
| 20 | 22 | 02 |
| 03 | 02 | 22 |
| 10 | 11 | 22 |

This associates with the Column and Row on the phone.

Example

23 = Column 2, Row 3 = 3

Decoding all of this we get the following.

|     |     |     |
| --- | --- | --- |
| 3 | 5 | 2 |
| 3 | 7 | 5 |
| 3 | # | 3 |
| 2 | 3 | 5 |
| 6 | 4 | 8 |
| 6 | 7 | 3 |
| \* | 7 | 4 |
| 6 | 4 | 3 |
| 7 | 5 | 2 |
| 4 | 4 | 8 |
| # | 6 | 4 |
| 1 | 4 | 6 |
| 0 | 8 | 6 |

Ordering this by the characters that spell the word phone we get.

```
333266*674#1057#34774546482535824328466
```

Using the letters associated on a phone and discovery of some crazy words we get the following.

```
DEFCON*ORG#1057#FISSILINGUALELUCIDATION
```

Cleaning this up we have our new target URL.

[defcon.org/1057/FissilingualElucidation](http://t.umblr.com/redirect?z=http%3A%2F%2Fdefcon.org%2F1057%2FFissilingualElucidation&t=M2QzOGFiNWU5ZTY3MzE3OTY5YjFhZGRiYjcyZGU4ZWNmOWY1YjUzNixacUcwcENnNA%3D%3D)

**Continue to Step\_3c with our newfound page.**

* * *

## Step\_3c

* * *

Going to the URL from Step\_3b

[http://defcon.org/1057/FissilingualElucidation](http://t.umblr.com/redirect?z=http%3A%2F%2Fdefcon.org%2F1057%2FFissilingualElucidation&t=M2QzOGFiNWU5ZTY3MzE3OTY5YjFhZGRiYjcyZGU4ZWNmOWY1YjUzNixacUcwcENnNA%3D%3D)

Page source:

[Step\_3c\_Source.txt (pastebin)](http://t.umblr.com/redirect?z=http%3A%2F%2Fpastebin.com%2FXmQLq5YA&t=ZTk0ZWE4NjIxYzkxMjdjZTI0NmU0YzBmODQ2NGE2YjQxOTRjZDVkYSxacUcwcENnNA%3D%3D)

Picture of the page.

[![](http://i.imgur.com/2XkPsPi.png)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%236&t=MDZjNmY5MmNjNzkzZDUzMDQxMjJlMjQ0NjRkY2ZkNTc5Mjk0N2VlZCxacUcwcENnNA%3D%3D)

This page contains an animated gif.

[![](http://i.imgur.com/SUVa10q.gif)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%235&t=YTZlY2RhOTI4ZTE0MTVkOWZiOWMwN2FhYjliNDhlYjQxMTg5M2E4MSxacUcwcENnNA%3D%3D)

The poem on this page reads as follows.

```
Here, I wrote you a poem:
lorem ip
Lorem ipsum dolor si
Lorem ipsum do
Lorem ipsum dolor s
lorem ipsum ama
Lorem ipsum dolor sit amet
Lorem ipsum dolor sit ame

Lorem ipsum dolor sit
lorem ipsum ips
lorem ipsum lor
lorem ipsum lo
lorem ipsum lorem
lorem ipsum amat
Lorem Ipsum
```

Dropping this into Google Translate we see a very interesting bug.

Our Lorem Ipsum text translates to the following.

```
Internet ip
Let's see if
We give
Pussycat Dolls
The Free Love
It can be used
Our goal is to ame

Our goal is to
vehicle dimensions
Free of pain
China, elsewhere
Free Internet
China loves
NATO
```

The source page from the site we found in step 3a\_1 talked about a poem.

It also stated “Who we gave free love to”

In this poem we see that the “free love” is given to the “Pussycat Dolls”

**Continue to Step\_3d with this new information.**

* * *

## Step\_3d

* * *

Using the newfound information from Step\_3c.

```
We give
Pussycat Dolls
The Free Love
```

We can add this to the puzzle from Step\_3a

```
Who we gave free love to
at
1o57
Are you being served?
```

This then becomes

```
PussycatDolls
at
1o57
Are you being served?
```

“Are you being served?” is a UK based comedy show.

[http://en.wikipedia.org/wiki/Are\_You\_Being\_Served%3F](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FAre_You_Being_Served%253F&t=MjJmNWUyNDZkZjA3NDQ1ZWU4NjE0MDNiOGM0NzA2NzEyNmEzODg4OSxacUcwcENnNA%3D%3D)

Adding that to the puzzle we get.

```
PussycatDolls
at
1o57
UK
```

This then becomes an email address.

PussycatDolls@1o57.uk

**Emailing anything to this address leads us to Step\_4a.**

* * *

## Step\_4a

* * *

Writing the email from Step\_3d we get the following response.

DEFCON.ORG/1057/ WHO DOES CHINA LOVE + Mickey’s Key

[![](http://i.imgur.com/XZHC7Th.png)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%237&t=NDk4MDMxYmNiMWEyZDg3MjgyZjg1OGI3OTE2N2UwMzEwNDBhMGVkZSxacUcwcENnNA%3D%3D)

We know who China loves from our previous Lorem Ipsum poem solved on Step\_3c

China loves

NATO

Our URL then becomes

defcon.org/1057/NATO + Mickey’s Key

As we have no idea what Mickey’s Key we have reached a dead end.

Move on to Step\_4b

* * *

## Step\_4b

* * *

Continue from dead end on Step\_4a

We noticed all of the convention lanyards had writing in Korean, numbers in Chinese, and a set of glyphs.

[![](http://i.imgur.com/FzTXRut.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%238&t=NTQxYWJkZGRmMTY1Zjk3ZDYyNjNkZjg0ZTgyNGUwODc1YjU0NTM5NCxacUcwcENnNA%3D%3D)

[![](http://i.imgur.com/A4xt11r.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%239&t=MDY3MWI5ZWZmMmYyMDAzODFhMGNjOGUwODlmYTk3MGU2NWU0ZWM4MyxacUcwcENnNA%3D%3D)

We rushed to record all of the lanyards much like we did with the symbols on the ground earlier.

The results of that are as follows.

|     |     |     |
| --- | --- | --- |
| Symbol | Korean | Chinese |
| Dial | 수평 | 四 |
| Skull | 수평 | 九 |
| Key | 수평 | 四 |
| Disk | 수평 | 三 |
| Dial | 수직 | 一一 |
| Skull | 수직 | 五 |
| Key | 수직 | 一四 |
| Disk | 수직 | 十 |

The Korean translates to Horizontal and Vertical.

We assumed this meant the direction the lanyards should be placed.

The Chinese characters are a set of numbers which is possibly the order in which they should be placed.

The glyphs themselves are an obscure cipher for numbers used by a group of monks in the middle ages.

[![](http://i.imgur.com/oK7SYGb.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2310&t=ZWYwNDllOGZiOGRiODA3YTI0YzU1MzQyZGQyNmU5MGI5OGNhYjU3YSxacUcwcENnNA%3D%3D)

[http://www.davidaking.org/Ciphers.htm](http://t.umblr.com/redirect?z=http%3A%2F%2Fwww.davidaking.org%2FCiphers.htm&t=ODk1NGRhOTMzZjQyMDAyNmIwYjEzNDc0NjBjZmY0NjRiYjQxZDZhNSxacUcwcENnNA%3D%3D)

If we take each glyph and cut it into quarters we get 4 unique cipher symbols resulting in a 4 digit number.

The numbers are then listed as follows.

|     |     |     |     |
| --- | --- | --- | --- |
| Symbol | Korean | Chinese | Glyphs |
| Dial | 수평 | 四 | 10 57 68 79 79 77 72 73 |
| Skull | 수평 | 九 | 83 83 79 78 83 67 79 73 |
| Key | 수평 | 四 | 78 83 73 78 65 82 67 65 |
| Disk | 수평 | 三 | 68 69 83 67 79 68 69 83 |
| Dial | 수직 | 一一 | 10 57 78 68 78 84 79 85 |
| Skull | 수직 | 五 | 67 55 84 72 79 78 83 67 |
| Key | 수직 | 一四 | 78 84 69 80 67 85 82 89 |
| Disk | 수직 | 十 | 77 73 65 73 82 73 80 84 |

Weaving the Horizontal and Vertical lanyards together we get conflicts between the Glyphs.

This results in the following pattern.

```
0100
1001
0100
0011
1011
0101
1110
1010
```

If we only take the numbers from this we get the following.

```
     6879
8383           7973
     7378
          7968 6983
1057      7884 7985
     8472      8367
7884 6980 6785
7773      8273
```

Collapsing these into a stack we get this new block.

```
8383 6879 7968 7973
1057 7378 7884 6983
7884 8472 6785 7985
7773 6980 8273 8367
```

Splitting these into blocks of two and then converting that into ASCII we get this jumbled text block.

```
SS DO OD OI
   IN NT ES
NT TH EP MI
OU SC CU RI
```

Unjumbling this block shows us the encoded message.

```
DO NT MI
SS TH EP OI
NT IN CU RI
OU SC OD ES
```

```
DONT MISS THE POINT IN CURIOUS CODES.
```

The point in curious codes is a period.

curious.codes

Continue to Step\_4c with our newfound page.

* * *

## Step\_4c

* * *

Going to the URL from Step\_4b

[curious.codes](http://t.umblr.com/redirect?z=http%3A%2F%2Fcurious.codes&t=ZmRmYTk1Y2QzYTEyMzU5ZTgzMTYyMTBjMWViYzU3NjcyOGFkOTdmZSxacUcwcENnNA%3D%3D)

Page source:

[Step\_4c\_Source.txt (pastebin)](http://t.umblr.com/redirect?z=http%3A%2F%2Fpastebin.com%2F6dEZrBEL&t=MjYxZTkwMWJiYjIyZmFiYzUzMDBhNzA4M2VkZjdhODQ0MWRkZmJiMyxacUcwcENnNA%3D%3D)

Picture of the page.

[![](http://i.imgur.com/d7ys7dg.png)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2311&t=ZTAxOGY1ZWZhODUxNmU3ZTM0YzRjOTA3Yjk5OGU5NzIzYTE3Y2NkMixacUcwcENnNA%3D%3D)

This page contains an image.

[![](http://i.imgur.com/6Aj11FV.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2312&t=ZTg0ZWI1YTQzNWYzODJjNDRiYTNkNmU4ZDZjNDdiMWI4NTFlYzIzZSxacUcwcENnNA%3D%3D)

At the bottom of the page is a link.

The link starts a file download for “NukeNukeMickeyLover”

Opening the file in a text editor we see the following.

Rar!

Converting the file to a .rar we are presented with an encrypted rar file and we don’t have the password.

With no password we have reached a dead end.

Move on to Step\_4d

* * *

## Step\_4d

* * *

Continue from dead end on Step\_4c

Time to rip open the badges.

The following are strings discovered in the source code provided on the DEFCON disc.

RayNelson byte

```
"IAIHG TPJNU QU CZR GALWXK DC MHR LANK FOTLA OTN LOYOC HPMPB PX HKICW",0
```

Test4 byte

```
"DID YOU REALLY THINK THAT IT WOULD BE SO EASY? Really? Just running strings?",0
```

Greets byte

```
16,77,85,66,83,69,67,85,32,74,69,32,84,85,86,83,69,68,32,74,77,85,68,74,79,32,74,77,69,13,0
```

Detective byte

```
13,74,85,82,69,82,32,71,66,32,79,82,84,86,65,32,86,32,88,65,66,74,32,83,86,65,81,32,85,78,69,66,89,81,13,0
```

Scientist byte

```
76,81,84,89,86,70,32,82,75,66,32,83,78,90,32,83,81,87,83,85,32,87,82,65,32,73,77,82,66,32,67,70,72,82,32,90,65,65,65,65,32,73,89,77,87,90,32,80,32,69,65,74,81,86,68,32,89,79,84,80,32,76,71,65,87,32,89,75,90,76,13,0
```

Diver byte

```
10,"DBI DRO PSBCD RKVP YP RSC ZRYXO XEWLOB PYVVYGON LI RSC VKCD XKWO DROX DRO COMYXN RKVP YP RSC XEWLOB",CR,0
```

Driver byte

```
"SOMETIMES WE HAVE ANSWERS AND DONT EVEN KNOW IT SO ENJOY THE VIEW JUST BE HAPPY",0
```

Politician byte

```
83,83,80,87,76,77,32,84,72,67,65,80,32,81,80,32,74,84,32,73,87,69,32,87,68,88,70,90,32,89,85,90,88,32,85,77,86,72,88,72,32,90,65,32,67,66,32,80,65,69,32,88,82,79,76,32,70,65,89,32,73,80,89,75,13,0
```

Test3 byte

```
"ZGJG MTM LLPN C NTER MPMH TW",CR,0
```

Football byte

```
"IT MIGHT BE HELPFUL LATER IF YOU KNOW HOW TO GET TO EDEN OR AT LEAST THE WAY",0
```

Mystery byte

```
"OH A MYSTERY STRING I SHOULD HANG ON TO THIS FOR LATER I WONDER WHAT ITS FOR OR WHAT IT DECODES TO?",0
```

Hooking the badge up to PC via micro-usb and dumping commands to terminal we can receive output from these variables.

```
WELCOME TO DEFCON TWENTY TWO
COME AND PLAY A GAME WITH ME
WHERE TO BEGIN I KNOW FIND HAROLD
TRY THE FIRST HALF OF HIS PHONE NUMBER FOLLOWED BY HIS LAST NAME THEN THE SECOND HALF OF HIS NUMBER

DEFCON DOT ORG SLASH ONE ZERO FIVE SEVEN SLASH I WONDER WHAT GOES HERE
ALBERT MIGHT BE ON THE PHONE WITH HAROLD SO IF ITS BUSY TRY BACK
WHITE LINES IN THE MIDDLE OF THE ROAD THATS THE WORST PLACE TO DRIVE
```

We have no idea who Harold is but we know that he may be on the phone with Albert.

We also have a set of variable names and a reference to a possible URL.

TO THE INTERNET!!!

Searching for Harold and some of variable names we find the following.

Harold Smith a renowned Detective which is one of our variable names.

[http://en.wikipedia.org/wiki/Harold\_Smith\_%28detective%29](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FHarold_Smith_%2528detective%2529&t=ZTEzZWJiMjA4MzBiYWY1OWIyY2VhMGQxYTA1ZDEwMTU0YWNlMjRkZSxacUcwcENnNA%3D%3D)

From here we start searching for Harold Smith.

Jackpot

[http://en.wikipedia.org/wiki/Harold\_Smith](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FHarold_Smith&t=NmRhMjAwOGI1NmMyZGUxMmFjZDQ5NzVjNGZhOThhYzQ4MGJkMzc3YixacUcwcENnNA%3D%3D)

All of the variable names can be found on this page.

We are moving in the right direction.

Searching for more information on Harold we start to pull in searches for Albert

“Harold Smith” Albert wikipedia

One of the entries on the page is regarding Smith numbers.

[http://en.wikipedia.org/wiki/Smith\_number](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FSmith_number&t=M2RiNDBkYzg2NmVjNWEwNDVhZmI2MWQ2MjI5NDg2YWRkOTdlYmFmNCxacUcwcENnNA%3D%3D)

Bingo, this is what we wanted.

Smith numbers were created by Albert Wilansky of Lehigh University.

He noticed the property in his brother-in-laws phone number “493-7775”

His brother-in-law was named Harold Smith.

Knowing this we can now complete the puzzle.

```
DEFCON DOT ORG SLASH ONE ZERO FIVE SEVEN SLASH I WONDER WHAT GOES HERE
TRY THE FIRST HALF OF HIS PHONE NUMBER FOLLOWED BY HIS LAST NAME THEN THE SECOND HALF OF HIS NUMBER
```

This becomes…

[defcon.org/1057/493SMITH7775/](http://t.umblr.com/redirect?z=http%3A%2F%2Fdefcon.org%2F1057%2F493SMITH7775%2F&t=NTI3NTNmZDFhM2Y4MGM2ZmYzODUwOThmZTIwNDM3MzgzOWJhZTRiMyxacUcwcENnNA%3D%3D)

Continue on to Step\_4e with our newfound page.

* * *

## Step\_4e

* * *

Going to the URL from Step\_4d

[http://defcon.org/1057/493SMITH7775/](http://t.umblr.com/redirect?z=http%3A%2F%2Fdefcon.org%2F1057%2F493SMITH7775%2F&t=NTI3NTNmZDFhM2Y4MGM2ZmYzODUwOThmZTIwNDM3MzgzOWJhZTRiMyxacUcwcENnNA%3D%3D)

Page source:

[Step\_4e\_Source.txt (pastebin)](http://t.umblr.com/redirect?z=http%3A%2F%2Fpastebin.com%2FCrg7Vr04&t=OTRkN2ZkMGIwM2UwYmE5MmU0OTE5YjAyYjA5NjQ5YzQxOTRhMzJkYyxacUcwcENnNA%3D%3D)

Picture of the page.

[![](http://i.imgur.com/30WAdAH.png)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2314&t=MzJmMTkxODI4ZTE0YzBhMGI1Y2FjODFiYzdmMTE0NzQzZGExYWRiNyxacUcwcENnNA%3D%3D)

This page contains an image.

[![](http://i.imgur.com/LjlFxnD.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2313&t=NjA4NWJmMmVlNGVhYzkwNmIzZjRmOTliZWM3MWM0NzQ5YjFkMmRiNCxacUcwcENnNA%3D%3D)

The page contains another riddle.

```
Why be
ye searchin' answers here?
Oh are
ye 1o57? The question
queue be
long...be ye not in despair,
em for
keepin' ye from spinnin' yer wheels they be.
```

The page source contains a string of characters in a comment.

```
<!--YQESMJDOJOTM-->
```

This string of characters can be found on an image provided on the DEFCON disc.

It is a picture of Cryptex given to 1o57 as a wedding gift.

[![](http://i.imgur.com/XRQYCGI.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2315&t=YWM4OTUyMDg2ZGI2YWE4YjRjYzcwZDMyZjhmMGIyZjM5YTQ3OTM2MyxacUcwcENnNA%3D%3D)

The string is the bottom most visible row on the Cryptex.

I set to record all of the visible information in the picture.

```
E    L    L    E    N    A    N    D    R    Y    A    N
W    W    B    V    F    E    J    U    V    K    H    N
C    I    Z    D    R    U    R    R    E    G    U    I
D    V    T    Q    I    M    U    F    N    X    N    V
Q    O    H    U    L    D    I    L    K    C    F    O
P    G    2    L    T    G    E    W    P    Z    R    H
K    N    R    I    G    Z    W    I    O    T    I    K
B    B    V    B    4    R    C    V    A    R    L    U
Y    Q    E    S    M    J    D    O    J    O    T    M
```

From here I noticed something interesting about the riddle we had found.

The two word sentences could be replaced with single letters or numbers.

```
Why be        YB
Oh are        OR
queue be    QB
em for        M4
```

The Cryptex contains 4 rows that have these characters right next to eachother.

This showed us we were on the right path.

However with nothing to use the code for we have reached a dead end.

Move on to Step\_4f

* * *

## Step\_4f

* * *

Continue from dead end on Step\_4e

We move to looking at the front of our badges.

There is a series of pin slots on the badge that aren’t standard for normal boards.

Normally a square is used for a grounding slot however all of the grounding slots are placed erratically all over the board.

There are two rows of pin slots on the right and left.

[![](http://i.imgur.com/j64VgcC.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2316&t=NTliYzFjZjVjMDljOGRmMmNmZjcyNTEwZjVlZmE0ZDFjY2JkZTY0YyxacUcwcENnNA%3D%3D)

We can get a binary output from reading the pin slots from left to right.

There are marks on the badge connecting to some of the bits and the line lengths are different between them.

```
0    1    1    0
0    1    0    1
0    1    1    1
0    1    1    0
0    1    1    0
0    1    1    0
0    1    1    0
0    1    0    1
0    1    1    1
0    1    1    1
0    1    0    0
0    1    1    0
1    0    0    0
0    1    0    1
1    0    0    0
0    0    1    1
```

From here we must then convert each line into it’s decimal equivalent.

```
0110 = 6
0101 = 5
0111 = 7
0110 = 6
0110 = 6
0110 = 6
0101 = 5
0111 = 7
0111 = 7
0100 = 4
0110 = 6
1000 = 8
0101 = 5
1000 = 8
0011 = 3
```

We then join these decimals into blocks of two and convert to ascii.

```
65 = A
76 = L
66 = B
65 = A
77 = M
46 = .
85 = U
83 = S
```

This decodes into the following URL.

albam.us

Continue to Step\_4g with our newfound URL.

* * *

## Step\_4g

* * *

Going to the URL from Step\_4f

albam.us

Page source:

[Step\_4g\_Source.txt (pastebin)](http://t.umblr.com/redirect?z=http%3A%2F%2Fpastebin.com%2FmswT8Z4B&t=MzI4YWFiZmZiN2YxZDZhOThkMTQ0NTk2Yzk1NjJhMjUxZDE4NzAwZixacUcwcENnNA%3D%3D)

Picture of the page.

[![](http://i.imgur.com/qPQ68Ua.png)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2317&t=MjMxYmYwZDI1NTJjZjEyOWU3YzYxN2UyZWZjYTkwNDNmM2MwNDkwNSxacUcwcENnNA%3D%3D)

This page contains an image.

[![](http://i.imgur.com/BUo6LnS.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2318&t=NjI3OTVlNzBmY2RhYzk5MWQxYTM3MjVmMmY1NTAyMDQwZDhjYzNmOCxacUcwcENnNA%3D%3D)

The page contains an encoded message on the front.

```
Bsz zfw vbffn up cbei dt la xvf op wtpskcuujjo? Rdjuk cybet uf
evlc dbfovozivnj?

T'fm mzu pqp ie zh b mduknz svnlfu...rivp D'm wpymjih ugalreye J
npdgoidpm uidob qa flyhz mduknz wfcxt, mdlv uzxktff (svxi-tvr!) ryx tvyevpgy Z'x
vbdf gvggier fjlz J tci dzlf ju do rivie. Yix xcbk yvs ksuu poivt aueys xpme? Zv
MERWFZ ive da iudmys...J ptlcglp suwf op kjdnb zz ju zjxjo tzxyt ji b iqr bvqisf D gvgg
lzvy nznfch vgrth...
```

To solve this we must return to our Cryptex dead end from Step\_4e.

The Cryptex reads as follows.

```
E    L    L    E    N    A    N    D    R    Y    A    N
W    W    B    V    F    E    J    U    V    K    H    N
C    I    Z    D    R    U    R    R    E    G    U    I
D    V    T    Q    I    M    U    F    N    X    N    V
Q    O    H    U    L    D    I    L    K    C    F    O
P    G    2    L    T    G    E    W    P    Z    R    H
K    N    R    I    G    Z    W    I    O    T    I    K
B    B    V    B    4    R    C    V    A    R    L    U
Y    Q    E    S    M    J    D    O    J    O    T    M
```

```
ELLENANDRYAN
WWBVFEJUVKHN
CIZDRURREGUI
DVTQIMUFNXNV
QOHULDILKCFO
PG2LTGEWPZRH
KNRIGZWIOTIK
BBVB4RCVARLU
YQESMJDOJOTM
```

Taking the following line from the Cryptex we can decode our message.

BBVB4RCVARLU

This is whats called an OTP or One Time Pad encryption.

[http://rumkin.com/tools/cipher/otp.php](http://t.umblr.com/redirect?z=http%3A%2F%2Frumkin.com%2Ftools%2Fcipher%2Fotp.php&t=NDYyNTIxM2M2OTg0ZDhjMmNkMzNlMjU5OGMxY2M5ZWM5NzBjYTI3NCxacUcwcENnNA%3D%3D)

OTP cannot be decrypted unless you discern the unique pad.

The outcome of our decryption is as follows.

```
Are you about to hang it up due to frustration?  About ready to
call shenanigans?

I'll let you in on a little secret...when I'm feeling deflated I
sometimes think of funny little words, like sextile (rawr-rar!) and suddenly I'm
back feeling like I can dial it in again. Now what was that other funny word? It
REALLY had my number...I usually have to think of it eight times in a row before I feel like myself again...
```

This is clearly referencing our encrypted .rar file we found previously and solves our dead end on Step\_4e.

(rawr-rar!)

A sextile is an astrological term used to describe two celestial bodies that are 60 degrees apart.

The symbol for this is what we commonly know as the Asterisk. \*

This symbol can be found on any modern numpad phone on the bottom left.

The reference to “feeling like I can dial it in again.” also points to phones.

“It REALLY had my number” leads us to the number symbol also found on a phones numpad.

“I usually have to think of it eight times in a row before I feel like myself again…”

This shows that whatever the .rar’s password is will be the same word 8 times in a row.

This is a good method of stopping brute forcing of the password as the string is so long.

Trying ######## we see that its not the way to handle this so we move to research the number sign.

[http://en.wikipedia.org/wiki/Number\_sign](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FNumber_sign&t=OWY3MmE5ZjIzZGM1NjU4NjZkY2MxMzMwMzIxMGE0ZTY4NzQyM2RmYSxacUcwcENnNA%3D%3D)

From here we can see that another “funny word” for a number sign is octothorp.

We then try the following password and unlock the .rar

```
OCTOTHORPOCTOTHORPOCTOTHORPOCTOTHORPOCTOTHORPOCTOTHORPOCTOTHORPOCTOTHORP
```

The .rar opens and our dead end on Step\_4c has been cleared.

Now that we have opened the .rar we can move on to Step\_4h

* * *

## Step\_4h

* * *

The contents of the .rar from Step\_4c are revealed!

Opening the .rar presents us with an image and a m4a format song file.

(TheBox.m4a)

[![](http://i.imgur.com/qXMbLJj.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2320&t=YTBkMzcxNzlmN2Y0YWM3MTY4MzhmZTRkOTQxNWYzNjMxMzE3YzQ3YixacUcwcENnNA%3D%3D)

The image shows the symbol Sigma, a rather hilarious picture of Kim-Jong-Un, Grumpy Cat, Psy, and a key.

Seeing the image of Mickey on Kim-Jong-Un and the key on the page immediately leads us to believe this will be Mickey’s Key which is required to complete the dead end on Step\_4a.

During most of the convention we had been taking pictures of everything we could find.

This included the backs of all of the badge variants which are as follows.

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Badge | Serial\_1 | Serial\_2 | Direction | Language |
| Human | 55586753 | 01458934 | West | Chinese |
| Human | 25348567 | 02933985 | East | Chinese |
| Human | 30303031 | 38563748 | South | Chinese |
| Human | 56456387 | 01924834 | North | Chinese |
| Human | 32439751 | 50932487 | North | Korean |
| Human | 77798753 | 00478041 | West | Korean |
| Human | 81303557 | 85345360 | South | Korean |
| Human | 05978344 | 85758673 | East | Korean |
| Artist | 94841634 | 88172253 | South | Chinese |
| Contest | 09856563 | 23454311 | East | Chinese |
| Vendor | 05729856 | 57380999 | North | Korean |
| Speaker | 31337017 | 34029545 | South | Chinese |
| Goon | 94841634 | 88172253 | South | Chinese |
| Press | 06060606 | 00000000 | South | Korean |

The symbol for Sigma is used to express the sum of a set of numbers.

[http://mathlesstraveled.com/appendices/sigma-notation/](http://t.umblr.com/redirect?z=http%3A%2F%2Fmathlesstraveled.com%2Fappendices%2Fsigma-notation%2F&t=MDNlYzAwZGYwNjdjZTJlMzRlNGFjNTlhZjg0ODBhMGE4ODE0MDVlOCxacUcwcENnNA%3D%3D)

From the images of Psy and Kim-Jong-Un we can guess that this most likely means the sum of North Korea and South Korea seperately with some kind of operation in-between.

Pulling our previously obtained badge information we get the following relevant sets of information.

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Vendor | 05729856 | 57380999 | North | Korean |
| Human | 32439751 | 50932487 | North | Korean |
| Press | 06060606 | 00000000 | South | Korean |
| Human | 81303557 | 85345360 | South | Korean |

Summing the numbers ends in the following values.

|     |     |     |
| --- | --- | --- |
| North | 05729856+57380999+32439751+50932487 | 146483093 |
| South | 06060606+00000000+81303557+85345360 | 172709523 |

Grumpy Cat in the picture refers to ConCATenation

[http://en.wikipedia.org/wiki/Concatenation](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FConcatenation&t=YzY0NjBjNjhjNTMzYjQ1MzNiNmNmMDY0MjFiZmEzMjM0MTQ0ZmVhOCxacUcwcENnNA%3D%3D)

This will take our values and concatenate them as follows.

```
146483093172709523
```

With that in mind we can now solve our dead end from Step\_4a

defcon.org/1057/NATO + Mickey’s Key

defcon.org/1057/NATO146483093172709523

With our newfound URL in hand we can continue to Step\_5

* * *

## Step\_5

* * *

Going to the URL from Step\_4h

[http://defcon.org/1057/NATO146483093172709523/](http://t.umblr.com/redirect?z=http%3A%2F%2Fdefcon.org%2F1057%2FNATO146483093172709523%2F&t=ZGNkNzJiNzI2MTBiZmY2MjU5MzI2NzVhNzJmMjJhZDVlMTZjZmFmYixacUcwcENnNA%3D%3D)

Page source:

[Step\_5\_Source.txt (pastebin)](http://t.umblr.com/redirect?z=http%3A%2F%2Fpastebin.com%2FmVxQ0Azq&t=ZThkNGQ2YTFhNTZkZmUzNjE1MGMxOGI1YjVkMmQxNjJjYTZjNWRhNixacUcwcENnNA%3D%3D)

Picture of the page.

[![](http://i.imgur.com/eZh30px.png)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2321&t=ZDhiZDk1NmE1OWNkNmVhZDVhMzkyODMzMTA2YmViMmJiZTA0MmVlNCxacUcwcENnNA%3D%3D)

This page contains an image and a gif.

[![](http://i.imgur.com/nweBV80.jpg)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2322&t=ZGFhZTM2NGQ2MmQyZWI3NWQ5MDM3MDA4MzI3ZTk0MTFkMTI2YWY0OCxacUcwcENnNA%3D%3D)

[![](http://i.imgur.com/BMmGks2.gif)](http://t.umblr.com/redirect?z=http%3A%2F%2Fimgur.com%2Fa%2FOE26v%2323&t=MzBjZjY4MmQ2NjMxMDBiMzhhNTU1YjVmNjM1ZTQ3OWYwNDE0MDNhNSxacUcwcENnNA%3D%3D)

The language displayed is called Ogham which was used between the 4th and 9th century.

While the origin is uncertain we do know how to translate it roughly as it uses a system much like the alphabet but with 25 letters.

The provided image translates to the following block.

```
I OFT CORRECT NGOUR GRAMMER
OR TELL NGOU TO NEE A NGNNGCHIARINF
BUT THE FILEN ASSISITNG TO NGIERCE
THE LAFD THAT CRAFEN FENT UNGOF
MIGHT LEAD NGOU TO DINCOER THE
FAME OS THE MOOF AT CODEN THAT ARE CURIOUN
```

This needs to be decoded further to make any kind of sense.

We accomplished this using the following key.

```
NG    Y
N    S
F    N
```

This gives us a slightly more readable message.

```
I OFT CORRECT YOUR GRAMMER
OR TELL YOU TO SEE A YSYCHIARISF
BUT THE NILES ASSISITNG TO YIERCE
THE LAFD THAT CRANES NEST UYON
MIGHT LEAD YOU TO DINCOER THE
NAME OS THE MOON AT CODES THAT ARE CURIOUS
```

From here we eyeballed it and performed changes to transform them into proper words.

```
I OFT CORRECT YOUR GRAMMER
OR TELL YOU TO SEE A PSYCHIARIST
BUT THE NILES AFFINITY TO PIERCE
THE LAND THAT CRANES NEST UPON
MIGHT LEAD YOU TO DISCOVER THE
NAME OF THE MOON AT CODES THAT ARE CURIOUS
```

At face value this appeared to be a reference to the egyptian name of the moon.

Attempting this at curious.codes gave us the following URL.

[http://curious.codes/Iah](http://t.umblr.com/redirect?z=http%3A%2F%2Fcurious.codes%2FIah&t=ZGE1Y2M0MzhhMmE0ZjEzZTAzYmQ1OWQwZWE0NjhmYzk3OTIyZTc0OCxacUcwcENnNA%3D%3D)

However, in the source of this page we can see that it is fact a 404 message.

<TITLE>404 Curious.Codes</TITLE>

Either we have the wrong name or we are looking in the wrong place.

It turns out we were wrong on both counts.

The riddle is referring to the show Fraiser.

[http://en.wikipedia.org/wiki/Frasier](http://t.umblr.com/redirect?z=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2FFrasier&t=MDUwYTBhYTlhZjJiZjgxYmQ5ZmExZWEwMWU1NmZmYjA4OTlhOWRlNSxacUcwcENnNA%3D%3D)

This is further backed up by the name of the Ogham message “ScrambledEggs.jpg” which was a line from the shows opening song.

The wife of Niles Crane is Daphne Moon and the actress who plays her is Jane Leeves.

We can then take her name and, much like our previous “pussycatdolls” riddle, send it to @curious.codes

JaneLeeves@curious.codes

With our email sent and a response inbound we can now move to Step 6.

* * *

## Step\_6

* * *

Writing the email from Step\_5 we get the following response.

```
+++
Well done!

Find 1o57, and hand him a note- written on blue paper....

On the note must be your name(s)  / team name - and this phrase:

perfer et obdura; dolor hic tibi proderit olim

Congratulations, you have earned a spot ... but I've said too much...

Include an email :)
```

My heart skipped a beat, we had reached the finish line.

After some frantic calls and a scramble to get a blue piece of paper, we turned in our submission and it was accepted.

The line “perfer et obdura; dolor hic tibi proderit olim” translates to the following.

“Be patient and tough; someday this pain will be useful to you.”

Thank you 1o57, this was a grand adventure indeed.