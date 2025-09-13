from django.test import TestCase
from django.contrib.auth.models import User
from .models import Goal,Progress

class CoreTestCase(TestCase):
    def setUp(self):
        
        test_user=User.objects.create(username='gg05')
        test_goal=Goal.objects.create(goal_name='learn python',user=test_user)

        test_progress=Progress.objects.create(progress='Learn functional programming',goal=test_goal)
        print(f'Test user created:{test_user}')
        print(f'Test goal created:{test_goal.goal_name}')
        print(f'Test progress created:{test_progress.progress}')
        
    def test_core(self):
        u1=User.objects.get(username='gg05')
        self.assertEqual(u1.username,'gg05')

    
    
        

