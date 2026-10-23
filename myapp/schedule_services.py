"""Vendor schedule normalization and slot availability helpers."""

from copy import deepcopy
from datetime import date, datetime

from django.db.models import Count
from django.utils import timezone

from .models import ServiceBooking


DAY_KEYS = (
    'monday', 'tuesday', 'wednesday', 'thursday',
    'friday', 'saturday', 'sunday',
)

STANDARD_SLOTS = (
    {'start': '09:00', 'end': '11:00', 'max_bookings': 1},
    {'start': '11:00', 'end': '13:00', 'max_bookings': 1},
    {'start': '14:00', 'end': '16:00', 'max_bookings': 1},
    {'start': '16:00', 'end': '18:00', 'max_bookings': 1},
    {'start': '18:30', 'end': '20:30', 'max_bookings': 1},
)


class ScheduleValidationError(ValueError):
    pass


def _parse_time(value, field_name='time'):
    if not isinstance(value, str):
        raise ScheduleValidationError(f'{field_name} must use HH:MM 24-hour format.')
    try:
        return datetime.strptime(value.strip(), '%H:%M').time()
    except ValueError as exc:
        raise ScheduleValidationError(
            f'{field_name} must use HH:MM 24-hour format.'
        ) from exc


def _parse_date(value, field_name='date'):
    if not isinstance(value, str):
        raise ScheduleValidationError(f'{field_name} must use YYYY-MM-DD format.')
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise ScheduleValidationError(
            f'{field_name} must use YYYY-MM-DD format.'
        ) from exc


def format_slot_label(start, end):
    start_time = _parse_time(start, 'slot start')
    end_time = _parse_time(end, 'slot end')
    return (
        f"{start_time.strftime('%I:%M %p')} - "
        f"{end_time.strftime('%I:%M %p')}"
    )


def default_schedule():
    """Return the platform fallback schedule without marking it customized."""
    slots = [dict(slot) for slot in STANDARD_SLOTS]
    return {
        'version': 1,
        'timezone': 'Asia/Kolkata',
        'slot_duration_minutes': 120,
        'days': {
            day: {'active': True, 'slots': deepcopy(slots)}
            for day in DAY_KEYS
        },
        'days_off': [],
        'unavailable_slots': [],
    }


def normalize_schedule(payload):
    """Validate and return the canonical JSON representation of a schedule."""
    if not isinstance(payload, dict):
        raise ScheduleValidationError('Schedule must be a JSON object.')

    source_days = payload.get('days')
    if not isinstance(source_days, dict):
        raise ScheduleValidationError('days must be an object keyed Monday through Sunday.')

    try:
        duration = int(payload.get('slot_duration_minutes', 120))
    except (TypeError, ValueError) as exc:
        raise ScheduleValidationError('slot_duration_minutes must be a number.') from exc
    if duration < 15 or duration > 720:
        raise ScheduleValidationError('slot_duration_minutes must be between 15 and 720.')

    days = {}
    for day in DAY_KEYS:
        day_data = source_days.get(day, {})
        if not isinstance(day_data, dict):
            raise ScheduleValidationError(f'{day} must be an object.')
        active = bool(day_data.get('active', False))
        source_slots = day_data.get('slots', [])
        if not isinstance(source_slots, list):
            raise ScheduleValidationError(f'{day}.slots must be a list.')

        slots = []
        starts = set()
        for index, raw_slot in enumerate(source_slots):
            if not isinstance(raw_slot, dict):
                raise ScheduleValidationError(f'{day} slot {index + 1} must be an object.')
            start = str(raw_slot.get('start', '')).strip()
            end = str(raw_slot.get('end', '')).strip()
            start_time = _parse_time(start, f'{day} slot {index + 1} start')
            end_time = _parse_time(end, f'{day} slot {index + 1} end')
            if end_time <= start_time:
                raise ScheduleValidationError(
                    f'{day} slot {index + 1} must end after it starts.'
                )
            if start in starts:
                raise ScheduleValidationError(f'{day} contains duplicate slot start {start}.')
            starts.add(start)
            try:
                maximum = int(raw_slot.get('max_bookings', 1))
            except (TypeError, ValueError) as exc:
                raise ScheduleValidationError(
                    f'{day} slot {index + 1} max_bookings must be a number.'
                ) from exc
            if maximum < 1 or maximum > 100:
                raise ScheduleValidationError('max_bookings must be between 1 and 100.')
            slots.append({'start': start, 'end': end, 'max_bookings': maximum})

        slots.sort(key=lambda item: item['start'])
        for previous, current in zip(slots, slots[1:]):
            if _parse_time(current['start']) < _parse_time(previous['end']):
                raise ScheduleValidationError(f'{day} contains overlapping time slots.')
        days[day] = {'active': active, 'slots': slots}

    days_off = payload.get('days_off', [])
    if not isinstance(days_off, list):
        raise ScheduleValidationError('days_off must be a list of YYYY-MM-DD dates.')
    clean_days_off = sorted({_parse_date(value, 'day off').isoformat() for value in days_off})

    unavailable = payload.get('unavailable_slots', [])
    if not isinstance(unavailable, list):
        raise ScheduleValidationError('unavailable_slots must be a list.')
    clean_unavailable = []
    seen_unavailable = set()
    for index, item in enumerate(unavailable):
        if not isinstance(item, dict):
            raise ScheduleValidationError(f'unavailable slot {index + 1} must be an object.')
        item_date = _parse_date(item.get('date'), 'unavailable slot date').isoformat()
        start = str(item.get('start', '')).strip()
        _parse_time(start, 'unavailable slot start')
        key = (item_date, start)
        if key not in seen_unavailable:
            clean_unavailable.append({'date': item_date, 'start': start})
            seen_unavailable.add(key)

    return {
        'version': 1,
        'timezone': 'Asia/Kolkata',
        'slot_duration_minutes': duration,
        'days': days,
        'days_off': clean_days_off,
        'unavailable_slots': clean_unavailable,
    }


