# Generated by Django 4.2.2 on 2023-06-14 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_delete_passwordrestore'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='discord_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='inst_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='telegram_url',
            field=models.URLField(blank=True),
        ),
    ]
