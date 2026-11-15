# LoadImpact – Unisex Gym Website (Django)

A complete gym management website built with plain Django (no extra frameworks):
a public website, a **member (user) module**, and a full **admin dashboard**.

## Features

### Public website
- Home, About, Membership Plans, Trainers, Weekly Class Schedule, Contact pages
- Contact form (messages go to the admin dashboard inbox)
- Responsive design (Bootstrap 5, Bootstrap Icons, Chart.js – loaded from CDN)

### Member module (`/member/`)
- Register, log in / log out, forgot password (reset link printed to the console in development), change password
- Profile with photo, phone, gender, date of birth, height, weight, **BMI**, fitness goal, emergency contact
- Member dashboard: active plan with days remaining and progress, visits, classes attended, BMI, announcements
- Buy or renew a membership plan (cash / UPI / card / bank transfer → admin confirms, then the plan activates)
- Book weekly group classes (seat limits, cancel bookings)
- Membership history, payment history and **printable invoices**
- Attendance history

### Admin dashboard (`/admin-panel/`)
- **Dashboard**: KPIs (members, active memberships, monthly and lifetime revenue, pending payments, check-ins, people in the gym now, unread messages), revenue and sign-up chart, gender chart, approvals queue, memberships expiring in the next 7 days, today's classes, recent payments and members
- **Members**: search, filter, add, edit, enable/disable, delete, reset password, check in/out, export to CSV, staff list
- **Membership plans**: create, edit, delete, hide, mark as popular
- **Memberships**: assign a plan to a member (optionally recording the payment), approve/activate, cancel, edit dates
- **Payments**: record, edit, mark as paid (activates the linked membership automatically), filters, totals, CSV export, invoices
- **Trainers** and **class schedule**: full create / edit / delete
- **Bookings**: filter by date, class and status; mark as attended, missed or cancelled
- **Attendance**: front-desk check-in and check-out, daily log, edit and delete
- **Messages** inbox and **announcements** (shown on the website and member dashboards)
- **Reports**: revenue by plan and by payment method, most-booked classes, membership status, for any date range
- Superusers also get Django's built-in database admin at `/django-admin/`

## Setup

You need Python 3.10 or newer.

```bash
cd loadimpact
python -m venv venv
# Windows: venv\Scripts\activate      macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

python manage.py makemigrations accounts gym appearance
python manage.py migrate
python manage.py seed_demo          # optional demo data + login accounts
python manage.py runserver
```

Then open http://127.0.0.1:8000/

| Role   | Username | Password    | Where to go                        |
|--------|----------|-------------|------------------------------------|
| Admin  | admin    | Admin@123   | http://127.0.0.1:8000/admin-panel/ |
| Member | member   | Member@123  | http://127.0.0.1:8000/member/dashboard/ |

If you didn't run `seed_demo`, create your own admin with `python manage.py createsuperuser`.
Staff users always land on the admin dashboard after logging in; members land on their dashboard.

## How the membership flow works

1. A member picks a plan → a **pending** membership and a **pending** payment are created.
2. An admin confirms the payment on the dashboard (**Approve** or **Mark paid**) → the membership becomes **active**.
   If the member already has an active plan, the new one starts the day after it ends (renewal).
3. Memberships whose end date has passed are marked **expired** automatically.
4. Only members with an active membership can book classes.

## Project structure

```
loadimpact/
├── loadimpact/        # settings, root urls, wsgi/asgi
├── accounts/          # registration, login, profile (Profile model)
├── gym/               # core models + public pages + seed_demo command
├── members/           # member area (dashboard, bookings, billing, attendance)
├── dashboard/         # custom admin dashboard (staff only)
├── templates/         # all HTML templates
└── static/            # css / js
```

## Appearance manager (Admin → Appearance)

Everything you see on the website can be changed from the admin dashboard, no code needed:

- **Branding & Logo** – gym name, tagline, logo text or an uploaded logo image, icon, favicon, header button text,
  SEO description, loading screen and animations on/off
- **Colours & Fonts** – website colours (primary, secondary, accent, background, cards, text) with ready-made themes
  and a live preview, heading/body fonts, and the **admin dashboard colours** (primary, secondary, sidebar, default light/dark)
- **Pages & Sections** – every section of Home, About, Plans, Trainers, Schedule, Contact and the Login/Sign-up panel:
  edit text, buttons and images (upload or URL), add/edit/delete cards, FAQ questions, gallery photos, counters, etc.,
  show/hide sections, move them up/down, or reset one to its default
- **Navigation** – header menu and footer links: add, edit, reorder, hide, open in new tab
- **Contact & Footer** – phone, WhatsApp, email, address, hours, currency, UPI ID, social links and all footer text

Staff also see an **"Edit this page"** button on every public page that jumps straight to that page's sections.

In text, `{members}`, `{trainers}` and `{classes}` are replaced with live numbers (used by the counters).

## User interface

- Dark, premium design with glass effects, gradient accents and Bebas Neue / Poppins fonts
- Animations: preloader, scroll-reveal sections, animated counters, typewriter hero text, Ken Burns photo zoom,
  3D tilt cards, mouse parallax, scrolling marquee, animated pricing border, scroll progress bar and back-to-top ring
- Home page: hero, programs, about, counters, pricing, **live BMI calculator**, trainers, gallery, announcements, call to action
- Schedule with day tabs (opens on today), contact page with map, split-screen login and sign-up
- Member area with progress ring for days left; admin dashboard with **light/dark mode toggle**, live clock,
  animated KPIs and gradient charts
- Animations are switched off automatically for visitors who turn on "reduce motion" on their device

## Customising

- **Everything visual:** Admin dashboard → **Appearance** (see above). Upload your own photos per section there.
- `GYM_INFO` / `GYM_IMAGES` in `loadimpact/settings.py` only provide the starting values the first time the site runs.

## Going live

Set the environment variables `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` and `DJANGO_ALLOWED_HOSTS=yourdomain.com`,
run `python manage.py collectstatic`, serve static and media files with your web server (e.g. Nginx),
configure a real email backend for password resets, and consider PostgreSQL instead of SQLite.
