from django.urls import path
from . import views

urlpatterns = [
    # Public Catalog
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Shopping Cart
    path('cart/', views.cart_view, name='cart'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),

    # Wishlist Module 
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Vendor Module
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/add-product/', views.vendor_add_product, name='vendor_add_product'),
    path('vendor/edit-product/<slug:slug>/', views.vendor_edit_product, name='vendor_edit_product'),
    path('vendor/delete-product/<slug:slug>/', views.vendor_delete_product, name='vendor_delete_product'),
]