from django.urls import path, include

from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("posts", views.PostViewSet)
router.register("tags", views.TagsViewSet)
router.register("comments", views.CommentViewSet)
router.register("token", views.TokenViewSet, basename="token")
router.register("user", views.UserViewSet, basename="user")
# print(router.urls)
app_name = "api"

urlpatterns = [
    path('', include(router.urls)),
    path('rating/', views.rating),

]
