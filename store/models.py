from django.db import models

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