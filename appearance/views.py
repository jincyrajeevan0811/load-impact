"""Appearance section of the admin dashboard: branding, colours, page sections and navigation."""
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from dashboard.views import staff_required

from .defaults import ITEM_FIELDS, PAGE_PATHS, SECTION_HELP
from .forms import BrandingForm, ColorsForm, ContactFooterForm, NavLinkForm, SectionForm, item_formset_for
from .models import NavLink, PageSection, SiteSettings
from .utils import ensure_defaults, reset_section

COLOR_PRESETS = [
    {"name": "LoadImpact Fire", "primary": "#ff5a1f", "secondary": "#ff2d55", "accent": "#ffb020", "bg": "#0a0b0f", "surface": "#12141b"},
    {"name": "Electric Blue", "primary": "#3b82f6", "secondary": "#8b5cf6", "accent": "#22d3ee", "bg": "#070b14", "surface": "#0f1624"},
    {"name": "Neon Lime", "primary": "#84cc16", "secondary": "#22c55e", "accent": "#facc15", "bg": "#090b08", "surface": "#121610"},
    {"name": "Royal Purple", "primary": "#a855f7", "secondary": "#ec4899", "accent": "#f59e0b", "bg": "#0c0812", "surface": "#161021"},
    {"name": "Ocean Teal", "primary": "#14b8a6", "secondary": "#0ea5e9", "accent": "#a3e635", "bg": "#06100f", "surface": "#0e1a19"},
    {"name": "Crimson Gold", "primary": "#dc2626", "secondary": "#b91c1c", "accent": "#eab308", "bg": "#0d0808", "surface": "#181010"},
]

DEFAULT_COLORS = {
    "primary_color": "#ff5a1f", "secondary_color": "#ff2d55", "accent_color": "#ffb020",
    "background_color": "#0a0b0f", "surface_color": "#12141b", "text_color": "#e9ecf2",
    "heading_font": "Bebas Neue", "body_font": "Poppins",
    "dash_primary_color": "#ff5a1f", "dash_secondary_color": "#ff2d55", "dash_sidebar_color": "#0f1117",
    "dash_default_theme": "light",
}


def _settings_form_view(request, form_class, template, title, tab, success):
    ensure_defaults()
    site = SiteSettings.load()
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, success)
            return redirect(request.path)
    else:
        form = form_class(instance=site)
    return render(request, template, {"form": form, "page_title": title, "tab": tab, "site": site})


@staff_required
def appearance_home(request):
    ensure_defaults()
    site = SiteSettings.load()
    pages = []
    counts = dict(PageSection.objects.order_by().values_list("page").annotate(c=Count("id")))
    hidden = dict(PageSection.objects.filter(is_visible=False).order_by().values_list("page").annotate(c=Count("id")))
    for key, label in PageSection.PAGE_CHOICES:
        pages.append({"key": key, "label": label, "count": counts.get(key, 0), "hidden": hidden.get(key, 0), "path": PAGE_PATHS.get(key, "/")})
    return render(request, "dashboard/appearance/home.html", {
        "page_title": "Appearance", "tab": "home", "site": site, "pages": pages,
        "header_links": NavLink.objects.filter(location="header").count(),
        "footer_links": NavLink.objects.filter(location="footer").count(),
    })


@staff_required
def appearance_branding(request):
    return _settings_form_view(request, BrandingForm, "dashboard/appearance/settings_form.html",
                               "Branding & Logo", "branding", "Branding updated.")


@staff_required
def appearance_contact(request):
    return _settings_form_view(request, ContactFooterForm, "dashboard/appearance/settings_form.html",
                               "Contact & Footer", "contact", "Contact details and footer updated.")


@staff_required
def appearance_colors(request):
    ensure_defaults()
    site = SiteSettings.load()
    if request.method == "POST" and request.POST.get("action") == "reset":
        for field, value in DEFAULT_COLORS.items():
            setattr(site, field, value)
        site.save()
        messages.success(request, "Colours and fonts restored to the original LoadImpact theme.")
        return redirect("dashboard:appearance_colors")
    if request.method == "POST":
        form = ColorsForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, "Colours and fonts saved. Open the website to see them live.")
            return redirect("dashboard:appearance_colors")
    else:
        form = ColorsForm(instance=site)
    return render(request, "dashboard/appearance/colors.html", {
        "form": form, "page_title": "Colours & Fonts", "tab": "colors", "site": site, "presets": COLOR_PRESETS,
    })


@staff_required
def appearance_pages(request):
    ensure_defaults()
    page = request.GET.get("page", "home")
    valid = dict(PageSection.PAGE_CHOICES)
    if page not in valid:
        page = "home"
    sections = PageSection.objects.filter(page=page).annotate(item_count=Count("items"))
    return render(request, "dashboard/appearance/pages.html", {
        "page_title": "Pages & Sections", "tab": "pages", "sections": sections, "current_page": page,
        "current_label": valid[page], "page_choices": PageSection.PAGE_CHOICES, "page_path": PAGE_PATHS.get(page, "/"),
    })


