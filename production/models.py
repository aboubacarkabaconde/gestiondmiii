from django.utils import timezone 
from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from sites.models import SiteFabrication
from produits.models import Produit

class Production(models.Model):
    site = models.ForeignKey(SiteFabrication, on_delete=models.CASCADE, related_name="productions")
    produit_fini = models.ForeignKey(Produit, on_delete=models.CASCADE, limit_choices_to={'type': 'PF'})
    quantite_produite = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Production {self.produit_fini.nom} - {self.quantite_produite}"


class ConsommationMatierePremiere(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name="consommations")
    produit_mp = models.ForeignKey(Produit, on_delete=models.CASCADE, limit_choices_to={'type': 'MP'})
    quantite_utilisee = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.produit_mp.nom} - {self.quantite_utilisee}"
    
class Consommation(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="consommations")
    site = models.ForeignKey(SiteFabrication, on_delete=models.CASCADE, related_name="consommations")
    quantite = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Conso {self.produit.nom} ({self.quantite} {self.produit.unite})"    
