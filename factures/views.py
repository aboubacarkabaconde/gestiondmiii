from django.shortcuts import render

# Create your views here.
import csv
from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum,Count
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date
from django.http import Http404
from .models import Facture, Paiement
from .forms import FactureForm, PaiementForm
from sites.models import SiteFabrication  # adapte si besoin
from django.core.paginator import Paginator
from django.utils.timezone import now
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

@login_required
def liste_factures(request):
    """
    Vue combinée :
    - ajout d'une facture via formulaire
    - filtres (type, site, période)
    - KPIs financiers
    - graphiques par mois / site / type
    - liste paginée des factures
    """
    # ======================
    # 1) Gestion du formulaire
    # ======================
    if request.method == "POST":
        form = FactureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Facture enregistrée avec succès ✅")
            return redirect("factures:liste")
    else:
        form = FactureForm()

    # ======================
    # 2) Queryset + Filtres
    # ======================
    qs = Facture.objects.select_related("site").all()

    type_f = request.GET.get("type")
    site_id = request.GET.get("site")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if type_f:
        qs = qs.filter(type=type_f)
    if site_id:
        qs = qs.filter(site_id=site_id)
    if start:
        qs = qs.filter(date__gte=parse_date(start))
    if end:
        qs = qs.filter(date__lte=parse_date(end))

    factures = qs.order_by("-date")

    # ======================
    # 3) KPIs financiers
    # ======================
    totaux = qs.aggregate(
        montant_total=Sum("total"),
        montant_paye=Sum("montant_paye"),
    )
    montant_total = totaux["montant_total"] or 0
    montant_paye = totaux["montant_paye"] or 0
    montant_a_recouvrer = montant_total - montant_paye

    today = now().date()
    montant_mensuel = (
        qs.filter(date__year=today.year, date__month=today.month)
        .aggregate(total=Sum("total"))["total"]
        or 0
    )

    # ======================
    # 4) Données pour graphiques
    # ======================
    # CA par mois
    monthly = (
        qs.annotate(m=TruncMonth("date"))
        .values("m")
        .order_by("m")
        .annotate(total=Sum("total"))
    )
    labels = [row["m"].strftime("%m/%Y") for row in monthly]
    serie_ventes = [float(row["total"] or 0) for row in monthly]

    # CA par site
    per_site = qs.values("site__nom").order_by("site__nom").annotate(total=Sum("total"))
    chart_sites = {
        "labels": [row["site__nom"] or "—" for row in per_site],
        "data": [float(row["total"] or 0) for row in per_site],
    }

    # Répartition par type
    per_type = qs.values("type").order_by("type").annotate(total=Sum("total"))
    chart_types = {
        "labels": [row["type"] for row in per_type],
        "data": [float(row["total"] or 0) for row in per_type],
    }

    # ======================
    # 5) Pagination
    # ======================
    paginator = Paginator(factures, 10)  # 10 factures par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ======================
    # 6) Contexte global
    # ======================
    context = {
        "form": form,
        "page_obj": page_obj,
        "sites": SiteFabrication.objects.all(),

        # KPIs
        "montant_total": montant_total,
        "montant_paye": montant_paye,
        "montant_a_recouvrer": montant_a_recouvrer,
        "montant_mensuel": montant_mensuel,

        # Graphiques
        "labels": labels,
        "serie_ventes": serie_ventes,
        "chart_sites": chart_sites,
        "chart_types": chart_types,
    }
    return render(request, "factures/liste.html", context)

    

@login_required
def detail_facture(request, id):
    facture = get_object_or_404(Facture.objects.select_related("site"), pk=id)
    paiements = facture.paiements.select_related("produit").all()
    return render(request, "factures/detail.html", {"facture": facture, "paiements": paiements})

