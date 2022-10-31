from enum import auto
from tokenize import group
from django.urls import reverse
from http import HTTPStatus
from urllib import response
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from random import random

from ..models import Group, Post

User = get_user_model()

class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username="TestUser")
        Group.objects.create(
            title = 'Тестовый заголовок',
            description = 'Тестовый текст',
            slug = 'test-slug',
        )
        Group.objects.create(
            title = 'Тестовый заголовок 2',
            description = 'Тестовый текст 2',
            slug = 'test-slug-2',
        )
        for post in range(50):
            try:
                group_id = str(Group.objects.get(pk=random(Group.objects.count())))
            except:
                group_id = ''
            Post.objects.create(
                text = 'testtext'+str(post),
                author = User.objects.get(username='TestUser'),
                group_id = group_id
            )
        #отдельно "свежий" пост чтобы попал на первую страницу
        Post.objects.create(
            id = 100,
            text = 'TEST TEXTTEST TEXTTEST TEXTTEST TEXT',
            author = User.objects.get(username='TestUser'),
            group = Group.objects.get(slug='test-slug'),
        )
    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(User.objects.get(username='TestUser'))
    
    def test_templates_view_auth(self):
        """(авторизован)Проверяюем, что во view-функциях используются правильные html-шаблоны."""
        Templates_Reverse = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': 'TestUser'}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={'post_id': '100'}),
            'posts/create_post.html': reverse('posts:post_edit', kwargs={'post_id': '100'}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_view in Templates_Reverse.items():
            with self.subTest(address=reverse_view):
                response = self.authorized_client.get(reverse_view)
                self.assertTemplateUsed(response, template)


    def test_templates_view_guest(self):
        """(неавторизован)Проверяюем, что во view-функциях используются правильные html-шаблоны."""
        Templates_Reverse = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': 'TestUser'}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={'post_id': '100'}),
        }
        for template, reverse_view in Templates_Reverse.items():
            with self.subTest(address=reverse_view):
                response = self.guest_client.get(reverse_view)
                self.assertTemplateUsed(response, template)

    def test_post_create_index(self):
        """Проверяем, что если при создании поста указать группу, то этот пост появляется на главной"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, Post.objects.get(id=100).text)
    
    def test_post_create_group(self):
        """Проверяем, что если при создании поста указать группу, то этот пост появляется на странице группы"""
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        self.assertContains(response, Post.objects.get(id=100).text)
    
    def test_post_create_profile(self):
        """Проверяем, что если при создании поста указать группу, то этот пост появляется в профайле"""
        response = self.authorized_client.get(reverse('posts:profile', kwargs={'username': 'TestUser'}))
        self.assertContains(response, Post.objects.get(id=100).text)
    
    def test_post_create_no_other_group(self):
        """Пост не попал в группу, для которой не был предназначен."""
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': 'test-slug-2'}))
        self.assertNotContains(response, Post.objects.get(id=100).text)
    


    def test_template_context(self):
        """Провеяем, соответствует ли ожиданиям словарь context, передаваемый в шаблон при вызове."""
        pass

 
