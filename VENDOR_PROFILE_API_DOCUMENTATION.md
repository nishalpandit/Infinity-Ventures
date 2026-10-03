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
"id": "VEN026",
"vendor_id": 26,
"vendor_code": "VEN026",
"user_id": 91,
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
"about": "Professional electrical contracting and maintenance services.",
"profile_image": "http://192.168.1.55:8000/media/vendor_profiles/vheadshot_ven_rajesh.jpg",
"rating": 4.9,
"available_bids": 14,
"kyc_status": "approved",
"registered_date": "2026-09-25 12:13:45",
"role": "VENDOR"
}
}


API for Vendor Edit Profile
url : (http://192.168.1.55:8000/api/vendor/profile/edit/)
method : POST
headers :-
Authorization: Bearer <token>
Content-Type: multipart/form-data
params :-
name:Rajesh Sharma
company_name:Reliable Power Systems Ltd
email:info@reliablepower.com
mobile:9123456780
category:Electrical & Power Systems
city:Ahmedabad
state:Gujarat
location:Ahmedabad, Gujarat
address:GIDC Naroda, Ahmedabad
vendor_type:company
experience:8
dob:01-01-1990
gender:Male
id_proof:123456789012
about:Professional electrical contracting and maintenance services.
profile_image:(File)
response :-
{
"status": "success",
"message": "Vendor profile updated successfully",
"vendor": {
"id": "VEN026",
"vendor_id": 26,
"vendor_code": "VEN026",
"user_id": 91,
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
"about": "Professional electrical contracting and maintenance services.",
"profile_image": "http://192.168.1.55:8000/media/vendor_profiles/vheadshot_ven_rajesh.jpg",
"rating": 4.9,
"available_bids": 14,
"kyc_status": "approved",
"registered_date": "2026-09-25 12:13:45",
"role": "VENDOR"
}
}
