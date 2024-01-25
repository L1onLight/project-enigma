import random
from datetime import timedelta
import validators
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import F, Count
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone

from apps.notifications.models import PasswordRestore
from apps.posts.models import Post, Tag, Comment
from apps.user.models import CustomUser
from .decorators import *
from ..notifications.views import password_restore_email

PAGINATION_N = 10

EXAMPLE_USER = {
    "email": "example@mail.com",
    "password": "qwerty1"
}


# Create your views here.

def home(request):
    all_posts = Post.objects.all()
    if request.GET.get('sortby'):
        # all_posts = all_posts.order_by(request.GET.get('sortby'))
        all_posts = all_posts.annotate(likes_count=Count('likes', distinct=True),
                                       dislikes_count=Count('dislikes', distinct=True)).annotate(
            rating=F('likes_count') - F('dislikes_count')).order_by(request.GET.get('sortby'))

    p = Paginator(all_posts, PAGINATION_N)
    page = request.GET.get('page')
    posts = p.get_page(page)

    if request.GET.get('sortby'):
        sort = request.GET.get('sortby') if not None else ''
    else:
        sort = None
    context = {'posts': posts, "paginator": p,
               'pn': PAGINATION_N, 'sort': sort}
    return render(request, 'core/index.html', context)


def post_view(request, pk):
    post = Post.objects.get(pk=pk)

    if request.method == "POST":
        if request.user.is_authenticated:
            body = request.POST.get('messageBody')
            new_comment = Comment(
                toPost=post, commentAuthor=request.user, commentBody=body)
            new_comment.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    comment_list = Comment.objects.filter(toPost=post)
    p = Paginator(comment_list, PAGINATION_N)
    page = request.GET.get('page')
    comment_list = p.get_page(page)
    context = {'post': post, "comments": comment_list,
               'pn': PAGINATION_N, 'paginator': p}
    return render(request, 'core/post.html', context)


def search(request):
    all_posts = Post.objects.all()
    print(request.build_absolute_uri())
    if request.GET.get('sortby'):
        all_posts = all_posts.annotate(likes_count=Count('likes', distinct=True),
                                       dislikes_count=Count('dislikes', distinct=True)).annotate(
            rating=F('likes_count') - F('dislikes_count')).order_by(request.GET.get('sortby'))

    tag_q = ''
    tags = request.GET.get('tags').split(
        '|') if not request.GET.get('tags') is None else None
    if tags and tags != ['']:
        for tag in tags:
            all_posts = all_posts.filter(tagList__tagTitle=tag)
            tag_q += f"{all_posts}|"
    author_body_name = request.GET.get('q') if not '' else None
    if author_body_name:
        all_posts = all_posts.filter(
            Q(author__email__icontains=author_body_name) | Q(author__username__icontains=author_body_name) | Q(
                body__icontains=author_body_name) | Q(title__icontains=author_body_name)).distinct()

    p = Paginator(all_posts, PAGINATION_N)
    page = request.GET.get('page')
    posts = p.get_page(page)

    sort = request.GET.get('sortby') if not '' else None

    context = {'posts': posts, "paginator": p, 'pn': PAGINATION_N, 'sort': sort, 'tag_q': tag_q,
               'abn': author_body_name}
    return render(request, 'core/search.html', context)


@login_required_my
def create_post(request):
    if request.method == 'POST':
        img = request.FILES.get('postImage')
        title = request.POST.get('postTitle')
        body = request.POST.get('postBody')
        tags = request.POST.getlist('tags')

        if img and title and body:
            np = Post(title=title, author=request.user,
                      body=body, postImage=img, )
            np.save()
            if tags:
                for tag in tags:
                    new_tag, created = Tag.objects.get_or_create(tagTitle=tag)
                    if created:
                        new_tag.save()
                    np.tagList.add(new_tag)
            return redirect('post', pk=np.id)
        else:
            if not img:
                messages.error(request, 'You should choose image.')
            if not title:
                messages.error(request, 'Title cannot be empty.')
            if not body:
                messages.error(request, 'Body cannot be empty.')
    return render(request, 'core/create_post.html')


def user_profile(request, pk):
    try:
        pn = 5
        user = CustomUser.objects.get(pk=pk)
        posts = Post.objects.filter(author=user)
        print(posts)
        p = Paginator(posts, pn)
        page = request.GET.get('page')
        posts = p.get_page(page)

    except CustomUser.DoesNotExist:
        return redirect('home')
    context = {'user': user, 'posts': posts, "paginator": p, 'pn': pn, }
    return render(request, 'core/profile.html', context)


