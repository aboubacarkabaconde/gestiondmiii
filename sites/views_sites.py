from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SiteFabrication
from .forms import SiteFabricationForm

@login_required
def liste_sites(request):
    sites = SiteFabrication.objects.all().order_by("nom")
    return render(request, "sites/liste.html", {"sites": sites})

@login_required
def ajouter_site(request):
    if request.method == "POST":
        form = SiteFabricationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Site créé avec succès !")
            return redirect("sites:liste")
    else:
        form = SiteFabricationForm()
    return render(request, "sites/form.html", {"form": form})

@login_required
def modifier_site(request, id):
    site = get_object_or_404(SiteFabrication, pk=id)
    if request.method == "POST":
        form = SiteFabricationForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, "Site modifié avec succès !")
            return redirect("sites:liste")
    else:
        form = SiteFabricationForm(instance=site)
    return render(request, "sites/form.html", {"form": form})

@login_required
def supprimer_site(request, id):
    site = get_object_or_404(SiteFabrication, pk=id)
    if request.method == "POST":
        site.delete()
        messages.success(request, "Site supprimé avec succès !")
        return redirect("sites:liste")
    return render(request, "sites/supprimer.html", {"site": site})
