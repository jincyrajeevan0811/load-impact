from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "LoadImpact Administration"
admin.site.site_title = "LoadImpact Admin"
admin.site.index_title = "Database Administration"

urlpatterns = [
    path("django-admin/", admin.site.urls),          # Django's built-in database admin
    path("admin-panel/", include("dashboard.urls")),  # Custom LoadImpact admin dashboard
    path("accounts/", include("accounts.urls")),
    path("member/", include("members.urls")),
    path("", include("gym.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
