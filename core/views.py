from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Goal,Progress
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import GoalSerializer

class ListUsers(APIView):
    def get(self,request):
        usernames=[user.username for user in User.objects.all()]
        return Response(usernames)

class GoalsView(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        goals = Goal.objects.filter(user=request.user)
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GoalSerializer(data=request.data)
        if serializer.is_valid():
            goal = serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


    

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
        

    
    
