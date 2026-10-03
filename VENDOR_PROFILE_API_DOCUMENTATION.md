API for Vendor Profile
url : (http://192.168.1.32:8000/api/vendor/profile/)
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
"profile_image": "http://192.168.1.32:8000/media/vendor_profiles/vheadshot_ven_rajesh.jpg",
"rating": 4.9,
"available_bids": 14,
"kyc_status": "approved",
"registered_date": "2026-09-25 12:13:45",
"role": "VENDOR"
}
}


API for Vendor Edit Profile
url : (http://192.168.1.32:8000/api/vendor/profile/edit/)
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
"profile_image": "http://192.168.1.32:8000/media/vendor_profiles/vheadshot_ven_rajesh.jpg",
"rating": 4.9,
"available_bids": 14,
"kyc_status": "approved",
"registered_date": "2026-09-25 12:13:45",
"role": "VENDOR"
}
}


API for Vendor Dashboard Summary & Dynamic Opportunities
url : (http://192.168.1.32:8000/api/vendor/dashboard/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "vendor": {
    "name": "Nishal Pandit",
    "company_name": "Infinity Electric",
    "vendor_code": "VEN109",
    "vendor_type": "Electrician",
    "location": "Banjara Hills, Hyderabad",
    "rating": 4.9,
    "profile_image": "http://192.168.1.32:8000/media/vendor_profiles/profile.jpg"
  },
  "kyc": {
    "status": "approved",
    "is_verified": true,
    "admin_notes": "",
    "id_type": "Aadhaar Card",
    "id_number": "123456789012"
  },
  "wallet": {
    "available_balance": 12500.0,
    "available_balance_formatted": "₹12,500.00",
    "total_earned": 35200.0,
    "total_earned_formatted": "₹35,200.00",
    "total_withdrawn": 22700.0,
    "total_withdrawn_formatted": "₹22,700.00",
    "pending_payouts": 0.0,
    "pending_payouts_formatted": "₹0.00"
  },
  "stats": {
    "today_jobs_count": 2,
    "available_jobs_count": 8,
    "available_qs_count": 12,
    "remaining_credits": 5,
    "active_bids_count": 3,
    "selected_jobs_count": 1,
    "completed_work_count": 14,
    "rating": 4.9
  },
  "next_appointment": {
    "bid_id": 4,
    "title": "Smart Home Wiring",
    "amount_formatted": "₹2,500",
    "client_name": "Priya Sharma",
    "location": "Kondapur, Hyderabad",
    "status": "Selected / In Progress"
  },
  "jobs": [
    {
      "id": 1,
      "job_code": "JOB001",
      "title": "Ceiling Fan Installation & Wiring",
      "category": "Electrical",
      "budget_formatted": "₹450 – ₹600",
      "location": "Banjara Hills, Hyderabad",
      "time_posted": "15 mins ago",
      "urgent": true,
      "bids_count": 2,
      "description": "Wiring and fixture assembly required for high ceiling."
    }
  ],
  "quick_services": [
    {
      "id": 1,
      "service_code": "QS0001",
      "title": "AC Filter Cleaning & Gas Check",
      "category": "AC Repair",
      "budget_formatted": "₹899",
      "location": "Madhapur, Hyderabad",
      "distance": "3.2 km",
      "time_posted": "20 mins ago",
      "urgent": true
    }
  ]
}


API for Browsing All Vendor Jobs
url : (http://192.168.1.32:8000/api/vendor/jobs/)
method : GET
headers :-
Authorization: Bearer <token>
query params (optional) :-
search: electrical
category: Electrical
response :-
{
  "status": "success",
  "count": 8,
  "jobs": [
    {
      "id": 1,
      "job_code": "JOB001",
      "title": "Ceiling Fan Installation & Wiring",
      "category": "Electrical",
      "budget": 500.0,
      "budget_formatted": "₹450 – ₹600",
      "location": "Banjara Hills, Hyderabad",
      "time_posted": "15 mins ago",
      "urgent": true,
      "bids_count": 2
    }
  ]
}

