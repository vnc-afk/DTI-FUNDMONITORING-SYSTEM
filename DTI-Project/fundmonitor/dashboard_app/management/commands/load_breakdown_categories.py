from django.core.management.base import BaseCommand
from data_management_app.models import BreakdownCategory


class Command(BaseCommand):
    help = 'Load Breakdown Categories from hardcoded data'

    def handle(self, *args, **options):
        """Populate Breakdown Categories"""
        
        # Define the data structure
        data = [
            'OO1',
            'OO2',
            'OO3',
            '4.1A',
            '4.1B',
            '4.2',
        ]
        
        created_count = 0
        
        # Create breakdown categories
        for order, code in enumerate(data, start=1):
            category, created = BreakdownCategory.objects.get_or_create(
                code=code.upper(),
                defaults={
                    'order': order,
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created Category: {code}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Category already exists: {code}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully loaded {created_count} categories!')
        )
