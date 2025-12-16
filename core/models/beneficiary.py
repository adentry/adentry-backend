from django.db import models
from django.conf import settings

class Beneficiary(models.Model):
    """
    Vendor / person / organization receiving payment.
    Keep as a separate entity for autocomplete and analytics.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="beneficiaries")
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50, blank=True, null=True)  # e.g., shop, person, service
    notes = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


