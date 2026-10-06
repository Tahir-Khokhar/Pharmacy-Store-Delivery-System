import uuid
from django.utils import timezone
from .models import Payment, PaymentStatus

class PaymentService:
    """
    Payment abstraction layer. Supports Cash on Delivery and Online Payment Gateway mocking.
    Designed so Stripe / PayPal / Square can be plugged in without refactoring order flow.
    """
    @staticmethod
    def initialize_payment(order, payment_method):
        status = PaymentStatus.PENDING
        paid_at = None
        gateway_response = ""

        if payment_method == 'ONLINE':
            # Simulated instant digital gateway authorization
            status = PaymentStatus.PAID
            paid_at = timezone.now()
            gateway_response = f"Simulated Card Auth - AuthCode: {uuid.uuid4().hex[:12].upper()} - Status: APPROVED"

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.grand_total,
            status=status,
            paid_at=paid_at,
            gateway_response=gateway_response
        )
        return payment
