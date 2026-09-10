from rest_framework import serializers
from .models import Conversation
from .models import Message

class ConversationSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    participant1_username = serializers.SerializerMethodField()
    participant2_username = serializers.SerializerMethodField()

    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    class Meta:
        model = Conversation
        fields  = '__all__'
        read_only_fields = ['participant1']
    def get_participant1_username(self, obj):
        return self._display_name(obj.participant1)

    def get_participant2_username(self, obj):
        return self._display_name(obj.participant2)

    def _display_name(self, user):
        try:
            name = user.profile.full_name
            if name:
                return name
        except Exception:
            pass
        return f"User {user.username[:8]}"
    def get_is_blocked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.blocked_by.filter(id=request.user.id).exists()
        return False
    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return msg.text[:50] if msg.text else '[Image]'
        return None

    def get_last_message_time(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        return msg.created_at.isoformat() if msg else None
class MessageSerializer(serializers.ModelSerializer):
    is_mine = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender' , 'conversation' ]
    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False
        