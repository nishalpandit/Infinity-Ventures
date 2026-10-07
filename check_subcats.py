import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from myapp.models import Category, SubCategory

cats = Category.objects.all()
for c in cats:
    subs = c.subcategories.all()
    print(f"Category: {c.name} has {subs.count()} subcategories.")
    if subs.count() == 0 and 'Beauty' in c.name:
        SubCategory.objects.create(category=c, name='Men')
        SubCategory.objects.create(category=c, name='Women')
        print(f"Created Men and Women for {c.name}")
    elif subs.count() == 0:
        SubCategory.objects.create(category=c, name='General Maintenance')
        SubCategory.objects.create(category=c, name='Deep Cleaning')
        print(f"Created generic subcategories for {c.name}")
