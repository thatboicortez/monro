#!/usr/bin/env python3
"""
Monro - statische sitegenerator (alleen Python standaardbibliotheek).

Bronnen:
  content/config.json   bedrijfsgegevens, behandelingen, prijzen
  content/nl.json       Nederlandse teksten
  content/uk.json       Oekraïense teksten

Gebruik:  python build.py
Resultaat: kant-en-klare HTML-pagina's in de projectmap:
  /  /behandelingen/  /over/  /werkwijze/  /contact/   (Nederlands)
  /uk/  /uk/behandelingen/  ...                        (Oekraïens)
"""
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
LANGS = ["nl", "uk"]
LANG_LABEL = {"nl": "NL", "uk": "UA"}
SLUGS = {
    "home": "",
    "treatments": "behandelingen/",
    "about": "over/",
    "process": "werkwijze/",
    "contact": "contact/",
}


def load(name):
    with open(os.path.join(ROOT, "content", name), encoding="utf-8") as f:
        return json.load(f)


CFG = load("config.json")
T = {lang: load(lang + ".json") for lang in LANGS}


def e(s):
    return html.escape(str(s), quote=True)


def loc(value, lang):
    """Config-waarden kunnen per taal verschillen: {"nl": ..., "uk": ...}."""
    return value.get(lang, value.get("nl")) if isinstance(value, dict) else value


def url(page, lang):
    return ("/" if lang == "nl" else "/uk/") + SLUGS[page]


def tel_href():
    return "tel:" + "".join(c for c in CFG["phone"].replace("(0)", "") if c.isdigit() or c == "+")


def price(t, amount):
    return f'{e(t["common"]["from"])} €{amount}'


def duration(t, value):
    return f'{e(value)} {e(t["common"]["min"])}'


# ---------------------------------------------------------------- layout

def head(lang, page, title, desc):
    t = T[lang]
    alternates = ""
    if CFG.get("siteUrl") and page in SLUGS:
        base = CFG["siteUrl"].rstrip("/")
        alternates = "".join(
            f'\n  <link rel="alternate" hreflang="{l}" href="{base}{url(page, l)}">' for l in LANGS
        ) + f'\n  <link rel="alternate" hreflang="x-default" href="{base}{url(page, "nl")}">' \
          + f'\n  <link rel="canonical" href="{base}{url(page, lang)}">'
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="theme-color" content="#F4F0EA">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{CFG.get('siteUrl', '').rstrip('/')}/images/hero.jpg">{alternates}
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="/fonts/prata-{'latin' if lang == 'nl' else 'cyrillic'}-400-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/css/fonts.css">
  <link rel="stylesheet" href="/css/style.css">
  <script>document.documentElement.classList.add("js")</script>
</head>
<body data-page="{page}">
  <a class="skip" href="#main">{e(t["skip"])}</a>
"""


def header(lang, page):
    t = T[lang]
    items = [("treatments", t["nav"]["treatments"]), ("about", t["nav"]["about"]), ("process", t["nav"]["process"])]

    def nav_links():
        out = []
        for key, label in items:
            cur = ' aria-current="page"' if key == page else ""
            out.append(f'<a href="{url(key, lang)}"{cur}>{e(label)}</a>')
        return "\n        ".join(out)

    langs = []
    for l in LANGS:
        target = url(page, l) if page in SLUGS else url("home", l)
        cur = ' aria-current="true"' if l == lang else ""
        langs.append(f'<a class="lang__link" href="{target}" hreflang="{l}" lang="{l}"{cur}>{LANG_LABEL[l]}</a>')
    lang_switch = '<span class="lang__sep" aria-hidden="true">/</span>'.join(langs)
    cta_cur = ' aria-current="page"' if page == "contact" else ""

    return f"""
  <header class="header" id="header">
    <div class="header__inner">
      <nav class="header__nav" aria-label="Menu">
        {nav_links()}
      </nav>
      <a class="brand" href="{url('home', lang)}" aria-label="Monro, {e(t['nav']['home'])}">
        <span class="brand__name">Monro</span>
        <span class="brand__sub">{e(t['brandSub'])}</span>
      </a>
      <div class="header__actions">
        <div class="lang">{lang_switch}</div>
        <a class="btn btn--dark btn--sm header__cta" href="{url('contact', lang)}"{cta_cur}>{e(t['nav']['book'])}</a>
        <button type="button" class="burger" id="burger" aria-expanded="false" aria-controls="mobile-menu">
          <span class="burger__lines" aria-hidden="true"></span>
          <span class="sr">{e(t['nav']['menu'])}</span>
        </button>
      </div>
    </div>
  </header>
  <div class="header-sentinel" aria-hidden="true"></div>

  <div class="mobile-menu" id="mobile-menu" hidden>
    <nav class="mobile-menu__nav" aria-label="{e(t['nav']['menu'])}">
      <a href="{url('home', lang)}"{' aria-current="page"' if page == 'home' else ''}>{e(t['nav']['home'])}</a>
      {nav_links()}
    </nav>
    <a class="btn btn--dark btn--block" href="{url('contact', lang)}">{e(t['nav']['book'])}</a>
  </div>
