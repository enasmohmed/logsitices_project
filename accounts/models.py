from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_admin:
            self.is_superuser = True
        super().save(*args, **kwargs)
