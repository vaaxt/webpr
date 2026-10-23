from io import BytesIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class AccountViewsTests(TestCase):
    def test_signup_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse('signup'),
            {
                'username': 'new-user',
                'password1': 'Example-password-384!',
                'password2': 'Example-password-384!',
            },
        )

        self.assertRedirects(response, reverse('login'))
        user = get_user_model().objects.get(username='new-user')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_new_users_automatically_get_a_profile(self):
        user = get_user_model().objects.create_user(username='profile-owner')

        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_login_and_post_logout(self):
        user = get_user_model().objects.create_user(
            username='existing-user',
            password='Example-password-384!',
        )
        response = self.client.post(
            reverse('login'),
            {'username': user.username, 'password': 'Example-password-384!'},
        )
        self.assertRedirects(response, reverse('events:event_list'))

        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('events:event_list'))

    def test_logout_rejects_get(self):
        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 405)

    def test_event_creation_requires_login(self):
        response = self.client.get(reverse('events:event_create'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('events:event_create')}",
        )

    def test_navigation_shows_account_links_based_on_authentication(self):
        response = self.client.get(reverse('events:event_list'))
        self.assertContains(response, reverse('login'))
        self.assertContains(response, reverse('signup'))
        self.assertContains(response, 'Мой профиль')
        self.assertContains(
            response,
            f'href="{reverse("login")}?next={reverse("profile")}"',
        )

        user = get_user_model().objects.create_user(
            username='existing-user',
            password='Example-password-384!',
        )
        self.client.force_login(user)
        response = self.client.get(reverse('events:event_list'))
        self.assertContains(response, user.username)
        self.assertContains(response, reverse('logout'))
        self.assertNotContains(response, 'Sign up')

    def test_profile_pages_require_authentication(self):
        for name in ('profile', 'profile_edit'):
            response = self.client.get(reverse(name))
            self.assertRedirects(
                response,
                f"{reverse('login')}?next={reverse(name)}",
            )

    def test_navigation_name_links_to_own_profile(self):
        user = get_user_model().objects.create_user(
            username='profile-owner',
            first_name='Ada',
            last_name='Lovelace',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('events:event_list'))

        self.assertContains(
            response,
            f'href="{reverse("profile")}"',
        )
        self.assertContains(response, 'Мой профиль')
        self.assertContains(response, 'Ada Lovelace')

    def test_profile_displays_user_and_profile_data(self):
        user = get_user_model().objects.create_user(
            username='profile-owner',
            first_name='Ada',
            last_name='Lovelace',
            email='ada@example.com',
        )
        UserProfile.objects.filter(user=user).update(city='London', about='First programmer')
        self.client.force_login(user)

        response = self.client.get(reverse('profile'))

        self.assertContains(response, 'Мой профиль')
        self.assertContains(response, 'Ada')
        self.assertContains(response, 'Lovelace')
        self.assertContains(response, 'ada@example.com')
        self.assertContains(response, 'London')
        self.assertContains(response, 'First programmer')
        self.assertContains(response, reverse('profile_edit'))

    def test_profile_edit_updates_only_authenticated_users_own_profile(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username='profile-owner',
            password='Example-password-384!',
        )
        other_user = user_model.objects.create_user(
            username='other-user',
            first_name='Unchanged',
            email='other@example.com',
        )
        image_data = BytesIO()
        Image.new('RGB', (1, 1), color='red').save(image_data, format='PNG')
        image = SimpleUploadedFile(
            'avatar.png',
            image_data.getvalue(),
            content_type='image/png',
        )
        self.client.force_login(user)

        with TemporaryDirectory() as media_root:
            with self.settings(MEDIA_ROOT=media_root):
                response = self.client.post(
                    reverse('profile_edit'),
                    {
                        'first_name': 'Ada',
                        'last_name': 'Lovelace',
                        'email': 'ada@example.com',
                        'city': 'London',
                        'about': 'First programmer',
                        'avatar': image,
                    },
                )

                self.assertRedirects(response, reverse('profile'))
                user.refresh_from_db()
                other_user.refresh_from_db()
                profile = UserProfile.objects.get(user=user)

                self.assertEqual(user.first_name, 'Ada')
                self.assertEqual(user.last_name, 'Lovelace')
                self.assertEqual(user.email, 'ada@example.com')
                self.assertEqual(profile.city, 'London')
                self.assertEqual(profile.about, 'First programmer')
                self.assertTrue(profile.avatar.name.startswith('avatars/'))
                self.assertEqual(other_user.first_name, 'Unchanged')
                self.assertEqual(other_user.email, 'other@example.com')
