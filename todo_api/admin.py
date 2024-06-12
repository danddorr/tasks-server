from django.contrib import admin

# Register your models here.

from .models import TaskList, Task, UserTaskList, ItemPosition

admin.site.register(TaskList)
admin.site.register(Task)
admin.site.register(UserTaskList)
admin.site.register(ItemPosition)
