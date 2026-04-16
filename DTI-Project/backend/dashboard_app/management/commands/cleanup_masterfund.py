"""
Management command to clean up all master fund monitoring records
"""

from django.core.management.base import BaseCommand

from mater_fundmonitor_app.models import MasterFundMonitoring


class Command(BaseCommand):
    help = "Delete all Master Fund Monitoring records"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete all master fund monitoring records (default is to just report)",
        )

    def handle(self, *args, **options):
        count = MasterFundMonitoring.objects.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("No master fund monitoring records found.")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"Found {count} master fund monitoring record(s) to delete."
            )
        )

        if options["delete"]:
            MasterFundMonitoring.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {count} master fund monitoring record(s).")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Run with --delete flag to actually delete the records.\n"
                    "Example: python manage.py cleanup_masterfund --delete"
                )
            )
