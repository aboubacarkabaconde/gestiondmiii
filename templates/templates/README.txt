# Pack complet de templates (intégrés) — Gestion D.M.I

Déposez ce dossier `templates/` à la racine de votre projet Django.

## Inclus
- `base.html` avec **thème sombre** (toggle) et **messages** factorisés
- Partials `templates/_includes/...` pour **filtres**, **graphiques Chart.js** et **cartes KPI**
- Pages modules (dépenses, factures, production, sites, employés, inventaire, recherche, stats) mises à jour pour utiliser les partials

## Dépendances
- Bootstrap 5, Bootstrap Icons (CDN)
- Chart.js (injecté via le partial `_includes/_chartjs_cdn.html` sur les pages qui ont des graphes)
- crispy-forms + crispy_bootstrap5 pour les formulaires

## Namespaces attendus
- `depenses`, `factures`, `production`, `sites`, `employes`, `inventaire`, `search`
