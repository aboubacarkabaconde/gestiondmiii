# core/views.py
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from django.utils import timezone


# core/views.py (extrait)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from django.utils.dateparse import parse_date

from factures.models import Facture, Paiement
from depenses.models import Depense
from produits.models import Produit
from production.models import Production
from sites.models import SiteFabrication, Employe


from factures.models import Facture
from produits.models import Stock

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth

from depenses.models import Depense
from factures.models import Facture
from sites.models import Employe
from produits.models import Produit
from produits.models import Stock  # si tu as bien ce modèle
from django.utils import timezone
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth

# Données métier
from depenses.models import Depense
from factures.models import Facture, Paiement
from produits.models import Produit, Stock
from sites.models import SiteFabrication, Employe
from production.models import Production, ConsommationMatierePremiere


@login_required
def dashboard(request):
    today = timezone.localdate()
    start_month = today.replace(day=1)
    six_months_ago = start_month - timezone.timedelta(days=180)

    mois = today.month
    annee = today.year

    # ========================
    # KPIs
    # ========================
    depenses_mois = (
        Depense.objects.filter(date__month=mois, date__year=annee)
        .aggregate(total=Sum("montant"))["total"] or 0
    )
    ca_mois = (
        Facture.objects.filter(type="Vente", date__month=mois, date__year=annee)
        .aggregate(total=Sum("total"))["total"] or 0
    )
    alertes_stock = Produit.objects.filter(quantite_stock__lte=5).count()
    total_employes = Employe.objects.count()

    # Stocks bas via Stock (si défini)
    stocks_bas = Stock.objects.filter(
        quantite_restante__lte=F("quantite_initiale") * 0.1
    ).select_related("produit")

    # ========================
    # Séries (6 derniers mois)
    # ========================
    ventes_series = (
        Facture.objects.filter(type="Vente", date__gte=six_months_ago)
        .annotate(m=TruncMonth("date"))
        .values("m")
        .annotate(total=Sum("total"))
        .order_by("m")
    )
    depenses_series = (
        Facture.objects.filter(type="Achat", date__gte=six_months_ago)
        .annotate(m=TruncMonth("date"))
        .values("m")
        .annotate(total=Sum("total"))
        .order_by("m")
    )

    months = []
    cursor = six_months_ago
    for _ in range(6):
        months.append(cursor.strftime("%m/%Y"))
        # avancer d'un mois
        if cursor.month == 12:
            cursor = cursor.replace(year=cursor.year + 1, month=1)
        else:
            cursor = cursor.replace(month=cursor.month + 1)

    ventes_map = {x["m"].strftime("%m/%Y"): float(x["total"] or 0) for x in ventes_series}
    depenses_map = {x["m"].strftime("%m/%Y"): float(x["total"] or 0) for x in depenses_series}

    chart_data = {
        "labels": months,
        "ventes": [ventes_map.get(m, 0) for m in months],
        "depenses": [depenses_map.get(m, 0) for m in months],
    }

    # ========================
    # Derniers enregistrements
    # ========================
    dernieres_depenses = Depense.objects.order_by("-date")[:5]
    dernieres_factures = Facture.objects.order_by("-date")[:5]

    # ========================
    # Contexte rendu
    # ========================
    context = {
        "depenses_mois": depenses_mois,
        "ca_mois": ca_mois,
        "alertes_stock": alertes_stock,
        "total_employes": total_employes,
        "dernieres_depenses": dernieres_depenses,
        "dernieres_factures": dernieres_factures,
        "stocks_bas": stocks_bas,
        "chart_data_json": json.dumps(chart_data),
    }

    return render(request, "dashboard.html", context)







