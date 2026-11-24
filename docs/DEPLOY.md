# Putting the website online (Streamlit Community Cloud, free)

The app reads only files already in this repository (`db/deals.db`, `data/processed/*`), so no API keys or secrets are needed.

1. Go to **https://share.streamlit.io** and click **Continue with GitHub** (use the account that owns this repository).
2. Allow Streamlit to access your repositories. The repository is private, so grant access to `arventum-deal-intelligence`.
3. Click **Create app** → **Deploy a public app from GitHub**.
4. Fill in:
   - **Repository:** `<your-github-username>/arventum-deal-intelligence`
   - **Branch:** `main`
   - **Main file path:** `app/Home.py`
   - **App URL:** choose something like `arventum-deal-intelligence`
5. Click **Deploy**. The first build takes 2–4 minutes while it installs `requirements.txt`.

**Who can see it:** a Streamlit app deployed from a private repository can still be viewable by anyone with the link, depending on your sharing settings. In the app's **Settings → Sharing** you can restrict it to specific email addresses (for example, the Arventum founders).

**Updating:** every push to `main` redeploys automatically. To refresh the data, run `python pipeline/run_all.py --refresh` locally, then commit and push.