"""


def footer(lang):
    t = T[lang]
    contact = []
    if CFG.get("phone"):
        contact.append(f'<a href="{tel_href()}">{e(CFG["phone"])}</a>')
    if CFG.get("whatsapp"):
        contact.append(f'<a href="https://wa.me/{e(CFG["whatsapp"])}" target="_blank" rel="noopener">WhatsApp</a>')
    if CFG.get("instagram"):
        contact.append(f'<a href="{e(CFG["instagram"])}" target="_blank" rel="noopener">Instagram</a>')
    if CFG.get("email"):
        contact.append(f'<a href="mailto:{e(CFG["email"])}">{e(CFG["email"])}</a>')
    if CFG.get("address"):
        contact.append(f'<a href="{e(CFG["mapsUrl"])}" target="_blank" rel="noopener">{e(CFG["address"])}</a>')
    kvk = f'<span>{e(t["footer"]["kvk"])} {e(CFG["kvk"])}</span>' if CFG.get("kvk") else ""
    return f"""
  <footer class="footer">
    <div class="footer__inner">
      <div class="footer__brand">
        <a class="brand__name brand__name--lg" href="{url('home', lang)}">Monro</a>
        <p>{e(t['footer']['tag'])}</p>
      </div>
      <nav class="footer__col" aria-label="{e(t['footer']['nav'])}">
        <p class="footer__label">{e(t['footer']['nav'])}</p>
        <a href="{url('treatments', lang)}">{e(t['nav']['treatments'])}</a>
        <a href="{url('about', lang)}">{e(t['nav']['about'])}</a>
        <a href="{url('process', lang)}">{e(t['nav']['process'])}</a>
        <a href="{url('contact', lang)}">{e(t['nav']['book'])}</a>
      </nav>
      <div class="footer__col">
        <p class="footer__label">{e(t['footer']['contact'])}</p>
        {chr(10).join('        ' + c for c in contact).strip()}
      </div>
    </div>
    <div class="footer__bottom">
      <span>© {date.today().year} Monro. {e(t['footer']['rights'])}</span>
      {kvk}
    </div>
  </footer>
  <script src="/js/main.js" defer></script>
