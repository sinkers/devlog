---
title: "TeamAICoder: 11 merged PRs and a notarised 0.1.0 build"
subtitle: "An open-source Electron app for running many projects with AI coding agents: what was merged between 28 October and 9 November 2026, and what is still open"
tags: [AI Agents, Electron, Developer Tools, macOS, Open Source]
canonical: https://sinkers.github.io/devlog/2026/11/10/teamai-desktop/
hero: ../../images/2026-11-10-teamai-desktop/hero.png
hero_alt: "The TeamAICoder app in its Build section: a terminal showing the repo's git log on the left and the teamaicoder.com home page in the preview on the right"
---

[TeamAICoder](https://github.com/teamaicoder/teamai-desktop) is an
open-source Electron app for running many software projects with AI coding
agents, such as Claude Code or Codex, in one window: terminals, files and
web previews grouped by project stage. Between 28 October and 9 November
2026 (Sydney time) 11 PRs were merged into it, and the unit tests went
from 46 to 141. On 10 November I opened #15, which signs and notarises a
0.1.0 build for macOS. As of 11 November it is open, not merged, and there
is no 0.1.0 release on GitHub.

## What was merged

- **Electron 31 to 44** (#3). macOS blocked Electron 31.7.7 as malware
  because its notarisation had been revoked.
- **CI** on every PR (#6): Jest unit tests, Playwright UI tests driving the
  app, and an unsigned build on `macos-latest`. There was none before.
- **Chat + Preview** (#12): a terminal and a browser side by side, with one
  persistent session for every preview tab.
- **Projects and session restore** (#13): projects imported from Markdown
  files, each repo matched to its checkout by its `origin` remote. On
  relaunch a terminal that was running `claude` resumes with
  `claude --continue`.
- **Board actions** (#14): a link on a section's status page opens Claude
  Code on a prompt in the right project folder, or passes a JSON payload to
  a configured command. The prompt has control characters replaced and is
  quoted as one shell argument.
- **Markdown from Finder** (#10).

## Checked

Re-run at each merge commit, unit tests went 46, 50, 64, 130, 141 and UI
tests 42, 49, 52, 62, 77, 84. Three PR descriptions quote counts that
differ from the run, because they were written before the last commits.

## Not done

- #15 is not merged and its release workflow has never run, so the Intel
  build is untested.
- macOS only. Terminal scrollback isn't restored.
- sitekit, which generates the website's `robots.txt`, sitemap and
  `llms.txt`, left the page's existing share image in place, so the
  1200×630 image it made is unused.

The full write-up, with the code, the test chart, the release workflow and
the sign-in workarounds, is on my devlog:

https://sinkers.github.io/devlog/2026/11/10/teamai-desktop/

The code is MIT on [GitHub](https://github.com/teamaicoder/teamai-desktop).
