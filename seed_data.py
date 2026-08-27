import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dinear_backend.settings')
django.setup()

from restaurants.models import Cuisine, RestaurantCategory, FoodCategory, Restaurant
from locations.models import Location
from django.contrib.auth import get_user_model

User = get_user_model()

def seed():
    # 1. Users
    admin, _ = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True})
    admin.set_password('admin123')
    admin.save()

    # 2. Locations
    Location.objects.all().delete() # Note: This deletes linked restaurants!
    loc_bharatpur, _ = Location.objects.get_or_create(name='Bharatpur', city='Chitwan', defaults={'address': 'Bharatpur, Chitwan, Nepal'})
    loc_butwal, _ = Location.objects.get_or_create(name='Butwal', city='Rupandehi', defaults={'address': 'Butwal, Rupandehi, Nepal'})
    loc_ktm, _ = Location.objects.get_or_create(name='Kathmandu', city='Kathmandu', defaults={'address': 'Kathmandu, Nepal'})

    # 3. Cuisines
    cuisines_list = ['Nepali', 'Indian', 'Chinese', 'Italian', 'American']
    cuisines_objs = {}
    for c in cuisines_list:
        obj, _ = Cuisine.objects.get_or_create(name=c)
        cuisines_objs[c] = obj

    # 4. Categories
    res_cat_fast, _ = RestaurantCategory.objects.get_or_create(name='Fast Food')
    res_cat_cafe, _ = RestaurantCategory.objects.get_or_create(name='Café')

    food_cat_main, _ = FoodCategory.objects.get_or_create(name='Main Course')

    # 5. Restaurants
    r1, _ = Restaurant.objects.get_or_create(
        name="The Burger House",
        defaults={
            'location': loc_bharatpur,
            'description': "Best burgers in Bharatpur.",
            'category': res_cat_fast,
            'status': 'APPROVED',
            'rating': 4.5,
            'price_range': '$$'
        }
    )
    r1.cuisines.add(cuisines_objs['American'])

    r2, _ = Restaurant.objects.get_or_create(
        name="Momo Center",
        defaults={
            'location': loc_butwal,
            'description': "Authentic Nepali Momo.",
            'category': res_cat_fast,
            'status': 'APPROVED',
            'rating': 4.8,
            'price_range': '$'
        }
    )
    r2.cuisines.add(cuisines_objs['Nepali'])

    print("Successfully seeded clean initial data including restaurants.")

if __name__ == '__main__':
    seed()