@login_required
def search(request):
    """
    Recherche transversale (factures, paiements, dépenses, produits, productions, sites, employés)
    Filtres:
      - q: terme de recherche
      - start, end: dates (YYYY-MM-DD) appliquées aux modèles qui ont une date
      - model: limiter à un module (factures|paiements|depenses|produits|production|sites|employes)
    """
    q = (request.GET.get("q") or "").strip()
    start = parse_date(request.GET.get("start") or "")
    end = parse_date(request.GET.get("end") or "")
    model = (request.GET.get("model") or "").lower()

    results = {}
    total_count = 0

    # Petits helpers
    def apply_date(qs, field_name):
        nonlocal start, end
        if start:
            qs = qs.filter(**{f"{field_name}__gte": start})
        if end:
            qs = qs.filter(**{f"{field_name}__lte": end})
        return qs

    def maybe_id_filter(qs, field="id"):
        # si q est un entier, on permet la recherche par id
        if q.isdigit():
            return qs.filter(Q(**{field: int(q)}) | Q(**{f"{field}__icontains": q}))
        return qs

    # --- FACTURES ---
    if not model or model == "factures":
        qs = Facture.objects.select_related("site").all()
        if q:
            qs = qs.filter(
                Q(type__icontains=q) |
                Q(site__nom__icontains=q)
            )
            qs = maybe_id_filter(qs, "id")
        qs = apply_date(qs, "date").order_by("-date", "-id")[:25]
        results["factures"] = list(qs)
        total_count += qs.count()

    # --- PAIEMENTS ---
    if not model or model == "paiements":
        qs = Paiement.objects.select_related("facture", "produit", "facture__site").all()
        if q:
            qs = qs.filter(
                Q(produit__nom__icontains=q) |
                Q(mode_paiement__icontains=q) |
                Q(facture__site__nom__icontains=q)
            )
            if q.isdigit():
                qs = qs.filter(Q(facture__id=int(q)) | Q(id=int(q)) | Q(facture__id__icontains=q))
        qs = apply_date(qs, "date_paiement").order_by("-date_paiement", "-id")[:25]
        results["paiements"] = list(qs)
        total_count += qs.count()

    # --- DEPENSES ---
    if not model or model == "depenses":
        qs = Depense.objects.select_related("site", "categorie").all()
        if q:
            qs = qs.filter(
                Q(site__nom__icontains=q) |
                Q(categorie__nom__icontains=q) |
                Q(description__icontains=q)
            )
        qs = apply_date(qs, "date").order_by("-date", "-id")[:25]
        results["depenses"] = list(qs)
        total_count += qs.count()

    # --- PRODUITS ---
    if not model or model == "produits":
        qs = Produit.objects.select_related("site").all()
        if q:
            # autoriser MP/PF comme filtre rapide
            t = q.upper()
            qs = qs.filter(
                Q(nom__icontains=q) |
                Q(unite__icontains=q) |
                Q(site__nom__icontains=q) |
                Q(type=t)  # MP / PF
            )
        qs = qs.order_by("nom")[:25]
        results["produits"] = list(qs)
        total_count += qs.count()

    # --- PRODUCTION ---
    if not model or model == "production":
        qs = Production.objects.select_related("site", "produit_fini").all()
        if q:
            qs = qs.filter(
                Q(produit_fini__nom__icontains=q) |
                Q(site__nom__icontains=q)
            )
        qs = apply_date(qs, "date").order_by("-date", "-id")[:25]
        results["production"] = list(qs)
        total_count += qs.count()

    # --- SITES ---
    if not model or model == "sites":
        qs = SiteFabrication.objects.all()
        if q:
            qs = qs.filter(Q(nom__icontains=q) | Q(localisation__icontains=q))
        qs = qs.order_by("nom")[:25]
        results["sites"] = list(qs)
        total_count += qs.count()

    # --- EMPLOYÉS ---
    if not model or model == "employes":
        qs = Employe.objects.select_related("site").all()
        if q:
            qs = qs.filter(
                Q(nom__icontains=q) |
                Q(poste__icontains=q) |
                Q(site__nom__icontains=q) |
                Q(situation_matrimoniale__icontains=q)
            )
        # Si start/end fournis, on applique sur date_embauche
        if start or end:
            qs = apply_date(qs, "date_embauche")
        qs = qs.order_by("nom")[:25]
        results["employes"] = list(qs)
        total_count += qs.count()

    context = {
        "q": q,
        "start": start,
        "end": end,
        "model": model,
        "results": results,
        "total_count": total_count,
    }
    return render(request, "search/results.html", context)

# core/views.py
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


