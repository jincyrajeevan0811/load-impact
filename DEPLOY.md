# Deploying LoadImpact

## Option A — Render (recommended)

The repository is ready for Render: `requirements.txt` (with gunicorn, whitenoise, PostgreSQL driver),
`build.sh` (installs, migrates, collects static files, loads starting content) and `render.yaml`.

### A1. If you already created a Web Service manually
Open your service on https://dashboard.render.com → **Settings**:

| Setting | Value |
|---|---|
| **Build Command** | `bash build.sh` |
| **Start Command** | `gunicorn loadimpact.wsgi:application` |

Then **Environment** → add these variables:

| Key | Value |
|---|---|
| `PYTHON_VERSION` | `3.12.7` |
| `DJANGO_SECRET_KEY` | any long random text (click *Generate*) |
| `DJANGO_ADMIN_PASSWORD` | a strong password for the `admin` login |
| `DATABASE_URL` | *(recommended)* the **Internal Database URL** of a Render PostgreSQL database |

Save, then **Manual Deploy → Deploy latest commit**.

### A2. Or create everything in one go (Blueprint)
Render → **New → Blueprint** → choose `jincyrajeevan0811/load-impact` → enter a value for
`DJANGO_ADMIN_PASSWORD` → **Apply**. This creates the web service *and* a free PostgreSQL database.
(Delete the old manually-created service afterwards so you don't have two.)

### After deploying
- Your site: `https://<service-name>.onrender.com`
- Admin: `/admin-panel/` — username `admin`, password = `DJANGO_ADMIN_PASSWORD`
- Every `git push` to `main` redeploys automatically (Auto-Deploy is on by default).

### Free-plan notes
- The free web service **sleeps after 15 minutes without visitors**; the first visit afterwards takes ~1 minute.
- **Without `DATABASE_URL`**, the site uses SQLite, which is **wiped on every deploy/restart**
  (members, payments and changes you make in Appearance are lost). Add a Render PostgreSQL database to keep data.
- Render's free PostgreSQL database expires after 30 days unless upgraded; Render emails you before that.
- Uploaded photos (logo, trainer photos) are stored on the server disk and are also lost on redeploy on the
  free plan. For permanent photos, paste image URLs in **Appearance**, or add a paid persistent disk.

## Option B — PythonAnywhere

See `deploy/pythonanywhere_wsgi.py` and `deploy/update.sh`. In short: clone the repo in a Bash console,
`mkvirtualenv --python=/usr/bin/python3.10 loadimpact-env`, `pip install -r requirements.txt`,
`makemigrations accounts gym appearance`, `migrate`, `collectstatic`, `seed_demo`, then create a
*Manual configuration* web app, paste the WSGI file, and map `/static/` → `staticfiles` and `/media/` → `media`.
