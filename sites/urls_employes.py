from django.urls import path
from . import views_employes

app_name = "employes"

urlpatterns = [
    path("", views_employes.liste_employes, name="liste"),
    path("ajouter/", views_employes.ajouter_employe, name="ajouter"),
    path("<int:id>/modifier/", views_employes.modifier_employe, name="modifier"),
    path("<int:id>/supprimer/", views_employes.supprimer_employe, name="supprimer"),
]
