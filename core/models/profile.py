from django.db import models
from django.conf import settings


class Profile(models.Model):
    '''
    Classifies spending context.
    '''

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profiles")
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True, null=True)

    is_default = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["is_default", "name"]


    def __str__(self):
        return f"{self.name}"


