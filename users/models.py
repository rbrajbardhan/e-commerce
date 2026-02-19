from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import random

class Profile(models.Model):
    # Role-based access (Admin, Vendor, Customer)
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Vendor', 'Vendor'),
        ('Customer', 'Customer'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='Customer'
    )

    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    wishlist = models.ManyToManyField('products.Product', blank=True, related_name='wishlisted_by')

    # OTP and Verification fields..

    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    # Helper properties for easy role checking in views/templates
    @property
    def is_vendor(self):
        return self.role == 'Vendor'

    @property
    def is_customer(self):
        return self.role == 'Customer'
    
    # OTP Generation
    def generate_otp(self):
        self.otp = str(random.randint(100000,999999))
        self.save()
        return self.otp 

# --- CONSOLIDATED SIGNALS ---

@receiver(post_save, sender=User, dispatch_uid='manage_user_profile_signal')
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        # Using get_or_create to prevent IntegrityErrors if a profile was somehow created via another process (like admin)
        Profile.objects.get_or_create(user=instance)
    else:
        # Only save the profile if it already exists
        if hasattr(instance, 'profile'):
            instance.profile.save()