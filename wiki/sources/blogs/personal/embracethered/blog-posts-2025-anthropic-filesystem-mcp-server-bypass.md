---
source: embracethered
source_url: https://embracethered.com/blog/posts/2025/anthropic-filesystem-mcp-server-bypass/
title: "Anthropic Filesystem MCP Server: Directory Access Bypass via Improper Path Validation · Embrace The Red"
description: "A few months ago I was looking at the filesystem MCP server from Anthropic. The server allows to give an AI, like Claude Desktop, access to the local …"
---

A few months ago I was looking at the [filesystem MCP server](https://github.com/modelcontextprotocol/servers/blob/main/src/filesystem/README.md) from Anthropic.

The server allows to give an AI, like Claude Desktop, access to the local filesystem to read files or edit them and so forth.

I was curious about access control and in the documentation there is a configuration setting to set `allowedDirectories`, which the AI should be allowed access to:

![filesystem-howto](https://embracethered.com/blog/images/2025/mcp-filesystem-how-to.png)

As you can see the example shows two folders being allowlisted for access.

Since the source code is public, I decided to review it quickly. That’s when I noticed the following vulnerability in the path validation, where it does a `.startsWith` comparison in the `validatePath` function of `index.ts`.

At no point is it enforced that the path is a directory, it only checks that it starts with one of the allowlisted path strings.

This is the code:

![filesystem MCP Server startswith bugstartswith](https://embracethered.com/blog/images/2025/mcp-fileserver-startsWith-bug.png)

This means that if there are sibling directories or files that start with the same name, Claude has access to them.

For instance, consider a folder structure like this:

```
/mnt/finance/data
/mnt/finance/data-archived
```

Now imagine a user wants to give Claude access to only the `/mnt/finance/data` directory, nothing else.

If a user follows the instructions in the `README.md` and adds that path `/mnt/finance/data` to the allowed directories list, **then Claude also has access to the `data-archived` folder**, and any other file starting with `/mnt/finance/data`.

## Video Walkthrough

Episode 3: Anthropic Filesystem MCP Server - Directory Access Bypass via Improper Path Validation - YouTube

Tap to unmute

[Episode 3: Anthropic Filesystem MCP Server - Directory Access Bypass via Improper Path Validation](https://www.youtube.com/watch?v=wqjLqO40org) [Embrace The Red](https://www.youtube.com/channel/UCSwcJXQWE6GWu9IKc0QwO5g)

![thumbnail-image](https://yt3.ggpht.com/imsZDUkdjQsq2tIvoc7CI3lsuuRWDHUg1yPph3eUDnYaT9OWHdEtnXnPzjzcWI891iASf8XQow=s68-c-k-c0x00ffffff-no-rj)

Embrace The Red9.37K subscribers

[Watch on](https://www.youtube.com/watch?v=wqjLqO40org)

## Responsible Disclosure and Fix

I reported this vulnerability to Anthropic on June 1, 2025 and the team highlighted that they are already tracking the issue.

Recently, after the Claude Desktop Extensions came out, I noticed that Anthropic had rewritten large parts of the filesystem server to support the `roots` feature of MCP. That rewrite and updated release also fixed this vulnerability.

Shout out to [Elad Beber, who also had identified this vulnerability, and reported it to Anthropic first](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/).

## Conclusion

This bug highlighted an interesting vulnerability that I consider a typical classical security issue. In the beginning of my career, I worked on filesystem drivers at Microsoft (WinFS and SQL Server), and back then I learned that file system security is actually quite difficult to get right.

My main take-away is that AI system at large, but especially MCP servers, often suffer from “classic” vulnerability types that we sometimes haven’t seen in a long time.

## References

- [Filesystem MCP Server](https://github.com/modelcontextprotocol/servers/blob/main/src/filesystem/README.md)
- [Roots Feature MCP](https://modelcontextprotocol.io/specification/2025-03-26/client/roots)
- [CVE-2025-53109](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-q66q-fx2p-7w4m)
- [EscapeRoute: Breaking the Scope of Anthropic’s Filesystem MCP Server](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/)
- [Month of AI Bugs 2025](https://monthofaibugs.com/)

Subscribe to learn about new posts and occasional updates

Sign up