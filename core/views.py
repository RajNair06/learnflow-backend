from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Goal,Progress
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import GoalSerializer,ProgressSerializer

class ListUsers(APIView):
    def get(self,request):
        usernames=[user.username for user in User.objects.all()]
        return Response(usernames)

class GoalsView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,goalNum=None):
        goals = Goal.objects.filter(user=request.user)
        serializer = GoalSerializer(goals, many=True)
        if goalNum:
            goal=serializer.data[goalNum-1]
            return Response(goal)
        else:
                     
            return Response(serializer.data)

    def post(self, request):
        serializer = GoalSerializer(data=request.data)
        if serializer.is_valid():
            goal = serializer.save(user=request.user)
            return Response(GoalSerializer(goal).data, status=201)
        return Response(serializer.errors, status=400)


class ProgressView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, goalNum, progressNum=None):
        goals = Goal.objects.filter(user=request.user).order_by("id")
        try:
            goal = goals[goalNum - 1]
        except IndexError:
            return Response({"error": "invalid goalNum"}, status=404)

        progresses = Progress.objects.filter(goal=goal).order_by("id")

        if progressNum:
            try:
                progress = progresses[progressNum - 1]
            except IndexError:
                return Response({"error": "invalid progressNum"}, status=404)
            return Response(ProgressSerializer(progress).data, status=200)

        return Response(ProgressSerializer(progresses, many=True).data, status=200)

    
    def post(self,request,goalNum):
        goals=Goal.objects.filter(user=request.user).order_by("id")
        try:
            goal=goals[goalNum-1]
        except IndexError:
            return Response({"error":"invalid goalNum"},status=404)
        
        serializer=ProgressSerializer(data=request.data)

        if serializer.is_valid():
            progress=serializer.save(goal=goal)
            return Response(ProgressSerializer(progress).data,status=201)
        
        return Response(serializer.errors,status=400)
    
    def patch(self, request, goalNum, progressNum):
            goals = Goal.objects.filter(user=request.user).order_by("id")
            try:
                goal = goals[goalNum - 1]
            except IndexError:
                return Response({"error": "invalid goalNum"}, status=404)

            progresses = Progress.objects.filter(goal=goal).order_by("id")
            try:
                progress = progresses[progressNum - 1]
            except IndexError:
                return Response({"error": "invalid progressNum"}, status=404)

            
            progress.logged_hours = request.data.get("logged_hours", progress.logged_hours)
            if progress.logged_hours == progress.total_hours:
                progress.is_complete = True
            progress.save()

            return Response(ProgressSerializer(progress).data, status=200)



    

class ListProgressView(APIView):
    def get(self,request):
        progress=Progress.objects.all().values('progress','goal__goal_name')
        progress=list(progress)
        return Response(progress)

class RegsisterUser(APIView):
    def post(self,request):
        body=request.data
        username=body.get("username")
        password=body.get("password")
        email=body.get("email")
        first_name=body.get("first_name")
        last_name=body.get("last_name")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            status=status.HTTP_201_CREATED
        )
        

    
    
