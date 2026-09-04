from rest_framework import serializers
from .models import Item

class ItemListSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
   
    poster_name = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = '__all__' 
        read_only_fields = ['user' , 'created_at' ]
    def get_poster_name(self, obj):
            profile = getattr(obj.user, 'profile', None)
            if profile and profile.full_name:
                return profile.full_name
            return obj.user.email or 'User'
    def get_is_owner(self, obj):
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                return obj.user == request.user
            return False
class ItemDetailSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    firebase_uid = serializers.SerializerMethodField()
   
    poster_name = serializers.SerializerMethodField()

    def get_firebase_uid(self, obj):
        return obj.user.username
    class Meta:
        model = Item
        fields = '__all__' 
         
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user == request.user
        return False
    def get_poster_name(self, obj):
        profile = getattr(obj.user, 'profile', None)
        if profile and profile.full_name:
            return profile.full_name
        return obj.user.email or 'User'