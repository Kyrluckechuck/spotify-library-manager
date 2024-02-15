# Generated by Django 5.0.2 on 2024-02-15 01:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library_manager", "0003_rename_settings_setting"),
    ]

    operations = [
        migrations.CreateModel(
            name="DownloadHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("url", models.CharField(max_length=2048)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(default=None)),
                (
                    "progress",
                    models.SmallIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(1000),
                        ],
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Setting",
        ),
    ]