@staff_required
def appearance_section_edit(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    FormSet = item_formset_for(section)
    if request.method == "POST":
        form = SectionForm(request.POST, request.FILES, instance=section)
        formset = FormSet(request.POST, request.FILES, instance=section, prefix="items") if FormSet else None
        if form.is_valid() and (formset is None or formset.is_valid()):
            form.save()
            if formset is not None:
                formset.save()
            messages.success(request, f'"{section.name}" saved.')
            if request.POST.get("next") == "stay":
                return redirect("dashboard:appearance_section_edit", pk=section.pk)
            return redirect(f"{reverse('dashboard:appearance_pages')}?page={section.page}")
    else:
        form = SectionForm(instance=section)
        formset = FormSet(instance=section, prefix="items") if FormSet else None
    item_config = ITEM_FIELDS.get(section.key)
    return render(request, "dashboard/appearance/section_form.html", {
        "page_title": f"Edit: {section.name}", "tab": "pages", "section": section, "form": form, "formset": formset,
        "item_name": item_config[1] if item_config else "", "item_help": item_config[2] if item_config else "",
        "section_help": SECTION_HELP.get(section.key, ""), "page_path": PAGE_PATHS.get(section.page, "/"),
    })


@staff_required
@require_POST
def appearance_section_toggle(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    section.is_visible = not section.is_visible
    section.save(update_fields=["is_visible"])
    messages.success(request, f'"{section.name}" is now {"visible" if section.is_visible else "hidden"}.')
    return redirect(f"{reverse('dashboard:appearance_pages')}?page={section.page}")


@staff_required
@require_POST
def appearance_section_move(request, pk, direction):
    section = get_object_or_404(PageSection, pk=pk)
    siblings = list(PageSection.objects.filter(page=section.page).order_by("order", "id"))
    for i, s in enumerate(siblings):  # normalise ordering first
        s.order = (i + 1) * 10
    idx = next(i for i, s in enumerate(siblings) if s.pk == section.pk)
    swap = idx - 1 if direction == "up" else idx + 1
    if 0 <= swap < len(siblings):
        siblings[idx].order, siblings[swap].order = siblings[swap].order, siblings[idx].order
    for s in siblings:
        PageSection.objects.filter(pk=s.pk).update(order=s.order)
    return redirect(f"{reverse('dashboard:appearance_pages')}?page={section.page}")


@staff_required
@require_POST
def appearance_section_reset(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    page, name = section.page, section.name
    new = reset_section(section)
    messages.success(request, f'"{name}" was restored to its default content.')
    return redirect("dashboard:appearance_section_edit", pk=new.pk) if new.pk else redirect(
        f"{reverse('dashboard:appearance_pages')}?page={page}"
    )


@staff_required
def appearance_nav(request):
    ensure_defaults()
    if request.method == "POST":
        form = NavLinkForm(request.POST)
        if form.is_valid():
            link = form.save()
            messages.success(request, f'Link "{link.label}" added to the {link.get_location_display().lower()}.')
            return redirect("dashboard:appearance_nav")
    else:
        form = NavLinkForm(initial={"location": request.GET.get("location", "header"), "order": 100, "is_active": True})
    return render(request, "dashboard/appearance/nav.html", {
        "page_title": "Navigation", "tab": "nav", "form": form,
        "header_links": NavLink.objects.filter(location="header"),
        "footer_links": NavLink.objects.filter(location="footer"),
        "quick_pages": [("Home", "/"), ("About", "/about/"), ("Plans", "/plans/"), ("Trainers", "/trainers/"),
                        ("Schedule", "/schedule/"), ("Contact", "/contact/"), ("Join / Register", "/accounts/register/"),
                        ("Login", "/accounts/login/"), ("Member Dashboard", "/member/dashboard/")],
    })


@staff_required
def appearance_nav_edit(request, pk):
    link = get_object_or_404(NavLink, pk=pk)
    if request.method == "POST":
        form = NavLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, "Link updated.")
            return redirect("dashboard:appearance_nav")
    else:
        form = NavLinkForm(instance=link)
    return render(request, "dashboard/form.html", {
        "form": form, "page_title": f"Edit link: {link.label}", "back_url": reverse("dashboard:appearance_nav"),
    })


@staff_required
@require_POST
def appearance_nav_action(request, pk, action):
    link = get_object_or_404(NavLink, pk=pk)
    if action == "delete":
        link.delete()
        messages.success(request, f'Link "{link.label}" removed.')
    elif action == "toggle":
        link.is_active = not link.is_active
        link.save(update_fields=["is_active"])
    elif action in ("up", "down"):
        siblings = list(NavLink.objects.filter(location=link.location).order_by("order", "id"))
        idx = next(i for i, s in enumerate(siblings) if s.pk == link.pk)
        swap = idx - 1 if action == "up" else idx + 1
        if 0 <= swap < len(siblings):
            siblings[idx], siblings[swap] = siblings[swap], siblings[idx]
        for i, s in enumerate(siblings):
            NavLink.objects.filter(pk=s.pk).update(order=(i + 1) * 10)
    return redirect("dashboard:appearance_nav")
