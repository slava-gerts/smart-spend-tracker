from decimal import Decimal

from django.utils import timezone

from apps.ai.parser import ExpenseParser
from apps.transactions.models import Category, CurrencyRate, Transaction
from apps.users.models import Family, Profile


class TransactionService:
	
	@staticmethod
	def process_raw_message(telegram_id: int, text: str, family_id: int = None):
		profile = Profile.objects.get(telegram_id=telegram_id)

		extractions = ExpenseParser().parse_text(text).expenses

		family = TransactionService._get_family_if_exists(family_id)

		categories = TransactionService._get_or_create_categories_bulk(profile, extractions)
		rates = TransactionService._get_exchange_rates_bulk(profile.base_currency, extractions)

		return TransactionService._save_transactions_bulk(profile, family, categories, rates, extractions, text)

	@staticmethod
	def _get_family_if_exists(family_id):
		return Family.objects.get(id=family_id) if family_id else None

	@staticmethod
	def _get_or_create_categories_bulk(profile, extractions):
		names = {item.category for item in extractions}

		existing_cats = {cat.name: cat for cat in Category.objects.filter(name__in=names, user=profile)}

		missing_names = names - set(existing_cats.keys())
		if missing_names:
			new_cats = [Category(name=name, user=profile) for name in missing_names]
			created_cats = Category.objects.bulk_create(new_cats)
			for cat in created_cats:
				existing_cats[cat.name] = cat

		return existing_cats

	@staticmethod
	def _get_exchange_rates_bulk(base_currency, extractions):
		currencies = {item.currency for item in extractions if item.currency and item.currency != base_currency}
		if not currencies:
			return {}

		rate_qs = CurrencyRate.objects.filter(
			from_currency__in=currencies,
			to_currency=base_currency
		).order_by('from_currency', '-date').distinct('from_currency')

		return {r.from_currency: r.rate for r in rate_qs}

	@staticmethod
	def _save_transactions_bulk(profile, family, categories, rates, extractions, raw_text):
		transactions = [
			Transaction(
				profile=profile,
				family=family,
				category=categories[item.category],
				amount=Decimal(item.amount),
				base_amount=Decimal(item.amount) * rates.get(item.currency or profile.base_currency, Decimal('1.0')),
				currency=item.currency or profile.base_currency,
				description=item.description or '',
				raw_text=raw_text,
				date=item.date or timezone.now().date()
			)
			for item in extractions
		]

		return Transaction.objects.bulk_create(transactions)
