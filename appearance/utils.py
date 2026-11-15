from django.db import transaction
from django.db.models import Prefetch

from .defaults import NAV_DEFAULTS, SECTION_DEFAULTS
from .models import NavLink, PageSection, SectionItem, SiteSettings

_defaults_checked = False


def _create_section(page, order, data):
    data = dict(data)
    items = data.pop("items", [])
    section = PageSection.objects.create(page=page, order=order, **data)
    SectionItem.objects.bulk_create(
        [SectionItem(section=section, order=(i + 1) * 10, **item) for i, item in enumerate(items)]
    )
    return section


def ensure_defaults(force=False):
    """Create any missing default sections / nav links (runs once per process unless forced)."""
    global _defaults_checked
    if _defaults_checked and not force:
        return
    _create_missing_defaults()
    _defaults_checked = True


@transaction.atomic
def _create_missing_defaults():
    site = SiteSettings.load()
    existing = set(PageSection.objects.values_list("page", "key"))
    for page, sections in SECTION_DEFAULTS.items():
        for index, data in enumerate(sections):
            if (page, data["key"]) not in existing:
                _create_section(page, (index + 1) * 10, data)
    if not site.links_seeded:
        if not NavLink.objects.exists():
            NavLink.objects.bulk_create(
                [NavLink(location=loc, label=label, url=url, order=(i + 1) * 10) for i, (loc, label, url) in enumerate(NAV_DEFAULTS)]
            )
        SiteSettings.objects.filter(pk=site.pk).update(links_seeded=True)


def reset_section(section):
    """Restore one section (and its items) to the default content."""
    for index, data in enumerate(SECTION_DEFAULTS.get(section.page, [])):
        if data["key"] == section.key:
            page, order = section.page, section.order
            section.delete()
            return _create_section(page, order, data)
    return section


def apply_tokens(value, tokens):
    value = value or ""
    for key, number in (tokens or {}).items():
        value = value.replace("{" + key + "}", str(number))
    return value


def page_context(page, tokens=None):
    """Sections of a page for templates: `sections` (visible, ordered) and `S` (visible, by key)."""
    try:
        ensure_defaults()
    except Exception:  # database not migrated yet
        return {"sections": [], "S": {}, "S_all": {}}
    qs = PageSection.objects.filter(page=page).prefetch_related(
        Prefetch("items", queryset=SectionItem.objects.filter(is_active=True).order_by("order", "id"))
    )
    all_sections = list(qs)
    for s in all_sections:
        s.item_list = list(s.items.all())
        for item in s.item_list:
            item.value = apply_tokens(item.title, tokens)
        s.badge_display = apply_tokens(s.badge_value, tokens)
    visible = [s for s in all_sections if s.is_visible]
    return {
        "sections": visible,
        "S": {s.key: s for s in visible},
        "S_all": {s.key: s for s in all_sections},
    }
