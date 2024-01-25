from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_routes),
    path('posts/', views.posts),
    path('post/<str:pk>', views.post),
    path('users/', views.users),
    path('user/<str:pk>', views.user),
    path('like-post/<str:pk>/<method>', views.post_like),
    path('like-comment/<str:pk>/<method>', views.comment_like),
    path('delete-comment/<str:pk>/', views.delete_comment),
    path('delete-post/<str:pk>/', views.delete_post),

]
