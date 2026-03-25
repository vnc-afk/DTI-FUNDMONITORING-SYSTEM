"""
Management command to clean up invalid staff records
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from data_management_app.models import Staff


class Command(BaseCommand):
    help = 'Clean up Staff records with null or empty first_name and last_name'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete invalid records (default is to just report)',
        )

    def handle(self, *args, **options):
        # Find invalid records
        invalid_records = Staff.objects.filter(
            Q(first_name__isnull=True) | 
            Q(last_name__isnull=True) |
            Q(first_name='') |
            Q(last_name='')
        )
        
        count = invalid_records.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No invalid staff records found.'))
            return
        
        self.stdout.write(
            self.style.WARNING(f'Found {count} invalid staff record(s):')
        )
        
        for staff in invalid_records:
            self.stdout.write(
                f"  - ID {staff.id}: first_name='{staff.first_name}', last_name='{staff.last_name}'"
            )
        
        if options['delete']:
            invalid_records.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted {count} invalid staff record(s).')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Run with --delete flag to remove these records.'
                )
            )
