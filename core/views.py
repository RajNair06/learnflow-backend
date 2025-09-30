from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import Goal,Progress
from rest_framework import status
from django.db.models import Sum,Value,ExpressionWrapper, F, DecimalField
from django.db.models.functions import TruncWeek,Coalesce,Extract
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import GoalSerializer,ProgressSerializer,WeeklySummarySerializer
from .pagination import CustomPagination

class WeeklySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, goalNum=None):
        try:
            
            goals = Goal.objects.filter(user=request.user).order_by('id')
            
            if goalNum is not None:
                
                if goalNum < 1 or goalNum > goals.count():
                    return Response(
                        {'error': 'Invalid goal number'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                goal = goals[goalNum - 1]
                queryset = Progress.objects.filter(goal=goal)
            else:
                
                queryset = Progress.objects.filter(goal__user=request.user)

            
            weekly_data = queryset.annotate(
                week_start=TruncWeek('created_at')
            ).values('week_start').annotate(
                total_hours=Coalesce(
                    ExpressionWrapper(
                        # Extract hours from interval sum
                        Sum(
                            Extract('logged_hours', 'epoch') / 3600.0  # Convert seconds to hours
                        ),
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    ),
                    Value(0.0, output_field=DecimalField(max_digits=10, decimal_places=2)),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ).order_by('week_start')

            
            serializer = WeeklySummarySerializer(weekly_data, many=True)
            return Response(serializer.data)
        except IndexError:
            return Response(
                {'error': 'Goal not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

            


class ListUsers(APIView):
    def get(self,request):
        usernames=[user.username for user in User.objects.all()]
        return Response(usernames)

class GoalsView(APIView):
    permission_classes=[IsAuthenticated]
    pagination_class=CustomPagination
    
    
    def get(self,request,goalNum=None):
        
        goals = Goal.objects.filter(user=request.user)
        category=request.query_params.get('category')
        is_complete=request.query_params.get('is_complete')
        if category:
            goals=goals.filter(category=category)
        if is_complete:
            goals=goals.filter(is_complete=is_complete)
        
        
        

        if goalNum:
            try:
                goal = goals.order_by('id')[goalNum-1] 
                serializer = GoalSerializer(goal) 
                return Response(serializer.data)
            except IndexError:
                return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            paginator=self.pagination_class()
            page=paginator.paginate_queryset(goals,request)
            if page is not None:
                serializer = GoalSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = GoalSerializer(goals, many=True)
                     
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
        

    
    