def schedule_for_profile(profile):
    raw = profile.working_hours if isinstance(profile.working_hours, dict) else {}
    if not raw or not raw.get('days'):
        return default_schedule(), False
    try:
        return normalize_schedule(raw), True
    except ScheduleValidationError:
        # Old or malformed persisted data must never break customer checkout.
        return default_schedule(), False


def get_slot_availability(profile, requested_date):
    if isinstance(requested_date, str):
        requested_date = _parse_date(requested_date)

    schedule, customized = schedule_for_profile(profile)
    day_key = DAY_KEYS[requested_date.weekday()]
    day_schedule = schedule['days'][day_key]
    now = timezone.now()
    if timezone.is_aware(now):
        now = timezone.localtime(now)
    today = now.date()
    is_day_off = requested_date.isoformat() in schedule['days_off']
    is_working = bool(day_schedule['active']) and not is_day_off
    reason = None
    if is_day_off:
        reason = 'day_off'
    elif not day_schedule['active']:
        reason = 'not_working_day'
    elif requested_date < today:
        reason = 'past_date'

    booked_counts = {
        row['scheduled_time'].strftime('%H:%M'): row['count']
        for row in ServiceBooking.objects.filter(
            vendor=profile.user,
            scheduled_date=requested_date,
            scheduled_time__isnull=False,
        ).exclude(status='cancelled').values('scheduled_time').annotate(count=Count('id'))
    }
    unavailable = {
        (item.get('date'), item.get('start'))
        for item in schedule['unavailable_slots']
        if isinstance(item, dict)
    }
    now_time = now.time().replace(tzinfo=None)
    slot_results = []
    for slot in day_schedule['slots'] if is_working else []:
        start_time = _parse_time(slot['start'])
        booked = booked_counts.get(slot['start'], 0)
        is_past = requested_date < today or (
            requested_date == today and start_time <= now_time
        )
        is_unavailable = (requested_date.isoformat(), slot['start']) in unavailable
        is_full = booked >= slot['max_bookings']
        if is_past:
            status = 'past'
        elif is_unavailable:
            status = 'unavailable'
        elif is_full:
            status = 'full'
        else:
            status = 'available'
        slot_results.append({
            **slot,
            'label': format_slot_label(slot['start'], slot['end']),
            'booked_count': booked,
            'remaining_capacity': max(slot['max_bookings'] - booked, 0),
            'status': status,
            'available': status == 'available',
        })

    return {
        'date': requested_date.isoformat(),
        'day': day_key,
        'is_working': is_working and requested_date >= today,
        'reason': reason,
        'customized': customized,
        'using_fallback': not customized,
        'slot_duration_minutes': schedule['slot_duration_minutes'],
        'slots': slot_results,
    }
