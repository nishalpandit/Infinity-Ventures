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
