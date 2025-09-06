from django.db.models.signals import post_save
from django.dispatch import receiver

from api.library_manager import tasks
from library_manager.models import Artist


@receiver(post_save, sender=Artist)
def artist_save(sender, instance: Artist, created: bool, **kwargs) -> None:
    # If it's a new artist, let's fetch all their albums
    if created:
        tasks.fetch_all_albums_for_artist.delay(instance.id)
