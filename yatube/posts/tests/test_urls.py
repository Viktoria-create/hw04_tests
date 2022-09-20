from django.test import Client, TestCase
from http import HTTPStatus
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    """"Создание двух пользователей (авторизованного и не авторизованного)
        Создание тестового поста и группы"""
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовое описание поста')
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание')

    def test_urls_guest_client(self):
        """Доступ неавторизованного пользователя"""
        pages: tuple = ('/',
                        f'/group/{self.group.slug}/',
                        f'/profile/{self.user.username}/',
                        f'/posts/{self.post.id}/')
        for page in pages:
            response = self.guest_client.get(page)
            error_name = f'Ошибка: нет доступа к странице {page}'
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_urls_redirect_guest_client(self):
        """Редирект неавторизованного пользователя"""
        url1 = '/auth/login/?next=/create/'
        url2 = f'/auth/login/?next=/posts/{self.post.id}/edit/'
        pages = {'/create/': url1, f'/posts/{self.post.id}/edit/': url2}
    # Проверяем редирект каждой страницы методом assertRedirects
        for page, value in pages.items():
            response = self.guest_client.get(page)
            self.assertRedirects(response, value)

    def test_reddirect_guest_client(self):
        """Проверка редиректа неавторизованного пользователя."""
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        form_data = {'text': 'Текст записанный в форму'}
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_urls_uses_correct_template_authorized_client(self):
        """URL-адрес использует соответствующий шаблон."""
        """Доступ авторизованного пользователя"""
        templates_url_names: dict = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html'}
        page: tuple = ('/create/',
                       f'/posts/{self.post.id}/edit/')
        # Проверка полученой страницы методом assertTemplateUsed.
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                error_name = f'Ошибка: нет доступа к странице {page}'
                error_name = f'Ошибка: {adress} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)
