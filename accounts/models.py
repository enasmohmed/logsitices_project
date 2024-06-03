from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # إذا كان المستخدم مُسجل كمسؤول
        if self.is_admin:
            # جعله فعالًا
            self.is_active = True
            # جعله موظفًا
            self.is_staff = True
            # جعله مشرفًا
            self.is_superuser = True
        super().save(*args, **kwargs)
