from django.contrib import admin
from django.urls import path, include

from . import views
namespace = "wiki"

urlpatterns = [
    path("", views.main_page, name='home'),
    #path('subcategory/<slug:slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('article/<slug:slug>/', views.get_article_by_slug, name='article_detail'),
    path('', views.BlogArticleListView.as_view(), name='list'),

    path('blog/', views.BlogArticleListView.as_view(), name='list'),
    path('blog/article/<slug:slug>/', views.BlogArticleDetailView.as_view(), name='detail'),


    # Создание статьи
    path('blog/create/', views.BlogArticleCreateView.as_view(), name='create'),

    # Редактирование статьи
    path('blog/article/<slug:slug>/edit/', views.BlogArticleUpdateView.as_view(), name='edit'),

    # Удаление статьи
    path('blog/article/<slug:slug>/delete/', views.BlogArticleDeleteView.as_view(), name='delete'),

    # Статьи автора
    path('author/<str:username>/', views.AuthorArticleListView.as_view(), name='author_articles'),

    # Комментарии
    path('blog/article/<slug:slug>/comment/', views.addCommentView, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.deleteCommentView, name='delete_comment'),
    path('comment/<int:comment_id>/reply/', views.addReplyView, name='add_reply'),
    path('upload-image/', views.upload_image, name='upload_image'),
]