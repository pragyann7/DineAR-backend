from django.db import models
from django.conf import settings
from locations.models import Location

class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='cuisine_icons/', blank=True, null=True)

    def __str__(self):
        return self.name

class RestaurantCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Restaurant Categories"

class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='food_category_icons/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Food Categories"

class Restaurant(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('REJECTED', 'Changes Required'),
        ('APPROVED', 'Approved'),
        ('SUSPENDED', 'Suspended'),
    ]

    name = models.CharField(max_length=200)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurant', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='restaurants')
    description = models.TextField()
    image = models.ImageField(upload_to='restaurant_images/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    # New relationships
    cuisines = models.ManyToManyField(Cuisine, related_name='restaurants', blank=True)
    category = models.ForeignKey(RestaurantCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='restaurants')

    price_range = models.CharField(max_length=10, default="$$")
    delivery_time = models.CharField(max_length=50, default="20-30 MIN")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    model_file = models.FileField(upload_to='models/', blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    model_version = models.CharField(max_length=50, default='v1')

    # New relationship
    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='menu_items')

    tag1 = models.CharField(max_length=50, blank=True, null=True, default='DineAR')
    tag2 = models.CharField(max_length=50, blank=True, null=True, default='Food')
    is_available = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=Restaurant.STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return self.name

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'restaurant', 'menu_item')

    def __str__(self):
        if self.restaurant:
            return f"{self.user.username} - Restaurant: {self.restaurant.name}"
        return f"{self.user.username} - Food: {self.menu_item.name}"
