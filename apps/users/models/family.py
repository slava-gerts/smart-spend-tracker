import secrets
import string
from django.db import models

from .user import Profile


def generate_invite_code():
	return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


class Family(models.Model):
	name = models.CharField(max_length=100)

	owner = models.ForeignKey(
		Profile,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='owned_families',
		help_text="Owner of the family"
	)

	invite_code = models.CharField(
		max_length=12,
		unique=True,
		default=generate_invite_code,
		null=True,
		help_text="Secure code for joining the family"
	)

	members = models.ManyToManyField(Profile, related_name='families')

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.name} ({self.invite_code})"
