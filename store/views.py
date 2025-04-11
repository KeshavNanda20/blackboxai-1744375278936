import json
from rest_framework import viewsets, status
import logging
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from .models import Category, Product, Cart, CartItem, Order
from .serializers import (
    CategorySerializer, ProductSerializer, CartSerializer,
    CartItemSerializer, OrderSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

logger = logging.getLogger(__name__)

class CartViewSet(viewsets.ViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_cart(self):
        if not self.request.user.is_authenticated:
            cart_id = self.request.session.get('cart_id')
            if cart_id:  
                try:
                    cart = Cart.objects.get(id=cart_id)
                    return cart
                except Cart.DoesNotExist:
                    pass
            cart = Cart.objects.create()
            self.request.session['cart_id'] = cart.id
            return cart
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request):
        try:
            cart = self.get_cart()
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Failed to retrieve cart'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))
            cart = self.get_cart()

            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
                logger.debug(f"Updated quantity for cart item {cart_item.id}")
            else:
                logger.debug(f"Created new cart item {cart_item.id}")

            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON data received")
            return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            logger.error(f"Product {product_id} not found")
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in add_item: {str(e)}")
            return Response({'error': 'Failed to add item to cart'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        try:
            cart = self.get_cart()
            data = json.loads(request.body)
            product_id = data.get('product_id')

            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Failed to remove item from cart'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        try:
            cart = self.get_cart()
            cart.items.all().delete()
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': 'Failed to clear cart'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, total=cart.get_total())

        for cart_item in cart.items.all():
            order.items.create(
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        cart.items.all().delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')

@ensure_csrf_cookie
def cart(request):
    return render(request, 'cart.html')
