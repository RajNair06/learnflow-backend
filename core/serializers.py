from rest_framework.serializers import ModelSerializer
from models import Goal,Progress
from django.contrib.auth.models import User

class GoalSerializer(ModelSerializer):
    model=Goal
    fields='__all__'
    

class ProgressSerializer(ModelSerializer):
    model=Progress
    fields='__all__'

class UserSerializer(ModelSerializer):
    model=User
    fields='__all__'
    
    