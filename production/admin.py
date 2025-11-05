from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Production, ConsommationMatierePremiere

class ConsommationInline(admin.TabularInline):
    model = ConsommationMatierePremiere
    extra = 1
    fields = ("produit_mp", "quantite_utilisee")
    autocomplete_fields = ("produit_mp",)

@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ("id", "site", "produit_fini", "quantite_produite", "date")
    list_filter = ("site", "produit_fini", "date")
    search_fields = ("site__nom", "produit_fini__nom")
    date_hierarchy = "date"
    inlines = (ConsommationInline,)
    autocomplete_fields = ("site", "produit_fini")

@admin.register(ConsommationMatierePremiere)
class ConsommationAdmin(admin.ModelAdmin):
    list_display = ("id", "production", "produit_mp", "quantite_utilisee")
    search_fields = ("production__id", "produit_mp__nom")
    list_filter = ("produit_mp",)
    autocomplete_fields = ("production", "produit_mp")
