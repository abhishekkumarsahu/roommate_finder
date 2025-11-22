from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_listing, name='add_listing'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('<int:listing_id>/', views.listing_detail, name='listing_detail'),
]
