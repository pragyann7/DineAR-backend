from rest_framework import serializers
from .models import Restaurant, MenuItem, Cuisine, RestaurantCategory, FoodCategory, Favorite

class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ['id', 'name', 'icon']

class RestaurantCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantCategory
        fields = ['id', 'name', 'icon']

class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ['id', 'name', 'icon']

class MenuItemSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    model_url = serializers.FileField(source='model_file', read_only=True)
    restaurant_id = serializers.PrimaryKeyRelatedField(source='restaurant', read_only=True)
    has_3d = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'restaurant_id', 'name', 'price', 'description',
            'image_url', 'model_url', 'model_name', 'model_version',
            'category', 'category_name', 'tag1', 'tag2', 'is_available', 'status', 'has_3d'
        ]

    def get_has_3d(self, obj):
        return bool(obj.model_file) and obj.status == 'APPROVED'

class RestaurantListSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    city = serializers.CharField(source='location.city', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    cuisine_names = serializers.StringRelatedField(source='cuisines', many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'image_url', 'rating', 'cuisine_names', 'category_name', 'price_range', 'delivery_time', 'city']

class RestaurantDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    cuisine_names = serializers.StringRelatedField(source='cuisines', many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'image_url', 'rating', 'cuisine_names', 'category_name', 'price_range', 'delivery_time']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'restaurant', 'menu_item', 'created_at']
        read_only_fields = ['user']

    def validate(self, data):
        restaurant = data.get('restaurant')
        menu_item = data.get('menu_item')
        if not restaurant and not menu_item:
            raise serializers.ValidationError("Must provide either a restaurant or a menu item.")
        if restaurant and menu_item:
            raise serializers.ValidationError("Cannot favorite both a restaurant and a menu item at once.")
        return data

# Simplified backward compatibility
class RestaurantSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    image_url = serializers.ImageField(source='image', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    cuisine_names = serializers.StringRelatedField(source='cuisines', many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'location', 'description', 'image_url', 'rating', 'cuisine_names', 'category_name', 'price_range', 'delivery_time', 'menu_items']
