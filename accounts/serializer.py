from .models import Profile
from rest_framework import serializers

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    class Meta:
        model = Profile
        fields = ['full_name', 'is_verified' ,'onesignal_id' , 'user_id']

