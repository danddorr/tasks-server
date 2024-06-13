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
from django.utils import timezone

class TaskListApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner] 

    # 1. List all
    def get(self, request, *args, **kwargs):
        # Retrieve all tasklist items for the authenticated user
        userTasklists = UserTaskList.objects.filter(user_id=request.user.id)
        userTasklists_ids = userTasklists.values_list('tasklist', flat=True)
        tasklists = TaskList.objects.filter(id__in=userTasklists_ids)
        serializer = TaskListSerializer(tasklists, many=True)

        print(ItemPosition.objects.filter(user_id=request.user.id))
        
        print(tasklists)
        print(serializer.data)
        for tasklist in tasklists:
            print(tasklist.itemposition_set.all())

        # Construct custom response data
        custom_data = {
            'count': tasklists.count(),  # Total count of tasklists
            'results': serializer.data,  # Serialized tasklist items
            'message': 'List of tasklist items retrieved successfully.'
        }
        # Return custom response
        return Response(custom_data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Tasklist with given tasklist data
        '''

        data = {
            'name': request.data.get('name'),
        }

        serializer = TaskListSerializer(data=data)
        if serializer.is_valid():
            tasklist = serializer.save()

            user_data = {
                'user': request.user.id,
                'tasklist': tasklist.id,
                'role': UserTaskList.creator,
            }

            length = UserTaskList.objects.filter(user_id=request.user.id).count()
            itemPosition = {
                'user': request.user.id,
                'tasklist': tasklist.id,
                'position': length,
            }

            itemPositionSerializer = ItemPositionSerializer(data=itemPosition)
            user_serializer = UsersTaskListsSerializer(data=user_data)

            if user_serializer.is_valid() and itemPositionSerializer.is_valid():
                user_serializer.save()
                itemPositionSerializer.save()
            else:
                return Response([user_serializer.errors, itemPositionSerializer.errors], status=status.HTTP_400_BAD_REQUEST)

            return Response([serializer.data, itemPositionSerializer.data], status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskListDetailApiView(APIView):
    # add permission to check if user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, tasklist_id, user_id):
        '''
        Helper method to get the object with given tasklist_id, and user_id
        '''
        try:
            userTasklist = UserTaskList.objects.get(tasklist_id=tasklist_id, user_id=user_id)
            return userTasklist.tasklist
        except UserTaskList.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, tasklist_id, *args, **kwargs):
        '''
        Retrieves the Tasklist with given tasklist_id
        '''
        tasklist_instance = self.get_object(tasklist_id, request.user.id)
        if not tasklist_instance:
            return Response(
                {"res": "Object with tasklist id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve all tasks that belong to the TaskList
        tasks = Task.objects.filter(tasklist=tasklist_instance)

        # Serialize the tasks
        task_serializer = TaskSerializer(tasks, many=True)

        # Serialize the TaskList
        tasklist_serializer = TaskListSerializer(tasklist_instance)

        # Return the serialized TaskList and tasks
        return Response({
            'tasklist': tasklist_serializer.data,
            'tasks': task_serializer.data
        }, status=status.HTTP_200_OK)
    
    def post(self, request, tasklist_id, *args, **kwargs):
        '''
        Create the Task with given task data
        '''
        tasklist_instance = self.get_object(tasklist_id, request.user.id)
        if not tasklist_instance:
            return Response(
                {"res": "Object with tasklist id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
            'tasklist': tasklist_instance.id,
            'task': request.data.get('task'),
        }

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 4. Update
    def put(self, request, tasklist_id, *args, **kwargs):
        '''
        Updates the tasklist item with given tasklist_id if exists
        '''
        tasklist_instance = self.get_object(tasklist_id, request.user.id)
        if not tasklist_instance:
            return Response(
                {"res": "Object with tasklist id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        completed = timezone.now() if request.data.get('completed') else None
        print(request.data.get('completed'))
        print(completed)

        data = {
            'name': request.data.get('name'), 
            'completed_at': completed, 
        }
        serializer = TaskListSerializer(instance = tasklist_instance, data=data, partial = True)
        if serializer.is_valid():
            print(serializer.validated_data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, tasklist_id, *args, **kwargs):
        '''
        Deletes the tasklist item with given tasklist_id if exists
        '''
        tasklist_instance = self.get_object(tasklist_id, request.user.id)
        if not tasklist_instance:
            return Response(
                {"res": "Object with tasklist id does not exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        tasklist_instance.delete()
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
            # Get all TaskList objects that the user owns
            user_tasklists = UserTaskList.objects.filter(user_id=user_id).values_list('tasklist', flat=True)

            # Get the Task object with the given task_id that belongs to one of the TaskList objects
            task = Task.objects.get(id=task_id, tasklist__in=user_tasklists)
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
        
        completed = timezone.now() if request.data.get('completed') else None

        data = {
            'task': request.data.get('task'), 
            'completed_at': completed, 
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
    
class ItemPositionsChange(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
        
    def get_tasklist(self, tasklist_id, user_id):
        try:
            userTasklist = UserTaskList.objects.get(tasklist_id=tasklist_id, user_id=user_id)
            
            return userTasklist.tasklist
        except UserTaskList.DoesNotExist:
            return None
    
    def get_task(self, task_id, user_id):
        try:
            user_tasklists = UserTaskList.objects.filter(user_id=user_id).values_list('tasklist', flat=True)

            task = Task.objects.get(id=task_id, tasklist__in=user_tasklists)
            
            return task
        except Task.DoesNotExist:
            return None
        
    def get_object(self, type, obj_id, user_id):
        if type == 'tasklists':
            return self.get_tasklist(obj_id, user_id)
        elif type == 'tasks':
            return self.get_task(obj_id, user_id)
        return None

    def put(self, request, type: str, *args, **kwargs):

        positions: dict[str, int] = request.data

        obj_pos = list(zip(map(lambda x: self.get_object(type, int(x), request.user.id), positions.keys()), positions.values()))
        print(*obj_pos)
        if not all(obj for obj, _ in obj_pos):
            return Response(
                {"res": "One of the ids is wrong"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if max(index for _, index in obj_pos) >= len(obj_pos):
            return Response(
                {"res": "One of the positions is higher than expected"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if min(index for _, index in obj_pos) < 0:
            return Response(
                {"res": "One of the positions is lower than expected"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        obj_serializers = []
        for obj, index in obj_pos:
            data = {
                'position': index, 
            }

            serializer = ItemPositionSerializer(instance=obj, data=data, partial=True)
            if serializer.is_valid():
                obj_serializers.append(serializer)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for serializer in obj_serializers:
            serializer.save() # toto nesavuje 

        return Response("success", status=status.HTTP_200_OK)
    