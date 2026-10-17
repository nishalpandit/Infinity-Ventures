from decimal import Decimal
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from myapp.models import AuthToken, UserProfile, VendorProfile, Job, Bid, VendorWallet, PayoutRequest, DisputeTicket, DisputeMessage, JobCompletionProof, Category

User = get_user_model()

class Phase2ApiTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Customer
        self.customer = User.objects.create_user(
            username='cust_phase2',
            email='cust2@example.com',
            password='Password123!',
            first_name='Alice',
            role='USER'
        )
        self.customer_token = AuthToken.objects.create(user=self.customer).key

        # 2. Vendor
        self.vendor = User.objects.create_user(
            username='vend_phase2',
            email='vend2@example.com',
            password='Password123!',
            first_name='Bob',
            role='VENDOR'
        )
        self.vendor_token = AuthToken.objects.create(user=self.vendor).key

        # 3. Third-party Customer
        self.other_user = User.objects.create_user(
            username='other_cust',
            email='other@example.com',
            password='Password123!',
            role='USER'
        )
        self.other_token = AuthToken.objects.create(user=self.other_user).key

        # 4. Wallet for vendor with balance
        self.wallet = VendorWallet.objects.create(
            vendor=self.vendor,
            available_balance=Decimal('2500.00'),
            total_earned=Decimal('5000.00')
        )

        # 5. Category and Job
        self.category = Category.objects.create(name='Carpentry', service_type='both', status='active')
        self.job = Job.objects.create(
            title='Fix Wooden Door',
            category=self.category,
            description='Door hinge broken',
            budget=1200.00,
            city='Ranchi',
            user=self.customer,
            assigned_vendor=self.vendor,
            status='progress'
        )

    # -------------------------------------------------------------
    # 1. Payout Request API Tests
    # -------------------------------------------------------------
    def test_payout_request_auth_and_validation(self):
        # Unauthenticated
        res = self.client.post('/api/vendor/wallet/payout/request/')
        self.assertEqual(res.status_code, 401)

        # Forbidden for customer
        res = self.client.post('/api/vendor/wallet/payout/request/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(res.status_code, 403)

        # Insufficient balance (balance is 2500, request 5000)
        res = self.client.post(
            '/api/vendor/wallet/payout/request/',
            data={'amount': '5000.00', 'payout_method': 'upi', 'upi_id': 'bob@okaxis'},
            HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}'
        )
        self.assertEqual(res.status_code, 400)

        # Successful UPI payout request
        res = self.client.post(
            '/api/vendor/wallet/payout/request/',
            data={'amount': '1000.00', 'payout_method': 'upi', 'upi_id': 'bob@okaxis'},
            HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}'
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['amount'], 1000.00)
        self.assertEqual(data['data']['status'], 'pending')

        # Prevent duplicate pending request
        res_dup = self.client.post(
            '/api/vendor/wallet/payout/request/',
            data={'amount': '500.00', 'payout_method': 'upi', 'upi_id': 'bob@okaxis'},
            HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}'
        )
        self.assertEqual(res_dup.status_code, 400)

    def test_payout_history(self):
        # Create a payout record
        PayoutRequest.objects.create(
            vendor=self.vendor,
            amount=Decimal('500.00'),
            payout_method='upi',
            upi_id='bob@upi',
            status='pending'
        )

        res = self.client.get('/api/vendor/wallet/payout/history/', HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertGreaterEqual(data['count'], 1)

    # -------------------------------------------------------------
    # 2. Dispute APIs Tests
    # -------------------------------------------------------------
    def test_dispute_lifecycle(self):
        # Create dispute
        res = self.client.post(
            '/api/disputes/create/',
            data={
                'subject': 'Delay in completing door work',
                'description': 'Vendor did not show up on time as agreed.',
                'category': 'delay',
                'priority': 'high',
                'job_id': self.job.id
            },
            HTTP_AUTHORIZATION=f'Bearer {self.customer_token}'
        )
        self.assertEqual(res.status_code, 201)
        ticket_id = res.json()['data']['ticket_id']
        self.assertTrue(ticket_id.startswith('CMP-'))

        # List disputes
        res_list = self.client.get('/api/disputes/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(res_list.json()['count'], 1)

        # Third party cannot view detail
        res_unauth = self.client.get(f'/api/disputes/{ticket_id}/', HTTP_AUTHORIZATION=f'Bearer {self.other_token}')
        self.assertEqual(res_unauth.status_code, 403)

        # Participant (vendor) CAN view detail
        res_detail = self.client.get(f'/api/disputes/{ticket_id}/', HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        self.assertEqual(res_detail.status_code, 200)
        self.assertEqual(res_detail.json()['data']['subject'], 'Delay in completing door work')

        # Post reply message
        res_msg = self.client.post(
            f'/api/disputes/{ticket_id}/message/',
            data={'message': 'Apologies for delay, traffic was blocked. Arriving in 15 mins.'},
            HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}'
        )
        self.assertEqual(res_msg.status_code, 201)

        # Check detail again to see reply in thread
        res_detail2 = self.client.get(f'/api/disputes/{ticket_id}/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(len(res_detail2.json()['data']['messages']), 1)
        self.assertEqual(res_detail2.json()['data']['messages'][0]['sender_name'], 'Bob')

    # -------------------------------------------------------------
    # 3. Job Completion Proof Tests
    # -------------------------------------------------------------
    def test_job_completion_proof_flow(self):
        # Check proof before submission (customer side)
        res_pre = self.client.get(f'/api/user/jobs/{self.job.id}/proof/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(res_pre.status_code, 200)
        self.assertFalse(res_pre.json()['data']['has_proof'])

        # Unauthorized vendor cannot submit proof
        unauth_vendor = User.objects.create_user(username='other_vend', role='VENDOR')
        unauth_token = AuthToken.objects.create(user=unauth_vendor).key
        p1 = SimpleUploadedFile("proof1.jpg", b"image bytes 1", content_type="image/jpeg")
        res_fail = self.client.post(
            f'/api/vendor/jobs/{self.job.id}/submit-proof/',
            data={'photo_1': p1, 'work_summary': 'Done'},
            HTTP_AUTHORIZATION=f'Bearer {unauth_token}'
        )
        self.assertEqual(res_fail.status_code, 403)

        # Assigned vendor submits proof
        p1 = SimpleUploadedFile("proof1.jpg", b"image bytes 1", content_type="image/jpeg")
        res_submit = self.client.post(
            f'/api/vendor/jobs/{self.job.id}/submit-proof/',
            data={'photo_1': p1, 'work_summary': 'Door hinge replaced with stainless steel fixtures.'},
            HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}'
        )
        self.assertIn(res_submit.status_code, [200, 201])
        self.assertEqual(res_submit.json()['status'], 'success')

        # Customer views proof
        res_view = self.client.get(f'/api/user/jobs/{self.job.id}/proof/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(res_view.status_code, 200)
        data = res_view.json()['data']
        self.assertTrue(data['has_proof'])
        self.assertEqual(data['work_summary'], 'Door hinge replaced with stainless steel fixtures.')
        self.assertEqual(data['vendor_name'], 'Bob')
        self.assertTrue(bool(data['photo_1_url']))
