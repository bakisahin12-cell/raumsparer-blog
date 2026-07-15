# raumsparer.blog — automatisiertes Content- & Affiliate-System

Nische: kompakte Möbel & Home-Office-Lösungen für kleine Wohnungen (Deutschland).

Das System:
1. **generate_post.py** — schreibt per Claude API automatisch einen neuen, fertigen Blogartikel (Markdown).
2. **build_site.py** — baut aus allen Artikeln eine statische Website (`site/`).
3. **.github/workflows/auto-post.yml** — läuft jeden Montag automatisch, generiert einen neuen Artikel,
   committet ihn und veröffentlicht die Seite neu. **Das ist der Teil, der "von selbst läuft".**

Kosten: 0€ Fixkosten. Einzige laufende Kosten sind ein paar Cent pro generiertem Artikel für die Claude-API
(Größenordnung: <0,05 € pro Artikel bei diesem Umfang).

---

## Einmaliges Setup (ca. 20–30 Minuten)

### 1. Anthropic API Key holen
- Auf https://console.anthropic.com registrieren, unter "Settings → API Keys" einen Key erstellen.
- Dort auch etwas Guthaben aufladen (5-10€ reichen für sehr lange).

### 2. Eigenes GitHub-Repository anlegen
- Kostenlosen Account auf https://github.com erstellen (falls noch nicht vorhanden).
- Neues **privates oder öffentliches** Repository anlegen, z. B. `raumsparer-blog`.
- Diesen kompletten Ordner in das Repository hochladen (per GitHub Web-Upload oder `git push`).

### 3. API Key als Secret hinterlegen
- Im Repository: **Settings → Secrets and variables → Actions → New repository secret**
- Name: `ANTHROPIC_API_KEY`, Wert: dein Key aus Schritt 1.

### 4. GitHub Pages aktivieren
- Im Repository: **Settings → Pages → Source: "GitHub Actions"** auswählen.
- Nach dem ersten Workflow-Lauf ist die Seite unter `https://<dein-username>.github.io/<repo-name>/` erreichbar.

### 5. Ersten Lauf manuell starten (zum Testen)
- Im Repository: **Actions → "Automatisch neuen Artikel veröffentlichen" → Run workflow**.
- Danach läuft es jeden Montag automatisch — du musst nichts mehr tun.

---

## Affiliate-Links einrichten (macht das System zu Geld)

Aktuell stehen in den Artikeln Platzhalter-Links (`href="#"`). Diese musst du **einmalig pro Artikel**
durch echte Affiliate-Links ersetzen:

1. Beim **Amazon PartnerNet** (https://partnernet.amazon.de) kostenlos anmelden.
2. Für die im Artikel empfohlenen Produkte passende Amazon-Links mit deiner Partner-ID suchen.
3. Die `href="#"`-Platzhalter in `posts/*.md` durch die echten Links ersetzen.
4. `python build_site.py` erneut laufen lassen (oder den Workflow erneut auslösen).

Für mehr Automatisierung könnte man später auch die Amazon Product Advertising API anbinden — das ist
aber optional und nicht nötig, um zu starten.

---

## Laufender Aufwand für dich

- **Alle paar Tage (5 Min.)**: kurz prüfen, ob der Artikel inhaltlich stimmt, bevor viel Traffic kommt.
- **Alle paar Wochen**: neue Themen in `THEMEN` (in `generate_post.py`) ergänzen, wenn der Pool zur Neige geht.
- **Einmalig pro neuem Artikel**: Affiliate-Links einsetzen (siehe oben).
- Alles andere — Schreiben, Bauen, Veröffentlichen — läuft automatisch über GitHub Actions.

## Lokal testen (optional)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="dein-key"
python generate_post.py        # neuen Artikel erzeugen
python build_site.py           # Seite bauen
open site/index.html           # lokal ansehen (macOS) / xdg-open unter Linux
```

## Ehrlicher Realitäts-Check

- Das ersetzt keinen Job. Realistisch dauert es Monate, bis nennenswerter Traffic und damit Einnahmen entstehen.
- Google/Amazon können Regeln ändern (SEO-Rankings, Partnerprogramm-Konditionen) — laufende Anpassung ist normal.
- Der Wert dieses Systems liegt darin, dass **die Fleißarbeit (Schreiben, Formatieren, Veröffentlichen)
  wegfällt** — nicht darin, dass komplett ohne jedes Zutun Geld entsteht.
