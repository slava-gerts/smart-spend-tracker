from apps.core.choices import CurrencyChoices

class CurrencyDescriptor:
	def __init__(self, name):
		self.name = name

	def __get__(self, instance, owner):
		if instance is None:
			return self

		return instance.__dict__.get(self.name)
		
	def __set__(self, instance, value):
		if value not in CurrencyChoices.values:
			raise ValueError(f'Invalid currency "{value}". Supported currencies are: {CurrencyChoices.values}')

		instance.__dict__[self.name] = value
		