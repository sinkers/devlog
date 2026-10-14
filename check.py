"""Checks every post must pass before it is merged (and so published).

    python check.py            # all posts
    python check.py --offline  # skip the link checks

- a hero: exists, PNG/JPEG/WebP, at least 1200 wide, with hero_alt
- alt text on every image in the body
- 600-1200 words, at least one code block
- every github.com/<o>/<r>/blob link is pinned to a commit sha, never a branch
- every link resolves, and every linked repo is public
- `medium` in channels: social/<post>/medium.md exists with a subtitle, one
  to five tags (Medium's limit), the post's canonical and a hero

What this cannot check is what must not be said: private repo names and each
project's `avoid` list live in the dashboard, and listing them here would
publish them. The dashboard checks those before a draft can be approved.
"""
from __future__ import annotations

import re
import struct
import sys
import urllib.error
import urllib.request
from pathlib import Path

from build import frontmatter

ROOT = Path(__file__).parent
UA = {"User-Agent": "devlog-check"}


def image_size(data: bytes) -> tuple[int, int] | None:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:3] == b"\xff\xd8\xff":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            if data[i + 1] in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP" and data[12:16] == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    return None


def resolves(url: str) -> bool:
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url.split("#")[0], method=method, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status < 400
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 405) and method == "HEAD":
                continue
            return False
        except Exception:  # noqa: BLE001
            return False
    return False


def check(post: Path, online: bool) -> list[str]:
    fm, body = frontmatter(post.read_text(encoding="utf-8"))
    errs = []
    hero = fm.get("hero", "")
    if not hero:
        errs.append("no hero: in frontmatter")
    else:
        f = (post.parent / hero).resolve()
        if not f.exists():
            errs.append(f"hero {hero} does not exist")
        else:
            size = image_size(f.read_bytes())
            if not size:
                errs.append("hero is not PNG, JPEG or WebP")
            elif size[0] < 1200:
                errs.append(f"hero is {size[0]}x{size[1]}, needs 1200 wide")
    if not fm.get("hero_alt"):
        errs.append("no hero_alt")
    for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)\s]+)\)", body):
        if not alt.strip():
            errs.append(f"image {src} has no alt text")
        if not src.startswith("http") and not (post.parent / src).resolve().exists():
            errs.append(f"image {src} does not exist")
    prose = re.sub(r"```.*?```", "", body, flags=re.S)
    words = len(prose.split())
    if not 600 <= words <= 1200:
        errs.append(f"{words} words; 600-1200")
    if "```" not in body:
        errs.append("no code excerpt")
    links = set(re.findall(r"\]\((https?://[^)\s]+)\)", body))
    for url in links:
        if re.match(r"https://github\.com/[^/]+/[^/]+/(blob|tree)/", url) and \
                not re.match(r"https://github\.com/[^/]+/[^/]+/(blob|tree)/[0-9a-f]{40}/", url):
            errs.append(f"not pinned to a commit: {url}")
    if "medium" in (fm.get("channels") or []):
        mf = ROOT / "social" / post.stem / "medium.md"
        if not mf.exists():
            errs.append("channels has medium but there is no medium.md")
        else:
            mfm, _ = frontmatter(mf.read_text(encoding="utf-8"))
            if not mfm.get("subtitle"):
                errs.append("medium.md has no subtitle")
            if not 1 <= len(mfm.get("tags") or []) <= 5:
                errs.append("medium.md needs 1-5 tags")
            if mfm.get("canonical") != fm.get("canonical"):
                errs.append("medium.md canonical differs from the post's")
            if not mfm.get("hero"):
                errs.append("medium.md has no hero")
    if online:
        for url in sorted(links):
            if not resolves(url):
                errs.append(f"does not resolve: {url}")
        for owner, repo in sorted({m for u in links for m in re.findall(r"https://github\.com/([^/]+)/([^/#)]+)", u)}):
            if not resolves(f"https://api.github.com/repos/{owner}/{repo}"):
                errs.append(f"repo is not public: {owner}/{repo}")
    return errs


def main() -> int:
    online = "--offline" not in sys.argv
    bad = 0
    for post in sorted((ROOT / "posts").glob("*.md")):
        errs = check(post, online)
        print(f"{'FAIL' if errs else 'ok  '} {post.name}")
        for x in errs:
            print(f"     - {x}")
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
