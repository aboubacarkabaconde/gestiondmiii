from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employe
from .forms import EmployeForm

@login_required
def liste_employes(request):
    employes = Employe.objects.select_related("site").order_by("nom")
    return render(request, "employes/list.html", {"employes": employes})

@login_required
def ajouter_employe(request):
    if request.method == "POST":
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employé ajouté avec succès !")
            return redirect("employes:liste")
    else:
        form = EmployeForm()
    return render(request, "employes/form.html", {"form": form})

@login_required
def modifier_employe(request, id):
    e = get_object_or_404(Employe, pk=id)
    if request.method == "POST":
        form = EmployeForm(request.POST, instance=e)
        if form.is_valid():
            form.save()
            messages.success(request, "Employé modifié avec succès !")
            return redirect("employes:liste")
    else:
        form = EmployeForm(instance=e)
    return render(request, "employes/form.html", {"form": form})

@login_required
def supprimer_employe(request, id):
    e = get_object_or_404(Employe, pk=id)
    if request.method == "POST":
        e.delete()
        messages.success(request, "Employé supprimé avec succès !")
        return redirect("employes:liste")
    return render(request, "employes/supprimer.html", {"employe": e})
