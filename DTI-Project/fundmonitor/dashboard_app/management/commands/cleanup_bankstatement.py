"""
Management command to clean up all bank statement records
"""
from django.core.management.base import BaseCommand
from bank_statement_app.models import BankStatement


class Command(BaseCommand):
    help = 'Delete all Bank Statement records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all bank statement records (default is to just report)',
        )

    def handle(self, *args, **options):
        count = BankStatement.objects.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No bank statement records found.'))
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {count} bank statement record(s) to delete.')
        )
        
        if options['delete']:
            BankStatement.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} bank statement record(s).')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Run with --delete flag to actually delete the records.\n'
                    'Example: python manage.py cleanup_bankstatement --delete'
                )
            )
