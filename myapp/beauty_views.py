import json
import uuid
import random
from datetime import datetime, date, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from myapp.models import Category, SubCategory, CustomUser, ServiceBooking

# ==============================================================================
# BEAUTY & WELLNESS MASTER CATALOG (AT-HOME SERVICES + LUXURY PARLOUR DIRECTORY)
# Designed to power Mobile App and Web with 100% Flow Parity
# ==============================================================================

BEAUTY_EXPERIENCES = [
    {
        "id": "womens_salon_spa",
        "name": "Women's Salon & Spa",
        "tagline": "At-Home Beauty or Book Top Luxury Parlours",
        "rating": 4.91,
        "reviews_count": "4.2M Reviews",
        "badge": "15 Min Pro",
        "starting_price": 349,
        "formatted_price": "₹349",
        "image": "/static/assets/beauty/women_photo.png",
        "icon": "/static/assets/icons/womens_salon_spa.png",
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
        "name": "Men's Salon & Massage",
        "tagline": "At-Home Grooming or Book Top Luxury Salons",
        "rating": 4.87,
        "reviews_count": "2.9M Reviews",
        "badge": "15 Min Pro",
        "starting_price": 249,
        "formatted_price": "₹249",
        "image": "/static/assets/beauty/men_photo.png",
        "icon": "/static/assets/icons/mens_salon_massage.png",
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

# ------------------------------------------------------------------------------
# AT-HOME SERVICES CATALOG (WOMEN & MEN)
# ------------------------------------------------------------------------------
AT_HOME_CATALOG = {
    "womens_salon_spa": [
        {
            "id": "salon_facial",
            "name": "Facials & Cleanup",
            "items": [
                {
                    "id": "facial_o3",
                    "title": "O3+ Bridal Glow Luxury Facial",
                    "rating": "4.93",
                    "reviews": "720K+",
                    "price": 1399,
                    "originalPrice": 1999,
                    "discount": "30% OFF",
                    "time": "75 mins",
                    "badge": "Celebrity Glow",
                    "image": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Sealed single-dose mono pack for absolute hygiene",
                        "Includes blackhead extraction & ultrasonic scrubber",
                        "Revitalizing peel-off rubber mask",
                        "Relaxing neck and shoulder acupressure massage"
                    ]
                },
                {
                    "id": "facial_lotus",
                    "title": "Lotus Herbal Skin Radiance & De-Tan",
                    "rating": "4.86",
                    "reviews": "340K+",
                    "price": 899,
                    "originalPrice": 1299,
                    "discount": "31% OFF",
                    "time": "55 mins",
                    "badge": "Herbal Care",
                    "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Natural fruit enzyme peel to lift sun tanning",
                        "Gentle herbal walnut scrub exfoliation",
                        "Cooling aloe vera gel hydrator"
                    ]
                }
            ]
        },
        {
            "id": "salon_waxing",
            "name": "Waxing & Hair Removal",
            "items": [
                {
                    "id": "wax_rica_bikini",
                    "title": "Rica Brazilian Bikini & Underarms Wax",
                    "rating": "4.91",
                    "reviews": "490K+",
                    "price": 1099,
                    "originalPrice": 1599,
                    "discount": "31% OFF",
                    "time": "45 mins",
                    "badge": "Pain-Less Rica",
                    "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "100% colophony-free Italian liposoluble Rica wax",
                        "Single-use disposable wooden spatulas & bed roll",
                        "Pre-wax gel & soothing post-wax chamomile lotion"
                    ]
                },
                {
                    "id": "wax_honey_full",
                    "title": "Honey Full Arms, Full Legs & Underarms",
                    "rating": "4.84",
                    "reviews": "820K+",
                    "price": 649,
                    "originalPrice": 899,
                    "discount": "28% OFF",
                    "time": "50 mins",
                    "badge": "Value Pack",
                    "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Warm honey wax suitable for all skin types",
                        "Post-wax soothing aloe rub",
                        "Includes sanitization of treatment area"
                    ]
                }
            ]
        },
        {
            "id": "salon_pedi_mani",
            "name": "Pedicure & Manicure",
            "items": [
                {
                    "id": "pedi_rose_crystal",
                    "title": "Rose Quartz Crystal Mani-Pedi Spa Ritual",
                    "rating": "4.94",
                    "reviews": "390K+",
                    "price": 1199,
                    "originalPrice": 1699,
                    "discount": "29% OFF",
                    "time": "70 mins",
                    "badge": "Luxury Pampering",
                    "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Effervescent rose mineral foot soak & dead-skin heel buffing",
                        "Cuticle nourishment, nail shaping and buffer shine",
                        "Ultra-rich shea butter & almond massage cream",
                        "Breathable quick-dry gel polish topcoat"
                    ]
                }
            ]
        },
        {
            "id": "salon_hair_care",
            "name": "Hair Spa & Styling",
            "items": [
                {
                    "id": "hair_spa_loreal",
                    "title": "L'Oreal Professionnel Serie Expert Hair Spa",
                    "rating": "4.89",
                    "reviews": "280K+",
                    "price": 999,
                    "originalPrice": 1499,
                    "discount": "33% OFF",
                    "time": "60 mins",
                    "badge": "Deep Nourish",
                    "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Deep moisture infusion for frizz & split end repair",
                        "20-minute relaxing neck, shoulder & scalp massage",
                        "Hot towel steam treatment for cuticles"
                    ]
                }
            ]
        }
    ],
    "mens_salon_massage": [
        {
            "id": "men_haircut",
            "name": "Haircut & Beard Grooming",
            "items": [
                {
                    "id": "men_pro_haircut",
                    "title": "Master Barber Fade Haircut & Beard Shaping",
                    "rating": "4.89",
                    "reviews": "850K+",
                    "price": 349,
                    "originalPrice": 499,
                    "discount": "30% OFF",
                    "time": "40 mins",
                    "badge": "Bestseller",
                    "image": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Custom hair styling consultation & precision shear cut",
                        "Electric trimmer zero fade + straight razor edging",
                        "Post-cut neck cleanup & mini head massage",
                        "Hair vacuum cleanup — zero hair mess at home"
                    ]
                },
                {
                    "id": "men_scalp_wash",
                    "title": "Anti-Dandruff Scalp Clarifying Wash & Head Massage",
                    "rating": "4.84",
                    "reviews": "310K+",
                    "price": 449,
                    "originalPrice": 599,
                    "discount": "25% OFF",
                    "time": "35 mins",
                    "badge": "Scalp Therapy",
                    "image": "https://images.unsplash.com/photo-1517832606589-715746200e6f?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Menthol & tea tree oil cooling scalp stimulation",
                        "15-minute invigorating acupressure head massage",
                        "Relieves migraine strain & clears dead scalp skin"
                    ]
                }
            ]
        },
        {
            "id": "men_detan_facial",
            "name": "D-Tan & Face Rejuvenation",
            "items": [
                {
                    "id": "men_charcoal_detan",
                    "title": "O3+ Men Charcoal Detox & Sun Tan Removal",
                    "rating": "4.88",
                    "reviews": "420K+",
                    "price": 799,
                    "originalPrice": 1199,
                    "discount": "33% OFF",
                    "time": "45 mins",
                    "badge": "Pollution Shield",
                    "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Activated bamboo charcoal pore decongestion",
                        "Targeted de-tan pack for forehead, nose and neck",
                        "Hydrating vitamin-C soothing moisturizer"
                    ]
                }
            ]
        },
        {
            "id": "men_massage_spa",
            "name": "Stress Relief & Deep Tissue Massage",
            "items": [
                {
                    "id": "men_deep_tissue",
                    "title": "60-Min Deep Tissue Muscle Relaxant Massage",
                    "rating": "4.93",
                    "reviews": "510K+",
                    "price": 1299,
                    "originalPrice": 1899,
                    "discount": "32% OFF",
                    "time": "60 mins",
                    "badge": "Full Body Bliss",
                    "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=600&q=80",
                    "features": [
                        "Certified physiotherapist-trained male massage therapist",
                        "Warm sesame or aromatic almond oil blend",
                        "Targets shoulder stiffness, lower back tension & fatigue",
                        "Disposable massage table setup"
                    ]
                }
            ]
        }
    ]
}

