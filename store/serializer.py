from rest_framework import serializers

from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')



class ProductSerializer(serializers.ModelSerializer):

    final_price = serializers.SerializerMethodField()
    category = CategorySerializer()
    promotion = serializers.StringRelatedField()

    def get_final_price(self, obj):
        return obj.final_price()
    

    class Meta:
        model = Product
        fields = ('id', 'title','description', 'category', 'promotion', 'price','final_price', 'inventory')
