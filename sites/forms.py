from django import forms
from .models import SiteFabrication, Employe

class SiteFabricationForm(forms.ModelForm):
    class Meta:
        model = SiteFabrication
        fields = ["nom", "localisation"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "localisation": forms.TextInput(attrs={"class": "form-control"}),
        }

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ["nom","poste","salaire","site","date_embauche","situation_matrimoniale"]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "poste": forms.TextInput(attrs={"class": "form-control"}),
            "salaire": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "site": forms.Select(attrs={"class": "form-control"}),
            "date_embauche": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "situation_matrimoniale": forms.Select(attrs={"class": "form-control"}),
        }
