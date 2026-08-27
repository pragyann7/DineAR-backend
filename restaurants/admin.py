from django.contrib import admin
from .models import Restaurant, MenuItem, Cuisine, RestaurantCategory, FoodCategory, Favorite

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(RestaurantCategory)
class RestaurantCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'owner', 'rating', 'status')
    list_filter = ('status', 'location', 'category')
    search_fields = ('name', 'description')
    filter_horizontal = ('cuisines',)
    inlines = [MenuItemInline]

    def save_model(self, request, obj, form, change):
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

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'menu_item', 'created_at')
    list_filter = ('created_at',)

admin.site.register(Favorite, FavoriteAdmin)
