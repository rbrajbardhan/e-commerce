from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    UserRegisterForm,
    UserLoginForm,
    UserUpdateForm,
    ProfileUpdateForm
)

def register(request):
    """Handles user registration and captures role selection."""
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save() 
            
            selected_role = form.cleaned_data.get('role')
            if selected_role:
                user.profile.role = selected_role
                user.profile.save()

            login(request, user)
            messages.success(request, f"Welcome to ShopX, {user.username}!")
            
            if selected_role == 'Vendor':
                return redirect('vendor_dashboard')
            return redirect('product_list')
    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """Handles secure login and redirects based on SRS role requirements."""
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            messages.success(request, f"Welcome back, {user.username}!")
            
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            role = user.profile.role
            if role == 'Vendor':
                return redirect('vendor_dashboard')
            elif role == 'Admin':
                return redirect('/admin/') 
            
            return redirect('product_list')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, "users/login.html", {"form": form})


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