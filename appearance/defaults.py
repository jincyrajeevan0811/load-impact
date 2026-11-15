"""
Default content for every editable page section, plus which fields the admin
editor shows for each section type. Used to create the sections the first time
the site runs (and when a section is "reset to default").
"""
from django.conf import settings

IMG = getattr(settings, "GYM_IMAGES", {})


def _img(key):
    return IMG.get(key, "")


def _gallery(i):
    gallery = IMG.get("gallery", [])
    return gallery[i] if i < len(gallery) else ""


# ---------------------------------------------------------------------------
# Default sections, per page, in display order
# ---------------------------------------------------------------------------
SECTION_DEFAULTS = {
    "home": [
        dict(
            key="hero", name="Hero banner",
            eyebrow="Premium unisex fitness studio", title="Build your",
            extra="STRENGTH|STAMINA|CONFIDENCE|BEST SELF", highlight="Feel the impact",
            subtitle="Modern equipment, certified male & female coaches and high-energy group classes. "
                     "Whether it's your first workout or your next PR — this is where it happens.",
            image_url=_img("hero"), image_2_url=_img("about"),
            button_text="Start Your Journey", button_url="/accounts/register/",
            button_2_text="View Classes", button_2_url="/schedule/",
            items=[
                dict(icon="bi-clock-history", title="Open 7 days", text="5:00 AM – 10:00 PM"),
                dict(icon="bi-patch-check-fill", title="Certified coaches", text="Male & female trainers"),
                dict(icon="bi-phone", title="Book online", text="Reserve your spot in seconds"),
            ],
        ),
        dict(
            key="marquee", name="Scrolling text strip",
            items=[dict(title=w) for w in [
                "Strength Training", "Cardio", "Yoga", "HIIT", "Zumba", "CrossFit", "Personal Training", "Weight Loss",
            ]],
        ),
        dict(
            key="programs", name="Programs",
            eyebrow="What we offer", title="Programs built for", highlight="every goal",
            subtitle="From heavy lifting to mindful movement, each zone is designed for results — and open to everyone, every day.",
            items=[
                dict(label="01 / Strength", title="Strength Zone", url="/schedule/", image_url=_img("strength"),
                     text="Power racks, Olympic platforms, dumbbells up to 50 kg and plate-loaded machines."),
                dict(label="02 / Cardio", title="Cardio Deck", url="/schedule/", image_url=_img("cardio"),
                     text="Treadmills, rowers, air bikes and a dedicated HIIT turf for maximum burn."),
                dict(label="03 / Classes", title="Group Classes", url="/schedule/", image_url=_img("classes"),
                     text="Zumba, yoga, CrossFit-style WODs and mobility — book online in seconds."),
                dict(label="04 / Coaching", title="Personal Training", url="/trainers/", image_url=_img("personal"),
                     text="One-to-one programs built around your body, schedule and goals."),
            ],
        ),
        dict(
            key="about", name="About / Why us",
            eyebrow="Why LoadImpact", title="A gym where everyone", highlight="belongs",
            subtitle="Our unisex floor brings men and women of all ages together in a safe, respectful and motivating "
                     "space. Expert coaching, clean equipment and a community that pushes you further.",
            image_url=_img("about"), image_2_url=_img("about_2"),
            badge_value="7", badge_text="Days a week open for you",
            button_text="Discover more", button_url="/about/",
            items=[
                dict(title="Safe & respectful", text="Zero-tolerance policy, CCTV and staff always on the floor."),
                dict(title="Male & female coaches", text="Train with whoever makes you most comfortable."),
                dict(title="Smart member portal", text="Book classes, track visits and renew plans online."),
            ],
        ),
        dict(
            key="stats", name="Counters",
            items=[
                dict(title="{members}+", text="Members"),
                dict(title="{trainers}", text="Trainers"),
                dict(title="{classes}", text="Classes / week"),
                dict(title="100%", text="Unisex friendly"),
            ],
        ),
        dict(
            key="plans", name="Membership plans",
            eyebrow="Membership", title="Pick a plan that", highlight="fits you",
            subtitle="No hidden fees. Full access to the unisex floor on every plan.",
            button_text="Compare all plans", button_url="/plans/",
        ),
        dict(
            key="bmi", name="BMI calculator",
            eyebrow="Free tool", title="Calculate your", highlight="BMI",
            subtitle="Body Mass Index is a quick way to see where you stand. Enter your height and weight to get your "
                     "score and a training suggestion.",
            button_text="Calculate",
        ),
        dict(
            key="trainers", name="Trainers",
            eyebrow="Our team", title="Meet your", highlight="coaches",
            button_text="All trainers", button_url="/trainers/",
        ),
        dict(
            key="gallery", name="Photo gallery",
            eyebrow="Inside LoadImpact", title="Feel the", highlight="vibe",
            items=[dict(title=f"Gallery photo {i + 1}", image_url=_gallery(i)) for i in range(6)],
        ),
        dict(
            key="announcements", name="Announcements",
            eyebrow="What's new", title="Latest", highlight="updates",
        ),
        dict(
            key="cta", name="Call to action",
            eyebrow="No more excuses", title="Your strongest self starts today",
            subtitle="Create your free account, choose a plan and book your first class in under two minutes.",
            image_url=_img("cta"),
            button_text="Join LoadImpact", button_url="/accounts/register/",
            button_2_text="Book a free visit", button_2_url="/contact/",
        ),
    ],
    "about": [
        dict(
            key="header", name="Page header", title="About LoadImpact",
            subtitle="A unisex gym where everyone belongs — built on expert coaching, real community and serious results.",
            image_url=_img("about"),
        ),
        dict(
            key="story", name="Our story",
            eyebrow="Our story", title="Built for", highlight="every body",
            subtitle="LoadImpact was founded on one simple idea: a gym should feel welcoming to everyone. Our unisex "
                     "facility brings together men and women of all ages and fitness levels in a safe, respectful and "
                     "motivating environment.\n\nFrom first-timers learning the basics to athletes chasing performance, "
                     "our certified coaches build programs that deliver real, measurable results.",
            image_url=_img("strength"), image_2_url=_img("classes"),
            badge_value="{trainers}", badge_text="Certified coaches",
            items=[
                dict(icon="bi-shield-check", title="Safe & respectful", text="CCTV, staff on floor, zero tolerance"),
                dict(icon="bi-gender-ambiguous", title="Truly unisex", text="Male & female trainers, separate changing rooms"),
                dict(icon="bi-droplet", title="Spotless facility", text="Equipment sanitised all day"),
                dict(icon="bi-phone", title="Online portal", text="Book classes & track progress"),
            ],
        ),
        dict(
            key="values", name="Mission, vision & promise",
            items=[
                dict(icon="bi-bullseye", title="Our Mission", text="Make quality fitness accessible, inclusive and genuinely enjoyable for everyone in our community."),
                dict(icon="bi-eye", title="Our Vision", text="A healthier, stronger and more confident community — one rep, one class, one member at a time."),
                dict(icon="bi-heart-pulse", title="Our Promise", text="Expert guidance, well-maintained equipment and a space where you always feel you belong."),
            ],
        ),
        dict(
            key="facilities", name="Facilities",
            eyebrow="Facilities", title="What's", highlight="inside",
            items=[
                dict(icon="bi-trophy", title="Free Weights"), dict(icon="bi-bicycle", title="Spin Studio"),
                dict(icon="bi-music-note-beamed", title="Group Studio"), dict(icon="bi-door-open", title="Lockers & Showers"),
                dict(icon="bi-wifi", title="Free Wi-Fi"), dict(icon="bi-cup-straw", title="Protein Bar"),
                dict(icon="bi-p-square", title="Parking"), dict(icon="bi-clipboard2-pulse", title="Body Assessment"),
            ],
        ),
        dict(
            key="cta", name="Call to action", title="Come see it for yourself",
            subtitle="Drop by for a free tour of the facility — no commitment.", image_url=_img("cta"),
            button_text="Plan your visit", button_url="/contact/",
        ),
    ],
    "plans": [
        dict(
            key="header", name="Page header", title="Membership Plans",
            subtitle="Simple pricing. No hidden fees. Full access to the unisex floor on every plan.",
            image_url=_img("cardio"),
        ),
        dict(key="grid", name="Plan cards", subtitle="Plans will be announced soon. Please contact us for details."),
        dict(
            key="perks", name="Payment perks",
            items=[
                dict(icon="bi-cash-coin", title="Pay your way", text="Cash, UPI, debit/credit card or bank transfer."),
                dict(icon="bi-lightning", title="Quick activation", text="Your plan goes live as soon as payment is confirmed."),
                dict(icon="bi-arrow-repeat", title="Easy renewals", text="Renew early — your new plan starts when the current one ends."),
            ],
        ),
        dict(
            key="faq", name="FAQ", eyebrow="FAQ", title="Questions?",
            items=[
                dict(title="Is the gym open to both men and women at the same time?",
                     text="Yes — LoadImpact is a fully unisex gym. We have male and female trainers and separate changing rooms."),
                dict(title="How do I activate my membership?",
                     text="Create an account, choose a plan and pay at the front desk or online. Your plan becomes active once the payment is confirmed."),
                dict(title="Are group classes included?",
                     text="Any active member can book classes from their dashboard. Check each plan's features for what's included."),
            ],
        ),
    ],
    "trainers": [
        dict(
            key="header", name="Page header", title="Our Trainers",
            subtitle="Certified male and female coaches dedicated to your progress.", image_url=_img("personal"),
        ),
        dict(key="grid", name="Trainer cards", subtitle="Trainer profiles coming soon."),
        dict(
            key="cta", name="Call to action", title="Want a personal coach?",
            subtitle="Tell us your goal and we'll match you with the right trainer.", image_url=_img("cta"),
            button_text="Talk to us", button_url="/contact/",
        ),
    ],
    "schedule": [
        dict(
            key="header", name="Page header", title="Weekly Schedule",
            subtitle="All classes are open to everyone. Members can reserve their spot online.", image_url=_img("classes"),
        ),
        dict(key="timetable", name="Timetable", title="Open gym day",
             subtitle="No group classes — the floor is all yours.", button_text="Book a Class"),
    ],
    "contact": [
        dict(
            key="header", name="Page header", title="Get in Touch",
            subtitle="Questions about plans, a free trial or personal training? We'd love to hear from you.",
            image_url=_img("page_header"),
        ),
        dict(key="info", name="Contact cards"),
        dict(key="form", name="Contact form", eyebrow="Send a message", title="We reply within a day", button_text="Send Message"),
        dict(key="map", name="Map", extra=""),
    ],
    "auth": [
        dict(
            key="login", name="Login & sign-up side panel",
            eyebrow="LoadImpact Members", title="Every rep", highlight="counts.",
            subtitle="Book classes, track your visits and manage your membership — all in one place.",
            image_url=_img("auth"),
        ),
    ],
}

