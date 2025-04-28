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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Count
from .apriori import apriori, generate_association_rules
from .models import Order, Product
from .serializers import ProductSerializer

# Existing imports and classes...

@api_view(['GET'])
@permission_classes([AllowAny])
def apriori_recommendations(request):
    min_support = float(request.query_params.get('min_support', 0.5))
    min_confidence = float(request.query_params.get('min_confidence', 0.7))

    # Get all orders and extract product IDs per order
    transactions = []
    orders = Order.objects.prefetch_related('items').all()
    for order in orders:
        product_ids = [item.product.id for item in order.items.all()]
        if product_ids:
            transactions.append(product_ids)

    # Run Apriori algorithm
    frequent_itemsets = apriori(transactions, min_support=min_support)
    rules = generate_association_rules(frequent_itemsets, min_confidence=min_confidence)

    # Prepare recommendations: for each antecedent, recommend consequents
    recommendations = {}
    for antecedent, consequent, confidence in rules:
        for item in antecedent:
            if item not in recommendations:
                recommendations[item] = set()
            recommendations[item].update(consequent)

    # If product_id provided, return recommendations for that product
    product_id = request.query_params.get('product_id')
    if product_id:
        product_id = int(product_id)
        recommended_ids = list(recommendations.get(product_id, []))
        recommended_products = Product.objects.filter(id__in=recommended_ids)
    else:
        # Return top recommended products overall
        all_recommended_ids = set()
        for recs in recommendations.values():
            all_recommended_ids.update(recs)
        recommended_products = Product.objects.filter(id__in=all_recommended_ids)

    serializer = ProductSerializer(recommended_products, many=True)
    return Response(serializer.data)

# Add this view to router or urlpatterns as needed

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

        delivery_address = request.data.get('delivery_address')
        if not delivery_address:
            return Response({'error': 'Delivery address is required'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, total=cart.get_total(), delivery_address=delivery_address)

        for cart_item in cart.items.all():
            order.items.create(
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        cart.items.all().delete()

        # Send email and WhatsApp notification
        from django.core.mail import send_mail
        import os
        from twilio.rest import Client

        # Email sending
        subject = f"New Order #{order.id} from {request.user.username}"
        message = f"Order Details:\nOrder ID: {order.id}\nUser: {request.user.username}\nDelivery Address:\n{delivery_address}\nTotal: {order.total}"
        recipient_list = ['keshavnanda.0087@gmail.com']
        send_mail(subject, message, os.environ.get('EMAIL_HOST_USER'), recipient_list)

        # WhatsApp sending via Twilio
        try:
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            client = Client(account_sid, auth_token)
            whatsapp_message = client.messages.create(
                body=message,
                from_='whatsapp:+14155238886',  # Twilio sandbox WhatsApp number
                to='whatsapp:+918699984018'
            )
        except Exception as e:
            # Log error but do not block order creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"WhatsApp message failed: {str(e)}")

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def accept_order(self, request, pk=None):
        # Admin accepts the order
        order = self.get_object()
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        order.status = 'processing'
        order.save()
        return Response({'status': 'Order accepted'})

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def tracking(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        tracking_info = {
            'order_id': order.id,
            'status': order.status,
            'delivery_address': order.delivery_address,
            'estimated_delivery': '3-5 business days'  # Placeholder
        }
        return Response(tracking_info)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        rating = request.data.get('rating')
        if not rating or not (1 <= int(rating) <= 5):
            return Response({'error': 'Rating must be an integer between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
        order.rating = int(rating)
        order.save()
        return Response({'status': 'Rating submitted'})

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html')

@ensure_csrf_cookie
def cart(request):
    return render(request, 'cart.html')
