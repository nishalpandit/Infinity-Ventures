from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import AuthToken, QuickService, ServiceBooking, ServiceReview

User = get_user_model()


class BookingReviewAndPrivacyTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='cust1', password='x', first_name='Rahul', last_name='Patil',
            email='rahul@example.com', role='CUSTOMER',
        )
        self.other_customer = User.objects.create_user(username='cust2', password='x', role='CUSTOMER')
        self.vendor = User.objects.create_user(username='vend1', password='x', role='VENDOR')
        self.service = QuickService.objects.create(vendor=self.vendor, title='Water Tank Cleaning', base_price=500)

        self.c_token = AuthToken.objects.create(user=self.customer).key
        self.o_token = AuthToken.objects.create(user=self.other_customer).key
        self.v_token = AuthToken.objects.create(user=self.vendor).key

    def _booking(self, status='pending'):
        return ServiceBooking.objects.create(
            customer=self.customer, vendor=self.vendor, quick_service=self.service,
            package_name='Base', total_amount=500, scheduled_date=date.today(),
            service_address='12 Park Road, Ranchi [GPS: 23.34, 85.31]', status=status,
        )

    def _auth(self, token):
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    # ---------------- privacy ----------------
    def test_pending_booking_hides_customer_and_location(self):
        self._booking('pending')
        res = self.client.get('/api/vendor/bookings/', **self._auth(self.v_token))
        b = res.json()['bookings'][0]
        self.assertTrue(b['details_locked'])
        self.assertEqual(b['customer_name'], 'Customer')
        for key in ('customer_email', 'customer_phone', 'service_address', 'clean_address', 'map_url'):
            self.assertEqual(b[key], '', key)
        self.assertIsNone(b['customer_id'])
        self.assertIsNone(b['latitude'])
        self.assertIsNone(b['longitude'])

    def test_accepted_booking_reveals_customer_and_location(self):
        self._booking('accepted')
        b = self.client.get('/api/vendor/bookings/', **self._auth(self.v_token)).json()['bookings'][0]
        self.assertFalse(b['details_locked'])
        self.assertEqual(b['customer_name'], 'Rahul Patil')
        self.assertEqual(b['customer_email'], 'rahul@example.com')
        self.assertIn('Park Road', b['clean_address'])
        self.assertEqual(b['latitude'], '23.34')

    def test_status_transitions_are_guarded(self):
        bk = self._booking('pending')
        url = f'/api/vendor/bookings/{bk.id}/status/'
        # cannot jump straight to completed (would skip payment)
        r = self.client.post(url, {'status': 'completed'}, content_type='application/json', **self._auth(self.v_token))
        self.assertEqual(r.status_code, 400)
        r = self.client.post(url, {'status': 'accepted'}, content_type='application/json', **self._auth(self.v_token))
        self.assertEqual(r.status_code, 200)
        bk.refresh_from_db()
        self.assertEqual(bk.status, 'accepted')

    def test_vendor_chat_list_excludes_pending_customers(self):
        self._booking('pending')
        r = self.client.get('/api/chat/conversations/', **self._auth(self.v_token))
        self.assertEqual(r.json()['conversations'], [])
        self._booking('accepted')
        r = self.client.get('/api/chat/conversations/', **self._auth(self.v_token))
        self.assertEqual(len(r.json()['conversations']), 1)

    # ---------------- reviews ----------------
    def test_cannot_review_until_completed(self):
        bk = self._booking('accepted')
        r = self.client.post('/api/user/reviews/submit/', {'booking_id': bk.id, 'rating': 5, 'comment': 'great'},
                             content_type='application/json', **self._auth(self.c_token))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(ServiceReview.objects.count(), 0)

    def test_only_booking_owner_can_review(self):
        bk = self._booking('completed')
        r = self.client.post('/api/user/reviews/submit/', {'booking_id': bk.id, 'rating': 5},
                             content_type='application/json', **self._auth(self.o_token))
        self.assertEqual(r.status_code, 403)

    def test_rating_validation(self):
        bk = self._booking('completed')
        for bad in (0, 6, 'abc', None):
            r = self.client.post('/api/user/reviews/submit/', {'booking_id': bk.id, 'rating': bad},
                                 content_type='application/json', **self._auth(self.c_token))
            self.assertEqual(r.status_code, 400, bad)

    def test_review_flow_and_vendor_my_reviews(self):
        bk = self._booking('completed')

        pending = self.client.get('/api/user/reviews/pending/', **self._auth(self.c_token)).json()
        self.assertEqual(pending['count'], 1)

        r = self.client.post('/api/user/reviews/submit/',
                             {'booking_id': bk.id, 'rating': 4, 'comment': 'Neat work', 'title': 'Good'},
                             content_type='application/json', **self._auth(self.c_token))
        self.assertEqual(r.status_code, 201)

        # resubmitting updates the same review (one per booking)
        r = self.client.post('/api/user/reviews/submit/', {'booking_id': bk.id, 'rating': 5, 'comment': 'Perfect'},
                             content_type='application/json', **self._auth(self.c_token))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(ServiceReview.objects.filter(booking=bk).count(), 1)

        pending = self.client.get('/api/user/reviews/pending/', **self._auth(self.c_token)).json()
        self.assertEqual(pending['count'], 0)

        data = self.client.get('/api/vendor/reviews/', **self._auth(self.v_token)).json()
        self.assertEqual(data['summary']['total_reviews'], 1)
        self.assertEqual(data['summary']['average_rating'], 5.0)
        self.assertEqual(data['summary']['breakdown']['5'], 1)
        review = data['reviews'][0]
        self.assertEqual(review['customer_name'], 'Rahul P.')  # masked
        self.assertEqual(review['service_title'], 'Water Tank Cleaning')
        self.assertEqual(review['comment'], 'Perfect')

        # vendor bookings list exposes the rating on the completed card
        b = self.client.get('/api/vendor/bookings/', **self._auth(self.v_token)).json()['bookings'][0]
        self.assertEqual(b['review_rating'], 5)

        # filter by rating
        self.assertEqual(self.client.get('/api/vendor/reviews/?rating=1', **self._auth(self.v_token)).json()['count'], 0)

    def test_two_bookings_same_service_keep_separate_reviews(self):
        b1, b2 = self._booking('completed'), self._booking('completed')
        for bk, rating in ((b1, 5), (b2, 3)):
            self.client.post('/api/user/reviews/submit/', {'booking_id': bk.id, 'rating': rating},
                             content_type='application/json', **self._auth(self.c_token))
        self.assertEqual(ServiceReview.objects.count(), 2)
        data = self.client.get('/api/vendor/reviews/', **self._auth(self.v_token)).json()
        self.assertEqual(data['summary']['average_rating'], 4.0)
