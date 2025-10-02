from django.urls import path
from .views import ListUsers,GoalsView,ListProgressView,RegsisterUser,ProgressView,WeeklySummaryView,MonthlySummaryView

urlpatterns=[
    path('users/',ListUsers.as_view()),
    path('goals/<int:goalNum>/progress/',ProgressView.as_view(),name="progress"),
    path('goals/<int:goalNum>/progress/<int:progressNum>',ProgressView.as_view(),name="goals"),

    path('goals/',GoalsView.as_view(),name="goals"),
    path('goals/<int:goalNum>',GoalsView.as_view(),name="goals"),
    path('progress/',ListProgressView.as_view()),
    path('summary/weekly/', WeeklySummaryView.as_view(), name='weekly_summary'),
    path('summary/weekly/<int:goalNum>/',WeeklySummaryView.as_view(), name='weekly_summary_goal'),
    path('summary/monthly/', MonthlySummaryView.as_view(), name='monthly_summary'),
    path('summary/monthly/<int:goalNum>/', MonthlySummaryView.as_view(), name='monthly_summary_goal'),
    path('user/',RegsisterUser.as_view(),name="register-user")
    
]