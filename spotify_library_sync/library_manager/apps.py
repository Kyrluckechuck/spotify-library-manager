from django.apps import AppConfig


class LibraryManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library_manager'

    def ready(self):
        import library_manager.signals  # noqa
