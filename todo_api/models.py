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


    def __str__(self):
        return self.user.username + " " + self.tasklist.name

class ItemPosition(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    tasklist = models.ForeignKey(TaskList, on_delete = models.CASCADE, blank = True, null = True)
    task = models.ForeignKey(Task, on_delete = models.CASCADE, blank = True, null = True)
    position = models.IntegerField()

    def __str__(self):
        if self.tasklist:
            return self.tasklist.name + " " + str(self.position)
        elif self.task:
            return self.task.task + " " + str(self.position)
