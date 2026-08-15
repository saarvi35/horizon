from django.db import models
from categories.models import Category

class Size(models.Model):
    size = models.CharField(max_length=10 , unique=True)

    def __str__(self):
        return self.size

class AllProducts(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = models.TextField(max_length=500, blank=True)
    discount_price  = models.IntegerField(null=True, blank=True)
    original_price  = models.IntegerField(null=True, blank=True)
    stock           = models.IntegerField()
    category        = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    size            = models.ManyToManyField(Size , blank=True)
    is_available    = models.BooleanField(default=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)
    ratings         = models.FloatField(default=0.0 , null=True , blank= True)
    reviews         = models.PositiveIntegerField(default=0 , null=True , blank=True)

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def discount_percent(self):
        return ((self.original_price - self.discount_price) / self.original_price) * 100
      
    def __str__(self):
        return self.product_name  

class ProductDetails(models.Model):
    product = models.ForeignKey(AllProducts, related_name="details_image" ,on_delete=models.CASCADE)
    image   = models.ImageField(upload_to='media/images')
    colors  = models.CharField(max_length=20 , null=True , blank=True)

    class Meta:
        verbose_name = 'product detail'
        verbose_name_plural = 'product details'

    def _str_(self):
        return self.product

# for contact page
class Contact(models.Model):
    name        = models.CharField(max_length=200, unique=True) 
    description = models.TextField(max_length=500, blank=True)
    contact     = models.IntegerField()
    email       = models.EmailField()


class CartItem(models.Model):
    product = models.ForeignKey(AllProducts, on_delete=models.CASCADE)  
    user = models.ForeignKey('accounts.Register', on_delete=models.CASCADE)        
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        if self.product.discount_price >0:
            return self.product.discount_price * self.quantity
        return self.product.original_price * self.quantity  
    
    def discount_price(self):
        if self.product.discount_price >0:
            return (self.product.original_price - self.product.discount_price) * self.quantity 
        return 0 


class Wishlist(models.Model):
    product =  models.ForeignKey(AllProducts,on_delete=models.CASCADE) 
    user=  models.ForeignKey('accounts.Register' , on_delete=models.CASCADE)  
    added_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.product.product_name

   