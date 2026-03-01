from django.core.management.base import BaseCommand
from dashboard_app.models import ExpenseCategory

# Color palette for categories
COLORS = [
    '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
    '#1abc9c', '#34495e', '#d35400', '#8e44ad', '#c0392b',
    '#27ae60', '#2980b9', '#16a085', '#7f8c8d', '#f1c40f',
    '#e67e22', '#ff6b6b', '#4ecdc4', '#45b7d1',
]

EXPENSE_CATEGORIES = [
    'Catering',
    'Communication Expense',
    'Electricity',
    'Gasoline',
    'Government Accounts',
    'Honorarium',
    'Internet',
    'Job Order',
    'Livelihood Kits',
    'Meals',
    'Office Supplies',
    'Petty Cash',
    'Rental',
    'Repair and Maintenance',
    'TEV',
    'Training Materials',
    'Transportation & Delivery',
    'Water',
]


class Command(BaseCommand):
    help = 'Load expense categories into the database'

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for idx, name in enumerate(EXPENSE_CATEGORIES):
            color = COLORS[idx % len(COLORS)]
            
            category, created = ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={
                    'color': color,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {name}')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⊘ Skipped: {name} - Already exists')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Complete! Created {created_count} categories, skipped {skipped_count}'
            )
        )
