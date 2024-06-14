from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('tasklists/', TaskListApiView.as_view()),
    path('tasklists/<int:tasklist_id>/', TaskListDetailApiView.as_view()),
    path('tasks/<int:task_id>/', TaskApiView.as_view()),
    re_path(r'positions/(?P<itemType>\btasks\b|\btasklists\b)/', ItemPositionsChange.as_view()),
]