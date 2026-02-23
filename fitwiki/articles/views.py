from django.http import JsonResponse

from .models import WikiArticle, Category
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Count, Q
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid

from django.contrib import messages

from .models import BlogArticle, Comment




def get_article_by_slug(request, slug):
    template_name = 'wiki/detail.html'
    article = get_object_or_404(WikiArticle, slug=slug)

    # Увеличиваем счетчик просмотров
    article.views += 1
    article.save(update_fields=['views'])

    return render(
        request=request,
        template_name=template_name,
        context={
            "article": article,
            "articles": WikiArticle.objects.all()
        }
    )




def main_page(request):
    categories = Category.objects.all()
    articles = WikiArticle.objects.order_by('-views')[:20]

    return render(
        request=request,
        template_name="wiki/main.html",
        context={"categories": categories, "articles": articles}
    )



from django.contrib.auth import get_user_model

User = get_user_model()


class BlogArticleListView(ListView):
    """Список всех опубликованных статей"""
    model = BlogArticle
    template_name = 'blogs/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = BlogArticle.objects.filter(is_published=True)
        print(queryset, "<<<<")
        # Поиск по заголовку и содержанию
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        # Сортировка
        sort_by = self.request.GET.get('sort', '-published_at')
        if sort_by in ['-published_at', 'published_at', '-views', 'views', '-created_at']:
            queryset = queryset.order_by(sort_by)
        return queryset.select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['current_sort'] = self.request.GET.get('sort', '-published_at')

        # Популярные статьи (по просмотрам за последние 30 дней)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        context['popular_articles'] = BlogArticle.objects.filter(
            is_published=True,
            published_at__gte=thirty_days_ago
        ).order_by('-views')[:5]

        # Топ авторов

        return context


class BlogArticleDetailView(DetailView):
    """Детальная страница статьи"""
    model = BlogArticle
    template_name = 'blogs/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        # Если пользователь не автор, показываем только опубликованные
        if not self.request.user.is_staff:
            return BlogArticle.objects.filter(is_published=True)
        return BlogArticle.objects.all()

    def get(self, request, *args, **kwargs):
        # Увеличиваем счетчик просмотров
        response = super().get(request, *args, **kwargs)

        if not request.user.is_staff or request.user != self.object.author:
            BlogArticle.objects.filter(pk=self.object.pk).update(views=self.object.views + 1)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем комментарии к статье
        content_type = ContentType.objects.get_for_model(BlogArticle)

        # Получаем все активные комментарии для этой статьи
        all_comments = Comment.objects.filter(
            content_type=content_type,
            object_id=self.object.pk,
            is_active=True
        ).select_related('author').order_by('created_at')

        # Строим дерево комментариев
        comment_tree = {}
        for comment in all_comments:
            if comment.parent_id not in comment_tree:
                comment_tree[comment.parent_id] = []
            comment_tree[comment.parent_id].append(comment)

        # Получаем корневые комментарии (без родителя)
        root_comments = comment_tree.get(None, [])

        # Для каждого корневого комментария добавляем его ответы
        for comment in root_comments:
            comment.replies = comment_tree.get(comment.id, [])

        context['comments'] = root_comments

        # Похожие статьи (по связанным wiki-статьям или автору)
        # if self.object.related_wiki.exists():
        #     similar = BlogArticle.objects.filter(
        #         is_published=True,
        #         related_wiki__in=self.object.related_wiki.all()
        #     ).exclude(pk=self.object.pk).distinct()[:3]
        # else:
        #     similar = BlogArticle.objects.filter(
        #         is_published=True,
        #         author=self.object.author
        #     ).exclude(pk=self.object.pk)[:3]
        #
        # context['similar_articles'] = similar

        return context


class BlogArticleCreateView(LoginRequiredMixin, CreateView):
    """Создание новой статьи"""
    model = BlogArticle
    template_name = 'blogs/article_form.html'
    fields = ['title', 'content', 'related_wiki', 'is_published']

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.is_published:
            form.instance.published_at = timezone.now()
        return super().form_valid(form)


class BlogArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование статьи"""
    model = BlogArticle
    template_name = 'blogs/article_form.html'
    fields = ['title', 'content', 'related_wiki', 'is_published']

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff

    def form_valid(self, form):
        if form.instance.is_published and not form.instance.published_at:
            form.instance.published_at = timezone.now()
        return super().form_valid(form)


class BlogArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление статьи"""
    model = BlogArticle
    template_name = 'blogs/article_confirm_delete.html'
    success_url = reverse_lazy('blogs:list')

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff


class AuthorArticleListView(ListView):
    """Список статей конкретного автора"""
    model = BlogArticle
    template_name = 'blogs/author_articles.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])

        # Если это автор или админ, показываем все статьи, иначе только опубликованные
        if self.request.user == self.author or self.request.user.is_staff:
            queryset = BlogArticle.objects.filter(author=self.author)
        else:
            queryset = BlogArticle.objects.filter(author=self.author, is_published=True)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context


@login_required
def addCommentView(request, slug):
    """Добавление комментария к статье"""
    article = get_object_or_404(BlogArticle, slug=slug)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            content_type = ContentType.objects.get_for_model(BlogArticle)

            comment = Comment.objects.create(
                author=request.user,
                content=content,
                content_type=content_type,
                object_id=article.pk
            )

            messages.success(request, 'Комментарий успешно добавлен!')

    return redirect('detail', slug=slug)


@login_required
def addReplyView(request, comment_id):
    """Ответ на комментарий"""
    parent_comment = get_object_or_404(Comment, pk=comment_id, is_active=True)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            reply = Comment.objects.create(
                author=request.user,
                content=content,
                content_type=parent_comment.content_type,
                object_id=parent_comment.object_id,
                parent=parent_comment
            )
            reply.save()

            messages.success(request, 'Ответ успешно добавлен!')

    # Возвращаем на страницу статьи
    if parent_comment.content_type.model == 'blogarticle':
        article = BlogArticle.objects.get(pk=parent_comment.object_id)
        return redirect('detail', slug=article.slug)

    return redirect('home')


@login_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        # Генерируем уникальное имя файла
        ext = file.name.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        # Сохраняем файл
        path = default_storage.save(f'uploads/articles/{filename}', ContentFile(file.read()))
        file_url = default_storage.url(path)

        return JsonResponse({
            'url': file_url,
            'filename': filename
        })

    return JsonResponse({'error': 'No file uploaded'}, status=400)

@login_required
def deleteCommentView(request, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user == comment.author or request.user.is_staff:
        comment.is_active = False
        comment.save()
        messages.success(request, 'Комментарий удален')

    # Возвращаем на страницу статьи
    if comment.content_type.model == 'blogarticle':
        article = BlogArticle.objects.get(pk=comment.object_id)
        return redirect('detail', slug=article.slug)

    return redirect('home')
