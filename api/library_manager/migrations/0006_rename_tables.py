# Generated manually for table renaming

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("library_manager", "0005_taskhistory_library_man_status_dfb074_idx_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL: rename tables
            sql="""
            ALTER TABLE library_manager_artist RENAME TO artists;
            ALTER TABLE library_manager_song RENAME TO songs;
            ALTER TABLE library_manager_contributingartist RENAME TO contributing_artists;
            ALTER TABLE library_manager_downloadhistory RENAME TO download_history;
            ALTER TABLE library_manager_taskhistory RENAME TO task_history;
            ALTER TABLE library_manager_album RENAME TO albums;
            ALTER TABLE library_manager_trackedplaylist RENAME TO playlists;
            """,
            # Reverse SQL: rename back
            reverse_sql="""
            ALTER TABLE artists RENAME TO library_manager_artist;
            ALTER TABLE songs RENAME TO library_manager_song;
            ALTER TABLE contributing_artists RENAME TO library_manager_contributingartist;
            ALTER TABLE download_history RENAME TO library_manager_downloadhistory;
            ALTER TABLE task_history RENAME TO library_manager_taskhistory;
            ALTER TABLE albums RENAME TO library_manager_album;
            ALTER TABLE playlists RENAME TO library_manager_trackedplaylist;
            """,
        ),
    ]
