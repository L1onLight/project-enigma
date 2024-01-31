from django.test import TestCase
from django.urls import reverse
from apps.api.for_test import create_test_user

from rest_framework.test import APIClient
from rest_framework import status

from apps.api.serializers import CommentSerializer
from apps.posts.models import Post, Comment

COMMENT_URL = reverse("api:comment-list")


def detail_view(comment_id):
    """Create and return a comment detail url."""
    return reverse("api:comment-detail", args=[comment_id])


class PublicCommentsApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.test_user = create_test_user(email="testus@mail.ex")
        self.post = Post.objects.create(author=self.test_user, title="ExamplePost", body="ExamplePostBody")
        self.payload = {"commentBody": "TextBody", "toPost": 1}

    def test_restricted_methods(self):
        """["GET", "POST", "PUT"]"""
        Comment.objects.create(commentAuthor=self.test_user, commentBody="Cool", toPost=self.post)
        comment = Comment.objects.create(commentAuthor=self.user, commentBody="MegaCoool", toPost=self.post)
        res1 = self.client.get(COMMENT_URL)
        res2 = self.client.post(COMMENT_URL, self.payload)
        url = detail_view(comment_id=comment.id)
        res3 = self.client.get(url)
        res4 = self.client.put(url, commentBody="NewMegaCool")

        self.assertEqual(res1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res2.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res3.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res4.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_is_required_error(self):
        """Test updating/deleting comments as unauthenticated user returns an error"""
        Comment.objects.create(commentAuthor=self.test_user, commentBody="Cool", toPost=self.post)
        comment = Comment.objects.create(commentAuthor=self.test_user, commentBody="MegaCoool", toPost=self.post)

        url = detail_view(comment.id)
        res1 = self.client.patch(url)
        res2 = self.client.delete(url)

        self.assertEqual(res1.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res2.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(Comment.objects.count(), 2)

    def test_update_comment_error(self):
        """Test returns error if user is unauthenticated and trying to update/patch/delete comment"""
        Comment.objects.create(commentBody="TextBody1", toPost=self.post, commentAuthor=self.test_user)
        url = detail_view(1)
        response = self.client.patch(url, {**self.payload})
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        response3 = self.client.delete(url)
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response3.status_code)


class PrivateCommentsApiTests(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.test_user = create_test_user(email="testus@mail.ex")
        self.post = Post.objects.create(author=self.test_user, title="ExamplePost", body="ExamplePostBody")
        self.payload = {"commentBody": "TextBodyPrivate", "toPost": 1}

    def test_restricted_methods(self):
        ["GET", "POST", "PUT"]
        Comment.objects.create(commentAuthor=self.test_user, commentBody="Cool", toPost=self.post)
        comment = Comment.objects.create(commentAuthor=self.user, commentBody="MegaCoool", toPost=self.post)
        res1 = self.client.get(COMMENT_URL)
        res2 = self.client.post(COMMENT_URL, self.payload)
        url = detail_view(comment_id=comment.id)
        res3 = self.client.get(url)
        res4 = self.client.put(url, commentBody="NewMegaCool")

        self.assertEqual(res1.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(res2.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(res3.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(res4.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_edit_comment(self):
        """Test that comment can be managed by author and toPost cannot be changed"""
        comment = Comment.objects.create(commentAuthor=self.user, commentBody="TestBody", toPost_id=1)
        url = detail_view(comment.id)
        payload = {"commentBody": "NewTestBody", "toPost": 4}
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.commentBody, payload["commentBody"])
        self.assertEqual(comment.toPost.id, 1)

    def test_delete_comment(self):
        """Test that comment can be deleted by author."""
        comm1 = Comment.objects.create(commentBody="TextBodySample", toPost=self.post, commentAuthor=self.user)
        comm2 = Comment.objects.create(commentBody="TextBody2", toPost=self.post, commentAuthor=self.user)
        res = self.client.delete(detail_view(comment_id=comm2.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        with self.assertRaises(Exception):
            Comment.objects.get(id=comm2.id)
        self.assertTrue(Comment.objects.filter(id=comm1.id).exists())
        self.assertFalse(Comment.objects.filter(id=comm2.id).exists())

    def test_manage_comment_error(self):
        """Test returns error if user is not an author and trying to update/patch/delete comment."""
        comment = Comment.objects.create(commentBody="TextBody1", toPost=self.post, commentAuthor=self.test_user)
        url = detail_view(comment.id)

        response1 = self.client.patch(url, {**self.payload})
        self.assertEqual(status.HTTP_403_FORBIDDEN, response1.status_code)
        response2 = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response2.status_code)
        comment.refresh_from_db()

        self.assertEqual(comment.commentBody, "TextBody1")
