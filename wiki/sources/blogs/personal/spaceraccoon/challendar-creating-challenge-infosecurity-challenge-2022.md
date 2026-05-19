---
source: spaceraccoon
source_url: https://spaceraccoon.dev/challendar-creating-challenge-infosecurity-challenge-2022/
title: "Challendar: Creating a Challenge for The Infosecurity Challenge 2022 | Spaceraccoon's Blog"
published: 2022-09-19T00:40:00+00:00
description: "Although I do not actively participate in CTFs, I enjoy creating challenges for them as it forces me to learn by doing. Creating a good CTF challenge is an art, not a science. As the winner of last year’s $30k The InfoSecurity Challenge (TISC), I decided to contribute a challenge instead this year."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Challendar: Creating a Challenge for The Infosecurity Challenge 2022

Sep 19, 2022
·

2517 words

·

12 minute read


Although I do not actively participate in CTFs, I enjoy creating CTF challenges as it forces me to learn by doing. Creating a good CTF challenge is an art, not a science. As the winner of [last year’s $30k The InfoSecurity Challenge (TISC)](https://spaceraccoon.dev/the-infosecurity-challenge-2021-full-writeup-battle-royale-for-30k/), I decided to contribute a challenge this year.

You can check out [the challenge on my GitHub](https://github.com/spaceraccoon/Challendar-TISC-2022-Challenge-7).

# Design Principles [🔗](https://spaceraccoon.dev/challendar-creating-challenge-infosecurity-challenge-2022/\#design-principles)

1. **Educational**: In my experience, some of the best CTF challenges are those that teach you something. Whether it’s an interesting encryption protocol or weird Content Security Policy handling, it always feels satisfying to learn something new to make all that time and pain worth it. For my challenge, I centered it around the [CalDAV](https://en.wikipedia.org/wiki/CalDAV) protocol, an under-researched superset of WEBDAV (itself a superset of HTTP) that is used everywhere, from the default iOS calendar to IoT devices. At DEF CON 30, I presented on the [iCalendar](https://spaceraccoon.dev/exploiting-icalendar-properties-enterprise-applications/) file format but did not disclose my other research into its corresponding communication protocol.
2. **Realistic**: Ultimately, all CTF challenges apply some level of contrivance, but I tried to keep it as realistic as possible by utilizing real open-souce code. Furthermore, I tried to ensure that the exploit vector was logical and ultimately explainable to most people. I wanted to recreate the day-to-day experience of web vulnerability research through code review.
3. **Transparent**: Black box challenges tend to rely on “difficulty by obscurity” which can be frustrating. I built a white box challenge where all the relevant code was available to the participant.
4. **Challenging**: Web tends to be one of the easiest CTF challenge categories because web vulnerabilities are well-known and fairly easy to exploit. I hoped to disrupt this assumption for TISC. Although the participant possessed the source code, I forced them to go the extra mile by reading RFCs and hopefully building unique payloads.

Finally, and most importantly, I wanted the challenge to be… _eleganto_.

![Elegance Spy X Family](https://spaceraccoon.dev/images/24/elegance-spy-x-family.gif)

No brute-forcing. No guessing. No blind exploits.

And a reverse shell.

# The Almost-Vulnerability [🔗](https://spaceraccoon.dev/challendar-creating-challenge-infosecurity-challenge-2022/\#the-almost-vulnerability)

One of the most painful parts of vulnerability research is discovering a potential exploit, only to realize that due to sanitization, validation, or some kind of transformation, the path from attacker-controlled input to the vulnerable code is blocked. These almost-vulnerabilities dangle tantalizingly out of reach, keeping you up at night.

An almost-vunerability (also known as “not a vulnerability”) exists in [Radicale](https://github.com/Kozea/Radicale), one of the most popular open-source CalDAV servers. The main job of a CalDAV server is to handle iCalendar files. To do so, it uses HTTP methods like POST, PUT, DELETE as well as CalDAV/WebDAV-specific methods like MKCALENDAR, REPORT, PROPFIND, MOVE, COPY to read and write these files. Each collection of iCalendar file is represented as a folder in storage, corresponding to a user or calendar.

In addition to iCalendar files, Radicale also relies on the standard library `pickle` to store calendar metadata such as history in serialized pickle files. This is a [well-known code execution vector](https://book.hacktricks.xyz/pentesting-web/deserialization#pickle) because when a function calls `pickle.load()` to deserialize a pickle, it also calls the `__reduce__` function of the class stored in the pickle file, which can be easily modified by an attacker.

Radicale uses `pickle.load()` in [three different locations](https://github.com/Kozea/Radicale/search?q=pickle.load), one of which is [`storage/multifilesystem/sync.py`](https://github.com/Kozea/Radicale/blob/master/radicale/storage/multifilesystem/sync.py):

```python
class CollectionPartSync(CollectionPartCache, CollectionPartHistory,
                         CollectionBase):
    def sync(self, old_token: str = "") -> Tuple[str, Iterable[str]]:
        # ...
        if old_token_name:
            # load the old token state
            old_token_path = os.path.join(token_folder, old_token_name)
            try:
                # Race: Another process might have deleted the file.
                with open(old_token_path, "rb") as f:
                    old_state = pickle.load(f)
```

In order to reach this line of code, the server must call the `sync` method in the `CollectionPartSync` class. This call occurs in `app/report.py`:

```python
def xml_report(base_prefix: str, path: str, xml_request: Optional[ET.Element],
               collection: storage.BaseCollection, encoding: str,
               unlock_storage_fn: Callable[[], None]
               ) -> Tuple[int, ET.Element]:
    """Read and answer REPORT requests.

    Read rfc3253-3.6 for info.

    """
    # ...
    elif root.tag == xmlutils.make_clark("D:sync-collection"):
        old_sync_token_element = root.find(
            xmlutils.make_clark("D:sync-token"))
        old_sync_token = ""
        if old_sync_token_element is not None and old_sync_token_element.text:
            old_sync_token = old_sync_token_element.text.strip()
        logger.debug("Client provided sync token: %r", old_sync_token)
        try:
            sync_token, names = collection.sync(old_sync_token)
```

So by sending a `REPORT` request with an XML body that includes `D:sync-collection` as the root along with a `D:sync-token` child element, Radicale will reach the vulnerable unpickle function. Looking back at `storage/multifilesystem/sync.py`, we see that the `sync-token` value must meet a few more conditions:

```python
class CollectionPartSync(CollectionPartCache, CollectionPartHistory,
                         CollectionBase):
    def sync(self, old_token: str = "") -> Tuple[str, Iterable[str]]:
        # ...
        def check_token_name(token_name: str) -> bool:
            if len(token_name) != 64:
                return False
            for c in token_name:
                if c not in "0123456789abcdef":
                    return False
            return True

        old_token_name = ""
        if old_token:
            # Extract the token name from the sync token
            if not old_token.startswith("http://radicale.org/ns/sync/"):
                raise ValueError("Malformed token: %r" % old_token)
            old_token_name = old_token[len("http://radicale.org/ns/sync/"):]
            if not check_token_name(old_token_name):
                raise ValueError("Malformed token: %r" % old_token)
```

These are fairly simple string-based checks (`http://radicale.org/ns/sync/<64 CHARACTER LONG LOWERCASE HEX STRING>`). However, another problem lies in the path from which the server reads the pickle file:

```python
        token_folder = os.path.join(self._filesystem_path,
                                    ".Radicale.cache", "sync-token")
        token_path = os.path.join(token_folder, token_name)
        old_state = {}
        if old_token_name:
            # load the old token state
            old_token_path = os.path.join(token_folder, old_token_name)
            try:
                # Race: Another process might have deleted the file.
                with open(old_token_path, "rb") as f:
                    old_state = pickle.load(f)
```

The file must exist in `<RADICALE ROOT FOLDER>/<USERNAME>/<CALENDAR NAME>/.Radicale.cache/sync-token/<VALID TOKEN NAME>`. At first, this appears writable because a user can write to any location in their collections using the `PUT` method. Unfortunately, Radicale employs [several sanitization and validation methods](https://github.com/Kozea/Radicale/blob/master/radicale/pathutils.py#L211) to avoid such a scenario:

```python
def sanitize_path(path: str) -> str:
    """Make path absolute with leading slash to prevent access to other data.

    Preserve potential trailing slash.

    """
    trailing_slash = "/" if path.endswith("/") else ""
    path = posixpath.normpath(path)
    new_path = "/"
    for part in path.split("/"):
        if not is_safe_path_component(part):
            continue
        new_path = posixpath.join(new_path, part)
    trailing_slash = "" if new_path.endswith("/") else trailing_slash
    return new_path + trailing_slash

def is_safe_path_component(path: str) -> bool:
    """Check if path is a single component of a path.

    Check that the path is safe to join too.

    """
    return bool(path) and "/" not in path and path not in (".", "..")

def is_safe_filesystem_path_component(path: str) -> bool:
    """Check if path is a single component of a local and posix filesystem
       path.

    Check that the path is safe to join too.

    """
    return (
        bool(path) and not os.path.splitdrive(path)[0] and
        (sys.platform != "win32" or ":" not in path) and  # Block NTFS-ADS
        not os.path.split(path)[0] and path not in (os.curdir, os.pardir) and
        not path.startswith(".") and not path.endswith("~") and
        is_safe_path_component(path))
```

In particular, all the write-related methods call `is_safe_filesystem_path_component` on each path segment, which checks that `not path.startswith(".")`, thereby blocking writes to the `.Radicale.cache` folder. Sad!

# With a Little Help from My Friends [🔗](https://spaceraccoon.dev/challendar-creating-challenge-infosecurity-challenge-2022/\#with-a-little-help-from-my-friends)

Thankfully, this was a CTF challenge, so I could create a scenario to make this almost-vulnerability exploitable. To keep with the CalDAV theme, I wrote a “beta” CalDAV server based on the Golang extended standard library `golang.org/x/net/webdav`. I crafted a story that the clueless developer was attempting to build a backward-compatible replacement for Radicale by using the same root collections folder as the Radicale server. I also added the same authorization checks as Radicale but excluded the crucial `not path.startswith(".")` check.

```go
func checkIsAuthorized(req *http.Request) error {
	// should already be authorized
	username, _, _ := req.BasicAuth()
	urlParts := strings.Split(req.URL.Path, "/")
	// users can only access their own resources
	if username != urlParts[1] || len(urlParts) > 4 {
		return ErrNotExist
	}
	return nil
}

func main() {
	// Backward-compatible with with our current Radicale files
	passwords, _ := ParseHtpasswdFile("/etc/radicale/users")
	fs := &webdav.Handler{
		FileSystem: webdav.Dir("/var/lib/radicale/collections/collection-root"),
		LockSystem: webdav.NewMemLS(),
	}

	http.HandleFunc("/", func(w http.ResponseWriter, req *http.Request) {
		username, password, ok := req.BasicAuth()
		if !ok {
			w.Header().Set("WWW-Authenticate", `Basic realm="CalDavServer - Password Required"`)
			w.WriteHeader(http.StatusUnauthorized)
			return
		}

		err := bcrypt.CompareHashAndPassword([]byte(passwords[username]), []byte(password))
		if err != nil {
			http.Error(w, "Access to the requested resource forbidden.", http.StatusUnauthorized)
			return
		}

		err = checkIsAuthorized(req)
		if err != nil {
			http.Error(w, "Access to the requested resource forbidden.", http.StatusUnauthorized)
			return
		}

		switch req.Method {
		// To update to CalDAV RFC... been taking too many coffee breaks
		case "PROPFIND", "PROPPATCH", "MKCALENDAR", "MKCOL", "REPORT":
			http.Error(w, "Method not implemented.", http.StatusNotImplemented)
			return
		}

		fs.ServeHTTP(w, req)
	})
	http.ListenAndServe(":4000", nil)

}
```

Unfortunately, this lazy developer hadn’t even written the CalDAV specific methods yet! However, they created a simple authorization check that also inadvertently prevented writing directly to `<RADICALE ROOT FOLDER>/<USERNAME>/<CALENDAR NAME>/.Radicale.cache/sync-token/<VALID TOKEN NAME>`. To do so, they would need to send a `PUT /<USERNAME>/<CALENDAR NAME>/.Radicale.cache/sync-token/<VALID TOKEN NAME>` request, which would exceed 4 URL path segments and fail `checkIsAuthorized`.

However, all was not lost. WebDAV also supports the `COPY` and `MOVE` methods, which move a file to a location specified in the `Destination` header instead of the request path. As such, the attacker could first write to `<RADICALE ROOT FOLDER>/<USERNAME>/<CALENDAR NAME>/<VALID TOKEN NAME>`, then copy/move it to the final payload destination.

All in all, the solution only needed 4 web requests to achieve RCE:

```python
# generate sync-token folder
session.request("REPORT", RADICALE_URL+"/"+USERNAME+"/default", data=generate_sync_token)

# upload payload
session.put(DEV_SERVER_URL+"/"+USERNAME+"/payload", data=pickle.dumps(RCE()))

# move payload
session.request("MOVE", DEV_SERVER_URL+"/"+USERNAME+"/payload", headers={"Destination":DEV_SERVER_URL+"/"+USERNAME+"/default/.Radicale.cache/sync-token/"+SYNC_TOKEN_NAME})

# execute payload
session.request("REPORT", RADICALE_URL+"/"+USERNAME+"/default", data=execute_payload)
```

# Things Fall Apart [🔗](https://spaceraccoon.dev/challendar-creating-challenge-infosecurity-challenge-2022/\#things-fall-apart)

With the basic scenario working, I fleshed out the rest of the challenge. To provide the calendar credentials and URLs to the participants, I created a simple Thunderbird backup that was synced to the Radicale and development calendar servers. This served more to deliver information than to pose any kind of challenge; a tool like [`firepwd`](https://github.com/lclevy/firepwd) could easily extract this information:

```console
participant@ctf:~/firepwd$ python3 firepwd.py -d backup/
decrypting login/password pairs
http://calendarserver:<PORT OF RADICALE SERVER>:b'jrarj',b'H3110fr13nD'
http://calendarserver:<PORT OF DEVELOPMENT SERVER>:b'jrarj',b'H3110fr13nD'
```

The Radicale and development calendar severs ran on separate ports. A participant could easily fingerprint the Radicale server because by default Radicale’s index redirects to `/.web` which returns the message `Radicale works!`. From there, they could look up the source code of Radicale on GitHub. The challenge provided the source code of the development calendar to participants and did not need any fingerprinting.

With that, I wrapped it all up in a simple Dockerfile and sent it for playtesting!

```markdown
# Challendar

## Introduction

PALINDROME suffers from Not Invented Here symdrome. They assigned an intern to build a replacement for their current calendar server! Luckily we managed to intercept their backups. Can you break in?

## Files

`caldavserver.go`
`backup.zip`
```

Although the feedback was good, I found out that there were a few unintended solutions. Remember how Radicale used `pickle.load()` in three different locations? Other than `storage/multifilesystem/sync.py`, they also occurred in `storage/multifilesystem/cache.py` and `storage/multifilesystem/history.py`. As it turned out, after writing to the files used in those two other methods, an attacker could trigger the payload by simply issuing a `GET` request to the corresponding calendar items. Radicale would attempt to load the items’ cache and history, deserializing the pickle files. I wanted to restrict the participants to the `sync.py` code path because it required them to use the `REPORT` method and craft an XML body that passed all the validation checks.

But how could I block these unintended solutions? I could alter the source code of Radicale, but this would affect the **Transparent** design principle and confuse the participants about whether they were actually dealing with a Radicale server. I could also block writing to specific folders e.g. `.Radicale.cache` in the development calendar code for `MOVE` and `COPY`, but that would make it too obvious.

After debating several workarounds, I ended up compromising a little by setting up a `nginx` reverse proxy that sat in front of the Radicale server. This `nginx` instance blocked the `GET` method along with several others (so as to not make it obvious that I only wanted to block `GET`) under the pretext that it was in development:

```nginx
        location /radicale/ {
            if ($request_method ~ ^(GET|PATCH|TRACE)$ ) {
                return 405 "Method temporarily disabled during development";
            }

            if ($request_method ~ ^(MOVE|DELETE|PROPPATCH|PUT|MKCALENDAR|COPY|POST)$ ) {
                return 403 "Read-only access during development";
            }

            proxy_pass        http://localhost:5232/;
            proxy_set_header  X-Script-Name /radicale;
            proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header  Host $http_host;
            proxy_pass_header Authorization;
        }
```

While this was a painful decision that weakened the **Transparent** design principle, I hoped that the impact was limited because a participant could easily enumerate which methods were blocked.

This change also made it more **Challenging**. A participant could not use a CalDAV client to browse the Radicale server due to the blocked methods. Instead, they had to manually craft a `PROPFIND` request (preferably with `Depth` header set to `infinity`) to retrieve the user’s writable calendars.

![PROPFIND Request and Response](https://spaceraccoon.dev/images/24/propfind-request-response.png)

For this challenge, that was `jrarj/default`.

Another issue that came up during playtesting was possible vandalism or leaked solutions because the files created by participants were visible to others. If a participant got RCE, they would be running as `root`, allowing them to overwrite any file. To prevent this, I used a `radicale` limited user and a cleanup script that ran in 1-minute intervals.

# Everyone Has a Plan Until They Get Punched in the Mouth [🔗](https://spaceraccoon.dev/challendar-creating-challenge-infosecurity-challenge-2022/\#everyone-has-a-plan-until-they-get-punched-in-the-mouth)

Anyone who has organized a CTF will understand how difficult it is to accurately estimate the difficulty of a challenge. Although I originally pitched the challenge at around 6 hours, after playtesting it was estimated to take around 1-2 days. However, during the actual competition, no one had solved it more than 7 days after the first participant had reached my challenge. Since TISC required participants to solve my Level 7 challenge to proceed to the prize money challenges, I began releasing hints in collaboration with the organizers. In total, 3 hints were released over several days.

![TISC Progression](https://spaceraccoon.dev/images/24/tisc-progression.png)

1. `Approach this as a code review challenge. We have also provided the reverse proxy configuration for one of the servers.`: This was meant to remove any further ambiguity by providing the `nginx` configuration. At this point, all relevant code for the challenge was avialable to the participant. The first sentence also guided participants to avoid guessing and use a white box approach.
2. `1. You can (PROP)FIND what you need in the RFC. 2. Open(source) your mind to the possibilities. 3. Look at the other HTTP methods you can use.`: This was meant to point participants towards the alternative CalDAV methods as well as the Radicale code.
3. `The two servers live in the same place. Why? Maybe you need the help of one server to exploit the other. Aim for code execution. If one is too small to do anything, take a closer look at the bigger codebase`: This was meant to narrow the search space greatly for participants to find the vulnerability. It was getting close to the end of TISC and I wanted participants to win some prize money!

After the third hint, the first participant solved it the next day and others soon followed.

Due to the long delay, I was worried that my challenge design was unexpectedly guessy or broken. I regularly checked that the solution was working. Fortunately, after TISC concluded I received good feedback that the challenge was “the good kind of stuck” because the path to the solution made sense. However, I wished I had tweaked the design more to avoid needing hints.

Designing the challenge also showed the importance of playtesting and balancing various design principles. Balancing **Challenging** and **Transparent** required some compromises but also forced me to build a more elegant (in my humble opinion!) challenge.

Ultimately, I hope the participants learned something useful about an ubiquitous but legacy standard. Furthermore, I hope they gained insights into the process of code review. [Congratulations to the winners!](https://www.csit.gov.sg/events/tisc/tisc-2022-summary)

[dev](https://spaceraccoon.dev/tags/dev) [web](https://spaceraccoon.dev/tags/web) [code review](https://spaceraccoon.dev/tags/code-review)