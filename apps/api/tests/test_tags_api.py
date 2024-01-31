from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.api.for_test import create_test_user
from rest_framework.test import APIClient
from rest_framework import status

from apps.api.serializers import TagSerializer
from apps.posts.models import Tag, Post

TAGS_URL = reverse("api:tag-list")


def detail_view(tag_id):
    """Create and return a tag detail url."""
    return reverse("api:tag-detail", args=[tag_id])


class PublicTagsApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.test_user = create_test_user(email="testus@mail.ex")
        self.post = Post.objects.create(author=self.test_user, title="ExamplePost", body="ExamplePostBody")
        self.payload = {"tagTitle": "ExampleTag"}

    def test_auth_not_required(self):
        """Test retrieving tags as unauthenticated user"""
        Tag.objects.create(tagTitle="Cool")
        Tag.objects.create(tagTitle="Mega Coool")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_unauthorized_create_tag_error(self):
        """Test returns error if user trying to create comment when unauthorized."""
        response = self.client.post(TAGS_URL, self.payload)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_unauthorized_delete_tag_error(self):
        tag = Tag.objects.create(tagTitle="Example")
        url = detail_view(tag.id)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)


class PrivateTagsApiTests(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.client.force_authenticate(self.user)

        self.payload = {"tagTitle": "ExampleTag"}

    def test_create_tag_error(self):
        """Test that comment is created successfully"""
        res = self.client.post(TAGS_URL, self.payload)
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, res.status_code)

    def test_retrieve_tags_error(self):
        """Test retrieving comments as authenticated user"""
        Tag.objects.create(tagTitle="Tag1")
        Tag.objects.create(tagTitle="Tag2")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_retrieve_specific_tag_error(self):
        """Test retrieving specific comments as authenticated user"""
        comm1 = Tag.objects.create(tagTitle="Tag1")
        comm2 = Tag.objects.create(tagTitle="Tag2")

        res1 = self.client.get(detail_view(comm1.id))
        res2 = self.client.get(detail_view(comm2.id))

        self.assertEqual(res1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(res2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_edit_tag_error(self):
        """Test that tags can be managed by author and toPost cannot be changed"""
        tag = Tag.objects.create(tagTitle="Tag1")
        url = detail_view(tag.id)
        payload = {"tagTitle": "NewTag"}
        res1 = self.client.patch(url, payload)
        res2 = self.client.put(url, payload)
        self.assertEqual(res1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(res2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        tag.refresh_from_db()
        self.assertEqual(tag.tagTitle, "Tag1")

    def test_delete_tag_error(self):
        tag = Tag.objects.create(tagTitle="SuperTag")
        url = detail_view(tag.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        tag.refresh_from_db()
        self.assertEqual(tag.tagTitle, "SuperTag")

    def test_delete_tag_staff(self):
        """Ensure that staff can delete tags."""
        staff = create_test_user(email="staff@mail.ex", is_staff=True)
        self.assertTrue(staff.is_staff)
        self.client.force_authenticate(staff)
        tag = Tag.objects.create(tagTitle="Staff")
        url = detail_view(tag.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        with self.assertRaises(Exception):
            tag.refresh_from_db()

    def test_delete_tag_superuser(self):
        """Ensure that superuser can delete tags."""
        superuser = create_test_user(email="superuser@mail.ex", is_superuser=True)
        self.assertTrue(superuser.is_superuser)
        self.client.force_authenticate(superuser)

        tag = Tag.objects.create(tagTitle="SuperUser")
        url = detail_view(tag.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        with self.assertRaises(Exception):
            tag.refresh_from_db()
