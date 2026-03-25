"""
Management command to clean up all supplier records
"""
from django.core.management.base import BaseCommand
from data_management_app.models import Supplier


class Command(BaseCommand):
    help = 'Delete all Supplier records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all supplier records (default is to just report)',
        )

    def handle(self, *args, **options):
        count = Supplier.objects.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No supplier records found.'))
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {count} supplier record(s) to delete.')
        )
        
        if options['delete']:
            Supplier.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} supplier record(s).')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Run with --delete flag to actually delete the records.\n'
                    'Example: python manage.py cleanup_supplier --delete'
                )
            )