# ------------------------------------------------------------------------------
# CURATED DIRECTORY OF TOP LUXURY PARLOURS / BARBERSHOPS (WOMEN & MEN)
# ------------------------------------------------------------------------------
LUXURY_PARLOURS_CATALOG = {
    "womens_salon_spa": [
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
                },
                {
                    "id": "lakme_collagen_facial",
                    "title": "Lakmé Youth Infinity Collagen Boost Facial",
                    "category": "Skin Bar",
                    "price": 2499,
                    "originalPrice": 3200,
                    "discount": "22% OFF",
                    "time": "75 mins",
                    "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=500&q=80",
                    "desc": "Infused with pure peptides and micro-current lifting probes for an instant youthful sculpting effect."
                },
                {
                    "id": "lakme_gel_nails",
                    "title": "French Ombre BIAB Gel Extensions & Nail Art",
                    "category": "Nail Lounge",
                    "price": 1599,
                    "originalPrice": 2100,
                    "discount": "24% OFF",
                    "time": "75 mins",
                    "image": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?auto=format&fit=crop&w=500&q=80",
                    "desc": "Builder In A Bottle (BIAB) nail hardening overlay with customized crystal rhinestones and gel gloss."
                }
            ]
        },
        {
            "id": "enrich_salon",
            "name": "Enrich Salon & Luxury Spa",
            "brandTag": "Kerastase Paris",
            "tagline": "Kerastase Scalp Diagnostics & Dermalogica Skin Bar",
            "rating": "4.91 ★ (2,400+ reviews)",
            "location": "4th Block, Koramangala",
            "distance": "1.2 km away",
            "timings": "09:30 AM - 09:30 PM",
            "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=700&q=80",
            "highlights": [
                "Kerastase Micro-Camera Scalp Diagnostic",
                "Zero Ammonia L'Oreal INOA Color Bar",
                "Aroma Steam Jacuzzi Foot Reflexology"
            ],
            "starting_price": 2299,
            "services": [
                {
                    "id": "enrich_fusio_dose",
                    "title": "Kerastase Fusio-Dose Instant Hair Transformation",
                    "category": "Hair Care",
                    "price": 2299,
                    "originalPrice": 2999,
                    "discount": "23% OFF",
                    "time": "45 mins",
                    "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=500&q=80",
                    "desc": "Custom blend of Kerastase concentre and booster tailored to your scalp type by certified trichologist."
                },
                {
                    "id": "enrich_proskin_60",
                    "title": "Dermalogica ProSkin 60 Customized Skin Treatment",
                    "category": "Skin Bar",
                    "price": 2899,
                    "originalPrice": 3800,
                    "discount": "24% OFF",
                    "time": "60 mins",
                    "image": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=500&q=80",
                    "desc": "Deep sonic pore cleansing, acid-free resurfacing peel, and calming colloidal masque."
                },
                {
                    "id": "enrich_balayage",
                    "title": "Sun-kissed Balayage / Global Color by Art Director",
                    "category": "Hair Care",
                    "price": 4499,
                    "originalPrice": 5999,
                    "discount": "25% OFF",
                    "time": "2.5 Hours",
                    "image": "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?auto=format&fit=crop&w=500&q=80",
                    "desc": "Freehand dimensional French balayage with Olaplex bond multiplier protection included."
                }
            ]
        },
        {
            "id": "bblunt_studio",
            "name": "BBlunt Premium Studio",
            "brandTag": "Celebrity Favorite",
            "tagline": "Bollywood Celebrity Haircuts, Olaplex & Balayage Bar",
            "rating": "4.89 ★ (1,900+ reviews)",
            "location": "Lavelle Road, Central Bengaluru",
            "distance": "2.1 km away",
            "timings": "10:00 AM - 08:30 PM",
            "image": "https://images.unsplash.com/photo-1562322140-8baeececf3df?auto=format&fit=crop&w=700&q=80",
            "highlights": [
                "Celebrity Master Stylists on Floor",
                "Olaplex Molecular Bond Multiplier Lab",
                "Complimentary Face Shape & Hair Consultation"
            ],
            "starting_price": 1499,
            "services": [
                {
                    "id": "bblunt_signature_cut",
                    "title": "BBlunt Signature Precision Restyle by Art Director",
                    "category": "Hair Care",
                    "price": 1499,
                    "originalPrice": 1999,
                    "discount": "25% OFF",
                    "time": "45 mins",
                    "image": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=500&q=80",
                    "desc": "Bespoke cut customized to your bone structure, followed by blowout and texturizing."
                },
                {
                    "id": "bblunt_olaplex_repair",
                    "title": "Olaplex No. 1 & 2 Molecular Damage Reversal",
                    "category": "Hair Care",
                    "price": 2999,
                    "originalPrice": 3999,
                    "discount": "25% OFF",
                    "time": "60 mins",
                    "image": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=500&q=80",
                    "desc": "Rebuilds broken disulfide bonds in chemically treated or bleached hair."
                }
            ]
        }
    ],
    "mens_salon_massage": [
        {
            "id": "truefitt_hill",
            "name": "Truefitt & Hill Luxury Barbershop",
            "brandTag": "Royal Warrant (London 1805)",
            "tagline": "The World's Oldest Luxury Barbershop • Indulgent Grooming",
            "rating": "4.97 ★ (2,400+ reviews)",
            "location": "Lavelle Road, Central Bengaluru",
            "distance": "1.1 km away",
            "timings": "08:30 AM - 09:00 PM",
            "image": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=700&q=80",
            "highlights": [
                "Royal Shave with Hot Towels & Badger Brush",
                "Private Gentleman's Grooming Suite",
                "Complimentary Espresso & Single Malt Bar"
            ],
            "starting_price": 1499,
            "services": [
                {
                    "id": "th_royal_shave",
                    "title": "The Royal Shave & Pre-Shave Essential Oil Ritual",
                    "category": "Royal Shave",
                    "price": 2499,
                    "originalPrice": 3200,
                    "discount": "22% OFF",
                    "time": "45 mins",
                    "image": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=500&q=80",
                    "desc": "Traditional hot towel wrap, badger hair brush lathering, straight razor precision shave, and aftershave balm."
                },
                {
                    "id": "th_royal_cut",
                    "title": "Signature Royal Haircut & Scalp Massage by Master Barber",
                    "category": "Hair Styling",
                    "price": 2199,
                    "originalPrice": 2800,
                    "discount": "21% OFF",
                    "time": "50 mins",
                    "image": "https://images.unsplash.com/photo-1517832606589-715746200e6f?auto=format&fit=crop&w=500&q=80",
                    "desc": "Consultation, precision shear cut tailored to face shape, revitalizing scalp shampoo, and friction lotion massage."
                },
                {
                    "id": "th_exec_manipedi",
                    "title": "Executive Hand & Foot Grooming Lounge",
                    "category": "Hands & Feet",
                    "price": 1899,
                    "originalPrice": 2400,
                    "discount": "21% OFF",
                    "time": "60 mins",
                    "image": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=500&q=80",
                    "desc": "Nail detailing, cuticle overhaul, dead skin exfoliation, and deep pressure acupressure hand/foot massage."
                },
                {
                    "id": "th_scalp_detox",
                    "title": "Rosemary & Mint Invigorating Scalp Therapy",
                    "category": "Scalp Care",
                    "price": 1499,
                    "originalPrice": 1999,
                    "discount": "25% OFF",
                    "time": "40 mins",
                    "image": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?auto=format&fit=crop&w=500&q=80",
                    "desc": "Essential oil stimulation to promote hair root density, ease migraine fatigue, and detoxify follicles."
                }
            ]
        },
        {
            "id": "bounce_men",
            "name": "Bounce Style Lounge for Men",
            "brandTag": "Celebrity Barbers",
            "tagline": "Laser Fade Artistry, Beard Sculpting & Kerastase Homme",
            "rating": "4.92 ★ (1,850+ reviews)",
            "location": "5th Block, Koramangala",
            "distance": "0.9 km away",
            "timings": "09:00 AM - 09:30 PM",
            "image": "https://images.unsplash.com/photo-1517832606589-715746200e6f?auto=format&fit=crop&w=700&q=80",
            "highlights": [
                "Laser-Aligned Razor Edging & Fade Bar",
                "Kerastase Homme Diagnostic Micro-Camera",
                "Complimentary Cold Brew Coffee"
            ],
            "starting_price": 999,
            "services": [
                {
                    "id": "bounce_fade_beard",
                    "title": "Precision Skin Fade + Razor Sharp Beard Architecture",
                    "category": "Hair & Beard",
                    "price": 999,
                    "originalPrice": 1499,
                    "discount": "33% OFF",
                    "time": "45 mins",
                    "image": "https://images.unsplash.com/photo-1621605815971-fbc98d665033?auto=format&fit=crop&w=500&q=80",
                    "desc": "Seamless taper fade with straight razor lineup, hot foam edging, and beard conditioning oil."
                },
                {
                    "id": "bounce_kerastase_homme",
                    "title": "Kerastase Homme Anti-Hair Fall Scalp Booster",
                    "category": "Scalp Care",
                    "price": 1799,
                    "originalPrice": 2400,
                    "discount": "25% OFF",
                    "time": "45 mins",
                    "image": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=500&q=80",
                    "desc": "Micro-infusion of Aminexil and stemoxydine to fortify hair anchors and remove sebum residue."
                }
            ]
        }
    ]
}

