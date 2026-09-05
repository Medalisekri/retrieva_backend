from django.db import models
from django.contrib.auth.models import User
from items.models import Item


class Conversation(models.Model):
    participant1 = models.ForeignKey(User , on_delete=models.CASCADE , related_name='conversations_as_p1')
    participant2 = models.ForeignKey(User , on_delete=models.CASCADE ,related_name='conversations_as_p2')
    item = models.ForeignKey(Item, on_delete=models.CASCADE,related_name='conversations_as_item')
    created_at = models.DateTimeField(auto_now_add=True)
    blocked_by = models.ManyToManyField(User  , blank=True , related_name='blocked_conversations')
   

class Message(models.Model):
    conversation = models.ForeignKey(Conversation , on_delete=models.CASCADE ,related_name='conversation')
    text = models.CharField(max_length=400)
    sender = models.ForeignKey(User , on_delete=models.CASCADE ,related_name='message_sender')
    is_deleted = models.BooleanField(default=False)
    img_url = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
