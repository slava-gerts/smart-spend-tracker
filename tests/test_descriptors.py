import pytest

from apps.core.descriptors import CurrencyDescriptor
from apps.core.choices import CurrencyChoices


class MockWallet:
	currency = CurrencyDescriptor('currency')

	def __init__(self, currency):
		self.currency = currency


def test_currency_descriptor_valid():
	wallet = MockWallet(CurrencyChoices.EUR)
	assert wallet.currency == CurrencyChoices.EUR


def test_currency_descriptor_invalid():
	with pytest.raises(ValueError) as excinfo:
		MockWallet('BTC')

	assert "Invalid currency" in str(excinfo.value)


def test_currency_descriptor_update():
	wallet = MockWallet(CurrencyChoices.RSD)
	wallet.currency = CurrencyChoices.EUR
	assert wallet.currency == CurrencyChoices.EUR
