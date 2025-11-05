from django.utils import timezone 
from django.db import models

# Create your models here.
from django.core.validators import MinValueValidator
from produits.models import Produit
from sites.models import SiteFabrication
from django.core.validators import MinValueValidator
from sites.models import SiteFabrication
from django.core.exceptions import ValidationError


from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models


class Facture(models.Model):
    TYPES = (
        ('Achat', 'Facture d’Achat'),
        ('Vente', 'Facture de Vente'),
    )
    type = models.CharField(max_length=10, choices=TYPES)
    client_fournisseur = models.CharField(max_length=255, blank=True, null=True)
    site = models.ForeignKey("sites.SiteFabrication", on_delete=models.CASCADE, related_name="factures")
    produit = models.ForeignKey("produits.Produit", on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=[("impayee", "Impayée"), ("partielle", "Payée Partiellement"), ("payee", "Payée")],
        default="impayee"
    )

    def clean(self):
        """Validation stricte côté modèle."""
        if self.quantite is None or self.prix_unitaire is None:
            raise ValidationError("La quantité et le prix unitaire sont obligatoires.")
        if self.quantite <= 0:
            raise ValidationError("La quantité doit être supérieure à 0.")
        if self.prix_unitaire <= 0:
            raise ValidationError("Le prix unitaire doit être supérieur à 0.")

    def save(self, *args, **kwargs):
        # Exécute les validations (y compris clean())
        self.full_clean()

        # Calcul du total uniquement si les deux champs sont valides
        if self.quantite is not None and self.prix_unitaire is not None:
            self.total = self.quantite * self.prix_unitaire
        else:
            self.total = 0

        # Calcul du statut
        if self.montant_paye >= self.total and self.total > 0:
            self.status = "payee"
        elif 0 < self.montant_paye < self.total:
            self.status = "partielle"
        else:
            self.status = "impayee"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type} #{self.pk or ''} - {self.client_fournisseur or 'N/A'}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_type_display()} - {self.client_fournisseur or 'N/A'} ({self.total} FG)"
    


    @property
    def restant(self):
        return (self.total or 0) - (self.montant_paye or 0)

    def __str__(self):
        return f"Facture {self.id} - {self.type} - {self.total} FG"
    

    @property
    def is_achat(self): return self.type == 'Achat'



    @property
    def is_vente(self): return self.type == 'Vente'


class Paiement(models.Model):
    MODES = (
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement Bancaire'),
        ('mobile', 'Mobile Money'),
    )
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name="paiements")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    montant_total = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    mode_paiement = models.CharField(max_length=20, choices=MODES, default='especes')
    date_paiement = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.montant_total} — {self.get_mode_paiement_display()}"
    
    def save(self, *args, **kwargs):
        if not self.montant_total:
            self.montant_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)

    
