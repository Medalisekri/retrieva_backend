from django.db import models
from django.contrib.auth.models import User
from datetime import date 
from datetime import timedelta
from django.utils import timezone

def get_expiry_date():
  return timezone.now() + timedelta(days=60)
class Item(models.Model):
    type = models.CharField(max_length=10)
    category = models.CharField(max_length=50)
    name = models.CharField(max_length=50 , blank=True)
    description = models.TextField(blank=True)
    img_url = models.CharField(max_length=500 , blank= True)
    status = models.CharField(max_length=10)
    lat = models.DecimalField(decimal_places=7 , max_digits=10)
    long = models.DecimalField(decimal_places=7 , max_digits=10)
    incident_date = models.DateField(max_length=50, default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateField(null=True , blank=True , default=get_expiry_date)
    is_reported = models.BooleanField(default=False)
    user = models.ForeignKey(User , on_delete=models.CASCADE)



