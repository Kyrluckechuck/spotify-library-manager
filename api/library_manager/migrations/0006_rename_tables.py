# Generated manually for table renaming - using proper Django operations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("library_manager", "0005_taskhistory_library_man_status_dfb074_idx_and_more"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="artist",
            table="artists",
        ),
        migrations.AlterModelTable(
            name="song",
            table="songs",
        ),
        migrations.AlterModelTable(
            name="contributingartist",
            table="contributing_artists",
        ),
        migrations.AlterModelTable(
            name="downloadhistory",
            table="download_history",
        ),
        migrations.AlterModelTable(
            name="taskhistory",
            table="task_history",
        ),
        migrations.AlterModelTable(
            name="album",
            table="albums",
        ),
        migrations.AlterModelTable(
            name="trackedplaylist",
            table="playlists",
        ),
    ]
