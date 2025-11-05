from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit
from .forms import ProduitForm
from django.core.paginator import Paginator
from django.db.models import Sum, F, DecimalField, ExpressionWrapper



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Produit


@login_required
def liste_produits(request):
    """
    Liste des produits avec pagination, graphiques et KPIs globaux.
    """
    produits = Produit.objects.select_related("site").all().order_by("nom")

    # Pagination
    paginator = Paginator(produits, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Données pour graphiques (stocks par produit)
    labels = [p.nom for p in produits]
    stocks = [float(p.quantite_stock or 0) for p in produits]

    # KPIs globaux
    total_mp = produits.filter(type="MP").aggregate(total=Sum("quantite_stock"))["total"] or 0
    total_pf = produits.filter(type="PF").aggregate(total=Sum("quantite_stock"))["total"] or 0
    valeur_globale = produits.aggregate(total=Sum("quantite_stock"))["total"] or 0

    # Données pour camembert MP vs PF
    labels_type = ["Matières Premières", "Produits Finis"]
    data_type = [float(total_mp), float(total_pf)]

    context = {
        "page_obj": page_obj,
        "labels": labels,
        "stocks": stocks,
        "total_mp": total_mp,
        "total_pf": total_pf,
        "valeur_globale": valeur_globale,
        "labels_type": labels_type,
        "data_type": data_type,
    }
    return render(request, "produits/liste.html", context)



@login_required
def ajouter_produit(request):
    if request.method == "POST":
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit créé avec succès !")
            return redirect("produits:liste")
    else:
        form = ProduitForm()
    return render(request, "produits/form.html", {"form": form})

@login_required
def modifier_produit(request, id):
    p = get_object_or_404(Produit, pk=id)
    if request.method == "POST":
        form = ProduitForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès !")
            return redirect("produits:detail", id=p.id)
    else:
        form = ProduitForm(instance=p)
    return render(request, "produits/form.html", {"form": form})

@login_required
def supprimer_produit(request, id):
    p = get_object_or_404(Produit, pk=id)
    if request.method == "POST":
        p.delete()
        messages.success(request, "Produit supprimé avec succès !")
        return redirect("produits:liste")
    return render(request, "produits/supprimer.html", {"produit": p})


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Produit

@login_required
def detail_produit(request, id):
    """
    Détail d’un produit (fiche produit).
    """
    produit = get_object_or_404(Produit, pk=id)
    return render(request, "produits/detail.html", {"produit": produit})



@login_required
def stock_view(request):
    """
    Vue de gestion du stock : liste des produits + KPI + graphiques.
    """
    produits = Produit.objects.select_related("site").all().order_by("nom")


    # Pagination (10 produits par page)
    paginator = paginator(produits, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # KPI
    total_mp = produits.filter(type="MP").aggregate(total=Sum("quantite_stock"))["total"] or 0
    total_pf = produits.filter(type="PF").aggregate(total=Sum("quantite_stock"))["total"] or 0
    valeur_globale = produits.aggregate(total=Sum("quantite_stock"))["total"] or 0

    # Graphique 1 : répartition MP vs PF
    repartition_type = {
        "labels": ["Matières Premières", "Produits Finis"],
        "data": [float(total_mp), float(total_pf)],
    }

    # Graphique 2 : stock par site
    per_site = produits.values("site__nom").annotate(total=Sum("quantite_stock")).order_by("site__nom")
    repartition_sites = {
        "labels": [row["site__nom"] or "—" for row in per_site],
        "data": [float(row["total"] or 0) for row in per_site],
    }

    ctx = {
        "page_obj": page_obj,  # ✅ utilisé dans le template
        "total_mp": total_mp,
        "total_pf": total_pf,
        "valeur_globale": valeur_globale,
        "repartition_type": repartition_type,
        "repartition_sites": repartition_sites,
    }
    return render(request, "produits/stock.html", ctx)