"""
WSGI config for pme_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""
import os
import sys

# ✅ chemin du projet
project_path = '/home/boubaa/gestiondmiii'
if project_path not in sys.path:
    sys.path.append(project_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'gestiondmiii.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

