API for Check Phone Number (Vendor)
url : (http://192.168.1.52:8000/api/auth/check-phone/)
method : POST
params :-
mobile:9123456780
role:VENDOR
response :-
{
"status": "success",
"is_registered": true,
"matches_role": true,
"mobile": "9123456780",
"message": "Phone number '9123456780' is already registered.",
"user": {
"user_id": 27,
"user_code": "VEN011",
"name": "Rajesh Sharma",
"role": "VENDOR",
"email": "info@reliablepower.com"
}
}


API for Send OTP (Vendor)
url : (http://192.168.1.52:8000/api/auth/send-otp/)
method : POST
params :-
mobile:9123456780
purpose:login
role:VENDOR
response :-
{
"status": "success",
"message": "OTP sent successfully to 9123456780",
"mobile": "9123456780",
"otp": "570474",
"purpose": "login",
"expires_in_minutes": 10
}


API for Verify OTP (Vendor)
url : (http://192.168.1.52:8000/api/auth/verify-otp/)
method : POST
params :-
mobile:9123456780
otp:570474
purpose:login
response :-
{
"status": "success",
"message": "OTP verified successfully.",
"mobile": "9123456780",
"is_verified": true
}


API for Vendor Signup with OTP
url : (http://192.168.1.52:8000/api/vendor/otp-signup/)
method : POST
params :-
name:Rajesh Sharma
company_name:Reliable Power Systems Ltd
mobile:9123456780
otp:570474
category:Electrical & Power Systems
city:Ahmedabad
state:Gujarat
address:GIDC Naroda, Ahmedabad
vendor_type:company
experience:8
email:info@reliablepower.com
password:Password@123
dob:1990-01-01 (optional)
gender:Male (optional)
id_type:aadhaar (required - aadhaar/pan/voter_id)
id_proof:123456789012 (optional - ID Number)
id_document_front: (File Upload - required)
id_document_back: (File Upload - optional)
business_license: (File Upload - optional)
about:Description (optional)
profile_image: (File Upload - optional)
response :-
{
"status": "success",
"message": "Vendor 'Reliable Power Systems Ltd' registered successfully. Your profile is under verification by admins.",
"token": "add7ab8b0d28746c823055ba2e4d9b231ff61a6b0c201a44",
"token_type": "Bearer",
"vendor": {
"id": "VEN011",
"vendor_id": 11,
"vendor_code": "VEN011",
"user_id": 27,
"name": "Rajesh Sharma",
"company_name": "Reliable Power Systems Ltd",
"contact": "9123456780",
"mobile": "9123456780",
"email": "info@reliablepower.com",
"category": "Electrical & Power Systems",
"location": "Ahmedabad, Gujarat",
"address": "GIDC Naroda, Ahmedabad",
"vendor_type": "company",
"experience": 8,
"dob": "1990-01-01",
"gender": "Male",
"id_proof": "123456789012",
"about": "Description",
"profile_image": "http://192.168.1.52:8000/media/vendor_profiles/image.jpg",

"role": "VENDOR"
}
}


API for Vendor Signup with Password
url : (http://192.168.1.52:8000/api/vendor/signup/)
method : POST
params :-
name:Rajesh Sharma
company_name:Reliable Power Systems Ltd
contact:9123456780
mobile:9123456780
email:info@reliablepower.com
password:securepassword123
confirm_password:securepassword123
category:Electrical & Power Systems
city:Ahmedabad
state:Gujarat
address:GIDC Naroda, Ahmedabad
vendor_type:company
dob:20-09-2012 (Mandatory, format: dd-mm-yyyy)
gender:Male
id_type:pan
id_proof:ygghi2555g
about:good
profile_image:(File)
id_document_front:(File)
id_document_back:(File)
business_license:(File)
address:GIDC Naroda, Ahmedabad
vendor_type:company
experience:8
password:Password@123
confirm_password:Password@123
dob:1990-01-01 (optional)
gender:Male (optional)
id_type:aadhaar (required - aadhaar/pan/voter_id)
id_proof:123456789012 (optional - ID Number)
id_document_front: (File Upload - required)
id_document_back: (File Upload - optional)
business_license: (File Upload - optional)
about:Description (optional)
profile_image: (File Upload - optional)
response :-
{
"status": "success",
"message": "Vendor 'Reliable Power Systems Ltd' registered successfully. Your profile is under verification by admins.",
"token": "add7ab8b0d28746c823055ba2e4d9b231ff61a6b0c201a44",
"token_type": "Bearer",
"vendor": {
"id": "VEN011",
"vendor_id": 11,
"vendor_code": "VEN011",
"user_id": 27,
"name": "Rajesh Sharma",
"company_name": "Reliable Power Systems Ltd",
"contact": "9123456780",
"mobile": "9123456780",
"email": "info@reliablepower.com",
"category": "Electrical & Power Systems",
"location": "Ahmedabad, Gujarat",
"address": "GIDC Naroda, Ahmedabad",
"vendor_type": "company",
"experience": 8,
"dob": "1990-01-01",
"gender": "Male",
"id_proof": "123456789012",
"about": "Description",
"profile_image": "http://192.168.1.52:8000/media/vendor_profiles/image.jpg",

"role": "VENDOR"
}
}


API for Vendor Login with OTP
url : (http://192.168.1.52:8000/api/vendor/otp-login/)
method : POST
params :-
mobile:9123456780
otp:570474
response :-
{
"status": "success",
"message": "Vendor 'Reliable Power Systems Ltd' logged in successfully via OTP",
"token": "add7ab8b0d28746c823055ba2e4d9b231ff61a6b0c201a44",
"token_type": "Bearer",
"vendor": {
"id": "VEN011",
"vendor_id": 11,
"vendor_code": "VEN011",
"user_id": 27,
"name": "Rajesh Sharma",
"company_name": "Reliable Power Systems Ltd",
"contact": "9123456780",
"mobile": "9123456780",
"email": "info@reliablepower.com",
"category": "Electrical & Power Systems",
"location": "Ahmedabad, Gujarat",
"address": "GIDC Naroda, Ahmedabad",
"vendor_type": "company",
"experience": 8,
"dob": "1990-01-01",
"gender": "Male",
"id_proof": "Aadhar/PAN",
"about": "Description",
"profile_image": "http://192.168.1.52:8000/media/vendor_profiles/image.jpg",

"role": "VENDOR"
}
}


API for Vendor Login with Password
url : (http://192.168.1.52:8000/api/vendor/login/)
method : POST
params :-
username:info@reliablepower.com
password:Password@123
response :-
{
"status": "success",
"message": "Vendor 'Reliable Power Systems Ltd' logged in successfully",
"token": "add7ab8b0d28746c823055ba2e4d9b231ff61a6b0c201a44",
"token_type": "Bearer",
"vendor": {
"id": "VEN011",
"vendor_id": 11,
"vendor_code": "VEN011",
"user_id": 27,
"name": "Rajesh Sharma",
"company_name": "Reliable Power Systems Ltd",
"contact": "9123456780",
"mobile": "9123456780",
"email": "info@reliablepower.com",
"category": "Electrical & Power Systems",
"location": "Ahmedabad, Gujarat",
"address": "GIDC Naroda, Ahmedabad",
"vendor_type": "company",
"experience": 8,
"dob": "1990-01-01",
"gender": "Male",
"id_proof": "Aadhar/PAN",
"about": "Description",
"profile_image": "http://192.168.1.52:8000/media/vendor_profiles/image.jpg",

"role": "VENDOR"
}
}


API for Get Categories
url : (http://192.168.1.52:8000/api/categories/)
method : GET
response :-
{
"status": "success",
"categories": [
{
"id": 26,
"name": "Plumbing",
"service_type": "quick_service"
}
]
}


API for Get All Categories with SubCategories
url : (http://192.168.1.52:8000/api/categories/subcategories/)
method : GET
response :-
{
  "status": "success",
  "categories": [
    {
      "id": 26,
      "name": "Plumbing",
      "service_type": "quick_service",
      "subcategories": [
        {"id": 3, "name": "Pipe & Tap Repair", "services_count": 5},
        {"id": 4, "name": "Water Tank & Motor Installation", "services_count": 2},
        {"id": 5, "name": "Toilet & Sanitary Fitting", "services_count": 4}
      ]
    }
  ]
}


API for Get SubCategories for a Specific Category
url : (http://192.168.1.52:8000/api/categories/<category_id>/subcategories/)
example : (http://192.168.1.52:8000/api/categories/26/subcategories/)
method : GET
response :-
{
  "status": "success",
  "category": {
    "id": 26,
    "name": "Plumbing",
    "service_type": "quick_service"
  },
  "subcategories": [
    {"id": 3, "name": "Pipe & Tap Repair", "status": "active", "services_count": 5},
    {"id": 4, "name": "Water Tank & Motor Installation", "status": "active", "services_count": 2},
    {"id": 5, "name": "Toilet & Sanitary Fitting", "status": "active", "services_count": 4}
  ]
}


API for Get Locations (States and Cities)
url : (http://192.168.1.52:8000/api/locations/)
method : GET
response :-
{
"status": "success",
"locations": [
{
"id": 1,
"state": "Gujarat",
"city": "Ahmedabad"
}
]
}



API for Get States
url : (http://192.168.1.52:8000/api/states/)
method : GET
response :-
{
"status": "success",
"states": [
{
"state": "Gujarat"
},
{
"state": "Maharashtra"
}
]
}


API for Get Cities
url : (http://192.168.1.52:8000/api/cities/?state=Gujarat)
method : GET
params :-
state:Gujarat (Optional query parameter)
response :-
{
"status": "success",
"cities": [
{
"id": 1,
"city": "Ahmedabad",
"state": "Gujarat"
},
{
"id": 2,
"city": "Surat",
"state": "Gujarat"
}
]
}


API for Get Vendor Types
url : (http://192.168.1.52:8000/api/vendor-types/)
method : GET
response :-
{
"status": "success",
"vendor_types": [
{
"id": "vendor",
"name": "Vendor"
},
{
"id": "company",
"name": "Company Vendor"
}
]
}


API for Vendor Selected Jobs (Unlocked Customer Details)
url : (http://192.168.1.52:8000/api/vendor/selected-jobs/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "job_id": 14,
      "title": "Kitchen Modular Cabinets Installation",
      "category": "Carpentry",
      "budget": 25000.0,
      "budget_type": "Fixed",
      "status": "selected",
      "bid_amount": 23500.0,
      "customer_name": "Ananya Sharma",
      "customer_phone": "9876543210",
      "site_address": "Flat 402, Green Valley Apartments, Kanke Road",
      "locality": "Kanke Road",
      "city": "Ranchi",
      "state": "Jharkhand",
      "pincode": "834008",
      "image": "http://192.168.1.52:8000/media/jobs/cabinet.jpg",
      "started_at": "2026-10-20",
      "expected_completion": "2026-10-25",
      "created_at": "2026-10-15 14:20:00"
    }
  ]
}


API for Vendor KYC Re-Submit / Update (Post-Signup Resubmission)
Note: During initial registration, KYC documents (id_type, id_document_front, id_document_back, business_license) are already submitted in ONE SHOT directly inside the Signup API (POST /api/vendor/otp-signup/ or POST /api/vendor/signup/). 
You do NOT need to call this endpoint during initial signup.

This dedicated endpoint is used for:
1. Re-submitting KYC if the Admin REJECTED the previous submission (e.g., blurry photo, name mismatch, expired document). Because the vendor's account is already registered, they re-upload their corrected documents here from the vendor dashboard.
2. Uploading additional documents later (e.g. GST Certificate, Business License).
url : (http://192.168.1.52:8000/api/vendor/kyc/submit/)
method : POST (multipart/form-data)
headers :-
Authorization: Bearer <token>
params :-
id_type: aadhaar (aadhaar/pan/voter_id)
id_number: 123456789012
id_document_front: [file] (required)
id_document_back: [file] (optional)
business_license: [file] (optional)
gst_certificate: [file] (optional)
response :-
{
  "status": "success",
  "message": "KYC documents submitted for review successfully",
  "data": {
    "kyc_id": 12,
    "status": "pending"
  }
}


API for Vendor KYC Status
url : (http://192.168.1.52:8000/api/vendor/kyc/status/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "data": {
    "has_kyc": true,
    "kyc_id": 12,
    "kyc_status": "pending",
    "id_type": "aadhaar",
    "id_number": "123456789012",
    "submitted_at": "2026-10-16 09:30:00",
    "reviewed_at": null,
    "admin_notes": "",
    "id_document_front": "http://192.168.1.52:8000/media/kyc/id_docs/front.jpg",
    "id_document_back": "http://192.168.1.52:8000/media/kyc/id_docs/back.jpg",
    "business_license": "",
    "gst_certificate": ""
  }
}


API for Vendor Wallet Payout Request
url : (http://192.168.1.52:8000/api/vendor/wallet/payout/request/)
method : POST
headers :-
Authorization: Bearer <token>
params (UPI):-
amount: 2500.00
payout_method: upi
upi_id: vendor@okaxis
params (Bank):-
amount: 5000.00
payout_method: bank
account_holder_name: Rajesh Sharma
account_number: 123456789012
ifsc_code: SBIN0001234
bank_name: State Bank of India
response :-
{
  "status": "success",
  "message": "Payout request submitted successfully",
  "data": {
    "request_id": 9,
    "amount": 2500.0,
    "payout_method": "upi",
    "status": "pending"
  }
}


API for Vendor Wallet Payout History
url : (http://192.168.1.52:8000/api/vendor/wallet/payout/history/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "id": 9,
      "amount": 2500.0,
      "payout_method": "upi",
      "account_number": "",
      "upi_id": "vendor@okaxis",
      "status": "pending",
      "bank_reference_number": "",
      "admin_remarks": "",
      "requested_at": "2026-10-16 10:45:00",
      "processed_at": null
    }
  ]
}


API for Vendor Job Completion Proof Submit
url : (http://192.168.1.52:8000/api/vendor/jobs/<job_id>/submit-proof/)
method : POST (multipart/form-data)
headers :-
Authorization: Bearer <token>
params :-
photo_1: [file] (required)
photo_2: [file] (optional)
work_summary: Completed full modular kitchen cabinet setup with water-resistant ply.
response :-
{
  "status": "success",
  "message": "Completion proof submitted successfully",
  "data": {
    "proof_id": 4,
    "completed_at": "2026-10-16 11:15:00"
  }
}


API for Vendor Earnings Summary & Breakdown
url : (http://192.168.1.52:8000/api/vendor/earnings/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "data": {
    "available_balance": 14500.0,
    "total_earned": 42000.0,
    "total_withdrawn": 27500.0,
    "total_commission_paid": 4200.0,
    "total_tax_paid": 756.0,
    "completed_jobs_count": 8,
    "completed_services_count": 5,
    "total_completed_orders": 13,
    "average_job_value": 3230.77,
    "monthly_breakdown": [
      {
        "month": "May 2026",
        "year_month": "2026-05",
        "earned": 6500.0,
        "jobs_count": 2,
        "commission": 650.0
      },
      {
        "month": "Jun 2026",
        "year_month": "2026-06",
        "earned": 8200.0,
        "jobs_count": 3,
        "commission": 820.0
      },
      {
        "month": "Jul 2026",
        "year_month": "2026-07",
        "earned": 7100.0,
        "jobs_count": 2,
        "commission": 710.0
      },
      {
        "month": "Aug 2026",
        "year_month": "2026-08",
        "earned": 9400.0,
        "jobs_count": 3,
        "commission": 940.0
      },
      {
        "month": "Sep 2026",
        "year_month": "2026-09",
        "earned": 5800.0,
        "jobs_count": 2,
        "commission": 580.0
      },
      {
        "month": "Oct 2026",
        "year_month": "2026-10",
        "earned": 5000.0,
        "jobs_count": 1,
        "commission": 500.0
      }
    ],
    "recent_transactions": [
      {
        "id": 18,
        "amount": 23500.0,
        "transaction_type": "credit",
        "description": "Net Payout for 'Kitchen Modular Cabinets Installation'",
        "created_at": "2026-10-15 17:00:00"
      }
    ]
  }
}


