from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

hex_color = RegexValidator(r"^#[0-9a-fA-F]{6}$", "Enter a colour like #ff5a1f.")

HEADING_FONTS = {
    "Bebas Neue": ("Bebas+Neue", 400),
    "Oswald": ("Oswald:wght@500;600;700", 600),
    "Anton": ("Anton", 400),
    "Teko": ("Teko:wght@500;600", 600),
    "Montserrat": ("Montserrat:wght@600;700;800", 800),
    "Poppins": ("Poppins:wght@600;700;800", 700),
}
BODY_FONTS = {
    "Poppins": "Poppins:wght@300;400;500;600;700",
    "Inter": "Inter:wght@300;400;500;600;700",
    "Roboto": "Roboto:wght@300;400;500;700",
    "Open Sans": "Open+Sans:wght@300;400;500;600;700",
    "Lato": "Lato:wght@300;400;700",
    "Nunito": "Nunito:wght@300;400;600;700",
    "Montserrat": "Montserrat:wght@300;400;500;600;700",
}


def _hex_to_rgb(value, fallback="255, 90, 31"):
    try:
        v = value.lstrip("#")
        return ", ".join(str(int(v[i:i + 2], 16)) for i in (0, 2, 4))
    except (ValueError, AttributeError, IndexError):
        return fallback


def _mix_with_white(value, amount=0.05):
    try:
        v = value.lstrip("#")
        rgb = [int(v[i:i + 2], 16) for i in (0, 2, 4)]
        mixed = [round(c + (255 - c) * amount) for c in rgb]
        return "#" + "".join(f"{c:02x}" for c in mixed)
    except (ValueError, AttributeError, IndexError):
        return value


