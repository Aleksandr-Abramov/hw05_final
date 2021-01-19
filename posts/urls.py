from django.urls import path

from . import views

urlpatterns = [
    # Функция отписки от автора
    path("follow/", views.follow_index, name="follow_index"),
    # гвавная страница
    path("", views.index, name="index"),
    # страница группы
    path("group/<slug:slug>/", views.group_posts, name="group_post"),
    # страница с формой добовления поста
    path("new/", views.new_post, name="new_post"),
    # Профайл пользователя
    path('<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    # Страница редактирования поста
    path('<str:username>/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Комментарии
    path("<str:username>/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    # Страница с избранными авторами follow.html
    path("<str:username>/follow/", views.profile_follow, name="profile_follow"),
    # Функция подписки на автора
    path("<str:username>/unfollow/", views.profile_unfollow, name="profile_unfollow"),
    path('404/', views.page_not_found, name="page404"),
    path('500/', views.server_error, name="page500")
]
