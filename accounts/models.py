from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from project import settings


# Create your models here.


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_profile', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile/', blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.user)

    @receiver(post_save, sender=CustomUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
