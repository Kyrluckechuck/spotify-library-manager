"""
Custom migrate command that extends Django's built-in migrate command.

This command automatically migrates data from SQLite to PostgreSQL when needed,
while maintaining all the standard Django migration functionality.
"""

import os
import sqlite3

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Run Django migrations and automatically migrate from SQLite if needed"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force migration even if PostgreSQL has data",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be migrated without actually doing it",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting Django migrations...")
        migrate_args = [arg for arg in args if not arg.startswith("--")]
        migrate_options = {
            k: v for k, v in options.items() if k not in ["force", "dry_run"]
        }

        # First, run normal Django migrations
        call_command("migrate", *migrate_args, **migrate_options)

        # Check if we need to migrate from SQLite
        if self._should_migrate_from_sqlite():
            self.stdout.write("SQLite database detected. Starting data migration...")
            self._migrate_from_sqlite()
        else:
            self.stdout.write("No SQLite migration needed.")

    def _should_migrate_from_sqlite(self):
        """Check if we should migrate from SQLite."""
        # Always check for migration - we'll handle individual table logic in the migration itself
        return True

    def _migrate_from_sqlite(self):  # pylint: disable=too-many-branches
        """Migrate data from SQLite to PostgreSQL."""
        sqlite_path = "/config/db/db.sqlite3"

        if not os.path.exists(sqlite_path):
            self.stdout.write("SQLite database not found. Skipping migration.")
            return

        try:
            # Connect to SQLite
            sqlite_conn = sqlite3.connect(sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row

            migrated_tables = 0
            total_rows = 0

            # Use a transaction to ensure all-or-nothing migration for the main data
            with transaction.atomic():
                # Check what needs to be migrated and migrate accordingly
                with connection.cursor() as pg_cursor:
                    # Check artists
                    pg_cursor.execute("SELECT COUNT(*) FROM artists")
                    artist_count = pg_cursor.fetchone()[0]

                    if artist_count == 0:
                        artist_rows = self._migrate_artists(sqlite_conn)
                        if artist_rows > 0:
                            migrated_tables += 1
                            total_rows += artist_rows
                            self.stdout.write(
                                f"  ✓ Migrated artists: {artist_rows} rows"
                            )
                    else:
                        self.stdout.write(
                            f"  - Skipped artists: already has {artist_count} rows"
                        )

                    # Check albums
                    pg_cursor.execute("SELECT COUNT(*) FROM albums")
                    album_count = pg_cursor.fetchone()[0]

                    if album_count == 0:
                        album_rows = self._migrate_albums(sqlite_conn)
                        if album_rows > 0:
                            migrated_tables += 1
                            total_rows += album_rows
                            self.stdout.write(f"  ✓ Migrated albums: {album_rows} rows")
                    else:
                        self.stdout.write(
                            f"  - Skipped albums: already has {album_count} rows"
                        )

                    # Check songs
                    pg_cursor.execute("SELECT COUNT(*) FROM songs")
                    song_count = pg_cursor.fetchone()[0]

                    if song_count == 0:
                        song_rows = self._migrate_songs(sqlite_conn)
                        if song_rows > 0:
                            migrated_tables += 1
                            total_rows += song_rows
                            self.stdout.write(f"  ✓ Migrated songs: {song_rows} rows")
                    else:
                        self.stdout.write(
                            f"  - Skipped songs: already has {song_count} rows"
                        )

                    # Check contributing artists
                    pg_cursor.execute("SELECT COUNT(*) FROM contributing_artists")
                    contrib_count = pg_cursor.fetchone()[0]

                    if contrib_count == 0:
                        contrib_rows = self._migrate_contributing_artists(sqlite_conn)
                        if contrib_rows > 0:
                            migrated_tables += 1
                            total_rows += contrib_rows
                            self.stdout.write(
                                f"  ✓ Migrated contributing_artists: {contrib_rows} rows"
                            )
                    else:
                        self.stdout.write(
                            f"  - Skipped contributing_artists: already has {contrib_count} rows"
                        )

                # Migrate other tables
                other_tables = [
                    ("library_manager_downloadhistory", "download_history"),
                    ("library_manager_taskhistory", "task_history"),
                    ("library_manager_trackedplaylist", "playlists"),
                ]

                for old_name, new_name in other_tables:
                    try:
                        with connection.cursor() as pg_cursor:
                            pg_cursor.execute(f"SELECT COUNT(*) FROM {new_name}")
                            existing_count = pg_cursor.fetchone()[0]

                            if existing_count == 0:
                                rows = self._migrate_generic_table(
                                    sqlite_conn, old_name, new_name
                                )
                                if rows > 0:
                                    migrated_tables += 1
                                    total_rows += rows
                                    self.stdout.write(
                                        f"  ✓ Migrated {new_name}: {rows} rows"
                                    )
                            else:
                                self.stdout.write(
                                    f"  - Skipped {new_name}: already has {existing_count} rows"
                                )
                    except Exception as e:
                        self.stdout.write(f"  - Skipped {new_name}: {e}")

            # Reset auto-increment sequences to continue from the highest IDs
            # Do this outside the main transaction to avoid rollback issues
            self._reset_sequences()

            sqlite_conn.close()

            if total_rows > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Migration completed! Migrated {total_rows} rows from "
                        f"{migrated_tables} tables."
                    )
                )
            else:
                self.stdout.write("No migration needed - all tables already have data.")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Migration failed: {e}"))
            raise

    def _migrate_artists(self, sqlite_conn):
        """Migrate artists with original IDs preserved."""
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM library_manager_artist")
        rows = cursor.fetchall()

        if not rows:
            return 0

        rows_inserted = 0
        with connection.cursor() as pg_cursor:
            for row in rows:
                try:
                    # Insert with original SQLite ID
                    insert_sql = """
                        INSERT INTO artists (id, name, gid, tracked, added_at, last_synced_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    pg_cursor.execute(
                        insert_sql,
                        (
                            row["id"],  # Preserve original ID
                            row["name"],
                            row["gid"],
                            (
                                bool(row["tracked"])
                                if row["tracked"] is not None
                                else False
                            ),
                            row["added_at"],
                            row["last_synced_at"],
                        ),
                    )
                    rows_inserted += 1
                except Exception as e:
                    self.stdout.write(
                        f"    Warning: Error inserting artist {row['gid']}: {e}"
                    )

        return rows_inserted

    def _migrate_albums(self, sqlite_conn):
        """Migrate albums with original IDs preserved."""
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM library_manager_album")
        rows = cursor.fetchall()

        if not rows:
            return 0

        rows_inserted = 0
        with connection.cursor() as pg_cursor:
            for row in rows:
                try:
                    # Insert with original SQLite ID
                    insert_sql = """
                        INSERT INTO albums (id, spotify_gid, artist_gid, spotify_uri, downloaded,
                                         total_tracks, wanted, name, failed_count, album_type, album_group)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    pg_cursor.execute(
                        insert_sql,
                        (
                            row["id"],  # Preserve original ID
                            row["spotify_gid"],
                            row["artist_gid"],
                            row["spotify_uri"],
                            (
                                bool(row["downloaded"])
                                if row["downloaded"] is not None
                                else False
                            ),
                            row["total_tracks"] or 0,
                            bool(row["wanted"]) if row["wanted"] is not None else True,
                            row["name"],
                            row["failed_count"] or 0,
                            row["album_type"],
                            row["album_group"],
                        ),
                    )
                    rows_inserted += 1
                except Exception as e:
                    self.stdout.write(
                        f"    Warning: Error inserting album {row['spotify_gid']}: {e}"
                    )

        return rows_inserted

    def _migrate_songs(self, sqlite_conn):
        """Migrate songs with original IDs preserved."""
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM library_manager_song")
        rows = cursor.fetchall()

        if not rows:
            return 0

        rows_inserted = 0
        with connection.cursor() as pg_cursor:
            for row in rows:
                try:
                    # Insert with original SQLite ID
                    insert_sql = """
                        INSERT INTO songs (id, name, gid, primary_artist_id, created_at,
                                         failed_count, bitrate, unavailable, file_path, downloaded)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # Truncate file_path if it's too long (PostgreSQL limit is varchar(100))
                    file_path = row["file_path"]
                    if file_path and len(file_path) > 100:
                        file_path = file_path[:97] + "..."
                        self.stdout.write(
                            f"    Warning: Truncated file_path for song {row['gid']} (was {len(row['file_path'])} chars)"
                        )

                    pg_cursor.execute(
                        insert_sql,
                        (
                            row["id"],  # Preserve original ID
                            row["name"],
                            row["gid"],
                            row["primary_artist_id"],  # Use original ID
                            row["created_at"],
                            row["failed_count"] or 0,
                            row["bitrate"] or 0,
                            (
                                bool(row["unavailable"])
                                if row["unavailable"] is not None
                                else False
                            ),
                            file_path,
                            (
                                bool(row["downloaded"])
                                if row["downloaded"] is not None
                                else False
                            ),
                        ),
                    )
                    rows_inserted += 1
                except Exception as e:
                    self.stdout.write(
                        f"    Warning: Error inserting song {row['gid']}: {e}"
                    )

        return rows_inserted

    def _migrate_contributing_artists(self, sqlite_conn):
        """Migrate contributing artists with original IDs preserved."""
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM library_manager_contributingartist")
        rows = cursor.fetchall()

        if not rows:
            return 0

        rows_inserted = 0
        with connection.cursor() as pg_cursor:
            for row in rows:
                try:
                    # Insert with original SQLite ID
                    insert_sql = """
                        INSERT INTO contributing_artists (id, song_id, artist_id)
                        VALUES (%s, %s, %s)
                    """

                    # Use original IDs directly
                    pg_cursor.execute(
                        insert_sql,
                        (
                            row["id"],  # Preserve original ID
                            row["song_id"],  # Use original ID
                            row["artist_id"],  # Use original ID
                        ),
                    )
                    rows_inserted += 1
                except Exception as e:
                    self.stdout.write(
                        f"    Warning: Error inserting contributing artist: {e}"
                    )

        return rows_inserted

    def _migrate_generic_table(self, sqlite_conn, old_table_name, new_table_name):
        """Migrate a generic table with original IDs preserved."""
        cursor = sqlite_conn.cursor()
        cursor.execute(f"SELECT * FROM {old_table_name}")
        rows = cursor.fetchall()

        if not rows:
            return 0

        # Get column names
        cursor.execute(f"PRAGMA table_info({old_table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        # Build INSERT statement
        placeholders = ", ".join(["%s"] * len(column_names))
        column_list = ", ".join(column_names)
        insert_sql = (
            f"INSERT INTO {new_table_name} ({column_list}) VALUES ({placeholders})"
        )

        rows_inserted = 0
        with connection.cursor() as pg_cursor:
            for row in rows:
                try:
                    # Convert boolean fields properly for PostgreSQL
                    converted_row = []
                    for i, value in enumerate(row):
                        if (
                            column_names[i] in ["enabled", "auto_track_artists"]
                            and value is not None
                        ):
                            # Convert integer to boolean for these specific fields
                            converted_row.append(bool(value))
                        else:
                            converted_row.append(value)

                    pg_cursor.execute(insert_sql, converted_row)
                    rows_inserted += 1
                except Exception as e:
                    self.stdout.write(
                        f"    Warning: Error inserting row in {new_table_name}: {e}"
                    )

        return rows_inserted

    def _reset_sequences(self):
        """Reset auto-increment sequences to continue from the highest IDs."""
        try:
            with connection.cursor() as pg_cursor:
                # Reset identity columns for all tables that have auto-increment IDs
                tables_and_identity_columns = [
                    ("artists", "id"),
                    ("albums", "id"),
                    ("songs", "id"),
                    ("contributing_artists", "id"),
                    ("playlists", "id"),
                    ("download_history", "id"),
                    ("task_history", "id"),
                ]

                for table_name, id_column in tables_and_identity_columns:
                    try:
                        # Get the maximum ID from the table
                        pg_cursor.execute(
                            f"SELECT COALESCE(MAX({id_column}), 0) FROM {table_name}"
                        )
                        max_id = pg_cursor.fetchone()[0]

                        if max_id > 0:
                            # Reset the identity column to continue from max_id + 1
                            pg_cursor.execute(
                                f"ALTER TABLE {table_name} ALTER COLUMN {id_column} RESTART WITH {max_id + 1}"
                            )
                            self.stdout.write(
                                f"    ✓ Reset identity column {table_name}.{id_column} to {max_id + 1}"
                            )
                    except Exception as e:
                        self.stdout.write(
                            f"    Warning: Could not reset identity column {table_name}.{id_column}: {e}"
                        )

        except Exception as e:
            self.stdout.write(f"    Warning: Error resetting identity columns: {e}")
