from rest_framework import serializers
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'quantity', 'image', 'description', 
                 'category', 'category_name', 'created_at')

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        min_value=0, read_only=True,
        source='get_cost'
    )

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'total')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        min_value=0, read_only=True,
        source='get_total'
    )
    user = UserSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total', 'created_at')

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        min_value=0, read_only=True,
        source='get_cost'
    )

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'total')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'items', 'total', 'status', 'created_at')
        read_only_fields = ('total', 'status')
