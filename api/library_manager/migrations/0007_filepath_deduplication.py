# Generated migration for file path deduplication

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library_manager", "0006_rename_tables"),
    ]

    operations = [
        # Create FilePath model
        migrations.CreateModel(
            name="FilePath",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("path", models.TextField(unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "file_paths",
            },
        ),
        # Add index on path field
        migrations.AddIndex(
            model_name="filepath",
            index=models.Index(fields=["path"], name="library_man_path_idx"),
        ),
        # Add new foreign key field (nullable initially)
        migrations.AddField(
            model_name="song",
            name="file_path_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="songs",
                to="library_manager.filepath",
            ),
        ),
        # Data migration to populate FilePath objects and update references
        migrations.RunSQL(
            """
            -- Insert unique file paths
            INSERT INTO file_paths (path, created_at)
            SELECT DISTINCT file_path, NOW()
            FROM songs
            WHERE file_path IS NOT NULL AND file_path != ''
            ON CONFLICT (path) DO NOTHING;

            -- Update song references
            UPDATE songs
            SET file_path_ref_id = fp.id
            FROM file_paths fp
            WHERE songs.file_path = fp.path;
            """,
            reverse_sql="""
            -- Restore file_path from references
            UPDATE songs
            SET file_path = fp.path
            FROM file_paths fp
            WHERE songs.file_path_ref_id = fp.id;

            -- Clear references
            UPDATE songs SET file_path_ref_id = NULL;

            -- Remove FilePath data
            DELETE FROM file_paths;
            """,
        ),
        # Remove old file_path field
        migrations.RemoveField(
            model_name="song",
            name="file_path",
        ),
    ]