</body>
</html>
"""


def cta_band(lang):
    t = T[lang]
    return f"""
    <section class="cta-band">
      <div class="cta-band__inner">
        <div>
          <h2 class="h2 reveal">{e(t['common']['ctaTitle'])}</h2>
          <p class="cta-band__text reveal">{e(t['common']['ctaText'])}</p>
        </div>
        <a class="btn btn--dark reveal" href="{url('contact', lang)}">{e(t['nav']['book'])}</a>
      </div>
    </section>"""


def page_head(title, lead):
    return f"""
    <section class="page-head">
      <h1 class="page-head__title reveal">{e(title)}</h1>
      <p class="page-head__lead reveal">{e(lead)}</p>
    </section>"""


# ---------------------------------------------------------------- pagina's

def home(lang):
    t, h = T[lang], T[lang]["home"]
    rows = []
    for tr in CFG["treatments"]:
        c = t["treatments"][tr["id"]]
        rows.append(f"""
          <li class="reveal">
            <a class="tlist__row" href="{url('treatments', lang)}#{tr['id']}">
              <span class="tlist__img"><img src="/images/{tr['image']}" alt="" loading="lazy" width="400" height="500"></span>
              <span class="tlist__name">{e(c['name'])}</span>
              <span class="tlist__short">{e(c['short'])}</span>
              <span class="tlist__price">{price(t, tr['price'])}</span>
              <span class="tlist__arrow" aria-hidden="true">→</span>
            </a>
          </li>""")
    body = f"""
  <main id="main">
    <section class="hero">
      <div class="hero__text">
        <p class="eyebrow reveal">{e(h['eyebrow'])}</p>
        <h1 class="hero__title reveal">{e(h['heroTitle'])} <span class="accent">{e(h['heroAccent'])}</span></h1>
        <p class="hero__lead reveal">{e(h['heroLead'])}</p>
        <div class="hero__ctas reveal">
          <a class="btn btn--dark" href="{url('contact', lang)}">{e(t['nav']['book'])}</a>
          <a class="btn btn--ghost" href="{url('treatments', lang)}">{e(t['nav']['treatments'])}</a>
        </div>
      </div>
      <div class="hero__media reveal">
        <img src="/images/hero.jpg" alt="" width="1400" height="2100" fetchpriority="high">
      </div>
    </section>

    <section class="manifesto">
      <p class="manifesto__text reveal">{e(h['manifesto'])}</p>
    </section>

    <section class="section">
      <div class="section__bar">
        <h2 class="h2 reveal">{e(h['treatmentsTitle'])}</h2>
        <a class="link-arrow reveal" href="{url('treatments', lang)}">{e(t['common']['allTreatments'])}</a>
      </div>
      <ul class="tlist">{''.join(rows)}
      </ul>
    </section>

    <section class="dark-split">
      <div class="dark-split__inner">
        <div class="dark-split__media reveal"><img src="/images/studio.jpg" alt="" loading="lazy" width="1200" height="1800"></div>
        <div class="dark-split__text">
          <h2 class="h2 reveal">{e(h['aboutTitle'])}</h2>
          <p class="reveal">{e(h['aboutText'])}</p>
          <p class="dark-split__sign reveal">{e(loc(CFG['owner'], lang))}, {e(t['common']['cosmetologist'])}</p>
          <a class="btn btn--light reveal" href="{url('about', lang)}">{e(h['aboutLink'])}</a>
        </div>
      </div>
    </section>

    <section class="gallery" aria-hidden="true">
      <div class="gallery__item reveal"><img src="/images/sfeer-1.jpg" alt="" loading="lazy" width="900" height="1350"></div>
      <div class="gallery__item gallery__item--offset reveal"><img src="/images/sfeer-2.jpg" alt="" loading="lazy" width="900" height="1350"></div>
      <div class="gallery__item reveal"><img src="/images/sfeer-3.jpg" alt="" loading="lazy" width="900" height="1350"></div>
    </section>
{cta_band(lang)}
  </main>"""
    return head(lang, "home", h["title"], h["desc"]) + header(lang, "home") + body + footer(lang)


def treatments(lang):
    t, p = T[lang], T[lang]["treatmentsPage"]
    index, articles = [], []
    for tr in CFG["treatments"]:
        c = t["treatments"][tr["id"]]
        index.append(f"""
          <li><a href="#{tr['id']}"><span>{e(c['name'])}</span><span class="tp__index-price">{price(t, tr['price'])}</span></a></li>""")
        tags = "".join(f"<li>{e(x)}</li>" for x in c["includes"])
        articles.append(f"""
        <article class="tr" id="{tr['id']}">
          <div class="tr__media reveal"><img src="/images/{tr['image']}" alt="" loading="lazy" width="1000" height="1250"></div>
          <div class="tr__body">
            <h2 class="tr__title reveal">{e(c['name'])}</h2>
            <p class="tr__desc reveal">{e(c['desc'])}</p>
            <p class="tr__label reveal">{e(p['includes'])}</p>
            <ul class="tags reveal">{tags}</ul>
            <dl class="meta reveal">
              <div><dt>{e(t['common']['duration'])}</dt><dd>{duration(t, tr['duration'])}</dd></div>
              <div><dt>{e(t['common']['price'])}</dt><dd>{price(t, tr['price'])}</dd></div>
            </dl>
            <a class="btn btn--dark reveal" href="{url('contact', lang)}?behandeling={tr['id']}">{e(t['nav']['book'])}</a>
          </div>
        </article>""")
    body = f"""
  <main id="main">{page_head(p['h1'], p['lead'])}
    <div class="tp">
      <aside class="tp__index">
        <ul>{''.join(index)}
        </ul>
        <p class="tp__note">{e(p['note'])}</p>
      </aside>
      <div class="tp__list">{''.join(articles)}
      </div>
    </div>
{cta_band(lang)}
  </main>"""
    return head(lang, "treatments", p["title"], p["desc"]) + header(lang, "treatments") + body + footer(lang)


def about(lang):
    t, p = T[lang], T[lang]["aboutPage"]
    values = "".join(f"""
        <li class="value reveal"><h3 class="value__title">{e(v['title'])}</h3><p>{e(v['text'])}</p></li>""" for v in p["values"])
    body = f"""
  <main id="main">
    <section class="about-hero">
      <div class="about-hero__text">
        <h1 class="page-head__title reveal">{e(p['h1'])}</h1>
        <p class="about-hero__intro reveal">{e(p['intro'])}</p>
        <p class="reveal">{e(p['p1'])}</p>
        <p class="reveal">{e(p['p2'])}</p>
        <p class="about-hero__sign reveal">{e(loc(CFG['owner'], lang))}</p>
      </div>
      <div class="about-hero__media reveal"><img src="/images/studio.jpg" alt="" width="1200" height="1800"></div>
    </section>

    <section class="section">
      <h2 class="h2 reveal">{e(p['valuesTitle'])}</h2>
      <ul class="values">{values}
      </ul>
    </section>

    <section class="dark-band">
      <div class="dark-band__inner">
        <h2 class="h2 reveal">{e(p['langTitle'])}</h2>
        <p class="reveal">{e(p['langText'])}</p>
      </div>
    </section>
{cta_band(lang)}
  </main>"""
    return head(lang, "about", p["title"], p["desc"]) + header(lang, "about") + body + footer(lang)


def process(lang):
    t, p = T[lang], T[lang]["processPage"]
    steps = "".join(f"""
        <li class="pstep reveal">
          <span class="pstep__num">{i:02d}</span>
          <h2 class="pstep__title">{e(s['title'])}</h2>
          <p class="pstep__text">{e(s['text'])}</p>
        </li>""" for i, s in enumerate(p["steps"], 1))
    faq = "".join(f"""
        <details class="faq__item reveal">
          <summary>{e(f['q'])}<span class="faq__icon" aria-hidden="true"></span></summary>
          <p>{e(f['a'])}</p>
        </details>""" for f in p["faq"])
    body = f"""
  <main id="main">{page_head(p['h1'], p['lead'])}
    <section class="section section--flush">
      <ol class="psteps">{steps}
      </ol>
    </section>

    <div class="wide-image reveal"><img src="/images/sfeer-1.jpg" alt="" loading="lazy" width="900" height="1350"></div>

    <section class="section faq">
      <h2 class="h2 reveal">{e(p['faqTitle'])}</h2>
      <div class="faq__list">{faq}
      </div>
    </section>
{cta_band(lang)}
  </main>"""
    return head(lang, "process", p["title"], p["desc"]) + header(lang, "process") + body + footer(lang)


def contact(lang):
    t, p, f = T[lang], T[lang]["contactPage"], T[lang]["form"]
    items = []
    if CFG.get("phone"):
        items.append(f'<div><dt>{e(p["phone"])}</dt><dd><a href="{tel_href()}">{e(CFG["phone"])}</a></dd></div>')
    if CFG.get("whatsapp"):
        items.append(f'<div><dt>{e(p["whatsapp"])}</dt><dd><a href="https://wa.me/{e(CFG["whatsapp"])}" target="_blank" rel="noopener">{e(p["whatsappCta"])}</a></dd></div>')
    if CFG.get("address"):
        items.append(f'<div><dt>{e(p["address"])}</dt><dd>{e(CFG["address"])}<br><a class="small-link" href="{e(CFG["mapsUrl"])}" target="_blank" rel="noopener">{e(p["route"])}</a></dd></div>')
    if CFG.get("instagram"):
        items.append(f'<div><dt>Instagram</dt><dd><a href="{e(CFG["instagram"])}" target="_blank" rel="noopener">{e(CFG.get("instagramHandle") or "Instagram")}</a></dd></div>')
    if CFG.get("email"):
        items.append(f'<div><dt>{e(p["email"])}</dt><dd><a href="mailto:{e(CFG["email"])}">{e(CFG["email"])}</a></dd></div>')
    items.append(f'<div><dt>{e(p["hours"])}</dt><dd>{e(p["hoursValue"])}</dd></div>')

    options = [("consult", f["consult"])] + [(tr["id"], t["treatments"][tr["id"]]["name"]) for tr in CFG["treatments"]] + [("unsure", f["unsure"])]
    opts = "".join(f'<option value="{k}">{e(v)}</option>' for k, v in options)
    via_wa = bool(CFG.get("whatsapp"))

    body = f"""
  <main id="main">
    <section class="contact">
      <div class="contact__info">
        <h1 class="page-head__title reveal">{e(p['h1'])}</h1>
        <p class="page-head__lead reveal">{e(p['lead'])}</p>
        <dl class="contact__list reveal">
          {chr(10).join('          ' + i for i in items).strip()}
        </dl>
      </div>

      <form class="form reveal" id="booking-form" novalidate
            data-whatsapp="{e(CFG.get('whatsapp', ''))}" data-email="{e(CFG.get('email', ''))}"
            data-subject="{e(f['subject'])}">
        <div class="form__row">
          <div class="field">
            <label class="field__label" for="f-name">{e(f['name'])}</label>
            <input id="f-name" type="text" name="name" autocomplete="name" required>
          </div>
          <div class="field">
            <label class="field__label" for="f-phone">{e(f['phone'])}</label>
            <input id="f-phone" type="tel" name="phone" autocomplete="tel" inputmode="tel">
          </div>
        </div>
        <div class="field field--select">
          <label class="field__label" for="f-service">{e(f['service'])}</label>
          <select id="f-service" name="service">{opts}</select>
        </div>
        <div class="field">
          <label class="field__label" for="f-message">{e(f['message'])}</label>
          <textarea id="f-message" name="message" rows="4"></textarea>
        </div>
        <label class="check">
          <input type="checkbox" name="consent" required>
          <span>{e(f['consent'])}</span>
        </label>
        <p class="form__error" id="form-error" role="alert" hidden>{e(f['error'])}</p>
        <button type="submit" class="btn btn--dark btn--block">{e(f['submit'] if via_wa else f['submitEmail'])}</button>
        <p class="form__note">{e(f['note'] if via_wa else f['noteEmail'])}</p>
      </form>
    </section>
  </main>"""
    return head(lang, "contact", p["title"], p["desc"]) + header(lang, "contact") + body + footer(lang)


def not_found(lang):
    t, p = T[lang], T[lang]["notFound"]
    body = f"""
  <main id="main">
    <section class="not-found">
      <h1 class="page-head__title">{e(p['h1'])}</h1>
      <p class="page-head__lead">{e(p['text'])}</p>
      <div class="hero__ctas">
        <a class="btn btn--dark" href="{url('home', lang)}">{e(p['home'])}</a>
        <a class="btn btn--ghost" href="{url('treatments', lang)}">{e(t['nav']['treatments'])}</a>
      </div>
    </section>
  </main>"""
    return head(lang, "404", p["title"], p["text"]) + header(lang, "404") + body + footer(lang)


PAGES = {"home": home, "treatments": treatments, "about": about, "process": process, "contact": contact}


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("  " + rel.replace(os.sep, "/"))


def main():
    print("Monro build:")
    for lang in LANGS:
        prefix = "" if lang == "nl" else "uk/"
        for key, fn in PAGES.items():
            write(prefix + SLUGS[key] + "index.html", fn(lang))
    write("404.html", not_found("nl"))

    if CFG.get("siteUrl"):
        base = CFG["siteUrl"].rstrip("/")
        urls = "".join(f"  <url><loc>{base}{url(k, l)}</loc></url>\n" for l in LANGS for k in SLUGS)
        write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
        write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")


if __name__ == "__main__":
    main()
