#!/usr/bin/env python3
"""
Generate SEO category / "best apps" landing pages that target how people search
("best call recorder app", "video downloader for android", etc.) and funnel visitors
to the matching app. Re-run after adding apps:  python scripts/build_categories.py

Reads the app cards from index.html (name, icon, tagline, desc, Play link, status),
writes best/<slug>.html pages, links them from index.html, and refreshes sitemap via build_seo.
Idempotent and safe to re-run.
"""
import os, re, html, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://masterabdullahkhalid-oss.github.io/kmtech-apps-site/"
OG_IMG = BASE + "assets/og.png"
PLAY_SVG = ('<svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true" style="flex:0 0 auto">'
 '<path d="M3.6 2.3 13.2 12 3.6 21.7a1 1 0 0 1-.6-.9V3.2a1 1 0 0 1 .6-.9Z" fill="#00d2ff"/>'
 '<path d="M16.9 8.5 13.2 12l3.7 3.5 3.4-1.9c1-.6 1-2 0-2.6l-3.4-1.5Z" fill="#ffc400"/>'
 '<path d="M3.6 2.3 13.2 12l3.7-3.5L6.2 2.2a1.2 1.2 0 0 0-2.6.1Z" fill="#00e07a"/>'
 '<path d="M3.6 21.7 13.2 12l3.7 3.5L6.2 21.8a1.2 1.2 0 0 1-2.6-.1Z" fill="#ff4b63"/></svg>')

def esc(s): return html.escape(s or "", quote=True)

# ---- parse app registry from index.html ----
def parse_apps():
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    apps = {}
    for block in src.split('<div class="card reveal">')[1:]:
        det = re.search(r'href="detail/([^"]+)\.html"', block)
        if not det: continue
        slug = det.group(1)
        icon = re.search(r'src="(assets/icons/[^"]+)"', block)
        name = re.search(r"<h3>(.*?)</h3>", block, re.S)
        tag = re.search(r'<p class="tagline">(.*?)</p>', block, re.S)
        desc = re.search(r'<p class="desc">(.*?)</p>', block, re.S)
        play = re.search(r'href="(https://play\.google\.com/store/apps/details\?id=[^"]+)"', block)
        apps[slug] = {
            "slug": slug,
            "icon": icon.group(1) if icon else "assets/og.png",
            "name": name.group(1).strip() if name else slug,
            "tagline": tag.group(1).strip() if tag else "",
            "desc": desc.group(1).strip() if desc else "",
            "play": play.group(1) if play else None,
        }
    return apps

