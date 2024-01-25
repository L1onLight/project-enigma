from django.contrib import admin
from .models import PasswordRestore


# Register your models here.
class PasswordDate(admin.ModelAdmin):
    readonly_fields = ('created_or_changed',)


admin.site.register(PasswordRestore, PasswordDate)
