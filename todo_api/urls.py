from django.urls import path
from .views import (
    TodoListApiView,
    TodoDetailApiView,
    TaskApiView,
)

urlpatterns = [
    path('api/', TodoListApiView.as_view()),
    path('api/<int:todo_id>/', TodoDetailApiView.as_view()),
    path('api/task/<int:task_id>/', TaskApiView.as_view()),
]