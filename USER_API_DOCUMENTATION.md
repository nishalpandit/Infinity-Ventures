API for Check Phone Number (User)
url : (http://192.168.1.52:8000/api/auth/check-phone/)
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
url : (http://192.168.1.52:8000/api/auth/send-otp/)
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
url : (http://192.168.1.52:8000/api/auth/verify-otp/)
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
url : (http://192.168.1.52:8000/api/user/otp-signup/)
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
url : (http://192.168.1.52:8000/api/user/signup/)
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
url : (http://192.168.1.52:8000/api/user/otp-login/)
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
url : (http://192.168.1.52:8000/api/user/login/)
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


API for Get All Categories with SubCategories
url : (http://192.168.1.52:8000/api/categories/subcategories/)
method : GET
headers :-
(None required)
response :-
{
  "status": "success",
  "categories": [
    {
      "id": 26,
      "name": "Plumbing",
      "service_type": "quick_service",
      "status": "active",
      "icon_class": "bi-droplet-fill",
      "icon_color": "#0284c7",
      "image": "http://192.168.1.52:8000/media/categories/plumbing.png",
      "subcategories": [
        {"id": 3, "name": "Pipe & Tap Repair", "services_count": 5},
        {"id": 4, "name": "Water Tank & Motor Installation", "services_count": 2},
        {"id": 5, "name": "Toilet & Sanitary Fitting", "services_count": 4},
        {"id": 6, "name": "Drainage & Blockage Cleaning", "services_count": 3},
        {"id": 7, "name": "Basin & Sink Installation", "services_count": 2}
      ]
    },
    {
      "id": 27,
      "name": "Electrical",
      "service_type": "quick_service",
      "status": "active",
      "icon_class": "bi-lightning-charge-fill",
      "icon_color": "#d97706",
      "image": "http://192.168.1.52:8000/media/categories/electrical.png",
      "subcategories": [
        {"id": 8, "name": "Wiring & Fuse Repair", "services_count": 4},
        {"id": 9, "name": "Switch & Socket Installation", "services_count": 6},
        {"id": 10, "name": "Fan Installation & Repair", "services_count": 3}
      ]
    }
  ]
}


API for User Display Beauty Experience (Cards: Women vs Men)
url : (http://192.168.1.52:8000/api/user/beauty/)
method : GET
response :-
{
  "status": "success",
  "title": "Beauty & Wellness",
  "subtitle": "Select Experience / Category",
  "experiences": [
    {
      "id": "womens_salon_spa",
      "gender": "women",
      "name": "Women's Salon & Spa",
      "tagline": "At-Home Beauty or Book Top Luxury Parlours",
      "rating": 4.91,
      "reviews_count": "4.2M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 349,
      "formatted_price": "₹349",
      "image": "http://192.168.1.52:8000/static/assets/beauty/women_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/womens_salon_spa.png",
      "hero_title": "Women's Salon, Spa & Parlours",
      "hero_desc": "Doorstep certified beauticians or guaranteed VIP slot at Bengaluru's top luxury salons.",
      "modes": [
        {
          "id": "home",
          "name": "1. Salon at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified beautician visits your home • 100% sealed mono-kits",
          "icon": "home",
          "accent_color": "#ec4899"
        },
        {
          "id": "parlour",
          "name": "2. Premium Parlour Services",
          "badge": "LUXURY SALON BRANDS",
          "description": "Book visit at Lakmé Luxe, Enrich, BBlunt, Toni & Guy in your area",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    },
    {
      "id": "mens_salon_massage",
      "gender": "men",
      "name": "Men's Salon & Massage",
      "tagline": "At-Home Grooming or Book Top Luxury Salons",
      "rating": 4.87,
      "reviews_count": "2.9M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 249,
      "formatted_price": "₹249",
      "image": "http://192.168.1.52:8000/static/assets/beauty/men_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/mens_salon_massage.png",
      "hero_title": "Men's Grooming, Massage & Barbershops",
      "hero_desc": "Certified male barbers at home or royal grooming at Truefitt & Hill, Bounce and top lounges.",
      "modes": [
        {
          "id": "home",
          "name": "1. Grooming & Massage at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified male stylist visits your home • Single-use sterilized tools & vacuum",
          "icon": "home",
          "accent_color": "#0284c7"
        },
        {
          "id": "parlour",
          "name": "2. Premium Barbershop & Lounge",
          "badge": "LUXURY BARBERSHOPS",
          "description": "Book visit at Truefitt & Hill, Bounce, Toni & Guy Men, The Man Company",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    }
  ]
}


API for User Display Beauty Services (At-Home Subcategories & Services)
url : (http://192.168.1.52:8000/api/user/beauty/services/)
method : GET
params :-
gender: women (options: women / men)
delivery_mode: home (options: home / parlour)
response :-
{
  "status": "success",
  "category_id": 37,
  "category_name": "Beauty",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "home",
  "mode_name": "Salon at Home",
  "subcategories": [
    {
      "id": "sub_48",
      "dbId": 48,
      "name": "Facials & Cleanup",
      "gender": "women",
      "items": [
        {
          "id": "qs_41",
          "dbId": 41,
          "title": "O3+ Diamond Glow Facial & De-Tan",
          "category": "Beauty",
          "subcategory": "Facials & Cleanup",
          "rating": "4.91",
          "reviews": "120+ reviews",
          "price": 899.0,
          "originalPrice": 1168,
          "time": "60 mins",
          "duration": "60 mins",
          "brand_name": "O3+ Professional",
          "is_mono_pack": true,
          "parlour_name": "",
          "gender": "women",
          "delivery_mode": "home",
          "badge": "100% Sealed Mono-Pack",
          "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg",
          "features": [
            "100% Sealed Single-Dose Mono-Pack",
            "Single-use disposable gown & cape",
            "Sterilized instruments sealed in pouch"
          ],
          "packages": [
            {
              "name": "Express Glow",
              "price": 899,
              "duration": "45 mins",
              "desc": "Cleansing, scrub and pack"
            },
            {
              "name": "Royal Bridal Glow",
              "price": 1499,
              "duration": "75 mins",
              "desc": "Full 7-step facial with gold serum"
            }
          ]
        }
      ]
    },
    {
      "id": "sub_49",
      "dbId": 49,
      "name": "Waxing & Hair Removal",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_50",
      "dbId": 50,
      "name": "Pedicure & Manicure",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_51",
      "dbId": 51,
      "name": "Hair Spa & Styling",
      "gender": "women",
      "items": []
    }
  ],
  "all_services": [
    {
      "id": "qs_41",
      "dbId": 41,
      "title": "O3+ Diamond Glow Facial & De-Tan",
      "category": "Beauty",
      "subcategory": "Facials & Cleanup",
      "rating": "4.91",
      "reviews": "120+ reviews",
      "price": 899.0,
      "duration": "60 mins",
      "brand_name": "O3+ Professional",
      "is_mono_pack": true,
      "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg"
    }
  ],
  "guarantee": "30-Day Money-Back & Free Re-work Guarantee",
  "damage_cover": "Up to ₹10,000 Free Accidental Damage Cover"
}


API for User Display Beauty Luxury Parlours Directory
url : (http://192.168.1.52:8000/api/user/beauty/parlours/)
method : GET
params :-
gender: women (options: women / men)
response :-
{
  "status": "success",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "parlour",
  "mode_name": "Premium Parlour Services",
  "guarantee": "Zero Waiting Time Guarantee • VIP Slot Reserved",
  "count": 3,
  "parlours": [
    {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
      "rating": "4.94 ★ (3,800+ reviews)",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM",
      "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Lakmé Fashion Week Certified Stylists",
        "Private VIP Bridal Lounge",
        "Complimentary Gourmet Brewed Coffee"
      ],
      "starting_price": 1599,
      "services_count": 4
    },
    {
      "id": "enrich_salon",
      "name": "Enrich Salon & Luxury Spa",
      "brandTag": "Kerastase Paris",
      "tagline": "Kerastase Hair Rituals, K-Glow Facials & BIAB Nails",
      "rating": "4.91 ★ (2,450+ reviews)",
      "location": "4th Block, Koramangala",
      "distance": "1.4 km away",
      "timings": "09:30 AM - 09:30 PM",
      "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Kerastase Certified Master Hair Diagnostics",
        "Dermat-Grade Hydrafacial Suites",
        "Premium Valet Parking"
      ],
      "starting_price": 1299,
      "services_count": 3
    }
  ]
}


API for User Display Beauty Luxury Parlour Details (Services, Slots & Stylists)
url : (http://192.168.1.52:8000/api/user/beauty/parlours/<parlour_id>/)
method : GET
params :-
parlour_id: lakme_luxe (path parameter e.g. lakme_luxe / enrich_salon / truefitt_hill / bounce_salon)
response :-
{
  "status": "success",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "parlour": {
    "id": "lakme_luxe",
    "name": "Lakmé Salon Luxe",
    "brandTag": "Runway Certified",
    "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
    "rating": "4.94 ★ (3,800+ reviews)",
    "location": "100ft Road, Indiranagar",
    "distance": "0.8 km away",
    "timings": "10:00 AM - 09:00 PM",
    "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
    "highlights": [
      "Lakmé Fashion Week Certified Stylists",
      "Private VIP Bridal Lounge",
      "Complimentary Gourmet Brewed Coffee"
    ],
    "starting_price": 1599,
    "services": [
      {
        "id": "lakme_moroccan_spa",
        "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
        "category": "Hair Care",
        "price": 1899,
        "originalPrice": 2499,
        "discount": "24% OFF",
        "time": "60 mins",
        "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
        "desc": "Deep argan oil treatment infused with infrared heat to restore silkiness and mirror shine."
      },
      {
        "id": "lakme_bridal_hd",
        "title": "Runway HD Airbrush Bridal Transformation",
        "category": "Bridal Studio",
        "price": 8999,
        "originalPrice": 12000,
        "discount": "25% OFF",
        "time": "3 Hours",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
        "desc": "Complete pre-bridal skin prep, Temptu HD airbrush base, 3D lash installation, and designer saree draping."
      }
    ]
  },
  "stylist_tiers": [
    {
      "id": "Senior Stylist",
      "name": "Senior Stylist",
      "desc": "Certified Expert (Included)",
      "extra_fee": 0
    },
    {
      "id": "Art Director",
      "name": "Master Art Director",
      "desc": "+₹300 (Celebrity Stylist)",
      "extra_fee": 300
    }
  ],
  "available_dates": [
    {"key": "Today", "label": "Today", "date": "17 Nov, Tue"},
    {"key": "Tomorrow", "label": "Tomorrow", "date": "18 Nov, Wed"}
  ],
  "available_slots": [
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "04:30 PM - 05:30 PM",
    "06:00 PM - 07:00 PM"
  ],
  "booking_terms": "Pay at Salon • Free Cancellation Anytime Before Scheduled Slot"
}


API for User Book Beauty Parlour Appointment / Instant VIP Pass
url : (http://192.168.1.52:8000/api/beauty/book-appointment/)
method : POST
params :-
parlour_id: lakme_luxe
service_id: lakme_moroccan_spa
slot_date: 2026-11-20
slot_time: 02:00 PM - 03:00 PM
stylist_tier: Senior Stylist (options: Senior Stylist / Art Director)
customer_name: Ananya Verma
customer_phone: 9876543210
customer_email: ananya@example.com
response :-
{
  "status": "success",
  "message": "Appointment confirmed at Lakmé Salon Luxe! Pass #LUXE-4821",
  "appointment": {
    "pass_code": "LUXE-4821",
    "booking_id": "BK-A91B2C3D",
    "status": "CONFIRMED",
    "hub": "womens_salon_spa",
    "hub_name": "Women's Salon & Spa",
    "parlour": {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM"
    },
    "service": {
      "id": "lakme_moroccan_spa",
      "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
      "time": "60 mins",
      "category": "Hair Care",
      "price": 1899.0
    },
    "stylist_tier": "Senior Stylist",
    "stylist_label": "Senior Stylist",
    "slot_date": "2026-11-20",
    "slot_time": "02:00 PM - 03:00 PM",
    "customer_name": "Ananya Verma",
    "customer_phone": "9876543210",
    "payment_mode": "PAY_AT_SALON",
    "total_amount": 1899.0,
    "currency": "INR",
    "instructions": [
      "Present VIP Pass #LUXE-4821 at the reception of Lakmé Salon Luxe.",
      "Zero waiting time guaranteed for your reserved time slot.",
      "You can pay after treatment completion via UPI, Card, or Cash."
    ]
  }
}


API for Get SubCategories for a Specific Category
url : (http://192.168.1.52:8000/api/categories/<category_id>/subcategories/)
example : (http://192.168.1.52:8000/api/categories/26/subcategories/)
method : GET
headers :-
(None required)
response :-
{
  "status": "success",
  "category": {
    "id": 26,
    "name": "Plumbing",
    "service_type": "quick_service",
    "status": "active",
    "icon_class": "bi-droplet-fill",
    "icon_color": "#0284c7",
    "image": "http://192.168.1.52:8000/media/categories/plumbing.png"
  },
  "subcategories": [
    {"id": 3, "name": "Pipe & Tap Repair", "status": "active", "services_count": 5},
    {"id": 4, "name": "Water Tank & Motor Installation", "status": "active", "services_count": 2},
    {"id": 5, "name": "Toilet & Sanitary Fitting", "status": "active", "services_count": 4},
    {"id": 6, "name": "Drainage & Blockage Cleaning", "status": "active", "services_count": 3},
    {"id": 7, "name": "Basin & Sink Installation", "status": "active", "services_count": 2}
  ]
}


API for User Display Beauty Experience (Cards: Women vs Men)
url : (http://192.168.1.52:8000/api/user/beauty/)
method : GET
response :-
{
  "status": "success",
  "title": "Beauty & Wellness",
  "subtitle": "Select Experience / Category",
  "experiences": [
    {
      "id": "womens_salon_spa",
      "gender": "women",
      "name": "Women's Salon & Spa",
      "tagline": "At-Home Beauty or Book Top Luxury Parlours",
      "rating": 4.91,
      "reviews_count": "4.2M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 349,
      "formatted_price": "₹349",
      "image": "http://192.168.1.52:8000/static/assets/beauty/women_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/womens_salon_spa.png",
      "hero_title": "Women's Salon, Spa & Parlours",
      "hero_desc": "Doorstep certified beauticians or guaranteed VIP slot at Bengaluru's top luxury salons.",
      "modes": [
        {
          "id": "home",
          "name": "1. Salon at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified beautician visits your home • 100% sealed mono-kits",
          "icon": "home",
          "accent_color": "#ec4899"
        },
        {
          "id": "parlour",
          "name": "2. Premium Parlour Services",
          "badge": "LUXURY SALON BRANDS",
          "description": "Book visit at Lakmé Luxe, Enrich, BBlunt, Toni & Guy in your area",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    },
    {
      "id": "mens_salon_massage",
      "gender": "men",
      "name": "Men's Salon & Massage",
      "tagline": "At-Home Grooming or Book Top Luxury Salons",
      "rating": 4.87,
      "reviews_count": "2.9M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 249,
      "formatted_price": "₹249",
      "image": "http://192.168.1.52:8000/static/assets/beauty/men_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/mens_salon_massage.png",
      "hero_title": "Men's Grooming, Massage & Barbershops",
      "hero_desc": "Certified male barbers at home or royal grooming at Truefitt & Hill, Bounce and top lounges.",
      "modes": [
        {
          "id": "home",
          "name": "1. Grooming & Massage at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified male stylist visits your home • Single-use sterilized tools & vacuum",
          "icon": "home",
          "accent_color": "#0284c7"
        },
        {
          "id": "parlour",
          "name": "2. Premium Barbershop & Lounge",
          "badge": "LUXURY BARBERSHOPS",
          "description": "Book visit at Truefitt & Hill, Bounce, Toni & Guy Men, The Man Company",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    }
  ]
}


API for User Display Beauty Services (At-Home Subcategories & Services)
url : (http://192.168.1.52:8000/api/user/beauty/services/)
method : GET
params :-
gender: women (options: women / men)
delivery_mode: home (options: home / parlour)
response :-
{
  "status": "success",
  "category_id": 37,
  "category_name": "Beauty",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "home",
  "mode_name": "Salon at Home",
  "subcategories": [
    {
      "id": "sub_48",
      "dbId": 48,
      "name": "Facials & Cleanup",
      "gender": "women",
      "items": [
        {
          "id": "qs_41",
          "dbId": 41,
          "title": "O3+ Diamond Glow Facial & De-Tan",
          "category": "Beauty",
          "subcategory": "Facials & Cleanup",
          "rating": "4.91",
          "reviews": "120+ reviews",
          "price": 899.0,
          "originalPrice": 1168,
          "time": "60 mins",
          "duration": "60 mins",
          "brand_name": "O3+ Professional",
          "is_mono_pack": true,
          "parlour_name": "",
          "gender": "women",
          "delivery_mode": "home",
          "badge": "100% Sealed Mono-Pack",
          "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg",
          "features": [
            "100% Sealed Single-Dose Mono-Pack",
            "Single-use disposable gown & cape",
            "Sterilized instruments sealed in pouch"
          ],
          "packages": [
            {
              "name": "Express Glow",
              "price": 899,
              "duration": "45 mins",
              "desc": "Cleansing, scrub and pack"
            },
            {
              "name": "Royal Bridal Glow",
              "price": 1499,
              "duration": "75 mins",
              "desc": "Full 7-step facial with gold serum"
            }
          ]
        }
      ]
    },
    {
      "id": "sub_49",
      "dbId": 49,
      "name": "Waxing & Hair Removal",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_50",
      "dbId": 50,
      "name": "Pedicure & Manicure",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_51",
      "dbId": 51,
      "name": "Hair Spa & Styling",
      "gender": "women",
      "items": []
    }
  ],
  "all_services": [
    {
      "id": "qs_41",
      "dbId": 41,
      "title": "O3+ Diamond Glow Facial & De-Tan",
      "category": "Beauty",
      "subcategory": "Facials & Cleanup",
      "rating": "4.91",
      "reviews": "120+ reviews",
      "price": 899.0,
      "duration": "60 mins",
      "brand_name": "O3+ Professional",
      "is_mono_pack": true,
      "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg"
    }
  ],
  "guarantee": "30-Day Money-Back & Free Re-work Guarantee",
  "damage_cover": "Up to ₹10,000 Free Accidental Damage Cover"
}


API for User Display Beauty Luxury Parlours Directory
url : (http://192.168.1.52:8000/api/user/beauty/parlours/)
method : GET
params :-
gender: women (options: women / men)
response :-
{
  "status": "success",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "parlour",
  "mode_name": "Premium Parlour Services",
  "guarantee": "Zero Waiting Time Guarantee • VIP Slot Reserved",
  "count": 3,
  "parlours": [
    {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
      "rating": "4.94 ★ (3,800+ reviews)",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM",
      "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Lakmé Fashion Week Certified Stylists",
        "Private VIP Bridal Lounge",
        "Complimentary Gourmet Brewed Coffee"
      ],
      "starting_price": 1599,
      "services_count": 4
    },
    {
      "id": "enrich_salon",
      "name": "Enrich Salon & Luxury Spa",
      "brandTag": "Kerastase Paris",
      "tagline": "Kerastase Hair Rituals, K-Glow Facials & BIAB Nails",
      "rating": "4.91 ★ (2,450+ reviews)",
      "location": "4th Block, Koramangala",
      "distance": "1.4 km away",
      "timings": "09:30 AM - 09:30 PM",
      "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Kerastase Certified Master Hair Diagnostics",
        "Dermat-Grade Hydrafacial Suites",
        "Premium Valet Parking"
      ],
      "starting_price": 1299,
      "services_count": 3
    }
  ]
}


API for User Display Beauty Luxury Parlour Details (Services, Slots & Stylists)
url : (http://192.168.1.52:8000/api/user/beauty/parlours/<parlour_id>/)
method : GET
params :-
parlour_id: lakme_luxe (path parameter e.g. lakme_luxe / enrich_salon / truefitt_hill / bounce_salon)
response :-
{
  "status": "success",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "parlour": {
    "id": "lakme_luxe",
    "name": "Lakmé Salon Luxe",
    "brandTag": "Runway Certified",
    "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
    "rating": "4.94 ★ (3,800+ reviews)",
    "location": "100ft Road, Indiranagar",
    "distance": "0.8 km away",
    "timings": "10:00 AM - 09:00 PM",
    "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
    "highlights": [
      "Lakmé Fashion Week Certified Stylists",
      "Private VIP Bridal Lounge",
      "Complimentary Gourmet Brewed Coffee"
    ],
    "starting_price": 1599,
    "services": [
      {
        "id": "lakme_moroccan_spa",
        "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
        "category": "Hair Care",
        "price": 1899,
        "originalPrice": 2499,
        "discount": "24% OFF",
        "time": "60 mins",
        "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
        "desc": "Deep argan oil treatment infused with infrared heat to restore silkiness and mirror shine."
      },
      {
        "id": "lakme_bridal_hd",
        "title": "Runway HD Airbrush Bridal Transformation",
        "category": "Bridal Studio",
        "price": 8999,
        "originalPrice": 12000,
        "discount": "25% OFF",
        "time": "3 Hours",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
        "desc": "Complete pre-bridal skin prep, Temptu HD airbrush base, 3D lash installation, and designer saree draping."
      }
    ]
  },
  "stylist_tiers": [
    {
      "id": "Senior Stylist",
      "name": "Senior Stylist",
      "desc": "Certified Expert (Included)",
      "extra_fee": 0
    },
    {
      "id": "Art Director",
      "name": "Master Art Director",
      "desc": "+₹300 (Celebrity Stylist)",
      "extra_fee": 300
    }
  ],
  "available_dates": [
    {"key": "Today", "label": "Today", "date": "17 Nov, Tue"},
    {"key": "Tomorrow", "label": "Tomorrow", "date": "18 Nov, Wed"}
  ],
  "available_slots": [
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "04:30 PM - 05:30 PM",
    "06:00 PM - 07:00 PM"
  ],
  "booking_terms": "Pay at Salon • Free Cancellation Anytime Before Scheduled Slot"
}


API for User Book Beauty Parlour Appointment / Instant VIP Pass
url : (http://192.168.1.52:8000/api/beauty/book-appointment/)
method : POST
params :-
parlour_id: lakme_luxe
service_id: lakme_moroccan_spa
slot_date: 2026-11-20
slot_time: 02:00 PM - 03:00 PM
stylist_tier: Senior Stylist (options: Senior Stylist / Art Director)
customer_name: Ananya Verma
customer_phone: 9876543210
customer_email: ananya@example.com
response :-
{
  "status": "success",
  "message": "Appointment confirmed at Lakmé Salon Luxe! Pass #LUXE-4821",
  "appointment": {
    "pass_code": "LUXE-4821",
    "booking_id": "BK-A91B2C3D",
    "status": "CONFIRMED",
    "hub": "womens_salon_spa",
    "hub_name": "Women's Salon & Spa",
    "parlour": {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM"
    },
    "service": {
      "id": "lakme_moroccan_spa",
      "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
      "time": "60 mins",
      "category": "Hair Care",
      "price": 1899.0
    },
    "stylist_tier": "Senior Stylist",
    "stylist_label": "Senior Stylist",
    "slot_date": "2026-11-20",
    "slot_time": "02:00 PM - 03:00 PM",
    "customer_name": "Ananya Verma",
    "customer_phone": "9876543210",
    "payment_mode": "PAY_AT_SALON",
    "total_amount": 1899.0,
    "currency": "INR",
    "instructions": [
      "Present VIP Pass #LUXE-4821 at the reception of Lakmé Salon Luxe.",
      "Zero waiting time guaranteed for your reserved time slot.",
      "You can pay after treatment completion via UPI, Card, or Cash."
    ]
  }
}


API for Browse Quick Services (Filter by Category and SubCategory)
url : (http://192.168.1.52:8000/api/user/quick-services/)
method : GET
params :-
category_id:26 (optional)
subcategory_id:3 (optional - filter by SubCategory ID)
subcategory:Pipe & Tap Repair (optional - filter by SubCategory name)
city:Ranchi (optional)
search:tap repair (optional)
response :-
{
  "status": "success",
  "total": 5,
  "services": [
    {
      "id": 1,
      "title": "Kitchen Sink & Tap Leak Repair",
      "category": "Plumbing",
      "category_id": 26,
      "subcategory": "Pipe & Tap Repair",
      "subcategory_id": 3,
      "base_price": 299.0,
      "image": "http://192.168.1.52:8000/media/quick_services/sink_repair.jpg",
      "service_packages": [
        {"name": "Standard Inspection & Minor Leak Fix", "price": 299},
        {"name": "Complete Tap Replacement (Material Extra)", "price": 499}
      ],
      "vendor": {
        "id": 27,
        "name": "Ranchi Plumbing Experts",
        "rating": 4.8,
        "reviews_count": 34
      }
    }
  ]
}


API for User Display Beauty Experience (Cards: Women vs Men)
url : (http://192.168.1.52:8000/api/user/beauty/)
method : GET
response :-
{
  "status": "success",
  "title": "Beauty & Wellness",
  "subtitle": "Select Experience / Category",
  "experiences": [
    {
      "id": "womens_salon_spa",
      "gender": "women",
      "name": "Women's Salon & Spa",
      "tagline": "At-Home Beauty or Book Top Luxury Parlours",
      "rating": 4.91,
      "reviews_count": "4.2M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 349,
      "formatted_price": "₹349",
      "image": "http://192.168.1.52:8000/static/assets/beauty/women_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/womens_salon_spa.png",
      "hero_title": "Women's Salon, Spa & Parlours",
      "hero_desc": "Doorstep certified beauticians or guaranteed VIP slot at Bengaluru's top luxury salons.",
      "modes": [
        {
          "id": "home",
          "name": "1. Salon at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified beautician visits your home • 100% sealed mono-kits",
          "icon": "home",
          "accent_color": "#ec4899"
        },
        {
          "id": "parlour",
          "name": "2. Premium Parlour Services",
          "badge": "LUXURY SALON BRANDS",
          "description": "Book visit at Lakmé Luxe, Enrich, BBlunt, Toni & Guy in your area",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    },
    {
      "id": "mens_salon_massage",
      "gender": "men",
      "name": "Men's Salon & Massage",
      "tagline": "At-Home Grooming or Book Top Luxury Salons",
      "rating": 4.87,
      "reviews_count": "2.9M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 249,
      "formatted_price": "₹249",
      "image": "http://192.168.1.52:8000/static/assets/beauty/men_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/mens_salon_massage.png",
      "hero_title": "Men's Grooming, Massage & Barbershops",
      "hero_desc": "Certified male barbers at home or royal grooming at Truefitt & Hill, Bounce and top lounges.",
      "modes": [
        {
          "id": "home",
          "name": "1. Grooming & Massage at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified male stylist visits your home • Single-use sterilized tools & vacuum",
          "icon": "home",
          "accent_color": "#0284c7"
        },
        {
          "id": "parlour",
          "name": "2. Premium Barbershop & Lounge",
          "badge": "LUXURY BARBERSHOPS",
          "description": "Book visit at Truefitt & Hill, Bounce, Toni & Guy Men, The Man Company",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    }
  ]
}


API for User Display Beauty Services (At-Home Subcategories & Services)
url : (http://192.168.1.52:8000/api/user/beauty/services/)
method : GET
params :-
gender: women (options: women / men)
delivery_mode: home (options: home / parlour)
response :-
{
  "status": "success",
  "category_id": 37,
  "category_name": "Beauty",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "home",
  "mode_name": "Salon at Home",
  "subcategories": [
    {
      "id": "sub_48",
      "dbId": 48,
      "name": "Facials & Cleanup",
      "gender": "women",
      "items": [
        {
          "id": "qs_41",
          "dbId": 41,
          "title": "O3+ Diamond Glow Facial & De-Tan",
          "category": "Beauty",
          "subcategory": "Facials & Cleanup",
          "rating": "4.91",
          "reviews": "120+ reviews",
          "price": 899.0,
          "originalPrice": 1168,
          "time": "60 mins",
          "duration": "60 mins",
          "brand_name": "O3+ Professional",
          "is_mono_pack": true,
          "parlour_name": "",
          "gender": "women",
          "delivery_mode": "home",
          "badge": "100% Sealed Mono-Pack",
          "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg",
          "features": [
            "100% Sealed Single-Dose Mono-Pack",
            "Single-use disposable gown & cape",
            "Sterilized instruments sealed in pouch"
          ],
          "packages": [
            {
              "name": "Express Glow",
              "price": 899,
              "duration": "45 mins",
              "desc": "Cleansing, scrub and pack"
            },
            {
              "name": "Royal Bridal Glow",
              "price": 1499,
              "duration": "75 mins",
              "desc": "Full 7-step facial with gold serum"
            }
          ]
        }
      ]
    },
    {
      "id": "sub_49",
      "dbId": 49,
      "name": "Waxing & Hair Removal",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_50",
      "dbId": 50,
      "name": "Pedicure & Manicure",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_51",
      "dbId": 51,
      "name": "Hair Spa & Styling",
      "gender": "women",
      "items": []
    }
  ],
  "all_services": [
    {
      "id": "qs_41",
      "dbId": 41,
      "title": "O3+ Diamond Glow Facial & De-Tan",
      "category": "Beauty",
      "subcategory": "Facials & Cleanup",
      "rating": "4.91",
      "reviews": "120+ reviews",
      "price": 899.0,
      "duration": "60 mins",
      "brand_name": "O3+ Professional",
      "is_mono_pack": true,
      "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg"
    }
  ],
  "guarantee": "30-Day Money-Back & Free Re-work Guarantee",
  "damage_cover": "Up to ₹10,000 Free Accidental Damage Cover"
}


API for User Display Beauty Luxury Parlours Directory
url : (http://192.168.1.52:8000/api/user/beauty/parlours/)
method : GET
params :-
gender: women (options: women / men)
response :-
{
  "status": "success",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "parlour",
  "mode_name": "Premium Parlour Services",
  "guarantee": "Zero Waiting Time Guarantee • VIP Slot Reserved",
  "count": 3,
  "parlours": [
    {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
      "rating": "4.94 ★ (3,800+ reviews)",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM",
      "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Lakmé Fashion Week Certified Stylists",
        "Private VIP Bridal Lounge",
        "Complimentary Gourmet Brewed Coffee"
      ],
      "starting_price": 1599,
      "services_count": 4
    },
    {
      "id": "enrich_salon",
      "name": "Enrich Salon & Luxury Spa",
      "brandTag": "Kerastase Paris",
      "tagline": "Kerastase Hair Rituals, K-Glow Facials & BIAB Nails",
      "rating": "4.91 ★ (2,450+ reviews)",
      "location": "4th Block, Koramangala",
      "distance": "1.4 km away",
      "timings": "09:30 AM - 09:30 PM",
      "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Kerastase Certified Master Hair Diagnostics",
        "Dermat-Grade Hydrafacial Suites",
        "Premium Valet Parking"
      ],
      "starting_price": 1299,
      "services_count": 3
    }
  ]
}


API for User Display Beauty Luxury Parlour Details (Services, Slots & Stylists)
url : (http://192.168.1.52:8000/api/user/beauty/parlours/<parlour_id>/)
method : GET
params :-
parlour_id: lakme_luxe (path parameter e.g. lakme_luxe / enrich_salon / truefitt_hill / bounce_salon)
response :-
{
  "status": "success",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "parlour": {
    "id": "lakme_luxe",
    "name": "Lakmé Salon Luxe",
    "brandTag": "Runway Certified",
    "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
    "rating": "4.94 ★ (3,800+ reviews)",
    "location": "100ft Road, Indiranagar",
    "distance": "0.8 km away",
    "timings": "10:00 AM - 09:00 PM",
    "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
    "highlights": [
      "Lakmé Fashion Week Certified Stylists",
      "Private VIP Bridal Lounge",
      "Complimentary Gourmet Brewed Coffee"
    ],
    "starting_price": 1599,
    "services": [
      {
        "id": "lakme_moroccan_spa",
        "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
        "category": "Hair Care",
        "price": 1899,
        "originalPrice": 2499,
        "discount": "24% OFF",
        "time": "60 mins",
        "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
        "desc": "Deep argan oil treatment infused with infrared heat to restore silkiness and mirror shine."
      },
      {
        "id": "lakme_bridal_hd",
        "title": "Runway HD Airbrush Bridal Transformation",
        "category": "Bridal Studio",
        "price": 8999,
        "originalPrice": 12000,
        "discount": "25% OFF",
        "time": "3 Hours",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
        "desc": "Complete pre-bridal skin prep, Temptu HD airbrush base, 3D lash installation, and designer saree draping."
      }
    ]
  },
  "stylist_tiers": [
    {
      "id": "Senior Stylist",
      "name": "Senior Stylist",
      "desc": "Certified Expert (Included)",
      "extra_fee": 0
    },
    {
      "id": "Art Director",
      "name": "Master Art Director",
      "desc": "+₹300 (Celebrity Stylist)",
      "extra_fee": 300
    }
  ],
  "available_dates": [
    {"key": "Today", "label": "Today", "date": "17 Nov, Tue"},
    {"key": "Tomorrow", "label": "Tomorrow", "date": "18 Nov, Wed"}
  ],
  "available_slots": [
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "04:30 PM - 05:30 PM",
    "06:00 PM - 07:00 PM"
  ],
  "booking_terms": "Pay at Salon • Free Cancellation Anytime Before Scheduled Slot"
}


API for User Book Beauty Parlour Appointment / Instant VIP Pass
url : (http://192.168.1.52:8000/api/beauty/book-appointment/)
method : POST
params :-
parlour_id: lakme_luxe
service_id: lakme_moroccan_spa
slot_date: 2026-11-20
slot_time: 02:00 PM - 03:00 PM
stylist_tier: Senior Stylist (options: Senior Stylist / Art Director)
customer_name: Ananya Verma
customer_phone: 9876543210
customer_email: ananya@example.com
response :-
{
  "status": "success",
  "message": "Appointment confirmed at Lakmé Salon Luxe! Pass #LUXE-4821",
  "appointment": {
    "pass_code": "LUXE-4821",
    "booking_id": "BK-A91B2C3D",
    "status": "CONFIRMED",
    "hub": "womens_salon_spa",
    "hub_name": "Women's Salon & Spa",
    "parlour": {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM"
    },
    "service": {
      "id": "lakme_moroccan_spa",
      "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
      "time": "60 mins",
      "category": "Hair Care",
      "price": 1899.0
    },
    "stylist_tier": "Senior Stylist",
    "stylist_label": "Senior Stylist",
    "slot_date": "2026-11-20",
    "slot_time": "02:00 PM - 03:00 PM",
    "customer_name": "Ananya Verma",
    "customer_phone": "9876543210",
    "payment_mode": "PAY_AT_SALON",
    "total_amount": 1899.0,
    "currency": "INR",
    "instructions": [
      "Present VIP Pass #LUXE-4821 at the reception of Lakmé Salon Luxe.",
      "Zero waiting time guaranteed for your reserved time slot.",
      "You can pay after treatment completion via UPI, Card, or Cash."
    ]
  }
}


API for User Post Job 
url : (http://192.168.1.52:8000/api/user/post-job/)
method : POST (multipart/form-data or application/json)
headers :-
Authorization: Bearer <token>
Content-Type: multipart/form-data (recommended when attaching photos) or application/json
params :-
title:Full Commercial Office Interior & AC Setup
budget:150000
category_id:28 (or category:AC & Appliance)
subcategory_id:13 (or subcategory:AC Servicing & Jet Cleaning)
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
images:[site_photo_1.jpg, site_photo_2.jpg] (File Upload - optional, attaches photos directly in THIS single request)
response :-
{
"status": "success",
"message": "Job posted successfully",
"job": {
"id": 14,
"job_code": "JOB-0014",
"title": "Full Commercial Office Interior & AC Setup",
"category": "AC & Appliance",
"category_id": 28,
"subcategory": "AC Servicing & Jet Cleaning",
"subcategory_id": 13,
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
"image": "http://192.168.1.52:8000/media/jobs/cabinet.jpg",
"images": [
"http://192.168.1.52:8000/media/jobs/gallery/site_photo_1.jpg",
"http://192.168.1.52:8000/media/jobs/gallery/site_photo_2.jpg"
],
"created_at": "2026-09-16 18:04:56"
}
}

Flutter (Dio) Multi-Image Example:
```dart
List<MultipartFile> imageFiles = [];
for (var file in pickedFiles) {
  imageFiles.add(await MultipartFile.fromFile(file.path, filename: file.name));
}

FormData formData = FormData.fromMap({
  'title': 'Leaking Tap Wash Basin',
  'budget': '1500',
  'category_id': '26',
  'subcategory_id': '3',
  'description': 'Water leaking under cabinet',
  'address': 'Main Road, Namkum',
  'city': 'Ranchi',
  'images': imageFiles, // Supports 1, 2, 5, or more images
});

Response response = await dio.post(
  'http://infinityventures.brightcodeapp.com/api/user/post-job/',
  data: formData,
  options: Options(headers: {'Authorization': 'Bearer $token'}),
);
```


API for User Fetch Posted Jobs (with Category & SubCategory)
url : (http://192.168.1.52:8000/api/user/jobs/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "jobs": [
    {
      "id": 14,
      "title": "Full Commercial Office Interior & AC Setup",
      "category": "AC & Appliance",
      "category_id": 28,
      "subcategory": "AC Servicing & Jet Cleaning",
      "subcategory_id": 13,
      "description": "Need full setup for new 2500 sq ft office space with HVAC and partition work",
      "budget": 150000.0,
      "budget_type": "Fixed Price",
      "status": "open",
      "created_at": "2026-09-16 18:04:56",
      "location": "Mumbai",
      "bids_count": 3,
      "assigned_vendor": null
    }
  ]
}


API for User Display Beauty Experience (Cards: Women vs Men)
url : (http://192.168.1.52:8000/api/user/beauty/)
method : GET
response :-
{
  "status": "success",
  "title": "Beauty & Wellness",
  "subtitle": "Select Experience / Category",
  "experiences": [
    {
      "id": "womens_salon_spa",
      "gender": "women",
      "name": "Women's Salon & Spa",
      "tagline": "At-Home Beauty or Book Top Luxury Parlours",
      "rating": 4.91,
      "reviews_count": "4.2M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 349,
      "formatted_price": "₹349",
      "image": "http://192.168.1.52:8000/static/assets/beauty/women_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/womens_salon_spa.png",
      "hero_title": "Women's Salon, Spa & Parlours",
      "hero_desc": "Doorstep certified beauticians or guaranteed VIP slot at Bengaluru's top luxury salons.",
      "modes": [
        {
          "id": "home",
          "name": "1. Salon at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified beautician visits your home • 100% sealed mono-kits",
          "icon": "home",
          "accent_color": "#ec4899"
        },
        {
          "id": "parlour",
          "name": "2. Premium Parlour Services",
          "badge": "LUXURY SALON BRANDS",
          "description": "Book visit at Lakmé Luxe, Enrich, BBlunt, Toni & Guy in your area",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    },
    {
      "id": "mens_salon_massage",
      "gender": "men",
      "name": "Men's Salon & Massage",
      "tagline": "At-Home Grooming or Book Top Luxury Salons",
      "rating": 4.87,
      "reviews_count": "2.9M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 249,
      "formatted_price": "₹249",
      "image": "http://192.168.1.52:8000/static/assets/beauty/men_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/mens_salon_massage.png",
      "hero_title": "Men's Grooming, Massage & Barbershops",
      "hero_desc": "Certified male barbers at home or royal grooming at Truefitt & Hill, Bounce and top lounges.",
      "modes": [
        {
          "id": "home",
          "name": "1. Grooming & Massage at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified male stylist visits your home • Single-use sterilized tools & vacuum",
          "icon": "home",
          "accent_color": "#0284c7"
        },
        {
          "id": "parlour",
          "name": "2. Premium Barbershop & Lounge",
          "badge": "LUXURY BARBERSHOPS",
          "description": "Book visit at Truefitt & Hill, Bounce, Toni & Guy Men, The Man Company",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    }
  ]
}


API for User Display Beauty Services (At-Home Subcategories & Services)
url : (http://192.168.1.52:8000/api/user/beauty/services/)
method : GET
params :-
gender: women (options: women / men)
delivery_mode: home (options: home / parlour)
response :-
{
  "status": "success",
  "category_id": 37,
  "category_name": "Beauty",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "home",
  "mode_name": "Salon at Home",
  "subcategories": [
    {
      "id": "sub_48",
      "dbId": 48,
      "name": "Facials & Cleanup",
      "gender": "women",
      "items": [
        {
          "id": "qs_41",
          "dbId": 41,
          "title": "O3+ Diamond Glow Facial & De-Tan",
          "category": "Beauty",
          "subcategory": "Facials & Cleanup",
          "rating": "4.91",
          "reviews": "120+ reviews",
          "price": 899.0,
          "originalPrice": 1168,
          "time": "60 mins",
          "duration": "60 mins",
          "brand_name": "O3+ Professional",
          "is_mono_pack": true,
          "parlour_name": "",
          "gender": "women",
          "delivery_mode": "home",
          "badge": "100% Sealed Mono-Pack",
          "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg",
          "features": [
            "100% Sealed Single-Dose Mono-Pack",
            "Single-use disposable gown & cape",
            "Sterilized instruments sealed in pouch"
          ],
          "packages": [
            {
              "name": "Express Glow",
              "price": 899,
              "duration": "45 mins",
              "desc": "Cleansing, scrub and pack"
            },
            {
              "name": "Royal Bridal Glow",
              "price": 1499,
              "duration": "75 mins",
              "desc": "Full 7-step facial with gold serum"
            }
          ]
        }
      ]
    },
    {
      "id": "sub_49",
      "dbId": 49,
      "name": "Waxing & Hair Removal",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_50",
      "dbId": 50,
      "name": "Pedicure & Manicure",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_51",
      "dbId": 51,
      "name": "Hair Spa & Styling",
      "gender": "women",
      "items": []
    }
  ],
  "all_services": [
    {
      "id": "qs_41",
      "dbId": 41,
      "title": "O3+ Diamond Glow Facial & De-Tan",
      "category": "Beauty",
      "subcategory": "Facials & Cleanup",
      "rating": "4.91",
      "reviews": "120+ reviews",
      "price": 899.0,
      "duration": "60 mins",
      "brand_name": "O3+ Professional",
      "is_mono_pack": true,
      "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg"
    }
  ],
  "guarantee": "30-Day Money-Back & Free Re-work Guarantee",
  "damage_cover": "Up to ₹10,000 Free Accidental Damage Cover"
}


API for User Display Beauty Luxury Parlours Directory
url : (http://192.168.1.52:8000/api/user/beauty/parlours/)
method : GET
params :-
gender: women (options: women / men)
response :-
{
  "status": "success",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "parlour",
  "mode_name": "Premium Parlour Services",
  "guarantee": "Zero Waiting Time Guarantee • VIP Slot Reserved",
  "count": 3,
  "parlours": [
    {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
      "rating": "4.94 ★ (3,800+ reviews)",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM",
      "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Lakmé Fashion Week Certified Stylists",
        "Private VIP Bridal Lounge",
        "Complimentary Gourmet Brewed Coffee"
      ],
      "starting_price": 1599,
      "services_count": 4
    },
    {
      "id": "enrich_salon",
      "name": "Enrich Salon & Luxury Spa",
      "brandTag": "Kerastase Paris",
      "tagline": "Kerastase Hair Rituals, K-Glow Facials & BIAB Nails",
      "rating": "4.91 ★ (2,450+ reviews)",
      "location": "4th Block, Koramangala",
      "distance": "1.4 km away",
      "timings": "09:30 AM - 09:30 PM",
      "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Kerastase Certified Master Hair Diagnostics",
        "Dermat-Grade Hydrafacial Suites",
        "Premium Valet Parking"
      ],
      "starting_price": 1299,
      "services_count": 3
    }
  ]
}


API for User Display Beauty Luxury Parlour Details (Services, Slots & Stylists)
url : (http://192.168.1.52:8000/api/user/beauty/parlours/<parlour_id>/)
method : GET
params :-
parlour_id: lakme_luxe (path parameter e.g. lakme_luxe / enrich_salon / truefitt_hill / bounce_salon)
response :-
{
  "status": "success",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "parlour": {
    "id": "lakme_luxe",
    "name": "Lakmé Salon Luxe",
    "brandTag": "Runway Certified",
    "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
    "rating": "4.94 ★ (3,800+ reviews)",
    "location": "100ft Road, Indiranagar",
    "distance": "0.8 km away",
    "timings": "10:00 AM - 09:00 PM",
    "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
    "highlights": [
      "Lakmé Fashion Week Certified Stylists",
      "Private VIP Bridal Lounge",
      "Complimentary Gourmet Brewed Coffee"
    ],
    "starting_price": 1599,
    "services": [
      {
        "id": "lakme_moroccan_spa",
        "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
        "category": "Hair Care",
        "price": 1899,
        "originalPrice": 2499,
        "discount": "24% OFF",
        "time": "60 mins",
        "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
        "desc": "Deep argan oil treatment infused with infrared heat to restore silkiness and mirror shine."
      },
      {
        "id": "lakme_bridal_hd",
        "title": "Runway HD Airbrush Bridal Transformation",
        "category": "Bridal Studio",
        "price": 8999,
        "originalPrice": 12000,
        "discount": "25% OFF",
        "time": "3 Hours",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
        "desc": "Complete pre-bridal skin prep, Temptu HD airbrush base, 3D lash installation, and designer saree draping."
      }
    ]
  },
  "stylist_tiers": [
    {
      "id": "Senior Stylist",
      "name": "Senior Stylist",
      "desc": "Certified Expert (Included)",
      "extra_fee": 0
    },
    {
      "id": "Art Director",
      "name": "Master Art Director",
      "desc": "+₹300 (Celebrity Stylist)",
      "extra_fee": 300
    }
  ],
  "available_dates": [
    {"key": "Today", "label": "Today", "date": "17 Nov, Tue"},
    {"key": "Tomorrow", "label": "Tomorrow", "date": "18 Nov, Wed"}
  ],
  "available_slots": [
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "04:30 PM - 05:30 PM",
    "06:00 PM - 07:00 PM"
  ],
  "booking_terms": "Pay at Salon • Free Cancellation Anytime Before Scheduled Slot"
}


API for User Book Beauty Parlour Appointment / Instant VIP Pass
url : (http://192.168.1.52:8000/api/beauty/book-appointment/)
method : POST
params :-
parlour_id: lakme_luxe
service_id: lakme_moroccan_spa
slot_date: 2026-11-20
slot_time: 02:00 PM - 03:00 PM
stylist_tier: Senior Stylist (options: Senior Stylist / Art Director)
customer_name: Ananya Verma
customer_phone: 9876543210
customer_email: ananya@example.com
response :-
{
  "status": "success",
  "message": "Appointment confirmed at Lakmé Salon Luxe! Pass #LUXE-4821",
  "appointment": {
    "pass_code": "LUXE-4821",
    "booking_id": "BK-A91B2C3D",
    "status": "CONFIRMED",
    "hub": "womens_salon_spa",
    "hub_name": "Women's Salon & Spa",
    "parlour": {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM"
    },
    "service": {
      "id": "lakme_moroccan_spa",
      "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
      "time": "60 mins",
      "category": "Hair Care",
      "price": 1899.0
    },
    "stylist_tier": "Senior Stylist",
    "stylist_label": "Senior Stylist",
    "slot_date": "2026-11-20",
    "slot_time": "02:00 PM - 03:00 PM",
    "customer_name": "Ananya Verma",
    "customer_phone": "9876543210",
    "payment_mode": "PAY_AT_SALON",
    "total_amount": 1899.0,
    "currency": "INR",
    "instructions": [
      "Present VIP Pass #LUXE-4821 at the reception of Lakmé Salon Luxe.",
      "Zero waiting time guaranteed for your reserved time slot.",
      "You can pay after treatment completion via UPI, Card, or Cash."
    ]
  }
}


API for User Book a Quick Service (15-Min Doorstep Service)
url : (http://192.168.1.52:8000/api/user/services/book/)
method : POST
headers :-
Authorization: Bearer <token>
Content-Type: application/json or multipart/form-data
params :-
qs_id:14 (Required - ID of the QuickService chosen from catalog/search)
package_name:Standard 2BHK (optional - default: Standard)
total_amount:2499.0 (Required - service price)
scheduled_date:2026-10-20 (Required - YYYY-MM-DD)
scheduled_time:10:00 AM (optional - HH:MM AM/PM or 24-hr HH:MM)
service_address:Flat 402, Green Valley Apartments, Kanke Road, Ranchi (Required)
additional_notes:Doorbell not working, call on arrival (optional)
response :-
{
"status": "success",
"message": "Service booked successfully! Awaiting vendor acceptance.",
"booking_id": 8,
"booking": {
"id": 8,
"booking_code": "BK-0008",
"service_id": 14,
"service_title": "AC Repair & Jet Servicing",
"vendor_id": 27,
"vendor_name": "Rajesh Sharma",
"package_name": "Standard 2BHK",
"scheduled_date": "2026-10-20",
"scheduled_time": "10:00:00",
"total_amount": 2499.0,
"service_address": "Flat 402, Green Valley Apartments, Kanke Road, Ranchi",
"additional_notes": "Doorbell not working, call on arrival",
"status": "pending",
"payment_status": "pending",
"created_at": "2026-10-16 14:30:00"
}
}


API for User Dashboard (Counters & Recent Activity)
url : (http://192.168.1.52:8000/api/user/dashboard/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "data": {
    "active_jobs_count": 3,
    "active_bookings_count": 2,
    "pending_bids_count": 5,
    "selected_vendors_count": 2,
    "completed_jobs_count": 4,
    "completed_bookings_count": 6,
    "total_spent": 18500.0,
    "recent_jobs": [
      {
        "id": 12,
        "title": "Emergency Server Room AC Repair",
        "category": "AC Repair",
        "budget": 3500.0,
        "budget_type": "Fixed",
        "status": "open",
        "city": "Mumbai",
        "bids_count": 2,
        "assigned_vendor": null,
        "image": "http://192.168.1.52:8000/media/jobs/photo.jpg",
        "created_at": "2026-09-16 18:04:35"
      }
    ],
    "recent_bookings": [
      {
        "id": 8,
        "service_title": "Deep Home Cleaning",
        "package_name": "Standard 2BHK",
        "vendor_name": "Sparkle Cleaners",
        "total_amount": 2499.0,
        "scheduled_date": "2026-09-18",
        "status": "accepted",
        "payment_status": "paid",
        "created_at": "2026-09-16 12:30:00"
      }
    ]
  }
}


API for Job Image Gallery Upload (Optional - Add Photos to Existing Job)
Note: This endpoint is OPTIONAL. Images can already be uploaded directly during initial job creation via POST /api/user/post-job/. Use this endpoint only if a user wants to append additional photos to a job after it has already been posted.
url : (http://192.168.1.52:8000/api/user/jobs/<job_id>/images/upload/)
method : POST (multipart/form-data)
headers :-
Authorization: Bearer <token>
params :-
images: [file_1, file_2]
response :-
{
  "status": "success",
  "message": "2 gallery image(s) uploaded successfully",
  "count": 2,
  "data": [
    {
      "id": 1,
      "image_url": "http://192.168.1.52:8000/media/jobs/gallery/site1.jpg",
      "created_at": "2026-10-16 11:30:00"
    },
    {
      "id": 2,
      "image_url": "http://192.168.1.52:8000/media/jobs/gallery/site2.jpg",
      "created_at": "2026-10-16 11:30:00"
    }
  ]
}


API for User Display Beauty Experience (Cards: Women vs Men)
url : (http://192.168.1.52:8000/api/user/beauty/)
method : GET
response :-
{
  "status": "success",
  "title": "Beauty & Wellness",
  "subtitle": "Select Experience / Category",
  "experiences": [
    {
      "id": "womens_salon_spa",
      "gender": "women",
      "name": "Women's Salon & Spa",
      "tagline": "At-Home Beauty or Book Top Luxury Parlours",
      "rating": 4.91,
      "reviews_count": "4.2M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 349,
      "formatted_price": "₹349",
      "image": "http://192.168.1.52:8000/static/assets/beauty/women_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/womens_salon_spa.png",
      "hero_title": "Women's Salon, Spa & Parlours",
      "hero_desc": "Doorstep certified beauticians or guaranteed VIP slot at Bengaluru's top luxury salons.",
      "modes": [
        {
          "id": "home",
          "name": "1. Salon at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified beautician visits your home • 100% sealed mono-kits",
          "icon": "home",
          "accent_color": "#ec4899"
        },
        {
          "id": "parlour",
          "name": "2. Premium Parlour Services",
          "badge": "LUXURY SALON BRANDS",
          "description": "Book visit at Lakmé Luxe, Enrich, BBlunt, Toni & Guy in your area",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    },
    {
      "id": "mens_salon_massage",
      "gender": "men",
      "name": "Men's Salon & Massage",
      "tagline": "At-Home Grooming or Book Top Luxury Salons",
      "rating": 4.87,
      "reviews_count": "2.9M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 249,
      "formatted_price": "₹249",
      "image": "http://192.168.1.52:8000/static/assets/beauty/men_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/mens_salon_massage.png",
      "hero_title": "Men's Grooming, Massage & Barbershops",
      "hero_desc": "Certified male barbers at home or royal grooming at Truefitt & Hill, Bounce and top lounges.",
      "modes": [
        {
          "id": "home",
          "name": "1. Grooming & Massage at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified male stylist visits your home • Single-use sterilized tools & vacuum",
          "icon": "home",
          "accent_color": "#0284c7"
        },
        {
          "id": "parlour",
          "name": "2. Premium Barbershop & Lounge",
          "badge": "LUXURY BARBERSHOPS",
          "description": "Book visit at Truefitt & Hill, Bounce, Toni & Guy Men, The Man Company",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    }
  ]
}


API for User Display Beauty Services (At-Home Subcategories & Services)
url : (http://192.168.1.52:8000/api/user/beauty/services/)
method : GET
params :-
gender: women (options: women / men)
delivery_mode: home (options: home / parlour)
response :-
{
  "status": "success",
  "category_id": 37,
  "category_name": "Beauty",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "home",
  "mode_name": "Salon at Home",
  "subcategories": [
    {
      "id": "sub_48",
      "dbId": 48,
      "name": "Facials & Cleanup",
      "gender": "women",
      "items": [
        {
          "id": "qs_41",
          "dbId": 41,
          "title": "O3+ Diamond Glow Facial & De-Tan",
          "category": "Beauty",
          "subcategory": "Facials & Cleanup",
          "rating": "4.91",
          "reviews": "120+ reviews",
          "price": 899.0,
          "originalPrice": 1168,
          "time": "60 mins",
          "duration": "60 mins",
          "brand_name": "O3+ Professional",
          "is_mono_pack": true,
          "parlour_name": "",
          "gender": "women",
          "delivery_mode": "home",
          "badge": "100% Sealed Mono-Pack",
          "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg",
          "features": [
            "100% Sealed Single-Dose Mono-Pack",
            "Single-use disposable gown & cape",
            "Sterilized instruments sealed in pouch"
          ],
          "packages": [
            {
              "name": "Express Glow",
              "price": 899,
              "duration": "45 mins",
              "desc": "Cleansing, scrub and pack"
            },
            {
              "name": "Royal Bridal Glow",
              "price": 1499,
              "duration": "75 mins",
              "desc": "Full 7-step facial with gold serum"
            }
          ]
        }
      ]
    },
    {
      "id": "sub_49",
      "dbId": 49,
      "name": "Waxing & Hair Removal",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_50",
      "dbId": 50,
      "name": "Pedicure & Manicure",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_51",
      "dbId": 51,
      "name": "Hair Spa & Styling",
      "gender": "women",
      "items": []
    }
  ],
  "all_services": [
    {
      "id": "qs_41",
      "dbId": 41,
      "title": "O3+ Diamond Glow Facial & De-Tan",
      "category": "Beauty",
      "subcategory": "Facials & Cleanup",
      "rating": "4.91",
      "reviews": "120+ reviews",
      "price": 899.0,
      "duration": "60 mins",
      "brand_name": "O3+ Professional",
      "is_mono_pack": true,
      "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg"
    }
  ],
  "guarantee": "30-Day Money-Back & Free Re-work Guarantee",
  "damage_cover": "Up to ₹10,000 Free Accidental Damage Cover"
}


API for User Display Beauty Luxury Parlours Directory
url : (http://192.168.1.52:8000/api/user/beauty/parlours/)
method : GET
params :-
gender: women (options: women / men)
response :-
{
  "status": "success",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "parlour",
  "mode_name": "Premium Parlour Services",
  "guarantee": "Zero Waiting Time Guarantee • VIP Slot Reserved",
  "count": 3,
  "parlours": [
    {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
      "rating": "4.94 ★ (3,800+ reviews)",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM",
      "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Lakmé Fashion Week Certified Stylists",
        "Private VIP Bridal Lounge",
        "Complimentary Gourmet Brewed Coffee"
      ],
      "starting_price": 1599,
      "services_count": 4
    },
    {
      "id": "enrich_salon",
      "name": "Enrich Salon & Luxury Spa",
      "brandTag": "Kerastase Paris",
      "tagline": "Kerastase Hair Rituals, K-Glow Facials & BIAB Nails",
      "rating": "4.91 ★ (2,450+ reviews)",
      "location": "4th Block, Koramangala",
      "distance": "1.4 km away",
      "timings": "09:30 AM - 09:30 PM",
      "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Kerastase Certified Master Hair Diagnostics",
        "Dermat-Grade Hydrafacial Suites",
        "Premium Valet Parking"
      ],
      "starting_price": 1299,
      "services_count": 3
    }
  ]
}


API for User Display Beauty Luxury Parlour Details (Services, Slots & Stylists)
url : (http://192.168.1.52:8000/api/user/beauty/parlours/<parlour_id>/)
method : GET
params :-
parlour_id: lakme_luxe (path parameter e.g. lakme_luxe / enrich_salon / truefitt_hill / bounce_salon)
response :-
{
  "status": "success",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "parlour": {
    "id": "lakme_luxe",
    "name": "Lakmé Salon Luxe",
    "brandTag": "Runway Certified",
    "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
    "rating": "4.94 ★ (3,800+ reviews)",
    "location": "100ft Road, Indiranagar",
    "distance": "0.8 km away",
    "timings": "10:00 AM - 09:00 PM",
    "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
    "highlights": [
      "Lakmé Fashion Week Certified Stylists",
      "Private VIP Bridal Lounge",
      "Complimentary Gourmet Brewed Coffee"
    ],
    "starting_price": 1599,
    "services": [
      {
        "id": "lakme_moroccan_spa",
        "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
        "category": "Hair Care",
        "price": 1899,
        "originalPrice": 2499,
        "discount": "24% OFF",
        "time": "60 mins",
        "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
        "desc": "Deep argan oil treatment infused with infrared heat to restore silkiness and mirror shine."
      },
      {
        "id": "lakme_bridal_hd",
        "title": "Runway HD Airbrush Bridal Transformation",
        "category": "Bridal Studio",
        "price": 8999,
        "originalPrice": 12000,
        "discount": "25% OFF",
        "time": "3 Hours",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
        "desc": "Complete pre-bridal skin prep, Temptu HD airbrush base, 3D lash installation, and designer saree draping."
      }
    ]
  },
  "stylist_tiers": [
    {
      "id": "Senior Stylist",
      "name": "Senior Stylist",
      "desc": "Certified Expert (Included)",
      "extra_fee": 0
    },
    {
      "id": "Art Director",
      "name": "Master Art Director",
      "desc": "+₹300 (Celebrity Stylist)",
      "extra_fee": 300
    }
  ],
  "available_dates": [
    {"key": "Today", "label": "Today", "date": "17 Nov, Tue"},
    {"key": "Tomorrow", "label": "Tomorrow", "date": "18 Nov, Wed"}
  ],
  "available_slots": [
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "04:30 PM - 05:30 PM",
    "06:00 PM - 07:00 PM"
  ],
  "booking_terms": "Pay at Salon • Free Cancellation Anytime Before Scheduled Slot"
}


API for User Book Beauty Parlour Appointment / Instant VIP Pass
url : (http://192.168.1.52:8000/api/beauty/book-appointment/)
method : POST
params :-
parlour_id: lakme_luxe
service_id: lakme_moroccan_spa
slot_date: 2026-11-20
slot_time: 02:00 PM - 03:00 PM
stylist_tier: Senior Stylist (options: Senior Stylist / Art Director)
customer_name: Ananya Verma
customer_phone: 9876543210
customer_email: ananya@example.com
response :-
{
  "status": "success",
  "message": "Appointment confirmed at Lakmé Salon Luxe! Pass #LUXE-4821",
  "appointment": {
    "pass_code": "LUXE-4821",
    "booking_id": "BK-A91B2C3D",
    "status": "CONFIRMED",
    "hub": "womens_salon_spa",
    "hub_name": "Women's Salon & Spa",
    "parlour": {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM"
    },
    "service": {
      "id": "lakme_moroccan_spa",
      "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
      "time": "60 mins",
      "category": "Hair Care",
      "price": 1899.0
    },
    "stylist_tier": "Senior Stylist",
    "stylist_label": "Senior Stylist",
    "slot_date": "2026-11-20",
    "slot_time": "02:00 PM - 03:00 PM",
    "customer_name": "Ananya Verma",
    "customer_phone": "9876543210",
    "payment_mode": "PAY_AT_SALON",
    "total_amount": 1899.0,
    "currency": "INR",
    "instructions": [
      "Present VIP Pass #LUXE-4821 at the reception of Lakmé Salon Luxe.",
      "Zero waiting time guaranteed for your reserved time slot.",
      "You can pay after treatment completion via UPI, Card, or Cash."
    ]
  }
}


API for Job Image Gallery List
url : (http://192.168.1.52:8000/api/user/jobs/<job_id>/images/)
method : GET
response :-
{
  "status": "success",
  "job_id": 12,
  "count": 2,
  "data": [
    {
      "id": 1,
      "image_url": "http://192.168.1.52:8000/media/jobs/gallery/site1.jpg",
      "created_at": "2026-10-16 11:30:00"
    }
  ]
}


API for User Display Beauty Experience (Cards: Women vs Men)
url : (http://192.168.1.52:8000/api/user/beauty/)
method : GET
response :-
{
  "status": "success",
  "title": "Beauty & Wellness",
  "subtitle": "Select Experience / Category",
  "experiences": [
    {
      "id": "womens_salon_spa",
      "gender": "women",
      "name": "Women's Salon & Spa",
      "tagline": "At-Home Beauty or Book Top Luxury Parlours",
      "rating": 4.91,
      "reviews_count": "4.2M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 349,
      "formatted_price": "₹349",
      "image": "http://192.168.1.52:8000/static/assets/beauty/women_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/womens_salon_spa.png",
      "hero_title": "Women's Salon, Spa & Parlours",
      "hero_desc": "Doorstep certified beauticians or guaranteed VIP slot at Bengaluru's top luxury salons.",
      "modes": [
        {
          "id": "home",
          "name": "1. Salon at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified beautician visits your home • 100% sealed mono-kits",
          "icon": "home",
          "accent_color": "#ec4899"
        },
        {
          "id": "parlour",
          "name": "2. Premium Parlour Services",
          "badge": "LUXURY SALON BRANDS",
          "description": "Book visit at Lakmé Luxe, Enrich, BBlunt, Toni & Guy in your area",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    },
    {
      "id": "mens_salon_massage",
      "gender": "men",
      "name": "Men's Salon & Massage",
      "tagline": "At-Home Grooming or Book Top Luxury Salons",
      "rating": 4.87,
      "reviews_count": "2.9M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 249,
      "formatted_price": "₹249",
      "image": "http://192.168.1.52:8000/static/assets/beauty/men_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/mens_salon_massage.png",
      "hero_title": "Men's Grooming, Massage & Barbershops",
      "hero_desc": "Certified male barbers at home or royal grooming at Truefitt & Hill, Bounce and top lounges.",
      "modes": [
        {
          "id": "home",
          "name": "1. Grooming & Massage at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified male stylist visits your home • Single-use sterilized tools & vacuum",
          "icon": "home",
          "accent_color": "#0284c7"
        },
        {
          "id": "parlour",
          "name": "2. Premium Barbershop & Lounge",
          "badge": "LUXURY BARBERSHOPS",
          "description": "Book visit at Truefitt & Hill, Bounce, Toni & Guy Men, The Man Company",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    }
  ]
}


API for User Display Beauty Services (At-Home Subcategories & Services)
url : (http://192.168.1.52:8000/api/user/beauty/services/)
method : GET
params :-
gender: women (options: women / men)
delivery_mode: home (options: home / parlour)
response :-
{
  "status": "success",
  "category_id": 37,
  "category_name": "Beauty",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "home",
  "mode_name": "Salon at Home",
  "subcategories": [
    {
      "id": "sub_48",
      "dbId": 48,
      "name": "Facials & Cleanup",
      "gender": "women",
      "items": [
        {
          "id": "qs_41",
          "dbId": 41,
          "title": "O3+ Diamond Glow Facial & De-Tan",
          "category": "Beauty",
          "subcategory": "Facials & Cleanup",
          "rating": "4.91",
          "reviews": "120+ reviews",
          "price": 899.0,
          "originalPrice": 1168,
          "time": "60 mins",
          "duration": "60 mins",
          "brand_name": "O3+ Professional",
          "is_mono_pack": true,
          "parlour_name": "",
          "gender": "women",
          "delivery_mode": "home",
          "badge": "100% Sealed Mono-Pack",
          "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg",
          "features": [
            "100% Sealed Single-Dose Mono-Pack",
            "Single-use disposable gown & cape",
            "Sterilized instruments sealed in pouch"
          ],
          "packages": [
            {
              "name": "Express Glow",
              "price": 899,
              "duration": "45 mins",
              "desc": "Cleansing, scrub and pack"
            },
            {
              "name": "Royal Bridal Glow",
              "price": 1499,
              "duration": "75 mins",
              "desc": "Full 7-step facial with gold serum"
            }
          ]
        }
      ]
    },
    {
      "id": "sub_49",
      "dbId": 49,
      "name": "Waxing & Hair Removal",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_50",
      "dbId": 50,
      "name": "Pedicure & Manicure",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_51",
      "dbId": 51,
      "name": "Hair Spa & Styling",
      "gender": "women",
      "items": []
    }
  ],
  "all_services": [
    {
      "id": "qs_41",
      "dbId": 41,
      "title": "O3+ Diamond Glow Facial & De-Tan",
      "category": "Beauty",
      "subcategory": "Facials & Cleanup",
      "rating": "4.91",
      "reviews": "120+ reviews",
      "price": 899.0,
      "duration": "60 mins",
      "brand_name": "O3+ Professional",
      "is_mono_pack": true,
      "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg"
    }
  ],
  "guarantee": "30-Day Money-Back & Free Re-work Guarantee",
  "damage_cover": "Up to ₹10,000 Free Accidental Damage Cover"
}


API for User Display Beauty Luxury Parlours Directory
url : (http://192.168.1.52:8000/api/user/beauty/parlours/)
method : GET
params :-
gender: women (options: women / men)
response :-
{
  "status": "success",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "parlour",
  "mode_name": "Premium Parlour Services",
  "guarantee": "Zero Waiting Time Guarantee • VIP Slot Reserved",
  "count": 3,
  "parlours": [
    {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
      "rating": "4.94 ★ (3,800+ reviews)",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM",
      "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Lakmé Fashion Week Certified Stylists",
        "Private VIP Bridal Lounge",
        "Complimentary Gourmet Brewed Coffee"
      ],
      "starting_price": 1599,
      "services_count": 4
    },
    {
      "id": "enrich_salon",
      "name": "Enrich Salon & Luxury Spa",
      "brandTag": "Kerastase Paris",
      "tagline": "Kerastase Hair Rituals, K-Glow Facials & BIAB Nails",
      "rating": "4.91 ★ (2,450+ reviews)",
      "location": "4th Block, Koramangala",
      "distance": "1.4 km away",
      "timings": "09:30 AM - 09:30 PM",
      "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Kerastase Certified Master Hair Diagnostics",
        "Dermat-Grade Hydrafacial Suites",
        "Premium Valet Parking"
      ],
      "starting_price": 1299,
      "services_count": 3
    }
  ]
}


API for User Display Beauty Luxury Parlour Details (Services, Slots & Stylists)
url : (http://192.168.1.52:8000/api/user/beauty/parlours/<parlour_id>/)
method : GET
params :-
parlour_id: lakme_luxe (path parameter e.g. lakme_luxe / enrich_salon / truefitt_hill / bounce_salon)
response :-
{
  "status": "success",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "parlour": {
    "id": "lakme_luxe",
    "name": "Lakmé Salon Luxe",
    "brandTag": "Runway Certified",
    "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
    "rating": "4.94 ★ (3,800+ reviews)",
    "location": "100ft Road, Indiranagar",
    "distance": "0.8 km away",
    "timings": "10:00 AM - 09:00 PM",
    "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
    "highlights": [
      "Lakmé Fashion Week Certified Stylists",
      "Private VIP Bridal Lounge",
      "Complimentary Gourmet Brewed Coffee"
    ],
    "starting_price": 1599,
    "services": [
      {
        "id": "lakme_moroccan_spa",
        "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
        "category": "Hair Care",
        "price": 1899,
        "originalPrice": 2499,
        "discount": "24% OFF",
        "time": "60 mins",
        "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
        "desc": "Deep argan oil treatment infused with infrared heat to restore silkiness and mirror shine."
      },
      {
        "id": "lakme_bridal_hd",
        "title": "Runway HD Airbrush Bridal Transformation",
        "category": "Bridal Studio",
        "price": 8999,
        "originalPrice": 12000,
        "discount": "25% OFF",
        "time": "3 Hours",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
        "desc": "Complete pre-bridal skin prep, Temptu HD airbrush base, 3D lash installation, and designer saree draping."
      }
    ]
  },
  "stylist_tiers": [
    {
      "id": "Senior Stylist",
      "name": "Senior Stylist",
      "desc": "Certified Expert (Included)",
      "extra_fee": 0
    },
    {
      "id": "Art Director",
      "name": "Master Art Director",
      "desc": "+₹300 (Celebrity Stylist)",
      "extra_fee": 300
    }
  ],
  "available_dates": [
    {"key": "Today", "label": "Today", "date": "17 Nov, Tue"},
    {"key": "Tomorrow", "label": "Tomorrow", "date": "18 Nov, Wed"}
  ],
  "available_slots": [
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "04:30 PM - 05:30 PM",
    "06:00 PM - 07:00 PM"
  ],
  "booking_terms": "Pay at Salon • Free Cancellation Anytime Before Scheduled Slot"
}


API for User Book Beauty Parlour Appointment / Instant VIP Pass
url : (http://192.168.1.52:8000/api/beauty/book-appointment/)
method : POST
params :-
parlour_id: lakme_luxe
service_id: lakme_moroccan_spa
slot_date: 2026-11-20
slot_time: 02:00 PM - 03:00 PM
stylist_tier: Senior Stylist (options: Senior Stylist / Art Director)
customer_name: Ananya Verma
customer_phone: 9876543210
customer_email: ananya@example.com
response :-
{
  "status": "success",
  "message": "Appointment confirmed at Lakmé Salon Luxe! Pass #LUXE-4821",
  "appointment": {
    "pass_code": "LUXE-4821",
    "booking_id": "BK-A91B2C3D",
    "status": "CONFIRMED",
    "hub": "womens_salon_spa",
    "hub_name": "Women's Salon & Spa",
    "parlour": {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM"
    },
    "service": {
      "id": "lakme_moroccan_spa",
      "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
      "time": "60 mins",
      "category": "Hair Care",
      "price": 1899.0
    },
    "stylist_tier": "Senior Stylist",
    "stylist_label": "Senior Stylist",
    "slot_date": "2026-11-20",
    "slot_time": "02:00 PM - 03:00 PM",
    "customer_name": "Ananya Verma",
    "customer_phone": "9876543210",
    "payment_mode": "PAY_AT_SALON",
    "total_amount": 1899.0,
    "currency": "INR",
    "instructions": [
      "Present VIP Pass #LUXE-4821 at the reception of Lakmé Salon Luxe.",
      "Zero waiting time guaranteed for your reserved time slot.",
      "You can pay after treatment completion via UPI, Card, or Cash."
    ]
  }
}


API for Job Image Gallery Delete
url : (http://192.168.1.52:8000/api/user/jobs/<job_id>/images/<image_id>/delete/)
method : POST or DELETE
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "message": "Gallery image deleted successfully"
}


API for View Job Completion Proof
url : (http://192.168.1.52:8000/api/user/jobs/<job_id>/proof/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "data": {
    "has_proof": true,
    "photo_1_url": "http://192.168.1.52:8000/media/jobs/proof/finished_1.jpg",
    "photo_2_url": "http://192.168.1.52:8000/media/jobs/proof/finished_2.jpg",
    "work_summary": "All AC compressor filters cleaned, gas refilled to optimal psi.",
    "vendor_name": "Cooling Pro Experts",
    "completed_at": "2026-10-16 10:15:00"
  }
}


API for Create Dispute / Complaint
url : (http://192.168.1.52:8000/api/disputes/create/)
method : POST (multipart/form-data)
headers :-
Authorization: Bearer <token>
params :-
subject: AC cooling stopped working after 2 hours
description: Technician claimed work complete but unit stopped functioning immediately.
category: quality (payment/quality/noshow/behavior/delay/platform/other)
priority: high (low/medium/high/urgent)
job_id: 12 (optional)
evidence_image: [file] (optional)
response :-
{
  "status": "success",
  "message": "Dispute ticket created successfully",
  "data": {
    "ticket_id": "CMP-2026-4819",
    "status": "open"
  }
}


API for List My Disputes
url : (http://192.168.1.52:8000/api/disputes/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "ticket_id": "CMP-2026-4819",
      "subject": "AC cooling stopped working after 2 hours",
      "category": "quality",
      "status": "open",
      "priority": "high",
      "related_item": "JOB-0012 · Emergency Server Room AC Repair",
      "created_at": "2026-10-16 11:45:00"
    }
  ]
}


API for User Display Beauty Experience (Cards: Women vs Men)
url : (http://192.168.1.52:8000/api/user/beauty/)
method : GET
response :-
{
  "status": "success",
  "title": "Beauty & Wellness",
  "subtitle": "Select Experience / Category",
  "experiences": [
    {
      "id": "womens_salon_spa",
      "gender": "women",
      "name": "Women's Salon & Spa",
      "tagline": "At-Home Beauty or Book Top Luxury Parlours",
      "rating": 4.91,
      "reviews_count": "4.2M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 349,
      "formatted_price": "₹349",
      "image": "http://192.168.1.52:8000/static/assets/beauty/women_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/womens_salon_spa.png",
      "hero_title": "Women's Salon, Spa & Parlours",
      "hero_desc": "Doorstep certified beauticians or guaranteed VIP slot at Bengaluru's top luxury salons.",
      "modes": [
        {
          "id": "home",
          "name": "1. Salon at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified beautician visits your home • 100% sealed mono-kits",
          "icon": "home",
          "accent_color": "#ec4899"
        },
        {
          "id": "parlour",
          "name": "2. Premium Parlour Services",
          "badge": "LUXURY SALON BRANDS",
          "description": "Book visit at Lakmé Luxe, Enrich, BBlunt, Toni & Guy in your area",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    },
    {
      "id": "mens_salon_massage",
      "gender": "men",
      "name": "Men's Salon & Massage",
      "tagline": "At-Home Grooming or Book Top Luxury Salons",
      "rating": 4.87,
      "reviews_count": "2.9M Reviews",
      "badge": "15 Min Pro",
      "starting_price": 249,
      "formatted_price": "₹249",
      "image": "http://192.168.1.52:8000/static/assets/beauty/men_photo.png",
      "icon": "http://192.168.1.52:8000/static/assets/icons/mens_salon_massage.png",
      "hero_title": "Men's Grooming, Massage & Barbershops",
      "hero_desc": "Certified male barbers at home or royal grooming at Truefitt & Hill, Bounce and top lounges.",
      "modes": [
        {
          "id": "home",
          "name": "1. Grooming & Massage at Home",
          "badge": "ALL SERVICES AVAILABLE",
          "description": "Certified male stylist visits your home • Single-use sterilized tools & vacuum",
          "icon": "home",
          "accent_color": "#0284c7"
        },
        {
          "id": "parlour",
          "name": "2. Premium Barbershop & Lounge",
          "badge": "LUXURY BARBERSHOPS",
          "description": "Book visit at Truefitt & Hill, Bounce, Toni & Guy Men, The Man Company",
          "icon": "crown",
          "accent_color": "#d97706"
        }
      ]
    }
  ]
}


API for User Display Beauty Services (At-Home Subcategories & Services)
url : (http://192.168.1.52:8000/api/user/beauty/services/)
method : GET
params :-
gender: women (options: women / men)
delivery_mode: home (options: home / parlour)
response :-
{
  "status": "success",
  "category_id": 37,
  "category_name": "Beauty",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "home",
  "mode_name": "Salon at Home",
  "subcategories": [
    {
      "id": "sub_48",
      "dbId": 48,
      "name": "Facials & Cleanup",
      "gender": "women",
      "items": [
        {
          "id": "qs_41",
          "dbId": 41,
          "title": "O3+ Diamond Glow Facial & De-Tan",
          "category": "Beauty",
          "subcategory": "Facials & Cleanup",
          "rating": "4.91",
          "reviews": "120+ reviews",
          "price": 899.0,
          "originalPrice": 1168,
          "time": "60 mins",
          "duration": "60 mins",
          "brand_name": "O3+ Professional",
          "is_mono_pack": true,
          "parlour_name": "",
          "gender": "women",
          "delivery_mode": "home",
          "badge": "100% Sealed Mono-Pack",
          "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg",
          "features": [
            "100% Sealed Single-Dose Mono-Pack",
            "Single-use disposable gown & cape",
            "Sterilized instruments sealed in pouch"
          ],
          "packages": [
            {
              "name": "Express Glow",
              "price": 899,
              "duration": "45 mins",
              "desc": "Cleansing, scrub and pack"
            },
            {
              "name": "Royal Bridal Glow",
              "price": 1499,
              "duration": "75 mins",
              "desc": "Full 7-step facial with gold serum"
            }
          ]
        }
      ]
    },
    {
      "id": "sub_49",
      "dbId": 49,
      "name": "Waxing & Hair Removal",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_50",
      "dbId": 50,
      "name": "Pedicure & Manicure",
      "gender": "women",
      "items": []
    },
    {
      "id": "sub_51",
      "dbId": 51,
      "name": "Hair Spa & Styling",
      "gender": "women",
      "items": []
    }
  ],
  "all_services": [
    {
      "id": "qs_41",
      "dbId": 41,
      "title": "O3+ Diamond Glow Facial & De-Tan",
      "category": "Beauty",
      "subcategory": "Facials & Cleanup",
      "rating": "4.91",
      "reviews": "120+ reviews",
      "price": 899.0,
      "duration": "60 mins",
      "brand_name": "O3+ Professional",
      "is_mono_pack": true,
      "image": "http://192.168.1.52:8000/media/quick_services/facial.jpg"
    }
  ],
  "guarantee": "30-Day Money-Back & Free Re-work Guarantee",
  "damage_cover": "Up to ₹10,000 Free Accidental Damage Cover"
}


API for User Display Beauty Luxury Parlours Directory
url : (http://192.168.1.52:8000/api/user/beauty/parlours/)
method : GET
params :-
gender: women (options: women / men)
response :-
{
  "status": "success",
  "gender": "women",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "mode": "parlour",
  "mode_name": "Premium Parlour Services",
  "guarantee": "Zero Waiting Time Guarantee • VIP Slot Reserved",
  "count": 3,
  "parlours": [
    {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
      "rating": "4.94 ★ (3,800+ reviews)",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM",
      "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Lakmé Fashion Week Certified Stylists",
        "Private VIP Bridal Lounge",
        "Complimentary Gourmet Brewed Coffee"
      ],
      "starting_price": 1599,
      "services_count": 4
    },
    {
      "id": "enrich_salon",
      "name": "Enrich Salon & Luxury Spa",
      "brandTag": "Kerastase Paris",
      "tagline": "Kerastase Hair Rituals, K-Glow Facials & BIAB Nails",
      "rating": "4.91 ★ (2,450+ reviews)",
      "location": "4th Block, Koramangala",
      "distance": "1.4 km away",
      "timings": "09:30 AM - 09:30 PM",
      "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
      "highlights": [
        "Kerastase Certified Master Hair Diagnostics",
        "Dermat-Grade Hydrafacial Suites",
        "Premium Valet Parking"
      ],
      "starting_price": 1299,
      "services_count": 3
    }
  ]
}


API for User Display Beauty Luxury Parlour Details (Services, Slots & Stylists)
url : (http://192.168.1.52:8000/api/user/beauty/parlours/<parlour_id>/)
method : GET
params :-
parlour_id: lakme_luxe (path parameter e.g. lakme_luxe / enrich_salon / truefitt_hill / bounce_salon)
response :-
{
  "status": "success",
  "hub": "womens_salon_spa",
  "hub_name": "Women's Salon & Spa",
  "parlour": {
    "id": "lakme_luxe",
    "name": "Lakmé Salon Luxe",
    "brandTag": "Runway Certified",
    "tagline": "Runway Bridal Expertise & Moroccan Oil Hair Therapy",
    "rating": "4.94 ★ (3,800+ reviews)",
    "location": "100ft Road, Indiranagar",
    "distance": "0.8 km away",
    "timings": "10:00 AM - 09:00 PM",
    "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=700&q=80",
    "highlights": [
      "Lakmé Fashion Week Certified Stylists",
      "Private VIP Bridal Lounge",
      "Complimentary Gourmet Brewed Coffee"
    ],
    "starting_price": 1599,
    "services": [
      {
        "id": "lakme_moroccan_spa",
        "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
        "category": "Hair Care",
        "price": 1899,
        "originalPrice": 2499,
        "discount": "24% OFF",
        "time": "60 mins",
        "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
        "desc": "Deep argan oil treatment infused with infrared heat to restore silkiness and mirror shine."
      },
      {
        "id": "lakme_bridal_hd",
        "title": "Runway HD Airbrush Bridal Transformation",
        "category": "Bridal Studio",
        "price": 8999,
        "originalPrice": 12000,
        "discount": "25% OFF",
        "time": "3 Hours",
        "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
        "desc": "Complete pre-bridal skin prep, Temptu HD airbrush base, 3D lash installation, and designer saree draping."
      }
    ]
  },
  "stylist_tiers": [
    {
      "id": "Senior Stylist",
      "name": "Senior Stylist",
      "desc": "Certified Expert (Included)",
      "extra_fee": 0
    },
    {
      "id": "Art Director",
      "name": "Master Art Director",
      "desc": "+₹300 (Celebrity Stylist)",
      "extra_fee": 300
    }
  ],
  "available_dates": [
    {"key": "Today", "label": "Today", "date": "17 Nov, Tue"},
    {"key": "Tomorrow", "label": "Tomorrow", "date": "18 Nov, Wed"}
  ],
  "available_slots": [
    "10:00 AM - 11:00 AM",
    "11:30 AM - 12:30 PM",
    "02:00 PM - 03:00 PM",
    "04:30 PM - 05:30 PM",
    "06:00 PM - 07:00 PM"
  ],
  "booking_terms": "Pay at Salon • Free Cancellation Anytime Before Scheduled Slot"
}


API for User Book Beauty Parlour Appointment / Instant VIP Pass
url : (http://192.168.1.52:8000/api/beauty/book-appointment/)
method : POST
params :-
parlour_id: lakme_luxe
service_id: lakme_moroccan_spa
slot_date: 2026-11-20
slot_time: 02:00 PM - 03:00 PM
stylist_tier: Senior Stylist (options: Senior Stylist / Art Director)
customer_name: Ananya Verma
customer_phone: 9876543210
customer_email: ananya@example.com
response :-
{
  "status": "success",
  "message": "Appointment confirmed at Lakmé Salon Luxe! Pass #LUXE-4821",
  "appointment": {
    "pass_code": "LUXE-4821",
    "booking_id": "BK-A91B2C3D",
    "status": "CONFIRMED",
    "hub": "womens_salon_spa",
    "hub_name": "Women's Salon & Spa",
    "parlour": {
      "id": "lakme_luxe",
      "name": "Lakmé Salon Luxe",
      "brandTag": "Runway Certified",
      "location": "100ft Road, Indiranagar",
      "distance": "0.8 km away",
      "timings": "10:00 AM - 09:00 PM"
    },
    "service": {
      "id": "lakme_moroccan_spa",
      "title": "Moroccan Oil Hydration Hair Ritual & Blowout",
      "time": "60 mins",
      "category": "Hair Care",
      "price": 1899.0
    },
    "stylist_tier": "Senior Stylist",
    "stylist_label": "Senior Stylist",
    "slot_date": "2026-11-20",
    "slot_time": "02:00 PM - 03:00 PM",
    "customer_name": "Ananya Verma",
    "customer_phone": "9876543210",
    "payment_mode": "PAY_AT_SALON",
    "total_amount": 1899.0,
    "currency": "INR",
    "instructions": [
      "Present VIP Pass #LUXE-4821 at the reception of Lakmé Salon Luxe.",
      "Zero waiting time guaranteed for your reserved time slot.",
      "You can pay after treatment completion via UPI, Card, or Cash."
    ]
  }
}


API for Dispute Detail & Messages
url : (http://192.168.1.52:8000/api/disputes/<ticket_id>/)
method : GET
headers :-
Authorization: Bearer <token>
response :-
{
  "status": "success",
  "data": {
    "ticket_id": "CMP-2026-4819",
    "subject": "AC cooling stopped working after 2 hours",
    "description": "Technician claimed work complete but unit stopped functioning immediately.",
    "category": "quality",
    "status": "open",
    "priority": "high",
    "raised_by": { "id": 18, "name": "Ananya Sharma", "role": "USER" },
    "against_user": { "id": 5, "name": "Cooling Pro Experts", "role": "VENDOR" },
    "related_job": { "id": 12, "title": "Emergency Server Room AC Repair", "budget": 3500.0 },
    "related_quick_service": null,
    "evidence_image_url": "http://192.168.1.52:8000/media/disputes/evidence/err.jpg",
    "resolution_notes": "",
    "created_at": "2026-10-16 11:45:00",
    "resolved_at": null,
    "messages": [
      {
        "id": 1,
        "sender_id": 5,
        "sender_name": "Cooling Pro Experts",
        "sender_role": "VENDOR",
        "is_me": false,
        "message": "We are sending our senior supervisor right now to re-inspect.",
        "attachment_url": "",
        "created_at": "2026-10-16 11:50:00"
      }
    ]
  }
}


API for Reply / Message in Dispute
url : (http://192.168.1.52:8000/api/disputes/<ticket_id>/message/)
method : POST (multipart/form-data)
headers :-
Authorization: Bearer <token>
params :-
message: Thank you, please confirm when technician arrives.
attachment: [file] (optional)
response :-
{
  "status": "success",
  "message": "Message added to dispute successfully",
  "data": {
    "message_id": 2,
    "created_at": "2026-10-16 11:55:00"
  }
}


