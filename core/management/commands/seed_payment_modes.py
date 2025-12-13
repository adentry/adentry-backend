from django.core.management.base import BaseCommand
from core.models.payment import PaymentMode

DEFAULT_MODES = [
    {
        "name": "Credit Card",
        "description": "Credit card with card_number, expiry_date, card_holder, issuing_bank",
        "fields": {
            "required": ["card_number", "expiry_date"],
            "optional": ["card_holder", "issuing_bank", "last_four"]
        }
    },
    {
        "name": "Debit Card",
        "description": "Debit card details",
        "fields": {
            "required": ["card_number", "expiry_date"],
            "optional": ["card_holder", "issuing_bank", "last_four"]
        }
    },
    {
        "name": "UPI",
        "description": "Unified Payments Interface (VPA)",
        "fields": {
            "required": ["upi_id"],
            "optional": ["linked_bank"]
        }
    },
    {
        "name": "Wallet",
        "description": "Digital wallet (Paytm, PhonePe, etc.)",
        "fields": {
            "required": ["wallet_id"],
            "optional": ["provider"]
        }
    },
    {
        "name": "Cash",
        "description": "Cash wallet or physical cash",
        "fields": {
            "required": [],
            "optional": ["location"]
        }
    }
]

class Command(BaseCommand):
    help = "Seed default PaymentMode values (Credit Card, Debit Card, UPI, Wallet, Cash)"

    def handle(self, *args, **options):
        created = 0
        for mode in DEFAULT_MODES:
            obj, created_flag = PaymentMode.objects.update_or_create(
                name=mode["name"],
                defaults={
                    "description": mode["description"],
                    "fields": mode["fields"],
                    "active": True,
                }
            )
            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created PaymentMode: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated PaymentMode: {obj.name}"))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))

