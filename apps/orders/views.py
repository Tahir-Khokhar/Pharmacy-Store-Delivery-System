from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from apps.cart.views import get_or_create_cart
from apps.accounts.models import Address
from apps.accounts.permissions import role_required, pharmacist_required
from apps.common.utils import log_audit_action
from apps.notifications.models import Notification, NotificationType
from .models import Order, OrderStatus
from .forms import CheckoutForm, OrderStatusUpdateForm
from .services import OrderService, OrderProcessingError

@login_required
def checkout_view(request):
    """
    Five-step checkout workflow with real-time price recalculation,
    prescription validation, and atomic database execution.
    """
    cart = get_or_create_cart(request)
    if cart.items.count() == 0:
        messages.warning(request, "Your cart is empty. Add medicines to proceed.")
        return redirect('products:product_list')

    addresses = Address.objects.filter(user=request.user)
    if not addresses.exists():
        messages.info(request, "Please add a delivery address before completing your checkout.")
        return redirect('accounts:addresses')

    user_prescriptions = request.user.prescriptions.all()
    has_prescription_items = cart.has_prescription_items

    if request.method == 'POST':
        form = CheckoutForm(request.user, request.POST)
        if form.is_valid():
            address = form.cleaned_data['shipping_address']
            payment_method = form.cleaned_data['payment_method']
            prescription = form.cleaned_data['prescription']
            notes = form.cleaned_data['customer_notes']

            try:
                order = OrderService.process_checkout(
                    user=request.user,
                    cart=cart,
                    shipping_address=address,
                    payment_method=payment_method,
                    prescription=prescription,
                    customer_notes=notes,
                    request=request
                )
                messages.success(request, f"Order #{order.order_number} placed successfully!")
                return redirect('orders:confirmation', order_number=order.order_number)
            except OrderProcessingError as exc:
                messages.error(request, str(exc))
        else:
            messages.error(request, "Please review the checkout options and address selected.")
    else:
        # Pre-select default address
        default_addr = addresses.filter(is_default=True).first() or addresses.first()
        initial = {'shipping_address': default_addr}
        # Pre-select approved prescription if available
        approved_rx = user_prescriptions.filter(status='APPROVED').first()
        if approved_rx:
            initial['prescription'] = approved_rx
        form = CheckoutForm(request.user, initial=initial)

    return render(request, 'cart/checkout.html', {
        'form': form,
        'cart': cart,
        'addresses': addresses,
        'prescriptions': user_prescriptions,
        'has_prescription_items': has_prescription_items,
    })


@login_required
def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_list_view(request):
    """
    Customer's order history. Staff can see all orders or filtered orders.
    """
    if request.user.is_staff or request.user.is_pharmacist() or request.user.is_admin_user():
        orders = Order.objects.all().select_related('customer', 'delivery')
    else:
        orders = Order.objects.filter(customer=request.user).select_related('delivery')

    return render(request, 'orders/order_list.html', {
        'orders': orders,
        'is_staff_view': request.user.is_staff or request.user.is_pharmacist() or request.user.is_admin_user()
    })


@login_required
def order_detail_view(request, order_number):
    if request.user.is_staff or request.user.is_pharmacist() or request.user.is_admin_user() or request.user.is_delivery_staff():
        order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_number=order_number)
    else:
        order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_number=order_number, customer=request.user)

    can_manage_status = request.user.is_pharmacist() or request.user.is_admin_user() or request.user.is_staff
    status_form = OrderStatusUpdateForm(initial={'order_status': order.order_status, 'staff_notes': order.staff_notes}) if can_manage_status else None

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'status_form': status_form,
        'can_manage_status': can_manage_status
    })


@login_required
def order_invoice_view(request, order_number):
    """
    Printable pharmacy invoice & receipt.
    """
    if request.user.is_staff or request.user.is_admin_user():
        order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_number=order_number)
    else:
        order = get_object_or_404(Order.objects.prefetch_related('items__product'), order_number=order_number, customer=request.user)

    return render(request, 'orders/invoice.html', {'order': order})


@login_required
@require_POST
def cancel_order_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, customer=request.user)
    if not order.can_be_cancelled:
        messages.error(request, "This order is already being packed or delivered and cannot be cancelled online.")
        return redirect('orders:detail', order_number=order.order_number)

    order.order_status = OrderStatus.CANCELLED
    order.save()
    log_audit_action(request.user, 'STATUS_CHANGE', 'Order', order.id, f"Order #{order.order_number} cancelled by customer", request)
    messages.info(request, f"Order #{order.order_number} has been cancelled.")
    return redirect('orders:detail', order_number=order.order_number)


@login_required
@require_POST
def update_order_status_view(request, order_number):
    """
    Staff / Pharmacist action to advance order status.
    """
    if not (request.user.is_pharmacist() or request.user.is_admin_user() or request.user.is_staff):
        raise PermissionDenied("Only authorized staff can alter order status.")

    order = get_object_or_404(Order, order_number=order_number)
    form = OrderStatusUpdateForm(request.POST)
    if form.is_valid():
        old_status = order.order_status
        new_status = form.cleaned_data['order_status']
        notes = form.cleaned_data['staff_notes']

        # Enforce prescription rule: Order cannot be PROCESSING or CONFIRMED if Rx required and not approved
        if new_status in [OrderStatus.PROCESSING, OrderStatus.PACKED, OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED]:
            if order.requires_prescription and not order.prescription_satisfied:
                messages.error(request, "Compliance Rule: You cannot advance this order beyond review without an approved prescription!")
                return redirect('orders:detail', order_number=order.order_number)

        order.order_status = new_status
        if notes:
            order.staff_notes = notes
        order.save()

        log_audit_action(
            request.user, 'STATUS_CHANGE', 'Order', order.id,
            f"Order #{order.order_number} status changed from {old_status} to {new_status} by {request.user.username}",
            request
        )

        # Notify customer
        Notification.objects.create(
            user=order.customer,
            title=f"Order Update #{order.order_number}",
            message=f"Your order is now: {order.get_order_status_display()}.",
            notification_type=NotificationType.ORDER_PROCESSING
        )

        messages.success(request, f"Order #{order.order_number} updated to {order.get_order_status_display()}.")

    return redirect('orders:detail', order_number=order.order_number)
