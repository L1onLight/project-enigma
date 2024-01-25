from django.db import models
from apps.user.models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=50)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    body = models.TextField()
    tagList = models.ManyToManyField("Tag", blank=True)
    postImage = models.ImageField(null=True, default="empty_body.jpg")
    addedToFav = models.ManyToManyField(CustomUser, blank=True, related_name='addedToFav')
    comments = models.ManyToManyField("Comment", blank=True)
    likes = models.ManyToManyField(CustomUser, related_name='liked_post')
    dislikes = models.ManyToManyField(CustomUser, related_name='disliked_post')

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ordering = ['-updated', '-created']
        ordering = ['-created']

    def __str__(self):
        return f"{self.title[:50]}"

    def count_fav(self):
        return self.addedToFav.count()

    def total_likes(self):
        return self.likes.all().count() - self.dislikes.all().count()

    def clean_tags(self):
        if self.tagList.count() > 4:
            raise ValidationError("You can select a maximum of 4 tags.")
        return True


class Tag(models.Model):
    tagTitle = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.tagTitle


class Comment(models.Model):
    toPost = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    commentAuthor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    commentBody = models.TextField()
    likes = models.ManyToManyField(CustomUser, related_name='liked_comment')
    dislikes = models.ManyToManyField(CustomUser, related_name='disliked_comment')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']

    def total_likes(self):
        return self.likes.all().count() - self.dislikes.all().count()

    def __str__(self):
        return f"{self.commentAuthor}: {self.commentBody[:50]}"
