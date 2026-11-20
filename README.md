# KMTech Apps & Privacy Policies

Static website (GitHub Pages) for the Android apps by **Khalid Mustafa Tech** — a landing page listing every app plus a dedicated **privacy policy** page for each (the URL you paste into the Google Play Console "Privacy Policy" field).

## Structure
```
index.html          landing page (all apps, grouped)
style.css           shared styles (light + dark)
privacy/<app>.html  one privacy policy page per app
```

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
