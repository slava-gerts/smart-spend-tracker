import pytest
from decimal import Decimal

from django.contrib.auth.models import User

from apps.core.choices import CurrencyChoices
from apps.users.models import Profile
from apps.transactions.models import CurrencyRate, Transaction
from apps.transactions.services import TransactionService


@pytest.mark.django_db
def test_create_transaction_with_conversion():
	user = User.objects.create(username="testuser")
	profile = Profile.objects.create(user=user, telegram_id=123, base_currency=CurrencyChoices.EUR)

	CurrencyRate.objects.create(
		from_currency=CurrencyChoices.RSD,
		to_currency=CurrencyChoices.EUR,
		rate=Decimal('0.0085')
	)

	transaction = TransactionService.create_transaction(
		telegram_id=123,
		amount=1000,
		currency=CurrencyChoices.RSD,
		category_name="Food"
	)

	assert transaction.base_amount == Decimal('8.50')
	assert transaction.category.name == "Food"
	assert Transaction.objects.count() == 1
