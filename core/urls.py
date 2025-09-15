from django.urls import path
from .views import ListUsers,GoalsView,ListProgressView,RegsisterUser,ProgressView

urlpatterns=[
    path('users/',ListUsers.as_view()),
    path('goals/<int:goalNum>/progress/',ProgressView.as_view(),name="progress"),
    path('goals/<int:goalNum>/progress/<int:progressNum>',ProgressView.as_view(),name="goals"),
    path('goals/',GoalsView.as_view(),name="goals"),
    path('goals/<int:goalNum>',GoalsView.as_view(),name="goals"),
    path('progress/',ListProgressView.as_view()),
    path('user/',RegsisterUser.as_view(),name="register-user")
    
]