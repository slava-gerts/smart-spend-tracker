from django.db import models

from apps.users.models import Profile

class Category(models.Model):
	name = models.CharField(max_length=50)

	user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='categories')

	class Meta:
		verbose_name_plural = 'Categories'
		constraints = [
			models.UniqueConstraint(
				fields=['name', 'user'],
				name='unique_category_per_user'
			)
		]

	def __str__(self):
		return f"{self.name} ({self.user.user.username})"
