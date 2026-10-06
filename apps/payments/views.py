from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.permissions import admin_required
from apps.common.utils import log_audit_action
from .models import Payment, PaymentStatus

@admin_required
def payment_list_view(request):
    payments = Payment.objects.all().select_related('order', 'order__customer')
    return render(request, 'dashboard/payments.html', {'payments': payments})


@admin_required
def payment_detail_view(request, pk):
    payment = get_object_or_404(Payment.objects.select_related('order', 'order__customer'), pk=pk)
    return render(request, 'dashboard/payment_detail.html', {'payment': payment})


@admin_required
def payment_mark_paid_action(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.mark_as_paid(gateway_note=f"Confirmed manually by {request.user.username}")
    log_audit_action(request.user, 'PAYMENT', 'Payment', payment.id, f"Marked payment #{payment.transaction_id} as PAID", request)
    messages.success(request, f"Payment #{payment.transaction_id} marked as PAID.")
    return redirect('dashboard:admin_dashboard')
