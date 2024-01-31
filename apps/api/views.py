from pprint import pprint

from django.contrib.auth import get_user_model
from drf_spectacular import renderers
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes, inline_serializer, OpenApiResponse, OpenApiExample
)
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from apps.posts.models import Post, Comment, Tag
from django.http import HttpResponse
from rest_framework import status, viewsets, serializers, parsers, mixins

from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from apps.api.serializers import PostSerializer, UserSerializer, TagSerializer, CommentSerializer, DetailPostSerializer, \
    CommentUpdateSerializer, PostCreateSerializer, UserManagerSerializer, DetailUserSerializer
from rest_framework import generics, authentication, permissions
from rest_framework.settings import api_settings
from apps.api.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.models import Token

"""
Views for User API.
"""


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    """Create a new user in the system."""
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return UserManagerSerializer
        elif self.action == "update" or self.action == "partial_update":
            return DetailUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == "create":
            return []
        else:
            return super().get_permissions()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance != request.user:
            return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            instance.refresh_from_db()
            return Response(serializer.data)
        return Response(serializer.errors)


class TokenViewSet(viewsets.ViewSet):
    """Get or create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            val = serializer.validate({"email": request.data.get("email"), "password": request.data.get("password")})
            if val.get("user"):
                user = val.get("user")
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "user_id": user.id,
                    "email": user.email,
                    "token": token.key,
                })
        return Response(serializer.errors, status=401)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "page",
                OpenApiTypes.INT,
                description="Posts result pagination"
            )
        ]
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete"]
    pagination_class = PageNumberPagination

    @extend_schema(request=PostCreateSerializer)
    def create(self, request, *args, **kwargs):
        """Create new post"""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, tagList=dict(request.data).get("tags"))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user:
            partial = kwargs.pop("partial", None)
            serializer = self.serializer_class(instance=instance, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save(tags=dict(request.data).get("tags"))
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You are not the author."}, status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author == request.user or request.user.is_staff or request.user.is_superuser:
            instance.delete()
            return Response({"message": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "You are not the author."}, status=status.HTTP_403_FORBIDDEN)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailPostSerializer
        return PostSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == "retrieve":
            return []
        elif self.action == "comments":
            if self.request.method == "PUT":
                return [IsAuthenticated()]
            else:
                return [IsAuthenticatedOrReadOnly()]
        else:
            return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "page",
                OpenApiTypes.INT,
                description="Comments result pagination"
            )
        ],
        request=CommentSerializer
    )
    @action(methods=["GET", "PUT"], detail=True, url_path="comments", pagination_class=CommentSerializer)
    def comments(self, request, pk=None, *args, **kwargs):
        if request.method == "PUT":

            post = self.get_object()
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(toPost=post, commentAuthor=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        elif request.method == "GET":
            queryset = self.filter_queryset(Comment.objects.filter(toPost=pk).all())
            paginator = PageNumberPagination()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = CommentSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                serializer = CommentSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # http_method_names = ["get", "post", "delete"]
    http_method_names = ["delete"]

    # @extend_schema(
    #     request=inline_serializer(
    #         name="TagSerializer2",
    #         fields={
    #             "tagTitle": serializers.CharField(),
    #         },
    #     ),
    # )
    # def create(self, request, *args, **kwargs):
    #     res = super().create(request, *args, **kwargs)
    #     return Response(res.data, status=status.HTTP_201_CREATED)

    @extend_schema(description="To delete tags. Staff or Superuser privileges are required.")
    def destroy(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.is_staff:
            self.get_object().delete()
            return Response({"message": "Tag removed."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "You must be an admin."}, status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        if self.action == 'list':
            return []
        else:
            return super().get_permissions()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "page",
                OpenApiTypes.INT,
                description="Comments result pagination"
            )
        ]
    )
)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, AllowAny]

    http_method_names = ["patch", "delete"]

    @extend_schema(
        request=CommentUpdateSerializer
    )
    def update(self, request, *args, **kwargs):
        if not request.data.get("commentBody", None):
            return Response({"message": "commentBody shouldn't be empty"},
                            status=status.HTTP_400_BAD_REQUEST)
        partial = kwargs.pop('partial', False)  # Determine if it's a partial update (PATCH)
        instance = self.get_object()

        serializer = self.serializer_class(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance.commentAuthor.id == request.user.id:
            serializer.save(commentAuthor=request.user)
        else:
            return Response({"message": "You are not the author."}, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.data)

    def destroy(self, request: Request, *args, **kwargs):
        try:
            comment = self.get_object()
            if request.user == comment.commentAuthor or request.user.is_staff or request.user.is_superuser:
                comment.delete()
                return Response({"message": "Deleted"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "You are not the author."}, status=status.HTTP_403_FORBIDDEN)
        except Comment.DoesNotExist:
            return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema(request=inline_serializer(name="RatingSerializer",
                                         fields={
                                             "pk": serializers.IntegerField(),
                                             "method": serializers.CharField(),
                                             "type": serializers.CharField(),
                                         }),
               examples=[OpenApiExample(name="Values", description="Values example for the request",
                                        value={
                                            "pk": "1 #integer id of post/comment",
                                            "method": "like/dislike",
                                            "type": "post/comment"
                                        }), ])
@api_view(["POST"])
def rating(request, ):
    method = request.data.get("method")
    type = request.data.get("type")
    pk = request.data.get("pk")
    if not request.user.is_authenticated:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    if type == "post":
        try:
            instance = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'message': 'Does Not Exist'}, status.HTTP_400_BAD_REQUEST)
    elif type == "comment":
        try:
            instance = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'message': 'Does Not Exist'}, status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "method, type and pk is required"}, status=status.HTTP_400_BAD_REQUEST)
    if method == 'like':
        if instance.dislikes.all().filter(email=request.user.email):
            instance.dislikes.remove(request.user)
        if instance.likes.all().filter(email=request.user.email):
            instance.likes.remove(request.user)
        else:
            instance.likes.add(request.user)
        instance.save()
        return Response({"total_likes": instance.total_likes()})
    elif method == 'dislike':
        if instance.likes.all().filter(email=request.user.email):
            instance.likes.remove(request.user)
        if instance.dislikes.all().filter(email=request.user.email):
            instance.dislikes.remove(request.user)
        else:
            instance.dislikes.add(request.user)
        instance.save()
        return Response({"total_likes": instance.total_likes()})
    return Response({'message': 'Unauthorized'})
