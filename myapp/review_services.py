"""
Review helpers shared by the web dashboard and the mobile/REST APIs.

Rules
-----
* Only the customer who made a booking can review it.
* A booking can only be reviewed once it is ``completed``.
* One review per booking (re-submitting updates the existing review).
* Vendors only ever see a masked customer name.
"""
from django.db.models import Avg, Count

from .models import ServiceBooking, ServiceReview

UNLOCKED_BOOKING_STATUSES = ('accepted', 'completed')


class ReviewError(Exception):
    """Raised for validation problems; ``status`` is the suggested HTTP code."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def booking_contact_unlocked(booking):
    """Customer identity / location may be shown to the vendor only after accept."""
    return booking.status in UNLOCKED_BOOKING_STATUSES


def mask_customer_name(user):
    """'Rahul Patil' -> 'Rahul P.'  (never exposes the full name to vendors)."""
    full = (user.get_full_name() or user.username or 'Customer').strip()
    parts = full.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[-1][0].upper()}."
    return parts[0] if parts else 'Customer'


def submit_booking_review(customer, booking_id=None, job_id=None, rating=5, comment='', title='', image=None):
    """Create or update the review for a completed booking or job. Returns (review, created)."""
    if not booking_id and not job_id:
        raise ReviewError('Either booking_id or job_id must be provided.', 400)

    booking = None
    job = None
    vendor = None
    quick_service = None

    if booking_id:
        try:
            booking = ServiceBooking.objects.select_related('vendor', 'quick_service').get(id=booking_id)
        except (ServiceBooking.DoesNotExist, ValueError, TypeError):
            raise ReviewError('Booking not found.', 404)

        if booking.customer_id != customer.id:
            raise ReviewError('You can only review your own bookings.', 403)
        if booking.status != 'completed':
            raise ReviewError('You can review a service only after it has been completed.', 400)
        vendor = booking.vendor
        quick_service = booking.quick_service

    elif job_id:
        from .models import Job
        try:
            job = Job.objects.select_related('assigned_vendor').get(id=job_id)
        except (Job.DoesNotExist, ValueError, TypeError):
            raise ReviewError('Job not found.', 404)

        if job.user_id != customer.id:
            raise ReviewError('You can only review your own jobs.', 403)
        if job.status not in ('completed', 'closed'):
            raise ReviewError('You can review a job only after it has been completed or closed.', 400)
        if not job.assigned_vendor:
            raise ReviewError('This job has no assigned vendor.', 400)
        vendor = job.assigned_vendor

    try:
        rating = int(rating)
    except (ValueError, TypeError):
        raise ReviewError('Rating must be a number between 1 and 5.')
    if rating < 1 or rating > 5:
        raise ReviewError('Rating must be between 1 and 5.')

    comment = (comment or '').strip()
    title = (title or '').strip()[:200]

    defaults = {
        'customer': customer,
        'vendor': vendor,
        'quick_service': quick_service,
        'rating': rating,
        'review_title': title,
        'comment': comment,
        'status': 'published',
    }
    if image:
        defaults['review_image'] = image

    if booking:
        review, created = ServiceReview.objects.update_or_create(booking=booking, defaults=defaults)
    else:
        review, created = ServiceReview.objects.update_or_create(job=job, defaults=defaults)
        
    return review, created


def vendor_review_summary(vendor):
    """Average, total and 1-5 star breakdown over the vendor's published reviews."""
    qs = ServiceReview.objects.filter(vendor=vendor, status='published')
    agg = qs.aggregate(avg=Avg('rating'), total=Count('id'))
    breakdown = {str(i): 0 for i in range(1, 6)}
    for row in qs.values('rating').annotate(c=Count('id')):
        key = str(row['rating'])
        if key in breakdown:
            breakdown[key] = row['c']
    return {
        'average_rating': round(agg['avg'], 1) if agg['avg'] else 0.0,
        'total_reviews': agg['total'] or 0,
        'breakdown': breakdown,
    }
