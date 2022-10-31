from tabnanny import verbose
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )


    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertAlmostEqual(self.group.title, 'Тестовая группа')
        self.assertAlmostEqual(self.group.slug, 'Тестовый слаг')
        self.assertAlmostEqual(self.group.description, 'Тестовое описание')
        
    def test_models_have_correct_verbose_name_and_helptext(self):
        """Проверяем, что у моделей корректно работает verbose_name и helptext"""
        self.assertAlmostEqual(self.post._meta.get_field('author').verbose_name, 'Author')
        self.assertAlmostEqual(self.post._meta.get_field('author').help_text, 'Автор')