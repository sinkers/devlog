"""Build the devlog: posts/*.md -> _site/, for GitHub Pages.

    pip install markdown && python build.py

One post is posts/YYYY-MM-DD-<slug>.md with frontmatter; it is served at
/YYYY/MM/DD/<slug>/. Images live in images/<post>/ and the post refers to them
as ../images/<post>/x.png, so the markdown previews on GitHub too. Every post
has a hero, which is also its og:image: links to it preview with a picture
wherever they are pasted.

A post with social/<post>/medium.md also gets /YYYY/MM/DD/<slug>/medium/: the
Medium version laid out to be copied into Medium's editor in one go (Medium
takes no new API integrations). It is noindex with its canonical pointing at
the post, so it never competes with the original.

/articles/ is the index of everything: devlog posts, and articles published
elsewhere (Medium and so on), each listed by a small elsewhere/<date>-<slug>.md
holding only frontmatter: title, date, url, venue, project, summary, hero.
articles.json is the same index as data.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

import markdown

SITE = "https://sinkers.github.io/devlog"
BASE = "/devlog"
NAME = "devlog"
AUTHOR = "Andrew Sinclair"
TAGLINE = "Notes from building things, with links to the code."

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)
e = html.escape


def frontmatter(text: str) -> tuple[dict, str]:
    m = FM.match(text)
    if not m:
        return {}, text
    out: dict = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            out[k.strip()] = [x.strip().strip("\"'") for x in v[1:-1].split(",") if x.strip()]
            continue
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        out[k.strip()] = v
    return out, text[m.end():]


def figures(html_: str) -> str:
    """An image paragraph followed by an italic-only paragraph becomes
    <figure> + <figcaption>. Medium's importer and editor both keep that as
    an image with its caption; two loose paragraphs they do not."""
    html_ = re.sub(r'<p>(<img [^>]+>)</p>\s*<p><em>(.*?)</em></p>',
                   r"<figure>\1<figcaption>\2</figcaption></figure>", html_, flags=re.S)
    return re.sub(r"<p>(<img [^>]+>)</p>", r"<figure>\1</figure>", html_)


def md(text: str) -> str:
    return figures(markdown.markdown(text, extensions=["fenced_code", "tables", "sane_lists"]))


def load_posts() -> list[dict]:
    posts = []
    for f in sorted((ROOT / "posts").glob("*.md"), reverse=True):
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md$", f.name)
        if not m:
            continue
        y, mo, d, slug = m.groups()
        fm, body = frontmatter(f.read_text(encoding="utf-8"))
        body = re.sub(r"\A\s*# .*\n+", "", body)          # the title is in the template
        body = body.replace("](../images/", f"]({BASE}/images/")
        path = f"{y}/{mo}/{d}/{slug}/"
        hero = fm.get("hero", "")
        medium = None
        mf = ROOT / "social" / f.stem / "medium.md"
        if mf.exists():
            mfm, mbody = frontmatter(mf.read_text(encoding="utf-8"))
            # Absolute image URLs: pasted into Medium, relative ones break.
            mbody = mbody.replace("](../../images/", f"]({SITE}/images/")
            medium = {**mfm, "html": md(mbody),
                      "hero_url": mfm.get("hero", "").replace("../../images/", f"{SITE}/images/")}
        posts.append({
            **fm,
            "date": datetime(int(y), int(mo), int(d), tzinfo=timezone.utc),
            "path": path,
            "url": f"{SITE}/{path}",
            "hero_url": hero.replace("../images/", f"{SITE}/images/") if hero else "",
            "hero_src": hero.replace("../images/", f"{BASE}/images/") if hero else "",
            "html": md(body),
            "words": len(body.split()),
            "medium": medium,
        })
    return posts


def load_elsewhere() -> list[dict]:
    """Articles published somewhere else, listed in the index and linked out.
    Same hero rule as posts: an entry without one fails the build."""
    out = []
    d = ROOT / "elsewhere"
    for f in sorted(d.glob("*.md")) if d.exists() else []:
        fm, _ = frontmatter(f.read_text(encoding="utf-8"))
        hero = fm.get("hero", "")
        out.append({
            **fm,
            "date": datetime.fromisoformat(fm["date"]).replace(tzinfo=timezone.utc),
            "external": True,
            "href": fm["url"],
            "hero_src": hero.replace("../images/", f"{BASE}/images/") if hero else "",
            "hero_url": hero.replace("../images/", f"{SITE}/images/") if hero else "",
            "words": int(fm.get("words") or 0),
            "source": f.name,
        })
    return out


def minutes(words: int) -> str:
    return f"{max(1, round(words / 230))} min read" if words else ""


CSS = """
:root{--bg:#fbfbfa;--ink:#1a1d22;--muted:#6a707c;--line:#e4e5e8;--code:#f1f2f4;--accent:#3d43a0}
@media (prefers-color-scheme:dark){:root{--bg:#121417;--ink:#e6e8ec;--muted:#9aa1ad;--line:#2a2f37;--code:#1c2026;--accent:#9ea3ee}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 "IBM Plex Sans",ui-sans-serif,-apple-system,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--accent)}
.wrap{max-width:760px;margin:0 auto;padding:0 20px}
header.site{border-bottom:1px solid var(--line);padding:18px 0;margin-bottom:28px}
header.site .wrap{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
header.site a.name{font-weight:600;color:var(--ink);text-decoration:none;font-size:18px}
header.site nav{display:flex;gap:16px;font-size:15px}
header.site nav a{color:var(--muted);text-decoration:none}
header.site nav a:hover,header.site nav a.on{color:var(--ink)}
.tagline{color:var(--muted);font-size:15px;margin:-8px 0 26px}
.idx h1{margin-top:0}
.idx h2{font-size:14px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:34px 0 6px;font-weight:600}
.row{display:grid;grid-template-columns:150px minmax(0,1fr);gap:16px;padding:14px 0;border-top:1px solid var(--line);text-decoration:none;color:inherit}
.row:hover .t{color:var(--accent)}
.row img{width:150px;height:auto;aspect-ratio:1200/630;object-fit:cover;border-radius:5px;border:1px solid var(--line);display:block}
.row .t{font-weight:600;font-size:18px;line-height:1.3}
.row .s{color:var(--muted);font-size:15px;margin-top:3px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.row .m{color:var(--muted);font-size:13.5px;margin-top:4px}
.pill{display:inline-block;font-size:12.5px;border:1px solid var(--line);border-radius:99px;padding:0 9px;margin-right:6px;color:var(--muted);text-decoration:none}
.projects{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 8px}
.more{border-top:1px solid var(--line);margin-top:46px;padding-top:6px}
.more h2{font-size:14px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:600;margin:18px 0 4px}
.all{display:inline-block;margin-top:14px;font-weight:600}
@media (max-width:560px){.row{grid-template-columns:96px minmax(0,1fr);gap:12px}.row img{width:96px}.row .t{font-size:16px}}
.hero{display:block;width:100%;height:auto;border-radius:8px;border:1px solid var(--line);aspect-ratio:1200/630;object-fit:cover}
h1{font-size:36px;line-height:1.15;margin:22px 0 8px;letter-spacing:-.01em}
.meta{color:var(--muted);font-size:14px;margin-bottom:26px}
article h2{font-size:23px;margin:38px 0 6px;line-height:1.25}
article p,article ul,article ol{margin:12px 0}
article figure{margin:22px 0}
article img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;display:block}
article figcaption{color:var(--muted);font-size:14px;margin-top:6px}
.howto{border:1px dashed var(--accent);border-radius:8px;padding:14px 18px;font-size:15px;margin-bottom:26px}
.howto ol{margin:6px 0 0;padding-left:20px}
.howto code{user-select:all}
code{font-family:"IBM Plex Mono",ui-monospace,Menlo,monospace;font-size:.86em;background:var(--code);padding:1px 5px;border-radius:4px}
pre{background:var(--code);padding:14px 16px;border-radius:8px;overflow-x:auto;font-size:14px;line-height:1.5}
pre code{background:none;padding:0;font-size:inherit}
footer.site{border-top:1px solid var(--line);margin-top:56px;padding:22px 0 40px;color:var(--muted);font-size:14px}
.list{display:grid;gap:34px;margin-bottom:20px}
.card{text-decoration:none;color:inherit;display:block}
.card h2{font-size:24px;margin:12px 0 4px;line-height:1.25}
.card p{margin:6px 0;color:var(--muted)}
@media (max-width:560px){body{font-size:16px}h1{font-size:28px}}
"""


def page(title: str, body: str, *, desc: str, url: str, image: str = "", article: dict | None = None,
         noindex: bool = False, nav: str = "") -> str:
    og = [
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{e(url)}">',
        f'<meta property="og:type" content="{"article" if article else "website"}">',
        f'<meta property="og:site_name" content="{NAME}">',
    ]
    if image:
        og += [f'<meta property="og:image" content="{e(image)}">',
               '<meta property="og:image:width" content="1200">',
               '<meta property="og:image:height" content="630">',
               f'<meta property="og:image:alt" content="{e((article or {}).get("hero_alt", title))}">',
               '<meta name="twitter:card" content="summary_large_image">',
               f'<meta name="twitter:image" content="{e(image)}">']
    ld = ""
    if article:
        ld = '<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": title, "description": desc, "image": image, "url": url,
            "datePublished": article["date"].date().isoformat(),
            "author": {"@type": "Person", "name": AUTHOR},
        }) + "</script>"
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(url)}">{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="{SITE}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&family=IBM+Plex+Sans:wght@400;600&display=swap">
{chr(10).join(og)}
{ld}
<style>{CSS}</style>
</head><body>
<header class="site"><div class="wrap"><a class="name" href="{BASE}/">{NAME}</a>
<nav><a href="{BASE}/articles/"{' class="on"' if nav == 'articles' else ''}>Articles</a><a href="{BASE}/feed.xml">RSS</a></nav></div></header>
<main class="wrap">{body}</main>
<footer class="site"><div class="wrap">{e(AUTHOR)} · <a href="{BASE}/feed.xml">RSS</a> · <a href="https://github.com/sinkers">GitHub</a></div></footer>
</body></html>
"""


def row(a: dict) -> str:
    href = a["href"] if a.get("external") else f"{BASE}/{a['path']}"
    ext = ' target="_blank" rel="noopener"' if a.get("external") else ""
    where = f" · on {e(a.get('venue', 'another site'))} ↗" if a.get("external") else ""
    bits = [a["date"].strftime("%-d %b %Y"), e(a.get("project", "")), minutes(a.get("words", 0))]
    return f"""<a class="row" href="{e(href)}"{ext}>
<img src="{e(a['hero_src'])}" alt="" loading="lazy" width="1200" height="630">
<div><div class="t">{e(a['title'])}</div><div class="s">{e(a.get('summary', ''))}</div>
<div class="m">{' · '.join(b for b in bits if b)}{where}</div></div></a>"""


def more(p: dict, everything: list[dict]) -> str:
    """Up to three other articles, same project first, then newest."""
    others = [a for a in everything if a is not p]
    others.sort(key=lambda a: (a.get("project") != p.get("project"), -a["date"].timestamp()))
    rows = "".join(row(a) for a in others[:3])
    return f"""<section class="more"><h2>More articles</h2>{rows}
<a class="all" href="{BASE}/articles/">All articles →</a></section>"""


def post_page(p: dict, everything: list[dict]) -> str:
    repos = " · ".join(f'<a href="https://github.com/{e(r)}">{e(r)}</a>' for r in p.get("repos") or [])
    body = f"""<article>
<img class="hero" src="{e(p['hero_src'])}" alt="{e(p.get('hero_alt', ''))}" width="1200" height="630">
<h1>{e(p['title'])}</h1>
<div class="meta">{p['date'].strftime('%-d %B %Y')} · {e(p.get('project', ''))}{' · ' + repos if repos else ''}</div>
{p['html']}
</article>
{more(p, everything)}"""
    return page(p["title"], body, desc=p.get("summary", ""), url=p["url"], image=p["hero_url"], article=p)


def medium_page(p: dict) -> str:
    m = p["medium"]
    tags = m.get("tags") or []
    body = f"""<div class="howto"><b>Medium copy.</b> Not for reading here: this is the Medium version of
<a href="{BASE}/{p['path']}">the post</a>, laid out to paste into Medium.
<ol>
<li>Select from the picture below to the last line, copy, and paste into a new Medium story.
Or use <a href="https://medium.com/p/import">Import a story</a> with
<code>{e(p['url'])}</code> and paste only the opening section from here.</li>
<li>Subtitle: <code>{e(m.get('subtitle', ''))}</code></li>
<li>Tags: {' '.join(f'<code>{e(t)}</code>' for t in tags)}</li>
<li>Story settings → Advanced → canonical link: <code>{e(p['url'])}</code></li>
</ol></div>
<article>
<figure><img src="{e(m['hero_url'])}" alt="{e(m.get('hero_alt', ''))}" width="1200" height="630"></figure>
<h1>{e(m.get('title') or p['title'])}</h1>
<p><em>{e(m.get('subtitle', ''))}</em></p>
{m['html']}
</article>"""
    return page(f"Medium copy: {p['title']}", body, desc=p.get("summary", ""), url=p["url"], noindex=True)


def articles_page(everything: list[dict]) -> str:
    by_year: dict[int, list[dict]] = {}
    for a in everything:
        by_year.setdefault(a["date"].year, []).append(a)
    years = "".join(f"<h2>{y}</h2>" + "".join(row(a) for a in items) for y, items in by_year.items())
    by_project: dict[str, list[dict]] = {}
    for a in everything:
        by_project.setdefault(a.get("project") or "other", []).append(a)
    chips = "".join(f'<a class="pill" href="#{e(k)}">{e(k)} · {len(v)}</a>' for k, v in sorted(by_project.items()))
    projects = "".join(f'<h2 id="{e(k)}">{e(k)}</h2>' + "".join(row(a) for a in v)
                       for k, v in sorted(by_project.items()))
    n = len(everything)
    body = f"""<div class="idx"><h1>All articles</h1>
<p class="tagline">{n} article{'' if n == 1 else 's'}, newest first. By project:</p>
<div class="projects">{chips}</div>
{years}
<h2 style="margin-top:56px;color:var(--ink);font-size:20px;text-transform:none;letter-spacing:0">By project</h2>
{projects}</div>"""
    return page(f"All articles · {NAME}", body, desc=f"Every {NAME} article, by date and by project.",
                url=f"{SITE}/articles/", image=everything[0]["hero_url"] if everything else "", nav="articles")


def articles_json(everything: list[dict]) -> str:
    return json.dumps([{
        "title": a["title"], "date": a["date"].date().isoformat(), "project": a.get("project", ""),
        "summary": a.get("summary", ""), "url": a["href"] if a.get("external") else a["url"],
        "venue": a.get("venue", "devlog") if a.get("external") else "devlog",
        "hero": a["hero_url"], "words": a.get("words", 0),
    } for a in everything], indent=1)


def index_page(posts: list[dict]) -> str:
    cards = "".join(f"""<a class="card" href="{BASE}/{p['path']}">
<img class="hero" src="{e(p['hero_src'])}" alt="" loading="lazy" width="1200" height="630">
<h2>{e(p['title'])}</h2><p>{e(p.get('summary', ''))}</p>
<p>{p['date'].strftime('%-d %b %Y')} · {e(p.get('project', ''))}</p></a>""" for p in posts)
    return page(NAME, f'<p class="tagline">{e(TAGLINE)}</p><div class="list">{cards}</div>'
                f'<a class="all" href="{BASE}/articles/">All articles →</a>', desc=TAGLINE, url=f"{SITE}/",
                image=posts[0]["hero_url"] if posts else "")


def feed(posts: list[dict]) -> str:
    items = "".join(f"""<item><title>{e(p['title'])}</title><link>{p['url']}</link><guid>{p['url']}</guid>
<pubDate>{format_datetime(p['date'])}</pubDate><description>{e(p.get('summary', ''))}</description>
<enclosure url="{e(p['hero_url'])}" type="image/png" length="0"/></item>""" for p in posts)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>{NAME}</title><link>{SITE}/</link><description>{e(TAGLINE)}</description>{items}</channel></rss>
"""


def main() -> int:
    posts = load_posts()
    elsewhere = load_elsewhere()
    everything = sorted(posts + elsewhere, key=lambda a: a["date"], reverse=True)
    missing = [a.get("path") or a.get("source") for a in everything if not a.get("hero")]
    if missing:
        print(f"posts without a hero: {missing}", file=sys.stderr)
        return 1
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "images", OUT / "images")
    for p in posts:
        d = OUT / p["path"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(post_page(p, everything), encoding="utf-8")
        if p["medium"]:
            (d / "medium").mkdir()
            (d / "medium" / "index.html").write_text(medium_page(p), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(posts), encoding="utf-8")
    (OUT / "articles").mkdir()
    (OUT / "articles" / "index.html").write_text(articles_page(everything), encoding="utf-8")
    (OUT / "articles.json").write_text(articles_json(everything), encoding="utf-8")
    (OUT / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + f"<url><loc>{SITE}/</loc></url><url><loc>{SITE}/articles/</loc></url>" + "".join(f"<url><loc>{p['url']}</loc></url>" for p in posts)
        + "</urlset>\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"built {len(posts)} post(s), {len(elsewhere)} elsewhere, into {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
