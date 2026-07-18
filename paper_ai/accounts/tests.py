from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsModelTests(TestCase):
    def test_create_user_with_role(self):
        user = User.objects.create_user(
            username='operator1',
            email='operator1@example.com',
            password='password123',
            role=User.Roles.OPERATOR
        )
        self.assertEqual(user.role, User.Roles.OPERATOR)
        self.assertTrue(user.is_operator)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_process_engineer)

    def test_create_process_engineer(self):
        user = User.objects.create_user(
            username='engineer1',
            email='engineer1@example.com',
            password='password123',
            role=User.Roles.PROCESS_ENGINEER
        )
        self.assertTrue(user.is_process_engineer)
        self.assertFalse(user.is_operator)
        self.assertFalse(user.is_admin)

    def test_create_admin(self):
        user = User.objects.create_user(
            username='admin1',
            email='admin1@example.com',
            password='password123',
            role=User.Roles.ADMIN
        )
        self.assertTrue(user.is_admin)
        self.assertFalse(user.is_operator)
        self.assertFalse(user.is_process_engineer)


class AuthenticationViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='operator1',
            password='password123',
            role=User.Roles.OPERATOR
        )
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.dashboard_url = reverse('dashboard:index')

    def test_login_page_renders(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            'username': 'operator1',
            'password': 'password123'
        })
        self.assertRedirects(response, self.dashboard_url)

    def test_unsuccessful_login(self):
        response = self.client.post(self.login_url, {
            'username': 'operator1',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_logout(self):
        self.client.login(username='operator1', password='password123')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
