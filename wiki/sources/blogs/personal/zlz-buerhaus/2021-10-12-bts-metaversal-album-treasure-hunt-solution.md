---
source: zlz-buerhaus
source_url: https://buer.haus/2021/10/12/bts-metaversal-album-treasure-hunt-solution/
title: "BT’s Metaversal Album Treasure Hunt Solution | ziot"
---

[< Back](https://buer.haus/)

![](http://buer.haus/wp-content/uploads/2021/10/0.png)

## Intro

The musical artist known as BT recently launched his 14th album as an interactive NFT experience on the Arweave blockchain called Metaversal. Part of this experience was a multiple day long puzzle treasure hunt.

Metaversal:

[https://btmusic.com/metaversal/](https://btmusic.com/metaversal/)

The beginning of the treasure hunt:

[https://twitter.com/BT/status/1443318319235444738](https://twitter.com/BT/status/1443318319235444738)

The whole experience involved a matic airdrop, three days of puzzles leading to 11 NFTs each day, a geocache treasure hunt in real life, and a final puzzle involving the NFT game Neon District.

We assembled a squad and dove in to solve the BT puzzles:

- [ziot](https://twitter.com/bbuerhaus)
- [jtobcat](https://twitter.com/jtobcat)
- [LeFevre](https://twitter.com/_LeFevre_)
- [lia](https://twitter.com/i_v_a_k_i)
- [omaru](https://twitter.com/omaru53684882)
- [mattm](https://twitter.com/mattmcquaig)
- zomperzon

**IMPORTANT!**

Before we dive into the write-up, some of the links require you to be in the BT Discord to load them. You can join his Discord via this link:

[https://discord.gg/btmusic](https://discord.gg/btmusic)

* * *

# Day 0

The day before the release of the Metaversal Engine, BT published a small puzzle on the discord where the solution is a hint for the upcoming puzzles.

Puzzle:

![](http://buer.haus/wp-content/uploads/2021/10/1.png)

The original full size image: [https://cdn.discordapp.com/attachments/888909629516550184/892579401504546866/Day\_Zero.png](https://cdn.discordapp.com/attachments/888909629516550184/892579401504546866/Day_Zero.png)

If you extract only the bold letters of the first paragraph, you get the following message : **letter one**

This is a clue to decipher the rest of the text, if you pick only the first letters of each word (minus the cross out words), you get the following message : **song number plus song mode plus enter equals NFT**

**song number + song mode + enter = NFT**

* * *

## The Metaversal Engine

Prior to the first sequence, BT launched his Metaversal Engine where you can interact and listen to his new album. You can find it on the following URL:

[https://bpbf7ma4eabfgunhibippcyjcmyrstazgpp4kteypbm4j3fs75na.arweave.net/C8JfsBwgAlNRp0BQ94sJEzEZTBkz38VMmHhZxOyy\_1o/](https://bpbf7ma4eabfgunhibippcyjcmyrstazgpp4kteypbm4j3fs75na.arweave.net/C8JfsBwgAlNRp0BQ94sJEzEZTBkz38VMmHhZxOyy_1o/)

On the bottom left there is a little spinning BT logo you can click on, it will pop up the tracklist and this is where most of the interaction is taking place.

![](http://buer.haus/wp-content/uploads/2021/10/2.png)

- By clicking on the numbers, it will open the tracklist (with 12 songs) and you can customize the order of the songs.
- By clicking on the little sun (on the right of each song), it will open the mode list and you can change the mode for each song : Day, Night, Lunar.
- By clicking on the “return key” button, it will check if your sequence is valid or not. That’s where the “Day 0” solution can be interpreted correctly, to get a NFT we need to gather both the right sequence of tracks and the right mode for each track.

You can see a video of this in action here (courtesy of lacy in the BT Discord):

* * *

## Sequence 1: Mirror Mirror

The first puzzle to drop in the treasure hunt is a crossword puzzle for the Mirror Mirror sequence. It was dropped into Discord with this video:

You can view a higher def version of the crossword puzzle here:

[https://cdn.discordapp.com/attachments/888909679638478859/892876796410888293/MIRRORMIRROR.png](https://cdn.discordapp.com/attachments/888909679638478859/892876796410888293/MIRRORMIRROR.png)

And there were additional instructions with 3 more files in a Dropbox folder:

[https://www.dropbox.com/s/26nokwsvxnnhfhi/The\_Mirror\_Mirror\_Key\_Crossword.zip?dl=0](https://www.dropbox.com/s/26nokwsvxnnhfhi/The_Mirror_Mirror_Key_Crossword.zip?dl=0)

Inside the folder contained 3 fairly large files.

![](http://buer.haus/wp-content/uploads/2021/10/3.png)

At the bottom of the 3rd image, you could see a list of individual crossword positions, as well as the phrase: "We never get a second chance to make first impressions." We determined that this was probably the “meta” solution that would lead to the next step. We got to work and started to fill out a spreadsheet in order to solve the crossword puzzle.

![](http://buer.haus/wp-content/uploads/2021/10/crossword-bottom3.png)

Using this, we know that we need to take the answers from each position listed in the crossword puzzle and take the first letter from each one.

[![](http://buer.haus/wp-content/uploads/2021/10/4-1024x643.png)](http://buer.haus/wp-content/uploads/2021/10/4.png)

You can see our completed crossword puzzle spreadsheet here:

[https://docs.google.com/spreadsheets/d/1pTDcqiwDXOCc5c1ZQfbS1V8zWx6MDugjPnyaMnKd3JU/edit?usp=sharing](https://docs.google.com/spreadsheets/d/1pTDcqiwDXOCc5c1ZQfbS1V8zWx6MDugjPnyaMnKd3JU/edit?usp=sharing)

[![](http://buer.haus/wp-content/uploads/2021/10/cw-extract-1024x635.png)](http://buer.haus/wp-content/uploads/2021/10/cw-extract.png)

The answer to the crossword "meta" puzzle is a URL:

- [https://www.beautifyconverter.com/image-steganography.php](https://www.beautifyconverter.com/image-steganography.php)

The steganography script on this website allows you to hide plaintext messages inside of image files. We have nowhere else to go, so this suggests that we have stego data hidden inside an image that we already received. Instead of the encoder, we go to the [decoder](https://www.beautifyconverter.com/steganographic-decoder.php).

Putting the first image from the Dropbox into the decoder, we get some plaintext out:

[![](http://buer.haus/wp-content/uploads/2021/10/5-1024x310.png)](http://buer.haus/wp-content/uploads/2021/10/5.png)

This is a shortened URL for a YouTube video (youtu.be), so we head off to YouTube:

_rorrim\_rorrim_ \- [https://youtu.be/qLSNW8j5hXk](https://youtu.be/qLSNW8j5hXk)

This is an unlisted video created by an account called “Mirror Mirror”:

[https://www.youtube.com/channel/UClFkibkRuJMk3E6WVn47ifg](https://www.youtube.com/channel/UClFkibkRuJMk3E6WVn47ifg)

The video shows some scenes from the Metaversal song videos. It also audibly states the following:

If the world was reversed and day was night, we'd watch the sea with great delight. may beautify converter be thy guide.

In the video description, we have the following:

- RGF5ME5pZ2h0MUx1bmFyMgpERUMuQ09OVkVSLlRFUg==
- BT\_AMENDING\_BT

We don’t know what to do with the second line yet, but the first line is Base64 which decodes to the following:

Day0Night1Lunar2

DEC.CONVER.TER

The day 0, night 1, lunar 2 string indicates that we will have something that will tell us which tracks to label as day, night, or lunar, with the indicators of 0, 1, or 2. The line “DEC CONVER TER” suggests that we need to convert decimal numbers into ternary (another numbering system)

In YouTube account’s channel, we see they also have another video:

**8edoc-rorrim\_rorrim**

8edoc-rorrim\_rorrim - YouTube

Tap to unmute

[8edoc-rorrim\_rorrim](https://www.youtube.com/watch?v=vT4zdz7kkB4) [mirror\_mirror](https://www.youtube.com/channel/UClFkibkRuJMk3E6WVn47ifg)

![thumbnail-image](https://yt3.ggpht.com/4I9-NZMqPDTyEjq5HnGrpHCKr_599-NLA0SN_FJVTHpht7Kx9KetVLoJsArrdai8lZ4YWPnIjw=s68-c-k-c0x00ffffff-no-rj)

mirror\_mirror10 subscribers

[Watch on](https://www.youtube.com/watch?v=vT4zdz7kkB4)

The video displays a number string: “8-122943”. We know we are looking for an order and mode sequence order and that there are 11 modes/NFTs per day, so there’s a good chance this number will give us the mode for #8.

We started by trying to convert the number 122943 from decimal to ternary, we get 11 numbers of 0, 1, or 2. This looked good. Given that the challenge of the day is called “Mirror Mirror” and the video suggests reversing, we set the song order in reverse starting at 11 and ending on 1. Then we set the modes to the following:

122943 -> 01122102002

... and, it didn’t work!

Around this time, we started to discover other codes being posted to the BT Discord and social media pages.

![](http://buer.haus/wp-content/uploads/2021/10/7.png)

By chance, we tried the same thing except with the first code instead of the eighth. It worked! For some reason, none of the other codes would work though.

Eventually a new video was posted containing the following info:

[https://cdn.discordapp.com/attachments/888909679638478859/892938389769310218/Twitter\_Sequence\_1\_-\_C.mp4](https://cdn.discordapp.com/attachments/888909679638478859/892938389769310218/Twitter_Sequence_1_-_C.mp4)

I’d change direction to all objectives, in sixty four this cloaked perspective. If you should seek, in earnest find. From eleven we’ll meet at the starting line

We figured out this meant shifting the starting song order based on the code number.

![](http://buer.haus/wp-content/uploads/2021/10/8.png)

This quickly concluded the first day of puzzling, however there were several more hints dropped throughout the rest of the day.

Ternary and order hints:

- [https://cdn.discordapp.com/attachments/888909679638478859/892939770924249108/TNSP.mp4](https://cdn.discordapp.com/attachments/888909679638478859/892939770924249108/TNSP.mp4)
- [https://cdn.discordapp.com/attachments/888909679638478859/892946899965972530/dcvt.png](https://cdn.discordapp.com/attachments/888909679638478859/892946899965972530/dcvt.png)

After all of the codes were claimed, BT posted a walkthrough of the puzzles in his Discord here:

[https://discord.com/channels/877707149072023572/888909679638478859/892995210529865749](https://discord.com/channels/877707149072023572/888909679638478859/892995210529865749)

* * *

## Sequence 2: Spiral Key

The second puzzle started with this tweet from BT:

Twitter Embed

[Visit this post on X](https://twitter.com/BT/status/1443673221769965572?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[![](https://pbs.twimg.com/profile_images/1884045538837790720/pKJg7pO0_normal.jpg)](https://twitter.com/BT?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[BT](https://twitter.com/BT?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[@BT](https://twitter.com/BT?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

·

[Follow](https://twitter.com/intent/follow?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F&screen_name=BT)

[View on X](https://twitter.com/BT/status/1443673221769965572?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

Day 2: For what you search are numbered as three from Meta to middle to end you seek
Two sequences of three and one sequence or four shall lead to a place we’ve not been before. [#Metaversal](https://twitter.com/hashtag/Metaversal?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F&src=hashtag_click) [https://dropbox.com/sh/ixnk4xscya4khew/AACzB73kZ52zf9JUjrUEiXMLa?dl=0…](https://www.dropbox.com/sh/ixnk4xscya4khew/AACzB73kZ52zf9JUjrUEiXMLa?dl=0)

[![Image](https://pbs.twimg.com/media/FAj1JAAX0AcafYI?format=jpg&name=small)](https://x.com/BT/status/1443673221769965572/photo/1)

[8:24 PM · Sep 30, 2021](https://twitter.com/BT/status/1443673221769965572?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[X Ads info and privacy](https://help.twitter.com/en/twitter-for-websites-ads-info-and-privacy)

[13](https://twitter.com/intent/like?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F&tweet_id=1443673221769965572) [Reply](https://twitter.com/intent/tweet?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F&in_reply_to=1443673221769965572)

Copy link

[Read 1 reply](https://twitter.com/BT/status/1443673221769965572?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1443673221769965572%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

> Day 2: For what you search are numbered as three from Meta to middle to end you seek
>
> Two sequences of three and one sequence or four shall lead to a place we’ve not been before. [#Metaversal](https://twitter.com/hashtag/Metaversal?src=hash&ref_src=twsrc%5Etfw) [https://t.co/WFC7cu2M7U](https://t.co/WFC7cu2M7U) [pic.twitter.com/uspAUer4Re](https://t.co/uspAUer4Re)
>
> — BT (@BT) [September 30, 2021](https://twitter.com/BT/status/1443673221769965572?ref_src=twsrc%5Etfw)

Along with a dropbox link to download the following picture:

- [https://cdn.discordapp.com/attachments/888909770076078080/893232123367002142/Sequence\_2.png](https://cdn.discordapp.com/attachments/888909770076078080/893232123367002142/Sequence_2.png)

According to the flavour text, we are looking for three numbers.

- By checking the alpha plane of the picture, we can see that something has been hidden in the middle of the picture. This is roman numerals for: 616

![](http://buer.haus/wp-content/uploads/2021/10/10.png)
- By opening the picture in a hex editor, we can notice that something has been hidden at the very end of the file. [https://youtu.be/92g4wY4Xhs8](https://youtu.be/92g4wY4Xhs8). The link leads to the following video : The Video Game Years 1987 - Full Gaming History Documentary (1987)
- By opening the picture in an exif viewer, we can find another hidden message in the meta data: [https://www.pinterest.com/pin/295971006747004614/](https://www.pinterest.com/pin/295971006747004614/) \- This is a paper about the introduction of the latest Rhythm machine from Roland : the TR-909

The Meta number is 909 since it was found in the metadatas of the png. So we get the following sequence : 9096161987 which is actually an US phone number : 909-616-1987

“Congratulations and welcome to theblacksun\_metaversal@protonmail.com M3t@veRs%l you found the first level of this spiral key, one man’s trash is another man’s treasure”

Sending an email to that address with “M3t@veRs%l” as the subject line, you get an automated response back:

![](http://buer.haus/wp-content/uploads/2021/10/11.png)

Reading the text in a spiral starting from the middle out, you get the following string:

TYPE THE FIRST ELEVEN DIGITS OF THE GOLDEN RATIO INCLUDING DECIMAL POINT

Going back to the Metaversal album website, we type in the following using our keyboard:

1.61803398874

Looking at our dev console, we see a text file in the log:

[![](http://buer.haus/wp-content/uploads/2021/10/12-1024x571.png)](http://buer.haus/wp-content/uploads/2021/10/12.png)

This leads us to:

- [https://bpbf7ma4eabfgunhibippcyjcmyrstazgpp4kteypbm4j3fs75na.arweave.net/C8JfsBwgAlNRp0BQ94sJEzEZTBkz38VMmHhZxOyy\_1o/L3on@rd0.txt](https://bpbf7ma4eabfgunhibippcyjcmyrstazgpp4kteypbm4j3fs75na.arweave.net/C8JfsBwgAlNRp0BQ94sJEzEZTBkz38VMmHhZxOyy_1o/L3on@rd0.txt)

![](http://buer.haus/wp-content/uploads/2021/10/13.png)

Keeping with the Spiral theme, we have a fibonacci sequence’s golden spiral.

Decoding the hex, we get: 0=day, 1=night, 2=lunar.

But the important part is “sequence =” 0, ?, ?, ?, ?, ?, ?, ?, 3, ?, 1. We know the fibonacci sequence begins with 0, so we try to see if it fits:

- Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21
- L3on@rd0.txt: 0, \_, \_, \_, \_, \_, \_, \_, 3, \_, 1
- Solution: 0, 1, 1, 2, 3, 5, 8, 1, 3, 2, 1

We see the 0 at the beginning fits and we can also see that 13 21 and \_3\_1 at the end are possible fits. This gives us a possible order to use because it is 11 numbers and appears to line up. Sure enough, this happened to be the solution that we needed for the song order.

However, we can’t use the track order to solve until we figure out the modes.

After a little while, modes started to be dropped on BT's social media and discords. All the modes for Spiral Key can be found in these locations:

01. https://twitter.com/BT/status/1443689260314468352
02. https://cdn.discordapp.com/attachments/892831484963082310/893262944870223922/unknown.png (from instagram)
03. https://cdn.discordapp.com/attachments/892831484963082310/893269756763865108/unknown.png (from facebook)
04. https://twitter.com/BT/status/1443718245257711616
05. https://cdn.discordapp.com/attachments/892831484963082310/893284783558393916/unknown.png (from instagram)
06. https://twitter.com/BT/status/1443730884855836673
07. https://cdn.discordapp.com/attachments/892831484963082310/893297953320628234/unknown.png (from instagram)
08. https://cdn.discordapp.com/attachments/878067755612532766/893272632319938600/p.png
09. https://cdn.discordapp.com/attachments/882443175875190846/893301166534975488/Sequence\_2\_Modes\_9.png
10. https://cdn.discordapp.com/attachments/882741721723711498/893301117109284905/Sequence\_2\_Modes\_10.png
11. https://cdn.discordapp.com/attachments/878139356450267146/893289586783047760/p.png

Modes:

- VPUDRCMBMFF
- WPUESANDNGD
- WMSCTAOBLGE
- UNSDSANBNGD
- VNSDRCMDLEE
- WMTCTAOBMFD
- VNUDRBNCNEF
- VPTESANBLGE
- WNSCRANCMED
- VPSDSCNBMEF
- VNTCSBNDLFF

At the bottom of each picture we can read : “rotatedandUNSCRAMBLED”.

This means that originally each string is the word “UNSCRAMBLED” where each character has been rotated (caesar shift) by a different amount. Since this amount only varies between three values 0, 1 and 2, appending the different amounts for a single string gives the mode we need to use in the Metaversal Engine.

The final modes from bottom to top :

- 12210200112
- 22221012220
- 21002020021
- 00011010220
- 10010202001
- 21102020110
- 10210111202
- 12121010021
- 20000011100
- 12011210102
- 10101112012

Using the fibonacci sequence solution and the unscrambled modes, we can complete the puzzle to get our Spiral Key!

* * *

## Sequence 3: Root Key

Since Day 1, a hidden song 0 could be selected from the music player. This song played a message in morse followed by a series of notes. The morse could be decoded to say:

11 ROOTS ARE SEQUENCE 3

A SECRET LAY AT THE ROOT OF TREES

At the start of day 3, the following image of a tree was posted to the BT discord:

[![](http://buer.haus/wp-content/uploads/2021/10/tree-1024x1024.png)](http://buer.haus/wp-content/uploads/2021/10/tree.png)

At the bottom of the image the roots are suspiciously separated into lines, 11 segments long.

[![](http://buer.haus/wp-content/uploads/2021/10/14-1024x625.png)](http://buer.haus/wp-content/uploads/2021/10/14.png)

Because of the length, we suspected these 11 lines related to the modes in the final sequence. Though we couldn't confirm this without the song order.

Slightly before the tree image was posted, a tweet went out:

Twitter Embed

[Visit this post on X](https://twitter.com/BT/status/1444016198191140865?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[![](https://pbs.twimg.com/profile_images/1884045538837790720/pKJg7pO0_normal.jpg)](https://twitter.com/BT?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[BT](https://twitter.com/BT?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[@BT](https://twitter.com/BT?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

·

[Follow](https://twitter.com/intent/follow?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F&screen_name=BT)

[View on X](https://twitter.com/BT/status/1444016198191140865?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

Day 3: For whoever holds a key that ends on e, what pray tell would this sequence be? And be it uncanny this gee or an Eee; personally I’d say a good major it’d be.

1 5 11
BT\_CLUTTERED\_BT

![](https://pbs.twimg.com/ext_tw_video_thumb/1444016111905869860/pu/img/sv0LKHmPdfKmAWEF.jpg)

[Watch on X](https://twitter.com/BT/status/1444016198191140865?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[7:07 PM · Oct 1, 2021](https://twitter.com/BT/status/1444016198191140865?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

[X Ads info and privacy](https://help.twitter.com/en/twitter-for-websites-ads-info-and-privacy)

[55](https://twitter.com/intent/like?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F&tweet_id=1444016198191140865) [Reply](https://twitter.com/intent/tweet?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F&in_reply_to=1444016198191140865)

Copy link

[Read 11 replies](https://twitter.com/BT/status/1444016198191140865?ref_src=twsrc%5Etfw%7Ctwcamp%5Etweetembed%7Ctwterm%5E1444016198191140865%7Ctwgr%5Eae906e1d2676845531b9db21067784aef21af68d%7Ctwcon%5Es1_&ref_url=https%3A%2F%2Fbuer.haus%2F2021%2F10%2F12%2Fbts-metaversal-album-treasure-hunt-solution%2F)

The text suggests we need to do something related to music to solve the root key. It is also telling us 1 5 11, possibly the beginning of the song order for the root key. Even with this info, it was not until this hint that we started to figure out what we needed to do:

HINT: The second half of track zero holds the key. In fact, it holds several.

This led us to focusing on the notes at the end of track 0. Listening to it, we identify 11 piano keys at the end of the song. It seemed that we had to figure out some method to get 1 5 and 11 to correspond to the first 3 notes. Not long after making this realization, a hint was posted:

![](http://buer.haus/wp-content/uploads/2021/10/Sequence_3_Root_Key_Hint_.png)

There are a few things to take from this, there are 11 notes. We can also see that the first notes have images associated with them correlating to songs 1 5 and 11. Later down, we can see that there is an image shown for 9. We knew if we could figure out how the notes correlated with each song, that we would have the song order we need for the root key.

Another important thing to note is that the only songs given were repeated notes. This gives more confidence that our guess is correct as it eliminates having to guess where to put songs on duplicate notes.

[![](http://buer.haus/wp-content/uploads/2021/10/root-key-notes-1024x577.png)](http://buer.haus/wp-content/uploads/2021/10/root-key-notes.png)

By identifying the key signature for each song, you can place them on top of the chart. There are a few ways to do this, there are online tools where you can upload songs and it will tell you what the key signature is. It is important to state that these tools are not always supremely accurate. For better results, frantically find someone who knows music that can figure it out for you.

The keys ended up being:

A A A Bb B GM Gm C D D E.

Giving us our final song order:

1 5 11 2 4 7 3 8 6 9 10

With the order, we now need to figure out the mode sequences. The 11 mode sequences were read from the roots starting from the circle with a horizontal line = night (1), a vertical line = day (0), and a diagonal line = lunar (2). This encoding method was confirmed through a series of hints (and finally a straight up key) released during the day.

Roots with directions three, give time of day at the base of the tree,

horizontal moves, vertical does not, the other gives you a double shot.

The roots of each song are sometimes the same,

but sequenced in order to finish the game

[https://cdn.discordapp.com/attachments/888909859460878416/893682362167226368/The\_Tree\_Key\_-\_Discord\_.png](https://cdn.discordapp.com/attachments/888909859460878416/893682362167226368/The_Tree_Key_-_Discord_.png)

The final mode sequences, from top to bottom, were:

01. 11102121021
02. 10120100110
03. 11022201011
04. 11102012100
05. 00221022110
06. 01100110201
07. 00112010221
08. 22111201010
09. 12212012002
10. 20101011122
11. 21212100201

* * *

## Treasure Puzzle

On day 3, a channel called #x-marks-the-spot on the discord opened along with the #root-key channel. The first messages in this channel were:

![](http://buer.haus/wp-content/uploads/2021/10/15.png)

- [https://www.dropbox.com/sh/8rettvswk3mgpm4/AAD4lWnsLAev85hez2cLCmBZa?dl=0](https://www.dropbox.com/sh/8rettvswk3mgpm4/AAD4lWnsLAev85hez2cLCmBZa?dl=0)

Which clued us in that we would need info from the previous days. Throughout the hunt, 8 words with the format of BT\_WORD\_BT were found at various steps. Here are the locations of each word:

|     |     |     |
| --- | --- | --- |
|  | BT\_text\_BT | BT = Buried Treasure |
| 1 | BT\_LIVING\_BT | Displays in the console when you click song 0. |
| 2 | BT\_CURRY\_BT | Found in the L3on@rd0.txt |
| 3 | BT\_GANGS\_BT | Posted in #mirror-mirror-key |
| 4 | BT\_AMENDING\_BT | https://www.youtube.com/watch?v=qLSNW8j5hXk |
| 5 | BT\_MUGS\_BT | In the spiral email |
| 6 | BT\_CLUTTERED\_BT | https://twitter.com/BT/status/1444016198191140865 |
| 7 | BT\_TIMER\_BT | At the bottom of TREE.png |
| 8 | BT\_AUDIBLE\_BT | Posted in #x-marks-the-spot |

A little later, an additional word BT\_EMBEDDED\_BT was posted in the discord.

Now, going back to the given image. There are 57 spaces in a spiral with one L already given. The number of spaces happens to match the number of letters in all of the BT words, so we naturally tried to find the correct order of words assuming that the letters in the box would give us an answer. The 10 numbers above the spiral are consecutive and non repeating and so suggest an ordering in which to read the boxed letters.

We also noticed that at the end of the image was a hidden password-protected zip file.

Reordering the boxes with the given L gave a 10 letter word with an L at the end. Through a stroke of lucky intuition, we guessed the word was METAVERSAL rearranged per the given string 7163940825 and quickly backsolved the ordering to be (reading inwards):

LIVINGGANGSMUGSEMBEDDEDTIMERCLUTTEREDAUDIBLEAMENDINGCURRY

The final unused element on the image is the text "What Three Words Will Guide You?". [https://what3words.com/](https://what3words.com/) is a site which assigns each location on the planet a series of 3 words. Splitting up our words into groups of 3 and searching on this site showed 3 places in the UK.

[https://cdn.discordapp.com/attachments/891895158143066142/893712270847254568/Auric\_Shape.png](https://cdn.discordapp.com/attachments/891895158143066142/893712270847254568/Auric_Shape.png)

A hint posted by BT said to overlay an "auric shape". What more fitting shape is there than the fibonacci spiral from day 2?

[![](http://buer.haus/wp-content/uploads/2021/10/16-1024x592.png)](http://buer.haus/wp-content/uploads/2021/10/16.png)

The location at the center of the spiral, and the password to the zip file, turned out to be:

billingeforest

Inside the zip file was a link to a youtube video.

Metaversal Burial Site - YouTube

Tap to unmute

[Metaversal Burial Site](https://www.youtube.com/watch?v=BJCgN77d9f0) [BT\_BuriedTreasure\_BT](https://www.youtube.com/channel/UCAdEgu_clhe3nRraREG6FpA)

![thumbnail-image](https://yt3.ggpht.com/ytc/AIdro_k2Z6xibrg89ceTOo7QwIhmWgTtrF_4kXgPI5mFtPQPS_pSZElk3qsj1WdP_NCQ-9WqQw=s68-c-k-c0x00ffffff-no-rj)

BT\_BuriedTreasure\_BTNo subscribers

[Watch on](https://www.youtube.com/watch?v=BJCgN77d9f0)

This video shows exactly where the buried treasure was located in this forest which you can watch being dug up here

Twitter Embed

Not found

> After 3 days of epic puzzles with 33 unique 1/1 NFTs prizes, [@BT](https://twitter.com/BT?ref_src=twsrc%5Etfw)'s puzzle quest to celebrate the release of his Metaversal album all lead to this IRL buried treasure!
>
> Solved with: [@bbuerhaus](https://twitter.com/bbuerhaus?ref_src=twsrc%5Etfw) [@\_LeFevre\_](https://twitter.com/_LeFevre_?ref_src=twsrc%5Etfw) [@mattmcquaig](https://twitter.com/mattmcquaig?ref_src=twsrc%5Etfw) [@i\_v\_a\_k\_i](https://twitter.com/i_v_a_k_i?ref_src=twsrc%5Etfw) [@omaru53684882](https://twitter.com/omaru53684882?ref_src=twsrc%5Etfw) and Zomperzon [pic.twitter.com/U6AzVya9Xe](https://t.co/U6AzVya9Xe)
>
> — JTobcat (@jtobcat) [October 2, 2021](https://twitter.com/jtobcat/status/1444349996363571204?ref_src=twsrc%5Etfw)

* * *

## ND Puzzle

We noticed in the Neon District Discord that a new puzzle channel was created called “Laurel Canyon Puzzle”.

[![](http://buer.haus/wp-content/uploads/2021/10/17-1024x470.png)](http://buer.haus/wp-content/uploads/2021/10/17.png)

We knew from the beginning that the airdropped matic NFTs for BT added new functionality to Neon District. It allows you to play different versions of the Laurel song during combat as long as you hold the NFT in your wallet.

Going into the game and looking through the JavaScript, we discovered the three versions of the song:

[![](http://buer.haus/wp-content/uploads/2021/10/18-1024x542.png)](http://buer.haus/wp-content/uploads/2021/10/18.png)

The JS file:

https://portal.neondistrict.io/static/js/2.295b5cb7.chunk.js

The webpack JS location:

/src/data/soundEffects.js"bt-laurel-canyon-loop": {

"tag": "bt-laurel-canyon-loop",

"location": "general",

"type": "combat",

"placement": "loop",

"path": "music/bt/3.\_Laurel\_Canyon\_Night\_Drive\_Mastered.wav"

},

"bt-laurel-canyon-night-loop": {

"tag": "bt-laurel-canyon-night-loop",

"location": "general",

"type": "combat",

"placement": "loop",

"path": "music/bt/3.\_Laurel\_Canyon\_Night\_Drive\_Night\_Mode.wav"

},

"bt-laurel-canyon-lunar-loop": {

"tag": "bt-laurel-canyon-lunar-loop",

"location": "general",

"type": "combat",

"placement": "loop",

"path": "music/bt/3.\_Laurel\_Canyon\_Night\_Drive\_Lunar\_Mode\_v2.wav"

}

This gives us the three file locations:

**Day:**

[https://neon-district-season-one.s3.amazonaws.com/sound-effects/music/bt/3.\_Laurel\_Canyon\_Night\_Drive\_Mastered.wav](https://neon-district-season-one.s3.amazonaws.com/sound-effects/music/bt/3._Laurel_Canyon_Night_Drive_Mastered.wav) **Night:**

[https://neon-district-season-one.s3.amazonaws.com/sound-effects/music/bt/3.\_Laurel\_Canyon\_Night\_Drive\_Night\_Mode.wav](https://neon-district-season-one.s3.amazonaws.com/sound-effects/music/bt/3._Laurel_Canyon_Night_Drive_Night_Mode.wav) **Lunar:**

[https://neon-district-season-one.s3.amazonaws.com/sound-effects/music/bt/3.\_Laurel\_Canyon\_Night\_Drive\_Lunar\_Mode\_v2.wav](https://neon-district-season-one.s3.amazonaws.com/sound-effects/music/bt/3._Laurel_Canyon_Night_Drive_Lunar_Mode_v2.wav)We tried several things at this point, such as:

- Trying to diff the audio files from the originals
- Looking for stego techniques such as Spectrograms
- Looking through the wav file for hidden data

Opening up the file in our trusty 010 Hex Editor, we can see there is a zip file embedded at the end of the file data. The way you identify this is by understanding that most file formats begin with magic byte headers and some have footers. For example, a PNG image begins with %PNG (hex: 89 50 4E 47), but also ends with IEND®B\`‚ (hex: 49 45 4E 44 AE 42 60 82). A common trick for hiding files inside of other files is to take the file data and shove it at the end of another file. A zip's magic bytes usually begins with PK, so we can see the PK after the IEND, thus we know we have a zip file hidden at the end of the PNG image.

This may sound extreme if you are unfamiliar with it, but there are easy ways to identify these. A good hex editor like 010 will identify data that does not belong in common file formats. There are also some tools such as binwalk that will identify and extract the files for you.

So we proceed to rip the zips out.

![](http://buer.haus/wp-content/uploads/2021/10/19.png)

Going through each audio file, we can see there is a password encrypted zip at the end of each wav. Each zip file contains a “1”, “2”, or “3” file inside of them. Unfortunately, though, we need a password in order to proceed.

Looking back at the string posted in the Discord image, we still haven’t figured out what to do with that yet.

i621756155i

Eventually, motive posted a hint in the Discord channel:

![](http://buer.haus/wp-content/uploads/2021/10/20.png)

This tells us that we need data from a previous puzzle in order to proceed.

If we were to consider that i = index, that would mean we need some strings to use. We have 9 numbers, so we are looking for a list of 9 things to index into. The end of the BT puzzle had 9 “Buried Treasure” (BT) strings.

Using the order from the W3W / Treasure Puzzle:

- 0 LIVING
- 1 CURRY
- 2 GANGS
- 3 AMENDING
- 4 MUGS
- 5 CLUTTERED
- 6 TIMER
- 7 AUDIBLE
- 8 EMBEDDED

Then taking the nth position based on the index string:

- 1 LIVIN G
- 2 G A NGS
- 3 M UGS
- 4 EMBEDD E D
- 5 TIME R
- 6 CLUTT E RED
- 7 A UDIBLE
- 8 AMEN D ING
- 9 CURR Y

We get the following string out: GAME READY

Sending it to the CERES bot, we get a response:

![](http://buer.haus/wp-content/uploads/2021/10/21.png)

This is shorthand for an imgur link: [https://imgur.com/a/GZZmnVl](https://imgur.com/a/GZZmnVl)

![](http://buer.haus/wp-content/uploads/2021/10/22-1.png)

Now we have three more strings, each one correlating to the day, night, and lunar. This matches up with our 3 zip files, suggesting that each string will be the password we need to extract the file inside of them.

In the previous puzzle, the i = index. Now we have an o, which given that we have a unique number for 1-9, we can assume that o = order.

Using the buried treasure words that we used in the previous step, we now permutate them into a string to create a password.

Zip passwords:

- Day: CLUTTEREDCURRYAMENDINGGANGSTIMERAUDIBLEMUGSEMBEDDEDLIVING
- Night: TIMERCLUTTEREDAUDIBLEMUGSAMENDINGLIVINGCURRYEMBEDDEDGANGS
- Lunar: MUGSCLUTTEREDAMENDINGEMBEDDEDCURRYLIVINGTIMERAUDIBLEGANGS

Inside of each zip is a file containing random bin data prepended by the string :BT:

![](http://buer.haus/wp-content/uploads/2021/10/23.png)

You can view the hex of each file here:

[https://gist.github.com/ziot/a9c9de4f20de5bd3f47d8c77284562f6](https://gist.github.com/ziot/a9c9de4f20de5bd3f47d8c77284562f6)

After messing around with these files for a bit, we discovered a few things:

- Each file is 2785 bytes of data.
- If you remove the null bytes (00 00), each file is 2741 bytes of data
- If you remove :BT: at the beginning of each file, each file is 2737 bytes of data.
- Just from experience, we know we have 3 files of similar length with this sort of data suggests that the data has been XOR’d with another set of data.

The first discovery we made is that if you XOR the content of the first file with a semi-colon (:), you get the following data out:

![](http://buer.haus/wp-content/uploads/2021/10/24.png)

If you have some technical experience, you’ll notice that the output begins with ivBORw0KGgo. You can derive a few things from this result:

- The data we are going to get out is Base64 encoded.
- This is a common type of Base64 encoded string, you’ll recognize that it is the magic bytes for a PNG image. So we know that we’re getting an image out of these 3 files.
- There are characters in the response that are not valid Base64 characters, so we know that either our XOR is bad (incomplete) or there is junk we need to remove.

After being stuck here for awhile, we wrote a script to highlight all of the characters that were not valid Base64 characters, when we had a sudden realization:

[![](http://buer.haus/wp-content/uploads/2021/10/25-1024x901.png)](http://buer.haus/wp-content/uploads/2021/10/25.png)

The invalid characters are the BT logo!

Simultaneously, while manually fixing the XOR another realization was made. The XOR that gives us proper data was a string that we had already seen in a past puzzle. The first 4 lines could be properly fixed using this string:

![](http://buer.haus/wp-content/uploads/2021/10/26.png)

If you remember from earlier in the puzzle, there is a text file that contains a string that looks similarly:

[https://bpbf7ma4eabfgunhibippcyjcmyrstazgpp4kteypbm4j3fs75na.arweave.net/C8JfsBwgAlNRp0BQ94sJEzEZTBkz38VMmHhZxOyy\_1o/L3on@rd0.txt](https://bpbf7ma4eabfgunhibippcyjcmyrstazgpp4kteypbm4j3fs75na.arweave.net/C8JfsBwgAlNRp0BQ94sJEzEZTBkz38VMmHhZxOyy_1o/L3on@rd0.txt)

Sure enough, the BT ascii logo is 2781 bytes which is a perfect match to the individual files we extracted from the zips. That means each file was likely XOR’d with this string.

Performing xor on the three files, combining them, and base64 decoding into a PNG file results in the following:

![](http://buer.haus/wp-content/uploads/2021/10/27.png)

This is the private key for a wallet containing 3 ETH and a Blockade Games Degen Trophy.

* * *

## Fin’

Overall, this was an incredible experience put together by BT and motive. Follow them on Twitter!!!

- [@BT](https://twitter.com/bt)
- [@motive](https://twitter.com/leemsparks)

This was a fun mix of music, classic puzzling techniques, technical challenges, and real world geo-cache hunting!

Spend some time listening to the METAVERSAL album, you'll love it!

[https://bpbf7ma4eabfgunhibippcyjcmyrstazgpp4kteypbm4j3fs75na.arweave.net/C8JfsBwgAlNRp0BQ94sJEzEZTBkz38VMmHhZxOyy\_1o/](https://bpbf7ma4eabfgunhibippcyjcmyrstazgpp4kteypbm4j3fs75na.arweave.net/C8JfsBwgAlNRp0BQ94sJEzEZTBkz38VMmHhZxOyy_1o/)

Twitter Widget Iframe