class SiteSettings(models.Model):
    """Single row holding branding, colours, contact details and footer content."""

    THEME_CHOICES = [("light", "Light"), ("dark", "Dark")]

    # Branding
    site_name = models.CharField(max_length=100, default="LoadImpact")
    brand_text_1 = models.CharField("Logo text (white part)", max_length=40, default="LOAD")
    brand_text_2 = models.CharField("Logo text (coloured part)", max_length=40, default="IMPACT", blank=True)
    tagline = models.CharField(max_length=150, default="Unisex Fitness Studio")
    logo = models.ImageField(
        upload_to="branding/", blank=True, null=True,
        help_text="Optional. A PNG/SVG with a transparent background replaces the icon + text logo.",
    )
    logo_height = models.PositiveIntegerField("Logo height (px)", default=42)
    brand_icon = models.CharField(
        max_length=60, default="bi-lightning-charge-fill",
        help_text='Icon shown when no logo is uploaded. Any Bootstrap Icons name, e.g. "bi-trophy-fill".',
    )
    favicon = models.ImageField(upload_to="branding/", blank=True, null=True, help_text="Small square image for the browser tab.")
    meta_description = models.CharField(
        "SEO description", max_length=255, blank=True,
        default="LoadImpact is a modern unisex gym offering strength training, cardio, group classes and personal training.",
    )
    nav_cta_text = models.CharField("Header button text", max_length=40, default="Join Now")
    show_preloader = models.BooleanField("Show loading screen", default=True)
    enable_animations = models.BooleanField("Enable scroll animations", default=True)

    # Website colours & fonts
    primary_color = models.CharField(max_length=7, default="#ff5a1f", validators=[hex_color])
    secondary_color = models.CharField(max_length=7, default="#ff2d55", validators=[hex_color])
    accent_color = models.CharField(max_length=7, default="#ffb020", validators=[hex_color])
    background_color = models.CharField(max_length=7, default="#0a0b0f", validators=[hex_color])
    surface_color = models.CharField("Card colour", max_length=7, default="#12141b", validators=[hex_color])
    text_color = models.CharField(max_length=7, default="#e9ecf2", validators=[hex_color])
    heading_font = models.CharField(max_length=40, default="Bebas Neue", choices=[(k, k) for k in HEADING_FONTS])
    body_font = models.CharField(max_length=40, default="Poppins", choices=[(k, k) for k in BODY_FONTS])

    # Admin dashboard colours
    dash_primary_color = models.CharField("Dashboard primary", max_length=7, default="#ff5a1f", validators=[hex_color])
    dash_secondary_color = models.CharField("Dashboard secondary", max_length=7, default="#ff2d55", validators=[hex_color])
    dash_sidebar_color = models.CharField("Dashboard sidebar", max_length=7, default="#0f1117", validators=[hex_color])
    dash_default_theme = models.CharField("Dashboard default mode", max_length=5, choices=THEME_CHOICES, default="light")

    # Contact & social
    phone = models.CharField(max_length=30, default="+91 98765 43210")
    whatsapp = models.CharField("WhatsApp number", max_length=30, blank=True, help_text="Leave blank to use the phone number.")
    email = models.EmailField(default="info@loadimpact.in")
    address = models.CharField(max_length=255, default="1st Floor, Fitness Plaza, MG Road, Kochi, Kerala")
    hours_weekday = models.CharField("Hours Mon–Sat", max_length=60, default="5:00 AM – 10:00 PM")
    hours_weekend = models.CharField("Hours Sunday", max_length=60, default="6:00 AM – 8:00 PM")
    currency = models.CharField(max_length=5, default="₹")
    upi_id = models.CharField("UPI ID", max_length=80, default="loadimpact@upi", blank=True)
    instagram = models.URLField(blank=True, default="https://instagram.com/")
    facebook = models.URLField(blank=True, default="https://facebook.com/")
    youtube = models.URLField(blank=True, default="https://youtube.com/")
    twitter = models.URLField("X / Twitter", blank=True)

    # Footer
    footer_about = models.TextField(
        default="A modern unisex gym built for everyone. Train hard, train smart, and feel the impact every single day."
    )
    footer_links_title = models.CharField(max_length=40, default="Explore")
    footer_big_text = models.CharField("Large outlined footer text", max_length=40, default="LOADIMPACT", blank=True)
    copyright_text = models.CharField(max_length=150, default="All rights reserved.")
    footer_note = models.CharField(max_length=150, default="Made with ❤ for every body.", blank=True)

    links_seeded = models.BooleanField(default=False, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Website settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj = cls.objects.filter(pk=1).first()
        if obj is None:
            info = getattr(settings, "GYM_INFO", {})
            obj = cls(pk=1)
            for field, key in [
                ("site_name", "name"), ("tagline", "tagline"), ("phone", "phone"), ("email", "email"),
                ("address", "address"), ("hours_weekday", "hours_weekday"), ("hours_weekend", "hours_weekend"),
                ("currency", "currency"), ("instagram", "instagram"), ("facebook", "facebook"),
                ("youtube", "youtube"), ("upi_id", "upi_id"),
            ]:
                if info.get(key):
                    setattr(obj, field, info[key])
            obj.save()
        return obj

    # ---- helpers used by templates ----
    @property
    def primary_rgb(self):
        return _hex_to_rgb(self.primary_color)

    @property
    def secondary_rgb(self):
        return _hex_to_rgb(self.secondary_color, "255, 45, 85")

    @property
    def accent_rgb(self):
        return _hex_to_rgb(self.accent_color, "255, 176, 32")

    @property
    def surface_2_color(self):
        return _mix_with_white(self.surface_color, 0.04)

    @property
    def dash_primary_rgb(self):
        return _hex_to_rgb(self.dash_primary_color)

    @property
    def heading_weight(self):
        return HEADING_FONTS.get(self.heading_font, ("", 400))[1]

    @property
    def google_fonts_url(self):
        head = HEADING_FONTS.get(self.heading_font, HEADING_FONTS["Bebas Neue"])[0]
        body = BODY_FONTS.get(self.body_font, BODY_FONTS["Poppins"])
        families = [head] if head.split(":")[0] == body.split(":")[0] else [head, body]
        return "https://fonts.googleapis.com/css2?" + "&".join(f"family={f}" for f in families) + "&display=swap"

    def as_gym_dict(self):
        whatsapp = (self.whatsapp or self.phone).replace(" ", "").replace("+", "").replace("-", "")
        return {
            "name": self.site_name, "tagline": self.tagline, "phone": self.phone, "email": self.email,
            "address": self.address, "hours_weekday": self.hours_weekday, "hours_weekend": self.hours_weekend,
            "currency": self.currency, "upi_id": self.upi_id, "instagram": self.instagram,
            "facebook": self.facebook, "youtube": self.youtube, "twitter": self.twitter, "whatsapp": whatsapp,
        }


class PageSection(models.Model):
    PAGE_CHOICES = [
        ("home", "Home page"),
        ("about", "About page"),
        ("plans", "Plans page"),
        ("trainers", "Trainers page"),
        ("schedule", "Schedule page"),
        ("contact", "Contact page"),
        ("auth", "Login & Sign-up pages"),
    ]

    page = models.CharField(max_length=20, choices=PAGE_CHOICES)
    key = models.CharField(max_length=40)
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=10)
    is_visible = models.BooleanField("Show this section", default=True)

    eyebrow = models.CharField("Small label above title", max_length=120, blank=True)
    title = models.CharField(max_length=200, blank=True)
    highlight = models.CharField("Highlighted (gradient) text", max_length=120, blank=True)
    subtitle = models.TextField("Description", blank=True)
    image = models.ImageField("Upload image", upload_to="sections/", blank=True, null=True)
    image_url = models.CharField("…or image URL", max_length=500, blank=True)
    image_2 = models.ImageField("Upload second image", upload_to="sections/", blank=True, null=True)
    image_2_url = models.CharField("…or second image URL", max_length=500, blank=True)
    button_text = models.CharField(max_length=60, blank=True)
    button_url = models.CharField("Button link", max_length=255, blank=True)
    button_2_text = models.CharField("Second button text", max_length=60, blank=True)
    button_2_url = models.CharField("Second button link", max_length=255, blank=True)
    extra = models.CharField("Extra setting", max_length=255, blank=True)
    badge_value = models.CharField(max_length=40, blank=True)
    badge_text = models.CharField(max_length=120, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["page", "order", "id"]
        constraints = [models.UniqueConstraint(fields=["page", "key"], name="unique_section_per_page")]

    def __str__(self):
        return f"{self.get_page_display()} – {self.name}"

    @property
    def img(self):
        return self.image.url if self.image else self.image_url

    @property
    def img2(self):
        return self.image_2.url if self.image_2 else self.image_2_url

    @property
    def extra_list(self):
        return [w.strip() for w in self.extra.split("|") if w.strip()]

    @property
    def template_name(self):
        if self.key in ("header", "cta"):
            return f"appearance/sections/{self.key}.html"
        return f"appearance/sections/{self.page}_{self.key}.html"


class SectionItem(models.Model):
    section = models.ForeignKey(PageSection, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=200, blank=True)
    label = models.CharField(max_length=80, blank=True)
    text = models.TextField(blank=True)
    icon = models.CharField(max_length=60, blank=True, help_text='Bootstrap icon, e.g. "bi-trophy"')
    image = models.ImageField(upload_to="sections/items/", blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True)
    url = models.CharField("Link", max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField("Show", default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or self.label or f"Item {self.pk}"

    @property
    def img(self):
        return self.image.url if self.image else self.image_url


class NavLink(models.Model):
    LOCATION_CHOICES = [("header", "Header menu"), ("footer", "Footer links")]

    location = models.CharField(max_length=10, choices=LOCATION_CHOICES, default="header")
    label = models.CharField(max_length=60)
    url = models.CharField("Link", max_length=255, help_text='A page path like "/about/" or a full URL.')
    icon = models.CharField(max_length=60, blank=True, help_text='Optional Bootstrap icon, e.g. "bi-star"')
    open_in_new_tab = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField("Show", default=True)

    class Meta:
        ordering = ["location", "order", "id"]

    def __str__(self):
        return f"{self.label} ({self.get_location_display()})"
