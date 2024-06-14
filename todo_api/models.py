from django.db import models
from django.contrib.auth.models import User

class TaskList(models.Model):
    name = models.CharField(max_length = 50)
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    completed_at = models.DateTimeField(blank = True, null=True)
    last_updated_at = models.DateTimeField(auto_now = True, blank = True)

    def __str__(self):
        return f"{self.name} {self.id}"
    
class Task(models.Model):
    tasklist = models.ForeignKey(TaskList, on_delete = models.CASCADE, blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
    completed_at = models.DateTimeField(blank = True, null=True)
    last_updated_at = models.DateTimeField(auto_now = True, blank = True)
    task = models.CharField(max_length = 300)
    position = models.IntegerField()

    def __str__(self):
        return self.task

class UserTaskList(models.Model):
    creator = "Creator"
    viewer = "Viewer"
    editor = "Editor"

    role_choices = [
        (creator, "Creator"),
        (viewer, "Viewer"),
        (editor, "Editor")
    ]

    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    tasklist = models.ForeignKey(TaskList, on_delete = models.CASCADE, blank = True, null = True)
    role = models.CharField(max_length = 10, choices = role_choices, default = creator)
    position = models.IntegerField()

    def __str__(self):
        return self.user.username + " " + self.tasklist.name
