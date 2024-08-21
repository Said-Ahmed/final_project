from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import manager

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=True)

    objects: manager

    def __str__(self):
        return f'Profile of {self.user.username}'
