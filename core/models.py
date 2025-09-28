from django.db import models
from django.contrib.auth.models import User 
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import Coalesce


# Create your models here.
class Goal(models.Model):
    class CategoryType(models.TextChoices):
        PRIMARY='Primary'
        SECONDARY='Secondary'
        MINOR='Minor'
    goal_name=models.TextField(blank=False)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='goal')
    category=models.TextField(blank=False,default=CategoryType.PRIMARY,choices=CategoryType.choices)
    is_complete=models.BooleanField(default=False)
    deadline=models.DateField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    

    def __str__(self):
        return f"Goal- {self.goal_name} -created_at:{self.created_at}"
    
    @property
    def completion_percentage(self):
        agg=self.progress.aggregate(
            total_logged=Coalesce(Sum("logged_hours"),timedelta()),
            total_hours=Coalesce(Sum("total_hours"),timedelta()),
        )
        total_logged=agg["total_logged"]
        total_hours=agg["total_hours"]

        if total_hours.total_seconds()==0:
            return 0
        return round((total_logged.total_seconds()/total_hours.total_seconds())*100,2)



    

class Progress(models.Model):
    progress=models.TextField(blank=False)
    goal=models.ForeignKey(Goal,on_delete=models.CASCADE,related_name='progress')
    is_complete=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    logged_hours=models.DurationField(blank=True,null=True)
    total_hours=models.DurationField(blank=True,null=True)
    updated_at=models.DateTimeField(auto_now=True)

    @property
    def percentage_complete(self):
        if self.total_hours and self.total_hours.total_seconds() > 0:
            return (self.logged_hours.total_seconds() / self.total_hours.total_seconds()) * 100
        return 0
    
    def save(self, *args, **kwargs):
    
        if isinstance(self.logged_hours, str):
            h, m, s = map(int, self.logged_hours.split(":"))
            self.logged_hours = timedelta(hours=h, minutes=m, seconds=s)

        if isinstance(self.total_hours, str):
            h, m, s = map(int, self.total_hours.split(":"))
            self.total_hours = timedelta(hours=h, minutes=m, seconds=s)

        
        self.is_complete = self.logged_hours >= self.total_hours

        super().save(*args, **kwargs)
    





def __str__(self):
    return f"Progress:{self.progress}-goal:{self.goal.goal_name}-complete:{self.is_complete}-created_at:{self.created_at}"





