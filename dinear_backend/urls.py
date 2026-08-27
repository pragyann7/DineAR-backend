from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from locations.views import LocationViewSet
from restaurants.views import (
    RestaurantViewSet, MenuItemViewSet, RestaurantRegistrationView, RestaurantUpdateView,
    MenuItemListView, MenuItemCreateView, MenuItemUpdateView, MenuItemDeleteView, GlobalSearchView,
    FavoriteView, FavoriteIdsView, FavoriteDetailsView, CuisineViewSet, RestaurantCategoryViewSet, FoodCategoryViewSet
)
from users.views import UserCreateView
from .views import dashboard_redirect, admin_dashboard, owner_dashboard
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'restaurants', RestaurantViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'cuisines', CuisineViewSet)
router.register(r'restaurant-categories', RestaurantCategoryViewSet)
router.register(r'food-categories', FoodCategoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Dashboards
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/owner/', owner_dashboard, name='owner_dashboard'),

    # Restaurant Registration (MVP)
    path('dashboard/register/', RestaurantRegistrationView.as_view(), name='restaurant_register'),
    path('dashboard/edit/', RestaurantUpdateView.as_view(), name='restaurant_edit'),

    # Food Management
    path('dashboard/menu/', MenuItemListView.as_view(), name='menu_item_list'),
    path('dashboard/menu/add/', MenuItemCreateView.as_view(), name='menu_item_add'),
    path('dashboard/menu/<int:pk>/edit/', MenuItemUpdateView.as_view(), name='menu_item_edit'),
    path('dashboard/menu/<int:pk>/delete/', MenuItemDeleteView.as_view(), name='menu_item_delete'),

    path('api/', include(router.urls)),
    path('api/search/', GlobalSearchView.as_view(), name='global_search'),
    path('api/favorites/ids/', FavoriteIdsView.as_view(), name='favorite_ids'),
    path('api/favorites/details/', FavoriteDetailsView.as_view(), name='favorite_details'),
    path('api/favorites/', FavoriteView.as_view(), name='favorite_add'),
    path('api/favorites/<str:type>/<int:id>/', FavoriteView.as_view(), name='favorite_remove'),
    path('api/register/', UserCreateView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
