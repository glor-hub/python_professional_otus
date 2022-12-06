import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.
from hasker import settings


class Account(AbstractUser):
    date_joined = models.DateTimeField(default=timezone.now)
    avatar = models.ImageField(upload_to='accounts/avatars/', null=True)
    def get_avatar(self):
       if not self.avatar:
           return os.path.join(settings.STATIC_URL, "default_avatar.png")
       else:
           return os.path.join(settings.MEDIA_URL, self.avatar.name)
