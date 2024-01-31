# Generated by Django 5.0.1 on 2024-01-29 17:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0012_alter_comment_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="toPost",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="posts.post"
            ),
            preserve_default=False,
        ),
    ]
