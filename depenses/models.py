from django.utils import timezone 
from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from sites.models import SiteFabrication

class CategorieDepense(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nom


class Depense(models.Model):
    site = models.ForeignKey(SiteFabrication, on_delete=models.CASCADE, related_name="depenses")
    categorie = models.ForeignKey(CategorieDepense, on_delete=models.SET_NULL, null=True)
    montant = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField(default=timezone.now)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.categorie} - {self.montant} GNF"
