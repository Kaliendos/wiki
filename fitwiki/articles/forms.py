# blogs/forms.py
from django import forms
from django_summernote.widgets import SummernoteWidget
from .models import BlogArticle

class BlogArticleForm(forms.ModelForm):
    class Meta:
        model = BlogArticle
        fields = ['title', 'content', 'related_wiki', 'is_published']
        widgets = {
            'content': SummernoteWidget(),
        }