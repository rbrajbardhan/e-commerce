from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
import random
from django import forms 

from .forms import (
    UserRegisterForm,
    UserLoginForm,
    UserUpdateForm,
    ProfileUpdateForm,
    AuthenticationForm
)

# --- HELPER FUNCTIONS ---

def send_otp_email(user):
    otp = str(random.randint(100000, 999999))
    profile = user.profile
    profile.otp = otp
    profile.save()

    send_mail(
        "ShopX Secure Access - Your OTP",
        f'Hello {user.username}, \n\nYour One-Time Password (OTP) is: {otp}\n\nPlease enter this code to finalize your access.\n\nStay Secure,\nShopX Team',
        'noreply@shopx.com',
        [user.email],
        fail_silently=False,
    )

# --- FORMS ---

class OTPform(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control bg-dark text-white border-secondary text-center fs-4',
        'placeholder': '000000'
    }))

class PasswordlessLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control bg-dark text-white border-secondary',
        'placeholder': 'Enter registered email'
    }))

# --- VIEWS ---

def register(request):
    """Handles user registration and captures role selection."""
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save() 
            
            # Update the profile with the selected role from the POST data
            selected_role = request.POST.get('role')
            if selected_role:
                user.profile.role = selected_role
                user.profile.save()

            # Registration still uses OTP for email verification
            send_otp_email(user)
            messages.success(request, f'Account created! A verification OTP has been sent to {user.email}.')
            request.session['temp_user_id'] = user.id
            return redirect('verify_otp')
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})

def login_view(request):
    """Standard (Direct) and Passwordless (OTP) Login entry points."""
    form = AuthenticationForm()
    otp_login_form = PasswordlessLoginForm()

    if request.method == 'POST':
        login_type = request.POST.get('login_type') # From the hidden field in login.html

        # OPTION 1: Passwordless OTP Login Request
        if login_type == 'otp' or 'request_otp' in request.POST:
            otp_login_form = PasswordlessLoginForm(request.POST)
            if otp_login_form.is_valid():
                email = otp_login_form.cleaned_data.get('email')
                try:
                    user = User.objects.get(email=email)
                    send_otp_email(user)
                    request.session['temp_user_id'] = user.id
                    messages.info(request, "OTP sent for passwordless login.")
                    return redirect('verify_otp')
                except User.DoesNotExist:
                    messages.error(request, "No account found with this email.")
        
        # OPTION 2: Standard Username/Password Login (Direct Access)
        else:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                # LOG IN DIRECTLY: Skip OTP for password users
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                
                # Role-based redirection
                role = user.profile.role
                if role == 'Vendor':
                    return redirect('vendor_dashboard')
                elif role == 'Admin':
                    return redirect('/admin/')
                return redirect('product_list')
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, 'users/login.html', {
        'form': form, 
        'otp_login_form': otp_login_form
    })



def verify_otp(request):
    """Verifies OTP for Registration and Passwordless Login paths."""
    user_id = request.session.get('temp_user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = OTPform(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data.get('otp')
            if user.profile.otp == entered_otp:
                user.profile.is_verified = True
                user.profile.otp = None 
                user.profile.save()
                
                login(request, user)
                del request.session['temp_user_id']
                
                messages.success(request, f"Welcome, {user.username}!")

                role = user.profile.role
                if role == 'Vendor':
                    return redirect('vendor_dashboard')
                elif role == 'Admin':
                    return redirect('/admin/')
                
                return redirect('product_list')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
    else:
        form = OTPform()
    
    return render(request, 'users/verify_otp.html', {'form': form, 'user_email': user.email})

# --- REMAINDER OF VIEWS (Logout, Profile) UNCHANGED ---
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('product_list')

@login_required
def profile(request):
    return render(request, "users/profile.html")

@login_required
def profile_edit(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile updated!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, "users/profile_edit.html", {"u_form": u_form, "p_form": p_form})