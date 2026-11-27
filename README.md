# KMTech Apps & Privacy Policies

Static website (GitHub Pages) for the Android apps by **Khalid Mustafa Tech** — a landing page listing every app plus a dedicated **privacy policy** page for each (the URL you paste into the Google Play Console "Privacy Policy" field).

## Structure
```
index.html           landing page (all apps, search, hero, grouped)
about.html           about / developer page
404.html             custom not-found page
style.css            shared styles (dark)
manifest.webmanifest PWA manifest
sitemap.xml          generated sitemap
robots.txt           crawler rules + sitemap pointer
favicon.svg          brand icon
assets/              hero.jpg, og.png, logo.png, icons/
best/<cat>.html      SEO category landing pages ("best call recorder", etc.)
detail/<app>.html    one detail page per app
privacy/<app>.html   one privacy policy page per app
scripts/             re-runnable SEO build scripts (see below)
```

## SEO build scripts (run after adding or editing apps)
All idempotent — safe to re-run; they only add what's missing.
```bash
python scripts/build_seo.py          # sitemap + OG/meta + SoftwareApplication + FAQ schema
python scripts/build_categories.py   # best/ category pages + link them from the home page
python scripts/build_internal.py     # breadcrumbs (+schema), related-apps linking, sitemap
```
After adding a new app: create its `detail/<slug>.html` + `privacy/<slug>.html`, add its card to
`index.html`, add its entry to `_content.json`, then run the three scripts above and commit.

The one-off share image (`assets/og.png`) and `assets/logo.png` are generated with small PIL
scripts and committed; they only need regenerating if the branding changes.

## Privacy policy URL per app
Once GitHub Pages is live, each app's policy URL is:
```
https://masterabdullahkhalid-oss.github.io/kmtech-apps-site/privacy/<app>.html
```
e.g. PinSaver → `.../privacy/pingrab.html`, SpotGrab → `.../privacy/snapgrab.html`.

## How to publish (one-time)
1. Create a new **empty** public repo on GitHub named `kmtech-apps-site` (no README/License).
2. From this folder:
   ```bash
   git remote add origin https://github.com/masterabdullahkhalid-oss/kmtech-apps-site.git
   git push -u origin main
   ```
3. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / `/ (root)` → Save.**
4. Wait ~1 minute; the site goes live at the URL above.

## Updating
Edit the matching `PRIVACY_<app>.md` in the app repo, re-run the generator, then `git add -A && git commit && git push`.
