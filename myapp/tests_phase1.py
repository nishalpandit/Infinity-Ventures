import io
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from myapp.models import AuthToken, UserProfile, VendorProfile, Job, ServiceBooking, Bid, VendorKYC, Category

User = get_user_model()

class Phase1ApiTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Create a customer user
        self.customer = User.objects.create_user(
            username='test_customer',
            email='customer@example.com',
            password='Password123!',
            first_name='John',
            last_name='Doe',
            role='USER'
        )
        self.customer_profile = UserProfile.objects.create(
            user=self.customer,
            phone_number='9876543210',
            city='Ranchi',
            state='Jharkhand'
        )
        self.customer_token = AuthToken.objects.create(user=self.customer).key

        # 2. Create a vendor user
        self.vendor = User.objects.create_user(
            username='test_vendor',
            email='vendor@example.com',
            password='Password123!',
            first_name='Bob',
            last_name='Plumber',
            role='VENDOR'
        )
        self.vendor_profile = VendorProfile.objects.create(
            user=self.vendor,
            mobile='9123456780',
            company_name='Bob Plumbing Services',
            category='Plumbing',
            location='Ranchi, Jharkhand'
        )
        self.vendor_token = AuthToken.objects.create(user=self.vendor).key

        # 3. Create category
        self.category = Category.objects.create(name='Plumbing', service_type='both', status='active')

        # 4. Create jobs
        self.job1 = Job.objects.create(
            title='Leaking Pipe Repair',
            category=self.category,
            description='Pipe leaking in bathroom',
            budget=1500.00,
            city='Ranchi',
            contact_name='John Doe',
            contact_mobile='9876543210',
            user=self.customer,
            status='open'
        )

        self.job2 = Job.objects.create(
            title='Kitchen Sink Installation',
            category=self.category,
            description='Install new sink',
            budget=3000.00,
            city='Ranchi',
            address='123 Main Road, Ranchi',
            contact_name='John Doe',
            contact_mobile='9876543210',
            user=self.customer,
            assigned_vendor=self.vendor,
            status='selected'
        )

        # 5. Create bid for job2
        self.bid = Bid.objects.create(
            vendor=self.vendor,
            job=self.job2,
            amount=2800.00,
            status='selected'
        )

    # -------------------------------------------------------------
    # 1. User Dashboard API Tests
    # -------------------------------------------------------------
    def test_user_dashboard_unauthenticated(self):
        res = self.client.get('/api/user/dashboard/')
        self.assertEqual(res.status_code, 401)

    def test_user_dashboard_forbidden_for_vendor(self):
        res = self.client.get('/api/user/dashboard/', HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        self.assertEqual(res.status_code, 403)

    def test_user_dashboard_success(self):
        res = self.client.get('/api/user/dashboard/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        dash = data['data']
        self.assertEqual(dash['active_jobs_count'], 2)  # job1 (open) + job2 (selected)
        self.assertEqual(dash['selected_vendors_count'], 1)
        self.assertEqual(len(dash['recent_jobs']), 2)
        self.assertEqual(dash['recent_jobs'][0]['title'], 'Kitchen Sink Installation')

    # -------------------------------------------------------------
    # 2. Vendor Selected Jobs API Tests
    # -------------------------------------------------------------
    def test_vendor_selected_jobs_unauthenticated(self):
        res = self.client.get('/api/vendor/selected-jobs/')
        self.assertEqual(res.status_code, 401)

    def test_vendor_selected_jobs_forbidden_for_customer(self):
        res = self.client.get('/api/vendor/selected-jobs/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(res.status_code, 403)

    def test_vendor_selected_jobs_success(self):
        res = self.client.get('/api/vendor/selected-jobs/', HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['count'], 1)
        job_item = data['data'][0]
        self.assertEqual(job_item['title'], 'Kitchen Sink Installation')
        self.assertEqual(job_item['bid_amount'], 2800.00)
        self.assertEqual(job_item['customer_name'], 'John Doe')
        self.assertEqual(job_item['customer_phone'], '9876543210')
        self.assertEqual(job_item['site_address'], '123 Main Road, Ranchi')

    # -------------------------------------------------------------
    # 3. Vendor KYC Submit API Tests
    # -------------------------------------------------------------
    def test_vendor_kyc_submit_unauthenticated(self):
        res = self.client.post('/api/vendor/kyc/submit/')
        self.assertEqual(res.status_code, 401)

    def test_vendor_kyc_submit_forbidden_for_customer(self):
        res = self.client.post('/api/vendor/kyc/submit/', HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        self.assertEqual(res.status_code, 403)

    def test_vendor_kyc_submit_missing_fields(self):
        res = self.client.post(
            '/api/vendor/kyc/submit/',
            data={'id_type': 'aadhaar'},
            HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}'
        )
        self.assertEqual(res.status_code, 400)

    def test_vendor_kyc_submit_and_status_flow(self):
        # Initial status before KYC
        res_status = self.client.get('/api/vendor/kyc/status/', HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        self.assertEqual(res_status.status_code, 200)
        self.assertFalse(res_status.json()['data']['has_kyc'])
        self.assertEqual(res_status.json()['data']['kyc_status'], 'not_submitted')

        # Submit KYC with dummy front file
        front_file = SimpleUploadedFile("front.jpg", b"fake image content", content_type="image/jpeg")
        res_submit = self.client.post(
            '/api/vendor/kyc/submit/',
            data={
                'id_type': 'aadhaar',
                'id_number': '123456789012',
                'id_document_front': front_file
            },
            HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}'
        )
        self.assertIn(res_submit.status_code, [200, 201])
        data_submit = res_submit.json()
        self.assertEqual(data_submit['status'], 'success')
        self.assertEqual(data_submit['data']['status'], 'pending')

        # Check status after submission
        res_status_after = self.client.get('/api/vendor/kyc/status/', HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        self.assertEqual(res_status_after.status_code, 200)
        status_data = res_status_after.json()['data']
        self.assertTrue(status_data['has_kyc'])
        self.assertEqual(status_data['kyc_status'], 'pending')
        self.assertEqual(status_data['id_type'], 'aadhaar')
        self.assertEqual(status_data['id_number'], '123456789012')
        self.assertTrue(bool(status_data['id_document_front']))
