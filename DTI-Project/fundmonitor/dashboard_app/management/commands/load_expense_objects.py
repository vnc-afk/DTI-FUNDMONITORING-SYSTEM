from django.core.management.base import BaseCommand
from dashboard_app.models import ExpenseObject

# Color palette for objects
COLORS = [
    '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
    '#1abc9c', '#34495e', '#d35400', '#8e44ad', '#c0392b',
    '#27ae60', '#2980b9', '#16a085', '#7f8c8d', '#f1c40f',
    '#e67e22', '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4',
]

EXPENSE_OBJECTS = [
    ('5020101000', 'Traveling Expenses - Local'),
    ('5020201000', 'Training Expenses'),
    ('5020301000', 'Office Supplies Expenses'),
    ('5020302000', 'Accountable Forms Expenses'),
    ('5020309000', 'Fuel, Oil and Lubricants Expenses'),
    ('5020401000', 'Water Expenses'),
    ('5020402000', 'Electricity Expenses'),
    ('5020501000', 'Postage and Courier Services'),
    ('50205020-01', 'Telephone Expenses - Mobile'),
    ('50205020-02', 'Telephone Expenses - Landline'),
    ('5020503000', 'Internet Subscription Expenses'),
    ('5020504000', 'Cable, Satellite, Telegraph and Radio Expenses'),
    ('5021101000', 'Legal Services'),
    ('5021199000', 'Other Professional Services'),
    ('5021202000', 'Janitorial Services'),
    ('5021299000', 'Other General Services'),
    ('50213040-01', 'R & M-Building'),
    ('50213050-02', 'R & M-Office Equipment'),
    ('50213050-03', 'R & M-ICT Equipment'),
    ('5021307000', 'R & M-Furniture and Fixtures'),
    ('50213080-02', 'R & M-Machinery and Equipment'),
    ('50213080-03', 'R & M-Transportation Equipment'),
    ('50213090-02', 'R & M-Leased Assets Improvements-Building'),
    ('50213090-99', 'R & M-Other Leased Assets Improvements'),
    ('50215010-01', 'Taxes, Duties and Licenses'),
    ('5021502000', 'Fidelity Bond Premiums'),
    ('5021503000', 'Insurance Expenses'),
    ('5029901000', 'Advertising Expenses'),
    ('5029902000', 'Printing and Publication Expenses'),
    ('5029903000', 'Representation Expenses'),
    ('5029904000', 'Transportation and Delivery Expenses'),
    ('50299050-01', 'Rents - Buildings and Structures'),
    ('50299050-04', 'Rents - Equipment'),
    ('5029907000', 'Subscription Expenses'),
    ('50299990-99', 'Other Maintenance and Operating Expenses'),
    ('10102020-16-05', 'Cash - LCCA (DBP Legazpi) APO-MOOE'),
    ('20201010-00-01-02', 'Due to BIR (VAT)'),
    ('20201010-00-01-04', 'Due to BIR (EWT)'),
    ('20201010-00-01-03', 'Due to BIR (PT)'),
]


class Command(BaseCommand):
    help = 'Load expense objects into the database'

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for idx, (code, name) in enumerate(EXPENSE_OBJECTS):
            color = COLORS[idx % len(COLORS)]
            
            obj, created = ExpenseObject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'color': color,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: ({code}) {name}')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⊘ Skipped: ({code}) {name} - Already exists')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Complete! Created {created_count} objects, skipped {skipped_count}'
            )
        )
