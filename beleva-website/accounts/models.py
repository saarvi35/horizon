from django.db import models
# register
class Register(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_no = models.CharField(max_length=10)
    password = models.CharField(max_length=256)

    def __str__(self):
        return self.email 
    
class BillingAddress(models.Model):
    user = models.ForeignKey(Register , on_delete=models.CASCADE , null=True , blank=True)
    full_name = models.CharField(max_length=100)
    email_shipping = models.EmailField()
    phone = models.IntegerField()
    address = models.CharField(max_length=150)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip_code = models.IntegerField()
    order_notes = models.TextField(blank=True , null=True)

    class Meta:
        verbose_name = 'billing address'
        verbose_name_plural = 'billing addresses'

    def __str__(self):
        return self.first_name
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING' , 'Pending'),
        ('PROCESSING' , 'Processing'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('IN_TRANSIT', 'In Transit'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('CANCELLED' , 'Cancelled'),
        ('DELIVERED' , 'Delivered'),
    ]
    PAYMENT_CHOICES = [
        ('COD' , 'Cah on Delivery'),
        ('CARD' , 'Paid via Card'),
    ]

    user = models.ForeignKey(Register , on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=15 , choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=50 , choices=STATUS_CHOICES)
    total_price = models.FloatField()
    billing_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order , on_delete=models.CASCADE , related_name='items')
    product = models.ForeignKey('products.AllProducts' , on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.order