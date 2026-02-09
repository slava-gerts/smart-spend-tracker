import pytest
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User

from apps.ai.schemas import ExpenseExtraction
from apps.core.choices import CurrencyChoices
from apps.transactions.models import Transaction, CurrencyRate
from apps.transactions.services import TransactionService
from apps.users.models import Profile


@pytest.mark.django_db
@patch('apps.ai.parser.ExpenseParser.parse_text')
def test_full_flow_logic(mock_parse):
	mock_parse.return_value = ExpenseExtraction(
		amount=100.0,
		currency=None,
		category="Transport",
		description="taxi"
	)

	user = User.objects.create(username="bot_user")
	Profile.objects.create(user=user, telegram_id=777, base_currency=CurrencyChoices.RSD)

	TransactionService.process_raw_message(777, "Taxi for 100")

	tx = Transaction.objects.first()
	assert tx.amount == Decimal('100.0')
	assert tx.currency == CurrencyChoices.RSD
	assert tx.category.name == "Transport"
	assert tx.profile.telegram_id == 777
	
