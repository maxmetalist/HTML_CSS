from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/catalog/", permanent=True), name="home"),
    path("catalog/", include("catalog.urls", namespace="catalog")),
    path("users/", include("users.urls", namespace="users")),
    path("blog/", include("blog.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
