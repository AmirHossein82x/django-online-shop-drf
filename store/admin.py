from typing import Any, List, Optional, Tuple
from urllib.parse import urlencode
from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from .models import Customer, Order, OrderItem, Product, Category, Promotion, ProductCover
# Register your models here.


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('amount','products_count')

    @admin.display(ordering='discount')
    def amount(self, obj:Promotion):
        return f"{int(obj.discount * 100)}%"
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count('products')).order_by('discount')
    
    def products_count(self, obj):
        return obj.products_count
    
    @admin.display(ordering='products_count')
    def products_count(self, obj:Promotion):
        url = (reverse('admin:store_product_changelist')
               + '?'
               + urlencode({
            'promotion_id__exact': str(obj.id)
               }))
        return format_html('<a href="{}">{} Products</a>', url, obj.products_count)

    

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'products_count', 'is_active')
    search_fields = ('title__istartswith', )

    def products_count(self, obj:Category):
        return obj.products_count

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(products_count=Count('products'))
    
    
    @admin.display(ordering='products_count')
    def products_count(self, category):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'category__id__exact': str(category.id)
            }))
        return format_html('<a href="{}">{} Products</a>', url, category.products_count)
    


class ProductFilter(admin.SimpleListFilter):
    title = 'available'
    parameter_name = 'available'


    def lookups(self, request, model_admin):
        if Product.objects.filter(inventory__gt=0):
            yield ('1', 'available')

        if Product.objects.filter(inventory=0):
            yield ('0', 'out_of_order')


    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any]:
        if self.value() == '1':
            return queryset.filter(inventory__gt=0)
        
        if self.value() == '0':
            return queryset.filter(inventory=0)
        


class ProductCoverInline(admin.TabularInline):
    model = ProductCover
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = ('title', 'category', 'price', 'promotion', 'final_price')
    list_display_links = ('title', 'category')
    inlines = [ProductCoverInline]
    list_filter = ('category', 'promotion', ProductFilter)
    list_select_related = ('category', 'promotion')
    radio_fields = {'category': admin.HORIZONTAL}
    search_fields = ('title__istartswith',)
    prepopulated_fields = {
        'slug': ('title',)  
    }
    # autocomplete_fields = ('category',)
    date_hierarchy = "date_time_created"
    list_per_page = 10

    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.filter(is_active=True).order_by('title')

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    

class CustomerFilter(admin.SimpleListFilter):
    title = 'member'
    parameter_name = 'member'

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        if Customer.objects.filter(status='1').exists():
            yield ('1', 'Gold')

        if Customer.objects.filter(status='2').exists():
            yield ('2', 'Silver')

        if Customer.objects.filter(status='3').exists():
            yield ('3', 'Bronze')

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any]:
        if self.value() == '1':
            return queryset.filter(status='1')
        
        if self.value() == '2':
            return queryset.filter(status='2')
        
        if self.value() == '3':
            return queryset.filter(status='3')
        

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'address', 'postal_code')
    search_fields = ('user__username__istartswith',)
    list_select_related = ['user']
    list_filter = [CustomerFilter]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('username',
                     'address','postal_code',
                       'total_price',
                         'date_time_created','status', 'is_delivered')
    search_fields = ('customer__postal_code__istartswith',)
    inlines = [OrderItemInline]
    list_select_related = ['customer__user']
    list_filter = ['is_delivered']


    def username(self, obj):
        return obj.customer.user.username
    
    def address(self, obj):
        return obj.customer.address
    
    def total_price(self, obj):
        return sum(item.price for item in obj.items.all())
    
    def postal_code(self, obj):
        return obj.customer.postal_code
    
    def status(self, obj):
        return obj.customer.status
