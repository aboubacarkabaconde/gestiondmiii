import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# ==========================
# 1. BASE & VARIABLES ENV
# ==========================
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger le fichier .env (utile en local et dans Docker)
load_dotenv(BASE_DIR / ".env")

# ==========================
# 2. PARAMÈTRES DE BASE
# ==========================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-me")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost 127.0.0.1 [::1]").split(" ")

# ==========================
# 3. APPLICATIONS
# ==========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Tes apps
    "factures",
    "depenses",
    "produits",
    "sites",
    "production", 

    # Librairies tierces
    "crispy_forms",
    "crispy_bootstrap5",
    "rest_framework",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ==========================
# 4. MIDDLEWARE
# ==========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # sert les fichiers statiques
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pme_manager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

LOGIN_TEMPLATE = "accounts/login.html"

WSGI_APPLICATION = "pme_manager.wsgi.application"

# ==========================
# 5. BASE DE DONNÉES (AUTO-CONFIGURATION)
# ==========================
# Si DATABASE_URL est présent dans .env → utilise PostgreSQL automatiquement
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback : SQLite pour développement local
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ==========================
# 6. VALIDATION DES MOTS DE PASSE
# ==========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==========================
# 7. INTERNATIONALISATION
# ==========================
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Conakry"
USE_I18N = True
USE_TZ = True



LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ==========================
# 8. FICHIERS STATIQUES
# ==========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ==========================
# 9. AUTRES PARAMÈTRES
# ==========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



# Permet de régler le niveau via l'env: DEBUG/INFO/WARNING/ERROR
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # Formatters lisibles en console
    "formatters": {
        "simple": {
            "format": "[{levelname}] {asctime} {name}: {message}",
            "style": "{",
        },
        # Plus compact pour prod
        "concise": {
            "format": "{levelname} {name}: {message}",
            "style": "{",
        },
    },

    # Handlers: on envoie tout en console (stdout)
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },

    # Loggers
    "loggers": {
        # Logger racine: tout Django + ton code
        "": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },

        # Django internals (tu peux remonter le niveau si trop verbeux)
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },

        # Requêtes Django (erreurs 500 etc.)
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },

        # Migrations, DB backend
        "django.db.backends": {
            "handlers": ["console"],
            "level": os.getenv("DB_LOG_LEVEL", "WARNING").upper(),
            "propagate": False,
        },

        # DRF (si tu veux affiner)
        "rest_framework": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

