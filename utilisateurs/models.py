from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    ROLES = (
        ('admin', 'Administrateur'),
        ('gestionnaire', 'Gestionnaire'),
        ('employe', 'Employé'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='employe')

    def __str__(self):
        return self.get_username()
