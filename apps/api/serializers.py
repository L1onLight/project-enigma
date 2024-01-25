from apps.posts.models import Post
from rest_framework import serializers

from apps.user.models import CustomUser


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ['id', 'title', 'body', 'postImage', 'author']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'bio', 'avatar', 'inst_url', 'steam_url',
                  'telegram_url', ]
