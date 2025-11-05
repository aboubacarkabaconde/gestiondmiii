from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from django.utils.dateparse import parse_date
from django.http import HttpResponse
import csv
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

from .models import Depense
from .forms import DepenseForm


# -------------------- LISTE --------------------
@login_required
def liste_depenses(request):
    """
    Liste paginée des dépenses + ajout via formulaire.
    """
    from django.core.paginator import Paginator

    if request.method == "POST":
        form = DepenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Dépense enregistrée avec succès ✅")
            return redirect("depenses:liste")
    else:
        form = DepenseForm()

    # KPIs
    montant_total = Depense.objects.aggregate(total=Sum("montant"))["total"] or 0
    today = now().date()
    montant_mensuel = (
        Depense.objects.filter(date__year=today.year, date__month=today.month)
        .aggregate(total=Sum("montant"))["total"]
        or 0
    )

    # Données pour graphiques
    serie = (
        Depense.objects.annotate(m=TruncMonth("date"))
        .values("m")
        .annotate(total=Sum("montant"))
        .order_by("m")
    )
    labels = [row["m"].strftime("%m/%Y") for row in serie]
    data = [float(row["total"] or 0) for row in serie]
    serie_depenses = {"labels": labels, "data": data}

    # Pagination
    depenses = Depense.objects.all().order_by("-date")
    paginator = Paginator(depenses, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    ctx = {
        "form": form,
        "page_obj": page_obj,
        "montant_total": montant_total,
        "montant_mensuel": montant_mensuel,
        "serie_depenses": serie_depenses,
    }
    return render(request, "depenses/liste.html", ctx)


# -------------------- DETAIL --------------------
@login_required
def detail_depense(request, id):
    depense = get_object_or_404(Depense, pk=id)
    return render(request, "depenses/detail.html", {"depense": depense})


# -------------------- AJOUTER --------------------
@login_required
def ajouter_depense(request):
    if request.method == "POST":
        form = DepenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Dépense ajoutée avec succès ✅")
            return redirect("depenses:liste")
    else:
        form = DepenseForm()
    return render(request, "depenses/form.html", {"form": form, "depense": None})


# -------------------- MODIFIER --------------------
@login_required
def modifier_depense(request, id):
    depense = get_object_or_404(Depense, pk=id)
    if request.method == "POST":
        form = DepenseForm(request.POST, instance=depense)
        if form.is_valid():
            form.save()
            messages.success(request, "Dépense modifiée ✅")
            return redirect("depenses:liste")
    else:
        form = DepenseForm(instance=depense)
    return render(request, "depenses/form.html", {"form": form, "depense": depense})


# -------------------- SUPPRIMER --------------------
@login_required
def supprimer_depense(request, id):
    depense = get_object_or_404(Depense, pk=id)
    if request.method == "POST":
        depense.delete()
        messages.success(request, "Dépense supprimée ✅")
        return redirect("depenses:liste")
    return render(request, "depenses/supprimer_depense.html", {"depense": depense})


# -------------------- EXPORT CSV --------------------
@login_required
def export_depenses_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="depenses.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Date", "Site", "Catégorie", "Description", "Montant (GNF)"])

    for d in Depense.objects.select_related("site", "categorie").all().order_by("-date"):
        writer.writerow([
            d.id,
            d.date.strftime("%d/%m/%Y") if d.date else "",
            d.site.nom if d.site else "—",
            d.categorie.nom if d.categorie else "—",
            d.description or "",
            f"{d.montant:.2f}" if d.montant else "0.00"
        ])
    return response




# -------------------- STATS --------------------
@login_required
def stats_depenses(request):
    qs = Depense.objects.all()

    start = parse_date(request.GET.get("start") or "")
    end = parse_date(request.GET.get("end") or "")
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)

    total_depenses = qs.aggregate(total=Sum("montant"))["total"] or 0

    # Mensuel
    serie = (
        qs.annotate(m=TruncMonth("date"))
        .values("m")
        .annotate(total=Sum("montant"))
        .order_by("m")
    )
    labels = [row["m"].strftime("%m/%Y") for row in serie]
    data = [float(row["total"] or 0) for row in serie]
    serie_depenses = {"labels": labels, "data": data}

    # Par catégorie
    categories = (
        qs.values("categorie")
        .annotate(total=Sum("montant"))
        .order_by("categorie")
    )
    chart_categories = {
        "labels": [row["categorie"] or "—" for row in categories],
        "data": [float(row["total"] or 0) for row in categories],
    }

    ctx = {
        "total_depenses": total_depenses,
        "serie_depenses": serie_depenses,
        "chart_categories": chart_categories,
        "filtre": {"start": start, "end": end},
    }
    return render(request, "depenses/stats.html", ctx)




@login_required
def export_depenses_pdf(request):
    """
    Exporte toutes les dépenses en PDF (tableau imprimable).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("Liste des Dépenses", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Header
    data = [["ID", "Date", "Site", "Catégorie", "Description", "Montant (GNF)"]]

    # Rows
    for d in Depense.objects.select_related("site", "categorie").all().order_by("-date"):
        data.append([
            d.id,
            d.date.strftime("%d/%m/%Y") if d.date else "",
            d.site.nom if d.site else "—",
            d.categorie.nom if d.categorie else "—",
            (d.description[:50] + "...") if d.description and len(d.description) > 50 else (d.description or ""),
            f"{d.montant:.2f}" if d.montant else "0.00"
        ])

    # Table style
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
    response["Content-Disposition"] = 'attachment; filename="depenses.pdf"'
    response.write(pdf)
    return response


