from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    # More granular tracking for the Order Module
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # Shipping Details
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # Payment Management Module integration
    is_paid = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='COD') # e.g., Stripe, PayPal, COD

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    # We store the price at the time of purchase to protect against future price changes
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    def get_total_price(self):
        return self.price * self.quantity