from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_summernote.fields import SummernoteTextField
from markdownx.models import MarkdownxField

User = get_user_model()


class Category(models.Model):
    """Категории статей (Тренировки, Питание, Добавки...)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """Категории статей (Тренировки, Питание, Добавки...)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Теги для статей"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class WikiArticle(models.Model):
    """Статья в базе знаний"""
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    content = RichTextUploadingField(blank=True, null=True)  # с загрузкой изображений

    # Метаданные
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, related_name="article")
    tags = models.ManyToManyField(Tag, blank=True)

    # Автор и даты
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Статус
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    # Статистика
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('wiki:detail', args=[self.slug])


class BlogArticle(models.Model):
    """Авторская статья (блог)"""
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    content = SummernoteTextField()

    # Связи
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    related_wiki = models.ManyToManyField(WikiArticle, blank=True,
                                          help_text="Связанные статьи из wiki")

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    views = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('detail', args=[self.slug])


class ArticleBlogImage(models.Model):
    """Изображения для статьи"""
    article = models.ForeignKey(BlogArticle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='articles/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.article.title}"

# apps/comments/models.py
class Comment(models.Model):
    """Универсальные комментарии для любой модели"""
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    # Generic Foreign Key (может привязываться к WikiArticle, BlogArticle и т.д.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.created_at}'
