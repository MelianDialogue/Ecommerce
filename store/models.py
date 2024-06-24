from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stock = models.IntegerField()
    image = CloudinaryField('image', blank=True, null=True)
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    demand = models.IntegerField(default=0)
    competition_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def final_price(self):
        final_price = self.price - (self.price * self.discount / 100)
        return round(final_price, 2)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_price(self):
        return self.quantity * self.product.final_price

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='credit_card')

    def calculate_total_price(self):
        total = sum(item.total_price for item in self.orderitem_set.all())
        return total

    def apply_discount(self, discount_amount):
        self.total_price -= discount_amount
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def total_price(self):
        return self.quantity * self.product.final_price

    def __str__(self):
        return self.product.name
    from django.contrib.auth.models import User

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ModuleNotFoundError:
    SentimentIntensityAnalyzer = None  # or handle this case as needed

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    review_text = models.TextField()
    sentiment = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if SentimentIntensityAnalyzer:
            analyzer = SentimentIntensityAnalyzer()
            sentiment_score = analyzer.polarity_scores(self.review_text)
            compound = sentiment_score['compound']
            self.sentiment = 'positive' if compound > 0.05 else 'negative' if compound < -0.05 else 'neutral'
        else:
            # Handle the case where SentimentIntensityAnalyzer could not be imported
            self.sentiment = 'unknown'
        
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

class PolicyPage(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

# notification system
# models.py

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.TextField()

    def __str__(self):
        return self.message


class UserProductInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)  # Rating or interaction score

    class Meta:
        unique_together = ('user', 'product')


from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='transactions')

    def __str__(self):
        return f"Transaction {self.id}: {self.description} - ${self.amount}"


from django.db import models

class SalesData(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sales_date = models.DateField()
    sales_quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product} - {self.sales_date}"


# Example model for UserBehavior (adjust as per your actual implementation)
from django.db import models
from django.contrib.auth.models import User

class UserBehavior(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    clicks = models.IntegerField(default=0)
    time_spent = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.query}"
