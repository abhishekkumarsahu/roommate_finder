from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import ListingForm, ListingImageForm
from .models import Listing, ListingImage

@login_required
def add_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        files = request.FILES.getlist('images')

        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.status = 'pending'
            listing.save()

            # Save images
            for img in files:
                ListingImage.objects.create(listing=listing, image=img)

            messages.success(request, "Room added successfully. Waiting for admin approval.")
            return redirect('listings:my_listings')
    else:
        form = ListingForm()

    return render(request, 'listings/add_listing.html', {'form': form})

@login_required
def my_listings(request):
    user_listings = Listing.objects.filter(owner=request.user)
    return render(request, 'listings/my_listings.html', {'listings': user_listings})

from .utils import calculate_distance

def home(request):
    user = request.user

    listings = Listing.objects.filter(status='approved')

    # If user location is known, sort by nearest
    if user.is_authenticated and user.latitude and user.longitude:
        for listing in listings:
            listing.distance = calculate_distance(
                user.latitude, user.longitude,
                listing.latitude, listing.longitude
            )

        listings = sorted(listings, key=lambda x: x.distance)

    return render(request, 'listings/home.html', {'listings': listings})
