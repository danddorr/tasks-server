from django.urls import path
from .views import (
    TaskListApiView,
    TaskListDetailApiView,
    TaskApiView,
)

urlpatterns = [
    path('tasklists/', TaskListApiView.as_view()),
    path('tasklists/<int:tasklist_id>/', TaskListDetailApiView.as_view()),
    path('tasks/<int:task_id>/', TaskApiView.as_view()),
]