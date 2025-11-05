from django import forms
from django.core.exceptions import ValidationError
from .models import Depense

class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ["site", "categorie", "montant", "description"]
        widgets = {
            "site":      forms.Select(attrs={"class": "form-control"}),
            "categorie": forms.Select(attrs={"class": "form-control"}),
            "montant":   forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "date":      forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def clean_montant(self):
        m = self.cleaned_data.get("montant")
        if m is None or m < 0:
            raise ValidationError("Le montant doit être positif.")
        return m


# --------- Formulaire de filtres pour la page Stats Dépenses ---------
class StatsDepensesFilterForm(forms.Form):
    start = forms.DateField(required=False, widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    end   = forms.DateField(required=False, widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    site_id = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}))
    categorie_id = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}))
