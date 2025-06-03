from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Ensure project directories (templates, static, media) exist."  # noqa: A003

    def handle(self, *args, **options):
        for path in (settings.TEMPLATES_DIR, getattr(settings, "STATIC_ROOT", None)):
            if path:
                path.mkdir(parents=True, exist_ok=True)
                self.stdout.write(
                    self.style.SUCCESS(f"Ensured directory exists: {path}")
                )
