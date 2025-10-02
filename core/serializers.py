from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Goal, Progress,CustomUser


class GoalSerializer(ModelSerializer):
    class Meta:
        model = Goal
        fields = ["id", "goal_name", "category", "is_complete", "deadline","completion_percentage", "created_at", "updated_at", "user"]
        read_only_fields=["created_at","completion_percentage","updated_at"]
        extra_kwargs = {"user": {"read_only": True}}

class ProgressSerializer(ModelSerializer):
    class Meta:
        model = Progress
        fields = ["id", "progress", "goal","logged_hours","total_hours","percentage_complete", "is_complete","created_at", "updated_at"]
        read_only_fields = ["goal","percentage_complete", "created_at", "updated_at"]
        extra_kwargs = {"goal": {"read_only": True}}  
    
class WeeklySummarySerializer(serializers.Serializer):
    week_start = serializers.DateTimeField()
    total_hours = serializers.DecimalField(max_digits=10, decimal_places=2)

class MonthlySummarySerializer(serializers.Serializer):
    month_start = serializers.DateTimeField()
    total_hours = serializers.DecimalField(max_digits=10, decimal_places=2)

class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {"password": {"write_only": True}}
