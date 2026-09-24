import json
import re
import random
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

from .models import UserProfile, VendorProfile, Category, Location, OTPVerification, AuthToken, Job, QuickService

User = get_user_model()


# =====================================================================
# REQUEST PARSING, PHONE NORMALIZATION & IDENTIFIER HELPERS
# =====================================================================

def _parse_api_request(request):
    """
    Parses incoming request payload whether provided as:
    - application/json (raw JSON body)
    - multipart/form-data (form uploads)
    - application/x-www-form-urlencoded (standard POST form)
    - query parameters (GET fallback)
    """
    data = {}
    if request.body:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            pass
    if not data:
        data = request.POST.dict()
    if not data and request.GET:
        data = request.GET.dict()
    return data


def _normalize_phone(phone):
    """
    Normalizes a phone number by stripping spaces, special chars,
    and removing leading Indian country code (+91 / 91) or leading 0.
    """
    if not phone:
        return ""
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 12 and digits.startswith('91'):
        return digits[2:]
    if len(digits) == 11 and digits.startswith('0'):
        return digits[1:]
    return digits


def _resolve_user_identifier(identifier):
    """
    Resolves a user record using either:
    1. Exact Username
    2. Email address
    3. Mobile phone number (from UserProfile, with normalization)
    """
    if not identifier:
        return None
    ident = str(identifier).strip()

    # 1. By username
    user = User.objects.filter(username__iexact=ident).first()
    if user:
        return user

    # 2. By email
    user = User.objects.filter(email__iexact=ident).first()
    if user:
        return user

    # 3. By mobile number in UserProfile (supports normalized search)
    norm_phone = _normalize_phone(ident)
    query = Q(phone_number__iexact=ident)
    if norm_phone:
        query |= Q(phone_number__iexact=norm_phone) | Q(phone_number__endswith=norm_phone)
    u_prof = UserProfile.objects.filter(query).select_related('user').first()
    if u_prof and u_prof.user:
        return u_prof.user

    return None


def _get_or_create_auth_token(user):
    """
    Retrieves or generates an active Bearer authentication token for the given user.
    """
    token = AuthToken.objects.filter(user=user).order_by('-created_at').first()
    if not token:
        token = AuthToken.objects.create(user=user)
    return token.key


