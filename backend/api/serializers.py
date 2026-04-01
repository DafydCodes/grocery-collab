from rest_framework import serializers
from .models import User, List, Item

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['added_by', 'completed_by', 'list']

class ListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = ['id', 'name', 'owner', 'members', 'items', 'created_at']
        read_only_fields = ['owner']