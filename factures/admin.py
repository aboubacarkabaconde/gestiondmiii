from django.contrib import admin
from .models import Facture, Paiement


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "type",
        "client_fournisseur",
        "site",
        "produit",
        "quantite",
        "prix_unitaire",
        "total",
        "montant_paye",
        "status",
        "date",
    )
    list_filter = ("type", "status", "site", "date")
    search_fields = ("client_fournisseur", "produit__nom")

    # On retire total et status du formulaire
    exclude = ("total", "status")


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "facture",
        "produit",
        "quantite",
        "prix_unitaire",
        "montant_total",
        "mode_paiement",
        "date_paiement",
    )
    list_filter = ("mode_paiement", "date_paiement")
    search_fields = ("facture__client_fournisseur", "produit__nom")
