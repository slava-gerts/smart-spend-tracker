import pytest

from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from apps.users.models import Profile, Family
from apps.core.decorators import require_family_access, require_profile


@require_family_access
def dummy_family_action(telegram_id, family_id):
	return "Success"


@require_profile
def dummy_profile_action(telegram_id):
	return "Success"


@pytest.mark.django_db
def test_require_family_access_granted():
	user = User.objects.create(username="testuser")
	profile = Profile.objects.create(user=user, telegram_id=123)
	family = Family.objects.create(name="Test Family")
	family.members.add(profile)

	assert dummy_family_action(123, family.id) == "Success"


@pytest.mark.django_db
def test_require_family_access_denied():
	user = User.objects.create(username="intruder")
	profile = Profile.objects.create(user=user, telegram_id=999)
	family = Family.objects.create(name="Private Family")

	with pytest.raises(PermissionDenied) as excinfo:
		dummy_family_action(999, family.id)

	assert "not a member of this family" in str(excinfo.value)


@pytest.mark.django_db
def test_require_profile_granted():
	user = User.objects.create(username="testuser")
	profile = Profile.objects.create(user=user, telegram_id=123)

	assert dummy_profile_action(123) == "Success"


@pytest.mark.django_db
def test_require_profile_denied():
	user = User.objects.create(username="intruder")

	with pytest.raises(PermissionDenied) as excinfo:
		dummy_profile_action(999)

	assert "User profile not found" in str(excinfo.value)
