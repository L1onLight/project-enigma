# Generated by Django 4.2.2 on 2023-06-11 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(default='avatar.svg', null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bio',
            field=models.TextField(default='', null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='full_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
