from django.contrib import admin

from apps.transactions.models import Transaction, Category, CurrencyRate


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('profile', 'amount', 'currency', 'category', 'date', 'family')
	list_filter = ('currency', 'category', 'date')
	search_fields = ('profile__user__username', 'description')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'user')


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
	list_display = ('from_currency', 'to_currency', 'rate', 'date')