# In-memory storage for active demo appointment passes (fallback when no db user)
ACTIVE_PARLOUR_APPOINTMENTS = []

# ==============================================================================
# REST API ENDPOINTS FOR MOBILE APP & WEB INTEGRATION
# ==============================================================================

@csrf_exempt
def beauty_experiences_api(request):
    """
    GET /api/beauty/experiences/ or /api/beauty/hubs/
    Screen 1: Returns the two gender categories (Women's Salon & Spa, Men's Salon & Massage)
    Each with starting price, rating, badge, banner image, and available dual modes.
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    base_url = request.build_absolute_uri('/')[:-1]
    experiences_with_abs_urls = []
    for exp in BEAUTY_EXPERIENCES:
        e = dict(exp)
        if e['image'].startswith('/'):
            e['image'] = f"{base_url}{e['image']}"
        if e['icon'].startswith('/'):
            e['icon'] = f"{base_url}{e['icon']}"
        experiences_with_abs_urls.append(e)

    return JsonResponse({
        'status': 'success',
        'title': 'Beauty & Wellness',
        'subtitle': 'Select Experience / Category',
        'experiences': experiences_with_abs_urls
    }, status=200)


@csrf_exempt
def beauty_services_api(request):
    """
    GET /api/beauty/services/
    Query parameters:
      - hub: 'womens_salon_spa' | 'mens_salon_massage' (default: 'womens_salon_spa')
      - mode: 'home' | 'parlour' (default: 'home')
    Screen 3: Returns at-home subcategories, services list, features, and pricing.
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    hub = request.GET.get('hub', 'womens_salon_spa')
    mode = request.GET.get('mode', 'home')

    if hub not in AT_HOME_CATALOG:
        hub = 'womens_salon_spa'

    if mode == 'parlour':
        # Delegate to parlour directory
        return beauty_parlours_api(request)

    subcategories = AT_HOME_CATALOG.get(hub, [])
    experience = next((e for e in BEAUTY_EXPERIENCES if e['id'] == hub), BEAUTY_EXPERIENCES[0])

    return JsonResponse({
        'status': 'success',
        'hub': hub,
        'hub_name': experience['name'],
        'mode': 'home',
        'mode_name': 'Salon at Home' if hub == 'womens_salon_spa' else 'Grooming & Massage at Home',
        'subcategories': subcategories,
        'guarantee': '30-Day Money-Back & Free Re-work Guarantee',
        'damage_cover': 'Up to ₹10,000 Free Accidental Damage Cover'
    }, status=200)


