# Generated by Django 5.0.2 on 2024-02-13 19:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("library_manager", "0004_alter_artist_uuid_alter_song_uuid"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ContributingArtists",
            new_name="ContributingArtist",
        ),
    ]
