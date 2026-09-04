import re
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class PhoneEmailUsernameBackend(ModelBackend):
    """
    Custom authentication backend allowing users and vendors to log in with:
    - Username
    - Email address
    - Phone number (from UserProfile, with flexible formatting like +91, spaces, dashes)
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('phone') or kwargs.get('email')
        if not username or not password:
            return None

        identifier = str(username).strip()
        if not identifier:
            return None

        candidate_users = []

        # 1. Look up by exact username
        try:
            candidate_users.extend(User.objects.filter(username__iexact=identifier))
        except Exception:
            pass

        # 2. Look up by exact email
        try:
            candidate_users.extend(User.objects.filter(email__iexact=identifier))
        except Exception:
            pass

        # 3. Look up by phone number in UserProfile
        from myapp.models import UserProfile

        try:
            # Direct exact match on phone_number
            direct_profiles = UserProfile.objects.filter(phone_number__iexact=identifier).select_related('user')
            for p in direct_profiles:
                if p.user and p.user not in candidate_users:
                    candidate_users.append(p.user)

            # Digit normalization for phone number matching
            digits = re.sub(r'\D', '', identifier)
            if digits:
                core_digits = digits[-10:] if len(digits) >= 10 else digits

                # DB lookup for phone ending with core_digits
                if len(core_digits) >= 7:
                    ending_profiles = UserProfile.objects.filter(
                        Q(phone_number=digits) | Q(phone_number__endswith=core_digits)
                    ).select_related('user')
                    for p in ending_profiles:
                        if p.user and p.user not in candidate_users:
                            candidate_users.append(p.user)

                # Normalized comparison across non-empty phone profiles
                for p in UserProfile.objects.exclude(phone_number__isnull=True).exclude(phone_number='').select_related('user'):
                    p_val = p.phone_number or ''
                    p_digits = re.sub(r'\D', '', p_val)
                    if not p_digits:
                        continue
                    p_core = p_digits[-10:] if len(p_digits) >= 10 else p_digits
                    if len(p_core) >= 7 and (p_digits == digits or p_core == core_digits):
                        if p.user and p.user not in candidate_users:
                            candidate_users.append(p.user)
        except Exception:
            pass

        # Deduplicate candidates preserving order
        seen_ids = set()
        unique_candidates = []
        for u in candidate_users:
            if u.id not in seen_ids:
                seen_ids.add(u.id)
                unique_candidates.append(u)

        # Authenticate against candidate users
        for u in unique_candidates:
            if u.check_password(password) and self.user_can_authenticate(u):
                return u

        return None
