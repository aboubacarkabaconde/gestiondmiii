from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from .models import Facture, Paiement
from produits.models import Produit

from django import forms
from .models import Facture

from django import forms
from .models import Facture


from django import forms
from django.core.exceptions import ValidationError
from .models import Facture


class FactureForm(forms.ModelForm):
    class Meta:
        model = Facture
        fields = [
            "type",
            "client_fournisseur",
            "site",
            "produit",
            "quantite",
            "prix_unitaire",
            "montant_paye",
            "date",
        ]
        widgets = {
            "type": forms.Select(attrs={"class": "form-control"}),
            "client_fournisseur": forms.TextInput(attrs={"class": "form-control"}),
            "site": forms.Select(attrs={"class": "form-control"}),
            "produit": forms.Select(attrs={"class": "form-control"}),
            "quantite": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "prix_unitaire": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "montant_paye": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        quantite = cleaned_data.get("quantite")
        prix_unitaire = cleaned_data.get("prix_unitaire")

        # Validation stricte
        if quantite is None or prix_unitaire is None:
            raise ValidationError("La quantité et le prix unitaire sont obligatoires.")

        if quantite <= 0:
            raise ValidationError("La quantité doit être supérieure à 0.")
        if prix_unitaire <= 0:
            raise ValidationError("Le prix unitaire doit être supérieur à 0.")

        return cleaned_data



class PaiementForm(forms.ModelForm):
    """
    - Inspiré de ton style: widgets Bootstrap, validation côté form.
    - Accepte un argument 'facture' à l'init pour valider le stock en cas de Vente.
      Dans ta vue, appelle: PaiementForm(request.POST, facture=facture)
    - Si montant_total est vide, on le calcule = quantite * prix_unitaire.
    """
    class Meta:
        model = Paiement
        fields = ["produit", "quantite", "prix_unitaire", "montant_total", "mode_paiement"]
        widgets = {
            "produit": forms.Select(attrs={"class": "form-control"}),
            "quantite": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "prix_unitaire": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "montant_total": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "mode_paiement": forms.Select(attrs={"class": "form-control"}),
            
        }

    def __init__(self, *args, facture=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.facture = facture  # pour validation du stock en Vente

    def clean(self):
        cleaned = super().clean()
        produit: Produit = cleaned.get("produit")
        quantite = cleaned.get("quantite") or Decimal("0")
        prix_unitaire = cleaned.get("prix_unitaire") or Decimal("0")
        montant_total = cleaned.get("montant_total")

        # Auto-calc du montant_total si absent
        if (montant_total is None or montant_total == 0) and quantite and prix_unitaire:
            cleaned["montant_total"] = quantite * prix_unitaire

        # Validation vente vs stock (si la facture a été injectée par la vue)
        if self.facture and self.facture.type == "Vente" and produit:
            stock = getattr(produit, "stock", None)
            if stock and quantite > stock.quantite_restante:
                raise ValidationError("Stock insuffisant pour cette vente (quantité demandée > stock restant).")

        return cleaned


# --------- Formulaire de filtres pour la page Stats Ventes ---------
class StatsVentesFilterForm(forms.Form):
    start = forms.DateField(required=False, widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    end = forms.DateField(required=False, widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    site_id = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}))
