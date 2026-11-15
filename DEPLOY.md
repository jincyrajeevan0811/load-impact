# Host LoadImpact for free on PythonAnywhere

Your site will be live at **https://YOUR_USERNAME.pythonanywhere.com** (about 15 minutes, no card needed).

## 1. Create the free account
1. Go to https://www.pythonanywhere.com/registration/register/beginner/
2. Pick your username carefully — it becomes the web address (e.g. `loadimpact` → `loadimpact.pythonanywhere.com`).
3. Confirm your email.

## 2. Get the code and set it up (Bash console)
On the **Dashboard**, under *New console*, click **$ Bash**, then paste these lines one block at a time:

```bash
git clone https://github.com/jincyrajeevan0811/load-impact.git
cd load-impact
mkvirtualenv --python=/usr/bin/python3.10 loadimpact-env
pip install -r requirements.txt
```

```bash
python manage.py makemigrations accounts gym appearance
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo --admin-password "CHOOSE-A-STRONG-PASSWORD"
```

> Use a strong admin password — this site is public. (Or skip `seed_demo` and run
> `python manage.py createsuperuser` to make your own admin account.)

## 3. Create the web app (Web tab)
1. Open the **Web** tab → **Add a new web app** → *Next* → choose **Manual configuration** (not "Django") → **Python 3.10** → *Next*.
2. In the **Code** section set:
   - **Source code:** `/home/YOUR_USERNAME/load-impact`
   - **Working directory:** `/home/YOUR_USERNAME/load-impact`
3. In the **Virtualenv** section enter: `/home/YOUR_USERNAME/.virtualenvs/loadimpact-env`
4. Click the **WSGI configuration file** link, delete everything in it, paste the contents of
   [`deploy/pythonanywhere_wsgi.py`](deploy/pythonanywhere_wsgi.py), replace `YOUR_USERNAME` (2 places) and the secret key, then **Save**.
5. In **Static files** add two rows:

   | URL        | Directory                                        |
   |------------|--------------------------------------------------|
   | `/static/` | `/home/YOUR_USERNAME/load-impact/staticfiles`    |
   | `/media/`  | `/home/YOUR_USERNAME/load-impact/media`          |

6. Under **Security**, turn **Force HTTPS** on.
7. Click the big green **Reload** button at the top, then open your link. 🎉

## Updating the live site after changes
Whenever new code is pushed to GitHub, open a Bash console on PythonAnywhere and run:

```bash
bash ~/load-impact/deploy/update.sh
```

Then click **Reload** on the Web tab.

## Good to know (free plan)
- Free sites must be kept alive: log in at least once every **3 months** and click
  **"Run until 3 months from today"** on the Web tab.
- Password-reset emails are printed to the server log, not sent. Add a real email
  service (e.g. Gmail SMTP) in `settings.py` if you need them.
- Your database (`db.sqlite3`) and uploaded photos (`media/`) live only on PythonAnywhere —
  they are not in GitHub, so `git pull` never overwrites them.
- If something shows an error page, check the **error log** link on the Web tab.
