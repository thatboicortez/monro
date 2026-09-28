# Monro

Statische website voor Monro, cosmetologie in Wissenkerke. Nederlands en Oekraïens.

## Pagina's

| NL | UA |
|---|---|
| `/` | `/uk/` |
| `/behandelingen/` | `/uk/behandelingen/` |
| `/over/` | `/uk/over/` |
| `/werkwijze/` | `/uk/werkwijze/` |
| `/contact/` | `/uk/contact/` |

## Iets aanpassen

1. Teksten of gegevens wijzigen in `content/`:
   - `config.json` voor telefoon, adres, Instagram, KvK, prijzen, behandelingen
   - `nl.json` en `uk.json` voor alle teksten
2. Pagina's opnieuw maken: `python build.py`
3. Lokaal bekijken: `python serve.py 5174` en open http://localhost:5174

Bewerk de HTML-bestanden niet met de hand: `build.py` overschrijft ze.

## Online zetten

Upload de hele map (behalve `content/`, `build.py`, `serve.py`, `README.md`) naar een statische host
(Netlify, GitHub Pages, Vercel of gewone webhosting). Vul daarna `siteUrl` in `config.json` in
en draai `python build.py` opnieuw: dan komen er ook `sitemap.xml`, `robots.txt` en hreflang-tags bij.
