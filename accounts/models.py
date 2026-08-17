from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    is_verified = models.BooleanField(default=False)
    user = models.OneToOneField(User , on_delete=models.CASCADE)

