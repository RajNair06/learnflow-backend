from django.urls import path
from .views import ListUsers,ListGoalsView,ListProgressView

urlpatterns=[
    path('users/',ListUsers.as_view()),
    path('goals/',ListGoalsView.as_view()),
    path('progress/',ListProgressView.as_view()),
    
]