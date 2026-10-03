API for Check Phone Number (Vendor)
url : (http://192.168.1.55:800/api/auth/check-phone/)
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
url : (http://192.168.1.55:800/api/auth/send-otp/)
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
url : (http://192.168.1.55:800/api/auth/verify-otp/)
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
url : (http://192.168.1.55:800/api/vendor/otp-signup/)
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
"profile_image": "http://192.168.1.55:800/media/vendor_profiles/image.jpg",

"role": "VENDOR"
}
}


API for Vendor Signup with Password
url : (http://192.168.1.55:8000/api/vendor/signup/)
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
"profile_image": "http://192.168.1.55:800/media/vendor_profiles/image.jpg",

"role": "VENDOR"
}
}


API for Vendor Login with OTP
url : (http://192.168.1.55:800/api/vendor/otp-login/)
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
"profile_image": "http://192.168.1.55:800/media/vendor_profiles/image.jpg",

"role": "VENDOR"
}
}


API for Vendor Login with Password
url : (http://192.168.1.55:800/api/vendor/login/)
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
"profile_image": "http://192.168.1.55:800/media/vendor_profiles/image.jpg",

"role": "VENDOR"
}
}


API for Get Categories
url : (http://192.168.1.55:800/api/categories/)
method : GET
response :-
{
"status": "success",
"categories": [
{
"id": 1,
"name": "Electrical & Power Systems",
"service_type": "both"
}
]
}


API for Get Locations (States and Cities)
url : (http://192.168.1.55:800/api/locations/)
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
url : (http://192.168.1.55:800/api/states/)
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
url : (http://192.168.1.55:800/api/cities/?state=Gujarat)
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
url : (http://192.168.1.55:800/api/vendor-types/)
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


API for Vendor Profile
url : (http://192.168.1.55:8000/api/vendor/profile/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
"status": "success",
"message": "Vendor profile fetched successfully",
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
"city": "Ahmedabad",
"state": "Gujarat",
"address": "GIDC Naroda, Ahmedabad",
"vendor_type": "company",
"experience": 8,
"dob": "1990-01-01",
"gender": "Male",
"id_proof": "123456789012",
"about": "Description",
"profile_image": "http://192.168.1.55:8000/media/vendor_profiles/image.jpg",
"rating": 0.0,
"available_bids": 5,
"kyc_status": "approved",
"registered_date": "2026-09-15 10:30:00",
"role": "VENDOR"
}
}


API for Vendor Edit Profile
url : (http://192.168.1.55:8000/api/vendor/profile/edit/)
method : POST
headers :-
Authorization: Bearer <token>
Content-Type: multipart/form-data (or application/json)
params :-
name:Rajesh Sharma (optional)
company_name:Reliable Power Systems Ltd (optional)
email:info@reliablepower.com (optional)
contact:9123456780 (optional)
mobile:9123456780 (optional)
category:Electrical & Power Systems (optional)
city:Ahmedabad (optional)
state:Gujarat (optional)
location:Ahmedabad, Gujarat (optional)
address:GIDC Naroda, Ahmedabad (optional)
vendor_type:company (optional - vendor/company)
experience:8 (optional)
dob:01-01-1990 (optional - format: dd-mm-yyyy or yyyy-mm-dd)
gender:Male (optional)
id_proof:123456789012 (optional)
about:Description (optional)
profile_image:(File Upload - optional)
response :-
{
"status": "success",
"message": "Vendor profile updated successfully",
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
"city": "Ahmedabad",
"state": "Gujarat",
"address": "GIDC Naroda, Ahmedabad",
"vendor_type": "company",
"experience": 8,
"dob": "1990-01-01",
"gender": "Male",
"id_proof": "123456789012",
"about": "Description",
"profile_image": "http://192.168.1.55:8000/media/vendor_profiles/image.jpg",
"rating": 0.0,
"available_bids": 5,
"kyc_status": "approved",
"registered_date": "2026-09-15 10:30:00",
"role": "VENDOR"
}
}