@login_required
def ajouter_facture(request):
    type_forced = request.GET.get("type")  # "achat" ou "vente"
    map_in = {"achat": "Achat", "vente": "Vente"}

    if request.method == "POST":
        form = FactureForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            if type_forced in map_in:
                obj.type = map_in[type_forced]
            obj.save()
            messages.success(request, "Facture créée.")
            return redirect("factures:liste")
    else:
        initial = {}
        if type_forced in map_in:
            initial["type"] = map_in[type_forced]
        form = FactureForm(initial=initial)
        if type_forced in map_in and "type" in form.fields:
            form.fields["type"].disabled = True

    return render(request, "factures/form.html", {"form": form})


@login_required
def modifier_facture(request, id):
    facture = get_object_or_404(Facture, pk=id)
    if request.method == "POST":
        form = FactureForm(request.POST, instance=facture)
        if form.is_valid():
            form.save()
            messages.success(request, "Facture modifiée avec succès !")
            return redirect("factures:liste")
    else:
        form = FactureForm(instance=facture)
    return render(request, "factures/form.html", {"form": form})

@login_required
def supprimer_facture(request, id):
    facture = get_object_or_404(Facture, pk=id)
    if request.method == "POST":
        facture.delete()
        messages.success(request, "Facture supprimée avec succès !")
        return redirect("factures:liste")
    return render(request, "factures/supprimer_facture.html", {"facture": facture})
@login_required
def enregistrer_paiement(request, id):
    facture = get_object_or_404(Facture, pk=id)

    if request.method == "POST":
        # ✅ on passe la facture au form
        form = PaiementForm(request.POST, facture=facture)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.facture = facture
            # calcule le montant si absent
            if not paiement.montant_total and paiement.quantite and paiement.prix_unitaire:
                paiement.montant_total = Decimal(paiement.quantite) * Decimal(paiement.prix_unitaire)
            paiement.save()  # ➜ déclenche les signaux de MAJ stock
            messages.success(request, "Paiement enregistré avec succès !")
            return redirect("factures:detail", id=facture.id)
    else:
        # (facultatif) on peut aussi passer la facture en GET
        form = PaiementForm(facture=facture)

    return render(request, "factures/paiement.html", {"form": form, "facture": facture})

@login_required
def export_factures_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="factures.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Type", "Site", "Date", "Montant total (FG)", "Payé (FG)", "Restant (FG)"])

    for f in Facture.objects.select_related("site").all().order_by("-date"):
        writer.writerow([
            f.id,
            f.type,
            f.site.nom if f.site else "—",
            f.date.strftime("%d/%m/%Y") if f.date else "",
            f"{f.total:.2f}" if f.total else "0.00",
            f"{f.montant_paye:.2f}" if f.montant_paye else "0.00",
            f"{f.restant:.2f}"  # ✅ grâce à la propriété
        ])
    return response



