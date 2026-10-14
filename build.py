"""Build the devlog: posts/*.md -> _site/, for GitHub Pages.

    pip install markdown && python build.py

One post is posts/YYYY-MM-DD-<slug>.md with frontmatter; it is served at
/YYYY/MM/DD/<slug>/. Images live in images/<post>/ and the post refers to them
as ../images/<post>/x.png, so the markdown previews on GitHub too. Every post
has a hero, which is also its og:image: links to it preview with a picture
wherever they are pasted.
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
        posts.append({
            **fm,
            "date": datetime(int(y), int(mo), int(d), tzinfo=timezone.utc),
            "path": path,
            "url": f"{SITE}/{path}",
            "hero_url": hero.replace("../images/", f"{SITE}/images/") if hero else "",
            "hero_src": hero.replace("../images/", f"{BASE}/images/") if hero else "",
            "html": markdown.markdown(body, extensions=["fenced_code", "tables", "sane_lists"]),
            "words": len(body.split()),
        })
    return posts


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
header.site span{color:var(--muted);font-size:14px}
.hero{display:block;width:100%;height:auto;border-radius:8px;border:1px solid var(--line);aspect-ratio:1200/630;object-fit:cover}
h1{font-size:36px;line-height:1.15;margin:22px 0 8px;letter-spacing:-.01em}
.meta{color:var(--muted);font-size:14px;margin-bottom:26px}
article h2{font-size:23px;margin:38px 0 6px;line-height:1.25}
article p,article ul,article ol{margin:12px 0}
article img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;margin:10px 0 0}
article p:has(> img)+p>em:only-child{display:block;color:var(--muted);font-size:14px;margin-top:-4px}
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


def page(title: str, body: str, *, desc: str, url: str, image: str = "", article: dict | None = None) -> str:
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
<link rel="canonical" href="{e(url)}">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="{SITE}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400&family=IBM+Plex+Sans:wght@400;600&display=swap">
{chr(10).join(og)}
{ld}
<style>{CSS}</style>
</head><body>
<header class="site"><div class="wrap"><a class="name" href="{BASE}/">{NAME}</a><span>{e(TAGLINE)}</span></div></header>
<main class="wrap">{body}</main>
<footer class="site"><div class="wrap">{e(AUTHOR)} · <a href="{BASE}/feed.xml">RSS</a> · <a href="https://github.com/sinkers">GitHub</a></div></footer>
</body></html>
"""


def post_page(p: dict) -> str:
    repos = " · ".join(f'<a href="https://github.com/{e(r)}">{e(r)}</a>' for r in p.get("repos") or [])
    body = f"""<article>
<img class="hero" src="{e(p['hero_src'])}" alt="{e(p.get('hero_alt', ''))}" width="1200" height="630">
<h1>{e(p['title'])}</h1>
<div class="meta">{p['date'].strftime('%-d %B %Y')} · {e(p.get('project', ''))}{' · ' + repos if repos else ''}</div>
{p['html']}
</article>"""
    return page(p["title"], body, desc=p.get("summary", ""), url=p["url"], image=p["hero_url"], article=p)


def index_page(posts: list[dict]) -> str:
    cards = "".join(f"""<a class="card" href="{BASE}/{p['path']}">
<img class="hero" src="{e(p['hero_src'])}" alt="" loading="lazy" width="1200" height="630">
<h2>{e(p['title'])}</h2><p>{e(p.get('summary', ''))}</p>
<p>{p['date'].strftime('%-d %b %Y')} · {e(p.get('project', ''))}</p></a>""" for p in posts)
    return page(NAME, f'<div class="list">{cards}</div>', desc=TAGLINE, url=f"{SITE}/",
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
    missing = [p["path"] for p in posts if not p.get("hero")]
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
        (d / "index.html").write_text(post_page(p), encoding="utf-8")
    (OUT / "index.html").write_text(index_page(posts), encoding="utf-8")
    (OUT / "feed.xml").write_text(feed(posts), encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + f"<url><loc>{SITE}/</loc></url>" + "".join(f"<url><loc>{p['url']}</loc></url>" for p in posts)
        + "</urlset>\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    print(f"built {len(posts)} post(s) into {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
