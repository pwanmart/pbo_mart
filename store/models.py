from django.db import models
from uuid import uuid4
from django.core.validators import MinValueValidator
from django.contrib import admin
from django.conf import settings
from store.validators import validate_file_size

        
class Collection(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, related_name='featured_product_collections', blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']
        
    
    
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[MinValueValidator(1)])
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='products')
    

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title', 'unit_price']
    

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='store/images',
        validators=[validate_file_size])
    


class Pbo(models.Model):
    MEMBERSHIP_AFFILIATE = 'A'
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CLASSIC_GOLD = 'C'
    

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_AFFILIATE, 'Affiliate'),
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
        (MEMBERSHIP_CLASSIC_GOLD, 'Classic Gold'),
    ]
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    voucher_balance = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    class Meta:
        ordering = ['user__first_name', 'user__last_name', 'membership', 'voucher_balance']
        # permissions = [
        #     ('view_history', 'Can view history')
        # ]

class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    pbo = models.ForeignKey(Pbo, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paystack_payment_reference = models.CharField(max_length=100, blank=True, null=True)

    # class Meta:
    #     permissions = [
    #         ('cancel_order', 'Can cancel order')
    #     ]
    class Meta:
        ordering = ['payment_status', 'placed_at']
        
    def __str__(self):
        return f"Order {self.id} - {self.payment_status} for {self.pbo}"

        


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        ordering = ['quantity', 'unit_price']
        
    def __str__(self):
        return f' Order number {self.order.id}'
    

class Address(models.Model):
    house_number = models.CharField(max_length=10)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pbo = models.ForeignKey(
        Pbo, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['street', 'city', 'state']
        
    def __str__(self):
        return f'Address for PBO {self.pbo}'

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = [['cart', 'product']]
        
class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f'Review for {self.product}'
    
class PboTopUp(models.Model):
    pbo = models.ForeignKey(Pbo, on_delete=models.PROTECT, related_name='top_ups')
    amount_paid = models.PositiveIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['amount_paid', 'created_at']
        
    def __str__(self):
        return f'Top Up for PBO {self.pbo}'
    
    
class Complains(models.Model):
    pbo = models.ForeignKey(Pbo, on_delete=models.PROTECT, related_name='complains')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Complain for PBO {self.pbo}'
    
    