# ---- categories: slug -> (title, h1, intro, [app slugs], [ (q,a) ] ) ----
CATS = {
 "call-recorder-apps": {
   "title": "Best Call Recorder Apps for Android",
   "intro": "Looking for a reliable call recorder for Android? These apps by Khalid Mustafa Tech let you record phone calls automatically and keep them organised on your device. Below is our call recording app — free on Google Play.",
   "members": ["talkkeep-call-recorder"],
   "faq": [("What is the best call recorder app for Android?",
            "All Call Recorder records your phone and app calls automatically in clear quality and keeps them in a tidy, searchable library — a great free option on Google Play."),
           ("Is there a free call recorder?",
            "Yes. All Call Recorder is free to download on Google Play.")],
 },
 "video-downloader-apps": {
   "title": "Best Video Downloader Apps for Android",
   "intro": "Want to save videos and reels to watch offline? These video downloader and saver apps by Khalid Mustafa Tech let you download the videos you have the right to keep, straight to your phone. Always respect copyright and each platform's terms.",
   "members": ["all-video-downloader", "vidgrab", "feedgrab", "reelgrab", "xsaver", "redgrab", "liksaver", "threads", "pinterest", "snapchat"],
   "faq": [("What is the best free video downloader for Android?",
            "All Video Downloader & Saver is an all-in-one app to save videos, reels and stories you have the right to keep, and watch them offline. It is free on Google Play."),
           ("Is it legal to download videos?",
            "You should only download or save content you own or have permission to use, and respect copyright and each platform's terms of service.")],
 },
 "whatsapp-status-saver-apps": {
   "title": "Best WhatsApp Status Saver Apps for Android",
   "intro": "Want to keep a WhatsApp status before it disappears? These status saver apps by Khalid Mustafa Tech let you save the photo and video statuses you can already view, in one tap. Save only content you are allowed to keep.",
   "members": ["eyecon-status-saver-360", "status-saver"],
   "faq": [("How do I save a WhatsApp status?",
            "Open a status saver app, view the status in WhatsApp first, then save the photo or video you are allowed to keep to your device."),
           ("Are these status saver apps free?",
            "Yes, these status saver apps are free to download on Google Play.")],
 },
 "android-utility-apps": {
   "title": "Best Android Utility Apps (Free & Useful)",
   "intro": "Handy everyday Android tools by Khalid Mustafa Tech — scan QR codes, control your flashlight, take notes, track money, split videos and convert video to MP3. Simple, useful and free on Google Play.",
   "members": ["barcode-scanner", "flashlight-alert", "noteora-notes", "ledger-x-360", "video-splitter-360", "video-to-mp3", "screen-recorder-pro-x", "keeplock"],
   "faq": [("What are the best free utility apps for Android?",
            "Popular free utilities by Khalid Mustafa Tech include a QR & barcode scanner, flashlight with alerts, notes app, money ledger, video splitter and a video-to-MP3 converter."),
           ("Are these apps free?",
            "Yes, these utility apps are free to download on Google Play.")],
 },
 "android-games": {
   "title": "Fun Free Android Games to Play",
   "intro": "Light, addictive Android games by Khalid Mustafa Tech — arrow puzzles, tilt-maze challenges and colourful match-3 fun. Easy to pick up, hard to put down, and free on Google Play.",
   "members": ["arrow-game", "sink-hole-teeter", "arrow-maze-zig-arrow", "fruit-match-puzzle", "gem-blast-match-3"],
   "faq": [("What are some fun free Android games?",
            "Try Arrow Game, Sink Hole, Arrow Maze and the match-3 games Fruit Match Puzzle and Gem Blast — all free, casual Android games by Khalid Mustafa Tech."),
           ("Do these games cost anything?",
            "No, these games are free to download and play on Google Play.")],
 },
}

def card(a):
    actions = (f'<a class="btn install" href="{esc(a["play"])}">{PLAY_SVG}<span>Install Now</span></a>'
               if a["play"] else '<span class="badge soon">Coming soon</span>')
    return (f'<div class="card reveal">\n'
      f'  <img class="icon" src="../{esc(a["icon"])}" alt="{esc(a["name"])}" loading="lazy" width="60" height="60">\n'
      f'  <div class="card-body">\n    <h3>{esc(a["name"])}</h3>\n'
      f'    <p class="tagline">{esc(a["tagline"])}</p>\n    <p class="desc">{esc(a["desc"])}</p>\n'
      f'    <div class="card-actions">{actions}<a class="btn ghost" href="../detail/{a["slug"]}.html">Details</a></div>\n'
      f'  </div></div>')

FAQ_STYLE = ('<style>.faq{max-width:760px;margin:6px auto 64px;padding:0 20px}'
 '.faq h2{font-family:"Space Grotesk",sans-serif;font-size:24px;margin:0 0 16px}'
 '.faq details{border:1px solid rgba(255,255,255,.09);border-radius:12px;margin:0 0 10px;background:rgba(23,30,48,.6);overflow:hidden}'
 '.faq summary{cursor:pointer;padding:15px 18px;font-weight:600;color:#eff3fa;list-style:none}'
 '.faq summary::-webkit-details-marker{display:none}.faq summary::after{content:"+";float:right;color:#9fabc2}'
 '.faq details[open] summary::after{content:"\\2013"}.faq .a{padding:0 18px 16px;color:#9fabc2}</style>')

import json
def ld(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False) + '</script>'

def build():
    apps = parse_apps()
    cat_links = []
    for cslug, c in CATS.items():
        members = [apps[m] for m in c["members"] if m in apps]
        canon = BASE + "best/" + cslug + ".html"
        title = c["title"]; desc = c["intro"][:155]
        cards = "\n".join(card(a) for a in members)
        faq_items = "".join(f'<details><summary>{esc(q)}</summary><div class="a">{esc(a)}</div></details>' for q, a in c["faq"])
        itemlist = ld({"@context":"https://schema.org","@type":"ItemList","name":title,
            "itemListElement":[{"@type":"ListItem","position":i+1,"url":canon,
              "name":a["name"]} for i,a in enumerate(members)]})
        faqld = ld({"@context":"https://schema.org","@type":"FAQPage",
            "mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in c["faq"]]})
        page = f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Khalid Mustafa Tech</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canon)}">
