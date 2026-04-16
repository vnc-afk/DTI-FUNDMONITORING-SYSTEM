from django.core.management.base import BaseCommand

from data_management_app.models import District, NegosyoCenter


class Command(BaseCommand):
    help = "Load Negosyo Centers and Districts"

    def handle(self, *args, **options):
        """Populate Districts and Negosyo Centers"""

        # Define the data structure
        data = {
            "District 1": [
                ("sto_domingo", "Sto. Domingo"),
                ("bacacay", "Bacacay"),
                ("malilipot", "Malilipot"),
                ("tabaco_city", "Tabaco City"),
                ("tiwi", "Tiwi"),
            ],
            "District 2": [
                ("apo", "APO"),
                ("sedcen", "SEDCEN"),
                ("camalig", "Camalig"),
                ("daraga", "Daraga"),
                ("manito", "Manito"),
            ],
            "District 3": [
                ("guinobatan", "Guinobatan"),
                ("ligao_city", "Ligao City"),
                ("oas", "Oas"),
                ("polangui", "Polangui"),
                ("piodoran", "Piodoran"),
            ],
        }

        created_count = 0

        # Create districts and negosyo centers
        for order, (district_name, centers) in enumerate(data.items(), start=1):
            # Create or get district
            district, district_created = District.objects.get_or_create(
                name=district_name,
                defaults={
                    "order": order,
                    "is_active": True,
                },
            )

            if district_created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created District: {district_name}")
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"→ District already exists: {district_name}")
                )

            # Create negosyo centers
            for code, name in centers:
                nc, nc_created = NegosyoCenter.objects.get_or_create(
                    code=code.lower(),
                    defaults={
                        "district": district,
                        "name": name,
                        "is_active": True,
                    },
                )

                if nc_created:
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Created NC: {name}"))
                    created_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  → NC already exists: {name}")
                    )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Successfully loaded {created_count} items!")
        )
