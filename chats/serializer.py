from rest_framework import serializers
from .models import Conversation
from .models import Message

class ConversationSerializer(serializers.ModelSerializer):
    is_blocked = serializers.SerializerMethodField()
    class Meta:
        model = Conversation
        fields  = '__all__'
    def get_is_blocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.blocked_by.filter(id=request.user.id).exists()
        return False
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        