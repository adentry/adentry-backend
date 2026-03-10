from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model.
    Allows extending authentication fields later.
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    """
    Financial context profile.

    Examples:
    - Personal
    - Household
    - Business
    """

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="profiles"
    )

    name = models.CharField(max_length=100)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"{self.user.username} - {self.name}"
        

 
