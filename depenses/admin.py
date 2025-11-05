from django.contrib import admin
from .models import CategorieDepense, Depense

@admin.register(CategorieDepense)
class CategorieDepenseAdmin(admin.ModelAdmin):
    list_display = ("id", "nom")
    search_fields = ("nom",)

@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ("id", "site", "categorie", "montant", "date", "description_courte")
    list_filter = ("site", "categorie", "date")
    search_fields = ("site__nom", "categorie__nom", "description")
    date_hierarchy = "date"
    autocomplete_fields = ("site", "categorie")

    def description_courte(self, obj):
        return (obj.description or "")[:60]
    description_courte.short_description = "Description"
