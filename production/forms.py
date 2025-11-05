from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from .models import Consommation, Production, ConsommationMatierePremiere

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ["site", "produit_fini", "quantite_produite", "date"]
        widgets = {
            "site": forms.Select(attrs={"class": "form-control"}),
            "produit_fini": forms.Select(attrs={"class": "form-control"}),
            "quantite_produite": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def clean_quantite_produite(self):
        q = self.cleaned_data.get("quantite_produite") or Decimal("0")
        if q <= 0:
            raise ValidationError("La quantité produite doit être > 0.")
        return q


class ConsommationForm(forms.ModelForm):
    class Meta:
        model = ConsommationMatierePremiere
        fields = ["production", "produit_mp", "quantite_utilisee"]
        widgets = {
            "production": forms.Select(attrs={"class": "form-control"}),
            "produit_mp": forms.Select(attrs={"class": "form-control"}),
            "quantite_utilisee": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
        }

    def clean(self):
        cleaned = super().clean()
        produit_mp = cleaned.get("produit_mp")
        qte = cleaned.get("quantite_utilisee") or Decimal("0")
        if produit_mp and qte > 0:
            stock = getattr(produit_mp, "stock", None)
            if stock and qte > stock.quantite_restante:
                raise ValidationError("Stock MP insuffisant pour cette consommation.")
        return cleaned
    




class ConsommationForm(forms.ModelForm):
    class Meta:
        model = Consommation
        fields = ["produit", "site", "quantite"]
        widgets = {
            "quantite": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
        }
# production/forms.py
from django import forms
from .models import Production, ConsommationMatierePremiere

class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ["site", "produit_fini", "quantite_produite", "date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


class ConsommationMatierePremiereForm(forms.ModelForm):
    class Meta:
        model = ConsommationMatierePremiere
        fields = ["produit_mp", "quantite_utilisee"]
        widgets = {
            "quantite_utilisee": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
        }