@login_required_my
def edit_profile(request):
    if request.method == 'POST':
        user = CustomUser.objects.get(id=request.user.id)
        error = False
        if request.FILES.get('avatar'):
            user.avatar = request.FILES.get('avatar')
        if request.POST.get('first_name'):
            user.first_name = request.POST.get('first_name')
        if request.POST.get('last_name'):
            user.last_name = request.POST.get('last_name')
        if request.POST.get('email'):
            user.email = request.POST.get('email')
        if request.POST.get('username'):
            user.username = request.POST.get('username')
        if request.POST.get('instagram_url'):
            if validators.url(request.POST.get('instagram_url')):
                user.inst_url = request.POST.get('instagram_url')
            else:
                error = True
                messages.error('Enter valid url.')
        if request.POST.get('steam_url'):
            if validators.url(request.POST.get('steam_url')):
                user.steam_url = request.POST.get('steam_url')
            else:
                error = True
                messages.error('Enter valid url.')
        if request.POST.get('telegram_url'):
            if validators.url(request.POST.get('telegram_url')):
                user.telegram_url = request.POST.get('telegram_url')
            else:
                error = True
                messages.error('Enter valid url.')
        if request.POST.get('body'):
            user.bio = request.POST.get('body')
        try:

            user.save()
        except IntegrityError as e:
            e = str(e)
            if 'username' in e:
                messages.error(request, 'This username already taken')
            if 'email' in e:
                messages.error(request, 'This email already taken')

            return render(request, 'core/edit-profile.html')
        if error:
            return render(request, 'core/edit-profile.html')
        return redirect('user_profile', pk=request.user.id)
    return render(request, 'core/edit-profile.html')


def post_like(request, pk, method):
    if not request.user.is_authenticated:
        return HttpResponse('/login/')

    post = Post.objects.get(pk=pk)
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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required_my
def comment_like(request, pk, method):
    comment = Comment.objects.get(pk=pk)
    if method == 'like':
        if comment.dislikes.all().filter(email=request.user.email):
            comment.dislikes.remove(request.user)
        if comment.likes.all().filter(email=request.user.email):
            comment.likes.remove(request.user)
        else:
            comment.likes.add(request.user)
        comment.save()
    elif method == 'dislike':
        if comment.likes.all().filter(email=request.user.email):
            comment.likes.remove(request.user)
        if comment.dislikes.all().filter(email=request.user.email):
            comment.dislikes.remove(request.user)
        else:
            comment.dislikes.add(request.user)
        comment.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def log_out(request):
    auth.logout(request)
    return redirect('home')


def restore_password(request):
    if request.method == 'POST' and "?code" in request.build_absolute_uri():
        r_email = request.POST.get('restoreEmail')
        r_code = request.POST.get('restoreCode')
        r_password = request.POST.get('restorePassword')
        try:
            pr = PasswordRestore.objects.get(user__email=r_email)
            current_datetime = timezone.now()
            model_datetime = pr.created_or_changed
            if current_datetime > model_datetime + timedelta(minutes=1):
                pr.delete()
                messages.error(request, 'Code expired.')
            else:
                if r_code == str(pr.restoreCode):
                    user = CustomUser.objects.get(email=r_email)
                    user.password = make_password(r_password)
                    user.save()
                    auth.login(request, user=user)
                    return redirect('home')
                else:
                    messages.error(request, 'Wrong code.')
        except PasswordRestore.DoesNotExist:
            messages.error(request, 'Wrong code.')
            pass

    if request.method == 'POST' and '?code' not in request.build_absolute_uri():
        email_ = request.POST.get('email')

        try:
            user = CustomUser.objects.get(email=email_)
            code = random.randrange(1000000, 10000000)

            try:
                pr = PasswordRestore.objects.get(user=user)
                pr.restoreCode = code
                pr.save()
            except Exception as e:
                print(e)
                pr = PasswordRestore(user=user, restoreCode=code)
                pr.save()
            print(f"Code: {code}")
            password_restore_email(
                request, receiver_email=email_, code=code, url=request.build_absolute_uri('?code'))

            messages.success(request, 'Check your email.')

        except CustomUser.DoesNotExist:
            # # Here you can change error message to check your email if
            # # you want to hide information about email from user.
            # messages.error(request, 'Check your email.') # To hide email info

            messages.error(request, 'User does not exist.')
    return render(request, 'core/password_restore.html')


@logout_required
def log_in(request):
    # # # Only for testing # TODO Remove
    try:
        CustomUser.objects.get(email=EXAMPLE_USER.get("email"))
    except CustomUser.DoesNotExist:
        example_password = make_password(EXAMPLE_USER["password"])

        CustomUser.objects.create(email=EXAMPLE_USER.get("email"),
                                  password=example_password)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(request, email=email, password=password)
        if user:
            auth.login(request, user=user)
            return redirect('home')
        else:
            messages.error(request, 'Wrong email or password.')

    return render(request, 'core/login.html')


@logout_required
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user_exist_or_not = CustomUser.objects.get(email=email)
            messages.error(request, 'User already exists.')
        except CustomUser.DoesNotExist:
            password = make_password(request.POST.get('password'))

            nu = CustomUser.objects.create(email=email, password=password)
            auth.login(request, nu)
            return redirect('home')
    return render(request, 'core/signup.html')
