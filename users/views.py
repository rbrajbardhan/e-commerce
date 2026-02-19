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

def send_otp_email(user):
    otp = str(random.randint(100000,999999))
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

def register(request):
    """Handles user registration and captures role selection."""
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user)
            messages.success(request, f"Welcome to ShopX, {user.username}! Your account has been created.")
            return redirect('product_list')
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})

def login_view(request):
    form = AuthenticationForm()
    otp_login_form = PasswordlessLoginForm()

    if request.method == 'POST':
        # OPTION 1: Passwordless OTP Login Request
        if 'request_otp' in request.POST:
            otp_login_form = PasswordlessLoginForm(request.POST)
            if otp_login_form.is_valid():
                email = otp_login_form.cleaned_data.get('email')
                try:
                    user = User.objects.get(email=email)
                    send_otp_email(user)
                    request.session['temp_user_id'] = user.id
                    messages.info(request, "OTP sent to your email for passwordless login.")
                    return redirect('verify_otp')
                except User.DoesNotExist:
                    messages.error(request, "No account found with this email.")
        
        # OPTION 2: Standard Username/Password Login
        else:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                
                if user is not None:
                    send_otp_email(user)
                    request.session['temp_user_id'] = user.id
                    messages.info(request, "Credentials verified. Please enter the OTP sent to your email.")
                    return redirect('verify_otp')
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, 'users/login.html', {
        'form': form, 
        'otp_login_form': otp_login_form
    })

# View to handle both Registration and Login OTP verification.
def verify_otp(request):
    user_id = request.session.get('temp_user_id')
    if not user_id:
        return redirect('login')
    
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = OTPform(request.POST)
        if form.is_valid():
            # Get user object directly from form to avoid AnonymousUser issues
            user = form.get_user()
            login(request, user)
            
            messages.success(request, f"Welcome back, {user.username}!")
            
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('product_list')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = OTPform()
    
    return render(request, 'users/verify_otp.html', {'form': form, 'user_email': user.email})



def logout_view(request):
    """Securely terminates user session."""
    logout(request)
    messages.info(request, "You have been safely logged out.")
    return redirect('product_list')


@login_required
def profile(request):
    """Displays user-specific profile data based on role."""
    return render(request, "users/profile.html")


@login_required
def profile_edit(request):
    """Simultaneously updates User and Profile models with error handling."""
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST,
            request.FILES, 
            instance=request.user.profile
        )

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Success! Your profile settings have been updated.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, "users/profile_edit.html", {
        "u_form": u_form,
        "p_form": p_form
    })