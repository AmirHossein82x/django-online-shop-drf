from django.db import models
from django.db.models.query import QuerySet

from config import settings

# Create your models here.
 

class Category(models.Model):
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title
    


class Promotion(models.Model):
    discount = models.DecimalField(max_digits=3, decimal_places=2)

    def __str__(self) -> str:
        return f"{int(self.discount * 100)}%"
    


class ProductManager(models.Manager):
    def available(self):
        return self.filter(inventory__gt=0)
    


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    promotion = models.ForeignKey(Promotion, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    price = models.DecimalField(max_digits=6, decimal_places=3)
    inventory = models.PositiveIntegerField()
    date_time_created = models.DateTimeField(auto_now_add=True)
    date_time_modified = models.DateTimeField(auto_now=True)
    objects = ProductManager()

    class Meta:
        ordering = ('-date_time_created',)


    def __str__(self) -> str:
        return f"{self.title}"
    
    
    def final_price(self):
        if not self.promotion:
            return self.price
        return int((1 - self.promotion.discount) * self.price)



class ProductCover(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products')


class Review(models.Model):
    CHOICES = [
        ('1', 'I recomend this product'),
        ('2', 'This product is awfull'),
        ('3', 'I have no idea')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    description = models.TextField()
    date_time_created = models.DateTimeField(auto_now_add=True)
    is_recomended = models.CharField(choices=CHOICES, max_length=1)
    is_show = models.BooleanField(default=False)
