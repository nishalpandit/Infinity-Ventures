import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from myapp.models import Category, SubCategory

# Mapping of category names to their desired subcategories
subcats_map = {
    'Appliances': ['AC Repair & Service', 'Washing Machine Repair', 'Refrigerator Repair'],
    'Beauty & Spa': ['Salon for Men', 'Salon for Women', 'Spa & Massage'],
    'Carpentry': ['Furniture Repair', 'Custom Furniture Assembly', 'Wood Polishing'],
    'Cleaning & Pest Control': ['Full Home Deep Cleaning', 'Pest Control', 'Bathroom Cleaning'],
    'Electrical': ['Wiring & Repairs', 'Inverter/Battery Setup', 'Fan/Light Fitting'],
    'Painting': ['Full Home Painting', 'Single Room/Wall Painting', 'Waterproofing'],
    'Plumbing': ['Pipe Leakage Repair', 'Tap/Mixer Fitting', 'Water Tank Installation']
}

print("Cleaning up old subcategories...")
SubCategory.objects.all().delete()

print("Creating specific subcategories for all categories...")
for cat_name, subcat_list in subcats_map.items():
    # Try to find the category using icontains since exact name might vary slightly
    cat = Category.objects.filter(name__icontains=cat_name.split()[0]).first()
    if cat:
        for sub_name in subcat_list:
            SubCategory.objects.get_or_create(category=cat, name=sub_name)
        print(f"Added {len(subcat_list)} subcategories to '{cat.name}'")
    else:
        print(f"Warning: Category matching '{cat_name}' not found!")

print("Done creating subcategories!")
