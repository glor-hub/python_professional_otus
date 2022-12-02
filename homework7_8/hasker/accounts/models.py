from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.

class Account(AbstractUser):
    date_joined = models.DateTimeField(default=timezone.now)
    avatar = models.ImageField(upload_to='accounts/', null=True)
