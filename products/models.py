from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True) 

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        # Always re-slugify on save to keep URLs in sync with name changes
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    #  Link product to a Vendor (User with Vendor role)
    vendor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="vendor_products",
        limit_choices_to={'profile__role': 'Vendor'},
        null=True,
        blank=True
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)

    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Standardized: Always re-slugify on name changes
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Review & Rating Module (Section 7 Database Design)
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        default=5, 
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.rating}-star review for {self.product.name}"