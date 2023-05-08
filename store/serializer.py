from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import serializers
from decimal import Decimal
from django.db.models import Q, F

from .models import Customer, Order, OrderItem, Product, Category, ProductCover, Review, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')


class ProductCoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCover
        fields = ('id', 'image')


    def create(self, validated_data):
        return ProductCover.objects.create(product=self.context['product'], **validated_data)
    
    
    def update(self, instance, validated_data):
        instance.image = validated_data['image']
        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer):

    final_price = serializers.SerializerMethodField()
    category = CategorySerializer()
    promotion = serializers.StringRelatedField()
    images = ProductCoverSerializer(many=True, read_only=True)

    def get_final_price(self, obj):
        return obj.final_price()
    

    class Meta:
        model = Product
        fields = ('id', 'title','description', 'category', 'promotion', 'price','final_price', 'inventory', 'images')


class SimpleProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    final_price = serializers.SerializerMethodField()

    def get_final_price(self, obj):
        return obj.final_price()
    class Meta:
        model = Product
        fields = ('id', 'title', 'category', 'final_price')




class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'description', 'is_recomended')


    def create(self, validated_data):
        return Review.objects.create(user=self.context['user'], product=self.context['product'], **validated_data)
    

class ReviewShowSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()
    def get_username(self, obj):
        return obj.user.username
    
    class Meta:
        model = Review
        fields = ('id','username', 'product', 'description', 'is_recomended', 'date_time_created')


class ReviewShowAdminSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()
    def get_username(self, obj):
        return obj.user.username
    
    class Meta:
        model = Review
        fields = ('id','username', 'product', 'description', 'is_recomended', 'date_time_created', 'is_show')


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('is_show',)


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return obj.product.final_price() * obj.quantity
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'price')


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return sum(item.product.final_price() * item.quantity for item in obj.items.all())
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price')


class CartItemAddSerializer(serializers.ModelSerializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_product_id(self, value):
        if Product.objects.filter(Q(id=value) & Q(inventory__gt=0)).exists():
            return value
        raise serializers.ValidationError({'product id not valid'})
    
    def save(self, **kwargs):
        cart = get_object_or_404(Cart, pk=self.context['cart_id'])
        if CartItem.objects.filter(cart=cart).exists():
            instance = CartItem.objects.filter(product_id=self.validated_data['product']).\
                update(quantity=F('quantity') + self.validated_data['quantity'])
            return instance
        
        instance = CartItem.objects.create(cart=cart, product_id=self.validated_data['product'], quantity=self.validated_data['quantity'])
        return instance

    # def create(self, validated_data):
    #     cart = get_object_or_404(Cart, pk=self.context['cart_id'])
    #     if CartItem.objects.filter(cart=cart).exists():
    #         instance = CartItem.objects.filter(product_id=self.validated_data['product']).\
    #             update(quantity=F('quantity') + self.validated_data['quantity'])
    #         return instance
        
    #     instance = CartItem.objects.create(cart=cart, product_id=self.validated_data['product'], quantity=self.validated_data['quantity'])
    #     return instance
        
    
    class Meta:
        model = CartItem
        fields = ('product', 'quantity')

        
   
        

class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('quantity',)


class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)

    def get_email(self, obj):
        return obj.user.username
    
    class Meta:
        model = Customer
        fields = ('user', 'email', 'status', 'postal_code')


class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        if not Cart.objects.filter(id=value).exists():
            raise serializers.ValidationError({'invalid cart id'})
        if CartItem.objects.filter(cart_id=value).count() < 1:
            raise serializers.ValidationError({'you can not commit order because your cart is empty'})
        if not Cart.objects.filter(id=value).exists():
            raise serializers.ValidationError({'invalid cart id'})
        return value
    

    def save(self, **kwargs):
        with transaction.atomic():
            order = Order.objects.create(customer=self.context['customer'])
            cart = Cart.objects.get(pk=self.validated_data['cart_id'])

            orderitems = [
                OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price * item.quantity
                )
                for item in cart.items.all()
            ]
            OrderItem.objects.bulk_create(orderitems)
            cart.delete()
            return order

        
        

class OrderitemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity','price']
        

class OrderShowSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    items = OrderitemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, obj):
        return sum(item.price for item in obj.items.all())

    def get_username(self, obj):
        return obj.customer.user.username
    
    class Meta:
        model = Order
        fields = ['id', 'username','items', 'total_price', 'is_delivered']


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['is_delivered']