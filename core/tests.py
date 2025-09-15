from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Goal,Progress
from datetime import timedelta

class GoalsAppJWTTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )

    def authenticate(self):
        """Helper method to get JWT token and set Authorization header"""
        url = "/api/token/"
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_goal_authenticated(self):
        self.authenticate()  # Get token and set header

        url = "/api/goals/"
        data = {
            "goal_name": "Learn Django",
            "category": "Primary",
            "is_complete": False,
            "deadline": "2025-12-31"
            
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["goal_name"], "Learn Django")
        self.assertEqual(response.data["user"], self.user.id)

    def test_create_goal_unauthenticated(self):
        url = "/api/goals/"
        data = {
            "goal_name": "Unauthorized Goal",
            "category": "Primary",
            "is_complete": False,
            "deadline": "2025-12-31"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_goals_authenticated(self):
        Goal.objects.create(
            goal_name="Complete Project",
            category="Primary",
            user=self.user
        )
        self.authenticate()

        url = "/api/goals/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["goal_name"], "Complete Project")

    def test_get_goals_unauthenticated(self):
        url = "/api/goals/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ProgressViewTests(TestCase):
    def setUp(self):
        
        # Create a user and authenticate
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create a Goal for this user
        self.goal = Goal.objects.create(
            user=self.user,
            goal_name="Learn Python",
            category="Primary",
            is_complete=False
        )

        # Create Progress items
        self.progress1 = Progress.objects.create(
            goal=self.goal,
            progress="Basics",
            total_hours=timedelta(hours=2),
            logged_hours=timedelta(hours=1),
            is_complete=False
        )
        self.progress2 = Progress.objects.create(
            goal=self.goal,
            progress="OOP",
            total_hours=timedelta(hours=3),
            logged_hours=timedelta(minutes=30),
            is_complete=False
        )

    def test_get_all_progress(self):
        url = f"/api/goals/1/progress/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["progress"], "Basics")

    def test_get_single_progress(self):
        url = f"/api/goals/1/progress/2/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["progress"], "OOP")

    def test_post_progress(self):
        url = f"/api/goals/1/progress/"
        data = {
            "progress": "Advanced Topics",
            "total_hours": timedelta(hours=1, minutes=30),
            "logged_hours": timedelta(0)  # start at 0
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["progress"], "Advanced Topics")
        self.assertEqual(Progress.objects.filter(goal=self.goal).count(), 3)

    def test_patch_progress_logged_hours(self):
        url = f"/api/goals/1/progress/1/"
        data = {"logged_hours": timedelta(hours=2)}  # equal to total_hours

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.progress1.refresh_from_db()
        self.assertEqual(self.progress1.logged_hours, timedelta(hours=2))
        self.assertTrue(self.progress1.is_complete)

    def test_invalid_goalNum_returns_404(self):
        url = f"/api/goals/5/progress/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_progressNum_returns_404(self):
        url = f"/api/goals/1/progress/10/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)