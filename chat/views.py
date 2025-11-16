from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from listings.models import Listing
from django.db import models
from .models import Inquiry, ChatMessage
from common.utils import notify


@login_required
def create_inquiry(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if listing.owner == request.user:
        messages.error(request, "You cannot show interest in your own listing.")
        return redirect('listings:home')

    # Check if inquiry already exists
    inquiry, created = Inquiry.objects.get_or_create(
        listing=listing,
        from_user=request.user,
        to_user=listing.owner
    )

    if created:
        messages.success(request, "Interest request sent! You can now chat with the owner.")
    else:
        messages.info(request, "You already have an active chat for this listing.")

    inquiry.status = 'in_chat'
    inquiry.save()

    notify(
    user=listing.owner,
    message=f"{request.user.full_name} has shown interest in your listing '{listing.title}'.",
    link=f"/chat/room/{inquiry.id}/"
)

    return redirect('chat:chat_room', inquiry_id=inquiry.id)

@login_required
def inbox(request):
    inquiries = Inquiry.objects.filter(
        models.Q(from_user=request.user) | models.Q(to_user=request.user)
    ).order_by('-created_at')

    return render(request, 'chat/inbox.html', {'inquiries': inquiries})

@login_required
def chat_room(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)

    if request.user not in [inquiry.from_user, inquiry.to_user]:
        messages.error(request, "You are not allowed to view this chat.")
        return redirect('chat:inbox')

    if request.method == 'POST':
        msg_text = request.POST.get('message')
        if msg_text:
            ChatMessage.objects.create(
                inquiry=inquiry,
                sender=request.user,
                text=msg_text
            )

            # 🔔 SEND NOTIFICATION TO THE OTHER USER
            other_user = inquiry.owner if request.user == inquiry.tenant else inquiry.tenant

            notify(
                user=other_user,
                message=f"New message from {request.user.full_name}",
                link=f"/chat/room/{inquiry.id}/"
            )


    messages_list = inquiry.messages.all().order_by('timestamp')

    return render(request, 'chat/chat_room.html', {
        'inquiry': inquiry,
        'messages': messages_list
    })

    

