from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('create/<int:listing_id>/', views.create_inquiry, name='create_inquiry'),
    path('room/<int:inquiry_id>/', views.chat_room, name='chat_room'),
]
