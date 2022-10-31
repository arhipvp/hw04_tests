from http import HTTPStatus
from urllib import response
from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """Отправляем запрос через client, созданный в setUp()"""
        response = self.guest_client.get('/')  
        self.assertEqual(response.status_code, 200)

class UrlAndTemplateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='TestUser')
        Group.objects.create(
            title = 'Тестовый заголовок',
            description = 'Тестовый текст',
            slug = 'test-slug',
        )
        Post.objects.create(
            id = 100,
            text = 'Тестовый текст поста',
            author = User.objects.get(username='TestUser'),
            group = Group.objects.get(slug='test-slug'),
        )
    
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='AuthUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_user = Client()
        self.author_user.force_login(User.objects.get(username='TestUser'))

    def test_HTTPStatus_and_Template_URL_public(self):
        """Проверяем доступность и соответствие шаблонов к URL """
        Templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/TestUser/',
            'posts/post_detail.html': '/posts/100/',
        }
        for template, address in Templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertAlmostEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)
    
    def test_redirect_from_privat(self):
        "Проверяем редирект при редактировании чужих постов (пользователь авторизован)"
        Redirect_url = {
            '/posts/100/edit/': '/posts/100/'
        }
        for adress, readress in Redirect_url.items():
            response = self.authorized_client.get(adress)
            self.assertRedirects(response, readress)
            
    def test_edit_own_post(self):
        "Проверяем доступность своих страниц"
        Post_autrhpr_url = (
            '/posts/100/edit/',
        )
        for adress in Post_autrhpr_url:
            response = self.author_user.get(adress)
            self.assertAlmostEqual(response.status_code, HTTPStatus.OK)
