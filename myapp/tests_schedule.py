import json
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import CustomUser, QuickService, ServiceBooking, VendorProfile
from .schedule_services import DAY_KEYS, default_schedule


class VendorScheduleApiTests(TestCase):
    def setUp(self):
        self.vendor = CustomUser.objects.create_user(
            username='schedule_vendor', password='pass12345', role='VENDOR'
        )
        self.profile = VendorProfile.objects.create(
            user=self.vendor, location='Ranchi', company_name='Schedule Services'
        )
        self.customer = CustomUser.objects.create_user(
            username='schedule_customer', password='pass12345', role='USER'
        )
        self.service = QuickService.objects.create(
            vendor=self.vendor, title='Scheduled Service', base_price=500
        )

    def future_date_for_day(self, day_key):
        target_index = DAY_KEYS.index(day_key)
        candidate = timezone.now().date() + timedelta(days=1)
        while candidate.weekday() != target_index:
            candidate += timedelta(days=1)
        return candidate

    def custom_schedule(self, day_key, max_bookings=1):
        schedule = default_schedule()
        for key in DAY_KEYS:
            schedule['days'][key] = {'active': False, 'slots': []}
        schedule['days'][day_key] = {
            'active': True,
            'slots': [{'start': '09:00', 'end': '11:30', 'max_bookings': max_bookings}],
        }
        return schedule

    def test_vendor_can_save_and_retrieve_schedule(self):
        schedule = self.custom_schedule('monday', max_bookings=3)
        self.client.force_login(self.vendor)

        response = self.client.post(
            '/api/vendor/schedule/',
            data=json.dumps({'schedule': schedule}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['customized'])
        self.assertEqual(
            response.json()['schedule']['days']['monday']['slots'][0]['max_bookings'], 3
        )

        response = self.client.get('/api/vendor/schedule/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['using_fallback'])

    def test_vendor_schedule_dashboard_renders(self):
        self.client.force_login(self.vendor)
        response = self.client.get('/vendor/schedule/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Working Hours &amp; Time Slots')

    def test_invalid_overlapping_slots_are_rejected(self):
        schedule = self.custom_schedule('monday')
        schedule['days']['monday']['slots'].append(
            {'start': '10:00', 'end': '12:00', 'max_bookings': 1}
        )
        self.client.force_login(self.vendor)
        response = self.client.post(
            '/api/vendor/schedule/', data=json.dumps(schedule), content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('overlapping', response.json()['message'])

    def test_vendor_can_save_schedule_as_multipart_form_data(self):
        schedule = self.custom_schedule('friday', max_bookings=2)
        self.client.force_login(self.vendor)
        response = self.client.post(
            '/api/vendor/schedule/',
            data={'schedule': json.dumps(schedule)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()['schedule']['days']['friday']['slots'][0]['max_bookings'], 2
        )

    def test_vendor_can_save_flat_multipart_schedule_fields(self):
        self.client.force_login(self.vendor)
        response = self.client.post('/api/vendor/schedule/', data={
            'slot_duration_minutes': '90',
            'monday_active': 'true',
            'monday_slots': json.dumps([
                {'start': '09:00', 'end': '10:30', 'max_bookings': 2}
            ]),
            'tuesday_active': 'false',
            'days_off': json.dumps(['2026-12-25']),
            'unavailable_slots': json.dumps([
                {'date': '2026-12-26', 'start': '09:00'}
            ]),
        })
        self.assertEqual(response.status_code, 200)
        saved = response.json()['schedule']
        self.assertEqual(saved['slot_duration_minutes'], 90)
        self.assertTrue(saved['days']['monday']['active'])
        self.assertEqual(saved['days_off'], ['2026-12-25'])

    def test_public_api_uses_platform_fallback(self):
        requested_date = timezone.now().date() + timedelta(days=2)
        response = self.client.get(
            f'/api/vendor/{self.vendor.id}/available-slots/?date={requested_date}'
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['using_fallback'])
        self.assertEqual(len(data['slots']), 5)

    def test_day_off_and_individual_unavailable_slot(self):
        requested_date = self.future_date_for_day('monday')
        schedule = self.custom_schedule('monday')
        schedule['days_off'] = [requested_date.isoformat()]
        self.profile.working_hours = schedule
        self.profile.save(update_fields=['working_hours'])

        response = self.client.get(
            f'/api/vendor/{self.vendor.id}/available-slots/?date={requested_date}'
        )
        self.assertFalse(response.json()['is_working'])
        self.assertEqual(response.json()['reason'], 'day_off')
        self.assertEqual(response.json()['slots'], [])

        schedule['days_off'] = []
        schedule['unavailable_slots'] = [
            {'date': requested_date.isoformat(), 'start': '09:00'}
        ]
        self.profile.working_hours = schedule
        self.profile.save(update_fields=['working_hours'])
        response = self.client.get(
            f'/api/vendor/{self.vendor.id}/available-slots/?date={requested_date}'
        )
        self.assertEqual(response.json()['slots'][0]['status'], 'unavailable')

    def test_booked_capacity_is_reported_and_enforced(self):
        requested_date = self.future_date_for_day('tuesday')
        schedule = self.custom_schedule('tuesday', max_bookings=1)
        self.profile.working_hours = schedule
        self.profile.save(update_fields=['working_hours'])
        ServiceBooking.objects.create(
            customer=self.customer,
            vendor=self.vendor,
            quick_service=self.service,
            package_name='Existing',
            total_amount=500,
            scheduled_date=requested_date,
            scheduled_time='09:00',
            service_address='Ranchi',
        )

        response = self.client.get(
            f'/api/vendor/{self.vendor.id}/available-slots/?date={requested_date}'
        )
        slot = response.json()['slots'][0]
        self.assertEqual(slot['status'], 'full')
        self.assertEqual(slot['booked_count'], 1)

        self.client.force_login(self.customer)
        response = self.client.post(
            '/api/user/services/book/',
            data=json.dumps({
                'qs_id': self.service.id,
                'scheduled_date': requested_date.isoformat(),
                'scheduled_time': '09:00 AM',
                'service_address': 'Customer address',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn('booked / full', response.json()['message'])

    def test_today_slots_that_have_started_are_past(self):
        today = timezone.now().date()
        day_key = DAY_KEYS[today.weekday()]
        schedule = self.custom_schedule(day_key)
        schedule['days'][day_key]['slots'] = [
            {'start': '00:00', 'end': '00:15', 'max_bookings': 1}
        ]
        self.profile.working_hours = schedule
        self.profile.save(update_fields=['working_hours'])

        response = self.client.get(
            f'/api/vendor/{self.vendor.id}/available-slots/?date={today}'
        )
        self.assertEqual(response.json()['slots'][0]['status'], 'past')
