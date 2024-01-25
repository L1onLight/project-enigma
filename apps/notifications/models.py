from django.db import models

from apps.user.models import CustomUser


# Create your models here.
class PasswordRestore(models.Model):
    # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, unique=True)
    restoreCode = models.IntegerField()
    created_or_changed = models.DateTimeField(auto_now=True)
