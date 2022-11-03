from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class ViewTests(TestCase):
    def generate_test_posts(count: int, author: str):
        postlist = []
        for i in range(count):
            if i % 2 == 0:
                post = Post(
                    text=(f'Тестовый текст №{i}'),
                    group=Group.objects.order_by('?').first(),
                    author=User.objects.get(username=author),
                )
            else:
                post = Post(
                    text=(f'Тестовый текст №{i}'),
                    author=User.objects.get(username=author),
                )
            postlist.append(post)
        Post.objects.bulk_create(postlist)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.testuser = User.objects.create_user(username="TestUser")

        cls.group1 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок 2',
            description='Тестовый текст 2',
            slug='test-slug-2',
        )

        cls.generate_test_posts(200, cls.testuser.username)
        cls.test_post_user_last = Post.objects.order_by('-pub_date').first()

        cls.TEMPLATES_FOR_VIEWS_AUTH = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group1.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.testuser.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': cls.test_post_user_last.pk
                }
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': cls.test_post_user_last.pk
                }
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        cls.TEMPLATES_FOR_VIEWS_GUEST = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': cls.group1.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': cls.testuser.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={
                    'post_id': cls.test_post_user_last.pk
                }
            ),
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            User.objects.get(username='TestUser')
        )

    def test_templates_view_auth(self):
        """(авторизован)Во view-функциях используются правильные шаблоны."""
        for reverse_view, template in self.TEMPLATES_FOR_VIEWS_AUTH.items():
            with self.subTest(address=reverse_view):
                response = self.authorized_client.get(reverse_view)
                self.assertTemplateUsed(response, template)

    def test_templates_view_guest(self):
        """(неавторизован)Во view-функциях используются правильные шаблоны."""
        for template, reverse_view in self.TEMPLATES_FOR_VIEWS_GUEST.items():
            with self.subTest(address=reverse_view):
                response = self.guest_client.get(reverse_view)
                self.assertTemplateUsed(response, template)

    def test_post_create_index(self):
        """Если при создании поста указать группу, то появляется на главной"""
        post_with_group = Post.objects.create(
            text='тестовый пост для test_post_create_index',
            group=Group.objects.first(),
            author=self.testuser,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, post_with_group.text)

    def test_post_create_group(self):
        """Если при создании поста указать группу,
        то этот пост появляется на странице группы"""
        post_with_group = Post.objects.create(
            text='тестовый пост для test_post_create_group',
            group=Group.objects.first(),
            author=self.testuser,
        )
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': post_with_group.group.slug}
            )
        )
        self.assertContains(response, post_with_group.text)

    def test_post_create_profile(self):
        """Если при создании поста указать группу,
        то этот пост появляется в профайле"""
        post_with_group = Post.objects.create(
            text='тестовый пост для test_post_create_profile',
            group=Group.objects.first(),
            author=self.testuser,
        )
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.testuser.username}
            )
        )
        self.assertContains(response, post_with_group.text)

    def test_post_create_no_other_group(self):
        """Пост не попал в группу, для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-2'})
        )
        self.assertNotContains(response, Post.objects.get(id=100).text)

    def test_paginator(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
