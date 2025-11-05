# sites/urls.py
from django.urls import path
from . import views_sites
from . import views_employes as views    # ← ajoute ceci

app_name = "sites"

urlpatterns = [
    # Routes de sites
    path("", views_sites.liste_sites, name="liste"),
    path("ajouter/", views_sites.ajouter_site, name="ajouter"),
    path("<int:id>/modifier/", views_sites.modifier_site, name="modifier"),
    path("<int:id>/supprimer/", views_sites.supprimer_site, name="supprimer"),

    # ✅ Routes employés sous /sites/employes/
    path("employes/", views.liste_employes, name="liste_employes"),
    path("employes/ajouter/", views.ajouter_employe, name="ajouter_employe"),
    path("employes/<int:id>/modifier/", views.modifier_employe, name="modifier_employe"),
    path("employes/<int:id>/supprimer/", views.supprimer_employe, name="supprimer_employe"),
]
