from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # keep it simple now; extend later if needed
    email = models.EmailField(blank=True, null=True)