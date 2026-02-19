from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Order, OrderItem
from products.models import Product
from products.cart import Cart

@login_required
def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('product_list')

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'total_price': cart.get_total_price()
    })


@login_required
def place_order(request):
    if request.method != "POST":
        return redirect('checkout')

    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('product_list')

    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    address = request.POST.get('address')

    total_price = cart.get_total_price()

    try:
        with transaction.atomic():
            
            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                email=email,
                address=address,
                total_price=total_price,
                status='Pending',
                is_paid=False  
            )

            
            for item in cart:
                product = item['product']
                quantity = item['quantity']

                if product.stock < quantity:
                    
                    raise ValueError(f"Not enough stock for {product.name}.")

                # Create order items
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=item['price'],
                    quantity=quantity
                )

                # Update stock
                product.stock -= quantity
                product.save()

            cart.clear()

            messages.success(request, "Order placed successfully! Please proceed to payment.")
            return redirect('order_history')

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('cart')
    except Exception:
        messages.error(request, "An unexpected error occurred during checkout.")
        return redirect('cart')


@login_required
def order_history(request):
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {
        'orders': orders
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order
    })


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'Pending':
        messages.error(request, "Only pending orders can be cancelled.")
        return redirect('order_detail', order_id=order.id)

    with transaction.atomic():
        # Restore stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()

        order.status = 'Cancelled'
        order.save()

    messages.success(request, "Order cancelled. Stock has been restored.")
    return redirect('order_detail', order_id=order.id)