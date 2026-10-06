from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, models
from django.utils import timezone
from apps.accounts.permissions import inventory_manager_required
from apps.common.utils import log_audit_action
from apps.products.models import Product
from .models import Batch, StockTransaction, TransactionType, BatchStatus
from .forms import BatchForm, StockAdjustmentForm

@inventory_manager_required
def inventory_list_view(request):
    """
    Inventory dashboard view displaying stock levels, alerts, and batch expiries.
    """
    tab = request.GET.get('tab', 'all')
    products = Product.objects.all().select_related('category').prefetch_related('batches')
    
    today = timezone.now().date()
    sixty_days = today + timezone.timedelta(days=60)
    
    total_products = products.count()
    low_stock_products = products.filter(stock_quantity__lte=models.F('min_stock_level'), stock_quantity__gt=0)
    out_of_stock_products = products.filter(stock_quantity=0)
    expiring_soon_batches = Batch.objects.filter(expiry_date__gt=today, expiry_date__lte=sixty_days, current_quantity__gt=0)
    expired_batches = Batch.objects.filter(expiry_date__lte=today, current_quantity__gt=0)
    
    if tab == 'low_stock':
        products = low_stock_products
    elif tab == 'out_of_stock':
        products = out_of_stock_products
    elif tab == 'expiring':
        products = products.filter(batches__in=expiring_soon_batches).distinct()
    elif tab == 'expired':
        products = products.filter(batches__in=expired_batches).distinct()
        
    recent_transactions = StockTransaction.objects.select_related('product', 'performed_by')[:10]

    context = {
        'products': products,
        'active_tab': tab,
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'out_of_stock_count': out_of_stock_products.count(),
        'expiring_soon_count': expiring_soon_batches.count(),
        'expired_count': expired_batches.count(),
        'expiring_soon_batches': expiring_soon_batches,
        'expired_batches': expired_batches,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'dashboard/inventory.html', context)


@inventory_manager_required
def stock_adjust_view(request):
    """
    Safely adjusts product inventory with transactional integrity and audit logs.
    """
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            batch = form.cleaned_data['batch']
            txn_type = form.cleaned_data['transaction_type']
            qty = form.cleaned_data['quantity']
            ref = form.cleaned_data['reference']
            notes = form.cleaned_data['notes']

            with transaction.atomic():
                prev_stock = product.stock_quantity
                new_stock = prev_stock + qty
                if new_stock < 0:
                    messages.error(request, f"Cannot reduce stock below 0. Current stock is {prev_stock}.")
                    return render(request, 'dashboard/stock_adjust.html', {'form': form})

                product.stock_quantity = new_stock
                product.save()

                if batch:
                    batch.current_quantity = max(0, batch.current_quantity + qty)
                    batch.save()

                StockTransaction.objects.create(
                    product=product,
                    batch=batch,
                    transaction_type=txn_type,
                    quantity=qty,
                    previous_stock=prev_stock,
                    new_stock=new_stock,
                    reference=ref,
                    notes=notes,
                    performed_by=request.user
                )

                log_audit_action(
                    request.user, 'STOCK_ADJUST', 'Product', product.id,
                    f"Stock adjusted by {qty} ({txn_type}). New stock: {new_stock}", request
                )

                messages.success(request, f"Stock updated for {product.name}. New total: {new_stock}")
                return redirect('inventory:list')
    else:
        product_id = request.GET.get('product_id')
        initial = {}
        if product_id:
            initial['product'] = product_id
        form = StockAdjustmentForm(initial=initial)

    return render(request, 'dashboard/stock_adjust.html', {'form': form})


@inventory_manager_required
def batch_create_view(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save()
            # Also increase product stock by initial quantity
            with transaction.atomic():
                prod = batch.product
                prev_stock = prod.stock_quantity
                prod.stock_quantity = prev_stock + batch.initial_quantity
                prod.batch_number = batch.batch_number
                prod.expiry_date = batch.expiry_date
                prod.save()

                StockTransaction.objects.create(
                    product=prod,
                    batch=batch,
                    transaction_type=TransactionType.PURCHASE,
                    quantity=batch.initial_quantity,
                    previous_stock=prev_stock,
                    new_stock=prod.stock_quantity,
                    reference=f"New Batch #{batch.batch_number}",
                    performed_by=request.user
                )
            messages.success(request, f"Batch {batch.batch_number} recorded for {prod.name}.")
            return redirect('inventory:list')
    else:
        form = BatchForm()
    return render(request, 'dashboard/batch_form.html', {'form': form})
