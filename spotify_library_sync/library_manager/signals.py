from django.db.models.signals import post_save
from django.dispatch import receiver

from library_manager.models import Artist
from library_manager import tasks

@receiver(post_save, sender=Artist)
def artist_save(sender, instance: Artist, created: bool, **kwargs):
    # If it's a new artist, let's fetch all their albums
    if created:
        tasks.fetch_all_albums_for_artist(instance.id)
