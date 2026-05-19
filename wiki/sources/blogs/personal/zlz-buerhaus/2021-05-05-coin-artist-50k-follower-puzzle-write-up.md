---
source: zlz-buerhaus
source_url: https://buer.haus/2021/05/05/coin_artist-50k-follower-puzzle-write-up/
title: "coin_artist 50k Follower Puzzle – Write-up | ziot"
---

[< Back](https://buer.haus/)

[![](http://buer.haus/wp-content/uploads/2021/05/logo-1024x357.png)](http://buer.haus/wp-content/uploads/2021/05/logo.png)

The infamous crypto puzzle artist [coin\_artist](https://twitter.com/coin_artist) just launched a new NFT airdrop for hitting 50,000 followers on Twitter. As with all coin\_artist related announcements and products, we immediately dusted off the magnifying glass and started to seek for a puzzle. We quickly saw that [she tweeted #1347](https://twitter.com/coin_artist/status/1389611450268721167?s=19) which is her bat signal that there is a puzzle to be found. It did not take long for us to find the trailhead!

**Solvers:**

- [ziot (@bbuerhaus)](https://twitter.com/bbuerhaus)
- [LeFevre (@\_LeFevre\_)](https://twitter.com/_LeFevre_)
- [mattm (@mattmcquaig)](https://twitter.com/mattmcquaig)

**The NFT Tweet:**

Twitter Embed

> I present the SLICKEST NFT airdrop to date!!! In collaboration with [@LinkdropHQ](https://twitter.com/LinkdropHQ?ref_src=twsrc%5Etfw) on [@0xPolygon](https://twitter.com/0xPolygon?ref_src=twsrc%5Etfw), my first 50K followers can now claim a special NFT and some MATIC for FREE!!
>
> Qualifying followers can claim their custom NFT here: [https://t.co/wd3ifbNUKM](https://t.co/wd3ifbNUKM) [#linkdrop](https://twitter.com/hashtag/linkdrop?src=hash&ref_src=twsrc%5Etfw)
>
> CLAIM DEMO: [pic.twitter.com/PYgMLv2Lqt](https://t.co/PYgMLv2Lqt)
>
> — COIN ARTIST (@coin\_artist) [May 4, 2021](https://twitter.com/coin_artist/status/1389611442677063681?ref_src=twsrc%5Etfw)

**NFT**

The NFT drop is part of a collection called [Coin Artist 50K collection](https://opensea.io/collection/coin-artist-50k) on OpenSea. The description for the NFT has a link to a mosaic image ( [mosaically.com](https://mosaically.com/photomosaic/fd40c771-f976-4bf7-96b8-80379da82333)) that you can scroll to view all of the 50k followers.

If you scroll down the page, there is an option for showing Mosaic stats. The interesting thing we noticed is the details show 50,001 total images in the mosaic. Knowing this is only supposed to be 50K we needed to find the extra image.

When you click on an image in the mosaic, you can see that it is Twitter follower id followed by their Twitter screen name. With that, we knew we could search for "50001" and find the extra profile.

![](http://buer.haus/wp-content/uploads/2021/05/2.png)

In the image we discovered an Ethereum address and the image name that is hex encoded. The image name [“5072697a6557616c6c6574” when decoded is “PrizeWallet”](https://gchq.github.io/CyberChef/#recipe=From_Hex('Auto')&input=NTA3MjY5N2E2NTU3NjE2YzZjNjU3NA) so we know this address is the prize and there is a puzzle hidden inside the mosaic.

![](http://buer.haus/wp-content/uploads/2021/05/3.png)

Wallet: [0x8baDc6F8ECFDD9736C5bA197CC0d820cF22E79B2](https://etherscan.io/address/0x8baDc6F8ECFDD9736C5bA197CC0d820cF22E79B2)

If you go to the location of the image, there is another image nearby that appeared to be a Neon District character with some text included.

![](http://buer.haus/wp-content/uploads/2021/05/4.png)

![](http://buer.haus/wp-content/uploads/2021/05/5.png)

What is interesting about these Neon District character images, the Twitter user associated with them contained a default Twitter profile image on twitter.com. We know that this change had to be a manual replacement by the creators so we needed to find additional images similar to this one. We also figured that they would not want to replace legitimate avatars because people wanted to be seen, so we decided to chase down the avatars.

![](http://buer.haus/wp-content/uploads/2021/05/6.png)

There was a two prong approach to solving this.

The first approach was to have one person manually scroll through and look for images.

Any programmatic approach we took, we needed to make sure that we had some manual effort in case they failed.

The second approach was to pull the first 50k Twitter followers on the coin\_artist twitter account. Pull the 50k images from the mosaic. Pull the avatar images from both and check to see if they were the default Twitter avatar images or not. If there was a default avatar image and a mismatch between the two, there is a good chance it is a puzzle related image.

We put together this script to pull the Twitter followers using the Twitter GraphQL API:

[https://gist.github.com/ziot/54333c0ddbdc3cf834da8f13af80b50f](https://gist.github.com/ziot/54333c0ddbdc3cf834da8f13af80b50f)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>``` | ```<br>import requests, json<br> <br>def getFollowers(cursor, count):<br>    variables = '{"userId":"2319408132","count":5000,"cursor":"'+cursor+'|'+count+'","withHighlightedLabel":false,"withTweetQuoteCount":false,"includePromotedContent":false,"withTweetResult":false,"withUserResults":false,"withNonLegacyCard":true,"withBirdwatchPivots":false}'<br>    url = "https://twitter.com/i/api/graphql/GFLX4V1lUMJo8xxmRPXqUQ/Followers?variables={}".format(variables)<br>    headers = {<br>        "Cookie": "",<br>        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",<br>        "Accept": "*/*",<br>        "Accept-Language": "en-US,en;q=0.5",<br>        "Accept-Encoding": "gzip, deflate",<br>        "Content-Type": "application/json",<br>        "X-Twitter-Auth-Type": "OAuth2Session",<br>        "X-Twitter-Client-Language": "en",<br>        "X-Twitter-Active-User": "yes",<br>        "X-Csrf-Token": "",<br>        "Authorization": "",<br>        "Referer": "https://twitter.com/coin_artist/followers"<br>    }<br>    r = requests.get(url, headers=headers)<br>    data = json.loads(r.text)<br> <br>    try:<br> <br>        for instructions in data["data"]["user"]["followers_timeline"]["timeline"]["instructions"]:<br>            if instructions["type"] == "TimelineAddEntries":<br> <br>                for user in instructions["entries"]:<br>                    if user["content"]["entryType"] == "TimelineTimelineCursor":<br> <br>                        # if user["content"]["cursorType"] == "Top":<br>                        if user["content"]["cursorType"] == "Bottom":<br>                            nextData = user["content"]["value"].split("|")<br>                            cursor = nextData[0]<br>                            count = nextData[1]<br>                    else:<br>                        try:<br>                            name = user["content"]["itemContent"]["user"]["legacy"]["name"]<br>                            screen = user["content"]["itemContent"]["user"]["legacy"]["screen_name"]<br>                            print(screen.encode("utf-8"))<br>                        except:<br>                            print("Failed: {0}".format(user["content"]))<br> <br>    except Exception as e:<br>        print("Failed ({0}|{1}): {2}".format(cursor, count, e))<br>        exit()<br> <br>    print(nextData)<br> <br>    return nextData<br> <br>cursor = "1698851070430206586"<br>count = "1389680245111520887"<br> <br>while True:<br>    nextData = getFollowers(cursor, count)<br>    cursor = nextData[0]<br>    count = nextData[1]<br>``` |

import requests, json

def getFollowers(cursor, count):
variables = '{"userId":"2319408132","count":5000,"cursor":"'+cursor+'\|'+count+'","withHighlightedLabel":false,"withTweetQuoteCount":false,"includePromotedContent":false,"withTweetResult":false,"withUserResults":false,"withNonLegacyCard":true,"withBirdwatchPivots":false}'
url = "https://twitter.com/i/api/graphql/GFLX4V1lUMJo8xxmRPXqUQ/Followers?variables={}".format(variables)
headers = {
"Cookie": "",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
"Accept": "\*/\*",
"Accept-Language": "en-US,en;q=0.5",
"Accept-Encoding": "gzip, deflate",
"Content-Type": "application/json",
"X-Twitter-Auth-Type": "OAuth2Session",
"X-Twitter-Client-Language": "en",
"X-Twitter-Active-User": "yes",
"X-Csrf-Token": "",
"Authorization": "",
"Referer": "https://twitter.com/coin\_artist/followers"
}
r = requests.get(url, headers=headers)
data = json.loads(r.text)

try:

for instructions in data\["data"\]\["user"\]\["followers\_timeline"\]\["timeline"\]\["instructions"\]:
if instructions\["type"\] == "TimelineAddEntries":

for user in instructions\["entries"\]:
if user\["content"\]\["entryType"\] == "TimelineTimelineCursor":

# if user\["content"\]\["cursorType"\] == "Top":
if user\["content"\]\["cursorType"\] == "Bottom":
nextData = user\["content"\]\["value"\].split("\|")
cursor = nextData\[0\]
count = nextData\[1\]
else:
try:
name = user\["content"\]\["itemContent"\]\["user"\]\["legacy"\]\["name"\]
screen = user\["content"\]\["itemContent"\]\["user"\]\["legacy"\]\["screen\_name"\]
print(screen.encode("utf-8"))
except:
print("Failed: {0}".format(user\["content"\]))

except Exception as e:
print("Failed ({0}\|{1}): {2}".format(cursor, count, e))
exit()

print(nextData)

return nextData

cursor = "1698851070430206586"
count = "1389680245111520887"

while True:
nextData = getFollowers(cursor, count)
cursor = nextData\[0\]
count = nextData\[1\]

Unfortunately, we were hit with rate limiting almost immediately.

We decided to take an alternative approach where we would:

- Pull all of the Twitter usernames from the mosaically.com page
- Query 100 Twitter profile pictures per request via api.twitter.com/1.1/users/lookup.json. Based on the Twitter Developer API docs, this is limited to 900 requests every 15 minutes. We would be able to fetch all 50k users without restriction.

In these scripts, I show how we created the sqlite database for storing the users and also how we pulled their Twitter profile pictures:

Updating sqlite file with profile images from Twitter: [https://gist.github.com/ziot/ca727f789b83c016af6e2fdbd6dde03e](https://gist.github.com/ziot/ca727f789b83c016af6e2fdbd6dde03e)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>``` | ```<br>import requests, json, sqlite3, time<br> <br>con = sqlite3.connect('db/memory.db')<br>cur = con.cursor()<br> <br>def getAvatars(userStr):<br>    url = "https://api.twitter.com/1.1/users/lookup.json?screen_name={0}".format(userStr)<br>    headers = {<br>        "Cookie": "",<br>        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",<br>        "Accept": "*/*",<br>        "Accept-Language": "en-US,en;q=0.5",<br>        "Accept-Encoding": "gzip, deflate",<br>        "Content-Type": "application/json",<br>        "X-Twitter-Auth-Type": "OAuth2Session",<br>        "X-Twitter-Client-Language": "en",<br>        "X-Twitter-Active-User": "yes",<br>        "X-Csrf-Token": "",<br>        "Authorization": "",<br>        "Referer": "https://twitter.com/coin_artist/followers"<br>    }<br>    r = requests.get(url, headers = headers)<br>    return json.loads(str(r.text).encode("utf-8"))<br> <br>def loadUsers(pagination):<br>    limit = 100<br>    users = []<br>    for row in cur.execute('SELECT user_name FROM users ORDER BY user_id ASC LIMIT {0},{1}'.format((pagination*limit), limit)):<br>        users.append(row[0])<br>    userStr = ",".join(users)<br>    users = getAvatars(userStr)<br>    try:<br>        for user in users:<br>            cur.execute('UPDATE users SET twitter_avatar="{0}" WHERE user_name="{1}"'.format(user["profile_image_url_https"], user["screen_name"]))<br>    except:<br>        print("failed:", users)<br>    # save<br>    con.commit()<br> <br>for x in range(1,501):<br>    loadUsers(x)<br>    print("{0} finished".format(x))<br>    time.sleep(1)<br> <br># close connection<br>con.close()<br>``` |

import requests, json, sqlite3, time

con = sqlite3.connect('db/memory.db')
cur = con.cursor()

def getAvatars(userStr):
url = "https://api.twitter.com/1.1/users/lookup.json?screen\_name={0}".format(userStr)
headers = {
"Cookie": "",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
"Accept": "\*/\*",
"Accept-Language": "en-US,en;q=0.5",
"Accept-Encoding": "gzip, deflate",
"Content-Type": "application/json",
"X-Twitter-Auth-Type": "OAuth2Session",
"X-Twitter-Client-Language": "en",
"X-Twitter-Active-User": "yes",
"X-Csrf-Token": "",
"Authorization": "",
"Referer": "https://twitter.com/coin\_artist/followers"
}
r = requests.get(url, headers = headers)
return json.loads(str(r.text).encode("utf-8"))

def loadUsers(pagination):
limit = 100
users = \[\]
for row in cur.execute('SELECT user\_name FROM users ORDER BY user\_id ASC LIMIT {0},{1}'.format((pagination\*limit), limit)):
users.append(row\[0\])
userStr = ",".join(users)
users = getAvatars(userStr)
try:
for user in users:
cur.execute('UPDATE users SET twitter\_avatar="{0}" WHERE user\_name="{1}"'.format(user\["profile\_image\_url\_https"\], user\["screen\_name"\]))
except:
print("failed:", users)
# save
con.commit()

for x in range(1,501):
loadUsers(x)
print("{0} finished".format(x))
time.sleep(1)

\# close connection
con.close()

Pulling the mosaic profiles and diffing the avatars: [https://gist.github.com/ziot/c2c681cc6424c62a2b9ebfa506f1eadb](https://gist.github.com/ziot/c2c681cc6424c62a2b9ebfa506f1eadb)

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>``` | ```<br>import requests, json, hashlib, re, urllib.request, sqlite3<br>from multiprocessing import Pool<br> <br>con = sqlite3.connect('db/memory.db')<br>cur = con.cursor()<br> <br>def find_between( s, first, last ):<br>    try:<br>        start = s.index( first ) + len( first )<br>        end = s.index( last, start )<br>        return s[start:end]<br>    except ValueError:<br>        return ""<br> <br>def checkDefaultAvatar(user):<br>    for row in cur.execute('SELECT twitter_avatar FROM users WHERE user_name="{0}" LIMIT 1'.format(user)):<br>        twitterAvatar = row[0]<br>    if "default_profile_images" in twitterAvatar:<br>        return True<br>    else:<br>        return False<br> <br> <br>def checkAvatar(path):<br>    url = "https://8.azureedge.net/img?l={0}".format(path)<br>    r = requests.get(url)<br>    hash = doMD5(r.text)<br>    return hash<br> <br>def getName(data):<br>    result = re.search('([0-9]+)\_(.*)\.jpg', data["name"])<br>    name = result.group(2)    <br>    return name<br> <br>def saveImage(url, name):<br>    url = "https://8.azureedge.net/img?l={0}".format(url)<br>    urllib.request.urlretrieve(url, "imgs/{0}.jpg".format(name))<br> <br>def getTile(tileCoords):<br>    try:<br>        x = tileCoords["x"]<br>        y = tileCoords["y"]<br>        url = "https://mosaically.com/slmake/gettileinfoatxy/?MosaicId=fd40c771-f976-4bf7-96b8-80379da82333&selectedRow=-1&x={0}&y={1}".format(x,y)<br>        r = requests.get(url)<br>        data = json.loads(r.text)<br>        # name = data["name"].split("_")[1]<br>        name = getName(data)<br>        thumb = data["thumb"]<br>        thumbMD5 = checkAvatar(thumb)<br>        if checkDefaultAvatar(name):<br>            if thumbMD5 != "611f87b37c4cbcb8143ccbcd6207277a":<br>                saveImage(thumb, name)<br>                print(x,y,name,thumb,thumbMD5)<br>    except Exception as e:<br>        print('exception: {0}  - {1}, {2}'.format(e, x, y))<br>        return<br> <br>    print('finished: {0}, {1}'.format(x,y))<br> <br> <br>def doMD5(input):<br>    m = hashlib.md5()<br>    m.update(input.encode("utf-8"))<br>    return m.hexdigest()<br> <br>toCheck = []<br> <br>for x in range(0, 182):<br>    for y in range (0, 273):<br>        toCheck.append({"x":x,"y":y})<br> <br>if __name__ == '__main__':<br>    pool = Pool(processes=10)<br>    pool.map(getTile, toCheck)<br>``` |

import requests, json, hashlib, re, urllib.request, sqlite3
from multiprocessing import Pool

con = sqlite3.connect('db/memory.db')
cur = con.cursor()

def find\_between( s, first, last ):
try:
start = s.index( first ) + len( first )
end = s.index( last, start )
return s\[start:end\]
except ValueError:
return ""

def checkDefaultAvatar(user):
for row in cur.execute('SELECT twitter\_avatar FROM users WHERE user\_name="{0}" LIMIT 1'.format(user)):
twitterAvatar = row\[0\]
if "default\_profile\_images" in twitterAvatar:
return True
else:
return False

def checkAvatar(path):
url = "https://8.azureedge.net/img?l={0}".format(path)
r = requests.get(url)
hash = doMD5(r.text)
return hash

def getName(data):
result = re.search('(\[0-9\]+)\\\_(.\*)\\.jpg', data\["name"\])
name = result.group(2)
return name

def saveImage(url, name):
url = "https://8.azureedge.net/img?l={0}".format(url)
urllib.request.urlretrieve(url, "imgs/{0}.jpg".format(name))

def getTile(tileCoords):
try:
x = tileCoords\["x"\]
y = tileCoords\["y"\]
url = "https://mosaically.com/slmake/gettileinfoatxy/?MosaicId=fd40c771-f976-4bf7-96b8-80379da82333&selectedRow=-1&x={0}&y={1}".format(x,y)
r = requests.get(url)
data = json.loads(r.text)
# name = data\["name"\].split("\_")\[1\]
name = getName(data)
thumb = data\["thumb"\]
thumbMD5 = checkAvatar(thumb)
if checkDefaultAvatar(name):
if thumbMD5 != "611f87b37c4cbcb8143ccbcd6207277a":
saveImage(thumb, name)
print(x,y,name,thumb,thumbMD5)
except Exception as e:
print('exception: {0} - {1}, {2}'.format(e, x, y))
return

print('finished: {0}, {1}'.format(x,y))

def doMD5(input):
m = hashlib.md5()
m.update(input.encode("utf-8"))
return m.hexdigest()

toCheck = \[\]

for x in range(0, 182):
for y in range (0, 273):
toCheck.append({"x":x,"y":y})

if \_\_name\_\_ == '\_\_main\_\_':
pool = Pool(processes=10)
pool.map(getTile, toCheck)

This script had a fairly good success rate. We hit 50 profiles that contained a Twitter default avatar and the mosaic avatar mismatched. Unfortunately, 2 were false positives and after further analysing the data, we were missing 2 puzzle images.

The manual effort had found all of them except for 1, meaning our manual effort actually worked faster AND better than the programmatic approach. We stuck with both efforts, but set out with a new goal:

- Download all 50k mosaic avatar images, then do image comparison analysis. At this point we knew there were 12 sets of 4 images and we already had 3 images for the set we were missing an image from. If we ran the image analysis comparison against each profile image with the 3 images we already had, we should get a hit.
- More importantly: continue our manual efforts!

After an hour, the manual effort pulled through and found the image we were missing. We decided to toss the image we found at the image analysis to see if it got a hit and it did not. This is a good lesson that trying to go fast with scripts and casting a wide net sometimes is a burden rather than saving you time.

The resulting set:

![](http://buer.haus/wp-content/uploads/2021/05/7.png)

Putting it together into a spreadsheet:

[![](http://buer.haus/wp-content/uploads/2021/05/matrix-992x1024.png)](http://buer.haus/wp-content/uploads/2021/05/matrix.png)

We realized there are sets of Neon District characters and each set had four images. These sets were labelled with A, B, C, and D. They also contained a numeric string on the right side of them. We put these numeric strings into the excel sheet to further analyze the data:

[![](http://buer.haus/wp-content/uploads/2021/05/8-927x1024.png)](http://buer.haus/wp-content/uploads/2021/05/8.png)

The strings:

- 9137174529995420057710
- 713876227637167595537
- 1913644091575210065956
- 1113582243745332142119
- 212779986703575572492
- 1513089092305320468505
- 313628096403213598723
- 212754788261437358094
- 19131476789261375078511
- 1113716079581827932188
- 12133854265528263475212
- 413821332111788154941

We made a few realizations:

- A-C were always 6 length and the font size is static in the image. It appeared that a single string was split across the four images. This suggests we should concat the strings together.
- The lengths were not even, they went between 21 to 23. This means we cannot turn them into a grid or anything of that sort.
- The puzzle wallet is an Ethereum address and with twelve numbers, they likely somehow result into BIP wallets for a bip seed word private key.

After a few hours of poking and prodding, we made our first breakthrough. If you look at the end of each string, there is 1 through 12.

- 9137174529995420057710 = 10
- 713876227637167595537 = 7
- 1913644091575210065956 = 6
- 1113582243745332142119 = 9
- Etc.

This was a really convenient thing to notice because the strings being uneven makes them vastly more difficult to work with. By establishing that parts of the string are probably indicators and the data to work with is somewhere in the middle of the string, it let us view it from a new perspective.

The second thing we noticed is that all of these strings near the front either started with 12 or 13.

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| 9 | 13 | 71745299954200577 | 10 |
| 7 | 13 | 87622763716759553 | 7 |  |
| 19 | 13 | 64409157521006595 | 6 |  |
| 11 | 13 | 58224374533214211 | 9 |  |
| 2 | 12 | 77998670357557249 | 2 |  |
| 15 | 13 | 08909230532046850 | 5 |  |
| 3 | 13 | 62809640321359872 | 3 |  |
| 2 | 12 | 75478826143735809 | 4 |  |
| 19 | 13 | 14767892613750785 | 11 |  |
| 11 | 13 | 71607958182793218 | 8 |  |
| 12 | 13 | 385426552826347521 | 2 |  |
| 4 | 13 | 82133211178815494 | 1 |

In previous coin\_artist puzzles, she was notorious for using 1347 as a calling card of sorts. If you found the number in a step or in a location relative to a puzzle, you knew you were on the right path. The fact that there were 1371, 1387, 1364, etc. all around the data, it was a rabbit-hole we dove into. This turned out to be nothing. After a few more hours, we made our second breakthrough!

The 12 and 13s were part of the data in the 3rd column, they are coin\_artist tweet IDs. Example: [https://twitter.com/coin\_artist/status/1371745299954200577](https://twitter.com/coin_artist/status/1371745299954200577)

|     |     |     |
| --- | --- | --- |
| 9 | [https://twitter.com/coin\_artist/status/1371745299954200577](https://twitter.com/coin_artist/status/1371745299954200577) | 10 |
| 7 | [https://twitter.com/coin\_artist/status/1387622763716759553](https://twitter.com/coin_artist/status/1387622763716759553) | 7 |
| 19 | [https://twitter.com/coin\_artist/status/1364409157521006595](https://twitter.com/coin_artist/status/1364409157521006595) | 6 |
| 11 | [https://twitter.com/coin\_artist/status/1358224374533214211](https://twitter.com/coin_artist/status/1358224374533214211) | 9 |
| 2 | [https://twitter.com/coin\_artist/status/1277998670357557249](https://twitter.com/coin_artist/status/1277998670357557249) | 2 |
| 15 | [https://twitter.com/coin\_artist/status/1308909230532046850](https://twitter.com/coin_artist/status/1308909230532046850) | 5 |
| 3 | [https://twitter.com/coin\_artist/status/1362809640321359872](https://twitter.com/coin_artist/status/1362809640321359872) | 3 |
| 2 | [https://twitter.com/coin\_artist/status/1275478826143735809](https://twitter.com/coin_artist/status/1275478826143735809) | 4 |
| 19 | [https://twitter.com/coin\_artist/status/1314767892613750785](https://twitter.com/coin_artist/status/1314767892613750785) | 11 |
| 11 | [https://twitter.com/coin\_artist/status/1371607958182793218](https://twitter.com/coin_artist/status/1371607958182793218) | 8 |
| 12 | [https://twitter.com/coin\_artist/status/13385426552826347521](https://twitter.com/coin_artist/status/13385426552826347521) | 2 |
| 4 | [https://twitter.com/coin\_artist/status/1382133211178815494](https://twitter.com/coin_artist/status/1382133211178815494) | 1 |

It was at this point that we knew what we had to do with the puzzle. The left number is a book cipher indexing into the tweet to pull bip words. The number on the right is the order for the BIP words for the private key.

For example, if we take “1113716079581827932188” and split it into the pieces:

- Word index: 11
- Tweet ID: 1371607958182793218
- Order index: 8

**Load the tweet:**

[https://twitter.com/coin\_artist/status/1371607958182793218](https://twitter.com/coin_artist/status/1371607958182793218)

Twitter Embed

> If your NFT doesn’t come with a magic trick or teach me something new, I don’t want it.
>
> — COIN ARTIST (@coin\_artist) [March 15, 2021](https://twitter.com/coin_artist/status/1371607958182793218?ref_src=twsrc%5Etfw)

**Extract:**

The 11th word of the tweet is: teach.

**Pulling out the words:**

| Word Index | Tweet ID | Index | BIP Word |
| --- | --- | --- | --- |
| 4 | 1382133211178815494 | 1 | right |
| 12 | 13385426552826347521 | 2 | rabbit |
| 3 | 1362809640321359872 | 3 | glad |
| 2 | 1275478826143735809 | 4 | cave |
| 15 | 1308909230532046850 | 5 | abstract |
| 19 | 1364409157521006595 | 6 | stage |
| 7 | 1387622763716759553 | 7 | fire |
| 11 | 1371607958182793218 | 8 | teach |
| 11 | 1358224374533214211 | 9 | choice |
| 9 | 1371745299954200577 | 10 | faith |
| 19 | 1314767892613750785 | 11 | special |
| 2 | 1277998670357557249 | 12 | play |

We get the final private key seed word phrase:

right rabbit glad cave abstract stage fire teach choice faith special play

Solved!

Thanks again to coin\_artist for always engaging us with fun puzzles and cutting edge experiences in the NFT space. Give [her a follow](https://twitter.com/coin_artist) and make sure you keep an eye out, you might be lucky enough to catch one of her puzzles as soon as it drops.

Twitter Widget Iframe