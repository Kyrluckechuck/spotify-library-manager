from django.apps import AppConfig


class LibraryManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "library_manager"

    def ready(self) -> None:
        # Import checks to register them with Django
        from . import checks  # noqa: F401
