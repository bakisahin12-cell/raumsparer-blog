#!/usr/bin/env python3
"""
generate_post.py
-----------------
Erzeugt automatisch einen neuen Blogartikel (Markdown mit Frontmatter) im
posts/-Ordner, mithilfe der Anthropic API.

Setup:
    pip install anthropic
    export ANTHROPIC_API_KEY="dein-key"   # https://console.anthropic.com/settings/keys

Nutzung:
    python generate_post.py
    python generate_post.py --topic "Klapptisch für den Balkon"

Ohne --topic wird automatisch ein noch nicht behandeltes Thema aus THEMEN
gewählt (die bereits vorhandenen posts/*.md werden dafür übersprungen).
"""
import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

import anthropic

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"

NISCHE = "kompakte Möbel, Home-Office- und Stauraum-Lösungen für kleine Wohnungen in Deutschland"

# Themen-Pool: einfach erweitern, sobald dir neue Ideen einfallen.
THEMEN = [
    "Faltbares Bett-Sofa für Studio-Wohnungen",
    "Wandregale statt Bücherregal: Vertikaler Stauraum",
    "Der ideale Bürostuhl für unter 150 Euro auf kleinem Raum",
    "Raumteiler-Ideen für Einzimmerwohnungen",
    "Kabelmanagement auf kleinem Schreibtisch: Die besten Lösungen",
    "Klapptisch für den Balkon als zweiter Arbeitsplatz",
    "Rollcontainer als Nachttisch, Beistelltisch und Stauraum",
    "Vertikale Küchen-Organizer für kleine Küchen",
    "Multifunktionsmöbel: Ottomane mit Stauraum im Test",
    "Kompakte Beleuchtung für dunkle Arbeitsecken",
]

SYSTEM_PROMPT = f"""Du bist Redakteur*in eines deutschsprachigen Ratgeber-Blogs zum Thema:
{NISCHE}

Schreibe einen SEO-freundlichen, hilfreichen und konkreten Blogartikel auf Deutsch.

Format-Vorgaben (WICHTIG, exakt einhalten):
1. Antworte NUR mit dem Markdown-Inhalt, kein Preamble, keine Erklärung.
2. Beginne mit Frontmatter in diesem Format:
---
title: <prägnanter Titel, max. 70 Zeichen>
date: {date.today().isoformat()}
excerpt: <1 Satz Teaser, max. 160 Zeichen>
---
3. Danach der Artikel in Markdown: mind. 2 H2-Überschriften, eine Bullet-Liste,
   und genau EINE Vergleichs-Tabelle (Markdown-Tabellensyntax).
4. Baue an einer sinnvollen Stelle diesen Affiliate-Hinweis-Block eins zu eins ein
   (Platzhalter-Link, wird später ersetzt):
<div class="affiliate-box">
  <span class="label">Empfehlung</span>
  <TEXT: 1-2 Sätze mit konkreter Produktempfehlung passend zum Thema>
  <br><br>
  <a href="#" rel="sponsored nofollow">→ Aktuelle Modelle auf Amazon ansehen*</a>
</div>
5. Ton: sachlich, konkret, keine Marketing-Floskeln, keine erfundenen Testergebnisse
   oder Studien. Nenne keine echten Markennamen/Preise, die du nicht sicher weißt.
6. Länge: 500-800 Wörter.
"""


def existing_titles() -> set[str]:
    titles = set()
    for path in POSTS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        m = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        if m:
            titles.add(m.group(1).strip().lower())
    return titles


def pick_topic() -> str:
    used = existing_titles()
    for topic in THEMEN:
        if not any(topic.lower() in t or t in topic.lower() for t in used):
            return topic
    return THEMEN[0]  # Themen-Pool leer -> von vorn anfangen


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[äöüß]", lambda m: {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}[m.group()], slug)
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug[:60]


def generate(topic: str) -> str:
    client = anthropic.Anthropic()  # liest ANTHROPIC_API_KEY aus der Umgebung
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Schreibe den Artikel zum Thema: {topic}"}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="Thema erzwingen statt automatisch zu wählen")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Fehler: ANTHROPIC_API_KEY ist nicht gesetzt.")

    topic = args.topic or pick_topic()
    print(f"Generiere Artikel zu: {topic}")

    content = generate(topic)
    title_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else topic
    slug = f"{date.today().isoformat()}-{slugify(title)}"

    POSTS_DIR.mkdir(exist_ok=True)
    out_path = POSTS_DIR / f"{slug}.md"
    out_path.write_text(content, encoding="utf-8")
    print(f"Gespeichert: {out_path}")


if __name__ == "__main__":
    main()
