---
source: spaceraccoon
source_url: https://spaceraccoon.dev/discovering-negative-days-llm-workflows/
title: "Discovering Negative-Days with LLM Workflows | Spaceraccoon's Blog"
published: 2026-02-07T00:00:00+00:00
description: "It’s no longer just about reverse-engineering n-days. You can detect vulnerabilities in open-source repositories before a CVE is published - or even if they’re never published. Here’s how I built an LLM workflow to detect “negative-days” and “never-days”."
---

[Get my new book with No Starch Press "From Day Zero to Zero Day: A Hands-On Guide to Vulnerability Research" here! 🚀](https://nostarch.com/zero-day)

# Discovering Negative-Days with LLM Workflows

Feb 7, 2026
·

1999 words

·

10 minute read


> ICYMI: A demo of the GitHub Action is now available at [https://vulnerabilityspoileralert.com](https://vulnerabilityspoileralert.com/)!

# Time-to-Exploit is Negative [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#time-to-exploit-is-negative)

By now, you’ve probably read Anthropic’s [zero-days](https://red.anthropic.com/2026/zero-days/) blogpost where an “out-of-the-box” Claude Opus 4.6 workflow was used to find 500 vulnerabilities in open-source projects. While I think this is a logical application of LLMs (see my [keynote](https://www.linkedin.com/pulse/storm-here-stay-applications-llms-cybersecurity-tooling-eugene-lim-1qvkc) at the recent Association for the Advancement of Artificial Intelligence workshop on Artificial Intelligence for Cyber Security), it was this paragraph in the blogpost that interested me the most:

> At the same time, existing disclosure norms will need to evolve. Industry-standard 90-day windows may not hold up against the speed and volume of LLM-discovered bugs, and the industry will need workflows that can keep pace.

This had been a problem that had been bothering me for a while. Open-source projects are inundated with LLM-generated reports precisely because of how accessible they are to scanners, and it’s trivial to run a decent code-oriented model on them. That aside, the open-source security disclosure process is uneven and may not be fully equipped to deal with the flood of reports - both valid and invalid ones.

However, there’s a far more logical outcome that’s already well underway - the sharp drop in time to exploit CVEs into the negatives (as per Mandiant’s latest reports), thanks to the increase in zero-days and speed of reverse-engineering n-days from the moment a CVE is published. For open-source projects, the risk is even greater because security patches are public.

## Negative-Days [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#negative-days)

Take the case of the React2Shell vulnerability. The commit patching the vulnerability (in a now-public [forked repo](https://github.com/sebmarkbage/react/commits/patchreplyserver/)) was made on 3 December 10.00 PM (GMT+8), the pull request at 11.38 PM (pull requests on public GitHub repos cannot be made private), and the [CVE was published](https://cveawg.mitre.org/api/cve/CVE-2025-55182) at 11.40 PM. The MITRE CVE repository which you can monitor for threat intel feeds [publishes on an hourly cadence](https://github.com/CVEProject/cvelistV5/releases), so most feeds only really got the word out at midnight. So for a critical issue like this, you could still have gotten an early warning by about 2 hours before CVE intel feeds just by monitoring GitHub repository activity.

This is for the ideal case of a well-managed vulnerability. This was tightly-run and coordinated by the Meta security team, since it was initially reported to their bug bounty program. However, there are many other major open-source projects that may have less-than-ideal disclosure processes which anyone operating in the vulnerability research space would be familiar with.

## Never-Days [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#never-days)

This is even before considering “never-days” - in other words, vulnerabilities that are patched (sometimes unknowingly), but never assigned a CVE. Without a CVE assigned, their users don’t know they are on a vulnerable version and aren’t motivated to patch. Things can get messy especially after an initial large CVE like React2Shell is followed up by multiple minor CVEs and security hardening improvements, muddling the waters.

# Building the Workflow [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#building-the-workflow)

I decided to build a threat intelligence workflow using LLMs. While there’s a lot of excitement around agents, I think Anthropic’s [own advice](https://www.anthropic.com/engineering/building-effective-agents) on when not to use agents is pretty sensible:

> When building applications with LLMs, we recommend finding the simplest solution possible, and only increasing complexity when needed. This might mean not building agentic systems at all. Agentic systems often trade latency and cost for better task performance, and you should consider when this tradeoff makes sense.
>
> When more complexity is warranted, workflows offer predictability and consistency for well-defined tasks, whereas agents are the better option when flexibility and model-driven decision-making are needed at scale. For many applications, however, optimizing single LLM calls with retrieval and in-context examples is usually enough.

With that in mind, I was able to mostly one-shot a simple GitHub action with this instruction:

> Build a GitHub Action cron job that continuously monitors open-source repositories defined by the user. It checks all commits since the last run, passes them to Claude API to analyse whether it appears to be patching a vulnerabilities. If it does, it should create an issue.

The workflow used a `state.json` to track the last-checked commit hash to avoid duplicate work, making it fairly efficient to run.

The initial approach used `git diff` and fed the output to Claude to analyze:

```fallback
Analyze this commit carefully. Look for signs that this commit is fixing a security vulnerability, such as:
- Input validation being added
- Sanitization of user input
- Fixes for injection vulnerabilities (SQL, command, XSS, etc.)
- Authentication or authorization fixes
- Buffer overflow or memory safety fixes
- Cryptographic improvements
- Path traversal fixes
- Rate limiting or DoS protections
- Security-related keywords in commit message (CVE, security, vulnerability, fix, patch, etc.)
```

However, this created a couple false positives and negatives. I decided to add more context beyond just the code diff.

## Tuning Context [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#tuning-context)

Commit messages are helpful but short. Actually the pull requests can provide a lot more information about what the commit is about, including any further comments. The prompt was tweaked to:

```fallback
Analyze this commit carefully. Look for signs that this commit is fixing a security vulnerability, such as:
- Input validation being added
- Sanitization of user input
- Fixes for injection vulnerabilities (SQL, command, XSS, etc.)
- Authentication or authorization fixes
- Buffer overflow or memory safety fixes
- Cryptographic improvements
- Path traversal fixes
- Rate limiting or DoS protections
- Security-related keywords in commit message (CVE, security, vulnerability, fix, patch, etc.)
- Pull request labels indicating security (e.g., "security", "vulnerability", "CVE")
- Pull request description mentioning security issues, CVE identifiers, or vulnerability details
```

In addition, the workflow would use the GitHub `listPullRequestsAssociatedWithCommit` API to fetch associated pull requests and its contents and add it to the prompt’s context. This improved the accuracy of findings.

However, there was still a lot of false positives, including “bugs-but-not-really-exploitable-vulnerabilities”. This time, I tuned the context further:

```fallback
Analyze the following commit and determine if it is patching an EXPLOITABLE security vulnerability.

...

Your task is to identify commits that patch REAL, EXPLOITABLE security vulnerabilities. You must be able to demonstrate the vulnerability with a concrete proof of concept.

Only flag a commit as a vulnerability patch if ALL of the following are true:
1. The code BEFORE the patch had a clear security flaw
2. You can write a specific proof of concept showing how to exploit it
3. The vulnerability has real security impact (not just theoretical)

DO NOT flag:
- General code quality improvements or defensive coding practices
- Adding validation that prevents edge cases but has no security impact
- Performance fixes or refactoring
- Error handling improvements without security implications
- Changes that only affect internal/trusted code paths
- Commits where you cannot write a concrete exploit PoC
```

## Fixing the JSON Output with Prefill Technique and Role [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#fixing-the-json-output-with-prefill-technique-and-role)

While the Action was chugging along, I still got occasional failures because Claude got a bit too talky and failed to output a pure-JSON output despite the prompt saying:

```fallback
Respond with a JSON object (and nothing else) in the following format:
{
  "isVulnerabilityPatch": boolean,
  "vulnerabilityType": string | null,
  "severity": "Critical" | "High" | "Medium" | "Low" | null,
  "description": string | null,
  "affectedCode": string | null,
  "proofOfConcept": string | null
}
```

This created parsing errors due to output like:

```mysql
Failed to parse Claude response: Looking at this commit, I can see it's removing the `enableHalt` feature flag and associated conditional logic from React's server-side rendering code. This appears to be a cleanup commit after a feature has shipped, not a security vulnerability patch.

Let me analyze the key changes:

1. Removes `@gate enableHalt` comments from tests
2. Removes conditional logic that checked `gate(flags => flags.enableHalt)`
3. Simplifies code paths by removing the flag-dependent behavior
4. Updates expectations in tests to reflect the new unified behavior

The diff shows that before this change, there were two different code paths depending on whether `enableHalt` was enabled:
- With `enableHalt`: certain operations would resolve with specific values (like `postponed: null`)
- Without `enableHalt`: the same operations might reject with errors or behave differently
...
```

To fix this, I used the prefill technique (not sure if this is still recommended, but it worked) and setting the role:

```fallback
  const response = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1024,
    messages: [\
      {\
        role: "user",\
        content: prompt,\
      },\
      {\
        role: "assistant",\
        content: "{",\
      },\
    ],
  });
```

This seemed to address the consistent output parsing failures.

# Results [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#results)

Doing a quick backtest, I was able to detect the React vulnerabilities, although I have some doubts about whether this is simply because it’s now part of the known context. What was more interesting was that I found a “never-day” in a canary release of `@next/codemod` (ironically, in a feature used to generated agent-friendly documentation):

> ## Potential Security Vulnerability Detected [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#potential-security-vulnerability-detected)
>
> **Repository:** [vercel/next.js](https://github.com/vercel/next.js) **Commit:** [b08049c](https://github.com/vercel/next.js/commit/b08049ccf54ecd95033d89f82b1261e4142a2dbc) **Author:** Jude Gao
> **Date:** 2026-02-03T18:21:05Z
>
> ### Commit Message [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#commit-message)
>
> ```mysql
> [Codemod] Fix agents-md on Windows (#89319)
>
> Fixes #89240
>
> The `agents-md` codemod failed on Windows because it assumed forward
> slashes in file paths. This caused the doc tree builder to skip files,
> resulting in an empty index being injected into `AGENTS.md`.
>
> The path handling code used string operations like `.split('/')` and
> `.endsWith('/index.mdx')` which don't work with Windows backslashes. Now
> uses regex patterns that match both separators: `/[/\\]/` for splitting
> and `!/[/\\]index\.mdx$/` for filtering. Also normalizes all paths to
> forward slashes in the output.
>
> While here, switched from `execSync` to `execa` for git commands. This
> is the pattern already used elsewhere in the codemod package
> (`upgrade.ts`, `handle-package.ts`) and passes arguments as an array
> instead of shell string interpolation.
>
> Tests were replaced with e2e tests that run the full CLI and include a
> cross-platform path normalization test case.
> ```
>
> ### Pull Request [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#pull-request)
>
> **PR:** [#89319 - \[Codemod\] Fix agents-md on Windows](https://github.com/vercel/next.js/pull/89319) **Labels:** type: next, created-by: Next.js team
>
> **Description:**
> Fixes #89240
>
> The `agents-md` codemod failed on Windows because it assumed forward slashes in file paths. This caused the doc tree builder to skip files, resulting in an empty index being injected into `AGENTS.md`.
>
> The path handling code used string operations like `.split('/')` and `.endsWith('/index.mdx')` which don’t work with Windows backslashes. Now uses regex patterns that match both separators: `/[/\\]/` for splitting and `!/[/\\]index\.mdx$/` for filtering. Also normalizes all paths to …
>
> ### Analysis [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#analysis)
>
> **Vulnerability Type:** Command Injection
> **Severity:** Medium
>
> ### Description [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#description)
>
> The commit fixes a potential command injection vulnerability by replacing shell string interpolation with parameterized command execution. The code previously used execSync with string concatenation for git commands, which could allow command injection if file paths or other inputs contained shell metacharacters. The fix switches to execa which passes arguments as an array, preventing shell interpretation of malicious input.
>
> ### Affected Code [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#affected-code)
>
> ```fallback
> - execSync(`git clone ${repoUrl} ${cloneDir}`)
> + await execa('git', ['clone', repoUrl, cloneDir])
> ```
>
> * * *
>
> _This issue was automatically created by the Vulnerability Spoiler Alert action._ _Detected at: 2026-02-04T01:38:15.727Z_

One important point is that the Affected Code section was actually hallucinated; there wasn’t that line of code, but there were similar enough ones that used `execSync` that were exploitable.

Based on this report, I went on to verify the vulnerability and wrote my own proof of concept. Assuming a trojanised cloned repository with this `package.json`:

```fallback
{
  "name": "agentsmd-poc",
  "version": "1.0.0",
  "description": "",
  "license": "ISC",
  "author": "",
  "type": "commonjs",
  "main": "index.js",
  "devDependencies": {
    "next": "$(touch /tmp/testpoc)"
  },
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  }
}
```

Running `npx @next/codemod@v16.2.0-canary.24 agents-mod --output CLAUDE.md` would trigger the command injection and create `/tmp/testpoc` on the device.

While this was obviously not a serious canary release and didn’t really necessitate a CVE, it did highlight the viability of this approach.

# Next Steps [🔗](https://spaceraccoon.dev/discovering-negative-days-llm-workflows/\#next-steps)

With this little experiment, I validated a critical threat intelligence workflow - we need to be monitoring for open-source vulnerabilities **before** (or if ever) a CVE is published. Threat actors are 100% already doing this in some form to quickly weaponise and exploit open-source issues. To emphasise the point: **This is already happening.**

In the same way, open-source projects need to really tighten up their security patch and disclosure processes. I’m not sure why GitHub doesn’t allow private pull requests on public repository, but that seems to be something that would help their [recommendations](https://docs.github.com/en/code-security/concepts/vulnerability-reporting-and-management/about-coordinated-disclosure-of-security-vulnerabilities) on coordinated disclosure.

Every serious security engineering team should be updating their threat intelligence workflows for this “precognition” capability. I’ve open-sourced the GitHub Action, but the barrier to entry to simply building your own variant is virtually zero. You can customise it to run your own models, create Slack alerts instead of GitHub Issues, and so on.

However, if you just want to take this for a spin, I’ve open-sourced (lol) the action at [https://github.com/spaceraccoon/vulnerability-spoiler-alert-action](https://github.com/spaceraccoon/vulnerability-spoiler-alert-action) (or [GitHub Marketplace](https://github.com/marketplace/actions/vulnerability-spoiler-alert)) \- check it out and let me know if anything breaks. I’d really rather you write your own action than introduce a third-party supply chain risk in your CI workflows, but I’m also interested to see if anyone wants to help develop this concept further in the open.

There’s also the last mile - I’ll be experimenting with subagents to validate the proof of concept exploits to fully close the loop, but this is already a deep area of focus for both threat actors and security teams alike.

[appsec](https://spaceraccoon.dev/tags/appsec) [dev](https://spaceraccoon.dev/tags/dev)