from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Production, ConsommationMatierePremiere
from .forms import ProductionForm, ConsommationMatierePremiereForm

# Liste des productions
@login_required
def liste_productions(request):
    productions = Production.objects.select_related("produit_fini", "site").prefetch_related("consommations")
    return render(request, "production/liste.html", {"productions": productions})


# Modifier une production
@login_required
def modifier_production(request, id):
    production = get_object_or_404(Production, pk=id)
    if request.method == "POST":
        form = ProductionForm(request.POST, instance=production)
        if form.is_valid():
            form.save()
            messages.success(request, "Production modifiée avec succès ✏️")
            return redirect("production:liste_productions")
    else:
        form = ProductionForm(instance=production)
    return render(request, "production/form.html", {"form": form, "production": production})


# Supprimer une production
@login_required
def supprimer_production(request, id):
    production = get_object_or_404(Production, pk=id)
    if request.method == "POST":
        production.delete()
        messages.success(request, "Production supprimée avec succès 🗑️")
        return redirect("production:liste_productions")
    return render(request, "production/supprimer_production.html", {"production": production})


# Modifier une consommation MP
@login_required
def modifier_consommation_mp(request, id):
    consommation = get_object_or_404(ConsommationMatierePremiere, pk=id)
    if request.method == "POST":
        form = ConsommationMatierePremiereForm(request.POST, instance=consommation)
        if form.is_valid():
            form.save()
            consommation.produit_mp.maj_stock()
            messages.success(request, "Consommation modifiée avec succès ✏️")
            return redirect("production:detail_production", id=consommation.production.id)
    else:
        form = ConsommationMatierePremiereForm(instance=consommation)
    return render(request, "production/form_consommation.html", {"form": form, "production": consommation.production})


# Ajouter une production avec consommation de MP
@login_required
def ajouter_production(request):
    if request.method == "POST":
        form = ProductionForm(request.POST)
        if form.is_valid():
            production = form.save()
            messages.success(request, "Production ajoutée avec succès ✅")
            return redirect("production:liste_productions")
    else:
        form = ProductionForm()
    return render(request, "production/form.html", {"form": form})


# Voir le détail d’une production + consommations
@login_required
def detail_production(request, id):
    production = get_object_or_404(Production.objects.prefetch_related("consommations__produit_mp"), pk=id)
    return render(request, "production/detail.html", {"production": production})


# Ajouter une consommation de MP à une production
@login_required
def ajouter_consommation_mp(request, production_id):
    production = get_object_or_404(Production, pk=production_id)
    if request.method == "POST":
        form = ConsommationMatierePremiereForm(request.POST)
        if form.is_valid():
            consommation = form.save(commit=False)
            consommation.production = production
            consommation.save()
            consommation.produit_mp.maj_stock()  # ✅ met à jour stock
            messages.success(request, "Consommation de matière première ajoutée ✅")
            return redirect("production:detail_production", id=production.id)
    else:
        form = ConsommationMatierePremiereForm()
    return render(request, "production/form_consommation.html", {"form": form, "production": production})


# Supprimer une consommation
@login_required
def supprimer_consommation_mp(request, id):
    consommation = get_object_or_404(ConsommationMatierePremiere, pk=id)
    production_id = consommation.production.id
    if request.method == "POST":
        produit = consommation.produit_mp
        consommation.delete()
        produit.maj_stock()
        messages.success(request, "Consommation supprimée avec succès 🗑️")
        return redirect("production:detail_production", id=production_id)
    return render(request, "production/supprimer_consommation.html", {"consommation": consommation})
