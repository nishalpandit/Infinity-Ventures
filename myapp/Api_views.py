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
<<<<<<< HEAD

from .models import UserProfile, VendorProfile, Category, Location, OTPVerification, AuthToken, Job, QuickService, VendorKYC, CustomerAddress, ServiceBooking, Bid

=======
from .models import UserProfile, VendorProfile, Category, Location, OTPVerification, AuthToken, Job, QuickService, VendorKYC, CustomerAddress, ServiceBooking
>>>>>>> origin/main
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
    2. Email address (if contains @)
    3. Mobile phone number (from UserProfile or VendorProfile, with normalization)
    4. Auto-generated phone-based username
    """
    if not identifier:
        return None
    ident = str(identifier).strip()

    # 1. By username
    user = User.objects.filter(username__iexact=ident).first()
    if user:
        return user

    # 2. By email (only if string contains '@' and is non-empty)
    if '@' in ident:
        user = User.objects.filter(email__iexact=ident).first()
        if user:
            return user

    # 3. By mobile number (from UserProfile or VendorProfile)
    norm_phone = _normalize_phone(ident)

    # 3a. Search UserProfile
    query_u = Q(phone_number__iexact=ident)
    if norm_phone:
        query_u |= Q(phone_number__iexact=norm_phone) | Q(phone_number__endswith=norm_phone)
    u_prof = UserProfile.objects.filter(query_u).select_related('user').first()
    if u_prof and u_prof.user:
        return u_prof.user

    # 3b. Search VendorProfile
    query_v = Q(mobile__iexact=ident)
    if norm_phone:
        query_v |= Q(mobile__iexact=norm_phone) | Q(mobile__endswith=norm_phone)
    v_prof = VendorProfile.objects.filter(query_v).select_related('user').first()
    if v_prof and v_prof.user:
        return v_prof.user

    # 4. Fallback by normalized phone username
    if norm_phone and len(norm_phone) >= 10:
        user = User.objects.filter(
            Q(username__iexact=norm_phone) |
            Q(username__iexact=f"usr_{norm_phone}") |
            Q(username__iexact=f"ven_{norm_phone}") |
            Q(username__endswith=norm_phone)
        ).first()
        if user:
            return user

    return None


def _check_vendor_kyc_status(user):
    """
    Checks if a vendor user has completed KYC and is approved.
    Returns (True, None) if verified or not a vendor.
    Returns (False, message) if pending or rejected.
    """
    if user.role != 'VENDOR':
        return True, None
    try:
        kyc = VendorKYC.objects.get(vendor=user)
        if kyc.status != 'approved':
            return False, f"Your profile is under verification by admins. Current status: {kyc.get_status_display()}. You can login once verified."
        return True, None
    except VendorKYC.DoesNotExist:
        return False, "KYC verification pending. Please complete your registration."

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
        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)

        norm_phone = _normalize_phone(mobile)
        if len(norm_phone) < 10:
            return JsonResponse({'status': 'error', 'message': "Please enter a valid 10-digit mobile number."}, status=400)

        existing_user = _resolve_user_identifier(mobile)
        if existing_user:
            return JsonResponse({
                'status': 'error',
                'message': f"Mobile number '{mobile}' is already registered with an existing account. Please log in."
            }, status=400)

        if not password:
            return JsonResponse({'status': 'error', 'message': "Field 'password' is required."}, status=400)
        if confirm_password and password != confirm_password:
            return JsonResponse({'status': 'error', 'message': "Passwords do not match."}, status=400)

        if email:
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already registered."}, status=400)
        else:
            email = ''

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
        user.set_password(password)
        user.save()

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
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
            return JsonResponse({'status': 'error', 'message': "Email/mobile and password are required."}, status=400)

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
        company_name = (data.get('company_name') or '').strip()
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
        
        gender = (data.get('gender') or '').strip()
        id_proof = (data.get('id_proof') or '').strip()
        about = (data.get('about') or '').strip()
        profile_image = request.FILES.get('profile_image')
        
        dob_raw = (data.get('dob') or '').strip()
        if not dob_raw:
            return JsonResponse({'status': 'error', 'message': "Field 'dob' is required."}, status=400)
            
        try:
            from datetime import datetime
            if '-' in dob_raw and len(dob_raw.split('-')[0]) == 4:
                dob = datetime.strptime(dob_raw, "%Y-%m-%d").date()
            else:
                dob = datetime.strptime(dob_raw, "%d-%m-%Y").date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': "Invalid 'dob' format. Expected YYYY-MM-DD or dd-mm-yyyy."}, status=400)
        
        experience = data.get('experience', 0)
        try:
            experience = int(experience)
        except (ValueError, TypeError):
            experience = 0

        if not name:
            return JsonResponse({'status': 'error', 'message': "Field 'name' is required."}, status=400)
        if not mobile:
            return JsonResponse({'status': 'error', 'message': "Field 'mobile' is required."}, status=400)

        norm_phone = _normalize_phone(mobile)
        if len(norm_phone) < 10:
            return JsonResponse({'status': 'error', 'message': "Please enter a valid 10-digit mobile number."}, status=400)

        existing_user = _resolve_user_identifier(mobile)
        if existing_user:
            return JsonResponse({
                'status': 'error',
                'message': f"Mobile number '{mobile}' is already registered with an existing account. Please log in."
            }, status=400)

        if not password:
            return JsonResponse({'status': 'error', 'message': "Field 'password' is required."}, status=400)
        if confirm_password and password != confirm_password:
            return JsonResponse({'status': 'error', 'message': "Passwords do not match."}, status=400)

        if email:
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already registered."}, status=400)
        else:
            email = ''

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
        user.set_password(password)
        user.save()

        vendor_profile = VendorProfile.objects.create(
            user=user,
            company_name=company_name,
            category=category,
            location=location,
            address=address,
            vendor_type=vendor_type,
            experience=experience,
        mobile=mobile,
        dob=dob,
        gender=gender,
        id_proof=id_proof,
        about=about,
        profile_image=profile_image
        )

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        if mobile:
            user_profile.phone_number = mobile
            user_profile.save()

        # Handle KYC Documents
        id_type = request.POST.get('id_type') or data.get('id_type')
        id_document_front = request.FILES.get('id_document_front')
        id_document_back = request.FILES.get('id_document_back')
        business_license = request.FILES.get('business_license')
        if id_type and id_document_front:
            VendorKYC.objects.create(
                vendor=user,
                id_type=id_type,
                id_number=id_proof or '',
                id_document_front=id_document_front,
                id_document_back=id_document_back,
                business_license=business_license,
                status='pending'
            )

        code = f"VEN{vendor_profile.id:03d}"
        display_name = company_name or name
        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"Vendor '{display_name}' registered successfully. Your profile is under verification by admins.",
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
                'dob': str(vendor_profile.dob) if vendor_profile.dob else '',
                'gender': vendor_profile.gender or '',
                'id_proof': vendor_profile.id_proof or '',
                'about': vendor_profile.about or '',
                'profile_image': vendor_profile.profile_image.url if vendor_profile.profile_image else '',
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
            return JsonResponse({'status': 'error', 'message': "Email/mobile and password are required."}, status=400)

        user = _resolve_user_identifier(identifier)
        if not user or not user.check_password(password):
            return JsonResponse({'status': 'error', 'message': "Invalid credentials."}, status=401)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "Vendor account is suspended or inactive."}, status=403)

        kyc_ok, kyc_msg = _check_vendor_kyc_status(user)
        if not kyc_ok:
            return JsonResponse({'status': 'error', 'message': kyc_msg}, status=403)

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

        mobile = ''
        try:
            if profile and profile.mobile:
                mobile = profile.mobile
            elif hasattr(user, 'user_profile') and user.user_profile.phone_number:
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
                'email': user.email or '',
                'category': category,
                'location': location,
                'address': address,
                'vendor_type': vendor_type,
                'experience': experience,
                'dob': str(profile.dob) if profile and profile.dob else '',
                'gender': profile.gender if profile and profile.gender else '',
                'id_proof': profile.id_proof if profile and profile.id_proof else '',
                'about': profile.about if profile and profile.about else '',
                'profile_image': profile.profile_image.url if profile and profile.profile_image else '',
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
        
        user_city = None
        user_state = None
        u_prof = getattr(u, 'user_profile', None)
        if u_prof and u_prof.city:
            user_city = u_prof.city.strip()
            user_state = u_prof.state.strip() if u_prof.state else None
        if not user_city:
            user_city = request.session.get('user_city') or request.COOKIES.get('sugu_user_city')
            user_state = request.session.get('user_state') or request.COOKIES.get('sugu_user_state')
        if not user_city and getattr(u, 'assigned_city', None):
            user_city = u.assigned_city.strip()
            user_state = u.assigned_state.strip() if u.assigned_state else None
        if not user_city and hasattr(u, 'vendor_profile') and u.vendor_profile and u.vendor_profile.location:
            parts = u.vendor_profile.location.split(',')
            user_city = parts[0].strip()
            if len(parts) > 1:
                user_state = parts[1].strip()

        if not user_city:
            user_city = "Ranchi"
            user_state = "Jharkhand"

        active_cities = {c.lower().strip() for c in Location.objects.filter(status='active').values_list('city', flat=True) if c}
        is_service_available = user_city.lower().strip() in active_cities

        return JsonResponse({
            'name': name,
            'initials': initials,
            'city': user_city,
            'state': user_state,
            'is_service_available': is_service_available,
        })
    return JsonResponse({'name': 'Guest', 'initials': 'GU', 'is_service_available': True})


@csrf_exempt
@require_POST
def add_category_api(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission Denied: Category management is restricted to Super Admin.'}, status=403)
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
    if not (request.user.is_authenticated and request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission Denied: Category management is restricted to Super Admin.'}, status=403)
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
    if not (request.user.is_authenticated and request.user.is_superuser):
        return JsonResponse({'success': False, 'error': 'Permission Denied: Category management is restricted to Super Admin.'}, status=403)
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
    API for Unified Login (Email / Mobile + Password)
    URL: /api/auth/login/
    Method: POST
    Params: username or mobile or email (required), password (required)
    """
    try:
        data = _parse_api_request(request)
        identifier = (data.get('username') or data.get('email') or data.get('mobile') or data.get('contact') or '').strip()
        password = data.get('password', '')

        if not identifier or not password:
            return JsonResponse({'status': 'error', 'message': "Email/mobile and password are required."}, status=400)

        user = _resolve_user_identifier(identifier)
        if not user or not user.check_password(password):
            return JsonResponse({'status': 'error', 'message': "Invalid credentials."}, status=401)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "Account is suspended or inactive."}, status=403)

        kyc_ok, kyc_msg = _check_vendor_kyc_status(user)
        if not kyc_ok:
            return JsonResponse({'status': 'error', 'message': kyc_msg}, status=403)

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

        # 1. Verify OTP (allows active OTP regardless of purpose tag or master demo 123456)
        is_valid, msg = _verify_otp_code(mobile, otp, purpose=None, allow_already_verified=True)
        if not is_valid:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)

        # 2. Find user by mobile or auto-provision if new
        user = _resolve_user_identifier(mobile)
        norm_phone = _normalize_phone(mobile) or str(mobile).strip()
        if not user:
            req_role = (data.get('role') or 'USER').strip().upper()
            if req_role in ['VENDOR', 'SERVICE PROVIDER']:
                base_username = f"ven_{norm_phone}"
                uname = base_username
                c = 1
                while User.objects.filter(username=uname).exists():
                    uname = f"{base_username}_{c}"
                    c += 1
                email = f"{uname}@sugu.local"
                user = User.objects.create_user(
                    username=uname,
                    email=email,
                    first_name=f"Partner {norm_phone[-4:]}",
                    role='VENDOR'
                )
                user.set_unusable_password()
                user.save()
                VendorProfile.objects.create(
                    user=user,
                    company_name=f"Partner {norm_phone[-4:]}",
                    category="General Services",
                    location="Local",
                    vendor_type="vendor"
                )
            else:
                base_username = f"usr_{norm_phone}"
                uname = base_username
                c = 1
                while User.objects.filter(username=uname).exists():
                    uname = f"{base_username}_{c}"
                    c += 1
                email = f"{uname}@sugu.local"
                user = User.objects.create_user(
                    username=uname,
                    email=email,
                    first_name=f"Customer {norm_phone[-4:]}",
                    role='USER'
                )
                user.set_unusable_password()
                user.save()
                UserProfile.objects.create(
                    user=user,
                    phone_number=mobile
                )

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': "Account is suspended or inactive."}, status=403)

        kyc_ok, kyc_msg = _check_vendor_kyc_status(user)
        if not kyc_ok:
            return JsonResponse({'status': 'error', 'message': kyc_msg}, status=403)

        # Invalidate the OTP so it cannot be reused
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
            # Check VendorProfile by mobile
            query_v = Q(mobile__iexact=mobile)
            if norm_phone:
                query_v |= Q(mobile__iexact=norm_phone) | Q(mobile__endswith=norm_phone)
            v_prof = VendorProfile.objects.filter(query_v).select_related('user').first()
            if v_prof and v_prof.user:
                user = v_prof.user

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
                    'email': user.email or ''
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

        user = _resolve_user_identifier(mobile)
        
        response_data = {
            'status': 'success',
            'message': msg,
            'mobile': mobile,
            'is_verified': True
        }
        
        if user:
            token_key = _get_or_create_auth_token(user)
            full_name = user.get_full_name() or user.first_name or user.username
            code = f"USR{user.id:03d}" if user.role in ['USER', 'CUSTOMER'] else f"VND{user.id:03d}"
            
            response_data['token'] = token_key
            response_data['token_type'] = 'Bearer'
            response_data['user'] = {
                'id': code,
                'user_id': user.id,
                'user_code': code,
                'name': full_name,
                'username': user.username,
                'email': user.email or '—',
                'mobile': mobile,
                'role': user.role
            }

        return JsonResponse(response_data, status=200)
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

        # 3. Check / handle optional email
        if email:
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already registered."}, status=400)
        else:
            email = ''

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
        gender = (data.get('gender') or '').strip()
        id_proof = (data.get('id_proof') or '').strip()
        about = (data.get('about') or '').strip()
        profile_image = request.FILES.get('profile_image') or request.FILES.get('image')

        dob_raw = (data.get('dob') or '').strip()
        if not dob_raw:
            return JsonResponse({'status': 'error', 'message': "Field 'dob' is required."}, status=400)
            
        try:
            from datetime import datetime
            dob = datetime.strptime(dob_raw, "%d-%m-%Y").date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': "Invalid 'dob' format. Expected dd-mm-yyyy."}, status=400)

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

        # 3. Check / handle optional email
        if email:
            if User.objects.filter(email__iexact=email).exists():
                return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already registered."}, status=400)
        else:
            email = ''

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
            experience=experience,
        mobile=mobile,
        dob=dob,
        gender=gender,
        id_proof=id_proof,
        about=about,
        profile_image=profile_image
        )

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        user_profile.phone_number = mobile
        user_profile.save()

        # Handle KYC Documents
        id_type = request.POST.get('id_type') or data.get('id_type')
        id_document_front = request.FILES.get('id_document_front')
        id_document_back = request.FILES.get('id_document_back')
        business_license = request.FILES.get('business_license')
        if id_type and id_document_front:
            VendorKYC.objects.create(
                vendor=user,
                id_type=id_type,
                id_number=id_proof or '',
                id_document_front=id_document_front,
                id_document_back=id_document_back,
                business_license=business_license,
                status='pending'
            )

        # Invalidate / consume the used OTP so it cannot be reused
        OTPVerification.objects.filter(
            Q(mobile=norm_phone) | Q(mobile=str(mobile).strip()),
            otp=otp
        ).update(is_verified=True, expires_at=timezone.now())

        code = f"VEN{vendor_profile.id:03d}"
        display_name = company_name or name
        token_key = _get_or_create_auth_token(user)
        response_data = {
            'status': 'success',
            'message': f"Vendor '{display_name}' registered successfully. Your profile is under verification by admins.",
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
                'dob': str(vendor_profile.dob) if vendor_profile.dob else '',
                'gender': vendor_profile.gender or '',
                'id_proof': vendor_profile.id_proof or '',
                'about': vendor_profile.about or '',
                'profile_image': vendor_profile.profile_image.url if vendor_profile.profile_image else '',
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

        kyc_ok, kyc_msg = _check_vendor_kyc_status(user)
        if not kyc_ok:
            return JsonResponse({'status': 'error', 'message': kyc_msg}, status=403)

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

        vendor_data = _serialize_vendor_profile_data(user, request)
        company_name = vendor_data.get('company_name') or vendor_data.get('name') or user.username
        token_key = _get_or_create_auth_token(user)

        response_data = {
            'status': 'success',
            'message': f"Vendor '{company_name}' logged in successfully via OTP",
            'token': token_key,
            'token_type': 'Bearer',
            'vendor': vendor_data
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




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

        latitude = data.get('lat') or data.get('latitude') or None
        longitude = data.get('long') or data.get('longitude') or None
        city = (data.get('city') or '').strip()
        state = (data.get('state') or '').strip()

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
            latitude=latitude,
            longitude=longitude,
            city=city,
            state=state,
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
                'latitude': float(job.latitude) if job.latitude else None,
                'longitude': float(job.longitude) if job.longitude else None,
                'city': job.city or "",
                'state': job.state or "",
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


# =====================================================================
# SERVICE LISTING & IMAGE DATA APIS (for Flutter app)
# =====================================================================

def _build_absolute_image_url(request, image_field=None, image_url_str=None):
    """
    Builds a full absolute URL for an image field or a raw image_url string.
    Returns empty string if no image is available.
    """
    if image_field and hasattr(image_field, 'url') and image_field.name:
        return request.build_absolute_uri(image_field.url)
    if image_url_str:
        if image_url_str.startswith('http'):
            return image_url_str
        return request.build_absolute_uri(image_url_str)
    return ''


def _serialize_quick_service(request, qs, vendor_profile=None, reviews_avg=None, reviews_count=None):
    """
    Serializes a QuickService instance into a dictionary with full image URLs.
    """
    from django.db.models import Avg, Count

    vendor = qs.vendor
    if vendor_profile is None:
        vendor_profile = getattr(vendor, 'vendor_profile', None)

    # Image: prefer uploaded image, then image_url field
    service_image = _build_absolute_image_url(request, qs.image, qs.image_url)

    # Vendor profile image
    vendor_image = ''
    if vendor_profile and vendor_profile.profile_image:
        vendor_image = _build_absolute_image_url(request, vendor_profile.profile_image)

    # Rating from VendorProfile (pre-computed aggregate)
    rating = float(vendor_profile.rating) if vendor_profile and vendor_profile.rating else 0.0

    # Reviews count (lazy fetch if not pre-computed)
    if reviews_count is None:
        from .models import ServiceReview
        reviews_count = ServiceReview.objects.filter(vendor=vendor, status='published').count()

    # Location text
    location_text = ''
    if qs.locality:
        location_text = qs.locality
    elif qs.location:
        location_text = f"{qs.location.city}, {qs.location.state}"
    elif vendor_profile:
        location_text = vendor_profile.location or ''

    # Vendor display name
    vendor_name = (vendor_profile.company_name if vendor_profile and vendor_profile.company_name else None) or vendor.get_full_name() or vendor.username

    return {
        'id': qs.id,
        'title': qs.title,
        'description': qs.description or '',
        'category': qs.category.name if qs.category else 'General',
        'category_id': qs.category.id if qs.category else None,
        'base_price': float(qs.base_price),
        'service_packages': qs.service_packages or [],
        'image': service_image,
        'inclusions': qs.inclusions or [],
        'exclusions': qs.exclusions or [],
        'tags': qs.tags or '',
        'status': qs.status,
        'location': location_text,
        'latitude': float(qs.latitude) if qs.latitude else None,
        'longitude': float(qs.longitude) if qs.longitude else None,
        'locality': qs.locality or '',
        'service_radius_km': qs.service_radius_km,
        'vendor': {
            'id': vendor.id,
            'name': vendor_name,
            'profile_image': vendor_image,
            'rating': rating,
            'reviews_count': reviews_count,
            'experience': vendor_profile.experience if vendor_profile else 0,
            'category': vendor_profile.category if vendor_profile else '',
            'location': vendor_profile.location if vendor_profile else '',
            'vendor_type': vendor_profile.vendor_type if vendor_profile else 'vendor',
            'about': vendor_profile.about if vendor_profile and vendor_profile.about else '',
        },
        'created_at': qs.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


@csrf_exempt
def services_nearby_api(request):
    """
    API to list active QuickServices with full image URLs, vendor info, and ratings.
    Supports optional geo-based filtering, category filtering, search, and pagination.
    URL: /api/services/nearby/
    Method: GET
    Params (all optional):
        lat, lng         - User's coordinates for distance-based sorting
        radius           - Max distance in km (default 50)
        category         - Filter by category name (partial match)
        category_id      - Filter by category ID
        search / q       - Keyword search on title/description/tags
        page             - Page number (default 1)
        page_size        - Results per page (default 20, max 50)
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        from django.db.models import Avg, Count
        from .models import ServiceReview
        import math

        # Query params
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        radius = float(request.GET.get('radius', 50))
        category = request.GET.get('category', '').strip()
        category_id = request.GET.get('category_id')
        search = (request.GET.get('search') or request.GET.get('q') or '').strip()
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 50)

        qs = QuickService.objects.filter(status='active').select_related(
            'vendor', 'vendor__vendor_profile', 'category', 'location'
        )

        # Category filter
        if category_id:
            qs = qs.filter(category_id=category_id)
        elif category:
            qs = qs.filter(category__name__icontains=category)

        # Keyword search
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__icontains=search) |
                Q(category__name__icontains=search)
            )

        # Geo-distance calculation & filtering
        results_with_distance = []
        user_lat = float(lat) if lat else None
        user_lng = float(lng) if lng else None

        all_services = list(qs.order_by('-created_at'))

        for svc in all_services:
            dist = None
            if user_lat is not None and user_lng is not None and svc.latitude and svc.longitude:
                # Haversine formula (approximate)
                R = 6371  # Earth radius in km
                dlat = math.radians(float(svc.latitude) - user_lat)
                dlng = math.radians(float(svc.longitude) - user_lng)
                a = (math.sin(dlat / 2) ** 2 +
                     math.cos(math.radians(user_lat)) *
                     math.cos(math.radians(float(svc.latitude))) *
                     math.sin(dlng / 2) ** 2)
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                dist = R * c

                if dist > radius:
                    continue

            results_with_distance.append((svc, dist))

        # Sort: by distance if available, otherwise by newest
        if user_lat is not None and user_lng is not None:
            results_with_distance.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))
        else:
            results_with_distance.sort(key=lambda x: x[0].created_at, reverse=True)

        total = len(results_with_distance)
        start = (page - 1) * page_size
        end = start + page_size
        page_results = results_with_distance[start:end]

        # Serialize
        services_data = []
        for svc, dist in page_results:
            data = _serialize_quick_service(request, svc)
            if dist is not None:
                data['distance_km'] = round(dist, 1)
            services_data.append(data)

        return JsonResponse({
            'status': 'success',
            'total': total,
            'page': page,
            'page_size': page_size,
            'has_more': end < total,
            'services': services_data,
        }, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def service_detail_api(request, service_id):
    """
    API to get a single QuickService detail with images, vendor info, reviews.
    URL: /api/services/<service_id>/
    Method: GET
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        from .models import ServiceReview

        svc = QuickService.objects.select_related(
            'vendor', 'vendor__vendor_profile', 'category', 'location'
        ).filter(id=service_id).first()

        if not svc:
            return JsonResponse({'status': 'error', 'message': 'Service not found.'}, status=404)

        data = _serialize_quick_service(request, svc)

        # Attach recent reviews with images
        reviews = ServiceReview.objects.filter(
            quick_service=svc, status='published'
        ).select_related('customer').order_by('-created_at')[:10]

        reviews_data = []
        for r in reviews:
            reviews_data.append({
                'id': r.id,
                'customer_name': r.customer.get_full_name() or r.customer.username,
                'rating': r.rating,
                'title': r.review_title or '',
                'comment': r.comment,
                'image': _build_absolute_image_url(request, r.review_image),
                'created_at': r.created_at.strftime("%Y-%m-%d"),
            })

        # Also include reviews for the vendor across all services
        vendor_reviews = ServiceReview.objects.filter(
            vendor=svc.vendor, status='published'
        ).select_related('customer').order_by('-created_at')[:10]

        vendor_reviews_data = []
        for r in vendor_reviews:
            vendor_reviews_data.append({
                'id': r.id,
                'customer_name': r.customer.get_full_name() or r.customer.username,
                'rating': r.rating,
                'title': r.review_title or '',
                'comment': r.comment,
                'image': _build_absolute_image_url(request, r.review_image),
                'created_at': r.created_at.strftime("%Y-%m-%d"),
            })

        data['service_reviews'] = reviews_data
        data['vendor_reviews'] = vendor_reviews_data

        return JsonResponse({'status': 'success', 'service': data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def vendor_public_profile_api(request, vendor_id):
    """
    API to get a vendor's public profile with image, rating, services.
    URL: /api/vendors/<vendor_id>/profile/
    Method: GET
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        from .models import ServiceReview
        from django.db.models import Avg, Count

        vendor = User.objects.filter(id=vendor_id, role='VENDOR').first()
        if not vendor:
            return JsonResponse({'status': 'error', 'message': 'Vendor not found.'}, status=404)

        profile = getattr(vendor, 'vendor_profile', None)
        kyc = getattr(vendor, 'kyc_document', None)

        vendor_image = _build_absolute_image_url(request, profile.profile_image if profile else None)

        review_stats = ServiceReview.objects.filter(
            vendor=vendor, status='published'
        ).aggregate(avg_rating=Avg('rating'), total_reviews=Count('id'))

        # Vendor's active services
        services = QuickService.objects.filter(
            vendor=vendor, status='active'
        ).select_related('category', 'location')

        services_data = [_serialize_quick_service(request, s, vendor_profile=profile) for s in services]

        return JsonResponse({
            'status': 'success',
            'vendor': {
                'id': vendor.id,
                'name': (profile.company_name if profile and profile.company_name else None) or vendor.get_full_name() or vendor.username,
                'profile_image': vendor_image,
                'category': profile.category if profile else '',
                'location': profile.location if profile else '',
                'address': profile.address if profile and profile.address else '',
                'experience': profile.experience if profile else 0,
                'about': profile.about if profile and profile.about else '',
                'vendor_type': profile.vendor_type if profile else 'vendor',
                'rating': float(profile.rating) if profile else 0.0,
                'reviews_count': review_stats['total_reviews'] or 0,
                'avg_rating': round(review_stats['avg_rating'], 1) if review_stats['avg_rating'] else 0.0,
                'is_kyc_verified': kyc.status == 'approved' if kyc else False,
                'registered_date': profile.registered_date.strftime("%Y-%m-%d") if profile else '',
                'services': services_data,
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def categories_with_services_api(request):
    """
    API to fetch active categories along with a count of active services in each.
    URL: /api/categories/with-services/
    Method: GET
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        from django.db.models import Count

        categories = Category.objects.filter(status='active').annotate(
            services_count=Count('quickservice', filter=Q(quickservice__status='active'))
        ).order_by('-services_count')

        cat_data = []
        for cat in categories:
            cat_data.append({
                'id': cat.id,
                'name': cat.name,
                'service_type': cat.service_type,
                'services_count': cat.services_count,
            })

        return JsonResponse({'status': 'success', 'categories': cat_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def get_categories_api(request):
    '''
    API to fetch all active categories.
    URL: /api/categories/
    Method: GET
    '''
    if request.method == 'GET':
        categories = Category.objects.filter(status='active').values('id', 'name', 'service_type')
        return JsonResponse({'status': 'success', 'categories': list(categories)}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def get_locations_api(request):
    '''
    API to fetch all active locations (states and cities).
    URL: /api/locations/
    Method: GET
    '''
    if request.method == 'GET':
        locations = Location.objects.filter(status='active').values('id', 'state', 'city')
        return JsonResponse({'status': 'success', 'locations': list(locations)}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)



@csrf_exempt
def get_states_api(request):
    '''
    API to fetch all distinct active states.
    URL: /api/states/
    Method: GET
    '''
    if request.method == 'GET':
        states = list(Location.objects.filter(status='active').values('state').distinct())
        return JsonResponse({'status': 'success', 'states': list(states)}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def get_cities_api(request):
    '''
    API to fetch cities, optionally filtered by state.
    URL: /api/cities/?state=Gujarat
    Method: GET
    '''
    if request.method == 'GET':
        state = request.GET.get('state')
        qs = Location.objects.filter(status='active')
        if state:
            qs = qs.filter(state__iexact=state)
        cities = list(qs.values('id', 'city', 'state'))
        return JsonResponse({'status': 'success', 'cities': list(cities)}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def get_vendor_types_api(request):
    '''
    API to fetch all vendor types for dropdown.
    URL: /api/vendor-types/
    Method: GET
    '''
    if request.method == 'GET':
        types = [
            {'id': 'vendor', 'name': 'Vendor'},
            {'id': 'company', 'name': 'Company Vendor'}
        ]
        return JsonResponse({'status': 'success', 'vendor_types': types}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


def _authenticate_api_user(request):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token_key = auth_header.split(' ')[1]
        token = AuthToken.objects.filter(key=token_key).first()
        if token:
            return token.user
    return None

@csrf_exempt
def add_customer_address_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    user = _authenticate_api_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    data = _parse_api_request(request)
    
    required = ['title', 'address_line_1', 'city', 'state', 'pincode']
    for req in required:
        if not data.get(req):
            return JsonResponse({'status': 'error', 'message': f'{req} is required'}, status=400)
            
    is_default = str(data.get('is_default', 'false')).lower() == 'true'
    
    if is_default:
        CustomerAddress.objects.filter(user=user).update(is_default=False)
        
    address = CustomerAddress.objects.create(
        user=user,
        title=data['title'],
        address_line_1=data['address_line_1'],
        address_line_2=data.get('address_line_2', ''),
        city=data['city'],
        state=data['state'],
        pincode=data['pincode'],
        latitude=data.get('latitude') if data.get('latitude') else None,
        longitude=data.get('longitude') if data.get('longitude') else None,
        is_default=is_default
    )
    
    return JsonResponse({'status': 'success', 'message': 'Address added', 'address_id': address.id})

@csrf_exempt
def get_customer_addresses_api(request):
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        
    user = _authenticate_api_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    addresses = CustomerAddress.objects.filter(user=user)
    
    addr_list = []
    for a in addresses:
        addr_list.append({
            'id': a.id,
            'title': a.title,
            'address_line_1': a.address_line_1,
            'address_line_2': a.address_line_2,
            'city': a.city,
            'state': a.state,
            'pincode': a.pincode,
            'latitude': float(a.latitude) if a.latitude else None,
            'longitude': float(a.longitude) if a.longitude else None,
            'is_default': a.is_default
        })
        
    return JsonResponse({'status': 'success', 'addresses': addr_list})

@csrf_exempt
def delete_customer_address_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
        
    user = _authenticate_api_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    data = _parse_api_request(request)
    address_id = data.get('address_id')
    
    if not address_id:
        return JsonResponse({'status': 'error', 'message': 'address_id is required'}, status=400)
        
    addr = CustomerAddress.objects.filter(id=address_id, user=user).first()
    if not addr:
        return JsonResponse({'status': 'error', 'message': 'Address not found'}, status=404)
        
    addr.delete()
    return JsonResponse({'status': 'success', 'message': 'Address deleted'})

@csrf_exempt
def top_professionals_api(request):
    """
    API to fetch top-rated professionals (vendors).
    URL: /api/top-professionals/
    Method: GET
    Params:
      - location (optional, string)
      - limit (optional, integer, default: 10)
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    data = _parse_api_request(request)
    location = data.get('location')
    limit = data.get('limit', 10)

    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    queryset = VendorProfile.objects.filter(user__is_active=True).order_by('-rating', '-experience')

    if location:
        queryset = queryset.filter(location__icontains=location)
    
    top_vendors = queryset[:limit]

    vendors_data = []
    for vp in top_vendors:
        profile_img_url = _build_absolute_image_url(request, vp.profile_image) if vp.profile_image else ""
        vendors_data.append({
            'vendor_profile_id': vp.id,
            'user_id': vp.user.id,
            'name': vp.user.get_full_name() or vp.company_name or vp.user.username,
            'company_name': vp.company_name or "",
            'category': vp.category or "",
            'location': vp.location or "",
            'experience_years': vp.experience,
            'rating': float(vp.rating) if vp.rating else 0.0,
            'profile_image': profile_img_url,
            'vendor_type': vp.vendor_type,
            'about': vp.about or ""
        })

    return JsonResponse({
        'status': 'success',
        'professionals': vendors_data
    })

# =====================================================================
# VENDOR PROFILE & EDIT PROFILE APIS (Bearer Token Protected)
# =====================================================================

def _serialize_vendor_profile_data(user, request=None):
    """
    Serializes comprehensive vendor profile data for profile and auth APIs.
    """
    vp = getattr(user, 'vendor_profile', None)
    if not vp:
        vp, _ = VendorProfile.objects.get_or_create(user=user)

    if not vp.vendor_code:
        vp.vendor_code = f"VEN{vp.id:03d}"
        vp.save(update_fields=['vendor_code'])

    code = vp.vendor_code or f"VEN{vp.id:03d}"
    company_name = vp.company_name or user.get_full_name() or user.username
    name = user.get_full_name() or user.first_name or user.username

    mobile = vp.mobile or ''
    if not mobile:
        try:
            if hasattr(user, 'user_profile') and user.user_profile.phone_number:
                mobile = user.user_profile.phone_number
        except Exception:
            pass

    city = ''
    state = ''
    loc = vp.location or ''
    if ',' in loc:
        parts = [p.strip() for p in loc.split(',', 1)]
        city = parts[0]
        state = parts[1]
    elif loc:
        city = loc

    profile_image_url = ''
    if vp.profile_image:
        try:
            profile_image_url = request.build_absolute_uri(vp.profile_image.url) if request else vp.profile_image.url
        except Exception:
            profile_image_url = vp.profile_image.url

    kyc_status = 'not_submitted'
    try:
        if hasattr(user, 'kyc_document'):
            kyc_status = user.kyc_document.status
        else:
            kyc = VendorKYC.objects.filter(vendor=user).first()
            if kyc:
                kyc_status = kyc.status
    except Exception:
        pass

    return {
        'id': code,
        'vendor_id': vp.id,
        'vendor_code': code,
        'user_id': user.id,
        'name': name,
        'company_name': company_name,
        'contact': mobile,
        'mobile': mobile,
        'email': user.email or '',
        'category': vp.category or '',
        'location': vp.location or '',
        'city': city,
        'state': state,
        'address': vp.address or '',
        'vendor_type': vp.vendor_type or 'vendor',
        'experience': vp.experience or 0,
        'dob': str(vp.dob) if vp.dob else '',
        'gender': vp.gender or '',
        'id_proof': vp.id_proof or '',
        'about': vp.about or '',
        'profile_image': profile_image_url,
        'rating': float(vp.rating) if vp.rating else 0.0,
        'available_bids': vp.available_bids if vp.available_bids is not None else 5,
        'kyc_status': kyc_status,
        'registered_date': vp.registered_date.strftime("%Y-%m-%d %H:%M:%S") if vp.registered_date else '',
        'role': 'VENDOR'
    }


def _handle_vendor_profile_update(request, user, vp):
    """
    Internal helper to process profile update data from either JSON or multipart form.
    """
    data = _parse_api_request(request)

    # 1. Update Name (User first_name & last_name / full name)
    name = (data.get('name') or data.get('full_name') or data.get('first_name') or '').strip()
    if name:
        parts = name.split(' ', 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''

    # 2. Update Email
    email = (data.get('email') or '').strip()
    if email:
        if User.objects.filter(email__iexact=email).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': f"Email '{email}' is already in use by another account."}, status=400)
        user.email = email

    # 3. Mobile / Phone number, Category, and Vendor Type cannot be changed by the vendor
    # (Mobile is primary auth identity; category and vendor type are verified via KYC)

    # 4. Update Company Name
    company_name = (data.get('company_name') or '').strip()
    if company_name:
        vp.company_name = company_name

    # 5. Update Location, City & State
    city = (data.get('city') or '').strip()
    state = (data.get('state') or '').strip()
    location = (data.get('location') or '').strip()

    if city and state:
        vp.location = f"{city}, {state}"
    elif location:
        vp.location = location
    elif city:
        vp.location = city
    elif state:
        vp.location = state

    # 6. Update Address
    if 'address' in data:
        vp.address = (data.get('address') or '').strip()

    # 9. Update Experience
    if 'experience' in data:
        try:
            vp.experience = int(data.get('experience') or 0)
        except (ValueError, TypeError):
            pass

    # 10. Update DOB (Date of Birth)
    dob_raw = (data.get('dob') or '').strip()
    if dob_raw:
        from datetime import datetime
        parsed_dob = None
        for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                parsed_dob = datetime.strptime(dob_raw, fmt).date()
                break
            except ValueError:
                pass
        if parsed_dob:
            vp.dob = parsed_dob
        else:
            return JsonResponse({'status': 'error', 'message': "Invalid 'dob' format. Expected dd-mm-yyyy or yyyy-mm-dd."}, status=400)

    # 11. Update Gender
    if 'gender' in data:
        vp.gender = (data.get('gender') or '').strip()

    # 12. Update ID Proof / ID Number
    if 'id_proof' in data:
        vp.id_proof = (data.get('id_proof') or '').strip()

    # 13. Update About / Bio
    if 'about' in data:
        vp.about = (data.get('about') or '').strip()

    # 14. Update Profile Image
    profile_image = request.FILES.get('profile_image') or request.FILES.get('image')
    if profile_image:
        vp.profile_image = profile_image

    # Save changes
    user.save()
    vp.save()

    return JsonResponse({
        'status': 'success',
        'message': 'Vendor profile updated successfully',
        'vendor': _serialize_vendor_profile_data(user, request)
    }, status=200)


@csrf_exempt
def vendor_profile_api(request):
    """
    API for Vendor Profile Details (GET) and Update (POST/PUT/PATCH)
    URL: /api/vendor/profile/
    Method: GET, POST, PUT, PATCH
    Header: Authorization: Bearer <token>
    """
    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)

    if user.role != 'VENDOR' and not user.is_superuser:
        return JsonResponse({'status': 'error', 'message': "Access denied. Only vendors can access this profile."}, status=403)

    vp, _ = VendorProfile.objects.get_or_create(user=user)

    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'message': 'Vendor profile fetched successfully',
            'vendor': _serialize_vendor_profile_data(user, request)
        }, status=200)

    elif request.method in ['POST', 'PUT', 'PATCH']:
        return _handle_vendor_profile_update(request, user, vp)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use GET to view or POST/PUT to edit.'}, status=405)


@csrf_exempt
def vendor_edit_profile_api(request):
    """
    Dedicated API for Vendor Edit Profile
    URL: /api/vendor/profile/edit/ or /api/vendor/profile/update/
    Method: POST, PUT, PATCH
    Header: Authorization: Bearer <token>
    """
    if request.method not in ['POST', 'PUT', 'PATCH']:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use POST or PUT to edit profile.'}, status=405)

    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)

    if user.role != 'VENDOR' and not user.is_superuser:
        return JsonResponse({'status': 'error', 'message': "Access denied. Only vendors can edit vendor profile."}, status=403)

    vp, _ = VendorProfile.objects.get_or_create(user=user)
    return _handle_vendor_profile_update(request, user, vp)


# =====================================================================
# 10. VENDOR DASHBOARD & JOBS APIS (Dynamic Mobile App Integration)
# =====================================================================

from .models import Job, QuickService, Bid, PayoutRequest, VendorKYC, VendorProfile


def _format_time_ago(dt):
    if not dt:
        return ""
    try:
        from django.utils.timesince import timesince
        ts = timesince(dt).split(',')[0].strip()
        return f"{ts} ago"
    except Exception:
        return ""


CATEGORY_IMAGE_MAP = {
    'Electrical': 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?w=600&auto=format&fit=crop&q=80',
    'Plumbing': 'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?w=600&auto=format&fit=crop&q=80',
    'AC & Appliance': 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&auto=format&fit=crop&q=80',
    'Cleaning': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=600&auto=format&fit=crop&q=80',
    'Painting': 'https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=600&auto=format&fit=crop&q=80',
    'Carpentry': 'https://images.unsplash.com/photo-1504148455328-c376907d081c?w=600&auto=format&fit=crop&q=80',
    'Pest Control': 'https://images.unsplash.com/photo-1632788320490-67d739818828?w=600&auto=format&fit=crop&q=80',
    'Home Renovation': 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=600&auto=format&fit=crop&q=80',
    'Default': 'https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=600&auto=format&fit=crop&q=80',
}

def _resolve_category_name(category=None, title=''):
    if category and hasattr(category, 'name') and category.name:
        return category.name
    t = (title or '').lower()
    if any(k in t for k in ['electr', 'wire', 'switch', 'light', 'fan', 'mcb', 'fuse', 'inverter']):
        return 'Electrical'
    if any(k in t for k in ['plumb', 'pipe', 'tap', 'leak', 'drain', 'flush', 'water tank', 'geyser', 'sink']):
        return 'Plumbing'
    if any(k in t for k in ['ac', 'air condition', 'refrigerator', 'washing machine', 'appliance', 'cooling']):
        return 'AC & Appliance'
    if any(k in t for k in ['clean', 'sofa', 'carpet', 'deep clean', 'disinfect', 'scrub']):
        return 'Cleaning'
    if any(k in t for k in ['paint', 'waterproof', 'coating', 'putty', 'sealing', 'texture']):
        return 'Painting'
    if any(k in t for k in ['carpent', 'wood', 'furniture', 'wardrobe', 'door', 'lock', 'cabinet']):
        return 'Carpentry'
    if any(k in t for k in ['pest', 'termite', 'cockroach', 'bug']):
        return 'Pest Control'
    if any(k in t for k in ['renovat', 'construct', 'tile', 'masonry', 'civil', 'interior']):
        return 'Home Renovation'
    return 'General Service'

def _get_category_or_service_image(category_name='', title='', image_field=None, image_url_str='', request=None):
    if image_field and hasattr(image_field, 'url') and image_field.name:
        try:
            return request.build_absolute_uri(image_field.url) if request else image_field.url
        except Exception:
            return image_field.url
    if image_url_str and image_url_str.strip():
        url = image_url_str.strip()
        if url.startswith('http'):
            return url
        try:
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return url

    cat = category_name or _resolve_category_name(title=title)
    cat_lower = cat.lower()
    for k, v in CATEGORY_IMAGE_MAP.items():
        if k.lower() in cat_lower or cat_lower in k.lower():
            return v
    return CATEGORY_IMAGE_MAP['Default']


def _serialize_job_summary(job, vendor_user=None, request=None):
    category_name = _resolve_category_name(job.category, job.title)
    budget_val = float(job.budget) if job.budget else 0.0
    locality = job.locality or ""
    city = job.location.city if job.location else ""
    loc_display = locality or city or job.address or "Local Area"
    if locality and city and locality.lower() != city.lower():
        loc_display = f"{locality}, {city}"

    has_bid = False
    if vendor_user:
        has_bid = Bid.objects.filter(job=job, vendor=vendor_user).exists()

    image_url = _get_category_or_service_image(category_name, title=job.title, request=request)

    return {
        'id': job.id,
        'job_code': f"JOB{job.id:04d}",
        'title': job.title,
        'category': category_name,
        'description': job.description or "",
        'budget': budget_val,
        'budget_formatted': f"₹{int(budget_val):,}" if budget_val >= 1000 else f"₹{budget_val:.0f}",
        'budget_type': job.budget_type or "Fixed Budget",
        'location': loc_display,
        'address': job.address or "",
        'pincode': job.pincode or "",
        'distance': "Nearby",
        'time_posted': _format_time_ago(job.created_at),
        'created_at': job.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        'urgent': bool(budget_val >= 10000 or (job.title and 'urgent' in job.title.lower())),
        'bids_count': job.bids_count or job.bids.count(),
        'max_bids': job.max_bids or 10,
        'status': job.status,
        'customer_name': job.contact_name or (job.user.get_full_name() if job.user else "Customer"),
        'has_bid': has_bid,
        'image_url': image_url
    }


def _serialize_quick_service_summary(qs, vendor_user=None, request=None):
    category_name = _resolve_category_name(qs.category, qs.title)
    base_price = float(qs.base_price) if qs.base_price else 0.0
    locality = qs.locality or ""
    city = qs.location.city if qs.location else ""
    loc_display = locality or city or "Nearby"
    if locality and city and locality.lower() != city.lower():
        loc_display = f"{locality}, {city}"

    image_url = _get_category_or_service_image(
        category_name,
        title=qs.title,
        image_field=qs.image,
        image_url_str=qs.image_url,
        request=request
    )

    return {
        'id': qs.id,
        'service_code': f"QS{qs.id:04d}",
        'title': qs.title,
        'category': category_name,
        'description': qs.description or "",
        'budget': base_price,
        'budget_formatted': f"₹{int(base_price):,}" if base_price >= 1000 else f"₹{base_price:.0f}",
        'location': loc_display,
        'distance': f"{qs.service_radius_km:.1f} km",
        'time_posted': _format_time_ago(qs.created_at),
        'created_at': qs.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        'urgent': True,
        'image_url': image_url,
        'status': qs.status
    }


@csrf_exempt
def vendor_dashboard_api(request):
    """
    API for Full Vendor Dashboard (Dynamic Data Matching Web Dashboard)
    URL: /api/vendor/dashboard/
    Method: GET
    Header: Authorization: Bearer <token>
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use GET.'}, status=405)

    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)

    if user.role != 'VENDOR' and not user.is_superuser:
        return JsonResponse({'status': 'error', 'message': "Access denied. Only vendors can access vendor dashboard."}, status=403)

    try:
        from .wallet_services import get_or_create_wallet
        from .models import PayoutRequest, Job, QuickService, Bid, VendorKYC, VendorProfile
        from django.db.models import Sum

        vp = getattr(user, 'vendor_profile', None)
        if not vp:
            vp, _ = VendorProfile.objects.get_or_create(user=user)

        wallet = get_or_create_wallet(user)
        kyc = VendorKYC.objects.filter(vendor=user).first()
        pending_payouts_sum = PayoutRequest.objects.filter(vendor=user, status='pending').aggregate(total=Sum('amount'))['total'] or 0

        # Dynamic query for open jobs and quick services
        open_jobs_qs = Job.objects.filter(status='open').select_related('category', 'location', 'user').order_by('-created_at')
        active_qs_qs = QuickService.objects.filter(status__in=['active', 'open']).select_related('category', 'location').order_by('-created_at')

        # Bids counts
        active_bids_count = Bid.objects.filter(vendor=user).exclude(status__in=['rejected', 'completed', 'withdrawn']).count()
        selected_bids_count = Bid.objects.filter(vendor=user, status='selected').count()
        completed_bids_count = Bid.objects.filter(vendor=user, status='completed').count()

        # Serialized lists
        jobs_list = [_serialize_job_summary(j, vendor_user=user, request=request) for j in open_jobs_qs]
        qs_list = [_serialize_quick_service_summary(q, vendor_user=user, request=request) for q in active_qs_qs[:12]]

        # Next Appointment / In-Progress Task
        next_appointment = None
        selected_bid = Bid.objects.filter(vendor=user, status='selected').select_related('job', 'quick_service').first()
        if selected_bid:
            target = selected_bid.job or selected_bid.quick_service
            if target:
                next_appointment = {
                    'bid_id': selected_bid.id,
                    'title': target.title,
                    'amount_formatted': f"₹{int(selected_bid.amount):,}",
                    'client_name': getattr(target, 'contact_name', None) or (target.user.get_full_name() if hasattr(target, 'user') and target.user else "Client"),
                    'location': getattr(target, 'locality', None) or getattr(target, 'address', 'Scheduled Location'),
                    'status': 'Selected / In Progress'
                }

        vendor_data = _serialize_vendor_profile_data(user, request)

        response_data = {
            'status': 'success',
            'vendor': vendor_data,
            'kyc': {
                'status': kyc.status if kyc else 'not_submitted',
                'is_verified': bool(kyc and kyc.status == 'approved'),
                'admin_notes': kyc.admin_notes if (kyc and kyc.admin_notes) else '',
                'id_type': kyc.get_id_type_display() if kyc else '',
                'id_number': kyc.id_number if kyc else ''
            },
            'wallet': {
                'available_balance': float(wallet.available_balance),
                'available_balance_formatted': f"₹{wallet.available_balance:,.2f}",
                'total_earned': float(wallet.total_earned),
                'total_earned_formatted': f"₹{wallet.total_earned:,.2f}",
                'total_withdrawn': float(wallet.total_withdrawn),
                'total_withdrawn_formatted': f"₹{wallet.total_withdrawn:,.2f}",
                'pending_payouts': float(pending_payouts_sum),
                'pending_payouts_formatted': f"₹{pending_payouts_sum:,.2f}"
            },
            'stats': {
                'today_jobs_count': selected_bids_count if selected_bids_count > 0 else (1 if active_bids_count > 0 else 0),
                'available_jobs_count': open_jobs_qs.count(),
                'available_qs_count': active_qs_qs.count(),
                'remaining_credits': vp.available_bids if vp.available_bids is not None else 5,
                'active_bids_count': active_bids_count,
                'selected_jobs_count': selected_bids_count,
                'completed_work_count': completed_bids_count,
                'rating': float(vp.rating) if vp.rating else 4.9
            },
            'next_appointment': next_appointment,
            'jobs': jobs_list,
            'quick_services': qs_list
        }
        return JsonResponse(response_data, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def vendor_jobs_api(request):
    """
    API for Browsing All Available Jobs
    URL: /api/vendor/jobs/
    Method: GET
    Header: Authorization: Bearer <token>
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use GET.'}, status=405)

    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)

    try:
        jobs_qs = Job.objects.filter(status='open').select_related('category', 'location', 'user').order_by('-created_at')

        search_query = request.GET.get('search', '').strip()
        if search_query:
            jobs_qs = jobs_qs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(locality__icontains=search_query) |
                Q(address__icontains=search_query)
            )

        category_filter = request.GET.get('category', '').strip()
        if category_filter:
            jobs_qs = jobs_qs.filter(category__name__iexact=category_filter)

        jobs_list = [_serialize_job_summary(j, vendor_user=user, request=request) for j in jobs_qs]
        return JsonResponse({
            'status': 'success',
            'count': len(jobs_list),
            'jobs': jobs_list
        }, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def vendor_services_api(request):
    """
    API for Vendor Services (Catalog)
    URL: /api/vendor/services/
    Method: GET (list), POST (create)
    Header: Authorization: Bearer <token>
    """
    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)
    
    gs = GlobalSettings.objects.first()
    platform_config = {
        'commission_percent': gs.get_qs_commission_percent() if gs else 10.0,
        'cgst_percent': gs.get_qs_cgst_percent() if gs else 9.0,
        'sgst_percent': gs.get_qs_sgst_percent() if gs else 9.0,
        'flat_fee': gs.get_qs_flat_fee() if gs else 0.0,
        'tax_mode': gs.get_qs_tax_mode() if gs else 'commission_only',
    }

    if request.method == 'GET':
        services = QuickService.objects.filter(vendor=user).select_related('category').order_by('-created_at')
        services_list = []
        for s in services:
            cat_name = _resolve_category_name(s.category, s.title)
            img_url = _get_category_or_service_image(cat_name, title=s.title, image_field=s.image, image_url_str=s.image_url, request=request)
            pkgs = s.service_packages or []
            v_payout = float(s.base_price)
            if pkgs and isinstance(pkgs, list) and len(pkgs) > 0 and isinstance(pkgs[0], dict):
                v_payout = float(pkgs[0].get('vendor_payout', s.base_price))

            services_list.append({
                'id': s.id,
                'title': s.title,
                'description': s.description or '',
                'category': cat_name,
                'category_id': s.category.id if s.category else None,
                'base_price': str(s.base_price),
                'vendor_payout': str(v_payout),
                'service_packages': pkgs,
                'inclusions': s.inclusions or [],
                'exclusions': s.exclusions or [],
                'status': s.status,
                'image_url': img_url,
                'created_at': s.created_at.isoformat()
            })
        return JsonResponse({
            'status': 'success',
            'services': services_list,
            'platform_config': platform_config
        }, status=200)

    elif request.method == 'POST':
        try:
            data = _parse_api_request(request)
            title = data.get('title', '').strip()
            if not title:
                return JsonResponse({'status': 'error', 'message': 'Title is required.'}, status=400)
            
            # Extract price (handling both 'price' and 'base_price')
            price_val = data.get('price') or data.get('base_price', 0.0)
            try:
                base_price = float(price_val)
            except (ValueError, TypeError):
                base_price = 0.0
            
            # Optional category
            category_id = data.get('category_id') or data.get('category')
            category = None
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    try:
                        category = Category.objects.filter(name__iexact=str(category_id).strip()).first()
                    except Exception:
                        pass

            # Packages, Inclusions, Exclusions (parse from JSON strings if present)
            import json
            def parse_json_field(field_name):
                val = data.get(field_name, '')
                if isinstance(val, str) and val.strip():
                    try:
                        return json.loads(val)
                    except json.JSONDecodeError:
                        return []
                elif isinstance(val, list):
                    return val
                return []

            service_packages = parse_json_field('packages')
            inclusions = parse_json_field('inclusions')
            exclusions = parse_json_field('exclusions')

            # Process packages with backend markup (cut % + GST)
            updated_packages = []
            if service_packages and isinstance(service_packages, list):
                for p in service_packages:
                    if isinstance(p, dict) and p.get('name'):
                        try:
                            raw_p = float(p.get('price', base_price))
                        except (ValueError, TypeError):
                            raw_p = base_price
                        calc = gs.calculate_qs_customer_price(raw_p) if gs else {'customer_price': round(raw_p), 'vendor_payout': raw_p, 'commission': 0, 'total_tax': 0}
                        updated_packages.append({
                            'name': str(p.get('name', 'Standard Package')).strip(),
                            'price': calc['customer_price'],        # Customer listed price
                            'vendor_payout': calc['vendor_payout'],  # Vendor net payout
                            'commission': calc.get('commission', 0),
                            'tax': calc.get('total_tax', 0),
                            'desc': str(p.get('desc', '')).strip()
                        })

            if not updated_packages:
                calc = gs.calculate_qs_customer_price(base_price) if gs else {'customer_price': round(base_price), 'vendor_payout': base_price, 'commission': 0, 'total_tax': 0}
                updated_packages = [{
                    'name': 'Standard Service',
                    'price': calc['customer_price'],
                    'vendor_payout': calc['vendor_payout'],
                    'commission': calc.get('commission', 0),
                    'tax': calc.get('total_tax', 0),
                    'desc': data.get('description', '')
                }]

            # Set starting listed base price from lowest customer package price
            final_customer_price = min(p['price'] for p in updated_packages)

            qs = QuickService.objects.create(
                vendor=user,
                title=title,
                category=category,
                base_price=final_customer_price,
                description=data.get('description', ''),
                service_packages=updated_packages,
                inclusions=inclusions,
                exclusions=exclusions,
                status='active'
            )
            
            # Handle Image Upload
            if 'image' in request.FILES:
                qs.image = request.FILES['image']
                qs.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Service published successfully with automatic markup.',
                'service_id': qs.id,
                'customer_price': final_customer_price,
                'vendor_payout': updated_packages[0]['vendor_payout']
            }, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)

@csrf_exempt
def vendor_service_suggestions_api(request):
    """
    API for Service Title/Description Suggestions by Category
    URL: /api/vendor/service-suggestions/
    Method: GET
    Query: ?category=Electrical (or category_id=5)
    Header: Authorization: Bearer <token>
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use GET.'}, status=405)

    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)

    CATEGORY_SUGGESTIONS = {
        'Electrical': [
            {'title': 'Switchboard Repair', 'base_price': 149, 'description': 'Professional switchboard repair and wiring fix by certified electricians.'},
            {'title': 'Ceiling Fan Installation', 'base_price': 199, 'description': 'Complete fan mounting, wiring and speed regulator setup.'},
            {'title': 'LED Light & Tube Fix', 'base_price': 99, 'description': 'LED panel, tube light and CFL replacement with proper wiring.'},
            {'title': 'MCB & Safety Check', 'base_price': 299, 'description': 'Full house MCB trip analysis, earthing test and safety audit.'},
            {'title': 'Inverter & UPS Setup', 'base_price': 399, 'description': 'Inverter installation, battery check and backup wiring setup.'},
        ],
        'Plumbing': [
            {'title': 'Tap & Mixer Repair', 'base_price': 149, 'description': 'Leaking tap fix, mixer cartridge replacement and joint sealing.'},
            {'title': 'Pipe Leakage Repair', 'base_price': 249, 'description': 'Hidden and visible pipe leak detection, cutting and re-joining.'},
            {'title': 'Toilet & Flush Repair', 'base_price': 299, 'description': 'Flush mechanism fix, seat replacement and drain cleaning.'},
            {'title': 'Water Tank Cleaning', 'base_price': 799, 'description': 'Complete tank drain, scrub, disinfection and refill service.'},
            {'title': 'Bathroom Fitting Install', 'base_price': 349, 'description': 'Shower, geyser, basin and accessory installation by experts.'},
        ],
        'Cleaning': [
            {'title': 'Deep Home Cleaning', 'base_price': 1499, 'description': 'Room by room deep clean including kitchen, bathrooms and balconies.'},
            {'title': 'Bathroom & Kitchen Cleaning', 'base_price': 699, 'description': 'Intensive scrub, tile stain removal and sanitization of wet areas.'},
            {'title': 'Sofa & Carpet Shampoo', 'base_price': 599, 'description': 'Professional fabric shampooing, vacuuming and stain treatment.'},
            {'title': 'Water Tank Cleaning', 'base_price': 799, 'description': 'Full drain, scrub, anti-bacterial wash and safe refill.'},
            {'title': 'Office & Commercial Cleaning', 'base_price': 1999, 'description': 'Desk area, floor, glass and washroom deep cleaning for offices.'},
        ],
        'AC': [
            {'title': 'AC Comprehensive Service', 'base_price': 499, 'description': 'Filter wash, gas pressure check and cooling coil cleaning.'},
            {'title': 'AC Gas Refill & Top-Up', 'base_price': 1499, 'description': 'Refrigerant gas leak check, top-up and performance test.'},
            {'title': 'AC Installation & Uninstall', 'base_price': 999, 'description': 'Wall mount, copper piping and drain pipe setup for split AC.'},
            {'title': 'AC PCB & Compressor Repair', 'base_price': 899, 'description': 'Circuit board diagnosis, compressor check and parts replacement.'},
        ],
        'Painting': [
            {'title': 'Room Wall Painting', 'base_price': 1999, 'description': 'Single or multi-room emulsion or distemper painting service.'},
            {'title': 'Exterior Wall Painting', 'base_price': 4999, 'description': 'Weatherproof exterior paint with primer and putty finish.'},
            {'title': 'Waterproofing & Sealing', 'base_price': 2499, 'description': 'Terrace, bathroom and wall waterproof coating application.'},
        ],
        'Carpentry': [
            {'title': 'Furniture Assembly', 'base_price': 399, 'description': 'Bed, wardrobe, table and shelf assembly or disassembly.'},
            {'title': 'Door & Lock Repair', 'base_price': 249, 'description': 'Door hinge fix, lock replacement and alignment adjustment.'},
            {'title': 'Custom Woodwork', 'base_price': 799, 'description': 'Custom shelving, cabinet and wooden partition fabrication.'},
        ],
        '_default': [
            {'title': 'Professional Home Service', 'base_price': 199, 'description': 'Verified and trained professionals for all home needs.'},
            {'title': 'Premium Maintenance Visit', 'base_price': 349, 'description': 'Comprehensive inspection and maintenance by certified experts.'},
            {'title': 'Emergency Repair Service', 'base_price': 299, 'description': 'Quick response repair and fix service at your doorstep.'},
        ],
    }

    CATEGORY_INCLUSIONS = {
        'Electrical': [
            'Complete wiring inspection and safety diagnostic',
            'Certified electrician with verified background',
            'Post-service cleanup and debris removal',
            '30 days Sugu protection warranty on workmanship',
            'All basic components and consumables included',
        ],
        'Plumbing': [
            'Full pipe and joint inspection before work',
            'Licensed plumber with verified credentials',
            'Leak-proof guarantee on all joints and fittings',
            '30 days Sugu protection warranty on workmanship',
            'Basic sealants, tape and washers included',
        ],
        'Cleaning': [
            'Professional grade cleaning chemicals and tools',
            'Trained and background-verified cleaning staff',
            'Post-service sanitization and disinfection',
            'Satisfaction guarantee or free re-clean within 48hrs',
            'Eco-friendly and child-safe products used',
        ],
        'AC': [
            'Complete AC diagnostic and performance check',
            'Certified AC technician with brand training',
            'Gas pressure test and cooling efficiency report',
            '30 days Sugu protection warranty on service',
            'Filter cleaning and drain pipe flush included',
        ],
        'Painting': [
            'Surface preparation, putty and primer included',
            'Trained painters with 3+ years experience',
            'Furniture and floor protection during work',
            '30 days Sugu protection warranty on finish',
            'Final touch-up and cleanup after completion',
        ],
        'Carpentry': [
            'Precision measurement and material assessment',
            'Experienced carpenter with verified portfolio',
            'Hardware, screws and basic fittings included',
            '30 days Sugu protection warranty on work',
            'Post-work cleanup and debris removal',
        ],
        '_default': [
            'Complete diagnostic inspection of existing fittings and components',
            'Execution by certified, background-checked professional',
            'Post-service sanitization and thorough debris cleanup',
            '30 days Sugu protection warranty on all workmanship',
        ],
    }

    CATEGORY_EXCLUSIONS = {
        'Electrical': ['Major civil masonry, pipe embedding or wall tearing included', 'Spare parts / extra hardware to be purchased or charged separately'],
        'Plumbing': ['Major civil masonry or wall breaking', 'Fixtures and fittings cost not included'],
        'Cleaning': ['Pest control treatment', 'Wall painting or polishing'],
        'AC': ['Spare parts / compressor replacement cost', 'Stabilizer or electrical wiring changes'],
        'Painting': ['Furniture shifting or moving', 'Structural repairs or plastering'],
        'Carpentry': ['Raw material / wood cost', 'Glass or mirror installations'],
        '_default': ['Major civil masonry, pipe embedding or wall tearing included', 'Spare parts / extra hardware to be purchased or charged separately'],
    }

    def get_cat_key(cat_name):
        if not cat_name:
            return '_default'
        n = cat_name.lower()
        if 'electr' in n: return 'Electrical'
        if 'plumb' in n: return 'Plumbing'
        if 'clean' in n: return 'Cleaning'
        if 'ac' in n or 'appliance' in n or 'air' in n: return 'AC'
        if 'paint' in n: return 'Painting'
        if 'carpen' in n or 'wood' in n: return 'Carpentry'
        return '_default'

    # Resolve category from request
    cat_name = request.GET.get('category', '').strip()
    cat_id = request.GET.get('category_id', '').strip()

    if cat_id:
        try:
            cat_obj = Category.objects.get(id=cat_id)
            cat_name = cat_obj.name
        except Category.DoesNotExist:
            pass

    key = get_cat_key(cat_name)
    suggestions = CATEGORY_SUGGESTIONS.get(key, CATEGORY_SUGGESTIONS['_default'])
    inclusions = CATEGORY_INCLUSIONS.get(key, CATEGORY_INCLUSIONS['_default'])
    exclusions = CATEGORY_EXCLUSIONS.get(key, CATEGORY_EXCLUSIONS['_default'])

    gs = GlobalSettings.objects.first()
    platform_config = {
        'commission_percent': gs.get_qs_commission_percent() if gs else 10.0,
        'cgst_percent': gs.get_qs_cgst_percent() if gs else 9.0,
        'sgst_percent': gs.get_qs_sgst_percent() if gs else 9.0,
        'flat_fee': gs.get_qs_flat_fee() if gs else 0.0,
        'tax_mode': gs.get_qs_tax_mode() if gs else 'commission_only',
    }

    return JsonResponse({
        'status': 'success',
        'category': cat_name or 'General',
        'suggestions': suggestions,
        'inclusions': inclusions,
        'exclusions': exclusions,
        'platform_config': platform_config
    }, status=200)

@csrf_exempt
def vendor_bookings_api(request):
    """
    API for Vendor Bookings
    URL: /api/vendor/bookings/
    Method: GET
    Header: Authorization: Bearer <token>
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use GET.'}, status=405)

    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)
    
    try:
        bookings = ServiceBooking.objects.filter(vendor=user).select_related('customer', 'quick_service').order_by('-created_at')
        bookings_list = []
        for b in bookings:
            bookings_list.append({
                'id': b.id,
                'service_title': b.quick_service.title if b.quick_service else 'Unknown Service',
                'customer_name': b.customer.get_full_name() or b.customer.username,
                'customer_phone': getattr(b.customer.user_profile, 'phone_number', '') if hasattr(b.customer, 'user_profile') else '',
                'package_name': b.package_name,
                'total_amount': str(b.total_amount),
                'scheduled_date': str(b.scheduled_date),
                'scheduled_time': str(b.scheduled_time) if b.scheduled_time else '',
                'service_address': b.service_address,
                'status': b.status,
                'created_at': b.created_at.isoformat()
            })
        return JsonResponse({'status': 'success', 'bookings': bookings_list}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def vendor_booking_status_api(request, booking_id):
    """
    API for Vendor to Update Booking Status
    URL: /api/vendor/bookings/<id>/status/
    Method: POST
    Header: Authorization: Bearer <token>
    Body: {'status': 'accepted' | 'completed' | 'cancelled'}
    """
    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)
    
    try:
        booking = ServiceBooking.objects.get(id=booking_id, vendor=user)
        data = _parse_api_request(request)
        new_status = data.get('status')
        if new_status in dict(ServiceBooking.STATUS_CHOICES).keys():
            booking.status = new_status
            booking.save()
            return JsonResponse({'status': 'success', 'message': f'Booking status updated to {new_status}.'}, status=200)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid status.'}, status=400)
    except ServiceBooking.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Booking not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def vendor_send_quotation_api(request):
    """
    API for Vendor to Submit a Quotation / Bid on an Opportunity (Job or QuickService).
    URL: /api/vendor/send-quotation/
    Method: POST
    Header: Authorization: Bearer <token>
    Body:
      - job_id (optional, int): target Job ID
      - quick_service_id (optional, int): target QuickService ID
      - amount (required, float): Vendor quotation / proposed base amount
      - estimated_time (optional, str): e.g. "2 hours", "1 day"
      - message / proposal (optional, str): proposal text
      - attachment (optional, file): file attachment
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use POST.'}, status=405)

    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)

    if user.role != 'VENDOR' and not user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Access denied. Only registered vendors can submit quotations.'}, status=403)

    try:
        from decimal import Decimal
        from .models import Job, QuickService, Bid, VendorProfile, GlobalSettings, BidCreditTransaction

        data = _parse_api_request(request)

        # Extract parameters (handling multipart POST and JSON)
        job_id = data.get('job_id') or request.POST.get('job_id')
        quick_service_id = data.get('quick_service_id') or request.POST.get('quick_service_id')

        amount_raw = data.get('amount') or request.POST.get('amount')
        if not amount_raw:
            return JsonResponse({'status': 'error', 'message': 'Quotation amount is required.'}, status=400)

        try:
            amount_float = float(amount_raw)
            if amount_float <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return JsonResponse({'status': 'error', 'message': 'Please provide a valid quotation amount greater than 0.'}, status=400)

        estimated_time = (data.get('estimated_time') or request.POST.get('estimated_time') or 'Standard delivery').strip()
        proposal = (data.get('proposal') or data.get('message') or request.POST.get('proposal') or request.POST.get('message') or '').strip()
        attachment = request.FILES.get('attachment')

        # Check vendor profile & bid credits
        vp = getattr(user, 'vendor_profile', None)
        if not vp:
            vp, _ = VendorProfile.objects.get_or_create(user=user)

        available_credits = vp.available_bids if vp.available_bids is not None else 0
        if available_credits <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Insufficient bid credits! You have 0 credits remaining. Please recharge your bid credits.'
            }, status=400)

        # Commission & Tax calculations from GlobalSettings
        gs = GlobalSettings.objects.first()
        comm_pct = Decimal(str(gs.platform_commission_percent if gs and gs.platform_commission_percent is not None else '10.00'))
        cgst_pct = Decimal(str(gs.cgst_percent if gs and gs.cgst_percent is not None else '9.00'))
        sgst_pct = Decimal(str(gs.sgst_percent if gs and gs.sgst_percent is not None else '9.00'))
        flat_fee = Decimal(str(gs.platform_flat_fee if gs and gs.platform_flat_fee is not None else '0.00'))
        tax_mode = gs.tax_calculation_mode if gs and gs.tax_calculation_mode else 'commission_only'

        vendor_base = Decimal(str(amount_float)).quantize(Decimal('0.01'))
        comm_amount = ((vendor_base * comm_pct) / Decimal('100.00') + flat_fee).quantize(Decimal('0.01'))

        if tax_mode == 'commission_only':
            cgst_amount = ((comm_amount * cgst_pct) / Decimal('100.00')).quantize(Decimal('0.01'))
            sgst_amount = ((comm_amount * sgst_pct) / Decimal('100.00')).quantize(Decimal('0.01'))
        else:
            taxable_base = vendor_base + comm_amount
            cgst_amount = ((taxable_base * cgst_pct) / Decimal('100.00')).quantize(Decimal('0.01'))
            sgst_amount = ((taxable_base * sgst_pct) / Decimal('100.00')).quantize(Decimal('0.01'))

        total_customer = (vendor_base + comm_amount + cgst_amount + sgst_amount).quantize(Decimal('0.01'))

        job = None
        qs = None

        if job_id:
            try:
                job = Job.objects.get(id=int(job_id))
            except (Job.DoesNotExist, ValueError):
                return JsonResponse({'status': 'error', 'message': f'Job #{job_id} not found.'}, status=404)

            # Validations on Job
            if job.status not in ['open', 'Open']:
                return JsonResponse({'status': 'error', 'message': f'This job is currently {job.status} and not accepting new bids.'}, status=400)

            if job.max_bids and job.bids.count() >= job.max_bids:
                return JsonResponse({'status': 'error', 'message': f'This job has reached its maximum limit of {job.max_bids} bids.'}, status=400)

            if job.min_bid_amount and amount_float < float(job.min_bid_amount):
                return JsonResponse({'status': 'error', 'message': f'Minimum quotation amount allowed for this job is ₹{int(job.min_bid_amount):,}.'}, status=400)

            if job.max_bid_amount and amount_float > float(job.max_bid_amount):
                return JsonResponse({'status': 'error', 'message': f'Maximum quotation amount allowed for this job is ₹{int(job.max_bid_amount):,}.'}, status=400)

            if Bid.objects.filter(job=job, vendor=user).exists():
                return JsonResponse({'status': 'error', 'message': 'You have already submitted a quotation for this job.'}, status=400)

        elif quick_service_id:
            try:
                qs = QuickService.objects.get(id=int(quick_service_id))
            except (QuickService.DoesNotExist, ValueError):
                return JsonResponse({'status': 'error', 'message': f'QuickService #{quick_service_id} not found.'}, status=404)

            if Bid.objects.filter(quick_service=qs, vendor=user).exists():
                return JsonResponse({'status': 'error', 'message': 'You have already submitted a quotation for this service request.'}, status=400)

        else:
            return JsonResponse({'status': 'error', 'message': 'Either job_id or quick_service_id must be provided.'}, status=400)

        # Create the Bid / Quotation
        bid = Bid.objects.create(
            vendor=user,
            job=job,
            quick_service=qs,
            amount=total_customer,
            vendor_base_amount=vendor_base,
            commission_percent_applied=comm_pct,
            commission_amount=comm_amount,
            cgst_percent_applied=cgst_pct,
            cgst_amount=cgst_amount,
            sgst_percent_applied=sgst_pct,
            sgst_amount=sgst_amount,
            flat_fee_amount=flat_fee,
            total_customer_amount=total_customer,
            estimated_time=estimated_time,
            proposal=proposal,
            message=proposal,
            attachment=attachment,
            status='submitted'
        )

        # Deduct 1 Bid Credit
        vp.available_bids = max(0, available_credits - 1)
        vp.save(update_fields=['available_bids'])

        # Increment Job bids count if applicable
        if job:
            job.bids_count = job.bids.count()
            job.save(update_fields=['bids_count'])

        # Log Credit Transaction
        target_title = job.title if job else (qs.title if qs else 'Service')
        BidCreditTransaction.objects.create(
            vendor=user,
            transaction_type='used',
            credits=-1,
            description=f"Quotation placed on {target_title}",
            related_job=job
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Quotation of ₹{int(amount_float):,} submitted successfully! 1 credit deducted ({vp.available_bids} remaining).',
            'bid_id': bid.id,
            'remaining_credits': vp.available_bids,
            'vendor_payout': float(vendor_base),
            'customer_total': float(total_customer)
        }, status=201)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def _serialize_bid_detail(bid, request=None):
    """
    Serializes a vendor Bid with all job details, customer contact, mini-map coordinates,
    and submitted quotation breakdown.
    """
    now = timezone.now()
    diff = now - bid.created_at
    if diff.days == 0:
        relative_date = f"Today, {bid.created_at.strftime('%I:%M %p')}"
    elif diff.days == 1:
        relative_date = "Yesterday"
    else:
        relative_date = f"{diff.days} days ago"

    # Status mapping for Flutter tabs: pending, accepted, rejected
    if bid.status == 'selected':
        status_key = 'accepted'
        status_label = 'Accepted'
    elif bid.status == 'submitted':
        status_key = 'pending'
        status_label = 'Pending'
    elif bid.status in ['rejected', 'withdrawn']:
        status_key = 'rejected'
        status_label = 'Rejected'
    else:
        status_key = bid.status
        status_label = bid.status.title()

    job = bid.job
    qs = bid.quick_service

    if job:
        title = job.title
        description = job.description or 'Professional service required. Inspection and execution by verified specialist.'
        cat_name = _resolve_category_name(job.category, job.title)
        image_url = _get_category_or_service_image(cat_name, title=job.title, request=request)
        address = job.address or '56 Elm St, Kondapur'
        locality = job.locality or 'Kondapur, Hyderabad'
        pincode = job.pincode or '500084'
        lat = float(job.latitude) if job.latitude is not None else 17.4699
        lng = float(job.longitude) if job.longitude is not None else 78.3578
        customer_user = job.user
        customer_name = job.contact_name or (customer_user.get_full_name() if customer_user else '') or (customer_user.username if customer_user else 'Priya Sharma')
        customer_phone = job.contact_mobile or (getattr(customer_user.user_profile, 'phone_number', '') if hasattr(customer_user, 'user_profile') else '') or '+91 98765 43210'
        budget_val = float(job.budget) if job.budget else float(bid.amount)
        preferred_start = job.preferred_start_date.strftime('%b %d, %Y') if job.preferred_start_date else 'Flexible / Immediate'
        expected_comp = job.expected_completion.strftime('%b %d, %Y') if job.expected_completion else 'Same day'
        scope_of_work = job.scope_of_work or ''
        required_work = job.required_work or []
        materials_details = job.materials_details or 'Standard materials and tools provided by technician.'
        additional_reqs = job.additional_requirements or 'Customer requested verified professional with safety gear.'
        job_status = job.status
    elif qs:
        title = qs.title
        description = qs.description or 'Fast and reliable on-demand service.'
        cat_name = _resolve_category_name(qs.category, qs.title)
        image_url = _get_category_or_service_image(cat_name, title=qs.title, image_field=qs.image, image_url_str=getattr(qs, 'image_url', None), request=request)
        address = '56 Elm St, Kondapur'
        locality = 'Kondapur, Hyderabad'
        pincode = '500084'
        lat = 17.4699
        lng = 78.3578
        customer_user = None
        customer_name = 'Priya Sharma'
        customer_phone = '+91 98765 43210'
        budget_val = float(qs.base_price) if qs.base_price else float(bid.amount)
        preferred_start = 'Today'
        expected_comp = 'Same day'
        scope_of_work = ''
        required_work = qs.inclusions or []
        materials_details = 'Standard service kit included.'
        additional_reqs = 'Please bring tools.'
        job_status = qs.status
    else:
        title = 'Home Service'
        description = 'Service requested by customer.'
        cat_name = 'General'
        image_url = 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&fit=crop'
        address = '56 Elm St, Kondapur'
        locality = 'Kondapur, Hyderabad'
        pincode = '500084'
        lat = 17.4699
        lng = 78.3578
        customer_name = 'Priya Sharma'
        customer_phone = '+91 98765 43210'
        budget_val = float(bid.amount)
        preferred_start = 'Today'
        expected_comp = 'Within 2 hours'
        scope_of_work = ''
        required_work = []
        materials_details = 'Standard materials.'
        additional_reqs = ''
        job_status = 'open'

    base_payout = float(bid.vendor_base_amount) if bid.vendor_base_amount is not None else float(bid.amount)
    total_cust = float(bid.total_customer_amount) if bid.total_customer_amount is not None else float(bid.amount)

    return {
        'id': bid.id,
        'bid_id': bid.id,
        'job_id': job.id if job else None,
        'quick_service_id': qs.id if qs else None,
        'title': title,
        'category': cat_name,
        'description': description,
        'image_url': image_url,
        'status': status_key,
        'raw_status': bid.status,
        'status_label': status_label,
        'budget': f"₹{int(base_payout):,}",
        'distance': '1.0 km',
        'date': relative_date,
        'created_at': bid.created_at.strftime('%b %d, %Y, %I:%M %p'),
        'location': address,
        # Mini-map and location coordinates
        'map_data': {
            'latitude': lat,
            'longitude': lng,
            'locality': locality,
            'address': address,
            'pincode': pincode,
            'distance': '1.0 km',
            'static_map_url': f"https://staticmap.openstreetmap.de/staticmap.php?center={lat},{lng}&zoom=15&size=600x300&markers={lat},{lng},ol-marker",
            'google_maps_url': f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        },
        # Customer Information & Chat Contact
        'customer': {
            'name': customer_name,
            'phone': customer_phone,
            'avatar': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=120&h=120&fit=crop&crop=face',
            'verified': True,
            'rating': 4.9,
            'total_bookings': 14
        },
        # Submitted Quotation Details
        'submitted_quotation': {
            'vendor_base_amount': base_payout,
            'formatted_vendor_payout': f"₹{int(base_payout):,}",
            'commission_percent': float(bid.commission_percent_applied or 10.0),
            'commission_amount': float(bid.commission_amount or 0.0),
            'cgst_percent': float(bid.cgst_percent_applied or 9.0),
            'cgst_amount': float(bid.cgst_amount or 0.0),
            'sgst_percent': float(bid.sgst_percent_applied or 9.0),
            'sgst_amount': float(bid.sgst_amount or 0.0),
            'flat_fee_amount': float(bid.flat_fee_amount or 0.0),
            'total_customer_amount': total_cust,
            'formatted_customer_total': f"₹{int(total_cust):,}",
            'estimated_time': bid.estimated_time or 'Within 2 hours',
            'proposal': bid.proposal or bid.message or 'I have verified experience and all necessary tools for this job.',
            'message': bid.message or bid.proposal or '',
            'attachment_url': bid.attachment.url if bid.attachment else None,
            'submitted_at': bid.created_at.strftime('%b %d, %Y, %I:%M %p')
        },
        # Additional Job Specifications
        'job_details': {
            'customer_budget': f"₹{int(budget_val):,}",
            'preferred_start_date': preferred_start,
            'expected_completion': expected_comp,
            'scope_of_work': scope_of_work,
            'required_work': required_work,
            'materials_details': materials_details,
            'additional_requirements': additional_reqs,
            'job_status': job_status
        }
    }


@csrf_exempt
def vendor_bids_api(request):
    """
    API for Vendor's Submitted Quotations / Bids
    URL: /api/vendor/bids/
    Method: GET
    Query Params: ?status=pending|accepted|rejected (optional)
    Header: Authorization: Bearer <token>
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use GET.'}, status=405)

    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)

    try:
        from .models import Bid
        bids_qs = Bid.objects.filter(vendor=user).select_related('job', 'job__category', 'job__user', 'quick_service', 'quick_service__category').order_by('-created_at')

        status_filter = request.GET.get('status', '').strip().lower()
        if status_filter:
            if status_filter == 'accepted':
                bids_qs = bids_qs.filter(status='selected')
            elif status_filter == 'pending':
                bids_qs = bids_qs.filter(status='submitted')
            elif status_filter == 'rejected':
                bids_qs = bids_qs.filter(status__in=['rejected', 'withdrawn'])

        serialized_bids = [_serialize_bid_detail(b, request=request) for b in bids_qs]

        return JsonResponse({
            'status': 'success',
            'count': len(serialized_bids),
            'bids': serialized_bids
        }, status=200)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def vendor_bid_detail_api(request, bid_id):
    """
    API for Fetching Single Bid Details
    URL: /api/vendor/bids/<bid_id>/
    Method: GET
    Header: Authorization: Bearer <token>
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed. Use GET.'}, status=405)

    user, err = _get_user_from_bearer_token(request)
    if err:
        return JsonResponse({'status': 'error', 'message': err}, status=401)

    try:
        from .models import Bid
        bid = Bid.objects.select_related('job', 'job__category', 'job__user', 'quick_service', 'quick_service__category').get(id=bid_id, vendor=user)
        return JsonResponse({
            'status': 'success',
            'bid': _serialize_bid_detail(bid, request=request)
        }, status=200)
    except Bid.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Quotation/Bid not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def book_service_api(request):
    """
    API for a user to book a vendor's service (QuickService).
    URL: /api/user/services/book/
    Method: POST
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    user = _authenticate_api_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    data = _parse_api_request(request)
    
    qs_id = data.get('qs_id')
    package_name = data.get('package_name', 'Standard')
    total_amount = data.get('total_amount', 0)
    scheduled_date = data.get('scheduled_date')
    scheduled_time = data.get('scheduled_time', '')
    service_address = data.get('service_address')
    
    if not qs_id or not scheduled_date or not service_address:
        return JsonResponse({
            'status': 'error', 
            'message': 'qs_id, scheduled_date, and service_address are required fields.'
        }, status=400)
        
    try:
        qs = QuickService.objects.get(id=qs_id)
        booking = ServiceBooking.objects.create(
            customer=user,
            vendor=qs.vendor,
            quick_service=qs,
            package_name=package_name,
            total_amount=total_amount,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time if scheduled_time else None,
            service_address=service_address,
            status='pending'
        )
        return JsonResponse({
            'status': 'success', 
            'message': 'Service booked successfully! Awaiting vendor acceptance.',
            'booking_id': booking.id
        })
    except QuickService.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Service not found.'}, status=404)

@csrf_exempt
def get_user_jobs_api(request):
    """
    API for a user to fetch their posted jobs.
    URL: /api/user/jobs/
    Method: GET
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    user = _authenticate_api_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    jobs = Job.objects.filter(user=user).select_related('category', 'location', 'assigned_vendor').order_by('-created_at')
    
    jobs_data = []
    for job in jobs:
        jobs_data.append({
            'id': job.id,
            'title': job.title,
            'category': job.category.name if job.category else None,
            'description': job.description,
            'budget': float(job.budget) if job.budget else 0.0,
            'budget_type': job.budget_type,
            'status': job.status,
            'created_at': job.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'location': job.location.city if job.location else job.address,
            'bids_count': job.bids_count,
            'assigned_vendor': job.assigned_vendor.get_full_name() or job.assigned_vendor.username if job.assigned_vendor else None
        })
        
    return JsonResponse({'status': 'success', 'jobs': jobs_data})

    

@csrf_exempt
def get_job_bids_api(request, job_id):
    """
    API to fetch bids for a specific job posted by the user.
    URL: /api/user/jobs/<job_id>/bids/
    Method: GET
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    user = _authenticate_api_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    try:
        job = Job.objects.get(id=job_id, user=user)
    except Job.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Job not found or unauthorized.'}, status=404)
        
    bids = Bid.objects.filter(job=job).select_related('vendor', 'vendor__vendor_profile').order_by('-created_at')
    
    bids_data = []
    for bid in bids:
        vendor_profile = getattr(bid.vendor, 'vendor_profile', None)
        
        profile_img_url = ""
        if vendor_profile and vendor_profile.profile_image:
            profile_img_url = _build_absolute_image_url(request, vendor_profile.profile_image)
            
        bids_data.append({
            'bid_id': bid.id,
            'vendor_id': bid.vendor.id,
            'vendor_name': bid.vendor.get_full_name() or bid.vendor.username,
            'vendor_company': vendor_profile.company_name if vendor_profile else '',
            'vendor_rating': float(vendor_profile.rating) if vendor_profile and vendor_profile.rating else 0.0,
            'profile_image': profile_img_url,
            'amount': float(bid.amount),
            'estimated_time': bid.estimated_time,
            'message': bid.message,
            'status': bid.status,
            'created_at': bid.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
        
    return JsonResponse({'status': 'success', 'bids': bids_data})

@csrf_exempt
def handle_bid_action_api(request):
    """
    API to accept or reject a bid.
    URL: /api/user/bids/action/
    Method: POST
    Payload: { 'bid_id': int, 'action': 'accept' | 'reject' }
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    user = _authenticate_api_user(request)
    if not user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)
        
    data = _parse_api_request(request)
    bid_id = data.get('bid_id')
    action = data.get('action') # 'accept' or 'reject'
    
    if not bid_id or action not in ['accept', 'reject']:
        return JsonResponse({'status': 'error', 'message': 'Valid bid_id and action (accept/reject) are required.'}, status=400)
        
    try:
        bid = Bid.objects.get(id=bid_id, job__user=user)
    except Bid.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Bid not found or unauthorized.'}, status=404)
        
    job = bid.job
    
    if action == 'accept':
        if job.status == 'selected':
            return JsonResponse({'status': 'error', 'message': 'A vendor has already been selected for this job.'}, status=400)
            
        bid.status = 'selected'
        bid.save()
        
        job.status = 'selected'
        job.assigned_vendor = bid.vendor
        job.save()
        
        # Reject other pending bids
        Bid.objects.filter(job=job).exclude(id=bid.id).update(status='rejected')
        
        return JsonResponse({'status': 'success', 'message': 'Bid accepted successfully. Vendor has been assigned.'})
        
    elif action == 'reject':
        bid.status = 'rejected'
        bid.save()
        return JsonResponse({'status': 'success', 'message': 'Bid rejected successfully.'})
