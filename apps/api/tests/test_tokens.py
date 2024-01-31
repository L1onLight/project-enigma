from django.test import TestCase
from django.urls import reverse
from apps.api.for_test import create_test_user

from rest_framework.test import APIClient
from rest_framework import status

from apps.api.serializers import CommentSerializer
from apps.posts.models import Post, Comment

TOKEN_URL = "/api/token/"


class PublicCommentsApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.payload = {"email": "testus@mail.ex", "password": "megapass123"}
        self.user = create_test_user(**self.payload)

    def test_retrieve_token_success(self):
        """Test that token can be retrieved with correct credentials"""
        res = self.client.post(TOKEN_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get("token"))

    def test_retrieve_token_error(self):
        """Test returns error if credentials are wrong"""
        res = self.client.post(TOKEN_URL, {"email": "testus@mail.ex", "password": "WrongPass"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_fields_error(self):
        """Test returns error if fields are empty"""
        res = self.client.post(TOKEN_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
