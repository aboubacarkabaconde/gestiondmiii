from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from .models import Paiement
from produits.models import Stock
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Facture
from produits.models import Produit

@receiver(post_save, sender=Paiement)
def maj_stock_apres_paiement(sender, instance: Paiement, created, **kwargs):
    if not created:
        return
    produit = instance.produit
    qte = instance.quantite or 0

    # Achat : on ajoute au stock
    if instance.facture.type == "Achat":
        if hasattr(produit, "stock"):
            produit.stock.quantite_restante = F("quantite_restante") + qte
            produit.stock.quantite_initiale = F("quantite_initiale") + qte
            produit.stock.save(update_fields=["quantite_restante", "quantite_initiale"])
        else:
            Stock.objects.create(produit=produit, quantite_initiale=qte, quantite_restante=qte)

        produit.quantite_disponible = F("quantite_disponible") + qte
        # Si MP, on met à jour aussi le poids_total (si tu l'utilises ainsi)
        if produit.type == "MP":
            produit.poids_total = F("poids_total") + qte
        produit.save(update_fields=["quantite_disponible", "poids_total"])

    # Vente : on déduit du stock (souvent PF)
    elif instance.facture.type == "Vente":
        if hasattr(produit, "stock"):
            produit.stock.quantite_utilisee = F("quantite_utilisee") + qte
            produit.stock.quantite_restante = F("quantite_restante") - qte
            produit.stock.save(update_fields=["quantite_utilisee", "quantite_restante"])

        produit.quantite_disponible = F("quantite_disponible") - qte
        produit.save(update_fields=["quantite_disponible"])


@receiver(post_save, sender=Facture)
def maj_stock_apres_facture(sender, instance, created, **kwargs):
    """
    Met à jour le stock du produit après enregistrement d'une facture.
    """
    produit = instance.produit

    if instance.type == "Achat":
        # On augmente le stock
        produit.quantite_stock += instance.quantite
    elif instance.type == "Vente":
        # On diminue le stock
        produit.quantite_stock -= instance.quantite

    produit.save(update_fields=["quantite_stock"])


@receiver(post_delete, sender=Facture)
def maj_stock_apres_suppression(sender, instance, **kwargs):
    """
    Réajuste le stock si une facture est supprimée.
    """
    produit = instance.produit

    if instance.type == "Achat":
        produit.quantite_stock -= instance.quantite
    elif instance.type == "Vente":
        produit.quantite_stock += instance.quantite

    produit.save(update_fields=["quantite_stock"])        