@login_required
def export_factures_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []

    styles = getSampleStyleSheet() # type: ignore
    title = Paragraph("Liste des Factures", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [["ID", "Type", "Site", "Date", "Montant (FG)", "Payé (FG)", "Restant (FG)"]]

    for f in Facture.objects.select_related("site").all().order_by("-date"):
        data.append([
            f.id,
            f.type,
            f.site.nom if f.site else "—",
            f.date.strftime("%d/%m/%Y") if f.date else "",
            f"{f.total:.2f}" if f.total else "0.00",
            f"{f.montant_paye:.2f}" if f.montant_paye else "0.00",
            f"{f.restant:.2f}"  # ✅ affichage du restant
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007BFF")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="factures.pdf"'
    response.write(pdf)
    return response


# ---------- STATISTIQUES VENTES ----------
@login_required
def stats_ventes(request):
    """
    Courbe mensuelle du CA (factures de type Vente), avec filtre période [start, end] et site_id.
    Renvoie: labels, serie_ventes, total_ventes, ventes_par_mois
    """
    qs = Facture.objects.filter(type="Vente")
    start = parse_date(request.GET.get("start") or "")
    end = parse_date(request.GET.get("end") or "")
    site_id = request.GET.get("site_id")

    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if site_id:
        qs = qs.filter(site_id=site_id)

    # Groupement par mois
    serie = (qs.annotate(m=TruncMonth("date"))
               .values("m").annotate(total=Sum("total")).order_by("m"))

    labels = [x["m"].strftime("%m/%Y") for x in serie]
    data = [float(x["total"] or 0) for x in serie]
    total = float(qs.aggregate(s=Sum("total"))["s"] or 0)

    ctx = {
        "labels": labels,
        "serie_ventes": data,
        "total_ventes": total,
        "filtre": {"start": start, "end": end, "site_id": site_id},
        "ventes_par_mois": serie,
    }
    return render(request, "stats/ventes.html", ctx)

@login_required
def ajouter_facture_by_type(request, kind):
    type_map = {"achats": "Achat", "ventes": "Vente"}
    if kind not in type_map:
        raise Http404("Type de facture invalide.")

    if request.method == "POST":
        form = FactureForm(request.POST)
        if form.is_valid():
            facture = form.save(commit=False)
            facture.type = type_map[kind]  # force le type
            facture.save()
            messages.success(request, f"Facture {facture.type} créée avec succès !")
            return redirect("factures:liste")
    else:
        form = FactureForm(initial={"type": type_map[kind]})

    # (optionnel) empêcher l’édition du champ 'type' dans le formulaire s’il existe
    if "type" in form.fields:
        form.fields["type"].disabled = True

    # NOTE: adapte le chemin du template si ton fichier est ailleurs
    return render(request, "factures/form.html", {"form": form, "facture": None})


def save(self, *args, **kwargs):
    # Assurer que les champs sont bien initialisés
    if self.quantite is not None and self.prix_unitaire is not None:
        self.total = self.quantite * self.prix_unitaire
    else:
        self.total = 0

    # Détermination du statut
    if self.montant_paye is None:
        self.montant_paye = 0

    if self.montant_paye >= self.total:
        self.status = "payee"
    elif 0 < self.montant_paye < self.total:
        self.status = "partielle"
    else:
        self.status = "impayee"

    super().save(*args, **kwargs)





from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Facture
from sites.models import SiteFabrication

@login_required
def stats_factures(request):
    """
    Vue combinée statistiques des factures :
    - Courbe mensuelle (CA)
    - Répartition par type (Achat/Vente)
    - Répartition par statut (payée, partielle, impayée)
    """

    qs = Facture.objects.all()

    # --- Filtres ---
    start = parse_date(request.GET.get("start") or "")
    end = parse_date(request.GET.get("end") or "")
    site_id = request.GET.get("site_id")

    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    if site_id:
        qs = qs.filter(site_id=site_id)

    # --- Courbe mensuelle ---
    serie = (
        qs.annotate(m=TruncMonth("date"))
          .values("m")
          .annotate(total=Sum("total"))
          .order_by("m")
    )

    labels = [x["m"].strftime("%m/%Y") for x in serie]
    data = [float(x["total"] or 0) for x in serie]
    total = float(qs.aggregate(s=Sum("total"))["s"] or 0)

    # --- Répartition par type (Achat/Vente) ---
    par_type = (
        qs.values("type")
          .annotate(total=Sum("total"), count=Count("id"))
          .order_by("type")
    )

    # --- Répartition par statut ---
    par_statut = (
        qs.values("status")
          .annotate(total=Sum("total"), count=Count("id"))
          .order_by("status")
    )

    # --- Contexte ---
    ctx = {
        # courbe mensuelle
        "labels": labels,
        "serie_factures": data,
        "total_factures": total,
        "factures_par_mois": serie,

        # répartitions
        "par_type": list(par_type),
        "par_statut": list(par_statut),

        # filtres & choix
        "filtre": {"start": start, "end": end, "site_id": site_id},
        "sites": SiteFabrication.objects.all(),
    }
    return render(request, "factures/stats.html", ctx)

