from rest_framework import serializers
from .models import Item

class ItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['user' , 'created_at']

class ItemDetailSerializer(serializers.ModelSerializer):
    firebase_uid = serializers.SerializerMethodField()
    def get_firebase_uid(self, obj):
        return obj.user.username
    class Meta:
        model = Item
        fields = '__all__'