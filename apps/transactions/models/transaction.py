from django.db import models

from apps.users.models import Profile, Family
from apps.core.choices import CurrencyChoices

from .category import Category

class Transaction(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='transactions')

	family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')

	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='transactions')

	amount = models.DecimalField(max_digits=12, decimal_places=2)

	base_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text='Amount in user`s base currency')

	currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)

	description = models.TextField(blank=True)

	raw_text = models.TextField(help_text='Original AI message', blank=True)

	date = models.DateField()

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.amount} {self.currency} - {self.category.name}"
