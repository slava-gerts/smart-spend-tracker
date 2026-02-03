from django.db import models

from .user import Profile

class Family(models.Model):
	name = models.CharField(max_length=100)

	members = models.ManyToManyField(Profile, related_name='families')

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name
