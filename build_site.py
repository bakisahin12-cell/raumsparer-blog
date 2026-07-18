#!/usr/bin/env python3
"""
build_site.py
--------------
Baut aus den Markdown-Dateien in posts/ eine statische HTML-Website in site/.
Kein Server nötig -> kann kostenlos auf GitHub Pages, Netlify oder Cloudflare
Pages gehostet werden.

Nutzung:
    python build_site.py
"""
import re
import shutil
import urllib.parse
from datetime import datetime
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
TEMPLATES_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"
SITE_DIR = ROOT / "site"

# Deine Amazon-PartnerNet Tracking-ID (Partner-ID)
AMAZON_TRACKING_ID = "raumsparerblo-21"

PLACEHOLDER_LINK_RE = re.compile(r'href="#" rel="sponsored nofollow"')


def amazon_search_link(suchbegriff: str) -> str:
    """Baut einen echten Amazon-Suchlink inkl. Tracking-ID (kein ASIN nötig)."""
    query = urllib.parse.quote_plus(suchbegriff)
    return f'https://www.amazon.de/s?k={query}&tag={AMAZON_TRACKING_ID}'


def insert_affiliate_link(body_html: str, suchbegriff: str) -> str:
    """Ersetzt den Platzhalter-Link (href="#") im Affiliate-Block durch einen
    echten, funktionierenden Amazon-Suchlink mit Tracking-ID."""
    if not suchbegriff:
        return body_html
    link = amazon_search_link(suchbegriff)
    replacement = f'href="{link}" rel="sponsored nofollow" target="_blank"'
    return PLACEHOLDER_LINK_RE.sub(replacement, body_html)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Sehr einfacher Frontmatter-Parser (key: value Zeilen, kein YAML nötig)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("Post hat kein gültiges Frontmatter (--- ... ---)")
    raw_meta, body = match.groups()
    meta = {}
    for line in raw_meta.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body


def slugify(name: str) -> str:
    return Path(name).stem.split("-", 3)[-1] if False else Path(name).stem


def load_posts() -> list[dict]:
    posts = []
    for path in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        raw = path.read_text(encoding="utf-8")
        meta, body_md = parse_frontmatter(raw)
        body_html = markdown.markdown(
            body_md, extensions=["tables", "fenced_code", "extra"]
        )
        body_html = insert_affiliate_link(body_html, meta.get("amazon_suchbegriff", ""))
        word_count = len(re.findall(r"\w+", body_md))
        posts.append(
            {
                "slug": path.stem,
                "title": meta.get("title", path.stem),
                "date": meta.get("date", ""),
                "excerpt": meta.get("excerpt", ""),
                "body_html": body_html,
                "read_minutes": max(1, round(word_count / 200)),
            }
        )
    return posts


def build():
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)
    (SITE_DIR / "posts").mkdir()
    shutil.copytree(STATIC_DIR, SITE_DIR / "static")

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    posts = load_posts()
    year = datetime.now().year

    # Startseite
    index_tpl = env.get_template("index.html")
    (SITE_DIR / "index.html").write_text(
        index_tpl.render(posts=posts, root="", year=year), encoding="utf-8"
    )

    # Über-Seite
    about_tpl = env.get_template("about.html")
    (SITE_DIR / "about.html").write_text(
        about_tpl.render(root="", year=year), encoding="utf-8"
    )

    # Einzelne Artikel
    post_tpl = env.get_template("post.html")
    for post in posts:
        out_path = SITE_DIR / "posts" / f"{post['slug']}.html"
        out_path.write_text(
            post_tpl.render(post=post, root="../", year=year), encoding="utf-8"
        )

    print(f"Fertig: {len(posts)} Artikel gebaut -> {SITE_DIR}/")


if __name__ == "__main__":
    build()
