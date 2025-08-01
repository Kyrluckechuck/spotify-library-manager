from django.contrib import admin

from .models import (
    Album,
    Artist,
    ContributingArtist,
    DownloadHistory,
    Song,
    TaskHistory,
    TrackedPlaylist,
)


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "gid",
        "tracked",
        "number_songs",
        "added_at",
        "last_synced_at",
    )
    list_filter = ("tracked", "added_at", "last_synced_at")
    search_fields = ("name", "gid")
    readonly_fields = ("number_songs", "albums")
    ordering = ("name",)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "gid",
        "primary_artist",
        "downloaded",
        "unavailable",
        "failed_count",
        "created_at",
    )
    list_filter = ("downloaded", "unavailable", "created_at", "primary_artist")
    search_fields = ("name", "gid", "primary_artist__name")
    readonly_fields = ("spotify_uri", "contributing_artists")
    ordering = ("name",)


@admin.register(ContributingArtist)
class ContributingArtistAdmin(admin.ModelAdmin):
    list_display = ("song", "artist")
    list_filter = ("artist",)
    search_fields = ("song__name", "artist__name")
    ordering = ("song__name", "artist__name")


@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ("url", "progress_percent", "added_at", "completed_at")
    list_filter = ("added_at", "completed_at")
    search_fields = ("url",)
    readonly_fields = ("progress_percent",)
    ordering = ("-added_at",)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "artist",
        "album_type",
        "album_group",
        "downloaded",
        "wanted",
        "total_tracks",
        "failed_count",
    )
    list_filter = ("downloaded", "wanted", "album_type", "album_group", "artist")
    search_fields = ("name", "spotify_gid", "artist__name")
    readonly_fields = ("desired_album_type",)
    ordering = ("name",)


@admin.register(TrackedPlaylist)
class TrackedPlaylistAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "enabled", "auto_track_artists", "last_synced_at")
    list_filter = ("enabled", "auto_track_artists", "last_synced_at")
    search_fields = ("name", "url")
    ordering = ("name",)


@admin.register(TaskHistory)
class TaskHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "task_id",
        "type",
        "entity_type",
        "entity_id",
        "status",
        "progress_percentage",
        "started_at",
        "completed_at",
    )
    list_filter = ("type", "entity_type", "status", "started_at", "completed_at")
    search_fields = ("task_id", "entity_id", "error_message")
    readonly_fields = ("task_id", "started_at", "last_heartbeat")
    ordering = ("-started_at",)

    fieldsets = (
        (
            "Task Information",
            {"fields": ("task_id", "type", "entity_type", "entity_id", "status")},
        ),
        (
            "Timing",
            {
                "fields": (
                    "started_at",
                    "completed_at",
                    "duration_seconds",
                    "timeout_minutes",
                    "last_heartbeat",
                )
            },
        ),
        ("Progress", {"fields": ("progress_percentage",)}),
        ("Error Information", {"fields": ("error_message",), "classes": ("collapse",)}),
        ("Logs", {"fields": ("log_messages",), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
