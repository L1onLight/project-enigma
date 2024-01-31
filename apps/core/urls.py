from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings

from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<str:pk>/', views.post_view, name='post'),
    path('create-post/', views.create_post, name='create_post'),
    path('search/', views.search, name='search'),
    path('user/<str:pk>', views.user_profile, name='user_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    # path('post-like/<str:pk>/<method>', views.post_like, name='post_like'),
    # path('comment-like/<str:pk>/<method>', views.comment_like, name='comment_like'),
    path('login/', views.log_in, name='login'),
    path('restore-password/', views.restore_password, name='restore_password'),
    path('logout/', views.log_out, name='logout'),
    path('register/', views.register, name='register'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
