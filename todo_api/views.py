from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsOwner
from rest_framework.permissions import IsAuthenticated
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
        
        print(tasklists)
        print(serializer.data)

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

            length = UserTaskList.objects.filter(user_id=request.user.id).count()

            user_data = {
                'user': request.user.id,
                'tasklist': tasklist.id,
                'role': UserTaskList.creator,
                'position': length,
            }

            user_serializer = UsersTaskListsSerializer(data=user_data)

            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

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
            'position': Task.objects.filter(tasklist=tasklist_instance).count(),
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

        data = {
            'name': request.data.get('name'), 
            'completed_at': completed, 
        }

        serializer = TaskListSerializer(instance = tasklist_instance, data=data, partial = True)
        
        if serializer.is_valid():
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
        
    def get_UserTaskList(self, tasklist_id, user_id):
        try:
            userTasklist = UserTaskList.objects.get(tasklist_id=tasklist_id, user_id=user_id)
            return userTasklist
        except UserTaskList.DoesNotExist:
            return None
        
    def get_Task(self, task_id, user_id):
        try:
            task = Task.objects.get(id=task_id, tasklist__usertasklist__user_id=user_id)
            return task
        except Task.DoesNotExist:
            return None
        
    def validate(self, itemType, positions, user_id: int) -> dict[UserTaskList|Task, int] | str:
        if not positions:
            return "No positions provided"
        
        elif not isinstance(positions, dict):
            return "Positions should be a dictionary"
        
        elif not all(str(k).isnumeric() for k in positions.keys()):
            return "Some of the ids are invalid"
        
        elif not all(str(v).isnumeric() for v in positions.values()):
            return "Some of the positions are invalid"

        elif max(positions.values()) >= len(positions):
            return "Some of the positions are too high"
        
        elif min(positions.values()) < 0:
            return "Some of the positions are negative"
        
        elif len(positions) != len(positions):
            return "Some of the ids are duplicated"
        
        elif len(positions) != len(set(positions.values())):
            return "Some of the positions are duplicated"
        
        if itemType == 'tasks':
            obj_pos = dict(zip(map(lambda x: self.get_Task(int(x), user_id), positions.keys()), positions.values()))
        else:
            obj_pos = dict(zip(map(lambda x: self.get_UserTaskList(int(x), user_id), positions.keys()), positions.values()))
        
        if not all(obj_pos.keys()):
            return "Some of the ids are invalid"

        return obj_pos

    def put(self, request, itemType, *args, **kwargs):

        positions = self.validate(itemType, request.data, request.user.id)

        if isinstance(positions, str):
            return Response(positions, status=status.HTTP_400_BAD_REQUEST)
        
        instances = []
        for obj, index in positions.items():
            obj.position = index
            obj.save()
            instances.append(obj)
            
        if itemType == 'tasks':
            serializer = TaskSerializer(instances, many=True)
        else:
            serializer = UsersTaskListsSerializer(instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
