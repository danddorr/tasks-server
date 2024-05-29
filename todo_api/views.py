from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import *
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsOwner
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

class TodoListApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner] 

    # 1. List all
    def get(self, request, *args, **kwargs):
        # Retrieve all todo items for the authenticated user
        todos = UserTodoList.objects.filter(user_id=request.user.id).values_list('todolist', flat=True)
        todos = TodoList.objects.filter(id__in=todos)
        serializer = TodoListSerializer(todos, many=True)
        print(serializer.data)
        # Construct custom response data
        custom_data = {
            'count': todos.count(),  # Total count of todos
            'results': serializer.data,  # Serialized todo items
            'message': 'List of todo items retrieved successfully.'
        }
        # Return custom response
        return Response(custom_data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Todo with given todo data
        '''

        data = {
            'name': request.data.get('name'),
        }

        serializer = TodoListSerializer(data=data)
        if serializer.is_valid():
            todo_list = serializer.save()

            user_data = {
                'user': request.user.id,
                'todolist': todo_list.id,  # Pass the ID of the newly created TodoList
                'role': 'owner'
            }

            user_serializer = UsersTodoListsSerializer(data=user_data)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TodoDetailApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, todolist_id, user_id):
        '''
        Helper method to get the object with given todo_id, and user_id
        '''
        try:
            user_todo_list = UserTodoList.objects.get(todolist_id=todolist_id, user_id=user_id)
            return user_todo_list.todolist
        except UserTodoList.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, todo_id, *args, **kwargs):
        '''
        Retrieves the Todo with given todo_id
        '''
        todo_instance = self.get_object(todo_id, request.user.id)
        if not todo_instance:
            return Response(
                {"res": "Object with todo id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve all tasks that belong to the TodoList
        tasks = Task.objects.filter(todolist=todo_instance)

        # Serialize the tasks
        task_serializer = TaskSerializer(tasks, many=True)

        # Serialize the TodoList
        todo_serializer = TodoListSerializer(todo_instance)

        # Return the serialized TodoList and tasks
        return Response({
            'todolist': todo_serializer.data,
            'tasks': task_serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request, todo_id, *args, **kwargs):
        '''
        Create the Task with given task data
        '''
        todo_instance = self.get_object(todo_id, request.user.id)
        if not todo_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
            'todolist': todo_instance.id,
            'task': request.data.get('task'),
        }

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 4. Update
    def put(self, request, todo_id, *args, **kwargs):
        '''
        Updates the todo item with given todo_id if exists
        '''
        todo_instance = self.get_object(todo_id, request.user.id)
        if not todo_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        completed = datetime.now() if request.data.get('completed') else None

        data = {
            'name': request.data.get('name'), 
            'completed': completed, 
        }
        serializer = TodoListSerializer(instance = todo_instance, data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, todo_id, *args, **kwargs):
        '''
        Deletes the todo item with given todo_id if exists
        '''
        todo_instance = self.get_object(todo_id, request.user.id)
        if not todo_instance:
            return Response(
                {"res": "Object with todo id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        todo_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
    
class TaskApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, task_id, user_id):
        '''
        Helper method to get the task object with given task_id, and user_id
        '''
        try:
            # Get all TodoList objects that the user owns
            user_todo_lists = UserTodoList.objects.filter(user_id=user_id).values_list('todolist', flat=True)

            # Get the Task object with the given task_id that belongs to one of the TodoList objects
            task = Task.objects.get(id=task_id, todolist__in=user_todo_lists)
            return task
        except Task.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, task_id, *args, **kwargs):
        '''
        Retrieves the Task with given task_id
        '''
        task_instance = self.get_object(task_id, request.user.id)
        if not task_instance:
            return Response(
                {"res": "Object with task id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Serialize the Task
        serializer = TaskSerializer(task_instance)

        # Return the serialized Task
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    # 4. Update
    def put(self, request, task_id, *args, **kwargs):
        '''
        Updates the task item with given task_id if exists
        '''
        task_instance = self.get_object(task_id, request.user.id)
        if not task_instance:
            return Response(
                {"res": "Object with task id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        completed = datetime.now() if request.data.get('completed') else None

        data = {
            'task': request.data.get('task'), 
            'completed': completed, 
        }
        serializer = TaskSerializer(instance = task_instance, data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, task_id, *args, **kwargs):
        '''
        Deletes the task item with given task_id if exists
        '''
        task_instance = self.get_object(task_id, request.user.id)
        if not task_instance:
            return Response(
                {"res": "Object with task id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        task_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )