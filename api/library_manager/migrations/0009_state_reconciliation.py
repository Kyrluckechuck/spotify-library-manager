# State-only migration to reconcile Django's internal schema state with actual database
# This migration tells Django what the database schema currently looks like without making changes

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library_manager", "0008_increase_name_field_lengths"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Tell Django the indexes have proper names (they were renamed by the actual database)
                migrations.RenameIndex(
                    model_name="artist",
                    old_name="library_man_gid_46cefb_idx",
                    new_name="artists_gid_22ab5b_idx",
                ),
                migrations.RenameIndex(
                    model_name="artist",
                    old_name="library_man_tracked_5fa14f_idx",
                    new_name="artists_tracked_692424_idx",
                ),
                migrations.RenameIndex(
                    model_name="filepath",
                    old_name="library_man_path_idx",
                    new_name="file_paths_path_8426ae_idx",
                ),
                migrations.RenameIndex(
                    model_name="song",
                    old_name="library_man_gid_2ef37b_idx",
                    new_name="songs_gid_42b6cf_idx",
                ),
                migrations.RenameIndex(
                    model_name="taskhistory",
                    old_name="library_man_status_dfb074_idx",
                    new_name="task_histor_status_3c4579_idx",
                ),
                migrations.RenameIndex(
                    model_name="taskhistory",
                    old_name="library_man_type_f81fd9_idx",
                    new_name="task_histor_type_15005b_idx",
                ),
                migrations.RenameIndex(
                    model_name="taskhistory",
                    old_name="library_man_entity__2522da_idx",
                    new_name="task_histor_entity__cbec7e_idx",
                ),
                migrations.RenameIndex(
                    model_name="taskhistory",
                    old_name="library_man_complet_362457_idx",
                    new_name="task_histor_complet_01b5e9_idx",
                ),
                # Tell Django about the file_path field changes (already done in the database)
                migrations.RemoveField(
                    model_name="song",
                    name="file_path",
                ),
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
                # Tell Django about BigAutoField changes (already correct in database)
                migrations.AlterField(
                    model_name="artist",
                    name="id",
                    field=models.BigAutoField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="artist",
                    name="name",
                    field=models.CharField(max_length=500),
                ),
                migrations.AlterField(
                    model_name="filepath",
                    name="id",
                    field=models.BigAutoField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="song",
                    name="id",
                    field=models.BigAutoField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="song",
                    name="name",
                    field=models.CharField(max_length=500),
                ),
            ],
            database_operations=[
                # No database operations - the database is already in the correct state
            ],
        ),
    ]
