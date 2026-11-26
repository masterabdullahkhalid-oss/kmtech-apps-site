#!/usr/bin/env python3
"""
Idempotent SEO builder for the Khalid Mustafa Tech apps site.

Run after adding or editing apps:   python scripts/build_seo.py

It regenerates sitemap.xml and ensures every detail/privacy page has:
  - canonical, theme-color, favicon
  - Open Graph + Twitter card meta (per-page title/description)
  - SoftwareApplication JSON-LD (app pages, from the page + _content.json)
  - FAQ section + FAQPage JSON-LD (app pages, from _content.json — accurate data only)

Safe to run repeatedly: blocks it already added are skipped.
(The OG share image assets/og.png is generated once separately and is not touched here.)
"""
import os, glob, re, json, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://masterabdullahkhalid-oss.github.io/kmtech-apps-site/"
OG_IMG = BASE + "assets/og.png"
GAME_HINTS = ("arrow", "sink-hole", "fruit", "gem", "maze", "teeter", "game", "puzzle")

def esc(s): return html.escape(s or "", quote=True)
def read(p): return open(p, encoding="utf-8").read()
def write(p, s): open(p, "w", encoding="utf-8").write(s)

def title_desc(src, slug):
    mt = re.search(r"<title>(.*?)</title>", src, re.S)
    md = re.search(r'<meta name="description" content="(.*?)"', src, re.S)
    t = (mt.group(1) if mt else slug).strip()
    d = (md.group(1).strip() if md else "An Android app by Khalid Mustafa Tech.")
    return t, d

def og_block(canon, title, desc, up="../", typ="article"):
    return (f'<link rel="canonical" href="{esc(canon)}">\n'
      f'<meta name="theme-color" content="#060910">\n'
      f'<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">\n'
      f'<meta property="og:type" content="{typ}">\n'
      f'<meta property="og:site_name" content="Khalid Mustafa Tech">\n'
      f'<meta property="og:title" content="{esc(title)}">\n'
      f'<meta property="og:description" content="{esc(desc)}">\n'
      f'<meta property="og:url" content="{esc(canon)}">\n'
      f'<meta property="og:image" content="{esc(OG_IMG)}">\n'
      f'<meta property="og:image:width" content="1200">\n'
      f'<meta property="og:image:height" content="630">\n'
      f'<meta name="twitter:card" content="summary_large_image">\n'
      f'<meta name="twitter:title" content="{esc(title)}">\n'
      f'<meta name="twitter:description" content="{esc(desc)}">\n'
      f'<meta name="twitter:image" content="{esc(OG_IMG)}">\n</head>')

FAQ_STYLE = ('<style>.faq{max-width:760px;margin:6px auto 64px;padding:0 20px}'
 '.faq h2{font-family:"Space Grotesk",sans-serif;font-size:24px;margin:0 0 16px}'
 '.faq details{border:1px solid rgba(255,255,255,.09);border-radius:12px;margin:0 0 10px;'
 'background:rgba(23,30,48,.6);overflow:hidden}'
 '.faq summary{cursor:pointer;padding:15px 18px;font-weight:600;color:#eff3fa;list-style:none}'
 '.faq summary::-webkit-details-marker{display:none}'
 '.faq summary::after{content:"+";float:right;color:#9fabc2}'
 '.faq details[open] summary::after{content:"\\2013"}'
 '.faq .a{padding:0 18px 16px;color:#9fabc2}</style>')

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'

def main():
    content = json.load(open(os.path.join(ROOT, "_content.json"), encoding="utf-8"))
    today = datetime.date.today().isoformat()

    # ---- sitemap ----
    urls = [("", "1.0")]
    for p in sorted(glob.glob(os.path.join(ROOT, "detail", "*.html"))):
        urls.append(("detail/" + os.path.basename(p), "0.8"))
    for p in sorted(glob.glob(os.path.join(ROOT, "privacy", "*.html"))):
        urls.append(("privacy/" + os.path.basename(p), "0.5"))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pr in urls:
        sm.append(f"  <url><loc>{BASE}{loc}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    write(os.path.join(ROOT, "sitemap.xml"), "\n".join(sm) + "\n")
    print("sitemap.xml:", len(urls), "urls")

    det = pri = app_ld = faq = 0
    # ---- detail pages ----
    for path in sorted(glob.glob(os.path.join(ROOT, "detail", "*.html"))):
        slug = os.path.basename(path)[:-5]; src = read(path); orig = src
        t, d = title_desc(src, slug)
        name = t.split("—")[0].strip().rstrip("- ").strip()
        canon = BASE + "detail/" + slug + ".html"
        on_play = "play.google.com/store/apps/details" in src
        if "og:title" not in src:
            src = src.replace("</head>", og_block(canon, t, d), 1); det += 1
        if "SoftwareApplication" not in src:
            mi = re.search(r'src="(\.\./assets/icons/[^"]+)"', src)
            image = BASE + mi.group(1).replace("../", "") if mi else OG_IMG
            mp = re.search(r'(https://play\.google\.com/store/apps/details\?id=[^"&]+)', src)
            cat = "GameApplication" if any(h in slug for h in GAME_HINTS) else "UtilitiesApplication"
            app = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": name,
                   "description": d, "operatingSystem": "Android", "applicationCategory": cat,
                   "image": image, "author": {"@type": "Organization", "name": "Khalid Mustafa Tech"},
                   "publisher": {"@type": "Organization", "name": "Khalid Mustafa Tech"}}
            if mp:
                app["downloadUrl"] = app["installUrl"] = mp.group(1)
                app["offers"] = {"@type": "Offer", "price": "0", "priceCurrency": "USD"}
            src = src.replace("</head>", ld(app) + "\n</head>", 1); app_ld += 1
        if "FAQPage" not in src and slug in content:
            c = content[slug]; feats = c.get("features", [])
            qa = [(f"What is {name}?", c.get("pitch") or c.get("short") or f"{name} is an Android app by Khalid Mustafa Tech.")]
            if feats: qa.append((f"What are the main features of {name}?", "; ".join(feats) + "."))
            qa.append((f"Is {name} free to download?",
                       f"Yes. {name} is free to download on Google Play." if on_play
                       else f"{name} is coming soon to Google Play and will be free to download."))
            qa.append((f"Who develops {name}?", f"{name} is developed by Khalid Mustafa Tech, an independent Android app developer."))
            items = "".join(f'<details><summary>{esc(q)}</summary><div class="a">{esc(a)}</div></details>' for q, a in qa)
            src = src.replace("</main>", f'{FAQ_STYLE}<section class="faq"><h2>{esc(name)} — Frequently asked questions</h2>{items}</section>\n</main>', 1)
            src = src.replace("</head>", ld({"@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}) + "\n</head>", 1)
            faq += 1
        if src != orig: write(path, src)

    # ---- privacy pages (canonical + favicon + basic OG) ----
    for path in sorted(glob.glob(os.path.join(ROOT, "privacy", "*.html"))):
        src = read(path)
        if "og:title" in src or 'rel="canonical"' in src: continue
        slug = os.path.basename(path)[:-5]; t, d = title_desc(src, slug)
        canon = BASE + "privacy/" + slug + ".html"
        write(path, src.replace("</head>", og_block(canon, t, d), 1)); pri += 1

    print(f"detail: +{det} og, +{app_ld} app-schema, +{faq} faq | privacy: +{pri} og")

if __name__ == "__main__":
    main()
