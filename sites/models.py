from django.db import models

# Create your models here.
from django.db import models

class SiteFabrication(models.Model):
    nom = models.CharField(max_length=200)
    localisation = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nom


class Employe(models.Model):
    SITUATION_CHOICES = (
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié(e)'),
        ('divorce', 'Divorcé(e)'),
        ('veuf', 'Veuf/Veuve'),
    )
    nom = models.CharField(max_length=200)
    poste = models.CharField(max_length=100)
    salaire = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    site = models.ForeignKey(SiteFabrication, on_delete=models.CASCADE, related_name="employes")

    # Ajouts demandés
    date_embauche = models.DateField()
    situation_matrimoniale = models.CharField(max_length=20, choices=SITUATION_CHOICES, default='celibataire')

    def __str__(self):
        return self.nom
