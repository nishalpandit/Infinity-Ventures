# COMPLETE API DOCUMENTATION

## USER APIs

API for Check Phone Number (User)
url : (http://192.168.1.54:8000/api/auth/check-phone/)
method : POST
params :-
mobile:9876543210
role:USER
response :-
{
"status": "success",
"is_registered": true,
"mobile": "9876543210",
"message": "Phone number '9876543210' is already registered.",
"user": {
"user_id": 18,
"user_code": "USR018",
"name": "Ananya Sharma",
"role": "USER",
"email": "ananya@example.com"
}
}


API for Send OTP (User)
url : (http://192.168.1.54:8000/api/auth/send-otp/)
method : POST
params :-
mobile:9876543210
purpose:login
role:USER
response :-
{
"status": "success",
"message": "OTP sent successfully to 9876543210",
"mobile": "9876543210",
"otp": "570474",
"purpose": "login",
"expires_in_minutes": 10
}


API for Verify OTP (User)
url : (http://192.168.1.54:8000/api/auth/verify-otp/)
method : POST
params :-
mobile:9876543210
otp:570474
purpose:login
response :-
{
"status": "success",
"message": "OTP verified successfully.",
"mobile": "9876543210",
"is_verified": true
}


API for User Signup with OTP
url : (http://192.168.1.54:8000/api/user/otp-signup/)
method : POST
params :-
name:Ananya Sharma
mobile:9876543210
otp:570474
email:ananya@example.com
password:Pass@123
response :-
{
"status": "success",
"message": "User 'Ananya Sharma' registered and logged in successfully via OTP",
"token": "e5b50ecb06f723b72b389f417f4b889eb25139cfa6b0a6da",
"token_type": "Bearer",
"user": {
"id": "USR018",
"user_id": 18,
"user_code": "USR018",
"name": "Ananya Sharma",
"username": "usr_9876543210",
"email": "ananya@example.com",
"mobile": "9876543210",
"role": "USER"
}
}


API for User Signup with Password
url : (http://192.168.1.54:8000/api/user/signup/)
method : POST
params :-
name:Ananya Sharma
email:ananya@example.com
mobile:9876543210
password:Pass@123
confirm_password:Pass@123
response :-
{
"status": "success",
"message": "User 'Ananya Sharma' registered successfully",
"token": "e5b50ecb06f723b72b389f417f4b889eb25139cfa6b0a6da",
"token_type": "Bearer",
"user": {
"id": "USR018",
"user_id": 18,
"user_code": "USR018",
"name": "Ananya Sharma",
"username": "ananya@example.com",
"email": "ananya@example.com",
"mobile": "9876543210",
"role": "USER"
}
}


API for User Login with OTP
url : (http://192.168.1.54:8000/api/user/otp-login/)
method : POST
params :-
mobile:9876543210
otp:570474
response :-
{
"status": "success",
"message": "User 'Ananya Sharma' logged in successfully via OTP",
"token": "e5b50ecb06f723b72b389f417f4b889eb25139cfa6b0a6da",
"token_type": "Bearer",
"user": {
"id": "USR018",
"user_id": 18,
"user_code": "USR018",
"name": "Ananya Sharma",
"username": "ananya",
"email": "ananya@example.com",
"mobile": "9876543210",
"role": "USER"
}
}


API for User Login with Password
url : (http://192.168.1.54:8000/api/user/login/)
method : POST
params :-
username:ananya@example.com
password:Pass@123
response :-
{
"status": "success",
"message": "User 'Ananya Sharma' logged in successfully",
"token": "e5b50ecb06f723b72b389f417f4b889eb25139cfa6b0a6da",
"token_type": "Bearer",
"user": {
"id": "USR018",
"user_id": 18,
"user_code": "USR018",
"name": "Ananya Sharma",
"username": "ananya",
"email": "ananya@example.com",
"mobile": "9876543210",
"role": "USER"
}
}


API for User Post Job
url : (http://192.168.1.54:8000/api/user/post-job/)
method : POST
headers :-
Authorization: Bearer <token>
Content-Type: application/json
params :-
title:Full Commercial Office Interior & AC Setup
budget:150000
category:Interior & Fitout
description:Need full setup for new 2500 sq ft office space with HVAC and partition work
required_work:["HVAC Installation", "Gypsum Partitions", "Electrical Rewiring", "Glass Doors"]
budget_type:Fixed Price
scope_of_work:Complete commercial fit-out including materials and labor
materials_details:Branded materials only (Schneider electricals, Daikin AC units)
preferred_start_date:2026-10-01
expected_completion:2026-11-15
required_time:45 Days
shift_availability:Full Day (9 AM - 6 PM)
working_hours:9 AM - 7 PM
location:Mumbai
address:Plot 42, Bandra Kurla Complex
pincode:400051
contact_name:Ananya Sharma
contact_mobile:9876543210
response :-
{
"status": "success",
"message": "Job posted successfully",
"job": {
"id": 14,
"job_code": "JOB-0014",
"title": "Full Commercial Office Interior & AC Setup",
"category": "Interior & Fitout",
"category_id": 1,
"description": "Need full setup for new 2500 sq ft office space with HVAC and partition work",
"required_work": [
"HVAC Installation",
"Gypsum Partitions",
"Electrical Rewiring",
"Glass Doors"
],
"scope_of_work": "Complete commercial fit-out including materials and labor",
"materials_details": "Branded materials only (Schneider electricals, Daikin AC units)",
"additional_requirements": "",
"budget": 150000.0,
"budget_type": "Fixed Price",
"preferred_start_date": "2026-10-01",
"expected_completion": "2026-11-15",
"required_time": "45 Days",
"shift_availability": "Full Day (9 AM - 6 PM)",
"working_hours": "9 AM - 7 PM",
"location": "Mumbai, Maharashtra",
"location_id": 1,
"address": "Plot 42, Bandra Kurla Complex",
"pincode": "400051",
"contact_name": "Ananya Sharma",
"contact_mobile": "9876543210",
"status": "open",
"bids_count": 0,
"created_at": "2026-09-16 18:04:56"
}
}


API for User Post Quick Service
url : (http://192.168.1.54:8000/api/user/post-quick-service/)
method : POST
headers :-
Authorization: Bearer <token>
Content-Type: application/json
params :-
title:Emergency Server Room AC Repair
budget:3500
category:AC Repair
description:Server room cooling failed, need technician urgently
required_work:["AC Compressor Check", "Gas Refill"]
shift_availability:Immediate / Evening
preferred_date:2026-09-17
preferred_time:18:00
location:Mumbai
address:Plot 42, BKC, Mumbai
contact_name:Ananya Sharma
contact_mobile:9876543210
response :-
{
"status": "success",
"message": "Quick service posted successfully",
"quick_service": {
"id": 12,
"qs_code": "QS-0012",
"title": "Emergency Server Room AC Repair",
"category": "AC Repair",
"category_id": 1,
"description": "Server room cooling failed, need technician urgently",
"required_work": [
"AC Compressor Check",
"Gas Refill"
],
"budget": 3500.0,
"shift_availability": "Immediate / Evening",
"preferred_date": "2026-09-17",
"preferred_time": "18:00",
"location": "Mumbai, Maharashtra",
"location_id": 1,
"address": "Plot 42, BKC, Mumbai",
"contact_name": "Ananya Sharma",
"contact_mobile": "9876543210",
"status": "open",
"bids_count": 0,
"created_at": "2026-09-16 18:04:35"
}
}


## VENDOR APIs

API for Check Phone Number (Vendor)
url : (http://192.168.1.54:8000/api/auth/check-phone/)
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
url : (http://192.168.1.54:8000/api/auth/send-otp/)
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
url : (http://192.168.1.54:8000/api/auth/verify-otp/)
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
url : (http://192.168.1.54:8000/api/vendor/otp-signup/)
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
response :-
{
"status": "success",
"message": "Vendor 'Reliable Power Systems Ltd' registered and logged in successfully via OTP",
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
"role": "VENDOR"
}
}


API for Vendor Signup with Password
url : (http://192.168.1.54:8000/api/vendor/signup/)
method : POST
params :-
name:Rajesh Sharma
company_name:Reliable Power Systems Ltd
contact:9123456780
mobile:9123456780
email:info@reliablepower.com
category:Electrical & Power Systems
city:Ahmedabad
state:Gujarat
address:GIDC Naroda, Ahmedabad
vendor_type:company
experience:8
password:Password@123
confirm_password:Password@123
response :-
{
"status": "success",
"message": "Vendor 'Reliable Power Systems Ltd' registered successfully",
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
"role": "VENDOR"
}
}


API for Vendor Login with OTP
url : (http://192.168.1.54:8000/api/vendor/otp-login/)
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
"role": "VENDOR"
}
}


API for Vendor Login with Password
url : (http://192.168.1.54:8000/api/vendor/login/)
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
"role": "VENDOR"
}
}
