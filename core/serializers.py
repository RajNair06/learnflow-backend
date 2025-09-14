from rest_framework.serializers import ModelSerializer
from .models import Goal, Progress
from django.contrib.auth.models import User

class GoalSerializer(ModelSerializer):
    class Meta:
        model = Goal
        fields = ["id", "goal_name", "category", "is_complete", "deadline", "created_at", "updated_at", "user"]
        extra_kwargs = {"user": {"read_only": True}}

class ProgressSerializer(ModelSerializer):
    class Meta:
        model = Progress
        fields = ["id", "progress", "goal", "is_complete", "created_at", "updated_at"]
        extra_kwargs = {"goal": {"read_only": True}}  

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {"password": {"write_only": True}}
