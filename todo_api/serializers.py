from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer as BaseUserSerializer
from .models import *

class ItemPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPosition
        fields = '__all__'

class TaskListSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()

    class Meta:
        model = TaskList
        fields = ['id', 'name', 'created_at', 'completed_at', 'last_updated_at', 'position']

    def get_position(self, obj):
        item_positions = obj.itemposition_set.all()
        if item_positions:
            return item_positions[0].position
        else:
            return None
        
class TaskSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'tasklist', 'created_at', 'completed_at', 'last_updated_at', 'task', 'position']

    def get_position(self, obj):
        item_positions = obj.itemposition_set.all()
        if item_positions:
            return item_positions[0].position
        else:
            return None
    
class UsersTaskListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTaskList
        fields = '__all__'

class UserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'email', 'username', 'password']

class CurrentUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'username', 'password']