<meta name="theme-color" content="#060910">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="Khalid Mustafa Tech">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canon)}"><meta property="og:image" content="{OG_IMG}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{OG_IMG}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="../style.css?v=4">
{itemlist}
{faqld}
</head><body>
<header class="site-head"><div class="wrap">
  <a class="brand" href="../index.html"><span class="logo-mark">KM</span><span><b>Khalid Mustafa Tech</b></span></a>
  <nav><a href="../index.html">Apps</a><a href="https://play.google.com/store/apps/developer?id=Khalid+Mustafa+Tech">Google Play</a></nav>
</div></header>
<main class="wrap">
<section class="hero" style="padding:40px 0 10px">
  <h1>{esc(c["title"])}</h1>
  <p>{esc(c["intro"])}</p>
</section>
<section class="sec"><div class="sec-head"><span class="dot"></span><h2>Apps in this category</h2><span class="count">{len(members)}</span></div>
<div class="grid">
{cards}
</div></section>
{FAQ_STYLE}<section class="faq"><h2>Frequently asked questions</h2>{faq_items}</section>
</main>
<footer class="site-foot"><div class="wrap">
  <a class="brand" href="../index.html"><span class="logo-mark">KM</span><span><b>Khalid Mustafa Tech</b></span></a>
  <p>Useful Android apps &mdash; crafted with care.</p>
  <p><a href="https://play.google.com/store/apps/developer?id=Khalid+Mustafa+Tech">Developer on Google Play</a> &middot; <a href="mailto:masterabdullahkhalid@gmail.com">masterabdullahkhalid@gmail.com</a></p>
  <p>&copy; 2026 Khalid Mustafa Tech. All trademarks belong to their respective owners.</p>
</div></footer>
<script>document.addEventListener('DOMContentLoaded',function(){{var els=document.querySelectorAll('.reveal');if(!('IntersectionObserver'in window)){{els.forEach(function(e){{e.classList.add('in')}});return;}}var io=new IntersectionObserver(function(en){{en.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target);}}}})}},{{threshold:.1}});els.forEach(function(e,i){{e.style.transitionDelay=(Math.min(i,8)*55)+'ms';io.observe(e);}});}});</script>
</body></html>
'''
        os.makedirs(os.path.join(ROOT, "best"), exist_ok=True)
        open(os.path.join(ROOT, "best", cslug + ".html"), "w", encoding="utf-8").write(page)
        cat_links.append((cslug, c["title"]))
    print("category pages:", len(cat_links))

    # ---- link categories from index.html (idempotent) ----
    idx_path = os.path.join(ROOT, "index.html")
    idx = open(idx_path, encoding="utf-8").read()
    if 'id="categories"' not in idx:
        links = "".join(f'<a class="btn ghost" href="best/{s}.html">{esc(t)}</a>' for s, t in cat_links)
        sec = (f'<section class="sec" id="categories"><div class="sec-head"><span class="dot"></span>'
               f'<h2>Browse by category</h2></div>'
               f'<div class="hero-cta" style="flex-wrap:wrap;justify-content:flex-start">{links}</div></section>\n</main>')
        idx = idx.replace("</main>", sec, 1)
        open(idx_path, "w", encoding="utf-8").write(idx)
        print("linked categories from index.html")
    else:
        print("index already links categories")

    # ---- refresh sitemap to include best/ ----
    today = datetime.date.today().isoformat()
    urls = [("", "1.0")]
    for p in sorted(glob.glob(os.path.join(ROOT, "best", "*.html"))): urls.append(("best/"+os.path.basename(p), "0.9"))
    for p in sorted(glob.glob(os.path.join(ROOT, "detail", "*.html"))): urls.append(("detail/"+os.path.basename(p), "0.8"))
    for p in sorted(glob.glob(os.path.join(ROOT, "privacy", "*.html"))): urls.append(("privacy/"+os.path.basename(p), "0.5"))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pr in urls: sm.append(f"  <url><loc>{BASE}{loc}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm)+"\n")
    print("sitemap.xml:", len(urls), "urls")

if __name__ == "__main__":
    build()
