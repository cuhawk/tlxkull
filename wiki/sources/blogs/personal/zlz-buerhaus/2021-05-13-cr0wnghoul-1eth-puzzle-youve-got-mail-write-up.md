---
source: zlz-buerhaus
source_url: https://buer.haus/2021/05/13/cr0wnghoul-1eth-puzzle-youve-got-mail-write-up/
title: "Cr0wnGhoul 1ETH Puzzle: You’ve Got Mail Write-up | ziot"
---

[< Back](https://buer.haus/)

![](http://buer.haus/wp-content/uploads/2021/05/cr0wnlogo-1.png)

Solved by:

- [ziot (@bbuerhaus)](https://twitter.com/bbuerhaus)
- [xEHLE (@xEHLE\_)](https://twitter.com/xEHLE_)
- [mattm (@mattmcquaig)](https://twitter.com/mattmcquaig)
- [LeFevre (@\_LeFevre\_)](https://twitter.com/_LeFevre_)

[Cr0wn\_Gh0ul](https://twitter.com/cr0wn_gh0ul) launched a new puzzle with a 1 Eth and 800 Matic prize recently. This involved airdropping matic NFTs and contracts to many addresses, similar to the one million matic NFTs he airdropped recently. This puzzle involved navigating the contracts, finding the NFTs, extracting text from the NFT images, and using the text as a private key. I will explain the process that went into solving this puzzle.

Twitter Embed

> Title: You Got Mail!
>
> Puzzle: 0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A
>
> Prize: 1 ETH + ? MATIC
>
> — T.Salem (@Cr0wn\_Gh0ul) [May 11, 2021](https://twitter.com/Cr0wn_Gh0ul/status/1392246558360543238?ref_src=twsrc%5Etfw)

# The Airdrop

This started with the tweet above, although some of us had already noticed the mass minting that was going on with NFTs on the "Recent" list on OpenSea. Using the Matic explorer, I was able to view the address that was creating all of the contracts:

[https://explorer-mainnet.maticvigil.com/address/0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A/transactions](https://explorer-mainnet.maticvigil.com/address/0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A/transactions)

Due to the amount of NFTs being created, it appeared to be causing problems for OpenSea and much like the similar Cr0wn NFTs, they were blacklisted and no longer viewable on OpenSea. With the address, I would still be able to view the transactions and NFTs. Sadly, I didn't get any screenshots of OpenSea before the write-up, but I can show you what it looked like linking it in Discord:

![](http://buer.haus/wp-content/uploads/2021/05/nft.png)

# The NFT

The NFT was comprised of a randomly generated name, text in a polar circle around the center, and two randomly picked colors.

![](http://buer.haus/wp-content/uploads/2021/05/0bed1en7.png)

Given the length of the hex string in the circle and also the amount of NFTs being generated, it was likely that one of the NFT hex strings was the private key to the puzzle wallet. Unfortunately, it seemed like a million of these NFTs were going to be created.

In order to tackle this, we would need to download every image related to the NFT and extract the strings off of them at scale.

# The Explorer

Unfortunately, maticvigil.com matic explorer had a strict WAF in front of it and loading it with Python requests was going to be next to impossible for the amount of requests I needed to make. We were stuck with what to do next until mattm found out we could query it with the api.covalenthq.com API.

## Getting the Contracts

First we would query the transactions from the address:

[https://api.covalenthq.com/v1/137/address/0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A/transactions\_v2/?no-logs=true&page-number=1&page-size=5000&key=](https://api.covalenthq.com/v1/137/address/0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A/transactions_v2/?no-logs=true&page-number=1&page-size=5000&key=)

Then we would get the transaction details:

[https://api.covalenthq.com/v1/137/transaction\_v2/{0}/?&key=](https://api.covalenthq.com/v1/137/transaction_v2/%7B0%7D/?&key=)

And finally we could fetch the token names from the transaction:

[https://api.covalenthq.com/v1/137/tokens/{0}/nft\_token\_ids/?&key=](https://api.covalenthq.com/v1/137/tokens/%7B0%7D/nft_token_ids/?&key=)

This was condensed down into the following Python script:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>76<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>``` | ```<br>import requests, json, urllib.request<br>from multiprocessing import Pool<br> <br>ckey = ""<br> <br>def dedupe(lst):<br>    return list(dict.fromkeys(lst))<br> <br>def getTransactions(url=""):<br>    if url == "":<br>        url = "https://api.covalenthq.com/v1/137/address/0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A/transactions_v2/?no-logs=true&page-number=1&page-size=5000&key="<br>    r = requests.get(url)<br>    txArr = []<br>    data = json.loads(r.text)<br>    for tx in data["data"]["items"]:<br>        txArr.append(tx["tx_hash"])<br>    return txArr<br> <br>def getCr0wn(name):<br>    url = "https://cr0wngh0ul.s3.us-east-2.amazonaws.com/{0}.json".format(name)<br>    r = requests.get(url)<br>    return json.loads(r.text)<br> <br>def getSender(tx):<br>    url = "https://api.covalenthq.com/v1/137/transaction_v2/{0}/?&key=".format(tx)<br>    r = requests.get(url)<br>    return json.loads(r.text)["data"]["items"]<br> <br>def getToken(address):<br>    url = "https://api.covalenthq.com/v1/137/tokens/{0}/nft_token_ids/?&key=".format(address)<br>    r = requests.get(url)<br>    return json.loads(r.text)["data"]<br> <br>def getSenderAddress(tx):<br>    senders = getSender(tx)<br>    for sender in senders:<br>        events = sender["log_events"]<br>        for event in events:<br>            if event["sender_address"] != "0x0000000000000000000000000000000000001010":<br>                return event["sender_address"]<br> <br>def getSenders(txArr):<br>    senders = []<br>    for tx in txArr:<br>        senderAddresses = getSenderAddress(tx)<br>        senders.append(senderAddresses)<br>    return dedupe(senders)<br> <br>def getContracts(senders):<br>    contracts = []<br>    for sender in senders:<br>        tokenData = getToken(sender)<br>        for item in tokenData["data"]["items"]:<br>            if item["contract_name"] not in contracts:<br>                contracts.append(item["contract_name"])<br>    return dedupe(contracts)<br> <br>def getContractName(tx):<br>    senderAddress = getSender(tx)[0]["log_events"][1]["sender_address"]<br>    token = getToken(senderAddress)<br>    name = token["items"][0]["contract_name"]<br>    return name<br> <br>def getImg(name):<br>    url = "https://cr0wngh0ul.s3.us-east-2.amazonaws.com/{0}.png".format(name)<br>    print("Saving: {0}".format(name))<br>    urllib.request.urlretrieve(url, "images/{0}.png".format(name))<br> <br>def poolRoutine(tx):<br>    try:<br>        name = getContractName(tx)<br>        getImg(name)<br>    except:<br>        print("Failed: {0}".format(tx))<br>        return<br> <br>if __name__=='__main__':<br> <br>    txArr = dedupe(getTransactions())<br> <br>    print("Total tx: {0}".format(len(txArr)))<br> <br>    pool = Pool(processes=10)<br>    pool.map(poolRoutine, txArr)<br>``` |

import requests, json, urllib.request
from multiprocessing import Pool

ckey = ""

def dedupe(lst):
return list(dict.fromkeys(lst))

def getTransactions(url=""):
if url == "":
url = "https://api.covalenthq.com/v1/137/address/0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A/transactions\_v2/?no-logs=true&page-number=1&page-size=5000&key="
r = requests.get(url)
txArr = \[\]
data = json.loads(r.text)
for tx in data\["data"\]\["items"\]:
txArr.append(tx\["tx\_hash"\])
return txArr

def getCr0wn(name):
url = "https://cr0wngh0ul.s3.us-east-2.amazonaws.com/{0}.json".format(name)
r = requests.get(url)
return json.loads(r.text)

def getSender(tx):
url = "https://api.covalenthq.com/v1/137/transaction\_v2/{0}/?&key=".format(tx)
r = requests.get(url)
return json.loads(r.text)\["data"\]\["items"\]

def getToken(address):
url = "https://api.covalenthq.com/v1/137/tokens/{0}/nft\_token\_ids/?&key=".format(address)
r = requests.get(url)
return json.loads(r.text)\["data"\]

def getSenderAddress(tx):
senders = getSender(tx)
for sender in senders:
events = sender\["log\_events"\]
for event in events:
if event\["sender\_address"\] != "0x0000000000000000000000000000000000001010":
return event\["sender\_address"\]

def getSenders(txArr):
senders = \[\]
for tx in txArr:
senderAddresses = getSenderAddress(tx)
senders.append(senderAddresses)
return dedupe(senders)

def getContracts(senders):
contracts = \[\]
for sender in senders:
tokenData = getToken(sender)
for item in tokenData\["data"\]\["items"\]:
if item\["contract\_name"\] not in contracts:
contracts.append(item\["contract\_name"\])
return dedupe(contracts)

def getContractName(tx):
senderAddress = getSender(tx)\[0\]\["log\_events"\]\[1\]\["sender\_address"\]
token = getToken(senderAddress)
name = token\["items"\]\[0\]\["contract\_name"\]
return name

def getImg(name):
url = "https://cr0wngh0ul.s3.us-east-2.amazonaws.com/{0}.png".format(name)
print("Saving: {0}".format(name))
urllib.request.urlretrieve(url, "images/{0}.png".format(name))

def poolRoutine(tx):
try:
name = getContractName(tx)
getImg(name)
except:
print("Failed: {0}".format(tx))
return

if \_\_name\_\_=='\_\_main\_\_':

txArr = dedupe(getTransactions())

print("Total tx: {0}".format(len(txArr)))

pool = Pool(processes=10)
pool.map(poolRoutine, txArr)

Although a metric ton of NFTs were made, they were not all unique. After running through this entire list, we were able to dump 2609 unique NFT images.

[![](http://buer.haus/wp-content/uploads/2021/05/nft-images-1024x789.png)](http://buer.haus/wp-content/uploads/2021/05/nft-images.png)

## Getting the text out

When faced with text in an image, we have a few options:

- Optical Character Recognition (OCR) - Programmatic way to extract text from images. Downsides: can be hard to train, images need to be clean and well formatted.
- Mechanical Turk - Pay people to write the text out. Downsides: cost money, no guarantee for accuracy.
- Type it yourself. Downsides: typing it yourself.

The clear winner is starting with OCR. The first issue we run into is that the text is circular and we will not be able to trivially train the characters. Before we can even consider going through OCR, we need to find a way to extract the text out into a straight line that is uniform across all 2609 images.

We have two options for this, that I know of:

- Pick a starting x,y coordinate in the image and height, width to crop to pull each letter. For each of the 66 characters, we need to rotate the image to ensure that the characters are all concatenated with the same rotation.
- Since all of the images are the same height, text is in the same position, and middle circle is always the same size, we can try to run it through a depolarization filter. This is a fairly standard filter that exists in a lot of image libraries such as ImageMagick, Photoshop, etc.

I don't want to dive too deep into the depolar because that was about an hour of effort that I did not document much. But here is an example of passing it through ImageMagick with depolar filter.

Command:

```
convert test3.png -virtual-pixel Black -set option:distort:scale 4 -distort DePolar -1 -roll +60+0 -virtual-pixel HorizontalTile -background Black -set option:distort:scale .25 polar.png
```

[![](http://buer.haus/wp-content/uploads/2021/05/polar-1024x1024.png)](http://buer.haus/wp-content/uploads/2021/05/polar.png)

Unfortunately, this was a bit stretched and it was hard to determine where (or even how) to shift the text so it did not get cropped out. I decided to pursue a Python PIL approach with the rotations instead.

The first problem we face with Python PIL is figuring out where we start, given that the circular text is always started in different positions. So we attempt to extract at 244,40 with the height/width of 20,20 or 25,25.

### Case A

[![](http://buer.haus/wp-content/uploads/2021/05/a1-1024x602.png)](http://buer.haus/wp-content/uploads/2021/05/a1.png)

### Case B

[![](http://buer.haus/wp-content/uploads/2021/05/a2-1024x602.png)](http://buer.haus/wp-content/uploads/2021/05/a2.png)

As you can see, there was no guarantee of a good starting position. Rotating the images manually in Photoshop, it was determined that the following approach had to be taken:

**Output 1:**

- Perform an initial rotation of 0
- Rotate the image every 15.45 degrees for each character

**Output 2:**

- Perform an initial rotation of 25
- Rotate the image every 5.45 degrees for each character

This was unfortunate because now we have doubled our image data, but it was the only way we could find a way forward quickly. This resulted in an image that looked like the following:

![](http://buer.haus/wp-content/uploads/2021/05/test0.png)

Now that we had letters extracting out, we can concatenate them together:

[![](http://buer.haus/wp-content/uploads/2021/05/test-1024x16.png)](http://buer.haus/wp-content/uploads/2021/05/test.png)

This is a good start, but when you try to use OCR to extract text from images, you will learn quickly that the best results is to contrast the image as much as possible and reduce it to two colors if possible.

Originally I tried to detect the background image color then replace any color not the background into white. This did not work well because of anti-aliasing. Then I tried to use PIL's filter grayscaling and autocontrast. This had decent results, but due to the random colors being selected, some images were still somewhat gray on gray which would not work well.

xEHLE came up with the idea of using numpy:

- Delete two color channels
- Threshhold cutoff for if a pixel should be white or black
- Invert if bg is white

This had a perfect result where all images would come out looking like this:

[![](http://buer.haus/wp-content/uploads/2021/05/1-0bed1en7-1024x15.png)](http://buer.haus/wp-content/uploads/2021/05/1-0bed1en7.png)

Here is what the final script looked like:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>76<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>89<br>90<br>91<br>92<br>93<br>94<br>95<br>96<br>97<br>98<br>99<br>100<br>101<br>102<br>103<br>104<br>105<br>106<br>107<br>108<br>109<br>110<br>111<br>112<br>113<br>114<br>115<br>116<br>117<br>118<br>119<br>120<br>121<br>122<br>123<br>124<br>125<br>126<br>127<br>128<br>129<br>130<br>131<br>132<br>133<br>134<br>135<br>136<br>137<br>138<br>139<br>140<br>141<br>142<br>143<br>144<br>145<br>146<br>147<br>148<br>149<br>150<br>151<br>152<br>153<br>154<br>155<br>``` | ```<br>import pytesseract<br> <br>from multiprocessing import Pool<br> <br>from PIL import Image, ImageEnhance, ImageFilter, ImageOps<br>from os import listdir<br>from os.path import isfile, join<br> <br>import numpy as np<br> <br>pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'<br> <br>def getCropPositions(position):<br> <br>    cropSizeHeight = 15<br>    cropSizeWidth = 20<br>    cropPosStartX = 250<br>    cropPosStartY = 45<br> <br>    cropPosEndX = cropPosStartX+cropSizeWidth<br>    cropPosEndY = cropPosStartY+cropSizeHeight<br> <br>    return {<br>        "startX": cropPosStartX,<br>        "startY": cropPosStartY,<br>        "endX": cropPosEndX,<br>        "endY": cropPosEndY<br>    }<br> <br>def recolor(img2):<br>    bgColor = getBgColor(img2)<br>    rgb_im = img2.convert('RGB')<br>    pixels = rgb_im.load()<br>    for i in range(img2.size[0]):<br>        for j in range(img2.size[1]):<br>            r,g,b = pixels[i,j]<br>            r2,g2,b2 = bgColor<br>            if r != r2 and g != g2 and b != b2:<br>                pixels[i,j] = (0,0,0)<br>    return rgb_im<br> <br>def getBgColor(img):<br>    rgb_im = img.convert('RGB')<br>    r, g, b = rgb_im.getpixel((1, 1))<br>    return(r,g,b)<br> <br>def getOCRText(file):<br>    text = pytesseract.image_to_string(<br>        Image.open(file),<br>        lang="English",<br>        config="--psm 4 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFX"<br>    )<br>    return text<br> <br>def getLetter(image, position, type=1):<br> <br>    cropPositions = getCropPositions(position)<br> <br>    img = Image.open("images/{0}".format(image))<br> <br>    #img = recolor(img)<br> <br>    if type == 1:<br>        baseRot = 0<br>        posRot = 15.45<br>    else:<br>        baseRot = 25<br>        posRot = 5.45<br> <br>    img = img.rotate((baseRot+(5.45*position)), resample=Image.BICUBIC)<br> <br> <br>    img = img.crop((<br>        cropPositions["startX"],<br>        cropPositions["startY"],<br>        cropPositions["endX"],<br>        cropPositions["endY"]<br>    ))<br> <br>    width, height = img.size<br>    img = img.resize((width*5, height*5), resample=Image.BICUBIC)<br>    img_arr = np.array(img, np.uint8)<br>    img_arr[::, ::, 0] = 0<br>    img_arr[::, ::, 2] = 100<br>    img = Image.fromarray(img_arr)<br> <br>    thresh = 85<br>    fn = lambda x : 255 if x > thresh else 0<br>    img = img.convert('L').point(fn, mode='1')<br> <br>    if img.getpixel((1, 1)) == 0xff:<br>        img = img.convert('L')<br>        img = ImageOps.invert(img)<br> <br>    return img<br> <br>def get_concat_h(im1, im2):<br>    dst = Image.new('RGB', (im1.width + im2.width, im1.height))<br>    dst.paste(im1, (0, 0))<br>    dst.paste(im2, (im1.width, 0))<br>    return dst<br> <br> <br>def makeStringImg(fileName, type=1):<br>    stringDir = "./strings"<br>    test = Image.new('RGB', (20, 20*5), (0, 0, 0))<br>    for x in range(0,66):<br>        newImg = getLetter(fileName, x, type)<br>        if x == 0:<br>            newImg = get_concat_h(test, newImg)<br>        else:<br>            newImg = get_concat_h(oldImg, newImg)<br>        oldImg = newImg<br>    newImg = get_concat_h(oldImg, test)<br>    newImg.save('{0}/{1}-{2}'.format(stringDir, type, fileName))<br> <br>def getImages(mypath="./images/"):<br>    images = [f for f in listdir(mypath) if isfile(join(mypath, f))]<br>    return images<br> <br>def getOCRImages(mypath="./strings/"):<br>    images = [f for f in listdir(mypath) if isfile(join(mypath, f))]<br>    for image in images:<br>        text = pytesseract.image_to_string(<br>            Image.open('{0}/{1}'.format(mypath, image)),<br>            lang="English",<br>            config="--psm 4 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFX"<br>        )<br>        print("Test: ", text)<br>        exit()<br> <br>def makeStrings(image):<br>    try:<br>        makeStringImg(image, 1)<br>        makeStringImg(image, 2)<br>        print('{0} finished'.format(image))<br>    except:<br>        print('{0} failed'.format(image))<br> <br>def testStrings():<br>    makeStringImg("0bl1ged_gray_jackal_57evena.png", 1)<br>    makeStringImg("0bl1ged_gray_jackal_57evena.png", 2)<br>    makeStringImg("0bed1en7.png", 1)<br>    makeStringImg("0bed1en7.png", 2)<br> <br># getImages()<br># makeStringImg("0range_red_7aran7ula_Darby.png", 1)<br># makeStringImg("0range_red_7aran7ula_Darby.png", 2)<br> <br>if __name__=='__main__':<br> <br>    images = getImages()<br> <br>    pool = Pool(processes=10)<br>    pool.map(makeStrings, images)<br>``` |

import pytesseract

from multiprocessing import Pool

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from os import listdir
from os.path import isfile, join

import numpy as np

pytesseract.pytesseract.tesseract\_cmd = 'C:\\\Program Files\\\Tesseract-OCR\\\tesseract.exe'

def getCropPositions(position):

cropSizeHeight = 15
cropSizeWidth = 20
cropPosStartX = 250
cropPosStartY = 45

cropPosEndX = cropPosStartX+cropSizeWidth
cropPosEndY = cropPosStartY+cropSizeHeight

return {
"startX": cropPosStartX,
"startY": cropPosStartY,
"endX": cropPosEndX,
"endY": cropPosEndY
}

def recolor(img2):
bgColor = getBgColor(img2)
rgb\_im = img2.convert('RGB')
pixels = rgb\_im.load()
for i in range(img2.size\[0\]):
for j in range(img2.size\[1\]):
r,g,b = pixels\[i,j\]
r2,g2,b2 = bgColor
if r != r2 and g != g2 and b != b2:
pixels\[i,j\] = (0,0,0)
return rgb\_im

def getBgColor(img):
rgb\_im = img.convert('RGB')
r, g, b = rgb\_im.getpixel((1, 1))
return(r,g,b)

def getOCRText(file):
text = pytesseract.image\_to\_string(
Image.open(file),
lang="English",
config="--psm 4 --oem 3 -c tessedit\_char\_whitelist=0123456789ABCDEFX"
)
return text

def getLetter(image, position, type=1):

cropPositions = getCropPositions(position)

img = Image.open("images/{0}".format(image))

#img = recolor(img)

if type == 1:
baseRot = 0
posRot = 15.45
else:
baseRot = 25
posRot = 5.45

img = img.rotate((baseRot+(5.45\*position)), resample=Image.BICUBIC)


img = img.crop((
cropPositions\["startX"\],
cropPositions\["startY"\],
cropPositions\["endX"\],
cropPositions\["endY"\]
))

width, height = img.size
img = img.resize((width\*5, height\*5), resample=Image.BICUBIC)
img\_arr = np.array(img, np.uint8)
img\_arr\[::, ::, 0\] = 0
img\_arr\[::, ::, 2\] = 100
img = Image.fromarray(img\_arr)

thresh = 85
fn = lambda x : 255 if x > thresh else 0
img = img.convert('L').point(fn, mode='1')

if img.getpixel((1, 1)) == 0xff:
img = img.convert('L')
img = ImageOps.invert(img)

return img

def get\_concat\_h(im1, im2):
dst = Image.new('RGB', (im1.width + im2.width, im1.height))
dst.paste(im1, (0, 0))
dst.paste(im2, (im1.width, 0))
return dst

def makeStringImg(fileName, type=1):
stringDir = "./strings"
test = Image.new('RGB', (20, 20\*5), (0, 0, 0))
for x in range(0,66):
newImg = getLetter(fileName, x, type)
if x == 0:
newImg = get\_concat\_h(test, newImg)
else:
newImg = get\_concat\_h(oldImg, newImg)
oldImg = newImg
newImg = get\_concat\_h(oldImg, test)
newImg.save('{0}/{1}-{2}'.format(stringDir, type, fileName))

def getImages(mypath="./images/"):
images = \[f for f in listdir(mypath) if isfile(join(mypath, f))\]
return images

def getOCRImages(mypath="./strings/"):
images = \[f for f in listdir(mypath) if isfile(join(mypath, f))\]
for image in images:
text = pytesseract.image\_to\_string(
Image.open('{0}/{1}'.format(mypath, image)),
lang="English",
config="--psm 4 --oem 3 -c tessedit\_char\_whitelist=0123456789ABCDEFX"
)
print("Test: ", text)
exit()

def makeStrings(image):
try:
makeStringImg(image, 1)
makeStringImg(image, 2)
print('{0} finished'.format(image))
except:
print('{0} failed'.format(image))

def testStrings():
makeStringImg("0bl1ged\_gray\_jackal\_57evena.png", 1)
makeStringImg("0bl1ged\_gray\_jackal\_57evena.png", 2)
makeStringImg("0bed1en7.png", 1)
makeStringImg("0bed1en7.png", 2)

\# getImages()
\# makeStringImg("0range\_red\_7aran7ula\_Darby.png", 1)
\# makeStringImg("0range\_red\_7aran7ula\_Darby.png", 2)

if \_\_name\_\_=='\_\_main\_\_':

images = getImages()

pool = Pool(processes=10)
pool.map(makeStrings, images)

The resulting images were good enough to start extracting text with an OCR library, but not without its own problems!

## Reading the text

How do you get text out of an image? There is a ton of research and tools that exist for OCR nowadays. These libraries are easy to install and can be imported easily as libraries into most programming languages. There are also toolkits that exist to help you train images into character sets.

I started with the following:

- Tesseract/pyTesseract
- jTessBoxEditor

jTessBoxEditor is a Java applet that lets you create box images from fonts or images. This is really useful if you know the font you are working with. In this case, it was either Georgia or Helvetica. I did not have any luck using either of these, so I tried to create my own box. It looks like this:

[![](http://buer.haus/wp-content/uploads/2021/05/jtessboxeditor-1024x586.png)](http://buer.haus/wp-content/uploads/2021/05/jtessboxeditor.png)

I must have spent four hours on this with no luck. I don't know if I was using it wrong or what was going on, but I was getting no results out of this. I eventually decided to pivot over to [Google Cloud's Vision OCR](https://cloud.google.com/vision/docs/).

The initial results were good! We were getting extracts out, but some of the characters were unicode from European character sets. It was not until we discovered that you could specify a specific charset language did we get clean strings out. This was really interesting to explore, but there is not much to really show other than the Python script:

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>15<br>16<br>17<br>18<br>19<br>20<br>21<br>22<br>23<br>24<br>25<br>26<br>27<br>28<br>29<br>30<br>31<br>32<br>33<br>34<br>35<br>36<br>37<br>38<br>39<br>40<br>41<br>42<br>43<br>44<br>45<br>46<br>47<br>48<br>49<br>50<br>51<br>52<br>53<br>54<br>55<br>56<br>57<br>58<br>59<br>60<br>61<br>62<br>63<br>64<br>65<br>66<br>67<br>68<br>69<br>70<br>71<br>72<br>73<br>74<br>75<br>76<br>77<br>78<br>79<br>80<br>81<br>82<br>83<br>84<br>85<br>86<br>87<br>88<br>89<br>90<br>91<br>92<br>93<br>94<br>95<br>``` | ```<br>import requests, json, base64, io<br>import binascii<br> <br>from multiprocessing import Pool<br> <br>from os import listdir<br>from os.path import isfile, join<br> <br>def getExtract(imageData):<br>    url = "https://content-vision.googleapis.com/v1/images:annotate?alt=json&key="<br>    r = requests.post(url, headers = {<br>        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",<br>        "Accept": "*/*",<br>        "Accept-Language": "en-US,en;q=0.5",<br>        "Accept-Encoding": "gzip, deflate",<br>        "X-Clientdetails": "",<br>        "Authorization": "",<br>        "Content-Type": "application/json",<br>        "X-Requested-With": "XMLHttpRequest",<br>        "X-Javascript-User-Agent": "apix/3.0.0 google-api-javascript-client/1.1.0",<br>        "X-Origin": "https://explorer.apis.google.com",<br>        "X-Referer": "https://explorer.apis.google.com",<br>        "X-Goog-Encode-Response-If-Executable": "base64",<br>        "Origin": "https://content-vision.googleapis.com",<br>        "Referer": "",<br>        "Te": "trailers",<br>        "Connection": "close"<br>    }, json = {<br>        "requests": [{<br>            "features": [{<br>                "type": "TEXT_DETECTION"<br>            }],<br>            "image": {<br>                "content": imageData<br>            },<br>            "imageContext": {<br>                "languageHints": [<br>                    "en"<br>                ]<br>            }<br>        }]<br>    })<br>    # json = {"requests":[{"features":[{"type":"TEXT_DETECTION"}],"image":{"source":{"imageUri":str(imageUrl)}}}]}<br>    return cleanText(json.loads(r.text)["responses"][0]["fullTextAnnotation"]["text"])<br> <br> <br>def cleanText(text):<br>    # lower<br>    text = text.lower()<br>    # replacements<br>    replacements = [<br>        [" ", ""],<br>        ["\n", ""],<br>        ["o", "0"],<br>        ["в","b"],<br>        ["с","c"],<br>        ["з","3"],<br>        ["o","0"],<br>        ["о","0"],<br>        ["х","x"]<br>    ]<br>    for replacement in replacements:<br>        text = text.replace(replacement[0], replacement[1])<br>    # shift<br>    textStart = text.find("0x")<br>    before = text[:textStart]<br>    after = text[len(before):]<br>    text = after+before<br>    # ensure no extra newline was added<br>    text = text.replace("\n", "")<br>    return text<br> <br>def getImages(mypath="./strings/"):<br>    images = [f for f in listdir(mypath) if isfile(join(mypath, f))]<br>    return images<br> <br>def getImageContent(file, path="./strings"):<br>    path = "{0}/{1}".format(path,file)<br>    with io.open(path, 'rb') as image_file:<br>        content = image_file.read()<br>    return base64.b64encode(content).decode('UTF-8')<br> <br>def poolRoutine(image):<br>    try:<br>        imageData = getImageContent(image)<br>        extract = getExtract(imageData)<br>        extract = extract.encode('utf-8')<br>        print("{0} success: {1}".format(image,extract))<br>    except Exception as e:<br>        print("{0} failed: {1}".format(image,e))<br> <br>images = getImages()<br> <br>for image in images:<br>    poolRoutine(image)<br>``` |

import requests, json, base64, io
import binascii

from multiprocessing import Pool

from os import listdir
from os.path import isfile, join

def getExtract(imageData):
url = "https://content-vision.googleapis.com/v1/images:annotate?alt=json&key="
r = requests.post(url, headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
"Accept": "\*/\*",
"Accept-Language": "en-US,en;q=0.5",
"Accept-Encoding": "gzip, deflate",
"X-Clientdetails": "",
"Authorization": "",
"Content-Type": "application/json",
"X-Requested-With": "XMLHttpRequest",
"X-Javascript-User-Agent": "apix/3.0.0 google-api-javascript-client/1.1.0",
"X-Origin": "https://explorer.apis.google.com",
"X-Referer": "https://explorer.apis.google.com",
"X-Goog-Encode-Response-If-Executable": "base64",
"Origin": "https://content-vision.googleapis.com",
"Referer": "",
"Te": "trailers",
"Connection": "close"
}, json = {
"requests": \[{\
"features": \[{\
"type": "TEXT\_DETECTION"\
}\],\
"image": {\
"content": imageData\
},\
"imageContext": {\
"languageHints": \[\
"en"\
\]\
}\
}\]
})
# json = {"requests":\[{"features":\[{"type":"TEXT\_DETECTION"}\],"image":{"source":{"imageUri":str(imageUrl)}}}\]}
return cleanText(json.loads(r.text)\["responses"\]\[0\]\["fullTextAnnotation"\]\["text"\])


def cleanText(text):
# lower
text = text.lower()
# replacements
replacements = \[\
\[" ", ""\],\
\["\\n", ""\],\
\["o", "0"\],\
\["в","b"\],\
\["с","c"\],\
\["з","3"\],\
\["o","0"\],\
\["о","0"\],\
\["х","x"\]\
\]
for replacement in replacements:
text = text.replace(replacement\[0\], replacement\[1\])
# shift
textStart = text.find("0x")
before = text\[:textStart\]
after = text\[len(before):\]
text = after+before
# ensure no extra newline was added
text = text.replace("\\n", "")
return text

def getImages(mypath="./strings/"):
images = \[f for f in listdir(mypath) if isfile(join(mypath, f))\]
return images

def getImageContent(file, path="./strings"):
path = "{0}/{1}".format(path,file)
with io.open(path, 'rb') as image\_file:
content = image\_file.read()
return base64.b64encode(content).decode('UTF-8')

def poolRoutine(image):
try:
imageData = getImageContent(image)
extract = getExtract(imageData)
extract = extract.encode('utf-8')
print("{0} success: {1}".format(image,extract))
except Exception as e:
print("{0} failed: {1}".format(image,e))

images = getImages()

for image in images:
poolRoutine(image)

From this I was able to get 5198 results out, even though we knew that at least half of them were going to have garbage outputs due to the faulty start rotations. You can view the full list of extracts here:

- [https://gist.github.com/ziot/e7167073e13d3278c15cd26659579ac9](https://gist.github.com/ziot/e7167073e13d3278c15cd26659579ac9) (extract.txt)

And finally, since we assume that these are private keys for the prize wallet, we use the web3 library to go through and see if any of these private keys are a hit against the prize wallet address: **0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A**

|     |     |
| --- | --- |
| ```<br>1<br>2<br>3<br>4<br>5<br>6<br>7<br>8<br>9<br>10<br>11<br>12<br>13<br>14<br>``` | ```<br>import web3<br> <br>def tryPkey(pkey):<br>    account = web3.eth.Account.privateKeyToAccount(pkey)<br>    if account.address.lower() == "0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A".lower():<br>        print("Found: {0}".format(pkey))<br> <br>pkeys = []<br> <br>for pkey in pkeys:<br>    try:<br>        tryPkey(pkey)<br>    except:<br>        continue<br>``` |

import web3

def tryPkey(pkey):
account = web3.eth.Account.privateKeyToAccount(pkey)
if account.address.lower() == "0xeF435c7042965dFA4Cac6be36D1c3CCCDd329A8A".lower():
print("Found: {0}".format(pkey))

pkeys = \[\]

for pkey in pkeys:
try:
tryPkey(pkey)
except:
continue

Running this script ....

```
puzzle@li158-114:/home/puzzles/cr0wn# python3 wallet.py
Found: 0xc3fb42759e4f802a75fb76bbcccd54b9d9751bb30709f7cbe95a21f0339058d1
```

**Boom!** The private key was found for the puzzle prize wallet. This turned out to be the following image:

5pare\_c0ffee\_cephal0p0d.png

![](http://buer.haus/wp-content/uploads/2021/05/5pare_c0ffee_cephal0p0d.png)

The extract:

- [https://etherscan.io/tx/0xbca2f5fa51c656caa8873c29dd0d36c73d927fd111d5455c11a159e69f8cc7a5](https://etherscan.io/tx/0xbca2f5fa51c656caa8873c29dd0d36c73d927fd111d5455c11a159e69f8cc7a5)

Overall this was another fun puzzle from cr0wn that was not without some insane frustrations and hurdles to overcome. This is one of my favorite aspects of a cr0wn puzzle, there is always something new for me to learn and they tend to be a blend of traditional security CTF puzzles and also what we see from the crypto puzzle scene.

Give [@cr0wn\_gh0ul](https://twitter.com/cr0wn_gh0ul) a follow and make sure to check out his future puzzle drops.

Twitter Widget Iframe