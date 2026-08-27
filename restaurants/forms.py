from django import forms
from .models import Restaurant, MenuItem

class RestaurantRegistrationForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'location', 'description', 'cuisine', 'price_range', 'delivery_time', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm'}),
            'location': forms.Select(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm', 'rows': 4}),
            'cuisine': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm', 'placeholder': 'e.g. Italian, Nepali'}),
            'price_range': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm', 'placeholder': 'e.g. $, $$, $$$'}),
            'delivery_time': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm', 'placeholder': 'e.g. 20-30 MIN'}),
            'image': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm'}),
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'price', 'description', 'category', 'image', 'model_file', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm'}),
            'price': forms.NumberInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm', 'rows': 3}),
            'category': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm'}),
            'image': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm'}),
            'model_file': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm', 'accept': '.glb'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded'}),
        }
