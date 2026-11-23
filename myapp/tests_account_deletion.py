import json
import re

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import AccountDeletionRequest, OTPVerification, UserProfile


sent_messages = []


def fake_sms_sender(phone, message):
    sent_messages.append((phone, message))


class AccountDeletionRequestTests(TestCase):
    def setUp(self):
        sent_messages.clear()
        self.user = get_user_model().objects.create_user(
            username='deletion-request-test',
            password='test-password',
        )
        UserProfile.objects.create(user=self.user, phone_number='9876543210')
        self.client = Client()

    def post_json(self, name, payload):
        return self.client.post(
            reverse(name),
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_page_only_asks_for_phone_and_otp(self):
        response = self.client.get(reverse('account_deletion'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="phone"')
        self.assertContains(response, 'name="otp"')
        self.assertNotContains(response, 'name="email"')
        self.assertContains(response, 'This page does not delete or deactivate your account.')

    @override_settings(DEBUG=False)
    def test_otp_is_unavailable_without_configured_sms_provider_in_production(self):
        response = self.post_json('account_deletion_send_otp', {'phone': '9876543210'})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(OTPVerification.objects.count(), 0)

    @override_settings(DEBUG=True)
    def test_debug_mode_returns_a_test_code_without_sms_provider(self):
        response = self.post_json('account_deletion_send_otp', {'phone': '9876543210'})
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.json()['debug_otp'], r'^\d{6}$')
        self.assertEqual(len(sent_messages), 0)

    @override_settings(ACCOUNT_DELETION_SMS_BACKEND='myapp.tests_account_deletion.fake_sms_sender')
    def test_verified_request_is_recorded_without_changing_user_account(self):
        response = self.post_json('account_deletion_send_otp', {'phone': '9876543210'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(sent_messages), 1)
        otp = re.search(r'(\d{6})', sent_messages[0][1]).group(1)

        response = self.post_json('account_deletion_verify_otp', {
            'phone': '9876543210',
            'otp': otp,
        })
        self.assertEqual(response.status_code, 200)

        response = self.post_json('account_deletion_submit', {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccountDeletionRequest.objects.count(), 1)
        self.assertEqual(AccountDeletionRequest.objects.first().user, self.user)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(get_user_model().objects.filter(pk=self.user.pk).exists())
        self.assertEqual(self.user.check_password('test-password'), True)

    @override_settings(ACCOUNT_DELETION_SMS_BACKEND='myapp.tests_account_deletion.fake_sms_sender')
    def test_invalid_otp_cannot_submit_request(self):
        self.post_json('account_deletion_send_otp', {'phone': '9876543210'})
        response = self.post_json('account_deletion_verify_otp', {
            'phone': '9876543210',
            'otp': '000000',
        })
        self.assertEqual(response.status_code, 400)
        response = self.post_json('account_deletion_submit', {})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(AccountDeletionRequest.objects.count(), 0)
