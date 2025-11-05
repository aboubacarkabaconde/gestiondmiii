from django.urls import path
from . import views

app_name = "production"

urlpatterns = [
    # Productions
    path("", views.liste_productions, name="liste_productions"),
    path("ajouter/", views.ajouter_production, name="ajouter_production"),
    path("<int:id>/", views.detail_production, name="detail_production"),
    path("<int:id>/modifier/", views.modifier_production, name="modifier_production"),
    path("<int:id>/supprimer/", views.supprimer_production, name="supprimer_production"),

    # Consommations de matières premières liées à une production
    path("<int:production_id>/consommations/ajouter/", views.ajouter_consommation_mp, name="ajouter_consommation_mp"),
    path("consommations/<int:id>/modifier/", views.modifier_consommation_mp, name="modifier_consommation_mp"),
    path("consommations/<int:id>/supprimer/", views.supprimer_consommation_mp, name="supprimer_consommation_mp"),
]
