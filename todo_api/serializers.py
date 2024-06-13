from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer as BaseUserSerializer
from .models import *

class TaskListSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()

    class Meta:
        model = TaskList
        fields = ['id', 'name', 'created_at', 'completed_at', 'last_updated_at', 'position']

    def get_position(self, obj):
        item_positions = obj.usertasklist_set.first()
        if item_positions:
            return item_positions.position
        else:
            return None
    
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
    
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