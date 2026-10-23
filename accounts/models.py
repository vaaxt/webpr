from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    city = models.CharField(max_length=100, blank=True)
    about = models.TextField(blank=True)

    def __str__(self):
        return f'Profile for {self.user.username}'
