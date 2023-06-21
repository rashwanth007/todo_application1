from django.shortcuts import HttpResponse 
from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
import jwt
from django.conf import settings
from .models import ToDo
from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage


# Create your views here.
def index(request):
    return HttpResponse("index")

def history(request,userName):
    data = ToDo.objects.filter(user_name=userName, status="Completed")
    tasks = []
    files = []
    description = []

    for item in data:
        tasks.append(item.task)
        files.append(item.file.path) 
        description.append(item.description)

    response_data = {
        "tasks": tasks,
        "files": files,
        "description": description,
    }
    return response_data


def delete_tasks(request):
    selected_tasks = request.data.get('tasks', [])
    
    # Delete the selected tasks from the database
    ToDo.objects.filter(task__in=selected_tasks).delete()
    
    return "deleted"
    
    
    
def create_task(request,userName,task,description,status):
    data = ToDo.objects.all()
    boolean = True
    for item in data:
        if item.task == task and item.status == "Pending" and item.user_name == userName:
            boolean = False
    if boolean:
        ToDo.objects.create(
            user_name=userName,
            task=task,
            description=description,
            status=status
            )
        print("obj created successfully")

    
def read_task(request,userName):
    data = ToDo.objects.filter(user_name=userName,status="Pending")
    task = []
    for item in data:
        task.append(item.task)
        
    response_data = {
        "task" : task,
    }
        
    return response_data

def upload_file(request,userName,task,description,status,uploaded_file):
    updating_obj = ToDo.objects.filter(user_name=userName, task=task, status="Pending").first()
    print(updating_obj)
    updating_obj.description = description
    updating_obj.status = status
    save_directory = 'files/'
    updating_obj.file = default_storage.save(save_directory + uploaded_file.name, uploaded_file)
    updating_obj.save()
    response_data={'message': 'File uploaded successfully', 'file_path': "wow"}
    return response_data

        

class Todo(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get(self,request,*args,**kwargs):
        try:
            response ={"WOW":"wow - 1"}
            Type = self.request.GET.get('type')
            userName = self.request.GET.get('userName')
            task = self.request.GET.get('task')
            status = self.request.GET.get('status')
            discription = self.request.GET.get('discription')
             
            if Type == "history":
                response = history(request,userName)
            elif Type == "delete":
                response = delete_tasks(request)
            elif Type == "create":
                response = create_task(request,userName,task,discription,status)
            elif Type == "read":
                response = read_task(request,userName)
            return JsonResponse(response,safe=False)
            
        except Exception as e:
            return Response({'error': str(e)})

    def post(self,request,*args,**kwargs):
        try:
            response ={"WOW":"wow - 1"}
            Type = self.request.GET.get('type')
            userName = self.request.GET.get('userName')
            task = self.request.GET.get('task')
            status = self.request.GET.get('status')
            description = self.request.GET.get('description')
            uploaded_file = self.request.FILES.get('file')

            
            if Type == "history":
                response = history(request,userName)
            elif Type == "create":
                response = create_task(request,userName,task,description,status)
            elif Type == "read":
                response = read_task(request,userName)
            elif Type == "uploadfile":
                response = upload_file(request,userName,task,description,status,uploaded_file)
            return JsonResponse(response,safe=False)
                
        except Exception as e:
            return Response({'error': str(e)})
            
    
    
class DataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            token = request.META['HTTP_AUTHORIZATION'].split()[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload['user_id']
            data = {"Userid":user_id}
            request.session['username']=data
            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=401)