NAV_DEFAULTS = [
    ("header", "Home", "/"), ("header", "About", "/about/"), ("header", "Plans", "/plans/"),
    ("header", "Trainers", "/trainers/"), ("header", "Schedule", "/schedule/"), ("header", "Contact", "/contact/"),
    ("footer", "About Us", "/about/"), ("footer", "Membership Plans", "/plans/"), ("footer", "Trainers", "/trainers/"),
    ("footer", "Class Schedule", "/schedule/"), ("footer", "Contact", "/contact/"),
]

PAGE_PATHS = {
    "home": "/", "about": "/about/", "plans": "/plans/", "trainers": "/trainers/",
    "schedule": "/schedule/", "contact": "/contact/", "auth": "/accounts/login/",
}

# ---------------------------------------------------------------------------
# Which fields the editor shows for each section key
# ---------------------------------------------------------------------------
HEAD = ["eyebrow", "title", "highlight", "subtitle"]
IMG1 = ["image", "image_url"]
IMG2 = ["image_2", "image_2_url"]
BTN1 = ["button_text", "button_url"]
BTN2 = ["button_2_text", "button_2_url"]

SECTION_FIELDS = {
    "hero": HEAD + ["extra"] + IMG1 + IMG2 + BTN1 + BTN2,
    "marquee": [],
    "programs": HEAD,
    "about": HEAD + IMG1 + IMG2 + ["badge_value", "badge_text"] + BTN1,
    "stats": [],
    "plans": HEAD + BTN1,
    "bmi": HEAD + ["button_text"],
    "trainers": HEAD + BTN1,
    "gallery": HEAD,
    "announcements": HEAD,
    "cta": ["eyebrow", "title", "subtitle"] + IMG1 + BTN1 + BTN2,
    "header": ["title", "subtitle"] + IMG1,
    "story": HEAD + IMG1 + IMG2 + ["badge_value", "badge_text"],
    "values": [],
    "facilities": ["eyebrow", "title", "highlight"],
    "grid": ["subtitle"],
    "perks": [],
    "faq": ["eyebrow", "title"],
    "timetable": ["title", "subtitle", "button_text"],
    "info": [],
    "form": ["eyebrow", "title", "button_text"],
    "map": ["extra"],
    "login": HEAD + IMG1,
}

