from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Restaurant, MenuItem, Favorite
from .serializers import (
    RestaurantSerializer,
    MenuItemSerializer,
    RestaurantListSerializer,
    RestaurantDetailSerializer,
    FavoriteSerializer
)
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import RestaurantRegistrationForm, MenuItemForm
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q

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
        # Check if user already has a restaurant
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
        # Automatically get the restaurant owned by the current user
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
            queryset = queryset.filter(location__city__iexact=city)

        if category:
            # Flexible category match
            queryset = queryset.filter(
                Q(category__icontains=category) |
                Q(cuisine__icontains=category)
            )

        return queryset

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Customers only see available items
        queryset = MenuItem.objects.filter(is_available=True).exclude(status='REJECTED')
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset

class GlobalSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        city = request.query_params.get('city', '')

        if not query:
            return Response({"restaurants": [], "food_items": []})

        # 1. Search Restaurants (Direct match + Matching dishes)
        restaurants_direct = Restaurant.objects.filter(status='APPROVED')
        if city:
            restaurants_direct = restaurants_direct.filter(location__city__iexact=city)

        restaurants_by_dish = Restaurant.objects.filter(
            status='APPROVED',
            menu_items__name__icontains=query,
            menu_items__is_available=True
        ).exclude(menu_items__status='REJECTED')

        if city:
            restaurants_by_dish = restaurants_by_dish.filter(location__city__iexact=city)

        restaurants = (restaurants_direct.filter(
            Q(name__icontains=query) |
            Q(cuisine__icontains=query) |
            Q(category__icontains=query) |
            Q(description__icontains=query)
        ) | restaurants_by_dish).distinct()

        # 2. Search Menu Items (for specific food result section)
        food_items = MenuItem.objects.filter(is_available=True).exclude(status='REJECTED')
        if city:
            food_items = food_items.filter(restaurant__location__city__iexact=city)

        food_items = food_items.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        ).distinct()

        # Serialize results
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
