# pme_manager/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static as static_serve  # pour servir MEDIA en dev
from django.views.generic import RedirectView
from django.templatetags.static import static as static_url  # pour construire l'URL du favicon
from core.views import dashboard

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),

    # --- Modules (tous avec namespaces cohérents) ---
    path("depenses/", include(("depenses.urls", "depenses"), namespace="depenses")),
    path("factures/", include(("factures.urls", "factures"), namespace="factures")),
    path("production/", include(("production.urls", "production"), namespace="production")),
    path("sites/", include(("sites.urls", "sites"), namespace="sites")),
    path("produits/", include("produits.urls")),
    
    

    path("search/", include("core.urls_search")),  # UNIQUEMENT si core/urls_search.py existe
    path("accounts/", include("django.contrib.auth.urls")),

    # Favicon: redirige /favicon.ico -> /static/favicon.svg
    re_path(r"^favicon\.ico$", RedirectView.as_view(url=static_url("favicon.svg"), permanent=True)),
]

# Servir MEDIA en dev
if settings.DEBUG:
    urlpatterns += static_serve(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
