# Generated by Django 5.0.1 on 2024-01-29 21:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0013_alter_comment_topost"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="comments",
        ),
    ]