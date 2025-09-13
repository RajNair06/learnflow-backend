from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Goal,Progress
from rest_framework.response import Response

class ListUsers(APIView):
    def get(self,request):
        usernames=[user.username for user in User.objects.all()]
        return Response(usernames)

class ListGoalsView(APIView):
    def get(self,request):
        goals=Goal.objects.all().values('user','user__username','goal_name','category')
        goals=list(goals)
        return Response(goals)
    

class ListProgressView(APIView):
    def get(self,request):
        progress=Progress.objects.all().values('progress','goal__goal_name')
        progress=list(progress)
        return Response(progress)
    
    