def _get_user_from_bearer_token(request):
    """
    Extracts and validates the Bearer token from the HTTP_AUTHORIZATION header.
    Supported Header format:
        Authorization: Bearer <token>
        Authorization: Token <token>
    Fallback:
        Query or Body parameter 'token' / 'bearer_token'
    Returns: (user_or_None, error_message_or_None)
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    token_key = ''
    if auth_header:
        parts = auth_header.strip().split()
        if len(parts) == 2 and parts[0].lower() in ['bearer', 'token']:
            token_key = parts[1]
        elif len(parts) == 1:
            token_key = parts[0]
        else:
            return None, "Invalid Authorization header format. Expected 'Bearer <token>'."
    else:
        # Fallback to query param or body
        token_key = request.GET.get('token') or request.POST.get('token')
        if not token_key and hasattr(request, 'body'):
            try:
                body_data = json.loads(request.body.decode('utf-8'))
                token_key = body_data.get('token') or body_data.get('bearer_token')
            except Exception:
                pass

    if not token_key:
        return None, "Authorization header with Bearer token is required."

    token_obj = AuthToken.objects.filter(key=token_key).select_related('user').first()
    if not token_obj:
        return None, "Invalid or expired Bearer token."

    if not token_obj.user.is_active:
        return None, "User account is suspended or inactive."

    return token_obj.user, None



def _generate_otp(mobile, purpose='general'):
    """
    Generates a 6-digit random OTP and stores it in OTPVerification.
    Returns the created OTPVerification instance.
    """
    norm_phone = _normalize_phone(mobile) or str(mobile).strip()
    otp_code = f"{random.randint(100000, 999999):06d}"
    expires_at = timezone.now() + timedelta(minutes=10)
    record = OTPVerification.objects.create(
        mobile=norm_phone,
        otp=otp_code,
        purpose=purpose,
        expires_at=expires_at
    )
    # Print OTP in terminal
    print("\n" + "=" * 45, flush=True)
    print(f" >>> OTP GENERATED FOR: {norm_phone} <<<", flush=True)
    print(f" >>> YOUR OTP IS: {otp_code} <<<", flush=True)
    print(f" Purpose: {purpose} | Expires in: 10 mins", flush=True)
    print("=" * 45 + "\n", flush=True)

    return record


def _verify_otp_code(mobile, otp, purpose=None, allow_already_verified=True):
    """
    Validates the provided OTP.
    Accepts master demo OTP '123456' for immediate testing / development.
    Supports both fresh unverified OTPs and recently verified active OTPs
    (for multi-step flows like Verify OTP -> Sign Up).
    Returns (success_boolean, message).
    """
    norm_phone = _normalize_phone(mobile) or str(mobile).strip()
    otp_str = str(otp).strip()

    if not otp_str:
        return False, "OTP is required."

    # Master development / demo bypass
    if otp_str == '123456':
        print(f"\n[OTP VERIFIED] Mobile: {norm_phone} | Code: 123456 (Master Bypass)\n", flush=True)
        return True, "Verified (Master/Demo OTP)"

    now = timezone.now()

    # 1. Look for unverified active OTP
    query_unverified = OTPVerification.objects.filter(
        Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
        otp=otp_str,
        is_verified=False,
        expires_at__gte=now
    )
    if purpose:
        query_unverified = query_unverified.filter(Q(purpose=purpose) | Q(purpose='general'))

    record = query_unverified.order_by('-created_at').first()
    if record:
        record.is_verified = True
        record.save()
        print(f"\n[OTP VERIFIED] Mobile: {norm_phone} | Code: {otp_str} (Verified Successfully)\n", flush=True)
        return True, "OTP verified successfully."

    # 2. Check if this OTP was already verified within its active validity window
    # (e.g., client called /api/auth/verify-otp/ first, and is now calling /api/user/otp-signup/)
    if allow_already_verified:
        query_verified = OTPVerification.objects.filter(
            Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
            otp=otp_str,
            is_verified=True,
            expires_at__gte=now
        )
        if purpose:
            query_verified = query_verified.filter(Q(purpose=purpose) | Q(purpose='general'))

        v_record = query_verified.order_by('-created_at').first()
        if v_record:
            print(f"\n[OTP RE-VERIFIED] Mobile: {norm_phone} | Code: {otp_str} (Previously Verified & Still Active)\n", flush=True)
            return True, "OTP verified successfully."

    # 3. Purpose fallback: Check if OTP matches with ANY purpose before failing
    fallback_query = OTPVerification.objects.filter(
        Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
        otp=otp_str,
        expires_at__gte=now
    )
    fallback_record = fallback_query.order_by('-created_at').first()
    if fallback_record:
        fallback_record.is_verified = True
        fallback_record.save()
        print(f"\n[OTP VERIFIED] Mobile: {norm_phone} | Code: {otp_str} (Matched with purpose '{fallback_record.purpose}')\n", flush=True)
        return True, "OTP verified successfully."

    # 4. Specific check for expired OTP
    expired_record = OTPVerification.objects.filter(
        Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
        otp=otp_str
    ).order_by('-created_at').first()
    if expired_record and expired_record.expires_at < now:
        print(f"\n[OTP FAILED] Mobile: {norm_phone} | Code: {otp_str} (Expired at {expired_record.expires_at})\n", flush=True)
        return False, "OTP has expired. Please request a new OTP."

    print(f"\n[OTP FAILED] Mobile: {norm_phone} | Code: {otp_str} (Invalid OTP)\n", flush=True)
    return False, "Invalid or expired OTP."



# =====================================================================
# 1. USER (CUSTOMER) AUTHENTICATION APIS
# =====================================================================

@csrf_exempt
@require_POST
def user_signup_api(request):
    """
    API for User / Customer Registration (Signup)
    URL: /api/user/signup/
    Method: POST
    """
    try:
        data = _parse_api_request(request)
        name = (data.get('name') or data.get('first_name') or '').strip()
        email = (data.get('email') or '').strip()
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone_number') or '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password')

        if not name:
            return JsonResponse({'status': 'error', 'message': "Field 'name' is required."}, status=400)
        if not email:
            return JsonResponse({'status': 'error', 'message': "Field 'email' is required."}, status=400)
        if not password:
            return JsonResponse({'status': 'error', 'message': "Field 'password' is required."}, status=400)
        if confirm_password and password != confirm_password:
            return JsonResponse({'status': 'error', 'message': "Passwords do not match."}, status=400)

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already registered."}, status=400)

        username = (data.get('username') or '').strip()
        if not username:
            base_username = email.split('@')[0] if '@' in email else name.replace(" ", "").lower()
            username = base_username
            counter = 1
            while User.objects.filter(username__iexact=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        elif User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'status': 'error', 'message': f"Username '{username}' is already taken."}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            first_name=name,
            role='USER'
        )
        user.set_password(password)
        user.save()

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        if mobile:
            user_profile.phone_number = mobile
            user_profile.save()

        code = f"USR{user.id:03d}"
        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"User '{name}' registered successfully",
            'token': token_key,
            'token_type': 'Bearer',
            'user': {
                'id': code,
                'user_id': user.id,
                'user_code': code,
                'name': name,
                'username': user.username,
                'email': user.email,
                'mobile': mobile or '—',
                'role': user.role
            }
        }
        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def user_login_api(request):
    """
    API for User / Customer Login
    URL: /api/user/login/
    Method: POST
    """
    try:
        data = _parse_api_request(request)
        identifier = (data.get('username') or data.get('email') or data.get('mobile') or data.get('contact') or '').strip()
        password = data.get('password', '')

        if not identifier or not password:
            return JsonResponse({'status': 'error', 'message': "Username/email/mobile and password are required."}, status=400)

        user = _resolve_user_identifier(identifier)
        if not user or not user.check_password(password):
            return JsonResponse({'status': 'error', 'message': "Invalid credentials."}, status=401)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "User account is suspended or inactive."}, status=403)

        if user.role not in ['USER', 'CUSTOMER'] and not user.is_superuser:
            return JsonResponse({'status': 'error', 'message': f"Access denied. Account is registered as {user.role}, not a customer user."}, status=403)

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        mobile = '—'
        try:
            if hasattr(user, 'user_profile') and user.user_profile.phone_number:
                mobile = user.user_profile.phone_number
        except Exception:
            pass

        full_name = user.get_full_name() or user.first_name or user.username
        code = f"USR{user.id:03d}"
        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"User '{full_name}' logged in successfully",
            'token': token_key,
            'token_type': 'Bearer',
            'user': {
                'id': code,
                'user_id': user.id,
                'user_code': code,
                'name': full_name,
                'username': user.username,
                'email': user.email or '—',
                'mobile': mobile,
                'role': user.role
            }
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# =====================================================================
# 2. VENDOR AUTHENTICATION APIS
# =====================================================================

@csrf_exempt
@require_POST
def vendor_signup_api(request):
    """
    API for Vendor Registration (Signup)
    URL: /api/vendor/signup/
    Method: POST
    """
    try:
        data = _parse_api_request(request)
        name = (data.get('name') or data.get('contact_name') or '').strip()
        company_name = (data.get('company_name') or name).strip()
        email = (data.get('email') or '').strip()
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone_number') or '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password')

        category = (data.get('category') or 'General Services').strip()
        city = (data.get('city') or '').strip()
        state = (data.get('state') or '').strip()
        location = f"{city}, {state}" if (city and state) else (data.get('location') or city or state or 'Ranchi, Jharkhand').strip()
        address = (data.get('address') or '').strip()
        vendor_type = (data.get('vendor_type') or ('company' if company_name else 'vendor')).strip()
        
        experience = data.get('experience', 0)
        try:
            experience = int(experience)
        except (ValueError, TypeError):
            experience = 0

        if not name:
            return JsonResponse({'status': 'error', 'message': "Field 'name' is required."}, status=400)
        if not email:
            return JsonResponse({'status': 'error', 'message': "Field 'email' is required."}, status=400)
        if not password:
            return JsonResponse({'status': 'error', 'message': "Field 'password' is required."}, status=400)
        if confirm_password and password != confirm_password:
            return JsonResponse({'status': 'error', 'message': "Passwords do not match."}, status=400)

        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already registered."}, status=400)

        username = (data.get('username') or '').strip()
        if not username:
            base_username = email.split('@')[0] if '@' in email else company_name.replace(" ", "").lower()
            username = base_username
            counter = 1
            while User.objects.filter(username__iexact=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        elif User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'status': 'error', 'message': f"Username '{username}' is already taken."}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            first_name=name,
            role='VENDOR'
        )
        user.set_password(password)
        user.save()

        vendor_profile = VendorProfile.objects.create(
            user=user,
            company_name=company_name,
            category=category,
            location=location,
            address=address,
            vendor_type=vendor_type,
            experience=experience
        )

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        if mobile:
            user_profile.phone_number = mobile
            user_profile.save()

        code = f"VEN{vendor_profile.id:03d}"
        display_name = company_name or name
        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"Vendor '{display_name}' registered successfully",
            'token': token_key,
            'token_type': 'Bearer',
            'vendor': {
                'id': code,
                'vendor_id': vendor_profile.id,
                'vendor_code': code,
                'user_id': user.id,
                'name': name,
                'company_name': company_name,
                'contact': mobile or '—',
                'mobile': mobile or '—',
                'email': user.email,
                'category': category,
                'location': location,
                'address': address or '—',
                'vendor_type': vendor_type,
                'experience': experience,
                'role': 'VENDOR'
            }
        }
        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def vendor_login_api(request):
    """
    API for Vendor Login
    URL: /api/vendor/login/
    Method: POST
    """
    try:
        data = _parse_api_request(request)
        identifier = (data.get('username') or data.get('email') or data.get('mobile') or data.get('contact') or '').strip()
        password = data.get('password', '')

        if not identifier or not password:
            return JsonResponse({'status': 'error', 'message': "Username/email/mobile and password are required."}, status=400)

        user = _resolve_user_identifier(identifier)
        if not user or not user.check_password(password):
            return JsonResponse({'status': 'error', 'message': "Invalid credentials."}, status=401)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "Vendor account is suspended or inactive."}, status=403)

        if user.role != 'VENDOR' and not user.is_superuser:
            return JsonResponse({'status': 'error', 'message': f"Access denied. Account is registered as {user.role}, not a vendor."}, status=403)

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        profile = getattr(user, 'vendor_profile', None)
        v_id = profile.id if profile else user.id
        code = f"VEN{v_id:03d}"
        company_name = (profile.company_name if profile and profile.company_name else user.get_full_name()) or user.username
        category = profile.category if profile else 'General'
        location = profile.location if profile else 'Unknown'
        address = profile.address if profile and profile.address else '—'
        vendor_type = profile.vendor_type if profile else 'vendor'
        experience = profile.experience if profile else 0

        mobile = '—'
        try:
            if hasattr(user, 'user_profile') and user.user_profile.phone_number:
                mobile = user.user_profile.phone_number
        except Exception:
            pass

        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"Vendor '{company_name}' logged in successfully",
            'token': token_key,
            'token_type': 'Bearer',
            'vendor': {
                'id': code,
                'vendor_id': v_id,
                'vendor_code': code,
                'user_id': user.id,
                'name': user.get_full_name() or user.username,
                'company_name': company_name,
                'contact': mobile,
                'mobile': mobile,
                'email': user.email or '—',
                'category': category,
                'location': location,
                'address': address,
                'vendor_type': vendor_type,
                'experience': experience,
                'role': 'VENDOR'
            }
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# =====================================================================
# 3. EXISTING MANAGEMENT APIS (Users, Categories, Nav)
# =====================================================================

@csrf_exempt
@require_POST
def add_user_api(request):
    try:
        data = _parse_api_request(request)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        mobile = data.get('mobile', '').strip()
        password = data.get('password', '').strip()

        if not name or not password:
            return JsonResponse({'success': False, 'error': 'Name and password are required.'})

        username = email if email else name.replace(" ", "").lower() + str(User.objects.count())

        if User.objects.filter(username=username).exists():
            import random
            username = username + str(random.randint(100, 999))

        user = User.objects.create(
            username=username,
            email=email,
            role='USER',
            first_name=name
        )
        user.set_password(password)
        
        # Tag with Area Admin's assigned state if created by an area admin
        if request.user.is_authenticated and request.user.role == 'ADMIN' and not request.user.is_superuser:
            user.assigned_state = request.user.assigned_state
        user.save()

        UserProfile.objects.create(user=user, phone_number=mobile)

        user_data = {
            'id': f'USR-{user.id:04d}',
            'name': name,
            'email': email or '—',
            'mobile': mobile or '—',
            'location': user.assigned_state or 'Unknown',
            'quickServices': 0,
            'jobs': 0,
            'completedJobs': 0,
            'status': 'active',
            'registered': user.date_joined.strftime('%Y-%m-%d')
        }

        return JsonResponse({'success': True, 'user': user_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def user_nav_data_api(request):
    if request.user.is_authenticated:
        u = request.user
        name = u.get_full_name() or u.username
        initials = (u.first_name[:1].upper() + u.last_name[:1].upper()) if u.first_name else u.username[:2].upper()
        return JsonResponse({'name': name, 'initials': initials})
    return JsonResponse({'name': 'Guest', 'initials': 'GU'})


@csrf_exempt
@require_POST
def add_category_api(request):
    try:
        data = _parse_api_request(request)
        name = data.get('name', '').strip()
        service_type = data.get('service_type', 'both')
        status = data.get('status', 'active')

        if not name:
            return JsonResponse({'success': False, 'error': 'Name is required.'})

        cat = Category.objects.create(
            name=name,
            service_type=service_type,
            status=status
        )

        cat_data = {
            'id': cat.id,
            'name': cat.name,
            'service_type': cat.service_type,
            'status': cat.status,
            'created_at': cat.created_at.strftime('%Y-%m-%d')
        }

        return JsonResponse({'success': True, 'category': cat_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def update_category_api(request):
    try:
        data = _parse_api_request(request)
        cat_id = data.get('id')
        name = data.get('name', '').strip()
        service_type = data.get('service_type', 'both')
        status = data.get('status', 'active')

        if not cat_id or not name:
            return JsonResponse({'success': False, 'error': 'ID and Name are required.'})

        cat = Category.objects.get(id=cat_id)
        cat.name = name
        cat.service_type = service_type
        cat.status = status
        cat.save()

        cat_data = {
            'id': cat.id,
            'name': cat.name,
            'service_type': cat.service_type,
            'status': cat.status,
            'created_at': cat.created_at.strftime('%Y-%m-%d')
        }

        return JsonResponse({'success': True, 'category': cat_data})
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_POST
def delete_category_api(request):
    try:
        data = _parse_api_request(request)
        cat_id = data.get('id')

        if not cat_id:
            return JsonResponse({'success': False, 'error': 'ID is required.'})

        cat = Category.objects.get(id=cat_id)
        cat.delete()

        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# =====================================================================
# 4. UNIFIED AUTH & OTP APIS
# =====================================================================

@csrf_exempt
@require_POST
def unified_login_api(request):
    """
    API for Unified Login (Username / Email / Mobile + Password)
    URL: /api/auth/login/
    Method: POST
    Params: username or mobile or email (required), password (required)
    """
    try:
        data = _parse_api_request(request)
        identifier = (data.get('username') or data.get('email') or data.get('mobile') or data.get('contact') or '').strip()
        password = data.get('password', '')

        if not identifier or not password:
            return JsonResponse({'status': 'error', 'message': "Username/email/mobile and password are required."}, status=400)

        user = _resolve_user_identifier(identifier)
        if not user or not user.check_password(password):
            return JsonResponse({'status': 'error', 'message': "Invalid credentials."}, status=401)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "Account is suspended or inactive."}, status=403)

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        role = user.role
        redirect_url = '/admin-dashboard' if (role == 'ADMIN' or user.is_superuser) else ('/vendor/dashboard' if role == 'VENDOR' else '/user/dashboard')
        full_name = user.get_full_name() or user.first_name or user.username
        code = f"VEN{user.vendor_profile.id:03d}" if hasattr(user, 'vendor_profile') else f"USR{user.id:03d}"
        token_key = _get_or_create_auth_token(user)

        return JsonResponse({
            'status': 'success',
            'message': f"Welcome back, {full_name}!",
            'redirect_url': redirect_url,
            'token': token_key,
            'token_type': 'Bearer',
            'user': {
                'id': code,
                'user_id': user.id,
                'name': full_name,
                'username': user.username,
                'email': user.email or '—',
                'role': role
            }
        }, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def unified_otp_login_api(request):
    """
    API for Unified OTP Login (Mobile + OTP)
    URL: /api/auth/otp-login/
    Method: POST
    Params: mobile (required), otp (required)
    """
    try:
        data = _parse_api_request(request)
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone') or data.get('phone_number') or '').strip()
        otp = (data.get('otp') or data.get('otp_code') or data.get('code') or '').strip()

        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)
        if not otp:
            return JsonResponse({'status': 'error', 'message': "Field 'otp' is required."}, status=400)

        # 1. Verify OTP (allows already verified active OTP)
        is_valid, msg = _verify_otp_code(mobile, otp, purpose='login', allow_already_verified=True)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        # 2. Find user by mobile
        user = _resolve_user_identifier(mobile)
        if not user:
            return JsonResponse({
                'status': 'error',
                'message': f"No account found with mobile number '{mobile}'. Please sign up first."
            }, status=404)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "Account is suspended or inactive."}, status=403)

        # Invalidate the OTP so it cannot be reused
        norm_phone = _normalize_phone(mobile)
        OTPVerification.objects.filter(
            Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
            otp=otp
        ).update(is_verified=True, expires_at=timezone.now())

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        role = user.role
        redirect_url = '/admin-dashboard' if (role == 'ADMIN' or user.is_superuser) else ('/vendor/dashboard' if role == 'VENDOR' else '/user/dashboard')
        full_name = user.get_full_name() or user.first_name or user.username
        code = f"VEN{user.vendor_profile.id:03d}" if hasattr(user, 'vendor_profile') else f"USR{user.id:03d}"
        token_key = _get_or_create_auth_token(user)

        return JsonResponse({
            'status': 'success',
            'message': f"Welcome back, {full_name}!",
            'redirect_url': redirect_url,
            'token': token_key,
            'token_type': 'Bearer',
            'user': {
                'id': code,
                'user_id': user.id,
                'name': full_name,
                'username': user.username,
                'email': user.email or '—',
                'mobile': mobile,
                'role': role
            }
        }, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def check_phone_api(request):
    """
    API to Check if a Phone Number is Already Registered or Not
    URL: /api/auth/check-phone/
    Method: POST or GET
    Params: mobile (required), role (optional: 'USER', 'VENDOR')
    """
    try:
        data = _parse_api_request(request)
        mobile = (
            data.get('mobile') or 
            data.get('phone') or 
            data.get('phone_number') or 
            data.get('contact') or ''
        ).strip()
        role = (data.get('role') or '').strip().upper()

        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' or 'phone' is required."}, status=400)

        norm_phone = _normalize_phone(mobile)
        if len(norm_phone) < 10:
            return JsonResponse({'status': 'error', 'message': "Please enter a valid 10-digit mobile number."}, status=400)

        # Search UserProfile by normalized or exact phone number
        query = Q(phone_number__iexact=mobile)
        if norm_phone:
            query |= Q(phone_number__iexact=norm_phone) | Q(phone_number__endswith=norm_phone)

        u_prof = UserProfile.objects.filter(query).select_related('user').first()
        user = u_prof.user if (u_prof and u_prof.user) else None

        if not user:
            # Fallback check in CustomUser if username matches phone
            user = User.objects.filter(
                Q(username__iexact=mobile) | 
                Q(username__iexact=f"usr_{norm_phone}") | 
                Q(username__iexact=f"ven_{norm_phone}")
            ).first()

        if user:
            code = f"VEN{user.vendor_profile.id:03d}" if hasattr(user, 'vendor_profile') else f"USR{user.id:03d}"
            full_name = user.get_full_name() or user.first_name or user.username

            res = {
                'status': 'success',
                'is_registered': True,
                'mobile': mobile,
                'message': f"Phone number '{mobile}' is already registered.",
                'user': {
                    'user_id': user.id,
                    'user_code': code,
                    'name': full_name,
                    'role': user.role,
                    'email': user.email or '—'
                }
            }
            if role:
                res['matches_role'] = (user.role == role or user.is_superuser)
                if user.role != role and not user.is_superuser:
                    res['message'] = f"Phone number '{mobile}' is registered as a {user.role}, not {role}."
            return JsonResponse(res, status=200)
        else:
            return JsonResponse({
                'status': 'success',
                'is_registered': False,
                'mobile': mobile,
                'message': f"Phone number '{mobile}' is not registered."
            }, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def send_otp_api(request):
    """
    API for Sending OTP to Mobile Number
    URL: /api/auth/send-otp/
    Method: POST
    Params: mobile (required), purpose (optional: 'login', 'signup', 'general', default: 'general'), role (optional: 'USER', 'VENDOR')
    """
    try:
        data = _parse_api_request(request)
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone_number') or '').strip()
        purpose = (data.get('purpose') or 'general').strip().lower()
        role = (data.get('role') or '').strip().upper()

        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)

        norm_phone = _normalize_phone(mobile)
        if len(norm_phone) < 10:
            return JsonResponse({'status': 'error', 'message': "Please enter a valid 10-digit mobile number."}, status=400)

        existing_user = _resolve_user_identifier(mobile)

        if purpose == 'login':
            if not existing_user:
                return JsonResponse({
                    'status': 'error',
                    'message': f"No registered account found with mobile number '{mobile}'. Please sign up first."
                }, status=404)
            if role and existing_user.role != role and not existing_user.is_superuser:
                return JsonResponse({
                    'status': 'error',
                    'message': f"Account is registered as {existing_user.role}, not {role}."
                }, status=403)

        elif purpose == 'signup':
            if existing_user:
                return JsonResponse({
                    'status': 'error',
                    'message': f"Mobile number '{mobile}' is already registered with an existing account. Please log in."
                }, status=400)

        otp_record = _generate_otp(mobile, purpose=purpose)

        return JsonResponse({
            'status': 'success',
            'message': f"OTP sent successfully to {mobile}",
            'mobile': mobile,
            'otp': otp_record.otp,
            'purpose': purpose,
            'expires_in_minutes': 10
        }, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def verify_otp_api(request):
    """
    API for Verifying OTP
    URL: /api/auth/verify-otp/
    Method: POST
    Params: mobile (required), otp (required), purpose (optional)
    """
    try:
        data = _parse_api_request(request)
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone') or data.get('phone_number') or '').strip()
        otp = (data.get('otp') or data.get('otp_code') or data.get('code') or '').strip()
        purpose = data.get('purpose')

        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)
        if not otp:
            return JsonResponse({'status': 'error', 'message': "Field 'otp' is required."}, status=400)

        is_valid, msg = _verify_otp_code(mobile, otp, purpose=purpose, allow_already_verified=True)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        return JsonResponse({
            'status': 'success',
            'message': msg,
            'mobile': mobile,
            'is_verified': True
        }, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# =====================================================================
# 5. USER OTP SIGNUP & LOGIN APIS
# =====================================================================

@csrf_exempt
@require_POST
def user_otp_signup_api(request):
    """
    API for User / Customer Registration with OTP
    URL: /api/user/otp-signup/
    Method: POST
    Params: name (required), mobile (required), otp (required), email (optional), password (optional)
    """
    try:
        data = _parse_api_request(request)
        name = (data.get('name') or data.get('first_name') or data.get('full_name') or '').strip()
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone') or data.get('phone_number') or '').strip()
        otp = (data.get('otp') or data.get('otp_code') or data.get('code') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password', '')

        if not name:
            return JsonResponse({'status': 'error', 'message': "Field 'name' is required."}, status=400)
        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)
        if not otp:
            return JsonResponse({'status': 'error', 'message': "Field 'otp' is required."}, status=400)

        norm_phone = _normalize_phone(mobile)
        if len(norm_phone) < 10:
            return JsonResponse({'status': 'error', 'message': "Please enter a valid 10-digit mobile number."}, status=400)

        # 1. Verify OTP (allows already-verified active OTPs from multi-step verify -> signup flows)
        is_valid, msg = _verify_otp_code(mobile, otp, purpose='signup', allow_already_verified=True)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        # 2. Check if mobile already registered
        existing_user = _resolve_user_identifier(mobile)
        if existing_user:
            return JsonResponse({
                'status': 'error',
                'message': f"Mobile number '{mobile}' is already registered with an existing account. Please log in."
            }, status=400)

        # 3. Check / generate email
        if email:
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already registered."}, status=400)
        else:
            email = f"user_{norm_phone}@infinityventures.local"

        # 4. Generate unique username
        username = (data.get('username') or '').strip()
        if not username:
            base_username = f"usr_{norm_phone}"
            username = base_username
            counter = 1
            while User.objects.filter(username__iexact=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
        elif User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'status': 'error', 'message': f"Username '{username}' is already taken."}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            first_name=name,
            role='USER'
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        user_profile.phone_number = mobile
        user_profile.save()

        # Invalidate / consume the used OTP so it cannot be reused
        OTPVerification.objects.filter(
            Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
            otp=otp
        ).update(is_verified=True, expires_at=timezone.now())

        # Session login
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        code = f"USR{user.id:03d}"
        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"User '{name}' registered and logged in successfully via OTP",
            'token': token_key,
            'token_type': 'Bearer',
            'user': {
                'id': code,
                'user_id': user.id,
                'user_code': code,
                'name': name,
                'username': user.username,
                'email': user.email,
                'mobile': mobile,
                'role': 'USER'
            }
        }
        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def user_otp_login_api(request):
    """
    API for User / Customer Login with OTP
    URL: /api/user/otp-login/
    Method: POST
    Params: mobile (required), otp (required)
    """
    try:
        data = _parse_api_request(request)
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone') or data.get('phone_number') or '').strip()
        otp = (data.get('otp') or data.get('otp_code') or data.get('code') or '').strip()

        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)
        if not otp:
            return JsonResponse({'status': 'error', 'message': "Field 'otp' is required."}, status=400)

        # 1. Verify OTP (allows already verified active OTP)
        is_valid, msg = _verify_otp_code(mobile, otp, purpose='login', allow_already_verified=True)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        # 2. Find user by mobile
        user = _resolve_user_identifier(mobile)
        if not user:
            return JsonResponse({
                'status': 'error',
                'message': f"No account found with mobile number '{mobile}'. Please sign up first."
            }, status=404)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "User account is suspended or inactive."}, status=403)

        if user.role not in ['USER', 'CUSTOMER'] and not user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': f"Access denied. Account is registered as {user.role}, not a customer user."
            }, status=403)

        # Invalidate the OTP so it cannot be reused
        norm_phone = _normalize_phone(mobile)
        OTPVerification.objects.filter(
            Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
            otp=otp
        ).update(is_verified=True, expires_at=timezone.now())

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        full_name = user.get_full_name() or user.first_name or user.username
        code = f"USR{user.id:03d}"
        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"User '{full_name}' logged in successfully via OTP",
            'token': token_key,
            'token_type': 'Bearer',
            'user': {
                'id': code,
                'user_id': user.id,
                'user_code': code,
                'name': full_name,
                'username': user.username,
                'email': user.email or '—',
                'mobile': mobile,
                'role': user.role
            }
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# =====================================================================
# 6. VENDOR OTP SIGNUP & LOGIN APIS
# =====================================================================

@csrf_exempt
@require_POST
def vendor_otp_signup_api(request):
    """
    API for Vendor Registration with OTP
    URL: /api/vendor/otp-signup/
    Method: POST
    Params: name (required), mobile (required), otp (required), company_name (optional), category (optional), location (optional)
    """
    try:
        data = _parse_api_request(request)
        name = (data.get('name') or data.get('contact_name') or data.get('first_name') or data.get('full_name') or '').strip()
        company_name = (data.get('company_name') or name).strip()
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone') or data.get('phone_number') or '').strip()
        otp = (data.get('otp') or data.get('otp_code') or data.get('code') or '').strip()
        email = (data.get('email') or '').strip()
        password = data.get('password', '')

        category = (data.get('category') or 'General Services').strip()
        city = (data.get('city') or '').strip()
        state = (data.get('state') or '').strip()
        location = f"{city}, {state}" if (city and state) else (data.get('location') or city or state or 'Ranchi, Jharkhand').strip()
        address = (data.get('address') or '').strip()
        vendor_type = (data.get('vendor_type') or ('company' if company_name else 'vendor')).strip()

        experience = data.get('experience', 0)
        try:
            experience = int(experience)
        except (ValueError, TypeError):
            experience = 0

        if not name:
            return JsonResponse({'status': 'error', 'message': "Field 'name' is required."}, status=400)
        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)
        if not otp:
            return JsonResponse({'status': 'error', 'message': "Field 'otp' is required."}, status=400)

        norm_phone = _normalize_phone(mobile)
        if len(norm_phone) < 10:
            return JsonResponse({'status': 'error', 'message': "Please enter a valid 10-digit mobile number."}, status=400)

        # 1. Verify OTP (allows already verified active OTP)
        is_valid, msg = _verify_otp_code(mobile, otp, purpose='signup', allow_already_verified=True)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        # 2. Check if mobile already registered
        existing_user = _resolve_user_identifier(mobile)
        if existing_user:
            return JsonResponse({
                'status': 'error',
                'message': f"Mobile number '{mobile}' is already registered with an existing account. Please log in."
            }, status=400)

        # 3. Check / generate email
        if email:
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already registered."}, status=400)
        else:
            email = f"vendor_{norm_phone}@infinityventures.local"

        # 4. Generate unique username
        username = (data.get('username') or '').strip()
        if not username:
            base_username = f"ven_{norm_phone}"
            username = base_username
            counter = 1
            while User.objects.filter(username__iexact=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
        elif User.objects.filter(username__iexact=username).exists():
            return JsonResponse({'status': 'error', 'message': f"Username '{username}' is already taken."}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            first_name=name,
            role='VENDOR'
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        vendor_profile = VendorProfile.objects.create(
            user=user,
            company_name=company_name,
            category=category,
            location=location,
            address=address,
            vendor_type=vendor_type,
            experience=experience
        )

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        user_profile.phone_number = mobile
        user_profile.save()

        # Invalidate / consume the used OTP so it cannot be reused
        OTPVerification.objects.filter(
            Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
            otp=otp
        ).update(is_verified=True, expires_at=timezone.now())

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        code = f"VEN{vendor_profile.id:03d}"
        display_name = company_name or name
        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"Vendor '{display_name}' registered and logged in successfully via OTP",
            'token': token_key,
            'token_type': 'Bearer',
            'vendor': {
                'id': code,
                'vendor_id': vendor_profile.id,
                'vendor_code': code,
                'user_id': user.id,
                'name': name,
                'company_name': company_name,
                'contact': mobile,
                'mobile': mobile,
                'email': user.email,
                'category': category,
                'location': location,
                'address': address or '—',
                'vendor_type': vendor_type,
                'experience': experience,
                'role': 'VENDOR'
            }
        }
        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def vendor_otp_login_api(request):
    """
    API for Vendor Login with OTP
    URL: /api/vendor/otp-login/
    Method: POST
    Params: mobile (required), otp (required)
    """
    try:
        data = _parse_api_request(request)
        mobile = (data.get('mobile') or data.get('contact') or data.get('phone') or data.get('phone_number') or '').strip()
        otp = (data.get('otp') or data.get('otp_code') or data.get('code') or '').strip()

        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)
        if not otp:
            return JsonResponse({'status': 'error', 'message': "Field 'otp' is required."}, status=400)

        # 1. Verify OTP (allows already verified active OTP)
        is_valid, msg = _verify_otp_code(mobile, otp, purpose='login', allow_already_verified=True)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        # 2. Find user by mobile
        user = _resolve_user_identifier(mobile)
        if not user:
            return JsonResponse({
                'status': 'error',
                'message': f"No vendor account found with mobile number '{mobile}'. Please sign up first."
            }, status=404)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "Vendor account is suspended or inactive."}, status=403)

        if user.role != 'VENDOR' and not user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': f"Access denied. Account is registered as {user.role}, not a vendor."
            }, status=403)

        # Invalidate the OTP so it cannot be reused
        norm_phone = _normalize_phone(mobile)
        OTPVerification.objects.filter(
            Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
            otp=otp
        ).update(is_verified=True, expires_at=timezone.now())

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        profile = getattr(user, 'vendor_profile', None)
        v_id = profile.id if profile else user.id
        code = f"VEN{v_id:03d}"
        company_name = (profile.company_name if profile and profile.company_name else user.get_full_name()) or user.username
        category = profile.category if profile else 'General'
        location = profile.location if profile else 'Unknown'
        address = profile.address if profile and profile.address else '—'
        vendor_type = profile.vendor_type if profile else 'vendor'
        experience = profile.experience if profile else 0
        token_key = _get_or_create_auth_token(user)

        response_data = {
            'status': 'success',
            'message': f"Vendor '{company_name}' logged in successfully via OTP",
            'token': token_key,
            'token_type': 'Bearer',
            'vendor': {
                'id': code,
                'vendor_id': v_id,
                'vendor_code': code,
                'user_id': user.id,
                'name': user.get_full_name() or user.username,
                'company_name': company_name,
                'contact': mobile,
                'mobile': mobile,
                'email': user.email or '—',
                'category': category,
                'location': location,
                'address': address,
                'vendor_type': vendor_type,
                'experience': experience,
                'role': 'VENDOR'
            }
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# =====================================================================
# 7. MARKETPLACE POSTING APIS (Jobs & Quick Services for Users)
# =====================================================================

@csrf_exempt
@require_POST
def user_post_job_api(request):
    """
    API for Posting a Long-Term Job by a User/Customer.
    Requires Bearer Token:
        Header: Authorization: Bearer <token>
    URL: /api/user/post-job/ or /api/user/jobs/create/
    Method: POST
    """
    try:
        # 1. Authenticate via Bearer token
        user, error_msg = _get_user_from_bearer_token(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': error_msg}, status=401)

        # 2. Check role authorization
        if user.role not in ['USER', 'CUSTOMER'] and not user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': f"Access denied. Only registered users/customers can post jobs (current account role: {user.role})."
            }, status=403)

        data = _parse_api_request(request)

        # 3. Extract and validate required fields
        title = (data.get('title') or '').strip()
        if not title:
            return JsonResponse({'status': 'error', 'message': "Field 'title' is required."}, status=400)

        budget_raw = data.get('budget')
        if budget_raw is None or budget_raw == '':
            return JsonResponse({'status': 'error', 'message': "Field 'budget' is required."}, status=400)

        try:
            budget = float(budget_raw)
            if budget < 0:
                return JsonResponse({'status': 'error', 'message': "Field 'budget' must be a positive number."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': "Field 'budget' must be a valid number."}, status=400)

        # 4. Extract other optional fields
        description = (data.get('description') or '').strip()
        scope_of_work = (data.get('scope_of_work') or '').strip()
        materials_details = (data.get('materials_details') or '').strip()
        additional_requirements = (data.get('additional_requirements') or '').strip()
        budget_type = (data.get('budget_type') or 'Fixed Price').strip()
        required_time = (data.get('required_time') or '').strip()
        shift_availability = (data.get('shift_availability') or 'Full Day (9 AM - 6 PM)').strip()
        working_hours = (data.get('working_hours') or '').strip()
        address = (data.get('address') or '').strip()
        pincode = (data.get('pincode') or '').strip()

        # Required work checklist (handles list or comma-separated string)
        req_work_raw = data.get('required_work') or data.get('required_work[]')
        if isinstance(req_work_raw, list):
            required_work = req_work_raw
        elif isinstance(req_work_raw, str) and req_work_raw.strip():
            try:
                parsed_list = json.loads(req_work_raw)
                required_work = parsed_list if isinstance(parsed_list, list) else [req_work_raw]
            except Exception:
                required_work = [w.strip() for w in req_work_raw.split(',') if w.strip()]
        else:
            required_work = []

        # Category resolution (ID or Name)
        category_obj = None
        category_param = data.get('category_id') or data.get('category')
        if category_param:
            if str(category_param).isdigit():
                category_obj = Category.objects.filter(id=int(category_param)).first()
            if not category_obj:
                category_obj = Category.objects.filter(name__iexact=str(category_param).strip()).first()
        if not category_obj:
            category_obj = Category.objects.filter(status='active').first()

        # Location resolution (ID or City/State)
        location_obj = None
        location_param = data.get('location_id') or data.get('location') or data.get('city')
        if location_param:
            if str(location_param).isdigit():
                location_obj = Location.objects.filter(id=int(location_param)).first()
            if not location_obj:
                location_obj = Location.objects.filter(city__iexact=str(location_param).strip()).first()
            if not location_obj:
                location_obj = Location.objects.filter(Q(city__icontains=str(location_param).strip()) | Q(state__icontains=str(location_param).strip())).first()
        if not location_obj:
            location_obj = Location.objects.filter(status='active').first()

        # Dates
        pref_start_date = data.get('preferred_start_date') or None
        exp_completion = data.get('expected_completion') or data.get('expected_completion_date') or None

        # Contact info
        user_phone = ''
        try:
            if hasattr(user, 'user_profile') and user.user_profile.phone_number:
                user_phone = user.user_profile.phone_number
        except Exception:
            pass

        contact_name = (data.get('contact_name') or user.get_full_name() or user.username).strip()
        contact_mobile = (data.get('contact_mobile') or data.get('contact_phone') or user_phone).strip()

        # 5. Create Job record
        job = Job.objects.create(
            user=user,
            title=title,
            category=category_obj,
            description=description,
            required_work=required_work,
            scope_of_work=scope_of_work,
            materials_details=materials_details,
            additional_requirements=additional_requirements,
            budget=budget,
            budget_type=budget_type,
            preferred_start_date=pref_start_date,
            expected_completion=exp_completion,
            required_time=required_time,
            shift_availability=shift_availability,
            working_hours=working_hours,
            location=location_obj,
            address=address,
            pincode=pincode,
            contact_name=contact_name,
            contact_mobile=contact_mobile,
            status='open',
            bids_count=0
        )

        job_code = f"JOB-{job.id:04d}"
        response_data = {
            'status': 'success',
            'message': "Job posted successfully",
            'job': {
                'id': job.id,
                'job_code': job_code,
                'title': job.title,
                'category': job.category.name if job.category else "General",
                'category_id': job.category.id if job.category else None,
                'description': job.description or "",
                'required_work': job.required_work or [],
                'scope_of_work': job.scope_of_work or "",
                'materials_details': job.materials_details or "",
                'additional_requirements': job.additional_requirements or "",
                'budget': float(job.budget),
                'budget_type': job.budget_type or "Fixed Price",
                'preferred_start_date': str(job.preferred_start_date) if job.preferred_start_date else None,
                'expected_completion': str(job.expected_completion) if job.expected_completion else None,
                'required_time': job.required_time or "",
                'shift_availability': job.shift_availability or "",
                'working_hours': job.working_hours or "",
                'location': f"{job.location.city}, {job.location.state}" if job.location else "",
                'location_id': job.location.id if job.location else None,
                'address': job.address or "",
                'pincode': job.pincode or "",
                'contact_name': job.contact_name or "",
                'contact_mobile': job.contact_mobile or "",
                'status': job.status,
                'bids_count': job.bids_count,
                'created_at': job.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def user_post_quick_service_api(request):
    """
    API for Posting a Quick Service by a User/Customer.
    Requires Bearer Token:
        Header: Authorization: Bearer <token>
    URL: /api/user/post-quick-service/ or /api/user/quick-services/create/
    Method: POST
    """
    try:
        user, error_msg = _get_user_from_bearer_token(request)
        if not user:
            return JsonResponse({'status': 'error', 'message': error_msg}, status=401)

        if user.role not in ['USER', 'CUSTOMER'] and not user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': f"Access denied. Only registered users/customers can post quick services (current role: {user.role})."
            }, status=403)

        data = _parse_api_request(request)

        title = (data.get('title') or '').strip()
        if not title:
            return JsonResponse({'status': 'error', 'message': "Field 'title' is required."}, status=400)

        budget_raw = data.get('budget')
        if budget_raw is None or budget_raw == '':
            return JsonResponse({'status': 'error', 'message': "Field 'budget' is required."}, status=400)

        try:
            budget = float(budget_raw)
            if budget < 0:
                return JsonResponse({'status': 'error', 'message': "Field 'budget' must be a positive number."}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': "Field 'budget' must be a valid number."}, status=400)

        description = (data.get('description') or '').strip()
        shift_availability = (data.get('shift_availability') or 'Flexible').strip()
        address = (data.get('address') or '').strip()
        additional_requirements = (data.get('additional_requirements') or '').strip()

        req_work_raw = data.get('required_work') or data.get('required_work[]')
        if isinstance(req_work_raw, list):
            required_work = req_work_raw
        elif isinstance(req_work_raw, str) and req_work_raw.strip():
            try:
                parsed_list = json.loads(req_work_raw)
                required_work = parsed_list if isinstance(parsed_list, list) else [req_work_raw]
            except Exception:
                required_work = [w.strip() for w in req_work_raw.split(',') if w.strip()]
        else:
            required_work = []

        category_obj = None
        category_param = data.get('category_id') or data.get('category')
        if category_param:
            if str(category_param).isdigit():
                category_obj = Category.objects.filter(id=int(category_param)).first()
            if not category_obj:
                category_obj = Category.objects.filter(name__iexact=str(category_param).strip()).first()
        if not category_obj:
            category_obj = Category.objects.filter(status='active').first()

        location_obj = None
        location_param = data.get('location_id') or data.get('location') or data.get('city')
        if location_param:
            if str(location_param).isdigit():
                location_obj = Location.objects.filter(id=int(location_param)).first()
            if not location_obj:
                location_obj = Location.objects.filter(city__iexact=str(location_param).strip()).first()
            if not location_obj:
                location_obj = Location.objects.filter(Q(city__icontains=str(location_param).strip()) | Q(state__icontains=str(location_param).strip())).first()
        if not location_obj:
            location_obj = Location.objects.filter(status='active').first()

        pref_date = data.get('preferred_date') or None
        pref_time = data.get('preferred_time') or None

        user_phone = ''
        try:
            if hasattr(user, 'user_profile') and user.user_profile.phone_number:
                user_phone = user.user_profile.phone_number
        except Exception:
            pass

        contact_name = (data.get('contact_name') or user.get_full_name() or user.username).strip()
        contact_mobile = (data.get('contact_mobile') or data.get('contact_phone') or user_phone).strip()

        qs = QuickService.objects.create(
            user=user,
            title=title,
            category=category_obj,
            description=description,
            required_work=required_work,
            budget=budget,
            shift_availability=shift_availability,
            preferred_date=pref_date,
            preferred_time=pref_time,
            location=location_obj,
            address=address,
            additional_requirements=additional_requirements,
            contact_name=contact_name,
            contact_mobile=contact_mobile,
            status='open',
            bids_count=0
        )

        qs_code = f"QS-{qs.id:04d}"
        response_data = {
            'status': 'success',
            'message': "Quick service posted successfully",
            'quick_service': {
                'id': qs.id,
                'qs_code': qs_code,
                'title': qs.title,
                'category': qs.category.name if qs.category else "General",
                'category_id': qs.category.id if qs.category else None,
                'description': qs.description or "",
                'required_work': qs.required_work or [],
                'budget': float(qs.budget),
                'shift_availability': qs.shift_availability or "",
                'preferred_date': str(qs.preferred_date) if qs.preferred_date else None,
                'preferred_time': str(qs.preferred_time) if qs.preferred_time else None,
                'location': f"{qs.location.city}, {qs.location.state}" if qs.location else "",
                'location_id': qs.location.id if qs.location else None,
                'address': qs.address or "",
                'contact_name': qs.contact_name or "",
                'contact_mobile': qs.contact_mobile or "",
                'status': qs.status,
                'bids_count': qs.bids_count,
                'created_at': qs.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        return JsonResponse(response_data, status=201)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

