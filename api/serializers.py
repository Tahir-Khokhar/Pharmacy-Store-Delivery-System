from decimal import Decimal
from rest_framework import serializers
from apps.accounts.models import User, Profile, Address
from apps.products.models import Category, Product, ProductImage
from apps.inventory.models import Batch
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem, OrderStatus, PaymentMethod
from apps.prescriptions.models import Prescription, PrescriptionStatus
from apps.deliveries.models import Delivery, DeliveryStatus
from apps.reviews.models import Review
from apps.notifications.models import Notification

# User & Auth Serializers
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('avatar', 'date_of_birth', 'blood_group', 'bio')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'profile')
        read_only_fields = ('role',)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'phone')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            role='CUSTOMER'
        )
        return user


# Address Serializer
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'title', 'full_name', 'phone', 'address_line', 'area', 'city', 'province', 'postal_code', 'landmark', 'is_default')


# Product & Category Serializers
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'icon', 'parent', 'active')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text')


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    effective_price = serializers.ReadOnlyField()
    discount_percent = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    reviews_count = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'generic_name', 'brand', 'category', 'category_name',
            'dosage_form', 'strength', 'short_description', 'description', 'image',
            'price', 'discount_price', 'effective_price', 'discount_percent', 'tax_rate',
            'stock_quantity', 'unit', 'manufacturer', 'batch_number', 'expiry_date',
            'prescription_required', 'active', 'featured', 'in_stock', 'average_rating', 'reviews_count'
        )


# Cart Serializers
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    item_subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'item_subtotal')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    tax_total = serializers.ReadOnlyField()
    delivery_fee = serializers.ReadOnlyField()
    grand_total = serializers.ReadOnlyField()
    has_prescription_items = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'subtotal', 'tax_total', 'delivery_fee', 'grand_total', 'has_prescription_items')


# Order Serializers
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_name_snapshot', 'sku_snapshot', 'quantity', 'unit_price', 'tax', 'subtotal', 'prescription_required')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_username = serializers.ReadOnlyField(source='customer.username')

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'customer', 'customer_username', 'shipping_address_snapshot',
            'subtotal', 'tax', 'delivery_fee', 'grand_total', 'payment_method', 'payment_status',
            'order_status', 'requires_prescription', 'prescription', 'customer_notes', 'created_at', 'items'
        )


class OrderCreateSerializer(serializers.Serializer):
    shipping_address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices, default='COD')
    prescription_id = serializers.IntegerField(required=False, allow_null=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True)


# Prescription Serializer
class PrescriptionSerializer(serializers.ModelSerializer):
    customer_username = serializers.ReadOnlyField(source='customer.username')

    class Meta:
        model = Prescription
        fields = (
            'id', 'prescription_number', 'customer', 'customer_username', 'uploaded_file',
            'patient_name', 'doctor_name', 'clinic_hospital', 'status',
            'verified_by', 'verified_at', 'rejection_reason', 'notes', 'created_at'
        )
        read_only_fields = ('prescription_number', 'customer', 'verified_by', 'verified_at')


# Delivery Serializer
class DeliverySerializer(serializers.ModelSerializer):
    order_number = serializers.ReadOnlyField(source='order.order_number')
    courier_name = serializers.ReadOnlyField(source='delivery_staff.username')

    class Meta:
        model = Delivery
        fields = (
            'id', 'tracking_number', 'order', 'order_number', 'delivery_staff', 'courier_name',
            'delivery_address', 'status', 'assigned_at', 'picked_up_at', 'out_for_delivery_at',
            'delivered_at', 'delivery_notes', 'recipient_name'
        )


# Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.username')

    class Meta:
        model = Review
        fields = ('id', 'product', 'customer', 'customer_name', 'rating', 'review', 'created_at')
        read_only_fields = ('customer',)


# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'notification_type', 'is_read', 'created_at')
