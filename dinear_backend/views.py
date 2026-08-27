from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import User
from restaurants.models import Restaurant, MenuItem
from locations.models import Location

@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    try:
        restaurant = Restaurant.objects.get(owner=request.user)
        if restaurant.status == 'APPROVED':
            return redirect('owner_dashboard')
        elif restaurant.status == 'PENDING':
            return render(request, 'owner/status_pending.html', {'restaurant': restaurant})
        elif restaurant.status == 'REJECTED':
            return render(request, 'owner/status_rejected.html', {'restaurant': restaurant})
        else: # DRAFT or other
            return redirect('owner_dashboard')
    except Restaurant.DoesNotExist:
        return render(request, 'owner/dashboard_no_restaurant.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('dashboard_redirect')

    context = {
        'total_users': User.objects.count(),
        'total_restaurants': Restaurant.objects.filter(status='APPROVED').count(),
        'total_locations': Location.objects.count(),
        'pending_applications': Restaurant.objects.filter(status='PENDING').count(),
        'recent_restaurants': Restaurant.objects.filter(status='APPROVED').order_by('-id')[:5],
        'pending_restaurants': Restaurant.objects.filter(status='PENDING').order_by('-id')[:5]
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def owner_dashboard(request):
    # Only allow if approved or manually overridden
    try:
        restaurant = Restaurant.objects.get(owner=request.user)
        if restaurant.status != 'APPROVED' and not request.user.is_superuser:
            return redirect('dashboard_redirect')
    except Restaurant.DoesNotExist:
        if not request.user.is_superuser:
            return redirect('dashboard_redirect')
        restaurant = None

    context = {
        'restaurant': restaurant
    }
    return render(request, 'owner/dashboard.html', context)
