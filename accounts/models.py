from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_employee:
            self.is_active = True
            self.is_staff = True
        elif self.is_admin:
            self.is_active = True
            self.is_staff = True
        super().save(*args, **kwargs)
