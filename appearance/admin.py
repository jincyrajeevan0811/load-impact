from django.contrib import admin

from .models import NavLink, PageSection, SectionItem, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


class SectionItemInline(admin.StackedInline):
    model = SectionItem
    extra = 0


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "page", "order", "is_visible")
    list_filter = ("page", "is_visible")
    list_editable = ("order", "is_visible")
    inlines = [SectionItemInline]


@admin.register(NavLink)
class NavLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "location", "url", "order", "is_active")
    list_filter = ("location",)
    list_editable = ("order", "is_active")
