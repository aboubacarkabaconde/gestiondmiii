# depenses/urls.py
from django.urls import path
from . import views

app_name = "depenses"

urlpatterns = [
    path("", views.liste_depenses, name="liste"),
    path("<int:id>/", views.detail_depense, name="detail"),
    path("ajouter/", views.ajouter_depense, name="ajouter"),
    path("<int:id>/modifier/", views.modifier_depense, name="modifier"),
    path("<int:id>/supprimer/", views.supprimer_depense, name="supprimer"),
    path("stats/", views.stats_depenses, name="stats"),
    path("export/csv/", views.export_depenses_csv, name="export_csv"),
    path("export/pdf/", views.export_depenses_pdf, name="export_pdf"),  # ✅ export PDF
]
