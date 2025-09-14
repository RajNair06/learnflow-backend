from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Goal

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
