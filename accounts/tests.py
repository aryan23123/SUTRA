from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from documents.models import Document
from records.models import Category, InformationRecord


class RegistrationTests(TestCase):
    def test_registration_signs_user_in_and_opens_dashboard(self):
        raw_password = 'SaffronRiver!482'
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newteammate',
                'email': 'newteammate@example.com',
                'first_name': 'Aditi',
                'last_name': 'Shah',
                'password1': raw_password,
                'password2': raw_password,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back, Aditi.')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

        user = get_user_model().objects.get(username='newteammate')
        self.assertNotEqual(user.password, raw_password)
        self.assertTrue(user.check_password(raw_password))


class ProfileTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='arya',
            email='arya@example.com',
            password='StrongPass123!',
            first_name='Arya',
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_updates_allowed_fields_and_keeps_username_unchanged(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile'),
            {
                'first_name': 'Arya',
                'last_name': 'Sharma',
                'email': 'arya.sharma@example.com',
                'username': 'changed-username',
            },
        )

        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Arya')
        self.assertEqual(self.user.last_name, 'Sharma')
        self.assertEqual(self.user.email, 'arya.sharma@example.com')
        self.assertEqual(self.user.username, 'arya')

    def test_profile_stats_are_scoped_to_signed_in_user(self):
        category = Category.objects.create(name='Profile test')
        own_record = InformationRecord.objects.create(
            title='My active record',
            description='Personal test record',
            status='active',
            category=category,
            created_by=self.user,
        )
        Document.objects.create(
            title='My document',
            file='documents/profile-test.txt',
            record=own_record,
            uploaded_by=self.user,
        )
        other_user = get_user_model().objects.create_user(
            username='other',
            password='StrongPass123!',
        )
        InformationRecord.objects.create(
            title='Someone else’s record',
            description='Not owned by the profile user',
            status='draft',
            created_by=other_user,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['record_count'], 1)
        self.assertEqual(response.context['active_record_count'], 1)
        self.assertEqual(response.context['draft_record_count'], 0)
        self.assertEqual(response.context['document_count'], 1)
