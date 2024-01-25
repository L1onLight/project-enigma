from django.shortcuts import render
from django.http import JsonResponse
from apps.posts.models import Post, Comment
from django.http import HttpResponse
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PostSerializer, UserSerializer
from ..user.models import CustomUser


# Create your views here.

@api_view(['GET'])
def get_routes(request):
    routes = [
        'GET /api',
        'GET /api/posts',
        'GET /api/post/:id',
        'GET /api/users',
        'GET /api/user/:id'

    ]
    return Response(routes)


@api_view(['GET'])
def posts(request):
    posts_data = PostSerializer(Post.objects.all(), many=True)
    # posts = Post.objects.all()
    return Response(posts_data.data)


@api_view(['GET'])
def post(request, pk):
    post_data = PostSerializer(Post.objects.get(pk=pk))
    return Response(post_data.data)


@api_view(['GET'])
def users(request):
    users_data = UserSerializer(CustomUser.objects.all(), many=True)
    return Response(users_data.data)


@api_view(['GET'])
def user(request, pk):
    user_data = UserSerializer(CustomUser.objects.get(id=pk))

    return Response(user_data.data)


@api_view(['GET'])
def post_like(request, pk, method):
    if not request.user.is_authenticated:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response({'message': 'Does Not Exist'}, status.HTTP_400_BAD_REQUEST)
    if method == 'like':
        if post.dislikes.all().filter(email=request.user.email):
            post.dislikes.remove(request.user)
        if post.likes.all().filter(email=request.user.email):
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        post.save()
        response = f"ratingG-1|{post.total_likes()}"
        return HttpResponse(response)
    elif method == 'dislike':
        if post.likes.all().filter(email=request.user.email):
            post.likes.remove(request.user)
        if post.dislikes.all().filter(email=request.user.email):
            post.dislikes.remove(request.user)
        else:
            post.dislikes.add(request.user)
        post.save()
        response = f"ratingR-1|{post.total_likes()}"
        return HttpResponse(response)
    return Response({'message': 'Unauthorized'})


@api_view(['GET'])
def comment_like(request, pk, method):
    if not request.user.is_authenticated:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        return Response({'message': 'Does Not Exist'}, status.HTTP_400_BAD_REQUEST)
    if method == 'like':
        if comment.dislikes.all().filter(email=request.user.email):
            comment.dislikes.remove(request.user)
        if comment.likes.all().filter(email=request.user.email):
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
        comment.save()
        response = f"ratingG-1|{comment.total_likes()}"
        return HttpResponse(response)

    elif method == 'dislike':
        if comment.likes.all().filter(email=request.user.email):
            comment.likes.remove(request.user)
        if comment.dislikes.all().filter(email=request.user.email):
            comment.dislikes.remove(request.user)
        else:
            comment.dislikes.add(request.user)
        comment.save()
        response = f"ratingR-1|{comment.total_likes()}"
        return HttpResponse(response)


@api_view(['GET'])
def delete_comment(request, pk):
    if not request.user.is_authenticated:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        cm = Comment.objects.get(id=pk)
    except Comment.DoesNotExist:
        return Response({'message': 'Does Not Exist'}, status.HTTP_400_BAD_REQUEST)
    if request.user == cm.commentAuthor or request.user.is_staff:
        cm.delete()
        return Response('OK')
    else:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def delete_post(request, pk):
    if not request.user.is_authenticated:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        post = Post.objects.get(id=pk)
    except Post.DoesNotExist:
        return Response({'message': 'Does Not Exist'}, status.HTTP_400_BAD_REQUEST)
    if request.user == post.author or request.user.is_staff:
        post.delete()
        return Response('OK')
    else:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
