from functools import wraps

from django.core.exceptions import PermissionDenied

from apps.users.models import Profile, Family


def require_family_access(func):
	@wraps(func)
	def wrapper(telegram_id, family_id, *args, **kwargs):
		try:
			profile = Profile.objects.get(telegram_id=telegram_id)
		except Profile.DoesNotExist:
			raise PermissionDenied('User profile not found')

		if not Family.objects.filter(id=family_id, members=profile).exists():
			raise PermissionDenied('You are not a member of this family')

		return func(telegram_id, family_id, *args, profile=profile, **kwargs)

	return wrapper


def require_profile(func):
	@wraps(func)
	def wrapper(telegram_id, *args, **kwargs):
		try:
			profile = Profile.objects.get(telegram_id=telegram_id)
		except Profile.DoesNotExist:
			raise PermissionDenied('User profile not found. Please start the bot first.')

		return func(telegram_id, *args, profile=profile, **kwargs)

	return wrapper
