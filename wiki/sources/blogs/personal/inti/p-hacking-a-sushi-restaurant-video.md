---
source: inti
source_url: https://inti.io/p/hacking-a-sushi-restaurant-video
title: "Hacking a sushi restaurant (video below)"
description: "It turned out not to be the romantic candlelit dinner my wife had hoped for."
---

# Hacking a sushi restaurant (video below)

### It turned out not to be the romantic candlelit dinner my wife had hoped for.

Time for a quick update. I’m in the middle of a research project that’s taking a bit longer to finish and write up, but in the meantime, I figured I’d share a random hacking moment: hacking a sushi restaurant. Yep. There’s a video below.

A few months ago, my wife and I were traveling through Germany and ended up at this all-you-can-eat sushi place. The concept was simple: you get a tablet, order as many plates as you want within your timeslot, and eat.

The moment the waitress handed me that tablet, my wife sighed. She knew exactly where this was going. So much for a peaceful, romantic dinner.

I spent the next 30 minutes poking around to see if I could extend our timeslot—instead of, you know… actually eating.

Getting out of the app’s kiosk mode was way too easy. I just swiped down on the clock, opened the control panel, and tapped “Devices” to jump straight into the Android settings. First thing I tried was changing the system clock, hoping it’d mess with the countdown timer. Nope. Didn’t work.

Then I checked out the file browser. To my surprise, the app’s config file was just… there. I opened it in the browser and realized the app was basically just a web app running locally. Hit the login screen, opened up the browser dev tools, and there it was:

The admin password—**8888**—hardcoded right into the page.

Anyone with half a clue could’ve found it. Once logged in, I had full control—clearing tables, wiping bills, adjusting time slots… the works.

Of course, I logged back out. I’m still an ethical hacker at the end of the day.

I showed the waitress, but she just shrugged and said, *“Our customers aren’t that smart.”* Cool. Still shot the restaurant a message afterwards, but surprise: no reply. Been about 3 months now.

The best part? I barely ate. Spent the whole time hacking instead of stuffing my face with sushi. Ended up booking another dinner the next night just to make up for it.

Anyway—video’s below.