---
source: zlz-buerhaus
source_url: https://buer.haus/2015/08/11/defcon-23-badge-challenge/
title: "DEFCON 23 Badge Challenge | ziot"
---

[< Back](https://buer.haus/)

Authors: [![image](https://blog.twitter.com/sites/all/themes/gazebo/img/ios_homescreen_icon.png) Brett Buerhaus](https://twitter.com/bbuerhaus), [![image](https://blog.twitter.com/sites/all/themes/gazebo/img/ios_homescreen_icon.png) Jason Thor Hall](https://twitter.com/PotatoSec)

Original Post: http://potatohatsecurity.tumblr.com/post/126411303994/defcon-23-badge-challenge

Brett, Jon, and I teamed up with Council of 9 and won this years badge challenge after having great success in the [DEFCON 22 Badge Challenge](http://potatohatsecurity.tumblr.com/post/94565729529/defcon-22-badge-challenge-walkthrough). Over the last year we have studied a huge number of cryptographic methods and ancient languages to prepare for this. We also released our own [crypto-challenge website](http://www.potatopla.net/crypto) for the community to follow along and have fun challenging themselves. With our new knowledge and a great team in tow we headed out to DEFCON.

Here is the entire adventure as we experienced it with all of the puzzles, their solutions, and the steps to solve them. Understand that this document contains MASSIVE spoilers so if you do not want to ruin it for yourself please stop reading now.

## Step\_1

* * *

After the we met up with the rest of the Council of 9 members we all immediately began hunting for signs off 1o57’s work around the convention. One of the first things that caught our teams eye was this years room keys. Interestingly enough 1o57 had never included room keys in previous challenges so this was rather unexpected.

![](https://i.imgur.com/2FuIvKN.jpg)

We talked to others and rotated our keys with the hotels until we were able to obtain photos of five different room keys. Each key having a different image and cryptic text and a small circle with a dot on it. This strange text turned out to be the language known as Telugu script which hails from southern India as far back as 400 BC and the circle was a representation of a clock face showing the order of the cards.

We originally tried to translate the text literally which came out to nothing but incoherent gibberish. At this point we knew that 1o57 had pulled another classic maneuver and was using the language in a more imaginative way. In this case the phonetic display of the text could be roughly compared to an english word. For instance the pictured card translates to “Latali” which we can then interpret as “Little”

The cards then translated out to the following:

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Card 1 | Card 2 | Card 3 | Card 4 | Card 5 |
| LITTLE | GIRL | RECORD | TWO | FIVE |

Without knowing what this was for we documented it and continued our hunt for additional information.

* * *

## Step\_2

* * *

Once we got our DEFCON bags from the glory that is LINECON we obtained a few new sources of information. A vinyl record badge, a booklet, two CD’s, and a lanyard. ( A big thanks to [@psifertex](https://twitter.com/psifertex) for lending us a booklet and the CD’s the night before ;D )

Having seen that in previous years the booklet contained an easy lead we immediately set to dig into it. On the bottom right corner of page 2 we found a block of cipher text in two different fonts.

```

VgjbhyqagorQrspbajvgubhgbhetbbqsevraqPnrfne
(fbzrgenqvgvbafjvyyarireqvr)
Hjvyyxabjjung2qbjuraHhafpenzoyr"Ubjqnqqlvfqbvat"

WFST HDXE HGY BNK BAWH QJG PSOR WNFATG IDDW OQUHVNKINGCY GQG CTUK.
```

1o57 has a tradition for each years badge challenge. Caesarian ROT13 must be used at least one time and most usually in the booklet. This year was no different and we can see this by rotating the first three lines with a tool from [Rumkin](http://rumkin.com/tools/cipher/rot13.php).

This comes out to the following after rotation:

```

ItwouldntbeDefconwithoutourgoodfriendCaesar
(sometraditionswillneverdie)
Uwillknowwhat2dowhenUunscramble"Howdaddyisdoing"
```

The writing style here is immediately noticeable and non-standard for 1o57, definitely a hint as to its true nature. Searching this on google we find that it refers to the movie L.A. Story in which Steve Martin frequently talks to a freeway sign. The sign is unable to write full sentences due to lack of space on his face so he writes them bunched up with numbers for words just like our text here.

![](https://i.imgur.com/r635VqH.jpg)

During the movie the sign gives Steve Martin a riddle telling him he will know what to do when he unscrambles "How is daddy doing". At the end of the movie his love interest, Victoria Tennant unscrambles the message to "Sing doo wah diddy". Hilariously enough she spoke her solution steps out loud and they do not result in the correct answer.

We interpreted this as needing to perform an anagram and set to unscramble the letters as this was the most logical path considering our information. Unfortunately this couldn't be farther from the truth and we fell down a rabbit hole for hours. We later found it was actually a Keyed Vignère cipher with the Alphabet and Passphrase set to LASTORY.

I cannot remember how we came about this answer but there were a lot of enraged words flying about when it was solved. The translation comes out to the following.

```

WELL DONE GET THE BLUE KEY PASS PHRASE FROM OPPENHEIMERS BIG BANG.
```

Without more information on what Oppenheimers big bang is we can move on to Step\_3

* * *

## Step\_3

* * *

The DEFCON 23 package had two CDs, one was a data CD and the other was a soundtrack. Similar to previous years badge challenges, we knew there was likely important information on one of these CD's. We set upon ripping them to our machines and inspecting the files.

None of the audio files held any secrets, no interesting spectrograms or hidden messages there. We found an encrypted MysteryFolder.rar and a program called ChipSec. We dumped the strings of ChipSec to see if anything was hidden there and found nothing so we set upon the RAR file.

Here is the file path:

```

data\Extras\1o57\Extras\MysteryFolder.rar
```

We popped open the RAR file in a hex editor just to confirm it was in fact a real RAR and not some sleight of hand. Thankfully it was but we didn't have a password for it so we shuffled this to the side and branched out for more information.

Without a password we moved on to Step\_4

* * *

## Step\_4

* * *

This year the DEFCON badge was a playable record. One of our team members ran to FRY's Electronics to obtain a record player that could dump audio to USB the moment we found out. Upon receiving this glorious machine we found that each record was exactly the same as the last. This was unlike previous years where each caste of badge would contain different information.

![](https://i.imgur.com/PkNOXq6.jpg)

The audio from Side A:

```

Track 1A





















  SoundCloud Widget


















Track 2A





















  SoundCloud Widget


















Track 3A





















  SoundCloud Widget

















```

The audio from Side B:

```

Track 1B





















  SoundCloud Widget

















```

**Track 1A**

This is a reading from the Hackers Manifesto in a slow deep voice. It appears to only be the last three paragraphs and does not contain any cryptographic meaning. That being said, this is a fucking awesome touch and really put people in the right mindset during the challenge.

You can find the full writing here:

http://phrack.org/issues/7/3.html

**Track 2A**

A young girl reads off a number station with a single date stated near the end.

```

-26-18-10-14-21-05-17-13-17-19-22-22-20-19-22-22-08-07-08-22-12-25-01-14-24-12-20-02-24-12-24-10-07-07-06-14-18-02-22-25-18-03-06-24-07-25-11-09-16-14-22-12-01-24-09-25-02-17-22-09-26-24-05-05-20-24-07-23-17-18-04-13-02-11-22-23-24-11-01-07-02-11-19-06-2 jun 18th 2024-13-12-26-09-18-13-16-24-14-12-18-05
```

**Track 3A**

DTMF is the tones produced when you hit a number on your phone. Each one is a dual tone sound one of which is high and the other low. The controller on the other end hears these tones and understands what button you pressed.

We pulled the audio into Audacity and viewed it was a spectrogram. This allowed us to easily split the tones based upon which frequencies were coupled together.

![](https://i.imgur.com/24AyJwd.png)

We then used a DTMF guidebook to determine which number on the dial pad was pressed. If both the upper and lower tone were the lowest Hz recorded then we knew the number pressed would be 1 for instance.

|     |     |     |     |
| --- | --- | --- | --- |
| 1 | 2 | 3 | 697 Hz |
| 4 | 5 | 6 | 770 Hz |
| 7 | 8 | 9 | 852 Hz |
| \* | 0 | # | 941 Hz |
| 1209 Hz | 1336 Hz | 1477 Hz |  |

This decrypted our message into the following information:

```

105710571057
35266386333266
105710571057
7335397277747273479327384368742625377263932738433732637763373267
```

When we saw the 1057 come out we knew we were on the right path but the numbers were jumbled in a way that made no sense. After hours of searching we came across a system known as T9 that converts dialpad numbers into letters based on predictive text.

Description of T9

https://en.wikipedia.org/wiki/T9\_%28predictive\_text%29

This then deciphers into the following:

```

105710571057
elcometodefcon
105710571057
redkeypassphraseiswearethemusicmakersandwearethedreamersofdreams
```

With the red key in hand and a hint towards the blue key we were feeling pretty good at this point. None of the information we had could open the RAR file from earlier so we moved on to the lanyards.

* * *

## Step\_5

* * *

For this part of the challenge 1o57 presented everyone with a number of keyboards

![](https://i.imgur.com/HTrRn1g.png)

The lanyards detail two enciphering methods. The box-like Nyctograph and the symbol driven Gold Bug

```

Nyctograph:
http://www.lewiscarroll.org/tag/nyctograph/

Gold Bug:
https://en.wikipedia.org/wiki/The_Gold-Bug
```

![](https://i.imgur.com/NOPANLy.png)

The lanyards could be decoded directly using these enciphering methods. We decoded them as follows.

```

Decoded Goldbug Lanyards
GDTOZEDNPMXDCJKXVLMYE
KRHLMVDFDFXDCHBKHDCV
LHBNDKHBDVHDB

Decoded Nyctograph Lanyards
WAITASNOTIPFITSPADPICK
WARPTORNRIFTIMSECURE
EXISTOVEREXPO
```

This was just the first layer of our lanyard decoding so we then set to work on the output texts. We noticed that each line of decoded text was exactly the same length.

1o57 then tweeted the following image.

![](https://i.imgur.com/fxcwsaZ.jpg)

This led us to use a playfair cipher with our decoded text and a QWERTY keyboard as the playfair board. This worked by taking the first letter of each decoded line and using them against your keyboard. For instance GW on your keyboard drawn as a box gives you TS as the other two box corners. This is the basis of playfair.

This came to the following output

```

theplaceyouseekisfound
ifyoureverseengineer
ontheinternet
```

With our lanyards decoded we set off to Step\_6

* * *

## Step\_6

* * *

Reversing Engineer on the internet is a really clever way of pushing us towards a website. After a few attempts at mixing engineer around we came to the following URL by taking the reverse of engineer and adding .engineer to it.

http://reenigne.engineer/

This page is dominated by a single image

![](https://i.imgur.com/ftKxIDw.png)

The first thing that stood out to us on this page was the reference to the word 'file'. We have our RAR file from Step\_3 so this seems to somehow contain the password for our RAR.

There are also a number of references to X-Files in the image content, name, and title.

The title of 'Star me kitten.' is a reference to William S Burroughs song that is inspired by the X-Files.

https://www.youtube.com/watch?v=xwmFaozzhJM

The text can be linked to a number of characters from the X-Files as shown here.

```

Fox (Fox Mulder)
Skin’er (Walter Skinner)
a lone (Lone Gunmen)
red hair (Dana Scully)
```

The commas and apostrophes are lined up and can be converted to 1's and 0's and then into an ascii X.

```

','',,,
1011000
X
```

The FBI warning points to either opening credits in a movie or just to that this deals with the FBI agents of the X-Files. Needless to say this page is drenched in X-Files references we just need to dig through them to understand the point.

At first we tried to take the text literally and build a password out of the actors and characters names. In last years challenge the password was exceedingly long so it stood to reason this one might be as well. None of these attempts worked and no combination seemed to yield any results.

When we were about to give up one of our team members who was unfamiliar with the show watched the opening credits. A few moments later he exlaimed THE TRUTH IS OUT THERE and went to try it.

There are few times where I feel like an absolute fool during these challenges, this was definitely one of them as we had overlooked the most obvious answer. The password to the RAR ended up being 'Thetruthisoutthere.' which fit all of the clues on the page.

```

first at the capital
Capitalize the password on the first letter

even if they have no space
Remove all of the spaces from the password

period
End the password with a period
```

With our RAR open we can now move on to Step\_7

* * *

## Step\_7

* * *

Our RAR contained the following files.

```

DigitalFun.jpg














































            Share

            ×












                    Link

                    Embed





                    Copy









                    Discover the magic of the Internet



                    The Best Dogs • GIFs • Memes • Science & Tech •
                    Videos •
                    Pancakes • LOLz


                Get the Imgur App














Haunted Mansion.mp3





















  SoundCloud Widget


















SuperNova.JPG














































            Share

            ×












                    Link

                    Embed





                    Copy









                    Discover the magic of the Internet



                    The Best Dogs • GIFs • Memes • Science & Tech •
                    Videos •
                    Pancakes • LOLz


                Get the Imgur App













```

The first thing we set upon was the DigitalFun.jpg file which shows a circuit board schematic.

![](https://i.imgur.com/a4erf31.jpg)

The hint of LostboY.net/? is pointing to this being a URL on the LostboY domain. You can follow each bit down it's pipe to the end and add the resulting 1 to that box.

This takes a rudimentary understanding of electrical schematics and logic gates.

![](https://i.imgur.com/PgQ7xhb.jpg)

We built a quick simulation to beat this puzzle.

![](https://i.imgur.com/AWlLZFl.png)

This comes out to the following output.

```

Resulting Bit Conversion
3E01A

Ending URL
http://lostboy.net/3E01A
```

With a new URL in our hands we move on to Step\_8.

* * *

## Step\_8

* * *

This page has a number of images as shown here.

![](https://i.imgur.com/J0UNuum.png)

It also has a block of text, some text hidden in HTML comments, and an interesting title.

```

TITLE:
This Island Answer

HTML COMMENTS:
Is the answer written on the stars?
Did you really think I'd put hints here? Don't be a knob...

TEXT BLOCK:
It's moving to think of all of you
helping a
number of little girls
find their way...
I'll be sure to keep a
record
of your good deeds.
```

The text block seems to be referencing the little girl number station we found back in Step\_4 so this may lead to the answer for that section.

Each of the images on the page is named as 'Item1.jpg' and so on so that gives us nothing. All of them seem completely unrelated as well so we started to reverse image lookup each one. Here is a list of each item we found.

```

1. Alabaster Statue
2. Russian Samovar
3. Mary Shelly Hair
4. Venus Boticelli
5. Cigar Cutter
6. Crystal Glasses
7. Pistol
8. Old Lamp
9. Portrait of Rembrandt's Father
10. Laocoön by El Grecos
11. At the Cafe La Mice
12. Burke's Peerage
13. Pricess Bride
14. The Fishmongers Apprentice
15. An old IBM
16. Potting Business Book
17. Yachting Book
18. Atilla the Hun
19. Token
20. Treasure
21. Yesterday by The Beatles
22. Clock and Watch Repair
23. Silver Pitcher
```

At first glance this is a menagerie of unrelated items and gives us nothing in terms of coorelation. However, dropping a few of them into google reveals something rather incredible.

1o57 has turned the entire song of Portobello Road from Bedknobs and Broomsticks into images on the page.

http://disney.wikia.com/wiki/Portobello\_Road\_%28song%29

This is absolutely brilliant and it is clear that we have the correct answer due to the previous hint of 'Don't be a knob'. Now that we have our target we can apply the rest of our hints and try to figure it out. Searching for 'Bedknobs and Broomsticks star' immediately brings us to the Great Star of Astoroth.

![](https://i.imgur.com/k3Urb9S.jpg)

```

TREGUNA
MEKOIDES
TRECORUM
SATIS
DEE
```

Now that we have our key we can use it against the target pointed to by the block of text at the bottom of the page. This brings us to Step\_9

* * *

## Step\_9

* * *

In Step\_8 we got a hint that the solve would be related to a 'number of little girls'. The number station we collected in Step\_4 was voiced by a little girl so we can now attempt to solve this. Here is the block from earlier.

```

-26-18-10-14-21-05-17-13-17-19-22-22-20-19-22-22-08-07-08-22-12-25-01-14-24-12-20-02-24-12-24-10-07-07-06-14-18-02-22-25-18-03-06-24-07-25-11-09-16-14-22-12-01-24-09-25-02-17-22-09-26-24-05-05-20-24-07-23-17-18-04-13-02-11-22-23-24-11-01-07-02-11-19-06-2 jun 18th 2024-13-12-26-09-18-13-16-24-14-12-18-05
```

Our first step was solving the room keys that gave us the hidden step for this number station.

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Card 1 | Card 2 | Card 3 | Card 4 | Card 5 |
| LITTLE | GIRL | RECORD | TWO | FIVE |

This then turns our number station into the following by adding 2 and 5 to the beginning.

```

25-26-18-10-14-21-05-17-13-17-19-22-22-20-19-22-22-08-07-08-22-12-25-01-14-24-12-20-02-24-12-24-10-07-07-06-14-18-02-22-25-18-03-06-24-07-25-11-09-16-14-22-12-01-24-09-25-02-17-22-09-26-24-05-05-20-24-07-23-17-18-04-13-02-11-22-23-24-11-01-07-02-11-19-06-2 jun 18th 2024-13-12-26-09-18-13-16-24-14-12-18-05
```

We can then crunch the date into 23 as all of the digits of june 18th 2024 add up to 23. (DEFCON 23)

```

25-26-18-10-14-21-05-17-13-17-19-22-22-20-19-22-22-08-07-08-22-12-25-01-14-24-12-20-02-24-12-24-10-07-07-06-14-18-02-22-25-18-03-06-24-07-25-11-09-16-14-22-12-01-24-09-25-02-17-22-09-26-24-05-05-20-24-07-23-17-18-04-13-02-11-22-23-24-11-01-07-02-11-19-06-23-13-12-26-09-18-13-16-24-14-12-18-05
```

None of these numbers are below 1 or above 26 so we can convert them directly over to the Alphabet as follows.

```

YZRJNUEQMQSVVTSVVHGHVLYANXLTBXLXJGGFNRBVYRCFXGYKIPNVLAXIYBQVIZXEETXGWQRDMBKVWXKAGBKSFWMLZIRMPXNLRE
```

We can then use TREGUNAMEKOIDESTRECORUMSATISDEE as vignere key to decrypt our message.

```

FINDTHEEIGENSPACEDETERMINEDBYTHESCALARPRODUCTOFTENZEROFIFTYSEVENANDTWENTYTHREETWENTYTEMSRQOILEWHLK

FIND THE EIGEN SPACE DETERMINED BY THE SCALAR PRODUCT OF TEN ZERO FIFTY SEVEN AND TWENTY THREE TWENTY THREE TWENTY THREE
```

Even though our decipherment wasn't perfect we were able to get a proper hint out of this message. Find the eigen space determined by the scalar product of the ten zero fifty seven. Before trying any math we searched the given terminology to prevent falling down additional rabbit holes. Thankfully we found that a Scalar Product may also be called a Dot Product. This then allows us to create the URL of Eigen.Space as it is the Dot Product of Eigen Space!

With Eigen.Space in tow we move on to Step\_10

* * *

## Step\_10

* * *

At this point our outlook on reality had been warped to such a point that things such as eigen.space were coming naturally. The cryptographic destroying machine was in full swing and sleep was at an all time low.

The eigen.space domain is composed of an image in the background, multiple references to Feynman, a mathematical equation, a cigar, and an animated gif of Sheldon from the Big Bang Theory TV Show.

![](https://i.imgur.com/lpyRini.png)

In the source for the page we also find a few HTML comments and hold on to them for later.

```

1. innovation is a very difficult thing in the real world
2. Why are things always the last place you look for them?
```

The cigar comes with a tagline of 'Sometimes...' which refers to the quote by Sigmeund Freud stating that sometimes things are exactly as they appear and nothing more or less. Knowing this we must apply Occam's Razor liberally to this page and make sure not to fall down any rabbit holes.

The equation in the center of the page is as follows.

```

1, 0, 16,
384, 23040, 2088960, 278323200,
50969640960, 12290021130240, 3774394191052800, 1438421245702963200,
666120016990568448000, 368420070161105761075200, 239869937154980747988172800
```

This equation describes 'The number of ways n couples can sit in rows of two seats with no person next to their partner.' Hilariously the equations author is Stewart Herring... Red Herring... We threw it away immediately and never found a use for it.

https://oeis.org/A189849

The costume from the Big Bang Theory gif is in reference to the Doppler Effect as seen here.

YouTube

Tap to unmute

Video unavailable

This video is no longer available because the YouTube account associated with this video has been terminated.

[Visit YouTube to search for more videos](https://www.youtube.com/)

It clicked immediately, a cigar is just a cigar, the equation on the page has no meaning the sound is just a sound under the Doppler effect. With this in mind we squished the image to remove the Doppler effect, rotated it, and inverted the color to be read by a tool called Coagula Light.

![](https://i.imgur.com/a33a2sV.png)

This came out to the following sound file.

SoundCloud Widget

When dealing with image to sound services black is most generally considered empty space and produces no sound so inverting the color allowed us to listen to this snippet. Coagula Light is one of my favorite tools although ancient and can be found here.

https://www.abc.se/~re/Coagula/Coagula.html

The sound file is 1o57 saying the following cryptic message

```

THIS IS 1057 WHEN REVERSE ENGINEERING LOOK FOR BUFFER OVERFLOWS UNALLOCATED SPACE OR ROP OPPORTUNITIES FOR AN APPROPRIATE ATTACK VECTOR.
```

Considering Reverse Engineer was a URL previously we tried each of these as a URL and struck gold.

This led to http://unallocated.space and Step\_11

* * *

## Step\_11

* * *

This page shows a number of Elements and Atomic Masses in columns and the title of the page is 1120 bits.

![](https://i.imgur.com/D990Gr7.png)

1120 bits refers to Short Message Service or SMS so we know that this has somehting to dow with a phone. Further the rows come out to 10 so 3 area code, 7 for number.

https://en.wikipedia.org/wiki/Short\_Message\_Service

There is also an HTML comment on the page that hints at the true nature of the elements.

```

1. Have you ever wondered why it's 1o57, and not 1057?
```

We tried all kinds of things with this list and 1o57 played with us quite a bit before revealing that the area code for the number we desired was 202. If we lay out the elements we have we can convert them as shown here.

```

He	106.42
O	144.24
He	10.811
N	208.9804
N	28.0855
O	65.39
O	102.9055
He	237.0
Be	30.9738
He	91.224
```

Turning each element on the left column into their atomic number barring the O's due to 1o57's hint we get the following.

```

2	106.42
0	144.24
2	10.811
7	208.9804
7	28.0855
0	65.39
0	102.9055
2	237.0
4	30.9738
2	91.224
```

This gives us the number (202) 7700-242 which we can then send a text to. A few moments later you receive an automated response.

```

¯\_(ツ)_/¯ Find 1o57. Tell him you would like to buy a custom key cap. He will tell you they cost a dollar. Pay him with a two dollar bill, and say keep the change.
```

This was meant to be a chase around Vegas to find a $2 bill, but someone on our team happened to have a “lucky” $2 bill in their wallet. Lucky indeed! We sprinted full speed down to the 1057 room, told LosT we were interested in buying a custom key cap and handed him a $2 bill.

When we handed him the bill he gave us a key cap and a small piece of wood with a skull on one side. I will not be revealing what information was on this skull as it leads to a message crafted specifically for those in the challenge.

![](https://i.imgur.com/bG9Ixdo.jpg)

After receiving that message it eventually leads us to the final domain and Step\_11

* * *

## Step\_11

* * *

The final URL is http://walley.world/ a page dominated by an image from National Lampoons Vacation and a video of Buckaroo Banzai's End Credits. Both fantastic movies, watch them if you haven't had the chance to.

![](https://i.imgur.com/Qbjsq3M.jpg)

This page also had two HTML comments embedded in it which were incorrectly formatted to have dashes connected to the comment. We found later that this was intentionally done to throw us off.

```

--11-11-1-1--1-1-1-1-1--1-----1111-1--1-1-1-1-1--1-1-1-----1-1-1-1--1-1-1--1-1--1-1--1-1--1-1-1--1-1--1--1-1-11111-1-1-1-1----11-111-1-1-1-1-1--1-1---1-1-1--1-1--1-1--1-1--1-1-1--1-1--1-----1--1111111111111-------1-1-1-1-1-1--1-1--11-11-1---1-1-1-1-1-1-1-1-1-11-----

--11----11---111----11---11-1111---11---111-1-111-1-111-111111@1-1---1-11--11111------11--11---1-1111-1111111-111--11-111-1111--1111.11--1---111------
```

This page led us down a rabbit hole like no other puzzle in my experience. The image is from the movie National Lampoon's Vacation where they visit a park known as Walley World. In the real world this park closed a ride known as Colossus last year as seen in the following URL:

http://www.slashfilm.com/walley-world-roller-coaster-national-lampoons-vacation-closing/

The Colossus was the first large-scale electronic computer and was used in World War 2 at Bletchley Park (Park's Closed) to break the Nazi's Tunny messages. Tunny messages are composed of 5 bit baudot code under the effects of the Lorenz cipher.

After researching this we attempted to break the 1's and -'s by converting them into 5 bit binary baudot and then use a colossus simulation to crack them... in dozens of different ways... This was all a rabbit hole, none of it had to do with the Colossus but we did learn a lot about World War 2, cryptography, and Baudot code.

The cipher used here is called Spirit DVD Code and can be found on rumkin.com in the Substitution section. The bottom message comes out to the following output.

```

TITIVILLUS@MYSTERIOUSBOOKS.NET
```

Emailing that address completed the challenge with the following message in response.

![](https://i.imgur.com/N07p8kB.png)

* * *

## Infinite\_Victory

* * *

Thank you Council of Nine for taking us in and believing in your newest members.

We make a fantastic team.

**Council of Nine**

![](https://i.imgur.com/hMVOjks.jpg)

[@bbuerhaus](https://twitter.com/bbuerhaus)

[@\_0rigen](https://twitter.com/_0rigen)

[@erbbysam](https://twitter.com/erbbysam)

[@M57C](https://twitter.com/M57C)

[@jumknail3](https://twitter.com/jumknail3)

[@benjuang](https://twitter.com/benjuang)

[@QAn1nja](https://twitter.com/QAn1nja)

Jon

Deno

Rusty

[@GriftersShoes](https://twitter.com/Grifter801)

[@PotatoSec](https://twitter.com/PotatoSec)