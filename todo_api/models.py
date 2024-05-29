from django.db import models
from django.contrib.auth.models import User

class TodoList(models.Model):
    name = models.CharField(max_length = 50)
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    completed_at = models.DateTimeField(blank = True, null=True)
    last_updated_at = models.DateTimeField(auto_now = True, blank = True)

    def __str__(self):
        return self.name
    
class Task(models.Model):
    todolist = models.ForeignKey(TodoList, on_delete = models.CASCADE, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    completed_at = models.DateTimeField(blank = True, null=True)
    last_updated_at = models.DateTimeField(auto_now = True, blank = True)
    task = models.CharField(max_length = 300)

    def __str__(self):
        return self.task

class UserTodoList(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    todolist = models.ForeignKey(TodoList, on_delete = models.CASCADE, blank = True, null = True)
    role = models.CharField(max_length = 300)


    def __str__(self):
        return self.user.username + " " + self.todolist.name

"""
class TodoList(models.Model):
    name = models.CharField(max_length = 50)
    timestamp = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    completed = models.BooleanField(default = False, blank = True)
    updated = models.DateTimeField(auto_now = True, blank = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)

    def __str__(self):
        return self.task
    
class Task(models.Model):
    todolist_id = models.ForeignKey(TodoList, on_delete = models.CASCADE, blank = True, null = True)
    timestamp = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    completed = models.BooleanField(default = False, blank = True)
    updated = models.DateTimeField(auto_now = True, blank = True)
    task = models.CharField(max_length = 300)

    def __str__(self):
        return self.task
    
"""  