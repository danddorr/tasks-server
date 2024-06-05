from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer as BaseUserSerializer
from .models import *

class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskList
        fields = '__all__'

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