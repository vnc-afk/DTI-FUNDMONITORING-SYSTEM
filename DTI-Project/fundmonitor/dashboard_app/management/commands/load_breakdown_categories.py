from django.core.management.base import BaseCommand
from dashboard_app.models import BreakdownCategory


class Command(BaseCommand):
    help = 'Load Breakdown Categories from hardcoded data'

    def handle(self, *args, **options):
        """Populate Breakdown Categories"""
        
        # Define the data structure
        data = [
            ('OO1', 'OO1 - Personnel Services', 'Salaries and wages for personnel'),
            ('OO2', 'OO2 - Maintenance & Other Operating Expenses', 'Operating and maintenance costs'),
            ('OO3', 'OO3 - Financial Expenses', 'Financial and interest expenses'),
            ('4.1A', '4.1A - Capital Outlay (Equipment)', 'Equipment purchases and upgrades'),
            ('4.1B', '4.1B - Capital Outlay (Infrastructure)', 'Infrastructure projects and construction'),
            ('4.2', '4.2 - Other Capital Outlays', 'Other capital expenditures'),
        ]
        
        created_count = 0
        
        # Create breakdown categories
        for order, (code, name, description) in enumerate(data, start=1):
            category, created = BreakdownCategory.objects.get_or_create(
                code=code.upper(),
                defaults={
                    'name': name,
                    'description': description,
                    'order': order,
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created Category: ({code}) {name}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'→ Category already exists: ({code}) {name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully loaded {created_count} categories!')
        )
