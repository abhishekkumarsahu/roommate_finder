from django.urls import path
from . import views

app_name = 'agreements'

urlpatterns = [
    path('start/<int:inquiry_id>/', views.start_agreement, name='start_agreement'),
    path('fill/<int:agreement_id>/', views.fill_agreement, name='fill_agreement'),
    path('view/<int:agreement_id>/', views.view_agreement, name='view_agreement'),
    path('download/<int:agreement_id>/', views.download_agreement, name='download'),
]
