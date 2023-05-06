from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.db.models import Q

from .models import Product, Category, ProductCover, Review
from .cart import Cart


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


class CartSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def validate_product(self, value):
        if Product.objects.filter(Q(id=value) & Q(inventory__gt=0)).exists():
            return value
        raise serializers.ValidationError('this product is not available')
    

    def validate_quantity(self, value):
        if value > 0:
            return value
        raise serializers.ValidationError('this product is not available')
    

    def create(self, validated_data):
        cart = Cart(self.context['request'])
        product = get_object_or_404(Product, pk=validated_data['product'])
        quantity = validated_data.get('quantity')
        cart.add_product(product, quantity)
        return cart
        








