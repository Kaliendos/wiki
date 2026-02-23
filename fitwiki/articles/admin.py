from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import WikiArticle, Category, SubCategory, BlogArticle, Tag


admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(BlogArticle)
admin.site.register(Tag)

from django.contrib import admin
from .models import WikiArticle

from django.contrib import admin
from .models import WikiArticle


@admin.register(WikiArticle)
class WikiArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'created_at']
    list_filter = ['is_published', 'category', 'subcategory']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    readonly_fields = ['views', 'created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'content')
        }),
        ('Категоризация', {
            'fields': ('category', 'subcategory', 'tags')
        }),
        ('Автор и статус', {
            'fields': ('author', 'is_published', 'published_at')
        }),
        ('Статистика', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)