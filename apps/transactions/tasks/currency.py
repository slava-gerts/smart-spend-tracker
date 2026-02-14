import requests

from decimal import Decimal
from celery import shared_task

from django.utils import timezone

from apps.transactions.models import CurrencyRate


@shared_task(name='apps.transactions.tasks.update_currency_rates')
def update_currency_rates():
	base_currency = 'EUR'
	target_currencies = ['RSD', 'USD', 'RUB', 'EUR']

	url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"

	try:
		response = requests.get(url, timeout=10)
		response.raise_for_status()
		rates = response.json().get('rates', {})

		for curr in target_currencies:
			if curr in rates:
				rate = Decimal(str(rates[curr]))

				CurrencyRate.objects.update_or_create(
					from_currency=curr,
					to_currency=base_currency,
					defaults={
						'rate': Decimal('1.0') / rate if rate != 0 else Decimal('0.0'),
						'date': timezone.now()
					}
				)

		return "Currency rates updated successfully"
	except Exception as e:
		return f"Error updating rates: {str(e)}"
