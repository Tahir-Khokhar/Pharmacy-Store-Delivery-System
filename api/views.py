from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.accounts.models import User, Address
from apps.accounts.permissions import IsPharmacist, IsDeliveryStaff, IsAdminUserRole
from apps.products.models import Product, Category
from apps.products.filters import ProductFilter
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order
from apps.orders.services import OrderService, OrderProcessingError
from apps.prescriptions.models import Prescription, PrescriptionStatus
from apps.deliveries.models import Delivery, DeliveryStatus
from apps.reviews.models import Review
from apps.notifications.models import Notification
from .serializers import (
    UserSerializer, RegisterSerializer, AddressSerializer,
    CategorySerializer, ProductSerializer,
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer,
    PrescriptionSerializer, DeliverySerializer,
    ReviewSerializer, NotificationSerializer
)

# Authentication Endpoints
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Account registered successfully.',
                'data': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'success': True,
            'data': UserSerializer(request.user).data
        })


# Category ViewSet
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


# Product ViewSet
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(active=True).select_related('category')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'generic_name', 'brand', 'sku', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    lookup_field = 'slug'


# Cart ViewSet
class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response({
            'success': True,
            'data': CartSerializer(cart).data
        })

    @action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id or quantity <= 0:
            return Response({'success': False, 'message': 'Valid product_id and positive quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, pk=product_id, active=True)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            total_req = cart_item.quantity + quantity
            if total_req > product.stock_quantity:
                return Response({'success': False, 'message': f"Insufficient stock for {product.name}."}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = total_req
            cart_item.save()

        return Response({
            'success': True,
            'message': f"{product.name} added to cart.",
            'data': CartSerializer(cart).data
        })

    @action(detail=False, methods=['post'], url_path='remove')
    def remove_item(self, request):
        item_id = request.data.get('item_id')
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        return Response({
            'success': True,
            'message': 'Item removed from cart.',
            'data': CartSerializer(cart).data
        })


# Order ViewSet
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_admin_user() or user.is_pharmacist():
            return Order.objects.all().select_related('customer', 'delivery').prefetch_related('items')
        return Order.objects.filter(customer=user).select_related('delivery').prefetch_related('items')

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.items.count() == 0:
            return Response({'success': False, 'message': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        address = get_object_or_404(Address, pk=serializer.validated_data['shipping_address_id'], user=request.user)
        payment_method = serializer.validated_data['payment_method']
        prescription_id = serializer.validated_data.get('prescription_id')
        notes = serializer.validated_data.get('customer_notes', '')

        prescription = None
        if prescription_id:
            prescription = get_object_or_404(Prescription, pk=prescription_id, customer=request.user)

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
            return Response({
                'success': True,
                'message': f"Order #{order.order_number} created successfully.",
                'data': OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)
        except OrderProcessingError as exc:
            return Response({'success': False, 'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


# Prescription ViewSet
class PrescriptionViewSet(viewsets.ModelViewSet):
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_pharmacist() or user.is_admin_user():
            return Prescription.objects.all().select_related('customer', 'verified_by')
        return Prescription.objects.filter(customer=user).select_related('verified_by')

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsPharmacist], url_path='verify')
    def verify_prescription(self, request, pk=None):
        prescription = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('rejection_reason', '')
        notes = request.data.get('notes', '')

        if new_status not in [PrescriptionStatus.APPROVED, PrescriptionStatus.REJECTED]:
            return Response({'success': False, 'message': 'Status must be APPROVED or REJECTED.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status == PrescriptionStatus.REJECTED and not reason:
            return Response({'success': False, 'message': 'Rejection reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

        prescription.status = new_status
        prescription.verified_by = request.user
        prescription.verified_at = timezone.now()
        if reason:
            prescription.rejection_reason = reason
        if notes:
            prescription.notes = notes
        prescription.save()

        return Response({
            'success': True,
            'message': f"Prescription marked as {new_status}.",
            'data': PrescriptionSerializer(prescription).data
        })


# Delivery ViewSet
class DeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'tracking_number'

    def get_queryset(self):
        user = self.request.user
        if user.is_delivery_staff() or user.is_admin_user():
            return Delivery.objects.all().select_related('order', 'delivery_staff')
        return Delivery.objects.filter(order__customer=user).select_related('order', 'delivery_staff')

    @action(detail=True, methods=['post'], permission_classes=[IsDeliveryStaff], url_path='update-status')
    def update_status(self, request, tracking_number=None):
        delivery = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('delivery_notes', '')

        if new_status in DeliveryStatus.values:
            delivery.status = new_status
            if notes:
                delivery.delivery_notes = notes
            if new_status == DeliveryStatus.DELIVERED:
                delivery.delivered_at = timezone.now()
            delivery.save()

            return Response({
                'success': True,
                'message': f"Delivery status updated to {new_status}.",
                'data': DeliverySerializer(delivery).data
            })
        return Response({'success': False, 'message': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)


# Review ViewSet
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(approved=True).select_related('customer', 'product')

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


# Notification ViewSet
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='read')
    def mark_as_read(self, request, pk=None):
        notif = self.get_object()
        notif.mark_as_read()
        return Response({'success': True, 'message': 'Notification marked as read.'})
