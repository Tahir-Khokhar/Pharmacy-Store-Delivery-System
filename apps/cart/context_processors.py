from .models import Cart

def cart_context(request):
    """
    Supplies cart counts and prescription check to all templates.
    Handles both logged-in users and guest sessions.
    """
    total_items = 0
    grand_total = 0
    has_rx = False
    
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if cart:
        total_items = cart.total_items
        grand_total = cart.grand_total
        has_rx = cart.has_prescription_items

    # Wishlist count
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = request.user.wishlist_items.count()

    return {
        'cart_total_items': total_items,
        'cart_grand_total': grand_total,
        'cart_has_prescription_items': has_rx,
        'wishlist_count': wishlist_count,
    }
