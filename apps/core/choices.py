from django.db import models

class CurrencyChoices(models.TextChoices):
	RSD = 'RSD', 'Serbian dinar'
	EUR = 'EUR', 'Euro'
	USD = 'USD', 'US Dollar'
	RUB = 'RUB', 'Russian ruble'
