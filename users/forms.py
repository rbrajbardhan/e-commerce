from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    """
    Form for user registration including email and role selection.
    Styled with 'form-control' classes for glassmorphism compatibility.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'})
    )
    
    # Defining the role choice field for backend validation
    role = forms.ChoiceField(
        choices=[('Customer', 'Customer'), ('Vendor', 'Vendor')],
        required=True,
        initial='Customer',
        widget=forms.Select(attrs={'class': 'form-select'}) # Matches your custom dropdown styling
    )

    class Meta:
        model = User
        # Fields must include 'role' to be captured in the cleaned_data
        fields = ['username', 'email', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Applying 'form-control' to all fields dynamically for consistent UI
        for field in self.fields.values():
            if not isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-control'})

class UserLoginForm(AuthenticationForm):
    """
    Standard login form used to verify credentials before the OTP gate.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class UserUpdateForm(forms.ModelForm):
    """Updates basic User model information (Username/Email)."""
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ProfileUpdateForm(forms.ModelForm):
    """Updates extended Profile model information including imagery."""
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'profile_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})