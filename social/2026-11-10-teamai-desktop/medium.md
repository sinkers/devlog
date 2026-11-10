---
title: "TeamAICoder 0.1.0: one window for many projects and their agents"
subtitle: "An open-source Electron workbench for running many software projects with AI coding agents, now signed and notarised for macOS"
tags: [AI Agents, Electron, Developer Tools, macOS, Open Source]
canonical: https://sinkers.github.io/devlog/2026/11/10/teamai-desktop/
hero: ../../images/2026-11-10-teamai-desktop/hero.png
hero_alt: "The TeamAICoder app in its Build section: a terminal showing the repo's git log on the left and the teamaicoder.com home page in the preview on the right"
---

If you use Claude Code or Codex seriously, you soon have more than one
going. One agent is fixing a bug in this repo, another is writing a spec in
that one, and a third is waiting on you for an answer you haven't noticed.
The agents are fine. Keeping track of them is the problem: which terminal
belongs to which project, where the spec lives, what shipped and what's
stuck.

[TeamAICoder](https://github.com/teamaicoder/teamai-desktop) is the
open-source desktop workbench I'm building in public for exactly that: one
person, many projects, AI coding agents doing most of the building. This
week it became a signed, notarised macOS app, version 0.1.0.

## What it is

One Electron window, organised by stage of a project's life: Ideas, Design,
Plan & Track, Build, Test, Deploy and Operate. Each section has its own
folder, file tree and tab strip. A tab is a file (Markdown or code), a real
terminal, or a web page. Run your agent in a terminal, and keep the spec and
the GitHub board in the next tab.

## What went into 0.1.0

- **Electron 31 to 44.** Not optional: macOS began blocking Electron 31.7.7
  as malware because Apple had revoked its notarisation.
- **CI** on every PR: Jest unit tests, Playwright UI tests driving the real
  app, and an unsigned build on macOS.
- **Chat + Preview**: the agent's terminal on the left, a live browser on the
  right. One shared, persistent sign-in for every preview tab.
- **Projects and session restore**: imported from a folder of Markdown
  files, each repo matched to its local checkout. On relaunch your tabs come
  back, and a terminal that was running `claude` resumes with
  `claude --continue`.
- **Status boards with actions**: a section's pinned status page can open
  Claude Code on an item in the right project folder, or hand a JSON payload
  to your own script and refresh.
- **Open Markdown from Finder**, so the app can be your default `.md` viewer.

The full write-up, with the code, the sign-in workarounds, the release
pipeline and test numbers, and sitekit (the small toolkit that makes the
project's website findable by search engines and AI assistants), is on my
devlog:

https://sinkers.github.io/devlog/2026/11/10/teamai-desktop/

The code is MIT on [GitHub](https://github.com/teamaicoder/teamai-desktop).
