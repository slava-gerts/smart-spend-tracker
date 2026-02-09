from decimal import Decimal

from django.utils import timezone

from apps.ai.parser import ExpenseParser
from apps.core.decorators import require_profile
from apps.transactions.models import Category, CurrencyRate, Transaction
from apps.users.models import Family, Profile


class TransactionService:
	
	@staticmethod
	def get_exchange_rate(from_curr, to_curr):
		if from_curr == to_curr:
			return Decimal('1.0')

		rate_obj = CurrencyRate.objects.filter(from_currency=from_curr, to_currency=to_curr).order_by('-date').first()

		return rate_obj.rate if rate_obj else None


	@staticmethod
	@require_profile
	def create_transaction(telegram_id, amount, currency, category_name, description='', family_id=None, raw_text='', date=None, profile=None):
		date = date or timezone.now().date()

		category, _ = Category.objects.get_or_create(name=category_name, user=profile)

		rate = TransactionService.get_exchange_rate(currency, profile.base_currency)
		if rate:
			base_amount = Decimal(amount) * rate
		else:
			base_amount = Decimal(amount)

		family = None
		if family_id:
			family = Family.objects.get(id=family_id)

		transaction = Transaction.objects.create(
			profile=profile,
			family=family,
			category=category,
			amount=Decimal(amount),
			base_amount=base_amount,
			currency=currency,
			description=description,
			raw_text=raw_text,
			date=date
		)

		return transaction


	@staticmethod
	def process_raw_message(telegram_id, text, family_id=None):
		parser = ExpenseParser()
		extracted = parser.parse_text(text)
		
		profile = Profile.objects.get(telegram_id=telegram_id)

		currency = extracted.currency or profile.base_currency

		return TransactionService.create_transaction(
			telegram_id=telegram_id,
			amount=extracted.amount,
			currency=currency,
			category_name=extracted.category,
			description=extracted.description or '',
			family_id=family_id,
			raw_text=text,
			date=extracted.date,
			profile=profile
		)