@csrf_exempt
def beauty_parlours_api(request):
    """
    GET /api/beauty/parlours/
    Query parameters:
      - hub: 'womens_salon_spa' | 'mens_salon_massage' (default: 'womens_salon_spa')
    Screen 4 & 5: Returns curated luxury verified parlours/barbershops list with badges, distance, ratings.
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    hub = request.GET.get('hub', 'womens_salon_spa')
    if hub not in LUXURY_PARLOURS_CATALOG:
        hub = 'womens_salon_spa'

    parlours = LUXURY_PARLOURS_CATALOG.get(hub, [])
    experience = next((e for e in BEAUTY_EXPERIENCES if e['id'] == hub), BEAUTY_EXPERIENCES[0])

    # Return summarized list of parlours (without inflating entire deep menu)
    summary_list = []
    for p in parlours:
        summary_list.append({
            'id': p['id'],
            'name': p['name'],
            'brandTag': p['brandTag'],
            'tagline': p['tagline'],
            'rating': p['rating'],
            'location': p['location'],
            'distance': p['distance'],
            'timings': p['timings'],
            'image': p['image'],
            'highlights': p['highlights'],
            'starting_price': p.get('starting_price', 999),
            'services_count': len(p.get('services', []))
        })

    return JsonResponse({
        'status': 'success',
        'hub': hub,
        'hub_name': experience['name'],
        'mode': 'parlour',
        'mode_name': 'Premium Parlour Services' if hub == 'womens_salon_spa' else 'Premium Barbershop & Lounge',
        'guarantee': 'Zero Waiting Time Guarantee • VIP Slot Reserved',
        'count': len(summary_list),
        'parlours': summary_list
    }, status=200)


@csrf_exempt
def beauty_parlour_detail_api(request, parlour_id):
    """
    GET /api/beauty/parlours/<parlour_id>/
    Screen 6: Full parlour profile and its Exclusive In-Salon Menu + available booking slots.
    """
    if request.method != 'GET':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    # Search in both women's and men's catalogs
    found_parlour = None
    hub = None
    for h, plist in LUXURY_PARLOURS_CATALOG.items():
        for p in plist:
            if p['id'] == parlour_id:
                found_parlour = p
                hub = h
                break
        if found_parlour:
            break

    if not found_parlour:
        return JsonResponse({'status': 'error', 'message': f'Parlour "{parlour_id}" not found'}, status=404)

    is_men = hub == 'mens_salon_massage'
    experience = next((e for e in BEAUTY_EXPERIENCES if e['id'] == hub), BEAUTY_EXPERIENCES[0])

    today = date.today()
    available_dates = [
        {"key": "Today", "label": "Today", "date": today.strftime("%d %b, %a")},
        {"key": "Tomorrow", "label": "Tomorrow", "date": (today + timedelta(days=1)).strftime("%d %b, %a")},
        {"key": "DayAfter", "label": (today + timedelta(days=2)).strftime("%a"), "date": (today + timedelta(days=2)).strftime("%d %b, %a")},
        {"key": "Day4", "label": (today + timedelta(days=3)).strftime("%a"), "date": (today + timedelta(days=3)).strftime("%d %b, %a")},
    ]

    time_slots = [
        "10:00 AM - 11:00 AM",
        "11:30 AM - 12:30 PM",
        "02:00 PM - 03:00 PM",
        "04:30 PM - 05:30 PM",
        "06:00 PM - 07:00 PM"
    ]

    stylist_tiers = [
        {
            "id": "Senior Stylist",
            "name": "Senior Barber" if is_men else "Senior Stylist",
            "desc": "Certified Expert (Included)",
            "extra_fee": 0
        },
        {
            "id": "Art Director",
            "name": "Master Hair Artist" if is_men else "Master Art Director",
            "desc": "+₹300 (Celebrity Stylist)",
            "extra_fee": 300
        }
    ]

    return JsonResponse({
        'status': 'success',
        'hub': hub,
        'hub_name': experience['name'],
        'parlour': found_parlour,
        'stylist_tiers': stylist_tiers,
        'available_dates': available_dates,
        'available_slots': time_slots,
        'booking_terms': 'Pay at Salon • Free Cancellation Anytime Before Scheduled Slot'
    }, status=200)


@csrf_exempt
def beauty_book_appointment_api(request):
    """
    POST /api/beauty/book-appointment/
    Book guaranteed in-salon appointment pass.
    Payload (JSON or form-data):
      - hub: 'womens_salon_spa' | 'mens_salon_massage'
      - parlour_id: e.g. 'bblunt_studio'
      - service_id: e.g. 'bblunt_signature_cut'
      - stylist_tier: 'Senior Stylist' | 'Art Director'
      - slot_date: 'Today' or '16 Oct, Fri'
      - slot_time: '02:00 PM - 03:00 PM'
      - customer_name: Full Name
      - customer_phone: 10-digit mobile number
      - customer_email: (optional)
      - customer_notes: (optional)
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON body'}, status=400)
    else:
        data = request.POST.dict()

    hub = data.get('hub', 'womens_salon_spa')
    parlour_id = data.get('parlour_id')
    service_id = data.get('service_id')
    stylist_tier = data.get('stylist_tier', 'Senior Stylist')
    slot_date = data.get('slot_date', 'Today')
    slot_time = data.get('slot_time', '02:00 PM - 03:00 PM')
    customer_name = data.get('customer_name', '').strip() or 'Guest Customer'
    customer_phone = data.get('customer_phone', '').strip() or '9876543210'
    customer_email = data.get('customer_email', '').strip()

    if not parlour_id or not service_id:
        return JsonResponse({'status': 'error', 'message': 'Missing parlour_id or service_id'}, status=400)

    # Locate parlour and service
    found_parlour = None
    found_service = None
    for h, plist in LUXURY_PARLOURS_CATALOG.items():
        for p in plist:
            if p['id'] == parlour_id:
                found_parlour = p
                for s in p.get('services', []):
                    if s['id'] == service_id:
                        found_service = s
                        hub = h
                        break
            if found_service:
                break
        if found_service:
            break

    if not found_parlour or not found_service:
        return JsonResponse({'status': 'error', 'message': 'Selected parlour or service not found'}, status=404)

    is_men = hub == 'mens_salon_massage'
    prefix = 'GENT' if is_men else 'LUXE'
    pass_number = f"{prefix}-{random.randint(1000, 9999)}"

    base_price = float(found_service.get('price', 999))
    stylist_extra = 300.0 if stylist_tier == 'Art Director' else 0.0
    total_payable = base_price + stylist_extra

    appointment_record = {
        'pass_code': pass_number,
        'booking_id': f"BK-{uuid.uuid4().hex[:8].upper()}",
        'status': 'CONFIRMED',
        'hub': hub,
        'hub_name': "Men's Salon & Massage" if is_men else "Women's Salon & Spa",
        'parlour': {
            'id': found_parlour['id'],
            'name': found_parlour['name'],
            'brandTag': found_parlour['brandTag'],
            'location': found_parlour['location'],
            'distance': found_parlour['distance'],
            'timings': found_parlour['timings']
        },
        'service': {
            'id': found_service['id'],
            'title': found_service['title'],
            'time': found_service['time'],
            'category': found_service.get('category', 'Salon Treatment'),
            'price': base_price
        },
        'stylist_tier': stylist_tier,
        'stylist_label': ('Master Hair Artist' if is_men else 'Master Art Director') if stylist_tier == 'Art Director' else ('Senior Barber' if is_men else 'Senior Stylist'),
        'slot_date': slot_date,
        'slot_time': slot_time,
        'customer_name': customer_name,
        'customer_phone': customer_phone,
        'customer_email': customer_email,
        'payment_mode': 'PAY_AT_SALON',
        'total_amount': total_payable,
        'currency': 'INR',
        'created_at': datetime.now().isoformat(),
        'instructions': [
            f"Present VIP Pass #{pass_number} at the reception of {found_parlour['name']}.",
            "Zero waiting time guaranteed for your reserved time slot.",
            "You can pay after treatment completion via UPI, Card, or Cash."
        ]
    }

    # Save to active passes memory cache
    ACTIVE_PARLOUR_APPOINTMENTS.append(appointment_record)

    # Optional: If customer is logged in, record in Django ServiceBooking table
    if request.user.is_authenticated:
        try:
            # find or use first available vendor
            vendor_user = CustomUser.objects.filter(role='vendor').first() or request.user
            ServiceBooking.objects.create(
                customer=request.user,
                vendor=vendor_user,
                package_name=f"{found_parlour['name']} - {found_service['title']} (Pass #{pass_number})",
                total_amount=total_payable,
                scheduled_date=date.today(),
                service_address=found_parlour['location'],
                status='accepted'
            )
        except Exception:
            pass

    return JsonResponse({
        'status': 'success',
        'message': f"Appointment confirmed at {found_parlour['name']}! Pass #{pass_number}",
        'appointment': appointment_record
    }, status=201)
