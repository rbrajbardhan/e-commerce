from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order
from users.models import Profile


User = get_user_model()


def staff_required(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(staff_required)
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    # Count vendors using Profile role system
    total_vendors = Profile.objects.filter(role='Vendor').count()

    # Extra professional stats (optional but useful)
    pending_orders = Order.objects.filter(status='Pending').count()
    completed_orders = Order.objects.filter(status='Completed').count()

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_vendors': total_vendors,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
    }

    return render(request, 'admin/admin.html', context)