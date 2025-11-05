from django import forms
from .models import Produit

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ["nom", "type", "unite", "poids_total", "quantite_disponible", "site"]
        widgets = {
            "nom":  forms.TextInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-control"}),
            "unite": forms.TextInput(attrs={"class": "form-control"}),
            "poids_total": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "quantite_disponible": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "site": forms.Select(attrs={"class": "form-control"}),
        }
