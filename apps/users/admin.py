from django.contrib import admin

from apps.users.models import Profile, Family


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'telegram_id', 'base_currency', 'timezone', 'active_family')
	search_fields = ('telegram_id', 'user__username')


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
	list_display = ('name', 'invite_code', 'owner', 'created_at')
	search_fields = ('name', 'invite_code')
