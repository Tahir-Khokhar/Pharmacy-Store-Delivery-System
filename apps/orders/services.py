from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.common.utils import log_audit_action
from apps.inventory.models import StockTransaction, TransactionType
from apps.payments.services import PaymentService
from apps.payments.models import PaymentStatus
from apps.deliveries.models import Delivery, DeliveryStatus
from apps.notifications.models import Notification, NotificationType
from .models import Order, OrderItem, OrderStatus, PaymentMethod

class OrderProcessingError(Exception):
    pass

class OrderService:
    @staticmethod
    def process_checkout(user, cart, shipping_address, payment_method, prescription=None, customer_notes="", request=None):
        """
        Executes order placement with database transaction, stock deduction,
        price calculation, prescription enforcement, and logistics initialization.
        """
        if not cart or cart.items.count() == 0:
            raise OrderProcessingError("Cannot place order for an empty cart.")

        requires_prescription = cart.has_prescription_items

        # Prescription Validation Rule
        if requires_prescription:
            if not prescription:
                raise OrderProcessingError("Your order includes prescription medicines. Please upload or select a valid prescription before placing the order.")
            if prescription.customer != user:
                raise OrderProcessingError("Prescription does not belong to your account.")

        with transaction.atomic():
            # 1. Validate real-time stock
            for item in cart.items.select_related('product'):
                if item.quantity > item.product.stock_quantity:
                    raise OrderProcessingError(
                        f"Stock shortage: '{item.product.name}' only has {item.product.stock_quantity} units available, but you requested {item.quantity}."
                    )

            # 2. Server-side financial calculations
            subtotal = cart.subtotal
            tax = cart.tax_total
            delivery_fee = cart.delivery_fee
            grand_total = subtotal + tax + delivery_fee

            # 3. Determine initial order status
            if requires_prescription:
                if prescription and prescription.is_approved:
                    initial_order_status = OrderStatus.CONFIRMED
                else:
                    initial_order_status = OrderStatus.PRESCRIPTION_REVIEW
            else:
                initial_order_status = OrderStatus.CONFIRMED

            # Address snapshot formatting
            address_snapshot = (
                f"{shipping_address.full_name} | {shipping_address.phone}\n"
                f"{shipping_address.address_line}, {shipping_address.area}\n"
                f"{shipping_address.city}, {shipping_address.province} - {shipping_address.postal_code}\n"
                f"Landmark: {shipping_address.landmark or 'N/A'}"
            )

            # 4. Create Order
            order = Order.objects.create(
                customer=user,
                shipping_address=shipping_address,
                shipping_address_snapshot=address_snapshot,
                subtotal=subtotal,
                tax=tax,
                delivery_fee=delivery_fee,
                grand_total=grand_total,
                payment_method=payment_method,
                payment_status=PaymentStatus.PENDING,
                order_status=initial_order_status,
                requires_prescription=requires_prescription,
                prescription=prescription,
                customer_notes=customer_notes
            )

            # 5. Create Order Items & Deduct Inventory
            for item in cart.items.select_related('product'):
                product = item.product
                item_subtotal = product.effective_price * item.quantity
                item_tax = round(item_subtotal * (Decimal(str(product.tax_rate or 5.0)) / Decimal('100.0')), 2)

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name_snapshot=product.name,
                    sku_snapshot=product.sku,
                    quantity=item.quantity,
                    unit_price=product.effective_price,
                    tax=item_tax,
                    subtotal=item_subtotal,
                    prescription_required=product.prescription_required
                )

                # Deduct inventory stock
                prev_stock = product.stock_quantity
                new_stock = prev_stock - item.quantity
                product.stock_quantity = new_stock
                product.save()

                # Audit transaction record
                StockTransaction.objects.create(
                    product=product,
                    transaction_type=TransactionType.SALE,
                    quantity=-item.quantity,
                    previous_stock=prev_stock,
                    new_stock=new_stock,
                    reference=f"Order #{order.order_number}",
                    performed_by=user
                )

            # 6. Initialize Payment
            payment = PaymentService.initialize_payment(order, payment_method)
            if payment.status == PaymentStatus.PAID:
                order.payment_status = PaymentStatus.PAID
                order.save(update_fields=['payment_status'])

            # 7. Initialize Delivery Logistics
            Delivery.objects.create(
                order=order,
                delivery_address=address_snapshot,
                status=DeliveryStatus.PENDING
            )

            # 8. Clear user cart
            cart.items.all().delete()

            # 9. Audit log
            log_audit_action(
                user, 'CREATE', 'Order', order.id,
                f"Order placed: #{order.order_number} (${order.grand_total}) - Status: {order.order_status}",
                request
            )

            # 10. Customer Notification
            Notification.objects.create(
                user=user,
                title=f"Order Placed #{order.order_number}",
                message=f"Thank you! Your order #{order.order_number} has been received. Status: {order.get_order_status_display()}.",
                notification_type=NotificationType.ORDER_PLACED
            )

            return order
