# Putting the website online (free)

The website in `site/` is static: HTML, CSS, JavaScript and JSON data files. It has no server, no database and no API keys, so it can be hosted free anywhere. Everything it shows comes from `site/data/*.json`, which `pipeline/export_site.py` writes.

## Option A: Vercel (recommended; works with this private repository)

1. Go to **https://vercel.com** and sign up with **Continue with GitHub**.
2. Click **Add New → Project**, choose `arventum-deal-intelligence`, and grant access to that one repository.
3. Under **Root Directory**, choose `site`. Framework preset: **Other**. Leave the build command empty.
4. Click **Deploy**. It takes under a minute. Vercel gives you a URL such as `deal-intelligence.vercel.app`.

Every push to `main` redeploys automatically. Vercel's free plan also offers password protection on preview links, if the page should not be public.

## Option B: Netlify Drop (no account linking)

Go to **https://app.netlify.com/drop** and drag the `site` folder onto the page. You get a URL immediately. To update it, drag the folder again.

## Option C: GitHub Pages

This works only if the repository is public on a free GitHub plan. In **Settings → Pages**, choose to deploy from the `main` branch. Pages serves only the repository root or a `/docs` folder, not `/site`, so it needs a small GitHub Actions workflow to publish `site/`. Prefer Option A while the repository is private.

## Refreshing the data

```
python pipeline/run_all.py
python pipeline/export_site.py
```

Then commit and push `site/data/`. With Option A, the site updates by itself.

To check locally before pushing, run `python analysis/serve_site.py` and open http://localhost:8600.

## The earlier Streamlit app

`app/Home.py` still runs (`streamlit run app/Home.py`) and can be deployed on Streamlit Community Cloud with main file `app/Home.py`. The static site replaces it for presenting.
