from django.urls import path
from . import views

app_name = "factures"

urlpatterns = [
     path("", views.liste_factures, name="liste"),
    path("ajouter/", views.ajouter_facture, name="ajouter"),
    path("<int:id>/modifier/", views.modifier_facture, name="modifier"),
    path("<int:id>/supprimer/", views.supprimer_facture, name="supprimer"),
    path("<int:id>/", views.detail_facture, name="detail"),
    path("<int:id>/paiement/", views.enregistrer_paiement, name="paiement"),
    path("export/csv/", views.export_factures_csv, name="export_csv"),
    path("stats/", views.stats_factures, name="stats"),
    path("stats/ventes/", views.stats_ventes, name="stats_ventes"),

    path("achats/add/", views.ajouter_facture_by_type, {"kind": "achats"}, name="ajouter_achat"),
    path("ventes/add/", views.ajouter_facture_by_type, {"kind": "ventes"}, name="ajouter_vente"),
]
