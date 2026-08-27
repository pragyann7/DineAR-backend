from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Restaurant, MenuItem, Favorite, Cuisine, RestaurantCategory, FoodCategory
from .serializers import (
    RestaurantSerializer,
    MenuItemSerializer,
    RestaurantListSerializer,
    RestaurantDetailSerializer,
    FavoriteSerializer,
    CuisineSerializer,
    RestaurantCategorySerializer,
    FoodCategorySerializer
)
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import RestaurantRegistrationForm, MenuItemForm
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q

class CuisineViewSet(viewsets.ModelViewSet):
    queryset = Cuisine.objects.all()
    serializer_class = CuisineSerializer
    permission_classes = [permissions.AllowAny]

class RestaurantCategoryViewSet(viewsets.ModelViewSet):
    queryset = RestaurantCategory.objects.all()
    serializer_class = RestaurantCategorySerializer
    permission_classes = [permissions.AllowAny]

class FoodCategoryViewSet(viewsets.ModelViewSet):
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    permission_classes = [permissions.AllowAny]

class MenuItemListView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'owner/menu_list.html'
    context_object_name = 'menu_items'

    def get_queryset(self):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        return MenuItem.objects.filter(restaurant=restaurant)

class MenuItemCreateView(LoginRequiredMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'owner/food_form.html'
    success_url = reverse_lazy('menu_item_list')

    def form_valid(self, form):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        form.instance.restaurant = restaurant
        return super().form_valid(form)

class MenuItemUpdateView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'owner/food_form.html'
    success_url = reverse_lazy('menu_item_list')

    def get_queryset(self):
        return MenuItem.objects.filter(restaurant__owner=self.request.user)

class MenuItemDeleteView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'owner/menu_confirm_delete.html'
    success_url = reverse_lazy('menu_item_list')

    def get_queryset(self):
        return MenuItem.objects.filter(restaurant__owner=self.request.user)

class RestaurantRegistrationView(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantRegistrationForm
    template_name = 'owner/register_restaurant.html'
    success_url = reverse_lazy('dashboard_redirect')

    def form_valid(self, form):
        if Restaurant.objects.filter(owner=self.request.user).exists():
            return redirect('dashboard_redirect')

        form.instance.owner = self.request.user
        form.instance.status = 'PENDING'
        return super().form_valid(form)

class RestaurantUpdateView(LoginRequiredMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantRegistrationForm
    template_name = 'owner/register_restaurant.html'
    success_url = reverse_lazy('dashboard_redirect')

    def get_object(self, queryset=None):
        return get_object_or_404(Restaurant, owner=self.request.user)

    def form_valid(self, form):
        if form.instance.status == 'REJECTED':
            form.instance.status = 'PENDING'
            form.instance.rejection_reason = ""
        return super().form_valid(form)

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return RestaurantListSerializer
        return RestaurantDetailSerializer

    def get_queryset(self):
        queryset = Restaurant.objects.filter(status='APPROVED')
        city = self.request.query_params.get('city')
        category = self.request.query_params.get('category')

        if city:
            # Match against Area Name (e.g. Bharatpur) OR District (e.g. Chitwan)
            queryset = queryset.filter(
                Q(location__name__iexact=city) |
                Q(location__city__iexact=city)
            )

        if category:
            # Flexible match across name, category model name, and cuisine model names
            queryset = queryset.filter(
                Q(category__name__icontains=category) |
                Q(cuisines__name__icontains=category)
            ).distinct()

        return queryset

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = MenuItem.objects.filter(is_available=True).exclude(status='REJECTED')
        restaurant_id = self.request.query_params.get('restaurant')
        category = self.request.query_params.get('category')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if category:
            queryset = queryset.filter(category__name__icontains=category)

        return queryset

class GlobalSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        city = request.query_params.get('city', '')

        if not query:
            return Response({"restaurants": [], "food_items": []})

        # 1. Search Restaurants
        restaurants_base = Restaurant.objects.filter(status='APPROVED')
        if city:
            restaurants_base = restaurants_base.filter(
                Q(location__name__iexact=city) |
                Q(location__city__iexact=city)
            )

        restaurants_by_dish = restaurants_base.filter(
            menu_items__name__icontains=query,
            menu_items__is_available=True
        ).exclude(menu_items__status='REJECTED')

        restaurants = (restaurants_base.filter(
            Q(name__icontains=query) |
            Q(cuisines__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(description__icontains=query)
        ) | restaurants_by_dish).distinct()

        # 2. Search Menu Items
        food_items = MenuItem.objects.filter(is_available=True).exclude(status='REJECTED')
        if city:
            food_items = food_items.filter(
                Q(restaurant__location__name__iexact=city) |
                Q(restaurant__location__city__iexact=city)
            )

        food_items = food_items.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

        res_serializer = RestaurantListSerializer(restaurants, many=True, context={'request': request})
        food_serializer = MenuItemSerializer(food_items, many=True, context={'request': request})

        return Response({
            "restaurants": res_serializer.data,
            "food_items": food_serializer.data
        })

class FavoriteIdsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        restaurant_ids = Favorite.objects.filter(user=user, restaurant__isnull=False).values_list('restaurant_id', flat=True)
        food_ids = Favorite.objects.filter(user=user, menu_item__isnull=False).values_list('menu_item_id', flat=True)
        return Response({
            "restaurants": list(restaurant_ids),
            "foods": list(food_ids)
        })

class FavoriteDetailsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # Fetch actual objects for the user's favorites
        favorites = Favorite.objects.filter(user=user)

        restaurant_ids = favorites.filter(restaurant__isnull=False).values_list('restaurant_id', flat=True)
        food_ids = favorites.filter(menu_item__isnull=False).values_list('menu_item_id', flat=True)

        restaurants = Restaurant.objects.filter(id__in=restaurant_ids, status='APPROVED')
        foods = MenuItem.objects.filter(id__in=food_ids, is_available=True).exclude(status='REJECTED')

        res_serializer = RestaurantListSerializer(restaurants, many=True, context={'request': request})
        food_serializer = MenuItemSerializer(foods, many=True, context={'request': request})

        return Response({
            "restaurants": res_serializer.data,
            "food_items": food_serializer.data
        })

class FavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        item_type = request.data.get('type')
        item_id = request.data.get('item_id')

        if item_type == 'restaurant':
            Favorite.objects.get_or_create(user=user, restaurant_id=item_id)
        elif item_type == 'food':
            Favorite.objects.get_or_create(user=user, menu_item_id=item_id)
        else:
            return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, type, id):
        user = request.user
        if type == 'restaurant':
            Favorite.objects.filter(user=user, restaurant_id=id).delete()
        elif type == 'food':
            Favorite.objects.filter(user=user, menu_item_id=id).delete()
        else:
            return Response({"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
