from django import forms
from django.forms import inlineformset_factory

from accounts.forms import BootstrapFormMixin

from .defaults import FIELD_LABELS, ITEM_FIELDS, SECTION_FIELDS
from .models import NavLink, PageSection, SectionItem, SiteSettings


class ColorInput(forms.TextInput):
    input_type = "color"

    def __init__(self, attrs=None):
        base = {"class": "form-control form-control-color w-100"}
        base.update(attrs or {})
        super().__init__(base)


class BrandingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            "site_name", "tagline", "brand_text_1", "brand_text_2", "brand_icon", "logo", "logo_height",
            "favicon", "nav_cta_text", "meta_description", "show_preloader", "enable_animations",
        )


class ColorsForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            "primary_color", "secondary_color", "accent_color", "background_color", "surface_color", "text_color",
            "heading_font", "body_font",
            "dash_primary_color", "dash_secondary_color", "dash_sidebar_color", "dash_default_theme",
        )
        widgets = {
            name: ColorInput()
            for name in (
                "primary_color", "secondary_color", "accent_color", "background_color", "surface_color",
                "text_color", "dash_primary_color", "dash_secondary_color", "dash_sidebar_color",
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, ColorInput):
                field.widget.attrs["class"] = "form-control form-control-color w-100"
                field.widget.attrs.pop("placeholder", None)


class ContactFooterForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            "phone", "whatsapp", "email", "address", "hours_weekday", "hours_weekend", "currency", "upi_id",
            "instagram", "facebook", "youtube", "twitter",
            "footer_about", "footer_links_title", "footer_big_text", "copyright_text", "footer_note",
        )
        widgets = {"footer_about": forms.Textarea(attrs={"rows": 3})}


class SectionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PageSection
        fields = (
            "name", "is_visible", "eyebrow", "title", "highlight", "subtitle", "extra",
            "image", "image_url", "image_2", "image_2_url",
            "button_text", "button_url", "button_2_text", "button_2_url", "badge_value", "badge_text",
        )
        labels = {"name": "Section name (shown in the editor)"}
        widgets = {"subtitle": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key = self.instance.key
        allowed = set(SECTION_FIELDS.get(key, [])) | {"name", "is_visible"}
        for name in list(self.fields):
            if name not in allowed:
                del self.fields[name]
        for name, label in FIELD_LABELS.get(key, {}).items():
            if name in self.fields:
                self.fields[name].label = label


class ItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = SectionItem
        fields = ("title", "label", "text", "icon", "image", "image_url", "url", "order", "is_active")
        widgets = {"text": forms.Textarea(attrs={"rows": 2})}


def item_formset_for(section):
    """An inline formset showing only the item fields this section type uses (or None)."""
    config = ITEM_FIELDS.get(section.key)
    if not config:
        return None
    fields = list(config[0]) + ["order", "is_active"]
    return inlineformset_factory(
        PageSection, SectionItem, form=ItemForm, fields=fields, extra=1, can_delete=True
    )


class NavLinkForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = NavLink
        fields = ("location", "label", "url", "icon", "order", "open_in_new_tab", "is_active")
