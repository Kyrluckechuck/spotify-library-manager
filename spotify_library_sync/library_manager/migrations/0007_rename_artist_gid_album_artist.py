# Generated by Django 5.0.2 on 2024-02-16 16:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("library_manager", "0006_album"),
    ]

    operations = [
        migrations.RenameField(
            model_name="album",
            old_name="artist_gid",
            new_name="artist",
        ),
    ]