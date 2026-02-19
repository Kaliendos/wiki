from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import WikiArticle, Category, Comment, SubCategory


class ArticleListView(ListView):
    model = WikiArticle
    template_name = 'wiki/list.html'
    context_object_name = 'articles'
    paginate_by = 20

    def get_queryset(self):
        queryset = WikiArticle.objects.filter(is_published=True)

        # Фильтр по категории
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset.select_related('category', 'author')


def subcategory_detail(request, slug):
    subcategory = get_object_or_404(SubCategory, slug=slug)
    articles = WikiArticle.objects.filter(subcategory=subcategory)
    return render(request, 'subcategory_detail.html', {'subcategory': subcategory, 'articles': articles})

class ArticleDetailView(DetailView):
    model = WikiArticle
    template_name = 'wiki/detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        return WikiArticle.objects.filter(is_published=True)

    def get_object(self):
        obj = super().get_object()
        # Увеличиваем счетчик просмотров
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем комментарии к этой статье
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(self.object)
        context['comments'] = Comment.objects.filter(
            content_type=content_type,
            object_id=self.object.id,
            parent=None
        ).select_related('author')

        return context


def main_page(request):
    categories = Category.objects.prefetch_related("subcategories")
    articles = WikiArticle.objects.order_by('-views')[:20]
    for category in categories:
        for subcategory in category.subcategories.all():
            print(f"  - {subcategory.name}")
    return render(
        request=request,
        template_name="main.html", context={"categories": categories, "articles": articles}
    )
