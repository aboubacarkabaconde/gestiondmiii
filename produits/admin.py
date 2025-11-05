from django.contrib import admin
from .models import Produit, Stock

class StockInline(admin.StackedInline):
    model = Stock
    can_delete = False
    extra = 0
    fk_name = "produit"
    fields = ("quantite_initiale", "quantite_utilisee", "quantite_restante",)
    readonly_fields = ()

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("id", "nom", "type", "unite", "quantite_disponible", "site", "stock_rest")
    list_filter = ("type", "site")
    search_fields = ("nom", "site__nom", "unite")
    inlines = (StockInline,)
    autocomplete_fields = ("site",)

    def stock_rest(self, obj):
        if hasattr(obj, "stock") and obj.stock:
            return obj.stock.quantite_restante
        return "-"
    stock_rest.short_description = "Stock restant"

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("produit", "quantite_initiale", "quantite_utilisee", "quantite_restante")
    search_fields = ("produit__nom",)
    autocomplete_fields = ("produit",)
