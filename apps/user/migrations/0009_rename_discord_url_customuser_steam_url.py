# Generated by Django 4.2.2 on 2023-06-14 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_customuser_discord_url_customuser_inst_url_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='discord_url',
            new_name='steam_url',
        ),
    ]
