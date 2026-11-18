from io import StringIO
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from documents.models import Document
from records.models import Category, InformationRecord, Tag

User = get_user_model()


class InformationManagementSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(name='Finance', description='Financial records')
        self.tag = Tag.objects.create(name='priority')
        self.record = InformationRecord.objects.create(
            title='Quarterly finance summary',
            description='Summary of business performance.',
            status='draft',
            category=self.category,
            created_by=self.user,
        )
        self.record.tags.add(self.tag)

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_and_record_list_load(self):
        self.client.login(username='alice', password='StrongPass123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total records')
        self.assertContains(response, 'Quarterly finance summary')

        list_response = self.client.get(reverse('record_list'), {'q': 'quarterly', 'status': 'draft'})
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'Quarterly finance summary')

    def test_record_form_explains_how_to_add_missing_options(self):
        self.category.delete()
        self.tag.delete()
        self.client.login(username='alice', password='StrongPass123!')

        response = self.client.get(reverse('record_create'))

        self.assertContains(response, 'No categories have been created yet.')
        self.assertContains(response, reverse('category_list'))
        self.assertContains(response, 'No tags have been created yet.')
        self.assertContains(response, reverse('tag_list'))

    def test_record_form_includes_existing_category_and_tags(self):
        self.client.login(username='alice', password='StrongPass123!')

        response = self.client.get(reverse('record_create'))

        self.assertContains(response, 'Finance')
        self.assertContains(response, 'priority')

    def test_record_crud_and_filtering(self):
        self.client.login(username='alice', password='StrongPass123!')
        create_response = self.client.post(
            reverse('record_create'),
            {
                'title': 'New customer intake',
                'description': 'Customer onboarding details.',
                'status': 'active',
                'category': self.category.pk,
                'tags': [self.tag.pk],
            },
        )
        self.assertEqual(create_response.status_code, 302)
        self.assertTrue(InformationRecord.objects.filter(title='New customer intake').exists())

        record = InformationRecord.objects.get(title='New customer intake')
        detail_response = self.client.get(reverse('record_detail', kwargs={'pk': record.pk}))
        self.assertContains(detail_response, 'New customer intake')

        update_response = self.client.post(
            reverse('record_edit', kwargs={'pk': record.pk}),
            {
                'title': 'Updated customer intake',
                'description': 'Updated onboarding details.',
                'status': 'archived',
                'category': self.category.pk,
                'tags': [self.tag.pk],
            },
        )
        self.assertEqual(update_response.status_code, 302)
        self.assertTrue(InformationRecord.objects.filter(title='Updated customer intake').exists())

        filter_response = self.client.get(reverse('record_list'), {'status': 'archived'})
        self.assertContains(filter_response, 'Updated customer intake')

    def test_document_upload_rejects_invalid_file(self):
        self.client.login(username='alice', password='StrongPass123!')
        invalid_file = SimpleUploadedFile('bad.csv', b'not-a-valid-doc', content_type='text/csv')
        response = self.client.post(
            reverse('document_upload', kwargs={'record_id': self.record.pk}),
            {'title': 'Bad file', 'file': invalid_file},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Only PDF, DOCX and TXT files are allowed.')
        self.assertFalse(Document.objects.filter(title='Bad file').exists())


class DemoSeedCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='demo-owner',
            email='demo-owner@example.com',
            password='StrongPass123!',
            first_name='Aditi',
        )

    def test_seed_command_is_idempotent_and_documents_download_securely(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                call_command(
                    'seed_demo_data',
                    username=self.user.username,
                    stdout=StringIO(),
                )
                counts_after_first_run = (
                    Category.objects.count(),
                    Tag.objects.count(),
                    InformationRecord.objects.count(),
                    Document.objects.count(),
                )

                self.assertEqual(counts_after_first_run, (10, 26, 21, 8))
                sutra_record = InformationRecord.objects.get(
                    title='Information Management System — Sutra',
                    created_by=self.user,
                )
                self.assertEqual(sutra_record.category.name, 'Projects & Development')
                self.assertIn('DEMO DATA', set(sutra_record.tags.values_list('name', flat=True)))
                self.assertIn('[SUTRA DEMO]', sutra_record.description)
                self.assertTrue(
                    Document.objects.filter(
                        record=sutra_record,
                        title='Sample — Django Project Documentation',
                        uploaded_by=self.user,
                    ).exists()
                )
                sample_document = Document.objects.get(
                    title='Sample — Django Project Documentation'
                )
                self.assertTrue(sample_document.file.storage.exists(sample_document.file.name))

                call_command(
                    'seed_demo_data',
                    username=self.user.username,
                    stdout=StringIO(),
                )
                counts_after_second_run = (
                    Category.objects.count(),
                    Tag.objects.count(),
                    InformationRecord.objects.count(),
                    Document.objects.count(),
                )
                self.assertEqual(counts_after_second_run, counts_after_first_run)

                document = Document.objects.get(title='Sample — DSA Interview Revision Notes')
                download_url = reverse('document_download', kwargs={'pk': document.pk})
                self.assertEqual(self.client.get(download_url).status_code, 302)

                self.client.force_login(self.user)
                response = self.client.get(download_url)
                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    b'SAMPLE DOCUMENT',
                    b''.join(response.streaming_content),
                )

                dashboard_response = self.client.get(reverse('dashboard'))
                self.assertEqual(dashboard_response.context['total_records'], 21)
                self.assertEqual(dashboard_response.context['total_categories'], 10)
                self.assertEqual(dashboard_response.context['total_documents'], 8)
                self.assertContains(dashboard_response, 'Recently added documents')
                self.assertContains(dashboard_response, 'Recent activity')

                detail_response = self.client.get(
                    reverse('record_detail', kwargs={'pk': sutra_record.pk})
                )
                self.assertContains(detail_response, 'Related documents')
                self.assertContains(detail_response, 'Sample — Django Project Documentation')
                self.assertContains(detail_response, 'Record history')

                search_response = self.client.get(
                    reverse('record_list'),
                    {'q': 'Phagwara', 'status': 'active'},
                )
                self.assertContains(
                    search_response,
                    'Final Year Project — Technical Documentation',
                )

    def test_seed_command_does_not_overwrite_existing_user_records(self):
        record = InformationRecord.objects.create(
            title='TCS NQT 2026 Preparation Plan',
            description='A private note created before the demo command.',
            status='draft',
            created_by=self.user,
        )

        call_command(
            'seed_demo_data',
            username=self.user.username,
            stdout=StringIO(),
            stderr=StringIO(),
        )

        record.refresh_from_db()
        self.assertEqual(record.description, 'A private note created before the demo command.')
        self.assertEqual(record.status, 'draft')
        self.assertFalse(record.tags.exists())

    def test_seed_command_requires_an_existing_user(self):
        with self.assertRaises(CommandError):
            call_command('seed_demo_data', username='missing-user', stdout=StringIO())

        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Tag.objects.count(), 0)
        self.assertEqual(InformationRecord.objects.count(), 0)
        self.assertEqual(Document.objects.count(), 0)
