from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.products.models import Product
from .models import Cart, CartItem

def get_or_create_cart(request):
    """
    Helper to get or create the current active cart for the session or user.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # Migrate guest cart if exists
        if request.session.session_key:
            guest_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if guest_cart and guest_cart != cart:
                for item in guest_cart.items.all():
                    existing = CartItem.objects.filter(cart=cart, product=item.product).first()
                    if existing:
                        existing.quantity += item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                guest_cart.delete()
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart


def cart_detail_view(request):
    """
    Displays the shopping cart with line items, stock validation, and price totals.
    """
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product', 'product__category')
    
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart_ajax(request):
    """
    AJAX endpoint to add medicines to cart with server-side stock validation.
    """
    product_id = request.POST.get('product_id')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        return JsonResponse({'success': False, 'message': 'Invalid quantity'}, status=400)

    product = get_object_or_404(Product, pk=product_id, active=True)

    # Server-side stock validation
    cart = get_or_create_cart(request)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()
    current_in_cart = cart_item.quantity if cart_item else 0
    total_requested = current_in_cart + quantity

    if total_requested > product.stock_quantity:
        available = max(0, product.stock_quantity - current_in_cart)
        return JsonResponse({
            'success': False,
            'message': f"Insufficient stock for {product.name}. You already have {current_in_cart} in cart and only {product.stock_quantity} are available in inventory."
        }, status=400)

    if cart_item:
        cart_item.quantity = total_requested
        cart_item.save()
    else:
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)

    return JsonResponse({
        'success': True,
        'message': f"{product.name} ({quantity}x) added to cart.",
        'total_items': cart.total_items,
        'subtotal': str(cart.subtotal),
        'grand_total': str(cart.grand_total),
        'has_prescription': cart.has_prescription_items,
    })


@require_POST
def update_cart_item_ajax(request):
    """
    Updates the quantity of an item in the cart.
    """
    item_id = request.POST.get('item_id')
    try:
        new_quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        new_quantity = 1

    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    if new_quantity <= 0:
        item.delete()
        item_subtotal = '0.00'
        message = f"Removed {item.product.name} from cart."
    else:
        if new_quantity > item.product.stock_quantity:
            return JsonResponse({
                'success': False,
                'message': f"Cannot set quantity to {new_quantity}. Only {item.product.stock_quantity} available in inventory."
            }, status=400)
        item.quantity = new_quantity
        item.save()
        item_subtotal = str(item.item_subtotal)
        message = f"Updated {item.product.name} quantity to {new_quantity}."

    return JsonResponse({
        'success': True,
        'message': message,
        'item_id': item_id,
        'quantity': new_quantity,
        'item_subtotal': item_subtotal,
        'total_items': cart.total_items,
        'subtotal': str(cart.subtotal),
        'tax_total': str(cart.tax_total),
        'delivery_fee': str(cart.delivery_fee),
        'grand_total': str(cart.grand_total),
        'has_prescription': cart.has_prescription_items,
    })


@require_POST
def remove_cart_item_ajax(request):
    """
    Removes a line item from the cart.
    """
    item_id = request.POST.get('item_id')
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    product_name = item.product.name
    item.delete()

    return JsonResponse({
        'success': True,
        'message': f"{product_name} removed from your cart.",
        'total_items': cart.total_items,
        'subtotal': str(cart.subtotal),
        'tax_total': str(cart.tax_total),
        'delivery_fee': str(cart.delivery_fee),
        'grand_total': str(cart.grand_total),
        'has_prescription': cart.has_prescription_items,
    })


@require_POST
def clear_cart_view(request):
    """
    Empties the customer's cart.
    """
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.info(request, "Your cart has been cleared.")
    return redirect('cart:cart_detail')
