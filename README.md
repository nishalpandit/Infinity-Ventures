# Sugu (Infinity Ventures)

Sugu is an on-demand multi-vendor home and commercial services marketplace.

## Key Features
- **Live Geolocation & Proximity Engine**: 10 km radius matching for instant nearby services using high-accuracy HTML5 geolocation and distance calculations.
- **Urban Company-Style Quick Services**: Multi-tier package options (Basic, Standard, Premium), transparent inclusions and exclusions.
- **Vendor Portal & Quotation Bidding**: Dedicated vendor dashboard for service listings, bookings management, and real-time customer job bidding.
- **Dynamic Bid & Credit System**: Database-backed credit packages, instant top-ups, audit transaction ledger, and quotation credit consumption.
- **Customer Job Management**: Flexible job posting with photo attachments, custom budgets, and quotation reviews.
- **Admin Control Center**: Complete oversight of users, KYC verification, complaints, and service catalogs.

## Tech Stack
- **Backend**: Python 3.12, Django 5.x
- **Database**: SQLite / PostgreSQL
- **Frontend**: Vanilla CSS, Tailwind CSS, Responsive JavaScript
- **Geolocation**: Nominatim / Browser Geolocation API

## Local Development
```bash
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
