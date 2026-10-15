# devlog

Notes from building things, with links to the code. Published at
https://sinkers.github.io/devlog/.

- `posts/YYYY-MM-DD-<slug>.md`: the article. Frontmatter: `title`, `project`,
  `repos`, `canonical`, `summary`, `hero`, `hero_alt`, `channels`.
- `images/YYYY-MM-DD-<slug>/`: the hero (required, 1200×630) and figures.
- `social/YYYY-MM-DD-<slug>/`: LinkedIn post, thread, short summary, and
  `medium.md` (subtitle, tags, Medium-audience opening). The Medium version is
  built to `/YYYY/MM/DD/<slug>/medium/` for pasting into Medium, which takes no
  new API integrations; it is noindex and canonical to the post.
- `elsewhere/YYYY-MM-DD-<slug>.md`: an article published on another site
  (Medium and so on), listed in the index and linked out. Frontmatter only:
  `title`, `date`, `url`, `venue`, `project`, `summary`, `hero` (an image
  under `images/`, required like every post), optional `words`.
- `/articles/` is the index of everything, by year and by project; each
  article ends with three more and a link to it. `articles.json` is the same
  list as data.
- `build.py`: builds `_site/`. `check.py`: what every post must pass.

Merging to `main` publishes. Drafts arrive as PRs from the dashboard's
promotion pipeline and are reviewed there before they are merged.
