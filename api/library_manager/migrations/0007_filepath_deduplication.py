# Generated migration for file path deduplication

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
        # Using RunSQL to ensure correct table name
        migrations.RunSQL(
            """
            ALTER TABLE songs
            ADD COLUMN file_path_ref_id INTEGER;

            ALTER TABLE songs
            ADD CONSTRAINT songs_file_path_ref_id_fk
            FOREIGN KEY (file_path_ref_id)
            REFERENCES file_paths(id)
            ON DELETE SET NULL;
            """,
            reverse_sql="""
            ALTER TABLE songs DROP CONSTRAINT IF EXISTS songs_file_path_ref_id_fk;
            ALTER TABLE songs DROP COLUMN IF EXISTS file_path_ref_id;
            """,
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
        # Using RunSQL to ensure correct table name
        migrations.RunSQL(
            """
            ALTER TABLE songs DROP COLUMN IF EXISTS file_path;
            """,
            reverse_sql="""
            ALTER TABLE songs ADD COLUMN file_path TEXT;
            """,
        ),
    ]
