---
source: zlz-buerhaus
source_url: https://buer.haus/2018/04/24/montecrypto-argss-write-up/
title: "Montecrypto – ARGSS Write-Up | ziot"
---

[< Back](https://buer.haus/)

# Montecrypto: The Bitcoin Enigma

A solve diary & challenge-by-challenge walkthrough by the crew who cracked it

![](https://buer.haus/wp-content/uploads/montecrypto/image28.jpg)

ARG Solving Station: **Luigy, en, JTobcat, ziot, motive, Askin, lucifers\_cat**

Special thanks to: Austin, nsnc, pipecork

Meet us and learn more in ARGSS [https://discord.me/arg\_solving\_station](https://discord.me/arg_solving_station)

## Solvers

- [@JTobcat](https://twitter.com/jtobcat)
- [@bbuerhaus](https://twitter.com/bbuerhaus) \- ziot
- [@hackerswhoblaze](https://twitter.com/hackerswhoblaze) \- en
- [@leemsparks](https://twitter.com/leemsparks) \- motive
- Askin
- [@Luigy](https://twitter.com/luigyGT)
- Lucifers\_cat
- and others on the [ARGSS Discord](https://discord.me/arg_solving_station)

# Summary

[MonteCrypto](http://store.steampowered.com/app/768750/MonteCrypto_The_Bitcoin_Enigma/)is a UE4 crypto puzzle game that launched on Steam February 20, 2018. You are tasked with completing 24 Enigma puzzles to obtain words used to open a cryptocurrency wallet containing a 1 Bitcoin prize.

Upon entering the game, you land in a lobby with three exits. As soon as you walk through one of the exits, it begins a 60 minute timer that forces the game to restart when the time runs out.

The objective is to use any means necessary to collect the Enigma solutions and figure out how to unlock the Bitcoin wallet. This extended as far as hacking the game client and finding ways to solve broken puzzles.

This write-up is a journey of the tools we used, the technical approach we took to solve each Enigma, and some of the mistakes we made along the way.

# Table of Contents

[Summary](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.4fzuzkpmx0ps)

[2](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.4fzuzkpmx0ps)

[TOOLS USED FOR SOLVING](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.chtdpedaa0uw)

[4](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.chtdpedaa0uw)

[TIMELINE](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.gaarhi3ml613)

[5](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.gaarhi3ml613)

[The Game Map](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.2ez9cz5ah5ok)

[6](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.2ez9cz5ah5ok)

[PI SEQUENCE ORDER](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ilm4uyw0u0h9)

[9](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ilm4uyw0u0h9)

[ENIGMAS](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.nply38281p5h)

[10](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.nply38281p5h)

[Enigma 1](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.p2zyxkwubgc8)

[10](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.p2zyxkwubgc8)

[Enigma 2](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.bylnbbpl1eob)

[13](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.bylnbbpl1eob)

[Enigma 3](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.7gf51ldwx2jv)

[17](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.7gf51ldwx2jv)

[Enigma 4](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.rkuehnobq3um)

[20](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.rkuehnobq3um)

[Enigma 5](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.sy4y7tgb1szw)

[23](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.sy4y7tgb1szw)

[Enigma 6](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.84yzcwqblxm1)

[25](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.84yzcwqblxm1)

[Enigma 7](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ffw9elm0phjh)

[27](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ffw9elm0phjh)

[Enigma 8](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ty67tijyjnc8)

[29](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ty67tijyjnc8)

[Enigma 9](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.w3rm2oli8y7k)

[31](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.w3rm2oli8y7k)

[Enigma 10](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.2efud6pa2at)

[34](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.2efud6pa2at)

[Enigma 11](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.676eiyh9vkrr)

[38](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.676eiyh9vkrr)

[Enigma 12](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.oupsvwyvuk0o)

[42](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.oupsvwyvuk0o)

[Enigma 13](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.vzoxgn4u1uq3)

[43](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.vzoxgn4u1uq3)

[Enigma 14](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ljexlu3q0bpt)

[44](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ljexlu3q0bpt)

[Enigma 15](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.p43asarbazfu)

[45](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.p43asarbazfu)

[Enigma 16](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.1k0lun2ouxpx)

[46](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.1k0lun2ouxpx)

[Enigma 17](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.um6qw8req3lh)

[47](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.um6qw8req3lh)

[Enigma 18](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.qwqx7h7uw85b)

[49](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.qwqx7h7uw85b)

[Enigma 19](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ufya537hv001)

[50](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ufya537hv001)

[Enigma 20](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.rxm7144ppbdu)

[54](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.rxm7144ppbdu)

[Enigma 21](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.xb7hpnknqjbo)

[58](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.xb7hpnknqjbo)

[Enigma 22](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.moayi78q38fb)

[59](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.moayi78q38fb)

[Enigma 23](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.j4wicxmp9nd7)

[60](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.j4wicxmp9nd7)

[Enigma 24](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.vhy7ecfg7dh1)

[62](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.vhy7ecfg7dh1)

[Final Solve Steps / MonteCrypto Solution](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.eq0eunbws3x2)

[65](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.eq0eunbws3x2)

[ADDITIONAL FLAVOR PUZZLES](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.adzgafd1teig)

[66](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.adzgafd1teig)

[Compasses and Skulls](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.2ykhz2vgdzdo)

[66](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.2ykhz2vgdzdo)

[Appendix A - Wallet bruting](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ucajvenfkjpz)

[67](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ucajvenfkjpz)

[Appendix B - Biham and Kocher’s Known Plaintext Attack](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.75md9o3db5wr)

[70](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.75md9o3db5wr)

[Appendix C - Disassembling UE4 Blueprints](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.926e34b9mcgt)

[73](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.926e34b9mcgt)

[Appendix D - important.jpg](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.jzrpr2almlm3)

[75](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.jzrpr2almlm3)

[Appendix E - Our Thoughts on Hacking the Client](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#hax)

[76](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.jzrpr2almlm3)

# TOOLS USED FOR SOLVING

### Ninjaripper

[https://gamebanana.com/tools/5638](https://gamebanana.com/tools/5638)

A tool that we used for ripping images from memory

### Cheatengine

We used this for teleporting and dumping data from game memory early on.

### Austin’s dll

Austin in the GameDetective community created a dll that did a lot of useful things. While some of it just made traversing the game 9000+ times tolerable, it also made one of the puzzles solvable. Without the ability to dump objects and teleport to them, it is likely that only a very few amount of teams would have solved the Spirit cave due to a bug that put all of the spirits outside of the game hallways in inaccessible areas.

- Anti-tp bypass
- noclip
- Game object dumper
- Dumped all of the disassembled code for Blueprints

### Umodel

[http://www.gildor.org/en/projects/umodel](http://www.gildor.org/en/projects/umodel)

This tools lets you load Unreal umodel 3d assets and 2d textures

### Quickbms

[http://aluigi.altervista.org/quickbms.htm](http://aluigi.altervista.org/quickbms.htm)

A tool for extracting Unreal pak files. Using the Unreal Editor 4 script we were able to extract all the files from the MonteCrypto pak file.

### Forensically

[https://29a.ch/photo-forensics/](https://29a.ch/photo-forensics/)

Really useful for quickly spotting weird shit in images without a lot of effort.

### [Password Generator](https://buer.haus/2018/04/24/montecrypto-argss-write-up/\#h.h2vxkqrnf659)

Script we wrote to generate possible wallet passwords using our ordering theory, or every possible order. Handles words we’re not sure about either.

# TIMELINE

An approximate timeline of our Enigma solves:

- (Day 1) 13 - Frog Pond / Jumping
- (Day 1) 17 - QR Codes
- (Day 1) 16 - Achievement
- (Day 1) 22 - Binary Window
- (Day 1) 14 - Server Room
- (Day 1) 6 - Office
- (Day 1) 18 - Blue Room
- (Day 1) 12 - Goblin Statue
- (Day 1) 23 - Painter
- (Day 2) 15 - White Lights
- (Day 3) 3 - Floating Crystal
- (Day 3) 24 - Sun Cave
- (Day 3) 21 - Vault
- (Day 4) 19 - Candle Cave
- (Day 4) 8 - Skull Room
- (Day 4) 5 - Lullaby
- (Day 4) 10 - Library
- (Day 4) 4 - Invisible Staircase
- (Day 4) 7 - Floor Pits-words mined day 1, solved via pi deduction
- (Day 4) 9 - Zelda Forest-words mined day 1, solved via pi deduction
- (Day 4) 1 - Epilepsy-words mined day 1, solved via pi deduction
- (Day 14) 11 - Rain
- (Day 22) 20 - Who Am I?
- (Day 63) 2 - Forest / Outside

# The Game Map

Our first few maps were Photoshop-fu via pulling together screenshots of each others maps as we blindly ran around the maze with one hour-timers preventing us from getting big areas of the maze mapped without needing to retrace our steps. Many times...

![](https://buer.haus/wp-content/uploads/montecrypto/image16.png)

After we realized that the maze extends beyond the confines of the in-game map, this effort quickly diminished and was replaced by mapping it by hand in a Google Spreadsheet, which took 3 people the better part of a week to complete:

Doing this was made easier by a few realizations about how the maze was built as we traversed through it:

- The maze corridors are always odd lengths
- A turn was never made without some length of corridor after the turn
- There are never greater than one distance gaps between parallel corridors
- Other than enigma rooms, there are no large empty spaces

![](https://buer.haus/wp-content/uploads/montecrypto/image61.png)

A labor of love - the maze mapped out by hand in a Google Spreadsheet.

![](https://buer.haus/wp-content/uploads/montecrypto/image35.png)

The map’s legend. We started to list out the locations of all “NOT THAT WAY” mayor appearances as well as the locations of all compasses and skull bookshelves.

# PI SEQUENCE ORDER

One of the first things we discovered in this game when roaming through the halls is that all of the dead-ends contain a creature that shouts “NOT THAT WAY!”. This event occurs as you approach the wall with a small slide opening and the creature briefly shouting at you before closing it. No one really knows what this creature is, but some guessed that this might be The Mayor.

![](https://buer.haus/wp-content/uploads/montecrypto/image43.jpg)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

Inside of the room, there is a terminal on the side that is somewhat obscured unless you look closely. The way the game works, it loads in a tiny room that is hidden above the lobby when you approach those dead-ends. By noclipping you can trivially fly into the tiny room and see the terminal.

The terminal says: Pi 121-144.

Taking the numbers of Pi starting at index 121 and going up until 144 gives you the following numbers: 093844609550582231725359

This gives us 24 numbers, the same number of Enigma/solutions in the game.

It was clear very early on that this was likely the order we needed to use to both validate some of our solutions and give a primary sort order to solution words for the wallet password.

# ENIGMAS

The Enigma solves below are not in the order that we solved them but the linear order based on the room numbers in the game.

## Enigma 1

Room Nickname: Epilepsy

The four possible answers from the game files:

- 5-mzuzwana
- 7-random
- 2-bushido
- 63-monaci

Several members of our team were hesitant to try anything in-game in this room, and for good reason. It is a maze within the maze, made out of invisible walls that trigger strobing lights when you touch them. This could cause serious harm to anyone with epilepsy.

Here is a map of the “maze inside of the maze”:

![](https://buer.haus/wp-content/uploads/montecrypto/image77.png)

Even though we had four possible answers for this room from the game files, we needed to rule out red herrings sooner or later and solve this room in the, what we thought, intended way.

After enduring those strobing lights for what felt like an eternity for the eyes, one of our members found a trigger spot in the back of the room which turned off all lights in the entire maze and gave us, what we called, the “victory sound”, but sadly no solution, yet.

After a while we figured out that there is a cube floating below the room, not visible for anyone who is playing the game without cheats, which had the four possible answers from the game files on it:

![](https://buer.haus/wp-content/uploads/montecrypto/image70.png)

We got one step closer to verifying our hypothesis, but we were still missing something.

It turned out that we needed to run the game with the unpacked .pak file and delete the “BP\_Black” files to see the correct solution projected to the top of the room - 5 mzuzwana.

### ![](https://buer.haus/wp-content/uploads/montecrypto/image13.png)

Solution: 5 mzuzwana

## Enigma 2

Room Nickname: Forest / Outside

A few hours after we got teleport / noclip cheats working we found the forest but had no idea where to start with it. It was the antithesis of low-hanging-fruit and quickly got put on the backburner until we had more information to work with. Little did we know that it would stay there until the end of the hunt.

The terminal text:

Y is sluggish in the sea;

Try and try again;

When and where the least expected;

When you enter the forest from the stairs, this is what you see:

![](https://buer.haus/wp-content/uploads/montecrypto/image19.jpg)

It’s a pretty overwhelming sight as you start to trek through the forest and realize there are over a hundred candles scattered across the area.

Using no-clip we could quickly see a top-down view of the forest:

![](https://buer.haus/wp-content/uploads/montecrypto/image68.png)

Also being able to remove game files, we could see the area without all of the foliage:

![](https://buer.haus/wp-content/uploads/montecrypto/image64.png)

Using similar tricks to datamine info from the game files, we were able to see the Enigma file names and object names contained inside of the files. We discovered that there was a single candle/blueprint named BP\_Actionable\_CandleEn2.

Using Austin’s DLL we were also able to dump all the object locations from memory so we could teleport directly to that candle eliminating the efforts of having to click every single candle in the forest.

Clicking the candle played the victory noise which enabled a PostProcess effect for around 60 seconds. This gave everything a slight blue outline until the timer expired and would disappear.

It’s also worth mentioning that the forest contained four boulders with PhysX enabled on them. As you enter the forest, walking over one of the candles enables the PhysX on it and it starts to roll down a hill in front of you.

![](https://buer.haus/wp-content/uploads/montecrypto/image23.png)

We tried many things over the span of a couple weeks, going as far as teleporting or rolling the rocks to different areas or on top of every candle. In the end, these rocks were red herrings that were not used in the solution.

Eventually @1nvisible#9872 in GD noticed that the PostProcess overlay was adding single pixel dots to the top left of the screen.

![](https://buer.haus/wp-content/uploads/montecrypto/image60.png)

It required a specific resolution and looking at certain areas such as the sky to visibly see the dots in the correct format. This is what it looked like when you extracted it correctly:

![](https://buer.haus/wp-content/uploads/montecrypto/image3.png)

Credits: 1nvisible/GameDetectives

We immediately jumped to the conclusion that this was either morse code or ternary, but neither of those produced useful output. Treating it as morse with an invisible 5 dot starting sequence gave us a 5, which we thought was on the right track. [We started applying every possible decoding scheme](https://i.imgur.com/5aBftnt.png). On the far side we’ve got CNTYHJT, which is off from the correct decoding by one character. This is because there is an invisible dot at the end we didn’t consider. Treating that invisible dot as a “.” gives us CNTYHJN -- which is the intended decoding.

Months later, while shooting the shit with pipecork/nsnc (as we ran [420blaze.in](http://420blaze.in/)), we were discussing outside. They were confident in their solve and told us rot13(CNTYHJN) = pagluwa, which translates to spit -- and if we translate “spit” back to the original language, we get that word back perfectly. This was the last Engima we needed; We used it to crack the Bitcoin wallet shortly after.

It’s funny how a single pixel mistake kept us from solving something many would consider a trivial crypto puzzle. Here is some insight into what our outside doc looked like:

![](https://buer.haus/wp-content/uploads/montecrypto/image67.png)

Solve:

![](https://buer.haus/wp-content/uploads/montecrypto/image73.png)

Solution: 5 pagluwa

## Enigma 3

Room Nickname: Floating Crystal

Terminal text:

In the race for success,

speed is less important than stamina.

When you enter this Enigma room, there is a giant floating crystal that makes noises as you get close to it. When you walk into the crystal, it would make a glass shattering noise. A new crystal will spawn in a random location in the room. If you do not break it quickly enough, the Enigma resets. You have to continue shattering these crystals for approximately 15 minutes until you get a victory sound. After that, a long base64 looking string appears in the room.

![](https://buer.haus/wp-content/uploads/montecrypto/image24.png)

As with the other Enigmas that displayed strings in the game, the string was easily datamined from the Enigma blueprint files. We already extracted this string including two other red herrings. We didn’t figure out how to use the string until after we solved the Enigma ingame.

![](https://buer.haus/wp-content/uploads/montecrypto/image52.png)

This string turned out to be a password for one of the zips in the game files. When you extract the zip, you are given the following image:

![](https://buer.haus/wp-content/uploads/montecrypto/image65.png)

The solution to this Enigma turned out to be 2 tuhinga. We never figured out what “boili Frennez Al-Mar” meant. The only thing we noticed is that boili could have meant “boile, fish bait made of red herrings.” If this is the case, we never figured out what red herring it was referencing other than possibly the final zip that was never opened.

Solution: 2 tuhinga

## Enigma 4

Room Nickname: Invisible Stairs

When you enter this room there is a small platform up some stairs with an opening on it. Eventually you realize you can walk out and there are invisible stairs leading you upwards. There is music playing that gets louder and then you fall to the ground and the music ends. The trick to this room becomes evident quickly. As you walk up the invisible stairs, the music gets louder as you get closer to the edge. So all you have to do is move slowly and listen to the music.

That doesn’t sound too bad, until you realize there is a 60 minute time limit and it takes a little bit of time to run to the room. Thankfully, we used Cheatengine (and austin.dll) to disable the timer entirely.

Even after people spent hours trying to run through the room legitimately, they always seemed to fall. Eventually, people tried to just teleport to the top, but it didn’t work. It turned out there was a checkpoint system that made sure you hit all of them in the correct order. So people turned to teleporting every x,y,z of the room until the hit the top, but that didn’t work either.

With some effort, the community found out they could make the stairs visible. This next screenshot will you show our pain.

![](https://buer.haus/wp-content/uploads/montecrypto/image63.png)

Image credit: [http://twitch.tv/qberty1337](http://twitch.tv/qberty1337)

Notice the false paths? Notice the jumps? Probably the most evil puzzle ever made.

The community eventually powered through it and solved it (without the 60 minute timer active).

![](https://buer.haus/wp-content/uploads/montecrypto/image66.jpg)

Funny enough, this string was extracted probably a month prior to the solve. Like some of the other Enigmas, there were some strings in the uasset files. The BP\_En4Manager.uexp file contained multiple strings such as:

- Gimmeahug
- Doyouwanttoworkforus
- Jobwelldone
- Areyoutired?
- Rickandmortyforever.com

I’m sure other teams had realized earlier on that jobwelldone was a password for one of the three zips in the game asset files. We did not make the connection until after jobwelldone was posted as a solution.

This led to a new image:

![](https://buer.haus/wp-content/uploads/montecrypto/image6.png)

Giving us the solution 3-kohokohta for this Enigma.

Interestingly, the image retrieved from solving Enigma 3 fits perfectly inside the gray area of this solve image. Many attempts were made to manipulate the two images together using steganography software, methods like xor, adding byte values between the images etc, but nothing came of this. It’s either a coincidence, red herring, or some flavor that we never solved.

Solution: 3 kohokohta

## Enigma 5

Room Nickname: Lullaby / Fairy

The Lullaby room contained high piles of books and a cone light in the center of the room.

![](https://buer.haus/wp-content/uploads/montecrypto/image59.jpg)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

When you stand in the light, it plays audio for a bit until it finishes. After that you gain a flashlight and a little wisp begins to fly around the room. You have to track the wisp with the flashlight for around 30-45 minutes.

I had a video link on Twitch of someone completing this room but it has since been deleted.

After you successfully track the wisp long enough, it plays the success audio and another audio file plays in the background. This second audio file contains Spectrogram steganography with the solution words.

![](https://buer.haus/wp-content/uploads/montecrypto/image48.png)

Image credit: Trailbl4z3r from GameDiscord

Using a tool such as Sonic Visualiser or Audacity, you can find the Spectro fairly trivially. The hard part was trying to trace out the word because it is hard to see.

Solution: 2 ondiep

## Enigma 6

Room Nickname: Office

![](https://buer.haus/wp-content/uploads/montecrypto/image53.jpg)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

This Enigma was probably one of the more interesting ones that required effort outside of the game to solve. Our team had eyes on MonteCrypto prior to it launching so we were already looking for clues on their website and social media.

The MonteCrypto website is hosted on Github:

- [http://montecrypto-game.github.io/](http://montecrypto-game.github.io/)

So we started to investigate the repository on Github:

- [https://github.com/montecrypto-game/montecrypto-game.github.io](https://github.com/montecrypto-game/montecrypto-game.github.io)

Looking at the [commit history](https://github.com/montecrypto-game/montecrypto-game.github.io/commits/master) we see multiple changes to a file called 21.html. These changes that look like the following:

![](https://buer.haus/wp-content/uploads/montecrypto/image26.png)

We didn’t know what it meant prior to the game going live, but we already had it documented. By the time we reached the office Enigma in the game, the answer was pretty clear.

The terminal text read:

A very very long time ago, Rai had left me an important message...

I must have kept a note of it, but where?

In this commit on Github, we can see the answer:

[https://github.com/montecrypto-game/montecrypto-game.github.io/commit/3e64758479f49d273cd7b2e979a32e70378e9d59#diff-2c54dd4f6d3b8154f30f974cfd3446ef](https://github.com/montecrypto-game/montecrypto-game.github.io/commit/3e64758479f49d273cd7b2e979a32e70378e9d59%23diff-2c54dd4f6d3b8154f30f974cfd3446ef)

\+ <img date='a very very long time ago' title='confidential' clue='5 persamaan' height='100%' width='50%'/>

Solution: 5 persamaan

## Enigma 7

Room Nickname: Floor Pit

The Floor pit enigma was a room containing small pits that would show you a word when you fell into them. Without noclip/teleport, this meant you had to restart the game and run back to the room to collect all of the words.

The terminal text for this Enigma:

Even Luther Cary, my old friend, couldn't compete (and he held the record!).

Try it yourself.

But don't miss a turn.

Some of the pits had wooden planks over them which made it impossible to get the words out without noclip. We assumed that the answer was one with the planks on top of it.

Luther Cary was an olympian runner that held records for track and field athletics. We quickly noticed that if you were fast enough, one of the planks had no collision on it. It wasn’t until we got access to the blueprint disassembly that we figured out the answer.

![](https://buer.haus/wp-content/uploads/montecrypto/image57.jpg)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

Part of the pits disassembly code:

![](https://buer.haus/wp-content/uploads/montecrypto/image25.png)

This confirmed that if you reached the room within a certain amount of time, the sm\_plank game objects above one of the pits would lack collision. After that time limit, the planks would gain collision preventing you from falling into it (without noclip). Validating our theory and knowing we needed an 8, it gave us the solution we needed.

Solution: 8 perro

## Enigma 8

Room Nickname: Skull Room

This is one of the more interesting Enigmas in the MonteCrypto game. It did not take long for people to stumble into the Skull room as it’s fairly close to the lobby. This led the entire room being filled with message signs everywhere.

When their time come,

The dead will answer;

Letters, Number,

Letters & Numbers,

Entered without feedback.

At exactly 03:33:00 AM (system clock, so you could change it) for a brief second textures would appear on every surface of the room.

![](https://buer.haus/wp-content/uploads/montecrypto/image79.png)

Creepy, right?

Unlike some of the other Enigmas where you could rip strings directly from the uasset/uexp files, we had to pull these strings directly from the game memory.

Using the terminal text, you can guess that we had to input the string back into the game. Using a script, we send only the key inputs from the string on the ceiling (letters only) and floor (numbers only).

Our first attempt to run this script resulted in it opening up UI elements like the map and causing the player to move around the map, since we were pressing valid key inputs. As an extra added step that was likely unnecessary, we ended up changing our keybindings to F1-F12 keys to prevent them from interrupting the input. The “entered without feedback” part of the hint led us to believe this was necessary.

![](https://buer.haus/wp-content/uploads/montecrypto/image18.png)

Solution: 6 okpu

## Enigma 9

Room Nickname: Zelda Forest

Enigma 9 is a giant steel tower that you enter through a doorway. Inside the first room you have three doors in front of you and one door behind you. If you go through the door behind you, you leave the Enigma and everything resets. When you move through the other three doors, you find yourself in a room similar to the one you just came from. We nicknamed this the Zelda Forest after a similar puzzle in the Nintendo 64 Legend of Zelda: Ocarina of Time.

![](https://buer.haus/wp-content/uploads/montecrypto/image20.jpg)

Image credits: [https://wiki.gamedetectives.net/index.php?title=File:4\_Doors.jpg](https://wiki.gamedetectives.net/index.php?title=File:4_Doors.jpg%26filetimestamp=20180224013406%26)

We were able to solve this one a bit earlier than the public discords did. We discovered one of the blueprint files for en9 (BP\_En9Manager.uexp) contained the following string:

33111221221312121122231322333232112213233332212331131212332333311212222111222121323212121221122111322113212332112121131312211121233323131233222232323222321232333321

Using a text or hex editor you could discover it trivially:

![](https://buer.haus/wp-content/uploads/montecrypto/image47.png)

After assigning 1 to the left door, 2 to the middle door, and 3 to the right door, we followed this path start to finish until the last doorway played the victory sound. After that, each room lit up super bright and the ground textures changed.

![](https://buer.haus/wp-content/uploads/montecrypto/image58.png)

Through three of the doors, you could see that there were 3 different ground textures. If you went through one of the doors, the puzzle reset. You either had to take pictures from the doorway or use noclip to get a clear view of it.

These dots on the ground were braille that gave you the room solve when translated

This was a solve that had already been extracted within the first day of the game being live, but like some of the other Enigmas it had a few red herrings with it.

![](https://buer.haus/wp-content/uploads/montecrypto/image1.png)

Two of the braille images in the game data turned out to be red herrings.

- 1 - boutil - Red Herring
- 5 - jaojet - Red Herring
- 9 - ogles - Solve

We never figured out if there was something in the game that told you which direction to go allowing you to solve it using only in-game mechanics.

Solution: 9 ogles

## Enigma 10

Room Nickname: Library

As you enter this Enigma you go into a multi-level library with stairs leading down to a table and terminal at the bottom. The terminal text hints at what you need to do.

This manor isn't a safe place to be alone;

Paths unlock when people come together;

Only through shared efforts will you get closer

To shed the light on the unknown

Throughout the library there are empty plaques on all the walls similar to the one you saw in the lobby at the beginning of the game. The terminal text and these plaque hinted that the community needed to come together to solve this room.

An individual player can only have one active sign at any given time, that means we needed a bunch of players to put signs on all of the plaques until it triggered the next step.

![](https://buer.haus/wp-content/uploads/montecrypto/image40.jpg)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

Once the condition was met, it would play a victory sound as soon as all the signs loaded. Given that there were thousands of signs in the game at this point, this could take up to 30-40 minutes for whatever reason.

Here comes the fun part. This Enigma is actually broken and required a bit of datamining and hacking the game client to solve it. After the victory sound, nothing happens.

Looking through the game files you’ll notice there are references to horse sculptures that are nowhere to be found in the library.

![](https://buer.haus/wp-content/uploads/montecrypto/image49.png)

One of the members of our team happened to notice three horse statues were appearing near 0,0,0 xyz.

![](https://buer.haus/wp-content/uploads/montecrypto/image37.png)

You can see the three horses at the bottom right of this screenshot

![](https://buer.haus/wp-content/uploads/montecrypto/image46.png)

A close-up inspection of the horse statues using noclip

This led us to investigating the horse textures in the game assets.

![](https://buer.haus/wp-content/uploads/montecrypto/image27.png)

The problem is, there are three different textures (HorseSculpture, HorseSculpture1, HorseSculpture2) with three different solves on them. Like the other Enigmas, any dataminable answer had multiple red herrings with them.

In the game itself, you couldn’t actually see the word on any of the models. We were only able to see the word via UE Viewer. One theory is that the horse statues were meant to be on the table in the library and a light in there would expose the word. Either way, we were able to determine the solution based on the pi sequence order. We needed a 7.

Solution: 7 beunghar

## Enigma 11

Room Nickname: Raining / Temple

This is probably the only room that was originally intended to utilize cheating to solve as indicated by the enigma text.

Honesty is for the most part less profitable than dishonesty.

Using no-clip and walking through the wall, you would see a series of signs on the backside of the wall that show 50280.0.

![](https://buer.haus/wp-content/uploads/montecrypto/image38.png)

This was giving you a Z coordinate that you needed to get to cheating allowing your character to teleport upwards. Z-axis teleportation was the only type of teleportation allowed by the game that didn’t result in your character resetting back to the lobby.

![](https://buer.haus/wp-content/uploads/montecrypto/image17.png)

Once entering the rain temple you could walk onto the platform to make a series of 5 16x16 pixel grids appear, with one being located on a low pedestal above the other. Many ideas were tried here such as XORing the grids together, ignoring all but the changed pixels between grids, or trying to merge the grids into a valid QR or datamatrix. We even extracted the blinking light from the statue as binary to use the grids as an XOR mask on them to see if anything appeared.

The 16x16 pixel grid on the center pedestal was the only important grid in this room (T\_0 for reference). T\_1-4 were most likely put in the files as red herrings to force you to go to the temple and see which grid was important. We guessed that you decode the black/white as binary starting from the top left and going to the bottom right. Converting that binary to a string gives a result like this, where \\x## corresponds to a byte that falls outside the printable ASCII range:

10+1\[1>5\\x82>\\x80+2<1-1\]\\x853\\x82.\\x8511\\x943\\x8f\\x95\\x8e1

(Code to convert the T0 directly from image to a string, [http://archive.is/4olAw](http://archive.is/4olAw))

The appearance of +,-,\[,\],>,. strongly hints at the [brainfuck esoteric language](https://esolangs.org/wiki/Brainfuck). In this case there’s numbers before the brainfuck operators, which was a strong hint at [Run Length Encoded brainfuck](https://codegolf.stackexchange.com/questions/146911/rle-brainfuck-dialect) (ie. 10+ means print ++++++++++).

Now, the unprintable bytes need to be resolved. Note that the string is 32 bytes long. Also note that the unprintable bytes are all values between \\x80 and \\x80+32. That sounds like a text compression algorithm already. So, pretend the string starts at index \\x80 -- the unprintable bytes are now an index into that string. To resolve them, you take the byte at string\[index\] and string\[index+1\] -- then replace the unprintable byte with those two characters. (ie. \\x82 tells you to use the third character from the string, in this case a + and combine it with the next character that appears after it, which was a 1, to get +1). Therefore you get the encoding for unprintable characters below:

\\x80 = 10

\\x82 = +1

\\x85 = 1>

\\x8E = 1-

\\x8F = -1

\\x94 = \\x82. = +1. ← Look! You had to resolve this one twice.

\\x95 = .\\x85 = .1 ← \\x85 is a “following” byte, so it is resolved to 1 char

This gives the final string of:

10+1\[1>5+1>10+2<1-1\]1>3+1.1>11+1.3-1.11-1.

Which expands to the final brainfuck program:

++++++++++\[>+++++>++++++++++<<-\]+++.>+++++++++++.---.-----------.

You can run that program and get the final word, but below we’ll try to explain it:

\+\+\+\+\+\+\+\+\+\+ set cell #0 to 10

\[\
\
>\+\+\+\+\+ add 5 to cell #1\
\
>\+\+\+\+\+\+\+\+\+\+ add 10 to cell #2\
\
<<\- Decrement the loop counter in Cell #0\
\
\] Loop till cell #0 is zero; number of iterations is 10

At this point we have:

```
Cell No :        0   1   2
Contents:        0   50  100
Pointer :        ^
```

>+++. add 3 to cell #1 (=53) and output char '5'

>+++++++++++. add 11 to cell #2 (=111) and output char 'o'

---. subtract 3 from cell #2 (=108) and output char 'l'

-----------. subtract 11 from cell #2 (=97) and output char 'a'

![](https://buer.haus/wp-content/uploads/montecrypto/image44.png)

Solution: 5 ola

## Enigma 12

Room Nickname: Goblin Statue

If you followed the MonteCrypto twitter account ([@MontecryptoGame](https://twitter.com/MontecryptoGame)) you noticed they tweeted a bunch of pictures of #themayor. Each of the pictures in these tweets contained a word at the bottom right of them.

As you get to the Goblin Statue / Mayor Room, you find a statue sitting on a table. When you click on them, it opens your browser to one of those tweets randomly.

The terminal text hints at which one you need to find:

Finding the good one amongst the liars,

To be left alone that's what he desires;

The final answer is hidden in plain sight,

With the help of the bird it should be alright.

There were a lot of good theories on this which reduced it down to two possible answers. We disregarded these because we knew that once we had all of the words that we could figure out which one it was based on the number we had left in the pi sequence order.

2-reproduckja - [https://twitter.com/MontecryptoGame/status/964464404598272000](https://twitter.com/MontecryptoGame/status/964464404598272000)

- "I would if I could, I remember saying. And then I sold them all."

0-jaojenn - [https://twitter.com/MontecryptoGame/status/964465837372354560](https://twitter.com/MontecryptoGame/status/964465837372354560)

- “"Leave me alone now!"”

The answer turned out to be: 2-reproduckja

![](https://buer.haus/wp-content/uploads/montecrypto/image29.jpg)

Solution: 2 reproduckja

## Enigma 13

Room Nickname: Frog Pond / Jumping

This was one of the first Enigmas in the game that was fairly trivial. The Frog Pond enigma could be considered the “tutorial” enigma. All you had to do was jump across a bunch of pillars to get a solve string at the end.

Terminal text:

Like frogs from nenuphars,

jump from rock to rock.

If fall you do, find the stairs and start over.

Soon enough the secret will be yours.

![](https://buer.haus/wp-content/uploads/montecrypto/image22.png)

Solution: 0 construct

## Enigma 14

Room Nickname: Server Room

This was one of the first rooms we encountered before using no-clip and flying/teleporting. There are 8 computers in this room which produce audio when clicking on it. You had to click on them in the correct order - I UPLOADED MYSELF IN THE MAZE’S COMPUTER THE CIRCUITS ARE MY VEINS AND THE POWER IS MY BLOOD - to get the solution.

![](https://buer.haus/wp-content/uploads/montecrypto/image14.png)

On a side note: Much later on we realized that the asset which handles the blinking on the computers in this room is reused in eenigma 11 on the blinking statue, so we ruled it out as a red herring.

Solution: 9 istisna

## Enigma 15

Room Nickname: White Lights

This is a really interesting puzzle that was solved by the GameDetective community before we even looked at it. It involved playing a small riddle game using game save files on your computer. I recommend reading the detailed write-up on the wiki:

[https://wiki.gamedetectives.net/index.php?title=MonteCrypto\_-\_The\_Bitcoin\_Enigma#Robot](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma%23Robot)

Solution: 5 velte

## Enigma 16

Room Nickname: Achievement

The solve for this enigma is printed on a hidden achievement icon that is obtained through doing a specific action in the game. The game came with Steam achievements but there are a few that are secret. Using a Steam achievement unlocker or just viewing it on some of the Steam achievement/stat sites, you quickly figure it out: That said, even though this Enigma is easily solvable using an out-of game method, we pretty quickly on the first day of the game’s release found how to unlock it legitimately.

When you enter this enigma room you’re presented with the text:

Just like platform 9 3/4,

Towards the door go forth;

Physical illusions,

everywhere in this maze;

Don't let yourself be fooled,

you will be amazed.

This is a reference to the Harry Potter series where at King’s Cross station in London Hogwarts Express passengers are able to run through walls to reach the hidden platform. We needed to do just that. Running straight through the wall down the corridor to the right of the console allows you to pass through it and unlock the hidden achievement with the solve to this enigma.

![](https://buer.haus/wp-content/uploads/montecrypto/image74.png)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

![](https://buer.haus/wp-content/uploads/montecrypto/image42.png)

Source: [https://steamdb.info/app/768750/stats/](https://steamdb.info/app/768750/stats/)

Solution: 8 optree

## Enigma 17

Room Nickname: QR Code

This is another one of the early Enigmas that you reach from the lobby. As you enter the room, you come across a terminal and a door.

Terminal text

Transcendental yet widely used,

On March 14th it gets amused.

Add an E an you can eat it

Keep it in mind, later you will need it.

Clicking on the door, it asks you for the solution to the riddle which is “Pi.”

- March 14th = pi day (3/14)
- Add an e and you can eat it (pie)
- Keep it in mind, later you will need it (the pi digit sequence for the wallet order).

When you get through the door, you see a QR code giving you the solution.

![](https://buer.haus/wp-content/uploads/montecrypto/image34.jpg)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

Solution: 3 prevoditi

## Enigma 18

Room Nickname: Blue Room

The enigma text terminal when approaching this room reads:

Find your path amongst the invisible forces.

Once the red is reached, the goal is almost accomplished.

One that would need additional clues for this one should reconsider actually winning the prize.

Inside the room ahead is an area that is completely rendered in blue textures and thusly very difficult to distinguish what is a wall vs ground, etc.. when moving around it in 3D space. On the opposite side of the room is a red platform, and between you and said platform is an invisible bridge and underneath it a pit that leads back to the start of the room.

Carefully traversing and falling lots of down into the pit, we were able to reach the red platform.

Upon reaching the platform a long deep sound plays. After some manipulation of this sound in Audacity we realized that it is an extremely slowed down audio of someone speaking the answer to the enigma.

Here’s a video of the puzzle:

- [https://streamable.com/l47i5](https://streamable.com/l47i5)

Since we likely sped up audio to not exactly its original form, it wasn’t completely clear what was being said - There was lots of debate over whether the audio here was saying NODO, NOVO, or NOTO. After some more Audacity-fu we were able to get a version that was leaning 80% towards NODO, but even then since we weren’t sure, when we reached the final step of entering our answers into the BTC transaction, we had to consider NOVO or NOTO as possible replacements for this solve.

Turns out nodo was correct.

Solution: 0 nodo

## Enigma 19

Room Nickname: Candle Cave / Spirits

This room evaded us for a very long time. And it turns out that it’s because it’s completely and utterly broken.

Terminal text:

Spirited machines ought to exist

Those who are correctly equipped

Can follow them as they communicate

At last are rewarded those who wait

Entering this room does not trigger anything to happen, nor does moving around it. For a while we were concerned that not getting here legitimately was the problem, but doing so many times did not result in anything new either.

Delving into the game data for this enigma we discovered a strings in \\CryptoChallenge\\Content\\CryptoChallenge\\Enigmas\\Logic\\En19\\BP\_En19Manager.uexp that showed the text PLEASEBEQUIETANDTAKEAREST and ASCII art of the text 0 colle.

![](https://buer.haus/wp-content/uploads/montecrypto/image10.png)

![](https://buer.haus/wp-content/uploads/montecrypto/image31.png)

Though we found this ascii art text in the game data, as with all of the puzzles we did not know if it was a red herring or the actual solution, so we set out to figure out how to actually solve the room in the game.

We had two conclusions going in to the room based on the hint given on the console and from data mining the files:

1. You’re going to need some “special equipment” to solve this one
2. There’s going to be some waiting involved.

Since the room appears to have a cube-shaped forcefield around it, the working theory for a long time was you needed to use a VR rig. We’d already seem a puzzle that required a controlled, and we didn’t think it was much of a stretch that other hardware might be required as well.

By default, the game doesn’t boot up properly when either an Oculus or Vive headset is enabled in steam, but after some coercion with command line arguments, we got it to work. The game doesn’t really support this, and making our way legitimately back to the cave was difficult since the UI for opening the trivia doors doesn't work properly with the headset on. Once we arrived there though, it didn’t seem to trigger anything or make any difference. Finally, after laying down on the floor to “take a rest” with the VR gear on produced no changes, we gave up on that idea.

But, we knew that vibration was involved somehow. The same vibractor references in the game files that we had seen in Enigma 20 were in this blueprint as well. So we dropped the Vive and picked up the controller again.

The breakthrough with this puzzle was when we were able to use a tool written by Austin to display every active entity that the game currently has spawned.

Using this tool, we could see that after entering the candle cave, there was one en19\_Vibractor active on the map. The problem? Its location was not only outside of the confines of the cave, but outside the entire maze.

![](https://buer.haus/wp-content/uploads/montecrypto/image80.png)

![](https://buer.haus/wp-content/uploads/montecrypto/image11.png)

Using Austin’s tool to teleport to this location (making sure we have Noclip turned on also so that we don’t fall to our death and reset) we hear the same glass smashing sound that we heard when solving Enigma 3.

![](https://buer.haus/wp-content/uploads/montecrypto/image78.png)

![](https://buer.haus/wp-content/uploads/montecrypto/image33.png)

At this point in the blackness of space, you see nothing, but repeating the process above we found that another vibractor had spawned at another unreachable location:

![](https://buer.haus/wp-content/uploads/montecrypto/image45.png)

This time it’s named ‘1’ instead of ‘0’ so we know we’re on to something. After repeating this 25 times the location resets back to 0. But we hadn’t figured anything else out. That’s where a controller came in to the picture.

motive drew the short straw since he was the only one with a controller.

![](https://buer.haus/wp-content/uploads/montecrypto/image56.png)

Repeating the process above 25 times with a controller plugged in causes it to vibrate in morse code with the following message: .--./.-.././.-/..././-..././--.-/..-/.././-/.-/-./-../-/.-/-.-/./.-/.-././.../-

Which translates to PLEASEBEQUIETANDTAKEAREST

At this point, the controller is vibrating constantly.

Being careful to not cross over the cube around the confines of the cave (making sure the teleport back into the center of it). We did just that. Unplugged microphone from the system in case being quiet was actually necessary, and did not move an inch. After 10 minutes, the controller slowly stops vibrating and the success sound plays. Displaying the message floating in the room:

![](https://buer.haus/wp-content/uploads/montecrypto/image36.png)

Yes, that’s a really long single line string containing ASCII art.

This confirmed the theory that the ASCII art found previously in the game files was the real solution.

Solution: 0 colle

## Enigma 20

Room Nickname: Who Am I?

When you get to this Enigma, you see a single door and the Enigma terminal with some text on it.

![](https://buer.haus/wp-content/uploads/montecrypto/image50.png)

When you try to open the door, it prompts you with “Who am I?”

The answer to this door may have actually been quite difficult if the answer wasn’t easily grabbed from the WB\_Question20.uasset file.

![](https://buer.haus/wp-content/uploads/montecrypto/image41.png)

There were references to SteamId in this uasset file which was not found in any other uasset/blueprint file data that we had at the time. Grabbing the SteamID 64 from our account and inputting it as the answer unlocked the door.

Going into the room, there are a couple of game objects but nothing interesting. It wasn’t until going through the game files a bit more and noticing Enigma 20 had a file called BP\_Vib.uexp containing references to Unreal controller functions such as EDynamicForceFeedbackAction. At this point we realized that controller vibration was likely at play in this Enigma.

Coming back and opening the door again with a controller we noticed the controller vibrated a message. We eventually were able to extract it out with an unconventional method - since it vibrated too quickly to jot down the morse code in real time, motive used his microphone to record the sound of his controller vibrating which we then played back slower so that we could transcribe the message. The vibration turned out to be morse code that we had already extracted from the BP\_Vib.uexp file earlier on.

![](https://buer.haus/wp-content/uploads/montecrypto/image12.png)

.\-\-\-\- / ..\-. \-\-\- .\-. \-.\-. . / .\- \-. \-.. / .... . .\- .\-. \- / .\- \-... \-\-\- ...\- . / .\- .\-.. .\-.. / . .\-.. ... . / \-... .\-. .. \-. \-\-. / .\-\-. . .\- \-.\-. . / .\- \-. \-.. / .\-.. \-\-\- ...\- . / .\-. . .\- \-.. / .\-\- .... \-\-\- / \-.\-\- \-\-\- ..\- / .\- .\-. . / .. \-. / . ...\- . .\-. \-.\-\- / .. \-. ... \- .\- \-. \- / \-.\- \-. \-\-\- .\-\- / \- .... \-.\-\- ... . .\-.. ..\-. / \-\-\- .\-. / \-.. .. . / \- .\-. \-.\-\- .. -. --.

This decodes into:

1 FORCE AND HEART ABOVE ALL ELSE BRING PEACE AND LOVE READ WHO YOU ARE IN EVERY INSTANT KNOW THYSELF OR DIE TRYING

This was odd for two reasons:

- Knowing the pi sequence order and having solved a good portion of the Enigmas at this point, we had not found a solve with a 1 in it yet. We knew we needed at least one 1-\[word\] if our pi sequence order theory was right. (Weak guess: 1-FORCE)
- None of the other Enigma solves had lengthy messages like this which really weakened our confidence that 1-FORCE was the answer.

The MonteCrypto team later tweeted an odd message:

[https://twitter.com/MontecryptoGame/status/967431857028648961](https://twitter.com/MontecryptoGame/status/967431857028648961)

![](https://buer.haus/wp-content/uploads/montecrypto/image9.png)

The binary translated into “mutu kokarin” which is Hausuan for die trying.This was a direct reference to the morse output in this Enigma. The numbers below were in a list format so we figured we needed to make a list of some sort.

At this point we couldn’t make sense of it and moved on for awhile. It wasn’t until a month or so later while discussing the tweet in one of the MonteCrypto Discord channels did we realize what the numbers meant.

Credits to Tsalnor for the late night discussion that led to this solve with his breakthrough.

Each line with a number was telling you the length of which to split the string obtained from the morse output.

1

15 FORCE AND HEART

14 ABOVE ALL ELSE

20 BRING PEACE AND LOVE

16 READ WHO YOU ARE

16 IN EVERY INSTANT

12 KNOW THYSELF

13 OR DIE TRYING

Reading the first letter of each line gives you: 1FABRIKO.

To shine some light on Tsalnor, this mad man solved it initially without even using the tweet. We were just discussing how we would split each line up and he did it perfectly. This is how it felt to solve Enigmas in this game:

![](https://buer.haus/wp-content/uploads/montecrypto/image71.png)

Solution: 1 fabriko

## Enigma 21

Room Nickname: Vault

The Enigma for this Room was:

Everyday, the same routine...

Accuracy is what matters at the end of the day.

This was one of the biggest rooms, and ended up being solved by trying the same method used in the Skull room. You had to be in the room at the exact time of 03:33 am and one of the doors would open. On the ground there would be a set of books. At first the books do not look like anything. After you return at the same time the next few days, more books are added on the ground. Eventually you could read the next word “3siya.”

![](https://buer.haus/wp-content/uploads/montecrypto/image69.png)

Solution: 3 siya

## Enigma 22

Room Nickname: Binary Window

This room was a relatively straightforward room to solve. The enigma states.

When back against the wall,

What seems like an obstacle,

Could very well be passable.

One of the hallways next to this terminal appears to be a deadend. There were some hidden doorways in the game that allowed you to run through the walls. This one however had collision and you could not run through it. You had to heed the tips of the terminal and move backwards to get through it.

Inside the room if you peer through the window you can see a string of binary (you had to do some guessing for the digits blocked by the window pane). But you should get: 00110100 01110101 01101011 01110101 01101110 01100111 01110001 01110101 01100010 01110101 01111010 01100001 01101110 01100001. Which translates to 4ukungqubuzana.

![](https://buer.haus/wp-content/uploads/montecrypto/image21.png)

Solution: 4 ukungqubuzana

## Enigma 23

Room Nickname: Painter

The Painter room was modeled after the Van Gogh painting [Bedroom in Arles](https://en.wikipedia.org/wiki/Bedroom_in_Arles).

![](https://buer.haus/wp-content/uploads/montecrypto/image30.jpg)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

The terminal text read as the following:

Several suns are shining,

TEN of which are dying.

As our universe continues to expand,

You are here trying to understand.

Sent to us from an unknown entity,

Terrorising our friends and families

In TEN MINUTES he burnt our symphony;

La-Mar, the one and only,

Lurking in the sky and our city.

The first letter in each line spells out “STAY STILL.” Given the TEN MINUTES in caps, it was clear the solve was to stand still and not move for 10 minutes. Doing so resulted in the solve being painted across the ceiling and wall.

![](https://buer.haus/wp-content/uploads/montecrypto/image15.jpg)

Image credits: [GameDetective Wiki](https://wiki.gamedetectives.net/index.php?title=MonteCrypto_-_The_Bitcoin_Enigma)

Solution: 4 bakar

## Enigma 24

Room Nickname: Sun Cave

Enigma 24 is a small cave-like room with a god-ray sun shaft beaming down onto the enigma’s terminal.

![](https://buer.haus/wp-content/uploads/montecrypto/image62.png)

![](https://buer.haus/wp-content/uploads/montecrypto/image51.png)

This was one that we solved some time before the public discord channels figured out what was going on and another example of how it was nerve racking and frustrating to watch them catch up as we struggled on the final two puzzles in the rain room and forest/outside.

The text on the console reads:

I remember it was a code...

Yes that’s it: “lake waves”

Was it in German? Or Chinese?

Not sure, I can’t seem to remember.

From this clue we knew that we needed to translate the “lake waves” text into some language that made more sense to the puzzle that likely wasn’t German or Chinese.

We made the connection pretty quickly after someone called out that “waves” in Japanese is “nami” and that instantly connected us with the word “code” in the clue to the Konami Code.

![](https://buer.haus/wp-content/uploads/montecrypto/image4.png)

We also almost simultaneously noticed the Konami code listed in the bp files ![](https://buer.haus/wp-content/uploads/montecrypto/image76.png)

![](https://buer.haus/wp-content/uploads/montecrypto/image39.png)

Entering into the room and typing out the Konami code using the arrow keys (udlr) and ‘b’ and ‘a’ on the keyboard played the success sound and triggered the message:

![](https://buer.haus/wp-content/uploads/montecrypto/image72.png)

Solution: 9 gull

# Final Solve Steps / MonteCrypto Solution

Having the pi sequence order, number-word solutions, and wallet files. We ran Hashcat with all of the possible permutations until we got a hit. Using that, we were able to use the Bitcoin Core to extract the Bitcoin prize out of the wallet.

Proof:

[https://live.blockcypher.com/btc/tx/b02f1aea315f677d98427ca0bd8c48e3cc5a7225a72436b1dfc2c163f69e02f0/](https://live.blockcypher.com/btc/tx/b02f1aea315f677d98427ca0bd8c48e3cc5a7225a72436b1dfc2c163f69e02f0/)

![](https://buer.haus/wp-content/uploads/montecrypto/image75.png)

The final password and solve for MonteCrypto:

construct istisna prevoditi optree bakar ukungqubuzana okpu colle gull velte mzuzwana nodo persamaan perro tuhinga reprodukcja siya fabriko beunghar ondiep ola kohokohta pagluwa ogles

See [Appendix A - Wallet bruting](https://buer.haus/2018/04/24/montecrypto-argss-write-up/#h.ucajvenfkjpz)for how we bruteforced the final solution from all the possible permutations from the above list.

# ADDITIONAL FLAVOR PUZZLES

Though we did not know this until much later in the solving process after lots of time had been sunk into them, the following puzzles and findings in the maze appear to be lore / flavor only and are note unnecessary for solving the main enigmas.

## Compasses and Skulls

The game included small compasses you could click on that would play audio files. There were also shrines that had skulls on them that would play lore audio when you clicked them. Both of these turned out to be entirely for achievements, game lore, or ciphered troll messages that did not appear to be related to the puzzles for the wallet. We’re not going to bother writing up information on them due to this.

## Appendix A - Wallet bruting

### Setup

john1.8J1-bc1bbc96f (john-jumbo bleeding) and 3 previous versions were used to convert wallet.dat, the zip files, and the dmg file to a brutable hash format for both John The Ripper (JTR) and hashcat. These are bitcoin2john.py, zip2john.exe, and dmg2john.exe.

### Generating wallet passwords

We weren’t sure on a few words. We also weren’t sure about the final password being the order of the enigmas. Here’s the script we wrote to generate those permutations:

[http://archive.is/o7mk9](http://archive.is/o7mk9)

Here’s what the final solve looked like:

![](https://buer.haus/wp-content/uploads/montecrypto/image7.png)

![](https://buer.haus/wp-content/uploads/montecrypto/image2.png)![](https://buer.haus/wp-content/uploads/montecrypto/image32.png)

### Stats

We ran the generator to brute a bunch of ideas that didn’t pan out for enigma words. We also ran JTR against the zip files with multiple wordlists + dive rulesets. At one point we ran strings against all extracted assets and passed that as a wordlist (this solves the first two zips).

Discussed below, we ran our B&K attack on iteratively lower numbers of known plaintext on 100 cores for 48 hours. Only the three keys were recovered.

## Appendix B - Biham and Kocher’s Known Plaintext Attack

Enigma 3 and 4 produced passwords to two zip files in MonteCrypto. Having only one challenge left (Enigma 2), we had one zip without a password as well. This is “dexterandalmar.zip,” it contained a file named “important.jpg”. By viewing the file headers, we could identify that it was made using p7zip-full on a unix distro. frVersion was 0x314, but the zip format does a bitwise and of this value with 0xFF to determine the proper version of 0x14. So after [googling around](https://sourceforge.net/p/sevenzip/bugs/1019/) for the number, it’s apparently the bitwise or of 0x14 and 0x300 -- 0x300 indicating it’s from the unix distro of 7zip. Who would’ve thought.

![](https://buer.haus/wp-content/uploads/montecrypto/image55.png)

[Biham and Kocher’s Known Plaintext attack](http://uvalight.net/~delaat/rp/2014-2015/p57/report.pdf)is the first thing that comes to mind when seeing pkzip-encrypted files. The idea is simple -- if you know 13 bytes of the original file before encryption, you can apply this attack to brute force the 12 byte encryption key. How many bytes of the original file do we know? Well, we collected every JPEG we could find associated with montecrypto. Here’s what the header bytes of some of them look like:

![](https://buer.haus/wp-content/uploads/montecrypto/image8.png)

You can immediately see there is a “JFIF” header, followed by an “Exif” header. Looking at all of the JFIF headers from JPEGs related to MonteCrypto, the first 21 bytes had only 3 variations. So we probably know 21 bytes of the original file, right?

Not quite.

The “plaintext” or original file here is compressed before it is encrypted with PKZIP. So those 21 bytes represent a smaller number of bytes before encryption. You might think -- oh, well just try to zip those bytes without a password! That could get you the bytes before encryption. However, 7zip and friends have an optimization to prevent “compressing” files that are too small to be effectively compressed by the DEFLATE algorithm. It won’t even attempt to compress the data.

Your options are now:

- Write your own DEFLATE implementation.
- Patch that optimization out and recompile.

- This was a pain and a waste of time.

- Find a DEFLATE library that will actually compress the data.

- Python ended up doing it with some coercion

This is the part where there’s more bad news. DEFLATE compressed data is different depending on the bytes that follow. We don’t know what bytes could follow our 21 bytes. So, if we just append some null bytes…. Python will give us something that looks correct.

>>\> import zlib

>>\> with open("bytes.bin","r") as fh: dat = fh.read(); do = zlib.compressobj(6, zlib.DEFLATED, -15); d = do.compress(dat+”\\x00”\*30);

>>\> print(repr(dat))

We actually notice several more possible variations of JPEG header (such as JPEGs that start with EXIF before JFIF). So we are down to a few possibilities:

03/13/2018 04:58 21 21bytes\_a\_compressed

03/13/2018 04:58 PM 21 21bytes\_c\_compressed

03/13/2018 04:59 PM 21 21bytes\_e\_compressed

03/13/2018 04:58 PM 35 exif\_40\_bytes\_compressed

03/13/2018 05:01 PM 46 exif\_64\_bytes\_presskitsandgithub\_compressed

03/13/2018 04:49 PM 14 thirteen\_bytes\_b\_compressed

03/13/2018 04:48 PM 14 thirteen\_bytes\_compressed

03/14/2018 10:26 PM 13 twelve\_compressed

8 File(s) 185 bytes

So, we have our compressed “plaintext” bytes! Now we can use a pre-written tool such as [bkcrack](https://github.com/kimci86/bkcrack) or [yazc](https://github.com/mferland/libzc/tree/master/yazc). These tools implement the B&K attack to reduce the space of possible encryption keys. They then attempt each, and see if they match up to the known plaintext. Plug everything in, bkcrack will quickly produce a key:

\[Tue Mar 13 18:29:07 DST 2018\] Starting /compressed\_testcases/21bytes\_e\_compressed

Generated 4194304 Z values.

\[18:29:07\] Z reduction using 9 extra bytes of known plaintext

100.0 % (9 / 9)

712488 values remaining.

\[18:29:08\] Attack on 712488 Z values at index 11

63.8 % (454229 / 712488)

\[18:42:34\] Keys

e91edb7c 6272c283 70857046

That’s a valid decryption key! We use bkcrack to dump the decrypted contents, which we then need to monkey-patch into the original 7zip to coerce it to decompress. However, trying it with that key will quickly show you the problem, when DEFLATE fails:

$ ./bkcrack -c important.jpg -C ./dexterandalmar.zip -k e055bf07 30532d26 97eaa917 -d compressed\_important\_2

\[22:14:31\] Keys

e055bf07 30532d26 97eaa917

Wrote deciphered text.

$ 7z e /mnt/e/fixed3.zip; ls -lhH important.jpg; xxd important.jpg

7-Zip \[64\] 9.20 Copyright (c) 1999-2010 Igor Pavlov 2010-11-18

p7zip Version 9.20 (locale=en\_US.UTF-8,Utf16=on,HugeFiles=on,12 CPUs)

Processing archive: /mnt/e/fixed3.zip

Extracting important.jpg Data Error

Sub items Errors: 1

-rw-rw-rw- 1 a a 48 Feb 4 19:55 important.jpg

00000000: ffd8 ffe0 0010 4a46 4946 0026 4f1b 4898 ......JFIF.&O.H.

00000010: 4898 4898 4898 4898 4898 4898 4898 4898 H.H.H.H.H.H.H.H.

00000020: 4898 4898 4898 4898 4898 4898 2409 8ed2 H.H.H.H.H.H.$...

That’s all the data it could dump. It doesn’t look like the correct bytes to follow a JFIF header. That’s because the decryption key was only valid for the first X bytes of plaintext we passed bkcrack.

So there can be more than one key that decrypts to a tiny portion of known plaintext. We modified bkcrack to not stop on the first key found, and we modified it to “work” on zip files smaller than 13 bytes (the keyspace is just much, much larger with more false positives). We pointed 100 cores at the problem and came up with these 3 keys:

e91edb7c 6272c283 70857046

e055bf07 30532d26 97eaa917

b9712087 33594506 a3b8ed2

None of which decrypt the entire DEFLATE-compressed JPEG correctly. Sad end 😭

## Appendix C - Disassembling UE4 Blueprints

It’s [literally done for you](https://github.com/EpicGames/UnrealEngine/blob/4.18/Engine/Source/Editor/UnrealEd/Private/ScriptDisassembler.cpp) (link requires UE4 source code access or it’ll say 404 -- request access on UE’s site). You can iterate over a global array of UObjects, check if they’re a UStruct, and then pass the disassembler their script pointer. Here’s an in-memory screenshot of what that array looks like:

![](https://buer.haus/wp-content/uploads/montecrypto/image5.png)

A pointer to the global objects array can be found by searching for this pattern in the game in IDA Pro: 48 8D 05 ?? ?? ?? ?? 48 89 01 33 C9 84 D2 41 8B 40 08 49 89 48 10 0F 45 05 ?? ?? ?? ?? FF C0 49 89 48 10 41 89 40 08

UStruct is the superclass that contains the pointer to blueprint bytecode as a TArray<uint8> -- which is effectively a byte array:

[https://github.com/EpicGames/UnrealEngine/blob/4.18/Engine/Source/Runtime/CoreUObject/Public/UObject/Class.h#L236](https://github.com/EpicGames/UnrealEngine/blob/4.18/Engine/Source/Runtime/CoreUObject/Public/UObject/Class.h%23L236)

* * *

## Appendix D - important.jpg

![](https://buer.haus/wp-content/uploads/montecrypto/image54.jpg)

## Appendix E - Our Thoughts on Hacking the Client

For some time after the game’s release our group was torn - should we hack the client to bend it to our will for the sake of solving and getting around the maze more quickly - or is that immoral and breaks the spirit of fair competition.

Just a few days after release though we realized the following:

- The game literally has an achievement that you can only get via falling through the world, something you could never do without noclip or teleporting
- The game has a wall that it explicitly encourages you to teleport or noclip through
- The rain room. The first half of the solve for this room is to teleport up to the listed value on the z axis.

Once we saw all three of these existed we felt like the developers of the game not only expected players to hack the client, but they required it to actually solve the full gambit of puzzles.

From that point forward, the only way to be on the same playing field as our competition, let alone win, was to embrace that hacking the client was an expected part of the race.