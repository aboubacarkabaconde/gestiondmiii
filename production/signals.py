from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import F
from .models import Production, ConsommationMatierePremiere
from produits.models import Stock

@receiver(post_save, sender=Production)
def maj_stock_produit_fini(sender, instance: Production, created, **kwargs):
    if not created:
        return
    pf = instance.produit_fini
    qte = instance.quantite_produite or 0

    if hasattr(pf, "stock"):
        pf.stock.quantite_restante = F("quantite_restante") + qte
        pf.stock.quantite_initiale = F("quantite_initiale") + qte
        pf.stock.save(update_fields=["quantite_restante", "quantite_initiale"])
    else:
        Stock.objects.create(produit=pf, quantite_initiale=qte, quantite_restante=qte)

    pf.quantite_disponible = F("quantite_disponible") + qte
    pf.save(update_fields=["quantite_disponible"])


@receiver(post_save, sender=ConsommationMatierePremiere)
def maj_stock_matiere_premiere(sender, instance: ConsommationMatierePremiere, created, **kwargs):
    if not created:
        return
    mp = instance.produit_mp
    qte = instance.quantite_utilisee or 0

    if hasattr(mp, "stock"):
        mp.stock.quantite_utilisee = F("quantite_utilisee") + qte
        mp.stock.quantite_restante = F("quantite_restante") - qte
        mp.stock.save(update_fields=["quantite_utilisee", "quantite_restante"])

    mp.quantite_disponible = F("quantite_disponible") - qte
    # Si tu utilises poids_total comme cumul d’entrées, ne pas le diminuer ici.
    mp.save(update_fields=["quantite_disponible"])
