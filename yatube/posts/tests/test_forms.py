from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class PostFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='Описание')

    def test_create_post(self):
        """Проверка создания поста."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        error_name1 = 'Данные поста не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        text='Текст записанный в форму',
                        group=self.group.id,
                        author=self.user
                        ).exists(), error_name1)
        error_name2 = 'Поcт не добавлен в базу данных'
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         error_name2)

    def test_group_null(self):
        """Проверка что группу можно не указывать."""
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        old_text = self.post
        form_data = {'text': 'Текст записанный в форму',
                     'group': ''}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name2 = 'Пользователь не может оставить поле нулевым'
        self.assertNotEqual(old_text.group, form_data['group'], error_name2)

    def test_can_edit_post(self):
        """Проверка прав редактирования"""
        old_text = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group
            )
        group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_group',
            description='Описание'
            )
        form_data = {
            'text': 'Текст записанный в форму',
            'group': group2.id
            }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True
            )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': old_text.id}),
            )
        self.assertTrue(
            Post.objects.filter(
            text=form_data['text'],
            group=group2.id,
            ).exists(),
            f'Не найдена тестовая запись {form_data ["text"]} в БД'
            )
        # не авторизованный пользователь не может изменить содержание поста'
        form_data = {
            'text': 'Неавторизованный текст записанный в форму',
            'group': group2.id
            }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text.id}),
            data=form_data,
            follow=True
            )
        self.assertRedirects(
            response,
            '/auth/login/?next=/posts/1/edit/'
            )
        self.assertFalse(
            Post.objects.filter(
            text=form_data['text'],        
            group=group2.id,
            ).exists(),
            f'записи {form_data ["text"]} в БД быть не должно'
            )

    def test_no_edit_post(self):
        """Проверка запрета добавления поста в базу данных
           не авторизованого пользователя."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.guest_client.post(reverse('posts:post_create'),
                                          data=form_data,
                                          follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name2 = 'Поcт добавлен в базу данных по ошибке'
        self.assertNotEqual(Post.objects.count(),
                            posts_count + 1,
                            error_name2)
