from django.urls import path
from .views import ListUsers,ListGoalsView,ListProgressView,RegsisterUser

urlpatterns=[
    path('users/',ListUsers.as_view()),
    path('goals/',ListGoalsView.as_view()),
    path('progress/',ListProgressView.as_view()),
    path('user/',RegsisterUser.as_view())
    
]