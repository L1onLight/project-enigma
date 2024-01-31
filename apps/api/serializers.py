"""
Serializers for the user API View.
"""

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field

from apps.posts.models import Post, Tag, Comment
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'username', 'bio', 'avatar', 'inst_url', 'steam_url',
                  'telegram_url', ]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}


class DetailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        # fields = "__all__"
        fields = ("id", "email", "username", "first_name", "last_name", "bio",
                  "avatar", "inst_url", "steam_url", "telegram_url")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}


class UserManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'username']
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return a user."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(request=self.context.get("request"),
                            username=email,
                            password=password, )
        if not user:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")
        attrs["user"] = user
        return attrs


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ['id', 'title', 'author', 'body', 'postImage', "tags_list",
                  "total_likes", "created"]
        read_only_fields = ["id", "likes", 'author', "dislikes", "created"]

    def _get_or_create_tags(self, tags):
        tag_list = []
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(tagTitle=tag)
            tag_list.append(tag_obj)
        return tag_list

    def save(self, **kwargs):
        _tagList1 = kwargs.pop("tagList", None)
        _tagList2 = kwargs.pop("tags", None)
        _tags = _tagList1 if _tagList1 else _tagList2
        if _tags:
            tags = self._get_or_create_tags(_tags)
            if self.partial and self.instance:
                self.instance: Post
                self.instance.tagList.set(tags)
                instance = Post.objects.filter(pk=self.instance.pk).update(**self.validated_data)
                return instance
            super().save(tagList=tags, **kwargs)
        else:
            super().save(**kwargs)


class PostCreateSerializer(PostSerializer):
    tags = serializers.ListSerializer(child=serializers.CharField())

    def title(self):
        pass

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'postImage', "tags", "created"]
        read_only_fields = ["id", "likes", 'author', "dislikes", "created"]
        extra_kwargs = {'postImage': {'required': True}}


class DetailPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ['id', 'title', 'author', "author_name", 'body', 'postImage', "tags_list", "postImage", "addedToFav",
                  "total_likes", "created"]
        read_only_fields = ["id", 'author', "likes", "dislikes", "comments", "created"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'tagTitle']
        read_only_fields = ["id"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # fields = ["id", "toPost", "commentAuthor", "commentBody", "likes", "dislikes", "updated", "created"]
        fields = ["id", "toPost", "commentAuthor", "author_name", "total_likes", "commentBody", "updated",
                  "created"]
        read_only_fields = ["id", "toPost", "commentAuthor", "likes", "dislikes", "updated", "created"]

    def save(self, **kwargs):
        if kwargs.get("commentAuthor"):
            return super().save(**kwargs)
        else:
            raise Exception("commentAuthor cannot be empty.")


class CommentUpdateSerializer(serializers.ModelSerializer):
    commentBody = serializers.CharField()

    class Meta:
        model = Comment
        fields = ['commentBody']
