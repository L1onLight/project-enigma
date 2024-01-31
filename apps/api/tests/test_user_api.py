import os.path
import tempfile
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.api.for_test import create_test_user
from rest_framework.test import APIClient
from rest_framework import status

USER_URL = reverse("api:user-list")


#
def detail_view(user_id):
    """Create and return a user detail url."""
    return reverse("api:user-detail", args=[user_id])


class PublicUserApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.payload = {"email": "test@mail.com", "password": "megapass123"}
        self.test_user = create_test_user()

    def test_create_user_unauthorized(self):
        res = self.client.post(USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data.get("id"))
        self.assertTrue(get_user_model().objects.filter(pk=res.data.get("id")).exists())

    def test_get_specific_user_unauthorized(self):
        """Test to retrieve specific user when unauthorized"""
        res = self.client.get(detail_view(self.test_user.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data.get("id"))

    def test_update_another_user_unauthorized_error(self):
        res = self.client.patch(detail_view(self.test_user.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)

        self.payload = {"email": "test@mailB.com",
                        "password": "megapass123",
                        "first_name": "string",
                        "last_name": "string",
                        "username": "string",
                        "avatar": tmp_file,
                        "bio": "string",
                        "inst_url": "https://example.com/",
                        "steam_url": "https://example.com/",
                        "telegram_url": "https://example.com/"}
        self.user = create_test_user(email="test@mail.com", password="megapass123")
        self.client.force_authenticate(self.user)
        self.test_user = create_test_user()

    def test_edit_another_user_error(self):
        res = self.client.patch(detail_view(self.test_user.id), self.payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_edit_personal_profile_success(self):
        user = create_test_user(email="sample@mail.net")
        self.client.force_authenticate(user)
        self.client.patch(detail_view(user.id), self.payload)
        user.refresh_from_db()
        self.assertEqual(user.email, self.payload["email"])
        self.assertEqual(user.first_name, self.payload["first_name"])
        self.assertEqual(user.last_name, self.payload["last_name"])
        self.assertEqual(user.username, self.payload["username"])
        self.assertEqual(user.bio, self.payload["bio"])
        self.assertEqual(user.inst_url, self.payload["inst_url"])
        self.assertEqual(user.steam_url, self.payload["steam_url"])
        self.assertEqual(user.telegram_url, self.payload["telegram_url"])

        self.assertEqual(user.avatar, os.path.basename(self.payload["avatar"].name))

    def test_put_edit_personal_profile_success(self):
        user = create_test_user(email="sample@mail.net")
        self.client.force_authenticate(user)
        self.client.put(detail_view(user.id), self.payload)
        user.refresh_from_db()
        self.assertEqual(user.email, self.payload["email"])
        self.assertEqual(user.first_name, self.payload["first_name"])
        self.assertEqual(user.last_name, self.payload["last_name"])
        self.assertEqual(user.username, self.payload["username"])
        self.assertEqual(user.bio, self.payload["bio"])
        self.assertEqual(user.inst_url, self.payload["inst_url"])
        self.assertEqual(user.steam_url, self.payload["steam_url"])
        self.assertEqual(user.telegram_url, self.payload["telegram_url"])

        self.assertEqual(user.avatar, os.path.basename(self.payload["avatar"].name))
