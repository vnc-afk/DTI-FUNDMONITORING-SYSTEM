from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from dashboard_app.models import SeedRun


class Command(BaseCommand):
    help = "Run initial reference data seed only once per database"

    SEED_KEY = "initial_reference_data_v1"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force seed even if already executed",
        )

    def handle(self, *args, **options):
        force = options["force"]

        with transaction.atomic():
            already_seeded = (
                SeedRun.objects.select_for_update().filter(key=self.SEED_KEY).exists()
            )

            if already_seeded and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f"Seed already executed for key: {self.SEED_KEY}. Skipping."
                    )
                )
                return

            call_command("load_divisions")
            call_command("load_breakdown_categories")
            call_command("load_negosyo_centers")
            call_command("load_purchase_types")
            call_command("load_expense_categories")
            call_command("load_expense_objects")

            SeedRun.objects.update_or_create(key=self.SEED_KEY)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Initial seed completed for key: {self.SEED_KEY}"
                )
            )
