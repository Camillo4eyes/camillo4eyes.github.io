# camillo4eyes.github.io

Personal site of Camillo Quattrocchi, PhD: <https://camillo4eyes.github.io>

## Structure

| Path | What it is |
|---|---|
| `index.html` | The whole home page (HTML, CSS and JS in one file, light and dark theme) |
| `scholar-data.json` | Google Scholar metrics and publications, read by the page |
| `scripts/fetch_scholar.py` | Refreshes `scholar-data.json` from Google Scholar |
| `.github/workflows/update-scholar.yml` | Runs the script every day at 06:00 UTC and commits changes |
| `games/<name>/index.html` | Playable games, one self-contained page each |
| `assets/games/*.webp` | Thumbnails for the Games section |
| `404.html`, `favicon.svg`, `robots.txt`, `sitemap.xml` | Site plumbing |

## Adding a game

1. Put the game in `games/<slug>/index.html` (a single self-contained HTML file works best).
2. Add an 800×500 thumbnail as `assets/games/<slug>.webp`.
3. Copy one of the `game-card` blocks in the Games section of `index.html` and edit it.
4. Add the URL to `sitemap.xml`.

## Scholar data

The workflow can also be started by hand from the Actions tab (*Update Scholar Data → Run workflow*).
If Google Scholar can't be reached, the script keeps the existing data instead of failing.
