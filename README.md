# devlog

Notes from building things, with links to the code. Published at
https://sinkers.github.io/devlog/.

- `posts/YYYY-MM-DD-<slug>.md`: the article. Frontmatter: `title`, `project`,
  `repos`, `canonical`, `summary`, `hero`, `hero_alt`, `channels`.
- `images/YYYY-MM-DD-<slug>/`: the hero (required, 1200×630) and figures.
- `social/YYYY-MM-DD-<slug>/`: LinkedIn post, thread, short summary.
- `build.py`: builds `_site/`. `check.py`: what every post must pass.

Merging to `main` publishes. Drafts arrive as PRs from the dashboard's
promotion pipeline and are reviewed there before they are merged.
