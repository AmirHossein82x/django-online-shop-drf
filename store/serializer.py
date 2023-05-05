from rest_framework import serializers

from .models import Product, Category, ProductCover


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
    images = ProductCoverSerializer(many=True)

    def get_final_price(self, obj):
        return obj.final_price()
    

    class Meta:
        model = Product
        fields = ('id', 'title','description', 'category', 'promotion', 'price','final_price', 'inventory', 'images')



