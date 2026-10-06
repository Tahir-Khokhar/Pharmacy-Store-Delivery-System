from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from apps.accounts.models import User, UserRole
from apps.accounts.permissions import admin_required, pharmacist_required
from apps.products.models import Product, Category
from apps.inventory.models import Batch, StockTransaction
from apps.orders.models import Order, OrderStatus
from apps.prescriptions.models import Prescription, PrescriptionStatus
from apps.deliveries.models import Delivery, DeliveryStatus
from apps.common.models import AuditLog

@login_required
def role_dashboard_router(request):
    """
    Intelligently routes users to their role-specific operational dashboard.
    """
    user = request.user
    if user.is_superuser or user.role == UserRole.ADMIN:
        return redirect('dashboard:admin_dashboard')
    elif user.role == UserRole.PHARMACIST:
        return redirect('dashboard:pharmacist')
    elif user.role == UserRole.INVENTORY_MANAGER:
        return redirect('inventory:list')
    elif user.role == UserRole.DELIVERY_STAFF:
        return redirect('deliveries:list')
    else:
        return redirect('dashboard:customer')


@admin_required
def admin_dashboard_view(request):
    """
    Executive management dashboard with financial metrics, order flows,
    and audit trail.
    """
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_customers = User.objects.filter(role=UserRole.CUSTOMER).count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status__in=[OrderStatus.PENDING, OrderStatus.PRESCRIPTION_REVIEW]).count()

    today_sales = Order.objects.filter(created_at__date=today, payment_status='PAID').aggregate(Sum('grand_total'))['grand_total__sum'] or Decimal('0.00')
    monthly_sales = Order.objects.filter(created_at__date__gte=month_start, payment_status='PAID').aggregate(Sum('grand_total'))['grand_total__sum'] or Decimal('0.00')

    low_stock_count = Product.objects.filter(stock_quantity__lte=F('min_stock_level'), stock_quantity__gt=0).count()
    expired_count = Batch.objects.filter(expiry_date__lte=today, current_quantity__gt=0).count()
    pending_prescriptions = Prescription.objects.filter(status=PrescriptionStatus.PENDING).count()
    pending_deliveries = Delivery.objects.filter(status=DeliveryStatus.PENDING).count()

    recent_orders = Order.objects.select_related('customer', 'delivery').order_by('-created_at')[:8]
    recent_audits = AuditLog.objects.select_related('user').order_by('-timestamp')[:8]

    # Order status breakdown
    status_counts = Order.objects.values('order_status').annotate(total=Count('id'))

    context = {
        'total_customers': total_customers,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'today_sales': today_sales,
        'monthly_sales': monthly_sales,
        'low_stock_count': low_stock_count,
        'expired_count': expired_count,
        'pending_prescriptions': pending_prescriptions,
        'pending_deliveries': pending_deliveries,
        'recent_orders': recent_orders,
        'recent_audits': recent_audits,
        'status_counts': status_counts,
    }
    return render(request, 'dashboard/admin.html', context)


@pharmacist_required
def pharmacist_dashboard_view(request):
    """
    Pharmacist clinical operations hub.
    Prioritizes prescriptions awaiting review and regulated medicine orders.
    """
    today = timezone.now().date()
    sixty_days = today + timezone.timedelta(days=60)

    pending_prescriptions = Prescription.objects.filter(
        status__in=[PrescriptionStatus.PENDING, PrescriptionStatus.UNDER_REVIEW]
    ).select_related('customer')[:10]

    orders_awaiting_rx = Order.objects.filter(
        requires_prescription=True,
        order_status__in=[OrderStatus.PENDING, OrderStatus.PRESCRIPTION_REVIEW]
    ).select_related('customer', 'prescription')[:10]

    expiring_medicines = Batch.objects.filter(
        expiry_date__gt=today,
        expiry_date__lte=sixty_days,
        current_quantity__gt=0
    ).select_related('product')[:8]

    low_stock_medicines = Product.objects.filter(
        stock_quantity__lte=F('min_stock_level'),
        stock_quantity__gt=0
    )[:8]

    today_orders_count = Order.objects.filter(created_at__date=today).count()

    context = {
        'pending_prescriptions': pending_prescriptions,
        'pending_rx_count': pending_prescriptions.count(),
        'orders_awaiting_rx': orders_awaiting_rx,
        'expiring_medicines': expiring_medicines,
        'low_stock_medicines': low_stock_medicines,
        'today_orders_count': today_orders_count,
    }
    return render(request, 'dashboard/pharmacist.html', context)


@login_required
def customer_dashboard_view(request):
    """
    Customer portal with quick stats, recent orders, prescription status,
    and profile shortcuts.
    """
    user = request.user
    recent_orders = Order.objects.filter(customer=user).select_related('delivery')[:5]
    total_orders_count = Order.objects.filter(customer=user).count()
    pending_orders_count = Order.objects.filter(customer=user).exclude(order_status__in=[OrderStatus.DELIVERED, OrderStatus.CANCELLED]).count()
    delivered_orders_count = Order.objects.filter(customer=user, order_status=OrderStatus.DELIVERED).count()
    prescriptions_count = Prescription.objects.filter(customer=user).count()
    approved_rx_count = Prescription.objects.filter(customer=user, status=PrescriptionStatus.APPROVED).count()

    context = {
        'recent_orders': recent_orders,
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'delivered_orders_count': delivered_orders_count,
        'prescriptions_count': prescriptions_count,
        'approved_rx_count': approved_rx_count,
    }
    return render(request, 'dashboard/customer.html', context)
