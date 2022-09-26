from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.

class SiteUser(AbstractUser):
    date_joined = models.DateTimeField(default=timezone.now)
    avatar = models.ImageField()
