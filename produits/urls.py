from django.urls import path
from . import views

app_name = "produits"

urlpatterns = [
    path("", views.liste_produits, name="liste"),
    path("ajouter/", views.ajouter_produit, name="ajouter"),
    path("<int:id>/", views.detail_produit, name="detail"),
    path("<int:id>/modifier/", views.modifier_produit, name="modifier"),
    path("<int:id>/supprimer/", views.supprimer_produit, name="supprimer"),
    path("stock/", views.stock_view, name="stock"),
]
