from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from sites.models import SiteFabrication
from django.apps import apps


class Produit(models.Model):
    TYPES = (
        ('MP', 'Matière Première'),
        ('PF', 'Produit Fini'),
    )

    nom = models.CharField(max_length=150)
    type = models.CharField(max_length=2, choices=TYPES, default='MP')
    unite = models.CharField(max_length=50, help_text="Ex: kg, litre, unité")
    poids_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    quantite_disponible = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    site = models.ForeignKey(SiteFabrication, on_delete=models.CASCADE, related_name="produits")
    quantite_stock = models.DecimalField(max_digits=12,decimal_places=2,default=0, help_text="Quantité actuelle en stock")

    def __str__(self):
        return f"{self.nom} ({self.quantite_stock} {self.unite})"

    

    def maj_stock(self):
        Paiement = apps.get_model("factures", "Paiement")
        Consommation = apps.get_model("production", "Consommation")

        entrees = Paiement.objects.filter(produit=self, facture__type="Achat").aggregate(total=Sum("quantite"))["total"] or 0
        sorties = Paiement.objects.filter(produit=self, facture__type="Vente").aggregate(total=Sum("quantite"))["total"] or 0
        conso = Consommation.objects.filter(produit=self).aggregate(total=Sum("quantite"))["total"] or 0

        self.quantite_stock = entrees - sorties - conso
        self.save(update_fields=["quantite_stock"])


class Stock(models.Model):
    produit = models.OneToOneField(Produit, on_delete=models.CASCADE, related_name="stock")
    quantite_initiale = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    quantite_utilisee = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    quantite_restante = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    
    def __str__(self):
        return f"Stock de {self.produit.nom}"


# ========================================
# Connexion aux autres modules (signals)
# ========================================

# Relations dynamiques


# ========== SIGNALS ==========
@receiver(post_save)
@receiver(post_delete)
def maj_stock_signals(sender, instance, **kwargs):
    """
    Met à jour le stock quand on enregistre ou supprime un Paiement ou une Consommation
    """
    from factures.models import Paiement
    from production.models import Consommation

    if isinstance(instance, Paiement) and instance.produit:
        instance.produit.maj_stock()

    if isinstance(instance, Consommation) and instance.produit:
        instance.produit.maj_stock()