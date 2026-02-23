# apps/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('reader', 'Читатель'),
        ('expert', 'Эксперт (может писать в блог)'),
        ('editor', 'Редактор (может править wiki)'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')

    # Профиль
    bio = models.TextField(blank=True, help_text="О себе")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    website = models.URLField(blank=True)


    def can_edit_wiki(self):
        return self.role in ['editor', 'admin']

    def can_write_blog(self):
        return self.role in ['expert', 'editor', 'admin']