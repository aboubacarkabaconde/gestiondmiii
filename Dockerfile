FROM python:3.12-slim

# Empêche la création de fichiers .pyc et permet un flush des logs direct
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système nécessaires pour Pillow, psycopg2 et ReportLab
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie et installe les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code du projet
COPY . .

# Collecte les fichiers statiques
RUN python manage.py collectstatic --noinput

# Commande de lancement
CMD ["gunicorn", "pme_manager.wsgi:application", "--bind", "0.0.0.0:8000"]
