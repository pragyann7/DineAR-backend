from django.contrib import admin
from .models import Restaurant, MenuItem

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'owner', 'rating', 'status')
    list_filter = ('status', 'location')
    search_fields = ('name', 'description')
    inlines = [MenuItemInline]

    def save_model(self, request, obj, form, change):
        # Automatically set is_restaurant_owner when approved
        if obj.status == 'APPROVED' and obj.owner:
            obj.owner.is_restaurant_owner = True
            obj.owner.save()
        super().save_model(request, obj, form, change)

admin.site.register(Restaurant, RestaurantAdmin)

class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'category', 'status', 'is_available')
    list_filter = ('status', 'is_available', 'category')
    search_fields = ('name', 'description')

admin.site.register(MenuItem, MenuItemAdmin)

from .models import Favorite
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'menu_item', 'created_at')
    list_filter = ('created_at',)

admin.site.register(Favorite, FavoriteAdmin)
