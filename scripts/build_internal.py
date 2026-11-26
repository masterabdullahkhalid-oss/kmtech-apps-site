#!/usr/bin/env python3
"""
Internal-linking + breadcrumbs builder (SEO). Re-run after adding apps:
    python scripts/build_internal.py

Adds to each detail page: a visible breadcrumb (Home > App) + BreadcrumbList schema,
and a "More from Khalid Mustafa Tech" related-apps section (internal links).
Adds breadcrumbs to category pages too. Refreshes sitemap (incl. about.html + best/).
Idempotent.
"""
import os, re, html, glob, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://masterabdullahkhalid-oss.github.io/kmtech-apps-site/"
def esc(s): return html.escape(s or "", quote=True)
def read(p): return open(p, encoding="utf-8").read()
def write(p, s): open(p, "w", encoding="utf-8").write(s)
def ld(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>'

def parse_apps():
    src = read(os.path.join(ROOT, "index.html")); apps = []
    for block in src.split('<div class="card reveal">')[1:]:
        det = re.search(r'href="detail/([^"]+)\.html"', block)
        icon = re.search(r'src="(assets/icons/[^"]+)"', block)
        name = re.search(r"<h3>(.*?)</h3>", block, re.S)
        tag = re.search(r'<p class="tagline">(.*?)</p>', block, re.S)
        if det:
            apps.append({"slug": det.group(1), "icon": icon.group(1) if icon else "assets/og.png",
                         "name": name.group(1).strip() if name else det.group(1),
                         "tagline": tag.group(1).strip() if tag else ""})
    return apps

CRUMB = ('<nav class="crumbs" aria-label="Breadcrumb" style="font-size:13px;color:#6b7891;'
         'max-width:1080px;margin:0 auto;padding:16px 20px 0">'
         '<a href="{home}" style="color:#9fabc2">Home</a> &rsaquo; {name}</nav>')

def crumb_ld(name, url, home_url):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": home_url},
        {"@type": "ListItem", "position": 2, "name": name, "item": url}]})

def main():
    apps = parse_apps()
    by_slug = {a["slug"]: a for a in apps}
    order = [a["slug"] for a in apps]
    bc = rel = catbc = 0

    for path in sorted(glob.glob(os.path.join(ROOT, "detail", "*.html"))):
        slug = os.path.basename(path)[:-5]; src = read(path); orig = src
        mt = re.search(r"<title>(.*?)</title>", src, re.S)
        name = (mt.group(1) if mt else slug).split("—")[0].strip().rstrip("- ").strip()
        url = BASE + "detail/" + slug + ".html"
        if "BreadcrumbList" not in src:
            src = src.replace('<main class="wrap">',
                '<main class="wrap">\n' + CRUMB.format(home="../index.html", name=esc(name)), 1)
            src = src.replace("</head>", crumb_ld(name, url, BASE) + "\n</head>", 1)
            bc += 1
        if "More from Khalid" not in src and slug in by_slug:
            i = order.index(slug) if slug in order else 0
            picks = [by_slug[order[(i + k) % len(order)]] for k in range(1, 5)] if order else []
            cards = "".join(
                f'<a class="card reveal" href="../detail/{p["slug"]}.html" style="text-decoration:none;color:inherit">'
                f'<img class="icon" src="../{esc(p["icon"])}" alt="{esc(p["name"])}" loading="lazy" width="60" height="60">'
                f'<div class="card-body"><h3>{esc(p["name"])}</h3><p class="tagline">{esc(p["tagline"])}</p></div></a>'
                for p in picks)
            sec = (f'<section class="sec"><div class="sec-head"><span class="dot"></span>'
                   f'<h2>More from Khalid Mustafa Tech</h2></div><div class="grid">{cards}</div></section>\n')
            if '<section class="faq">' in src:
                src = src.replace('<style>.faq', sec + '<style>.faq', 1)
            else:
                src = src.replace("</main>", sec + "</main>", 1)
            rel += 1
        if src != orig: write(path, src)

    for path in sorted(glob.glob(os.path.join(ROOT, "best", "*.html"))):
        src = read(path)
        if "BreadcrumbList" in src: continue
        mt = re.search(r"<title>(.*?)</title>", src, re.S)
        name = (mt.group(1) if mt else "Category").split("|")[0].strip()
        url = BASE + "best/" + os.path.basename(path)
        src = src.replace('<main class="wrap">', '<main class="wrap">\n' + CRUMB.format(home="../index.html", name=esc(name)), 1)
        src = src.replace("</head>", crumb_ld(name, url, BASE) + "\n</head>", 1)
        write(path, src); catbc += 1

    # sitemap (incl about + best + detail + privacy)
    today = datetime.date.today().isoformat(); urls = [("", "1.0"), ("about.html", "0.6")]
    for p in sorted(glob.glob(os.path.join(ROOT, "best", "*.html"))): urls.append(("best/" + os.path.basename(p), "0.9"))
    for p in sorted(glob.glob(os.path.join(ROOT, "detail", "*.html"))): urls.append(("detail/" + os.path.basename(p), "0.8"))
    for p in sorted(glob.glob(os.path.join(ROOT, "privacy", "*.html"))): urls.append(("privacy/" + os.path.basename(p), "0.5"))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pr in urls: sm.append(f"  <url><loc>{BASE}{loc}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>"); write(os.path.join(ROOT, "sitemap.xml"), "\n".join(sm) + "\n")

    print(f"breadcrumbs: +{bc} detail, +{catbc} category | related sections: +{rel} | sitemap: {len(urls)} urls")

if __name__ == "__main__":
    main()
