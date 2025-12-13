import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class PaymentMode(models.Model):
    """
    Master template that defines what fields are required/optional
    for each type of payment method.
    Example:
    - Credit Card → card_number, expiry_date, card_holder, bank_name
    - Wallet → wallet_id, provider
    - Cash → no fields
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    # JSON structure:
    # {
    #   "required": ["card_number", "expiry_date"],
    #   "optional": ["bank_name", "card_holder"]
    # }
    fields = models.JSONField(default=dict)

    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Payment Mode"
        verbose_name_plural = "Payment Modes"

    def __str__(self):
        return self.name


class PaymentAccount(models.Model):
    """
    User's actual instrument linked to a PaymentMode.
    Example:
    - "HDFC Credit Card"
    - "Paytm Wallet"
    - "My UPI ID"
    - "Cash - Home Drawer"
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # User-friendly name: "HDFC Credit Card", "PhonePe", "Cash Wallet"
    name = models.CharField(max_length=150)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_accounts")
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.PROTECT)

    # Stores actual values filled for dynamic fields
    # Example:
    # {
    #   "card_number": "XXXX-1234",
    #   "expiry_date": "04/30",
    #   "bank_name": "HDFC"
    # }
    data = models.JSONField(default=dict, blank=True)

    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Payment Account"
        verbose_name_plural = "Payment Accounts"

    def clean(self):
        """
        Validates dynamic fields according to PaymentMode.fields
        """
        required_fields = self.payment_mode.fields.get("required", [])
        optional_fields = self.payment_mode.fields.get("optional", [])

        # Check all required fields exist
        for field in required_fields:
            if field not in self.data or not self.data.get(field):
                raise ValidationError(
                    { "data": f"Field '{field}' is required for {self.payment_mode.name}." }
                )

        # Check no unknown keys are added
        allowed_fields = set(required_fields + optional_fields)
        for key in self.data.keys():
            if key not in allowed_fields:
                raise ValidationError(
                    { "data": f"Field '{key}' is not allowed for payment mode {self.payment_mode.name}." }
                )

    def __str__(self):
        """
        Returns smart readable name like:
        - "Aditya Jain - HDFC Credit Card (XXXX1234)"
        - "Aditya Jain - Paytm Wallet (ID: rahul@paytm)"
        - "Aditya Jain - Cash"
        """
        display = self.name

        mode_fields = self.payment_mode.fields.get("required", []) + \
                      self.payment_mode.fields.get("optional", [])

        # Pick a good identifier if available
        identifier = None
        for key in ["card_number", "wallet_id", "upi_id", "account_number"]:
            if key in self.data:
                identifier = self.data[key]
                break

        if identifier:
            display = f"{self.user} - {self.name} ({identifier})"

        return display

