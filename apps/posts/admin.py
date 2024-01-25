from django.contrib import admin
from .models import *
from .forms import PostAdmin, CommentAdmin

# Register your models here.

# admin.site.register(Post)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
