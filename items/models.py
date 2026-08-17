from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    type = models.CharField(max_length=10)
    category = models.CharField(max_length=50)
    name = models.CharField(max_length=50 , blank=True)
    description = models.TextField(blank=True)
    img_url = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    lat = models.DecimalField(decimal_places=7 , max_digits=10)
    long = models.DecimalField(decimal_places=7 , max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateField(null=True , blank=True)
    is_reported = models.BooleanField(default=False)
    user = models.ForeignKey(User , on_delete=models.CASCADE)


