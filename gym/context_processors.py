from django.conf import settings
from django.db import DatabaseError


def site_info(request):
    """Branding, contact details, navigation and colours for every template."""
    ctx = {
        "GYM": settings.GYM_INFO,
        "IMG": getattr(settings, "GYM_IMAGES", {}),
        "SITE": None,
        "NAV_HEADER": [],
        "NAV_FOOTER": [],
    }
    try:
        from appearance.models import NavLink, SiteSettings
        from appearance.utils import ensure_defaults

        ensure_defaults()
        site = SiteSettings.load()
        ctx["SITE"] = site
        ctx["GYM"] = site.as_gym_dict()
        links = list(NavLink.objects.filter(is_active=True))
        ctx["NAV_HEADER"] = [link for link in links if link.location == "header"]
        ctx["NAV_FOOTER"] = [link for link in links if link.location == "footer"]
    except DatabaseError:
        # Tables not created yet (before `migrate`) – fall back to settings.py values.
        pass

    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated and user.is_staff:
        from .models import ContactMessage, Payment

        ctx["unread_messages_count"] = ContactMessage.objects.filter(is_read=False).count()
        ctx["pending_payments_count"] = Payment.objects.filter(status="pending").count()
    return ctx
