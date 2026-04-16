from django.core.management.base import BaseCommand

from data_management_app.models import PurchaseType

PURCHASE_TYPES = [
    "VGoods",
    "VService",
    "VRental",
    "VHonorarium",
    "VJob Order",
    "VContract",
    "NVGoods",
    "NVService",
    "NVRental",
    "NVHonorarium",
    "NVJob Order",
    "NVContract",
    "Premium",
]


class Command(BaseCommand):
    help = "Load purchase types into the database"

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for name in PURCHASE_TYPES:
            purchase_type, created = PurchaseType.objects.get_or_create(
                name=name,
                defaults={
                    "is_active": True,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created purchase type: {name}")
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"⊘ Purchase type already exists: {name}")
                )
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Successfully loaded purchase types.\n"
                f"  Created: {created_count}\n"
                f"  Skipped: {skipped_count}\n"
                f"  Total: {created_count + skipped_count}"
            )
        )
