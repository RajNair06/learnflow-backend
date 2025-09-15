from django.db import models
from django.contrib.auth.models import User 


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
    
    def save(self,*args,**kwargs):
        if self.total_hours and self.logged_hours>=self.total_hours:
            self.is_complete=True
        else:
            self.is_complete=False
        super().save(*args,**kwargs)
    





def __str__(self):
    return f"Progress:{self.progress}-goal:{self.goal.goal_name}-complete:{self.is_complete}-created_at:{self.created_at}"





