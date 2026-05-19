---
source: zlz-buerhaus
source_url: https://buer.haus/2020/09/11/coin-coin-artist-20k-puzzle-write-up/
title: "coin_artist – 34700 $coin Puzzle Write-Up ($20,000) | ziot"
---

[< Back](https://buer.haus/)

[![](http://buer.haus/wp-content/uploads/2020/09/logo-1-1024x341.png)](https://buer.haus/wp-content/uploads/2020/09/logo-1.png)

Solvers:

- [ziot - Brett Buerhaus](https://twitter.com/bbuerhaus)
- [JTobcat - Justin Tobin](https://twitter.com/jtobcat)
- [LeFevre - Ben LeFevre](https://twitter.com/_LeFevre_)
- [mattm - Matt McQuaig](https://twitter.com/mattmcquaig)

A few of us recently participated in another puzzle and managed to be victorious, collecting 34700 [$coin](https://uniswap.info/token/0x87b008e57f640d94ee44fd893f0323af933f9195) (est $20,000 at time of solve) prize. [coin\_artist](https://twitter.com/coin_artist) of Blockade Game and Bitcoin fame recently launched a new crypto currency called $coin. She had the idea of having the coin's original value backed by the purchase of NFTs that cost several Ethereum.

There was a clever stipulation involved though, anyone who owned one of these original $coin NFTs would be able to solve a puzzle with a $coin reward once launched. [Cloverme of Age of Rust (Space Pirate)](https://www.ageofrust.games/) purchased a few of these NFTs and gifted one of them to us. This gave us the chance to participate and attempt to solve her puzzle.

With the launch of $coin, it unleashed a new puzzle designed and created by [Lee Sparks (motive)](https://twitter.com/leemsparks).

Let's dive into it.

# Stage 0: Start

The initial puzzle began with [coin\_artist](https://twitter.com/coin_artist) announcing the puzzle on Twitter:

Twitter Embed

> [$COIN](https://twitter.com/search?q=%24COIN&src=ctag&ref_src=twsrc%5Etfw) IS LIVE! This crypto puzzle features COIN, the BOSS of a Neon District Syndicate.
>
> This image contains everything you need to explore Coin's E-Den for a bounty of 34700 COIN. Good luck! ⚔️ [https://t.co/bYjnrYnqm5](https://t.co/bYjnrYnqm5) [pic.twitter.com/MlFeiFHITJ](https://t.co/MlFeiFHITJ)
>
> — YT $COIN ⚔️ coinartist.eth (@coin\_artist) [September 5, 2020](https://twitter.com/coin_artist/status/1302261520601096195?ref_src=twsrc%5Etfw)

It's important you follow this link to the blog post and get the raw original image here:

[https://ibb.co/N9Q4r8x](https://ibb.co/N9Q4r8x)

Analyzing the image, we see the following.

![](http://buer.haus/wp-content/uploads/2020/09/1.png)

Using a visual stego tool such as stegsolve and scrolling through the various channels, we can see that those lines are actually morse code in an alpha layer.

![](http://buer.haus/wp-content/uploads/2020/09/2.png)

We proceed to cconvert that into morse code, this gives you: **COINTOKENSWAP**

So we:

- go to [cointokenswap.com](https://cointokenswap.com/)
- Swap the old version of $COIN for the new version.
- Interact with the bot on the Neon District Discord to get access to private Discord channel for Coin's E-den

This led to a countdown and we had to wait for the puzzle to launch.

# Stage 1: Street Scum

... once the countdown hit on mid-afternoon EST 9/10/20, we were greeted with a new channel. The Blockade Games Discord has a bot that checks to see if you have $coin in your wallet and assigns you a new Discord role. With this bot, they were able to verify that you were eligible for the puzzle and this automatically adds you to a new Discord channel.

![](http://buer.haus/wp-content/uploads/2020/09/streetscum.png)

Inside of the new #puzzle-street-scum channel, there is a Discord bot named $CERES-IV.

![](http://buer.haus/wp-content/uploads/2020/09/ceresbot.png)

The bot tells you that it has a few different commands:

```
$CERES-IV
BOT
09/10/2020
Hello. I'm CERES-IV, the AI.
Here's what I can do:

1. Type "$ceres-iv muse" and I will generate text randomly
2. Type "$ceres-iv ask [yourtexthere] " and I will generate text based on your input
3. DM me with your answers and it will be submitted for evaluation.
```

Despite the bot being interactive, the first thing we notice is in the channel topic:

```
uhzrxhcgheotg.gsf/lniym106
$ceres-iv help
```

`
`

``

Although we tried a bit, this was the beginning of the puzzle and the answer is relatively obvious as there is not much to go off of yet.

[https://gchq.github.io/CyberChef/#recipe=Vigen%C3%A8re\_Decode('streetscum')&input=dWh6cnhoY2doZW90Zy5nc2YvbG5peW0xMDY](https://gchq.github.io/CyberChef/#recipe=Vigen%C3%A8re_Decode('streetscum')&input=dWh6cnhoY2doZW90Zy5nc2YvbG5peW0xMDY)

Vigenere with the code of **streetscum** gives you:

```
cointokenswap.com/tlomu106
```

This leads to a 55mb wav file.

SoundCloud Widget

[Brett Buerhaus](https://soundcloud.com/brett-buerhaus "Brett Buerhaus") · [$coin Puzzle - tlomu106.wav](https://soundcloud.com/brett-buerhaus/coin-puzzle-tlomu106wav "$coin Puzzle - tlomu106.wav")

You'll notice that the beginning and end have DTMF tones, but there is a song in-between them. If you load this file up in Audacity, you'll see the following. The highlighted yellow areas are the DTMF tones:

[![](http://buer.haus/wp-content/uploads/2020/09/audio-1024x307.png)](http://buer.haus/wp-content/uploads/2020/09/audio.png)

There are a few ways you can extract this information. One method is to use a tool like Sonic Visualizer and view the Spectrogram, e.g.

[![](http://buer.haus/wp-content/uploads/2020/09/spectrogram-1024x454.png)](http://buer.haus/wp-content/uploads/2020/09/spectrogram.png)

Another method is to use an audio tool like Audacity, extract the audio out, and export it as wav. There are some online tools that will decode wav files and convert the DTMF tones into their number representations. This works because DTMF buttons have specific frequencies and the websites are able to parse the frequency throughout the audio.

Here's the start DTMF ( **volume warning**):

SoundCloud Widget

[Brett Buerhaus](https://soundcloud.com/brett-buerhaus "Brett Buerhaus") · [$Coin Puzzle DTMF Start](https://soundcloud.com/brett-buerhaus/start "$Coin Puzzle DTMF Start")

And here's the end DTMF:

SoundCloud Widget

[Brett Buerhaus](https://soundcloud.com/brett-buerhaus "Brett Buerhaus") · [$Coin Puzzle - DTMF End](https://soundcloud.com/brett-buerhaus/coin-puzzle-dtmf-end "$Coin Puzzle - DTMF End")

Unfortunately, individually the DTMF tones meant nothing. There are 16 tones in the beginning of the song and 16 at the end. Dual Tone Multi Frequency(DTMF) requires 2 tones per button. The starting tones are the lower frequency, and the ending tones are the higher frequencies. Using the DTMF chart you can find the button intersection for each tone pair.

![](http://buer.haus/wp-content/uploads/2020/09/unknown.png)

The result is **2633967366366642** and the resulting output is **CODEWORD MNEMONIC**.

Sending the word **MNEMONIC** to the Discord bot, we get the following:

![](http://buer.haus/wp-content/uploads/2020/09/mnemonic.png)

This completed the first step and sent you to a new channel - #puzzle-runner.

## Stage 2: Runner

![](http://buer.haus/wp-content/uploads/2020/09/runner.png)

This channel had the following in the topic:

```
ar52K:ye#F]4pE>idPzIj>jT%yF2!5#qVR01j>N1r%zt,PqmKBy15+qiLR*&ZQ`oKBxIU*%;$yV%lEOiWuDg<W{{$y^4axlLwrdKY@UCN!]+qxM
```

With the special characters in the string, it looks like it'll be a base85 (ASCII85) or similar encoding. Not many encodings have these types of special characters and casings in them. It took us awhile, but we eventually found out there is a Base91 out there.

Using [dcode's Base91 tool](https://www.dcode.fr/base-91-encoding), we were able to get the following output:

[![](http://buer.haus/wp-content/uploads/2020/09/base91-1024x259.png)](http://buer.haus/wp-content/uploads/2020/09/base91.png)

```
combine the creators of my favorite game and favorite album and apply to what you repaired
```

So we go back to the Discord bot and ask the following:

- What is your favorite game?
- What is your favorite album?

Favorite game:

![](http://buer.haus/wp-content/uploads/2020/09/unknown-7.png)

Answer: Minecraft

Creator: Notch

Favorite album:

![](http://buer.haus/wp-content/uploads/2020/09/favoritealbum.png)

Answer: The Amalgamut

Creator: Filter

Combining the two answers, you get the following answer: Notch Filter.

We 'repaired' the audio file, so we go back and try to apply the Notch Filter. The Notch Filter works by allowing you to destroy audio above a certain frequency range. By removing the frequency for the DTMF tones, you can now hear the voice of a woman reading out numbers. Here's a sample of what that sounded like:

SoundCloud Widget

[Brett Buerhaus](https://soundcloud.com/brett-buerhaus "Brett Buerhaus") · [$Coin Puzzle - Filtered Codes](https://soundcloud.com/brett-buerhaus/start-code "$Coin Puzzle - Filtered Codes")

Extracting what the woman is reading out, you get the following:

```
6d 75 73 31 63 61 6c 61 72 74 73 31 36 6d 70 34
```

Converting hex to ascii, you get the following string out: mus1calarts16.mp3

This leads to a new file:

[https://cointokenswap.com/mus1calarts16.mp3](https://cointokenswap.com/mus1calarts16.mp3)

This file fails to load in the browser, but it looks like a valid mp3 at a glance. Opening it in a hex editor, you see the following:

![](http://buer.haus/wp-content/uploads/2020/09/footerdata.png)

It's quick to notice that this is ASCII art hidden in the base of the mp3 file:

[![](http://buer.haus/wp-content/uploads/2020/09/asciiart-1024x771.png)](http://buer.haus/wp-content/uploads/2020/09/asciiart.png)

This gives you a new word: **n3tw0rk3duP**

Boom~!

![](http://buer.haus/wp-content/uploads/2020/09/n3t.png)

This moved us up to the #puzzle-handler channel.

## Stage 3: Handler

![](http://buer.haus/wp-content/uploads/2020/09/handler.png)

This channel has the topic of the following:

```
1.$+>:c;6Z/1<qX.m,jL3<    xCERES ver.
```

The text on the right says "CERES ver." which is the Discord bot name. If you take the "IV" from the name and treat it as 4, you eventually come to the conclusion that this is enciphered 4 times in a row. So you take the cipher text and base85 (ascii85) decode 4 times in a row. This gives the following output:

**frown106**

Toss this into the website: [https://cointokenswap.com/frown106](https://cointokenswap.com/frown106) and you get a new wav file. If you listen to it, you realize it's the same as the first tlomu106 wav file. After doing an md5 checksum on both files, you will realize that both files are not entirely the same even though the audio matches. Knowing they were different, we assumed maybe some audio differed. Tossing these into Sonic Visualizer, they look identical:

![](http://buer.haus/wp-content/uploads/2020/09/unknown-6.png)

It took a bit, but eventually we realized that the two names matched up:

- tlomu106
- frown106

frown could come up to tlomu if you "turn that frown upside-down". If you take both files and overlay them in a tool like Audacity, then you invert the frown file, the audio becomes completely silent. But there is a timeframe between 1:05 and 1:25 where a new "modem" sound plays.

SoundCloud Widget

[Brett Buerhaus](https://soundcloud.com/brett-buerhaus "Brett Buerhaus") · [$coin Puzzle - Modem Sounds](https://soundcloud.com/brett-buerhaus/modem-sounds "$coin Puzzle - Modem Sounds")

If you know it, you know it. You can quickly recognize that this sound is SSTV and an image embedded in noise.

![](http://buer.haus/wp-content/uploads/2020/09/sstv.png)

This gives you a new string: "/p4r4d1s3". You would think it's a new endpoint, but it's a string you send to the Discord bot:

![](http://buer.haus/wp-content/uploads/2020/09/p4r4d1s3.png)

```
JACK 3 tokyo zip QUEEN tokyo 5 xbox PARK QUEEN JACK WALMART GOLF walmart FRUIT queen WALMART HULU 8 NUT 2 VISA queen bestbuy EGG egg WALMART xbox coffee 2 9 4
```

It's quick to recognize that this cipher is simply a string encoded with words and numbers. Taking the first character or number and casing, you get the following: **J3tzQt5xPQJWGwFqWH8N2VqbEgWxc294**. This leads to a new file:

[https://cointokenswap.com/J3tzQt5xPQJWGwFqWH8N2VqbEgWxc294](https://cointokenswap.com/J3tzQt5xPQJWGwFqWH8N2VqbEgWxc294)

Downloading this file and viewing it with a hex editor. You quickly recognize that this file does not contain any magic bytes, strings, or anything; it's just a file with seemingly random data.

![](http://buer.haus/wp-content/uploads/2020/09/junk.png)

This is when we tapped into CTF forensic mentality and started to analyzing it as a file that has been xor'd. To put simply, a file of bytes that are the result of being manipulated with other bytes. The goal would be to reverse what was done to get the original bytes out. The first thing you do when you are trying to xor an unknown file type is to throw all the known magic bytes you can at it. This will either expose another file via magic bytes (xor of two files) or a string used as a xor key.

Going to the ["file signatures" section of Wikipedia](https://en.wikipedia.org/wiki/List_of_file_signatures) we start to copy hex bytes of different file types such as jpg, wav, png, gif, etc.

[![](http://buer.haus/wp-content/uploads/2020/09/magic-bytes-1024x357.png)](http://buer.haus/wp-content/uploads/2020/09/magic-bytes.png)

In the past, you had to pay real good attention or memorize a lot of different magic bytes to go this route. Lucky for us, Cyberchef can identify most of the common file formats nowadays and let you know if you're on the right path:

[![](http://buer.haus/wp-content/uploads/2020/09/unknown-1-1024x691.png)](http://buer.haus/wp-content/uploads/2020/09/unknown-1.png)

Putting in the hex bytes for WAV and xoring the junk file, we see that we get the magic bytes for a TIF image. So we know that we need to XOR a wav file with this junk file to get a TIF image out.

[\[Click this link to see how it works on Cyberchef\]](https://gchq.github.io/CyberChef/#recipe=From_Hex('Auto')XOR(%7B'option':'Hex','string':'52%2049%2046%2046%20??%20??%20??%20??%2057%2041%2056%2045'%7D,'Standard',false)Detect_File_Type(true,true,true,true,true,true,true)&input=MUIgMDAgNkMgNDYgMUUgMTIgNzEgMDMgRDcgNTUgNTkgNDIgMTEgOTUgNzYgMkQgMTcgODQgNDIgNjEgNTEgQjggNjYgMzYgNTkgQTMgODggNDQgRkEgNTggM0MgQTQgNTAgMkQgMEYgOEMgMkMgMTYgM0YgRDMgRDAgNzYgM0QgMUYgOTAgNDggNjQgNTIgMzkgMjQgOTYgNEQgMjcgODkgNDAgQTAgOTIgODkgNjQgQjYgNUQgMkYgOTggNEMgNjYgNTMgMzkgQTQgRDYgNkQgMzcgOUMgNEUgMjUgNTAgNTkgQ0MgRjYgN0QgM0YgQTAgNTAgNjggNTQgM0EgMjUgMTYgOEQgMkQgOUQgRDEgRTkgNTQgQkEgNjUgMzYgRjkgMkUgREMgMzUgODIgQzUgRTkgOTYgNTYgQUQgNTcgQUMgNTYgNkIgOTUgQUQgMEQgOTIgQUUgNUYgNjEgMUMgNkMgOTggN0YgMjUgOEYgMzQgNjUgNTggRDMgNkQgQjIgNUIgNjUgNUQgREIgNjcgODIgMTAgNkYgN0UgNzcgQTQgQkEgNkIgNzEgRDcgOUEgNkUgQTUgRjAgRTcgMEQgMUEgN0EgMTMgQkUgNzIgRjQgRTIgMjQgNTIgNzcgODYgODYgMTQgNzIgQUMgQUEgMTIgRjYgMDggOEIgMzkgQzggNzYgQTcgODAgNzIgNjggNjUgOTIgRTAgMkUgNjEgRDAgOEIgRDMgRkMgRUEgOUEgODkgMUQgMzUgRjggNDIgMjAgNjggOUEgOEYgM0MgM0UgRjMgOEYgODMgNjIgMTIgNkQgQUEgQTMgRkMgNzEgREYgMkQgNzkgMTQgQUIgQjAgMTQgOTcgQTcgRjcgNjcgMTMgRDYgRTAgNzAgCg)

Result:

![](http://buer.haus/wp-content/uploads/2020/09/tiff.png)

Now we know that we need to take one of the wav files (frown106.wav or tlomu106.wav) and XOR it against the J3tzQt5xPQJWGwFqWH8N2VqbEeWxc294 junk file. Using a tool like [XorJ](https://github.com/ae27ff/XorJ) we can put both files in and get the TIF out real fast.

![](http://buer.haus/wp-content/uploads/2020/09/xorj.png)

And this is the TIF file we get out:

[![](http://buer.haus/wp-content/uploads/2020/09/unknown-2-76x1024.png)](http://buer.haus/wp-content/uploads/2020/09/unknown-2.png)

We get an image with a strange looking alien symbol language. After spending hours looking for a font or trying to decode the cipher into morse, ternary, or something of the sort, we eventually had a realization. We can cut the image into three columns and they almost exactly align. After a bit of rotation, they align perfectly.

![](http://buer.haus/wp-content/uploads/2020/09/unknown-3.png)

Although it looks like we got some strange looking letters in here, we could not get legible text out. Deep diving into the dots, we finally realized we could color them in to get some text out:

![](http://buer.haus/wp-content/uploads/2020/09/fancy.png)

This gives us the string: **st3r3oglyph**. Yeeting it off to the bot:

![](http://buer.haus/wp-content/uploads/2020/09/st3r3oglyph.png)

```
At least! This is a significant discovery. Return to the beginning with this bit of information and tell me what you unPElock.
```

At the same time, this also updates you to the top role "mastermind" letting you know this is likely the last step (or steps) of the puzzle.

![](http://buer.haus/wp-content/uploads/2020/09/mastermind.png)

This step is fairly on the nose with what you need to do. If you look at the text, you can see the following words least, significant, bit. This is a hint towards "LSB" stenography. It also gives you the hint of "PELock" which turned out to be a stego tool. It also says "return to the beginning" which was either referencing the initial coin\_artist $coin image or wav.

Using the following website with the password and the $coin png:

[https://www.pelock.com/products/steganography-online-codec](https://www.pelock.com/products/steganography-online-codec)

We get the following out:

![](http://buer.haus/wp-content/uploads/2020/09/unknown-5.png)

Boomski!

![](http://buer.haus/wp-content/uploads/2020/09/soulve.png)

Solved!

## Fin

This ended up being a fun technical puzzle that also led to one of the bigger prizes we have seen. This is mostly due to [$coin growing rapidly and being worth a lot more money than original speculated](https://uniswap.info/token/0x87b008e57f640d94ee44fd893f0323af933f9195). We hope that $coin will continue to have lots of engagement of this type and that people will be able to experience lots of fun puzzles like this in the future.

If you enjoy reading these write-ups and are wondering how you can get notified of cool puzzles or get involved in solving them, there are a few Discord's I recommend joining:

- [Crypto Puzzles - https://discord.gg/vgdj9t5](https://discord.gg/vgdj9t5)
- [Neon District - https://discord.gg/7sNBV6v](https://discord.gg/7sNBV6v)

## Special Thanks

I also cannot recommend enough that you follow these people on Twitter:

- [Lee Sparks (motive)](https://twitter.com/leemsparks) for making this awesome puzzle.
- [Cloverme of Age of Rust (Space Pirate)](https://www.ageofrust.games/) purchased a few of the $coin puzzle NFTs and gifted one of them to us giving us access to the puzzle.
- [Blockade Games](https://twitter.com/blockadegames) / [coin\_artist](https://twitter.com/coin_artist) for always putting out awesome engaging puzzles and content.

Twitter Widget Iframe