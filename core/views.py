from rest_framework.views import APIView
from .throttling import TierUserThrottle
from .models import Goal,Progress,CustomUser
from rest_framework import status
from django.db.models import Sum,Value,ExpressionWrapper, DecimalField
from django.db.models.functions import TruncWeek,Coalesce,Extract,TruncMonth
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import GoalSerializer,ProgressSerializer,WeeklySummarySerializer,MonthlySummarySerializer
from .pagination import CustomPagination
from django.core.cache import cache
from django.conf import settings
import logging

logger=logging.getLogger(__name__)


class MonthlySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, goalNum=None):
        cache_key = f"monthly_summary_{request.user.id}_{goalNum if goalNum is not None else 'all'}"
        cached_data=cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Cache hit for key: {cache_key}",extra={'cache_status':'hit'})
            return Response(cached_data)
        
        logger.info(f'Cache miss for key:{cache_key}',extra={'cache_status':'miss'})
        try:
            # Filter goals for the authenticated user, ordered consistently
            goals = Goal.objects.filter(user=request.user).order_by('id')
            
            if goalNum is not None:
                # Validate goalNum (1-based index)
                if goalNum < 1 or goalNum > goals.count():
                    return Response(
                        {'error': 'Invalid goal number'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Get the nth goal (0-based index internally)
                goal = goals[goalNum - 1]
                queryset = Progress.objects.filter(goal=goal)
            else:
                # If no goalNum, aggregate across all goals for the user
                queryset = Progress.objects.filter(goal__user=request.user)

            # Monthly summary: group by month, sum logged_hours (converted to hours)
            monthly_data = queryset.annotate(
                month_start=TruncMonth('created_at')
            ).values('month_start').annotate(
                total_hours=Coalesce(
                    ExpressionWrapper(
                        Sum(Extract('logged_hours', 'epoch') / 3600.0),  # Convert seconds to hours
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    ),
                    Value(0.0, output_field=DecimalField(max_digits=10, decimal_places=2)),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ).order_by('month_start')

            # Serialize the data
            serializer = MonthlySummarySerializer(monthly_data, many=True)

            cache_timeout=getattr(settings,'MONTHLY_SUMMARY_CACHE_TIMEOUT',300)


            cache.set(cache_key,serializer.data,timeout=cache_timeout)
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

class WeeklySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, goalNum=None):
        cache_key = f"weekly_summary_{request.user.id}_{goalNum if goalNum is not None else 'all'}"
        cached_data=cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"Cache hit for key: {cache_key}",extra={'cache_status':'hit'})
            return Response(cached_data)
        
        logger.info(f'Cache miss for key:{cache_key}',extra={'cache_status':'miss'})
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
            cache_timeout=getattr(settings,'WEEKLY_SUMMARY_CACHE_TIMEOUT',300)


            cache.set(cache_key,serializer.data,timeout=cache_timeout)
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
        usernames=[user.username for user in CustomUser.objects.all()]
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
    throttle_classes=[TierUserThrottle]
    
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
        tier=body.get("tier")

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        

        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            tier=tier
        )

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "tier":user.tier
            },
            status=status.HTTP_201_CREATED
        )
        

    
    
