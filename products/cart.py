from decimal import Decimal
from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def __iter__(self):
        """
        Enables the cart to be used in loops: {% for item in cart %}.
        Fetches Product objects from the DB for display.
        """
        product_ids = self.cart.keys()
        # Fetch actual Product objects from DB
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Allows using {{ cart|length }} in templates."""
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'price': float(product.price), # Keep as float for JSON serialization
                'quantity': 0,
            }

        self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def get_total_items(self):
        return sum(
            item['quantity']
            for item in self.cart.values()
        )