# Custom labels / help per section key
FIELD_LABELS = {
    "hero": {
        "title": "Title (first line)",
        "extra": "Rotating words (separate with |)",
        "highlight": "Outlined last line",
        "image": "Background photo (upload)", "image_url": "…or background photo URL",
        "image_2": "Round photo (upload)", "image_2_url": "…or round photo URL",
    },
    "timetable": {"title": "Title for days without classes", "subtitle": "Text for days without classes"},
    "grid": {"subtitle": "Message when the list is empty"},
    "map": {"extra": "Map location (leave blank to use the gym address)"},
    "form": {"button_text": "Send button text"},
    "bmi": {"button_text": "Calculate button text"},
}

TOKEN_HELP = "You can use {members}, {trainers} and {classes} to show live numbers."

# Item fields per section key: (fields, singular name, help)
ITEM_FIELDS = {
    "hero": (["icon", "title", "text"], "floating card", ""),
    "marquee": (["title"], "word", ""),
    "programs": (["label", "title", "text", "image", "image_url", "url"], "program card", ""),
    "about": (["title", "text"], "checklist point", ""),
    "stats": (["title", "text"], "counter", "Title = number, Text = label. " + TOKEN_HELP),
    "gallery": (["title", "image", "image_url"], "photo", "Title is used as the image description."),
    "story": (["icon", "title", "text"], "feature", ""),
    "values": (["icon", "title", "text"], "card", ""),
    "facilities": (["icon", "title"], "facility", ""),
    "perks": (["icon", "title", "text"], "perk", ""),
    "faq": (["title", "text"], "question", "Title = question, Text = answer."),
}

SECTION_HELP = {
    "plans": "The plan cards come from Dashboard → Membership Plans.",
    "trainers": "The trainer cards come from Dashboard → Trainers.",
    "announcements": "The posts come from Dashboard → Announcements. The section hides itself when there are none.",
    "grid": "The cards themselves are managed in the dashboard (Plans / Trainers).",
    "timetable": "Classes come from Dashboard → Class Schedule.",
    "info": "Shows the address, phone, email and hours from Appearance → Contact & Footer.",
    "stats": TOKEN_HELP,
    "about": "Badge value: " + TOKEN_HELP,
    "story": "Badge value: " + TOKEN_HELP,
    "map": "Uses Google Maps.",
}
