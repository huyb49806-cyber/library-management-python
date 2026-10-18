from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Optional profile extension for the Django auth user."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    student_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return self.user.get_username()
