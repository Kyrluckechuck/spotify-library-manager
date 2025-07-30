"""
Django model type definitions for better type safety.
These are type aliases that represent the actual Django models.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Import Django models only for type checking
    from library_manager.models import Album as DjangoAlbum
    from library_manager.models import Artist as DjangoArtist
    from library_manager.models import Song as DjangoSong
    from library_manager.models import TaskHistory as DjangoTaskHistory
    from library_manager.models import TrackedPlaylist as DjangoTrackedPlaylist
else:
    # Runtime aliases to avoid circular imports
    DjangoArtist = Any
    DjangoAlbum = Any
    DjangoSong = Any
    DjangoTrackedPlaylist = Any
    DjangoTaskHistory = Any

# Re-export for convenience
__all__ = [
    "DjangoArtist",
    "DjangoAlbum",
    "DjangoSong",
    "DjangoTrackedPlaylist",
    "DjangoTaskHistory",
]
