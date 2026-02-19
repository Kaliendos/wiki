from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.main_page),
    path('subcategory/<slug:slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
]