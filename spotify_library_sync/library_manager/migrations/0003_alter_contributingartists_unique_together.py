# Generated by Django 5.0.2 on 2024-02-13 17:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("library_manager", "0002_contributingartists"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="contributingartists",
            unique_together={("song", "artist")},
        ),
    ]
