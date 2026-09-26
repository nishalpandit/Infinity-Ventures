from django.core.management.base import BaseCommand
from myapp.models import (
    SiteBranding,
    HeroSection,
    QuickServiceCard,
    FeaturedProjectCard,
    PackageCard,
    Testimonial,
    TrustMetric,
)

class Command(BaseCommand):
    help = 'Seeds initial Landing Page CMS content (Branding, Hero, Quick Services, Featured Projects, Packages, Testimonials, Trust Metrics)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Landing Page CMS data..."))

        # 1. Site Branding
        branding, created = SiteBranding.objects.get_or_create(
            pk=1,
            defaults={
                'site_title': 'Suggu Services',
                'tagline': 'Instant Home Services & Custom Project Bidding Marketplace',
                'contact_email': 'support@sugguservices.com',
                'support_phone': '+91 98765 43210',
                'address': 'Main Road, Ranchi, Jharkhand 834001, India',
                'facebook_url': 'https://facebook.com',
                'instagram_url': 'https://instagram.com',
                'linkedin_url': 'https://linkedin.com',
                'twitter_url': 'https://twitter.com',
                'youtube_url': 'https://youtube.com',
                'copyright_text': '© 2026 Suggu Services Marketplace. All rights reserved.',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("[OK] Created Site Branding"))
        else:
            self.stdout.write("  Site Branding already exists")

        # 2. Hero Section
        hero, created = HeroSection.objects.get_or_create(
            pk=1,
            defaults={
                'badge_text': 'DUAL-ENGINE SERVICE MARKETPLACE',
                'headline': 'Book verified home pros in 60s or receive competitive contractor bids.',
                'subtext': "India's smartest dual-engine marketplace: Book verified technicians at fixed rates in 60 seconds, or post major renovation and contracting projects and compare bids side-by-side.",
                'cta_primary_text': 'Book Quick Service',
                'cta_primary_url': '/user/quick-services/create.html',
                'cta_secondary_text': 'Post a Project for Bids',
                'cta_secondary_url': '/user/jobs/create.html',
                'stat1_number': '60s',
                'stat1_label': 'Instant Matching',
                'stat2_number': '15k+',
                'stat2_label': 'Verified Pros',
                'stat3_number': '100%',
                'stat3_label': 'Price Protection',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("[OK] Created Hero Section"))
        else:
            self.stdout.write("  Hero Section already exists")

        # 3. Quick Service Cards
        quick_services_data = [
            {
                'title': 'Kitchen Sink Pipe Leakage',
                'subtitle': 'Drainage fix & joint sealing',
                'price': 299.00,
                'discount_price': 499.00,
                'duration': '30 Mins',
                'category_tag': 'Plumbing',
                'badge_text': 'Popular',
                'order': 1,
            },
            {
                'title': 'AC Deep Jet Cleaning',
                'subtitle': 'Split/Window cooling boost & coil wash',
                'price': 599.00,
                'discount_price': 899.00,
                'duration': '45 Mins',
                'category_tag': 'AC Repair',
                'badge_text': 'Instant',
                'order': 2,
            },
            {
                'title': 'Switchboard & MCB Repair',
                'subtitle': 'Short circuit check & switch replacement',
                'price': 249.00,
                'discount_price': 399.00,
                'duration': '20 Mins',
                'category_tag': 'Electrical',
                'badge_text': 'Emergency',
                'order': 3,
            },
            {
                'title': 'Full Bathroom Deep Clean',
                'subtitle': 'Tile descaling, stain removal & sanitization',
                'price': 799.00,
                'discount_price': 1299.00,
                'duration': '60 Mins',
                'category_tag': 'Cleaning',
                'badge_text': 'Top Rated',
                'order': 4,
            },
            {
                'title': 'Door Lock & Hinge Fixing',
                'subtitle': 'Cylinder replacement & alignment fix',
                'price': 349.00,
                'discount_price': 499.00,
                'duration': '40 Mins',
                'category_tag': 'Carpentry',
                'badge_text': 'Handyman',
                'order': 5,
            },
            {
                'title': 'RO Water Purifier Service',
                'subtitle': 'Filter change & TDS calibration',
                'price': 449.00,
                'discount_price': 699.00,
                'duration': '35 Mins',
                'category_tag': 'Appliance',
                'badge_text': 'Essential',
                'order': 6,
            },
        ]

        if QuickServiceCard.objects.count() == 0:
            for item in quick_services_data:
                QuickServiceCard.objects.create(**item)
            self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(quick_services_data)} Quick Service Cards"))
        else:
            self.stdout.write("  Quick Service Cards already exist")

        # 4. Featured Project Cards (Bidding Showcase)
        featured_projects_data = [
            {
                'title': 'Full 3BHK Apartment Interior Renovation',
                'category_name': 'Full Renovation',
                'budget_range': '₹2.5L - ₹4.0L',
                'location': 'Kanke Road, Ranchi',
                'timeline': '45 Days',
                'vendor_quote_preview': 'Lowest bid: ₹2,80,000 · 4 Verified Contractors quoted',
                'bids_count': 6,
                'status_tag': 'Active Bidding',
                'order': 1,
            },
            {
                'title': 'Terrace Waterproofing & Heat Proofing',
                'category_name': 'Waterproofing',
                'budget_range': '₹45,000 - ₹65,000',
                'location': 'Harmu Housing Colony, Ranchi',
                'timeline': '7 Days',
                'vendor_quote_preview': 'Lowest bid: ₹48,000 · Includes 5-year leak warranty',
                'bids_count': 4,
                'status_tag': 'Quotes In Review',
                'order': 2,
            },
            {
                'title': 'Commercial Office Electrical Rewiring',
                'category_name': 'Electrical Contracting',
                'budget_range': '₹80,000 - ₹1,20,000',
                'location': 'Lalpur, Ranchi',
                'timeline': '14 Days',
                'vendor_quote_preview': 'Lowest bid: ₹85,000 · Grade-A Fire retardant wiring',
                'bids_count': 5,
                'status_tag': 'Active Bidding',
                'order': 3,
            },
        ]

        if FeaturedProjectCard.objects.count() == 0:
            for item in featured_projects_data:
                FeaturedProjectCard.objects.create(**item)
            self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(featured_projects_data)} Featured Project Cards"))
        else:
            self.stdout.write("  Featured Project Cards already exist")

        # 5. Service Packages
        packages_data = [
            {
                'title': 'Home Essentials Shield',
                'subtitle': 'Quarterly preventive maintenance',
                'price': 1499.00,
                'price_unit': '/ Quarter',
                'original_price': 2499.00,
                'feature_bullets': "2 AC Deep Servicing sessions\n1 Plumbing checkup & pressure test\n1 Electrical safety audit\nFree priority technician dispatch",
                'filter_tag': 'Maintenance',
                'cta_label': 'Select Plan',
                'cta_url': '/user/quick-services/create.html',
                'is_popular': False,
                'order': 1,
            },
            {
                'title': 'Complete Home Care Pro',
                'subtitle': 'Annual unlimited repairs & priority cover',
                'price': 4999.00,
                'price_unit': '/ Year',
                'original_price': 7999.00,
                'feature_bullets': "Unlimited minor plumbing & electrical repairs\n4 AC Jet washes & filter replacements\n1 Full home deep cleaning session\nZero visitation fee guarantee\nDedicated customer success manager",
                'filter_tag': 'All',
                'cta_label': 'Get Annual Protection',
                'cta_url': '/user/quick-services/create.html',
                'is_popular': True,
                'order': 2,
            },
            {
                'title': 'Commercial Facility Care',
                'subtitle': 'Tailored maintenance for offices & clinics',
                'price': 9999.00,
                'price_unit': '/ Year',
                'original_price': 14999.00,
                'feature_bullets': "Monthly preventive site inspection\nEmergency 30-minute SLA response\nGST invoice & credit ledger support\nCertified electrical & HVAC technicians",
                'filter_tag': 'Commercial',
                'cta_label': 'Enterprise Quote',
                'cta_url': '/user/jobs/create.html',
                'is_popular': False,
                'order': 3,
            },
        ]

        if PackageCard.objects.count() == 0:
            for item in packages_data:
                PackageCard.objects.create(**item)
            self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(packages_data)} Service Packages"))
        else:
            self.stdout.write("  Service Packages already exist")

        # 6. Testimonials
        testimonials_data = [
            {
                'client_name': 'Dr. Rajesh Sharma',
                'client_role_or_company': 'Clinic Owner, Ranchi',
                'rating': 5.0,
                'review_text': 'Posted our clinic renovation on Suggu Services and received 5 detailed vendor bids within 4 hours. Saved nearly ₹60,000 compared to off-market contractors!',
                'service_taken': 'Clinic Interior Renovation',
                'order': 1,
            },
            {
                'client_name': 'Pooja Verma',
                'client_role_or_company': 'Apartment Owner, Harmu',
                'rating': 5.0,
                'review_text': 'Booked an emergency plumber at 9:00 PM for a burst pipe. The technician reached within 25 minutes with full replacement parts. Outstanding service!',
                'service_taken': 'Emergency Plumbing',
                'order': 2,
            },
            {
                'client_name': 'Amitabh Sen',
                'client_role_or_company': 'Facility Manager, Tech Hub',
                'rating': 4.9,
                'review_text': 'The transparent quotation comparison tool makes contractor selection seamless. All background checks and past review scores were clearly visible.',
                'service_taken': 'Commercial Electrical Overhaul',
                'order': 3,
            },
        ]

        if Testimonial.objects.count() == 0:
            for item in testimonials_data:
                Testimonial.objects.create(**item)
            self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(testimonials_data)} Testimonials"))
        else:
            self.stdout.write("  Testimonials already exist")

        # 7. Trust Metrics
        trust_metrics_data = [
            {
                'title': 'Aadhaar & Police Verified',
                'description': 'Every technician and firm undergoes a rigorous background check — Aadhaar authentication, police verification, address proof and skill assessment before their first job.',
                'badge_text': '100% of active pros verified',
                'icon_class': 'fa-solid fa-shield-halved',
                'icon_svg': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l8 4v6c0 5-3.4 8.7-8 10-4.6-1.3-8-5-8-10V6l8-4Z"/><path d="M9 12l2 2 4-4"/></svg>',
                'stat_number': '100%',
                'label': 'Aadhaar & Police Verified',
                'order': 1,
            },
            {
                'title': '₹10,000 Damage Protection',
                'description': 'Accidental damage to your property during service is covered up to ₹10,000 per booking. Raise a claim in-app with photos and get resolution within 72 hours.',
                'badge_text': 'In-built warranty cover',
                'icon_class': 'fa-solid fa-shield-virus',
                'icon_svg': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l8 4v6c0 5-3.4 8.7-8 10-4.6-1.3-8-5-8-10V6l8-4Z"/><path d="M12 8v5M12 16.5h.01"/></svg>',
                'stat_number': '₹10,000',
                'label': 'Damage Protection Cover',
                'order': 2,
            },
            {
                'title': 'Call Masking & In-App Chat',
                'description': 'Your phone number is never exposed to contractors without your explicit consent. Communicate through masked calling and end-to-end logged chat inside the app.',
                'badge_text': 'Privacy by default',
                'icon_class': 'fa-solid fa-comment-dots',
                'icon_svg': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z"/><path d="M8 9h8M8 13h5"/></svg>',
                'stat_number': '100% Private',
                'label': 'Call Masking & In-App Chat',
                'order': 3,
            },
            {
                'title': 'Transparent & Escrow Payments',
                'description': 'Pay via UPI, cards or netbanking — only after you are satisfied with the work. Funds are held in escrow and released to the provider on your confirmation.',
                'badge_text': 'PCI-DSS compliant gateway',
                'icon_class': 'fa-solid fa-credit-card',
                'icon_svg': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="14" rx="3"/><path d="M2 10h20M16 15h2"/></svg>',
                'stat_number': '₹0 Extra',
                'label': 'Transparent & Escrow Payments',
                'order': 4,
            },
        ]

        if TrustMetric.objects.count() == 0:
            for item in trust_metrics_data:
                TrustMetric.objects.create(**item)
            self.stdout.write(self.style.SUCCESS(f"[OK] Seeded {len(trust_metrics_data)} Trust Metrics"))
        else:
            self.stdout.write("  Trust Metrics already exist")

        self.stdout.write(self.style.SUCCESS("[OK] CMS Seeding completed successfully!"))
