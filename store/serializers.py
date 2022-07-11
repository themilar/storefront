from typing import Dict
from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import (
    Cart,
    CartItem,
    Customer,
    Order,
    OrderItem,
    Product,
    Collection,
    Review,
)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ("id", "title", "product_count")

    product_count = serializers.IntegerField(read_only=True)


class ProductSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "slug",
            "inventory",
            "unit_price",
            "price_with_tax",
            "collection",
        )

    price_with_tax = serializers.SerializerMethodField("calculate_tax")

    def calculate_tax(self, product: Product) -> Decimal:
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "date", "name", "body", "date")

    def create(self, validated_data: Dict):
        product_id = self.context.get("product_id")
        return Review.objects.create(product_id=product_id, **validated_data)


class BasicProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "title", "unit_price")


class CartItemSerializer(serializers.ModelSerializer):
    product = BasicProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cartitem: CartItem) -> int:
        return cartitem.quantity * cartitem.product.unit_price

    class Meta:
        model = CartItem
        fields = ("id", "product", "quantity", "total_price")


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart) -> Decimal:
        return sum(item.quantity * item.product.unit_price for item in cart.items.all())

    class Meta:
        model = Cart
        fields = ("id", "items", "total_price")


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value: int):
        if not Product.objects.filter(pk=value):
            raise serializers.ValidationError("No product with the given ID exists")
        return value

    def save(self, **kwargs):
        quantity = self.validated_data.get("quantity")
        product_id = self.validated_data.get("product_id")
        cart_id = self.context.get("cart_id")
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )
        return self.instance

    class Meta:
        model = CartItem
        fields = ("id", "product_id", "quantity")


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("quantity",)


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ("id", "user_id", "phone", "birth_date", "membership")


class OrderItemSerializer(serializers.ModelSerializer):
    product = BasicProductSerializer()

    class Meta:
        model = OrderItem
        fields = ("id", "product", "unit_price", "quantity")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "customer", "placed_at", "payment_status", "items")


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("payment_status",)


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No cart with the given ID was found.")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("The cart is empty.")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data.get("cart_id")

            customer = Customer.objects.get(user_id=self.context.get("user_id"))
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related("product").filter(
                cart_id=cart_id
            )
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            return order
