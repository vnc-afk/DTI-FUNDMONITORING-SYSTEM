from django.core.management.base import BaseCommand
from data_management_app.models import Division


class Command(BaseCommand):
    help = 'Add predefined divisions to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--divisions',
            type=str,
            default='BDD,CPD,FAD',
            help='Comma-separated list of division names (default: BDD,CPD,FAD)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all divisions before adding new ones'
        )

    def handle(self, *args, **options):
        divisions_input = options['divisions']
        divisions_list = [d.strip() for d in divisions_input.split(',')]
        
        # Clear existing divisions if --clear flag is used
        if options['clear']:
            Division.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all divisions'))
        
        # Add divisions
        created_count = 0
        for division_name in divisions_list:
            if not division_name:
                continue
            
            division, created = Division.objects.get_or_create(
                name=division_name,
                defaults={
                    'is_active': True,
                    'description': f'{division_name} Division'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created division: {division_name}'))
                created_count += 1
            else:
                self.stdout.write(f'→ Division already exists: {division_name}')
        
        self.stdout.write(self.style.SUCCESS(f'\n{created_count} divisions added successfully!'))
