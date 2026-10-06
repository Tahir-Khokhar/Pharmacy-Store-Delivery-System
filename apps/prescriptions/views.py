from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from apps.accounts.permissions import pharmacist_required
from apps.common.utils import log_audit_action
from apps.notifications.models import Notification, NotificationType
from .models import Prescription, PrescriptionStatus
from .forms import PrescriptionUploadForm, PrescriptionReviewForm

@login_required
def prescription_list_view(request):
    """
    Shows prescriptions uploaded by the logged-in customer.
    Staff/pharmacists can also toggle into view.
    """
    if request.user.is_pharmacist() or request.user.is_admin_user():
        prescriptions = Prescription.objects.all().select_related('customer', 'verified_by')
    else:
        prescriptions = Prescription.objects.filter(customer=request.user).select_related('verified_by')

    return render(request, 'prescriptions/prescription_list.html', {
        'prescriptions': prescriptions,
        'is_staff_view': request.user.is_pharmacist() or request.user.is_admin_user()
    })


@login_required
def prescription_upload_view(request):
    """
    Allows customers to safely upload prescription documents (PDF, JPG, PNG).
    """
    if request.method == 'POST':
        form = PrescriptionUploadForm(request.POST, request.FILES)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.customer = request.user
            prescription.status = PrescriptionStatus.PENDING
            prescription.save()

            log_audit_action(
                request.user, 'CREATE', 'Prescription', prescription.id,
                f"Uploaded prescription {prescription.prescription_number}", request
            )

            # Internal notification for user
            Notification.objects.create(
                user=request.user,
                title="Prescription Uploaded",
                message=f"Prescription {prescription.prescription_number} received. A licensed pharmacist will verify it shortly.",
                notification_type=NotificationType.ORDER_PLACED
            )

            messages.success(request, f"Prescription {prescription.prescription_number} uploaded successfully! Our pharmacist will review it.")
            return redirect('prescriptions:detail', pk=prescription.pk)
    else:
        form = PrescriptionUploadForm()

    return render(request, 'prescriptions/prescription_upload.html', {'form': form})


@login_required
def prescription_detail_view(request, pk):
    """
    Detailed review of a prescription document and clinical status.
    """
    if request.user.is_pharmacist() or request.user.is_admin_user():
        prescription = get_object_or_404(Prescription, pk=pk)
    else:
        prescription = get_object_or_404(Prescription, pk=pk, customer=request.user)

    review_form = None
    if request.user.is_pharmacist() or request.user.is_admin_user():
        review_form = PrescriptionReviewForm(instance=prescription)

    return render(request, 'prescriptions/prescription_detail.html', {
        'prescription': prescription,
        'review_form': review_form,
        'can_review': request.user.is_pharmacist() or request.user.is_admin_user()
    })


@pharmacist_required
def prescription_review_action(request, pk):
    """
    Pharmacist action to approve or reject a prescription with clinical justification.
    """
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.method == 'POST':
        form = PrescriptionReviewForm(request.POST, instance=prescription)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.verified_by = request.user
            prescription.verified_at = timezone.now()
            prescription.save()

            action_type = 'APPROVE' if prescription.status == PrescriptionStatus.APPROVED else 'REJECT'
            log_audit_action(
                request.user, action_type, 'Prescription', prescription.id,
                f"Prescription {prescription.prescription_number} set to {prescription.status} by Pharmacist {request.user.username}",
                request
            )

            # Notify customer
            if prescription.status == PrescriptionStatus.APPROVED:
                Notification.objects.create(
                    user=prescription.customer,
                    title="Prescription Approved",
                    message=f"Your prescription {prescription.prescription_number} was approved by Pharmacist {request.user.get_full_name() or request.user.username}. Your orders can now be processed.",
                    notification_type=NotificationType.PRESCRIPTION_APPROVED
                )
                messages.success(request, f"Prescription {prescription.prescription_number} approved successfully.")
            elif prescription.status == PrescriptionStatus.REJECTED:
                Notification.objects.create(
                    user=prescription.customer,
                    title="Prescription Rejected",
                    message=f"Prescription {prescription.prescription_number} was rejected. Reason: {prescription.rejection_reason}",
                    notification_type=NotificationType.PRESCRIPTION_REJECTED
                )
                messages.warning(request, f"Prescription {prescription.prescription_number} marked as rejected.")

            return redirect('prescriptions:detail', pk=prescription.pk)
        else:
            messages.error(request, "Please fix the form errors.")
            return render(request, 'prescriptions/prescription_detail.html', {
                'prescription': prescription,
                'review_form': form,
                'can_review': True
            })

    return redirect('prescriptions:detail', pk=prescription.pk)
