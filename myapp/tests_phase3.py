from decimal import Decimal
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from myapp.models import AuthToken, UserProfile, VendorProfile, Job, JobImage, VendorWallet, PlatformRevenueLedger, Category

User = get_user_model()

class Phase3ApiTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Customer
        self.customer = User.objects.create_user(
            username='cust_phase3',
            email='cust3@example.com',
            password='Password123!',
            first_name='Carol',
            role='USER'
        )
        self.customer_token = AuthToken.objects.create(user=self.customer).key

        # 2. Vendor
        self.vendor = User.objects.create_user(
            username='vend_phase3',
            email='vend3@example.com',
            password='Password123!',
            first_name='Dave',
            role='VENDOR'
        )
        self.vendor_token = AuthToken.objects.create(user=self.vendor).key

        # 3. Third-party Customer
        self.other_user = User.objects.create_user(
            username='other_cust3',
            email='other3@example.com',
            password='Password123!',
            role='USER'
        )
        self.other_token = AuthToken.objects.create(user=self.other_user).key

        # 4. Vendor Wallet & Platform Revenue Ledgers
        self.wallet = VendorWallet.objects.create(
            vendor=self.vendor,
            available_balance=Decimal('4500.00'),
            total_earned=Decimal('9000.00'),
            total_withdrawn=Decimal('4500.00')
        )

        # 5. Category and Job
        self.category = Category.objects.create(name='Painting', service_type='both', status='active')
        self.job = Job.objects.create(
            title='Interior Wall Painting',
            category=self.category,
            description='Living room 2 coats paint',
            budget=8000.00,
            city='Ranchi',
            user=self.customer,
            assigned_vendor=self.vendor,
            status='completed'
        )

        # Ledger entry for the completed job
        self.ledger = PlatformRevenueLedger.objects.create(
            vendor=self.vendor,
            related_job=self.job,
            vendor_payout=Decimal('7200.00'),
            platform_commission=Decimal('800.00'),
            cgst_collected=Decimal('72.00'),
            sgst_collected=Decimal('72.00'),
            total_customer_paid=Decimal('8144.00')
        )

    # -------------------------------------------------------------
    # 1. Vendor Earnings Summary API Tests
    # -------------------------------------------------------------
    def test_vendor_earnings_unauthenticated(self):
        res = self.client.get('/api/vendor/earnings/')
        self.assertEqual(res.status_code, 401)

    def test_vendor_earnings_forbidden_for_customer(self):
        res = self.client.get('/api/vendor/earnings/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(res.status_code, 403)

    def test_vendor_earnings_success(self):
        res = self.client.get('/api/vendor/earnings/', HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        edata = data['data']
        self.assertEqual(edata['available_balance'], 4500.00)
        self.assertEqual(edata['total_earned'], 9000.00)
        self.assertEqual(edata['total_commission_paid'], 800.00)
        self.assertEqual(edata['total_tax_paid'], 144.00)
        self.assertEqual(edata['completed_jobs_count'], 1)
        self.assertGreater(edata['average_job_value'], 0.0)
        self.assertEqual(len(edata['monthly_breakdown']), 6)

    # -------------------------------------------------------------
    # 2. Job Image Gallery APIs Tests
    # -------------------------------------------------------------
    def test_job_images_upload_unauthorized(self):
        img = SimpleUploadedFile("wall1.jpg", b"wall image content", content_type="image/jpeg")
        res = self.client.post(
            f'/api/user/jobs/{self.job.id}/images/upload/',
            data={'images': [img]},
            HTTP_AUTHORIZATION=f'Bearer {self.other_token}'
        )
        self.assertEqual(res.status_code, 403)

    def test_job_images_lifecycle(self):
        # 1. Upload images as job owner
        img1 = SimpleUploadedFile("wall1.jpg", b"wall image content 1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("wall2.jpg", b"wall image content 2", content_type="image/jpeg")
        res_upload = self.client.post(
            f'/api/user/jobs/{self.job.id}/images/upload/',
            data={'images': [img1, img2]},
            HTTP_AUTHORIZATION=f'Bearer {self.customer_token}'
        )
        self.assertEqual(res_upload.status_code, 201)
        data = res_upload.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['count'], 2)
        img_id_1 = data['data'][0]['id']

        # 2. List images
        res_list = self.client.get(f'/api/user/jobs/{self.job.id}/images/')
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(res_list.json()['count'], 2)

        # 3. Third party cannot delete
        res_del_fail = self.client.post(
            f'/api/user/jobs/{self.job.id}/images/{img_id_1}/delete/',
            HTTP_AUTHORIZATION=f'Bearer {self.other_token}'
        )
        self.assertEqual(res_del_fail.status_code, 403)

        # 4. Owner deletes image
        res_del = self.client.post(
            f'/api/user/jobs/{self.job.id}/images/{img_id_1}/delete/',
            HTTP_AUTHORIZATION=f'Bearer {self.customer_token}'
        )
        self.assertEqual(res_del.status_code, 200)

        # 5. List images again -> count should be 1
        res_list2 = self.client.get(f'/api/user/jobs/{self.job.id}/images/')
        self.assertEqual(res_list2.status_code, 200)
        self.assertEqual(res_list2.json()['count'], 1)
