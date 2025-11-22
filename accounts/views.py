from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import CustomUser
from .forms import SignupForm, LoginForm, ProfileForm
from .tokens import account_activation_token
from django.db import models

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # inactive until email verified
            user.save()

            # Send activation email
            current_site = get_current_site(request)
            subject = 'Activate Your Roommate Finder Account'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            email = EmailMessage(subject, message, to=[user.email])
            email.send()
            messages.success(request, 'Account created! Check your email to activate your account.')
            return redirect('accounts:login')
    else:
        form = SignupForm()
        print("FORM ERRORS:", form.errors)

    return render(request, 'accounts/signup.html', {'form': form})

# Email activation
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('accounts:signup')

# Login view
# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(request, data=request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(email=email, password=password)
#             if user is not None:
#                 if user.verification_status == 'verified':
#                     login(request, user)
#                     return redirect('accounts:profile')
#                 else:
#                     messages.warning(request, 'Your account is pending admin verification.')
#             else:
#                 messages.error(request, 'Invalid credentials.')
#     else:
#         form = LoginForm()
#     return render(request, 'accounts/login.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # If you use EMAIL as username
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Check verification status
                if user.verification_status == 'verified':
                    login(request, user)
                    messages.success(request, 'Login successful!')
                    return redirect('accounts:profile')
                else:
                    messages.warning(request, 'Your account is pending admin verification.')
                    return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid credentials.')
                return redirect('accounts:login')

        else:
            # AuthenticationForm returns errors here
            errors = form.non_field_errors()
            for error in errors:
                messages.error(request, error)
            return redirect('accounts:login')

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# Logout
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

# Profile view
@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def dashboard(request):
    from listings.models import Listing
    from chat.models import Inquiry
    from agreements.models import Agreement

    listings = Listing.objects.filter(owner=request.user)
    inquiries = Inquiry.objects.filter(
        models.Q(from_user=request.user) | models.Q(to_user=request.user)
    )
    agreements = Agreement.objects.filter(
        models.Q(tenant=request.user) | models.Q(owner=request.user)
    )
    
    return render(request, 'accounts/dashboard.html', {
        'listings': listings,
        'inquiries': inquiries,
        'agreements': agreements
    })
