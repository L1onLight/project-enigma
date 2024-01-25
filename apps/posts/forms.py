from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Post, Comment
from ..user.models import CustomUser
from django.db.models import Count


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'author', 'body', 'tagList', ]


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        exclude = ['likes', 'dislikes', 'addedToFav', 'comments']

    def clean(self):
        super().clean()

        tagList = self.cleaned_data.get('tagList')
        if tagList.count() > 4:
            raise ValidationError("You can select a maximum of 4 tags.")


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'author', 'get_total_rating')

    def get_total_rating(self, obj):
        likes_count = obj.likes.count()
        dislikes_count = obj.dislikes.count()
        return likes_count - dislikes_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(total_rating=Count('likes') - Count('dislikes'))
        return queryset

    get_total_rating.short_description = 'Total Rating'
    get_total_rating.admin_order_field = 'total_rating'  # Enable ordering by total_rating field

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Existing object, display total_rating as read-only
            return self.readonly_fields + ('get_total_rating',)  # Add get_total_rating to readonly_fields
        return self.readonly_fields


class CommentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ['likes', 'dislikes']


class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm
    list_display = ('toPost', 'commentAuthor', 'commentBody', 'get_total_rating')

    def get_total_rating(self, obj):
        likes_count = obj.likes.count()
        dislikes_count = obj.dislikes.count()
        return likes_count - dislikes_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(total_rating=Count('likes') - Count('dislikes'))
        return queryset

    get_total_rating.short_description = 'Total Rating'
    get_total_rating.admin_order_field = 'total_rating'  # Enable ordering by total_rating field

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Existing object, display total_rating as read-only
            return self.readonly_fields + ('get_total_rating',)  # Add get_total_rating to readonly_fields
        return self.readonly_fields
