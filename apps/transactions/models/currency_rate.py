from django.db import models

from apps.core.choices import CurrencyChoices

class CurrencyRate(models.Model):
	from_currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)

	to_currency = models.CharField(max_length=3, choices=CurrencyChoices.choices)

	rate = models.DecimalField(max_digits=12, decimal_places=6)

	date = models.DateField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('from_currency', 'to_currency', 'date')

	def __str__(self):
		return f"{self.from_currency} to {self.to_currency}: {self.rate}"
