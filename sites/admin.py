from django.contrib import admin
from .models import SiteFabrication, Employe

@admin.register(SiteFabrication)
class SiteFabricationAdmin(admin.ModelAdmin):
    list_display = ("id", "nom", "localisation")
    search_fields = ("nom", "localisation")

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ("id", "nom", "poste", "site", "date_embauche", "situation_matrimoniale", "salaire")
    list_filter = ("site", "situation_matrimoniale", "date_embauche")
    search_fields = ("nom", "poste", "site__nom")
    date_hierarchy = "date_embauche"
    autocomplete_fields = ("site",)
