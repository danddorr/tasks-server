from django.urls import path
from .views import *

urlpatterns = [
    path('tasklists/', TaskListApiView.as_view()),
    path('tasklists/<int:tasklist_id>/', TaskListDetailApiView.as_view()),
    path('tasks/<int:task_id>/', TaskApiView.as_view()),
    path('positions/', TaskListPositionsChange.as_view()),
]