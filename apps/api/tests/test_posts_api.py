import tempfile

from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from apps.api.for_test import create_test_user
from apps.api.serializers import PostSerializer, DetailPostSerializer
from apps.posts.models import Post

POSTS_URL = reverse("api:post-list")


def detail_view(post_id):
    return reverse("api:post-detail", args=[post_id])


class PublicPostsApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.test_user = create_test_user(email="testus@mail.ex")
        self.post = Post.objects.create(author=self.test_user, title="ExamplePost", body="ExamplePostBody")
        self.payload = {
            "title": "string",
            "body": "string",
            "postImage": "string",
            "tags": [
                "string"
            ]
        }

    def test_get_posts_success(self):
        """Test to retrieve posts as an unauthenticated user"""
        res1 = self.client.get(POSTS_URL)
        posts = Post.objects.all()
        serializer = PostSerializer(instance=posts, many=True)

        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        self.assertEqual(res1.data["results"][0]["body"], serializer.data[0]["body"])

        serializer2 = DetailPostSerializer(instance=posts.first())
        res2 = self.client.get(detail_view(self.post.id))
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["body"], serializer2.data["body"])

    def test_create_post_error(self):
        """Test returns an error if an unauthenticated user tries to create a post"""
        res = self.client.post(POSTS_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_post_error(self):
        """Test returns an error if an unauthenticated user tries to edit a post"""
        res = self.client.put(detail_view(self.post.id), self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_post_error(self):
        """Test returns an error if an unauthenticated user tries to delete a post"""
        res = self.client.delete(detail_view(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_comment_unauthorized_error(self):
        res2 = self.client.get(f"/api/posts/{self.post.id}/comments/")
        res = self.client.put(f"/api/posts/{self.post.id}/comments/", {"commentBody": "TestComment"})
        # self.assertEqual(res.status_code, status.HTTP_200_OK)
        # self.assertEqual(res.data.get("commentBody"), "TestComment")


class PrivatePostsApiTests(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.test_user = create_test_user(email="testus@mail.ex")
        self.post = Post.objects.create(author=self.test_user, title="ExamplePost", body="ExamplePostBody")

        self.payload = {
            "title": "Test Title",
            "body": "Test Body",
            "tags": [
                "Tag1",
                "Tag2"
            ]
        }

    def test_get_posts_success(self):
        """Test to retrieve posts as an authenticated user"""
        res1 = self.client.get(POSTS_URL)
        posts = Post.objects.all()
        serializer = PostSerializer(instance=posts, many=True)

        self.assertEqual(res1.status_code, status.HTTP_200_OK)

        self.assertEqual(res1.data["results"][0]["body"], serializer.data[0]["body"])

        serializer2 = DetailPostSerializer(instance=posts.first())
        res2 = self.client.get(detail_view(self.post.id))
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data["body"], serializer2.data["body"])

    def test_create_post_with_image_success(self):
        """Test to create a post with image as an authenticated user"""
        self.assertEqual(Post.objects.count(), 1)
        # To upload image
        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        tmp_file.seek(0)
        payload = self.payload.copy()
        payload["postImage"] = tmp_file
        res = self.client.post(POSTS_URL, payload, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(PostSerializer(instance=Post.objects.get(pk=2)).data, res.data)

    def test_create_post_without_image_success(self):
        """Test to create a post without image as an authenticated user"""

        self.assertEqual(Post.objects.count(), 1)
        res = self.client.post(POSTS_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(PostSerializer(instance=Post.objects.get(pk=2)).data, res.data)

    def test_edit_post_put_success(self):
        """Test for editing a post using put method"""
        post = Post.objects.create(author=self.user, title="TestTitle", body="TestBody")
        new_payload = {"title": "NewTitle", "body": "NewBody", "tags": ["NewTag", "NewTag1"]}

        res = self.client.put(detail_view(post.id), new_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        post.refresh_from_db()
        self.assertEqual(post.title, new_payload["title"])
        self.assertEqual(post.tagList.all()[0].tagTitle, new_payload["tags"][0])
        self.assertEqual(post.tagList.all()[1].tagTitle, new_payload["tags"][1])

    def test_edit_post_patch_title_success(self):
        """Test patch title with new data"""

        payload = {"title": "TestTitle", "body": "TestBody"}
        post = Post.objects.create(author=self.user, **payload)
        res = self.client.patch(detail_view(post.id), {"title": "NewTitle"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(res.data.get("title"), "NewTitle")
        self.assertEqual(res.data.get("body"), payload.get("body"))

    def test_edit_post_patch_body_success(self):
        """Test patch body with new data"""
        payload = {"title": "TestTitle", "body": "TestBody"}
        post = Post.objects.create(author=self.user, **payload)
        res = self.client.patch(detail_view(post.id), {"body": "NewBody"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(res.data.get("body"), "NewBody")
        self.assertEqual(res.data.get("title"), payload.get("title"))

    def test_edit_post_patch_tags_success(self):
        """Test patch post with single tag"""
        payload = {"title": "TestTitle", "body": "TestBody"}
        post = Post.objects.create(author=self.user, **payload)
        res = self.client.patch(detail_view(post.id), {"tags": ["FirstTag"]})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()

        self.assertEqual(post.tagList.first().tagTitle, "FirstTag")

        self.assertEqual(res.data.get("body"), payload.get("body"))
        self.assertEqual(res.data.get("title"), payload.get("title"))

    def test_edit_post_patch_multiple_tags_success(self):
        """Test patch post with multiple tags"""
        payload = {"title": "TestTitle", "body": "TestBody"}
        post = Post.objects.create(author=self.user, **payload)
        res = self.client.patch(detail_view(post.id), {"tags": ["FirstTag", "SecondTag", "ThirdTag", "FourthTag"]})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()

        self.assertEqual(post.tagList.first().tagTitle, "FirstTag")
        self.assertEqual(post.tagList.all()[1].tagTitle, "SecondTag")
        self.assertEqual(post.tagList.all()[2].tagTitle, "ThirdTag")
        self.assertEqual(post.tagList.all()[3].tagTitle, "FourthTag")

        self.assertEqual(res.data.get("body"), payload.get("body"))
        self.assertEqual(res.data.get("title"), payload.get("title"))

    def test_edit_another_post_error(self):
        """Test for editing someone else's post"""
        res = self.client.put(detail_view(self.post.id), {"title": "Test Title",
                                                          "body": "Test Body", })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_another_post_error(self):
        """Test returns error if user is not author and tries to delete post"""
        res = self.client.delete(detail_view(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_staff_success(self):
        """Test to delete someone else's post as staff"""
        staff = create_test_user(email="super@user.com", is_staff=True)
        self.client.force_authenticate(staff)
        res = self.client.delete(detail_view(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_post_superuser_success(self):
        """Test to delete someone else's post as superuser"""
        superuser = create_test_user(email="super@user.com", is_superuser=True)
        self.client.force_authenticate(superuser)
        res = self.client.delete(detail_view(self.post.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_send_comment(self):
        res = self.client.put(f"/api/posts/{self.post.id}/comments/", {"commentBody": "TestComment"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("commentBody"), "TestComment")
