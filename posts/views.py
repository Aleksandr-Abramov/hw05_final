from django.shortcuts import render, redirect, reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post
from .models import Group
from .models import User
from .models import Follow

from .forms import PostForm
from .forms import CommentForm


def index(request):
    """Главная страница Index"""
    post_list = Post.objects.select_related("group")
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator
    }
    return render(request, "index.html", context)


def group_posts(request, slug):
    """Страница записей сообщества group_post"""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    """Страница создание поста new"""
    if request.method != "POST":
        form = PostForm()
        context = {
            "form": form
        }
        return render(request, "add_or_change_post.html", context)

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, "add_or_change_post.html")


def profile(request, username):
    """Профайл пользователя User and Post"""
    following = False
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=user).exists():
            following = True
    posts = user.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "author": user,
        "page": page,
        "paginator": paginator,
        "following": following,

    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    """Просмотр записи Post"""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author_posts = post.author
    comments = post.comments.all()
    form = CommentForm()
    context = {
        "author": author_posts,
        "post": post,
        "form": form,
        "comments": comments
    }
    return render(request, "post.html", context)


@login_required
def post_edit(request, username, post_id):
    """Страница редактирования поста post_edit"""
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)

    if request.user != profile:
        return redirect('post', username=username, post_id=post_id)

    if request.method != "POST":
        form = PostForm(instance=post)
        context = {
            "form": form,
            "is_edit": True,
            "post": post
        }
        return render(request, 'add_or_change_post.html', context)

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("post", username=request.user.username, post_id=post_id)


@login_required()
def add_comment(request, username, post_id):
    """Добовление комментарив"""
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if request.GET or not form.is_valid():
        return render(request, 'post.html', {'post': post_id})

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()
    return redirect(reverse('post', kwargs={'username': username,
                                            'post_id': post_id}))


@login_required
def follow_index(request):
    """Страница с избранными авторами follow.html"""
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    """Функция подписки на автора"""
    author = get_object_or_404(User, username=username)
    if request.user != author and not Follow.objects.filter(
            user=request.user, author=author).exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Функция отписки от автора"""
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    """Страница ошибки 404"""
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    """Страница ошибки 500"""
    return render(request, "misc/500.html", status=500)
