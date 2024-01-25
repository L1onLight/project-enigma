from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    # username = None
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        max_length=50, unique=True, null=True, blank=True)
    bio = models.TextField(null=True, default='', blank=True)
    avatar = models.ImageField(null=True, default="avatar.svg")
    inst_url = models.URLField(blank=True)
    steam_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.username:
            return self.username

        return self.email

    def un(self):
        if self.username:
            return self.username
        else:
            return self.email.split('@')[0]
