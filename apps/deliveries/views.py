from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from apps.accounts.permissions import delivery_staff_required
from apps.common.utils import log_audit_action
from apps.notifications.models import Notification, NotificationType
from apps.orders.models import OrderStatus
from .models import Delivery, DeliveryStatus

@delivery_staff_required
def delivery_list_view(request):
    """
    Dedicated dashboard for delivery couriers and dispatch managers.
    """
    user = request.user
    if user.is_admin_user():
        deliveries = Delivery.objects.all().select_related('order', 'order__customer', 'delivery_staff')
    else:
        # Show assigned to current courier OR unassigned pending
        deliveries = Delivery.objects.filter(
            models.Q(delivery_staff=user) | models.Q(delivery_staff__isnull=True)
        ).select_related('order', 'order__customer', 'delivery_staff')

    # Metrics
    today = timezone.now().date()
    assigned_count = deliveries.filter(delivery_staff=user, status=DeliveryStatus.ASSIGNED).count()
    out_for_delivery_count = deliveries.filter(delivery_staff=user, status=DeliveryStatus.OUT_FOR_DELIVERY).count()
    completed_today_count = deliveries.filter(delivery_staff=user, status=DeliveryStatus.DELIVERED, delivered_at__date=today).count()
    pending_dispatch_count = Delivery.objects.filter(status=DeliveryStatus.PENDING).count()

    return render(request, 'deliveries/delivery_list.html', {
        'deliveries': deliveries,
        'assigned_count': assigned_count,
        'out_for_delivery_count': out_for_delivery_count,
        'completed_today_count': completed_today_count,
        'pending_dispatch_count': pending_dispatch_count,
    })


@delivery_staff_required
def delivery_detail_view(request, tracking_number):
    delivery = get_object_or_404(
        Delivery.objects.select_related('order', 'order__customer', 'delivery_staff'),
        tracking_number=tracking_number
    )
    return render(request, 'deliveries/delivery_detail.html', {'delivery': delivery})


@delivery_staff_required
@require_POST
def delivery_update_status(request, tracking_number):
    """
    Courier status transition logic:
    PENDING -> ASSIGNED -> PICKED_UP -> OUT_FOR_DELIVERY -> DELIVERED / FAILED
    """
    delivery = get_object_or_404(Delivery, tracking_number=tracking_number)
    new_status = request.POST.get('status')
    notes = request.POST.get('delivery_notes', '')
    recipient_name = request.POST.get('recipient_name', '')

    # Assign action
    if new_status == DeliveryStatus.ASSIGNED:
        delivery.delivery_staff = request.user
        delivery.assigned_at = timezone.now()
        delivery.status = DeliveryStatus.ASSIGNED
        messages.success(request, f"Delivery #{delivery.tracking_number} assigned to you.")
    
    elif new_status == DeliveryStatus.PICKED_UP:
        delivery.status = DeliveryStatus.PICKED_UP
        delivery.picked_up_at = timezone.now()
        delivery.order.order_status = OrderStatus.PACKED
        delivery.order.save(update_fields=['order_status'])
        messages.info(request, f"Order #{delivery.order.order_number} marked as picked up from pharmacy.")

    elif new_status == DeliveryStatus.OUT_FOR_DELIVERY:
        delivery.status = DeliveryStatus.OUT_FOR_DELIVERY
        delivery.out_for_delivery_at = timezone.now()
        delivery.order.order_status = OrderStatus.OUT_FOR_DELIVERY
        delivery.order.save(update_fields=['order_status'])
        
        Notification.objects.create(
            user=delivery.order.customer,
            title="Order Out for Delivery",
            message=f"Courier {request.user.get_full_name() or request.user.username} is on the way with order #{delivery.order.order_number}.",
            notification_type=NotificationType.ORDER_SHIPPED
        )
        messages.info(request, f"Order #{delivery.order.order_number} is now Out for Delivery.")

    elif new_status == DeliveryStatus.DELIVERED:
        delivery.status = DeliveryStatus.DELIVERED
        delivery.delivered_at = timezone.now()
        delivery.recipient_name = recipient_name or delivery.order.customer.get_full_name()
        delivery.order.order_status = OrderStatus.DELIVERED
        # If payment is COD, mark as paid upon delivery
        if delivery.order.payment_method == 'COD':
            delivery.order.payment_status = 'PAID'
            if hasattr(delivery.order, 'payment'):
                delivery.order.payment.mark_as_paid(gateway_note="Cash collected by courier upon delivery")
        delivery.order.save()

        Notification.objects.create(
            user=delivery.order.customer,
            title="Order Delivered",
            message=f"Order #{delivery.order.order_number} has been delivered successfully. Thank you for choosing PharmaCare!",
            notification_type=NotificationType.ORDER_DELIVERED
        )
        messages.success(request, f"Delivery #{delivery.tracking_number} completed successfully!")

    elif new_status == DeliveryStatus.FAILED:
        delivery.status = DeliveryStatus.FAILED
        messages.warning(request, f"Delivery marked as failed.")

    if notes:
        delivery.delivery_notes = notes
    delivery.save()

    log_audit_action(
        request.user, 'STATUS_CHANGE', 'Delivery', delivery.id,
        f"Delivery #{delivery.tracking_number} updated to {delivery.status} by {request.user.username}",
        request
    )

    return redirect('deliveries:detail', tracking_number=delivery.tracking_number)
