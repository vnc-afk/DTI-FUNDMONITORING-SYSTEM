"""Management command to archive records by year"""

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from dashboard_app.utils.archive_utils import (
    archive_by_year,
    get_archive_stats,
    unarchive_by_year,
)


class Command(BaseCommand):
    help = "Archive or manage archived records for a specific year"

    def add_arguments(self, parser):
        parser.add_argument("year", type=int, help="Year to archive (e.g., 2026)")
        parser.add_argument(
            "--action",
            type=str,
            choices=["archive", "unarchive", "stats"],
            default="archive",
            help="Action to perform: archive, unarchive, or stats",
        )
        parser.add_argument(
            "--reason", type=str, default="", help="Reason for archiving"
        )
        parser.add_argument(
            "--user", type=str, help="Username to record as archiving user"
        )

    def handle(self, *args, **options):
        year = options["year"]
        action = options["action"]
        reason = options.get("reason", "")
        username = options.get("user")

        # Validate year
        if year < 1900 or year > datetime.now().year + 10:
            raise CommandError(f"Invalid year: {year}. Please provide a valid year.")

        # Get user if specified
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User "{username}" not found.')

        if action == "archive":
            self.stdout.write(f"Archiving records for year {year}...")

            try:
                result = archive_by_year(year, user=user, reason=reason)

                self.stdout.write(
                    self.style.SUCCESS("\n✓ Archive completed successfully!\n")
                )
                self.stdout.write(
                    f'  Fund Monitoring Records Archived: {result["fund_monitoring_count"]}'
                )
                self.stdout.write(
                    f'  Bank Statement Records Archived: {result["bank_statement_count"]}'
                )
                self.stdout.write(
                    f'  Total Records Archived: {result["total_archived"]}'
                )
                self.stdout.write(f'  Archived By: {result["archived_by"]}')
                self.stdout.write(
                    f'  Time: {result["archived_at"].strftime("%Y-%m-%d %H:%M:%S")}'
                )

                if reason:
                    self.stdout.write(f"  Reason: {reason}")

            except Exception as e:
                raise CommandError(f"Error archiving records: {str(e)}")

        elif action == "unarchive":
            self.stdout.write(f"Unarchiving records for year {year}...")

            if not self._confirm_action("unarchive"):
                self.stdout.write(self.style.WARNING("Unarchive cancelled."))
                return

            try:
                result = unarchive_by_year(year)

                self.stdout.write(
                    self.style.SUCCESS("\n✓ Unarchive completed successfully!\n")
                )
                self.stdout.write(
                    f'  Fund Monitoring Records Unarchived: {result["fund_monitoring_count"]}'
                )
                self.stdout.write(
                    f'  Bank Statement Records Unarchived: {result["bank_statement_count"]}'
                )
                self.stdout.write(
                    f'  Total Records Unarchived: {result["total_unarchived"]}'
                )

            except Exception as e:
                raise CommandError(f"Error unarchiving records: {str(e)}")

        elif action == "stats":
            self.stdout.write("Archive statistics:\n")

            try:
                stats = get_archive_stats(year)

                self.stdout.write("Overall Statistics:")
                self.stdout.write(
                    f'  Active Fund Monitoring Records: {stats["active_fund_monitoring"]}'
                )
                self.stdout.write(
                    f'  Archived Fund Monitoring Records: {stats["archived_fund_monitoring"]}'
                )
                self.stdout.write(
                    f'  Active Bank Statements: {stats["active_bank_statements"]}'
                )
                self.stdout.write(
                    f'  Archived Bank Statements: {stats["archived_bank_statements"]}'
                )

                if "fund_monitoring_year" in stats:
                    self.stdout.write(f"\nYear {year} Statistics:")
                    self.stdout.write(
                        f'  Active Fund Monitoring: {stats["fund_monitoring_year"]["active"]}'
                    )
                    self.stdout.write(
                        f'  Archived Fund Monitoring: {stats["fund_monitoring_year"]["archived"]}'
                    )
                    self.stdout.write(
                        f'  Active Bank Statements: {stats["bank_statements_year"]["active"]}'
                    )
                    self.stdout.write(
                        f'  Archived Bank Statements: {stats["bank_statements_year"]["archived"]}'
                    )

            except Exception as e:
                raise CommandError(f"Error retrieving statistics: {str(e)}")

    def _confirm_action(self, action):
        """Confirm potentially destructive action"""
        response = input(f'Are you sure you want to {action}? Type "yes" to confirm: ')
        return response.lower() == "yes"
