from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum

from .models import Product, Category, Review
from .cart import Cart
from .forms import ReviewForm, ProductForm
from orders.models import OrderItem

# --- PERMISSION DECORATOR ---

def vendor_required(function):
    """Custom decorator to restrict access to users with the Vendor role."""
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.role == 'Vendor':
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "Access denied. Vendor account required.")
            return redirect('product_list')
    return wrap

# --- PUBLIC CATALOG VIEWS ---

def product_list(request):
    """Displays available products with category and search filtering."""
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    category_slug = request.GET.get("category")
    query = request.GET.get("q")

    if category_slug:
        products = products.filter(category__slug=category_slug)

    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    context = {
        "products": products,
        "categories": categories
    }
    return render(request, "products/product_list.html", context)

def product_detail(request, slug):
    """Displays product details and handles review submissions."""
    product = get_object_or_404(Product, slug=slug, available=True)
    reviews = product.reviews.all().order_by('-created_at')
    
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to leave a review.")
            return redirect('login')
            
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Review posted successfully!")
            return redirect('product_detail', slug=slug)
    else:
        form = ReviewForm()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'user_review': user_review
    })

# --- WISHLIST MODULE ---

@login_required
def toggle_wishlist(request, product_id):
    """AJAX view to add or remove a product from the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)
    profile = request.user.profile
    
    if product in profile.wishlist.all():
        profile.wishlist.remove(product)
        added = False
        message = f"{product.name} removed from wishlist."
    else:
        profile.wishlist.add(product)
        added = True
        message = f"{product.name} added to wishlist."
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'added': added,
            'message': message
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def wishlist_view(request):
    """Displays the user's saved items."""
    wishlist_items = request.user.profile.wishlist.all()
    return render(request, 'products/wishlist.html', {
        'wishlist_items': wishlist_items
    })

# --- CART OPERATIONS ---

def add_to_cart(request, product_id):
    """Handles cart additions via AJAX or standard Redirect."""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock < 1:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Out of stock'}, status=400)
        messages.error(request, "Sorry, this item is out of stock.")
        return redirect('product_list')

    cart.add(product)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} added to cart!',
            'cart_count': cart.get_total_items()
        })
    
    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart')

def cart_view(request):
    """Displays cart contents."""
    cart = Cart(request)
    return render(request, 'products/cart.html', {
        'cart': cart,
        'total_price': cart.get_total_price()
    })

def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"{product.name} removed from your collection.")
    return redirect('cart')

def update_cart(request, product_id):
    if request.method == "POST":
        try:
            quantity = int(request.POST.get("quantity", 1))
            cart = Cart(request)
            product = get_object_or_404(Product, id=product_id)
            
            if 0 < quantity <= product.stock:
                cart.update(product, quantity)
                messages.success(request, "Quantity updated.")
            else:
                messages.error(request, f"Invalid quantity or exceeds stock ({product.stock}).")
        except ValueError:
            messages.error(request, "Invalid input.")
    return redirect('cart')

# --- VENDOR MODULE ---

@vendor_required
def vendor_dashboard(request):
    """
    Dashboard for vendors with database-level revenue aggregation.
    Orders products by most recent to ensure new data appears at the top.
    """
    my_products = Product.objects.filter(vendor=request.user).order_by('-id')
    my_sales = OrderItem.objects.filter(product__vendor=request.user)
    
    # Calculate revenue using Sum and F expressions for efficiency
    stats = my_sales.aggregate(
        total_revenue=Sum(F('price') * F('quantity'))
    )
    total_revenue = stats['total_revenue'] or 0

    return render(request, 'products/vendor_dashboard.html', {
        'products': my_products,
        'total_revenue': total_revenue,
        'sales_count': my_sales.count()
    })

@vendor_required
def vendor_add_product(request):
    """Vendor-facing form to add new inventory. Automatically sets product to available."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.available = True  # AUTOMATICALLY SET VISIBILITY
            product.save()
            messages.success(request, f"Product '{product.name}' listed successfully!")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'products/vendor_product_form.html', {
        'form': form, 
        'title': 'Add New Product'
    })

@vendor_required
def vendor_edit_product(request, slug):
    """Vendor-facing form to edit their own inventory."""
    product = get_object_or_404(Product, slug=slug, vendor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.available = True # ENSURE EDITED PRODUCTS REMAIN VISIBLE
            product.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/vendor_product_form.html', {
        'form': form, 
        'title': 'Edit Product'
    })

@vendor_required
def vendor_delete_product(request, slug):
    """Secure deletion of vendor-owned products."""
    product = get_object_or_404(Product, slug=slug, vendor=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product removed from your inventory.")
        return redirect('vendor_dashboard')
    return render(request, 'products/vendor_confirm_delete.html', {'product': product})