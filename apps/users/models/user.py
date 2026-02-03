from django.db import models
from django.contrib.auth.models import User

from apps.core.choices import CurrencyChoices

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

	telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)

	base_currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.EUR)

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Profile of {self.user.username} ({self.telegram_id})"
