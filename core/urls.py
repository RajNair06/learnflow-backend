from django.urls import path
from .views import ListUsers,GoalsView,ListProgressView,RegsisterUser

urlpatterns=[
    path('users/',ListUsers.as_view()),
    path('goals/',GoalsView.as_view(),name="goals"),
    path('progress/',ListProgressView.as_view()),
    path('user/',RegsisterUser.as_view(),name="register-user")
    
]