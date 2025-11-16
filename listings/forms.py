from django import forms
from .models import Listing, ListingImage

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['owner', 'status']

class ListingImageForm(forms.ModelForm):
    class Meta:
        model = ListingImage
        fields = ['image']
