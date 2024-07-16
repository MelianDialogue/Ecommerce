import numpy as np

from sklearn.neighbors import NearestNeighbors
from .models import Product

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Order, OrderItem, Review, Wishlist
from .forms import ReviewForm
from .payments import create_stripe_payment_intent, create_paypal_payment, execute_paypal_payment
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Cart, Order
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Order, OrderItem
from .payments import create_stripe_payment_intent, create_paypal_payment
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Order, OrderItem
from .payments import create_stripe_payment_intent, create_paypal_payment
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Order, OrderItem
from .payments import create_stripe_payment_intent, create_paypal_payment
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Order, OrderItem, Review, Wishlist
from .forms import ReviewForm
from .payments import create_stripe_payment_intent, create_paypal_payment, execute_paypal_payment
from sklearn.metrics.pairwise import cosine_similarity
from .models import Order, OrderItem, Product
import numpy as np

# Views for product display and cart management
from django.shortcuts import render
from .models import Product


from django.shortcuts import render
from .models import Product

def index(request):
    # Example: Filter products for Category 1
    category_1_products = Product.objects.filter(category='1')[:6]
    category_2_products = Product.objects.filter(category='2')[:4]
    category_3_products = Product.objects.filter(category='3')[:6]
    category_4_products = Product.objects.filter(category='4')[:4]
    category_5_products = Product.objects.filter(category='5')[:3]
    # Repeat for other categories as needed

    context = {
        'category_1_products': category_1_products,
        'category_2_products': category_2_products,
        'category_3_products': category_3_products,
        'category_4_products': category_4_products,
        'category_5_products': category_5_products,
        # Include other categories similarly
    }
    return render(request, 'store/index.html', context)



# Views for product display and cart management
# def index(request):
#     products = Product.objects.all()[:4]
#     return render(request, 'store/index.html', {'products': products})

# def product_list(request):
#     products = Product.objects.all()
#     return render(request, 'store/product_list.html', {'products': products})
#


from django.shortcuts import render
from .models import Product

def product_list(request):
    category_1_products = Product.objects.filter(category='1')
    category_2_products = Product.objects.filter(category='2')
    category_3_products = Product.objects.filter(category='3')
    category_4_products = Product.objects.filter(category='4')

    context = {
        'category_1_products': category_1_products,
        'category_2_products': category_2_products,
        'category_3_products': category_3_products,
        'category_4_products': category_4_products,
    }

    return render(request, 'store/product_list.html', context)


from django.shortcuts import render
from .models import Product

def product_list(request):
    category_1_products = Product.objects.filter(category='1')
    category_2_products = Product.objects.filter(category='2')
    category_3_products = Product.objects.filter(category='3')
    category_4_products = Product.objects.filter(category='4')
    user_id = request.user.id if request.user.is_authenticated else None

    context = {
        'category_1_products': category_1_products,
        'category_2_products': category_2_products,
        'category_3_products': category_3_products,
        'category_4_products': category_4_products,
        'recommend_url': reverse('recommend_products', args=[user_id]) if user_id else None,
    }

    return render(request, 'store/product_list.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    
    # Fetch similar products
    similar_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'similar_products': similar_products
    })

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.product.add(product)
    return redirect('wishlist_detail')

@login_required
def wishlist_detail(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.product.all()
    return render(request, 'store/wishlist_detail.html', {'wishlist': wishlist, 'products': products})

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.product.remove(product)
    return redirect('wishlist_detail')


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    subtotal = sum(item.total_price for item in cart_items)
    shipping = 100  # Example shipping cost
    total_price = subtotal + shipping
    order, created = Order.objects.get_or_create(user=request.user, status='pending', defaults={'total_price': total_price})
    if not created:
        order.total_price = total_price
        order.save()

    if request.method == 'POST':
        # Redirect to the checkout view with the calculated prices
        checkout_url = reverse('checkout', args=[order.id])
        return redirect(f'{checkout_url}?subtotal={subtotal}&shipping={shipping}&total={total_price}')

    return render(request, 'store/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total_price': total_price,
        'order': order
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')

def update_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    action = request.GET.get('action')
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return JsonResponse({'quantity': cart_item.quantity, 'total_price': cart_item.total_price})

def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return JsonResponse({'success': True})


@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    # Get the values from the query parameters
    subtotal = float(request.GET.get('subtotal', 0))
    shipping = float(request.GET.get('shipping', 100))
    total_price = float(request.GET.get('total', subtotal + shipping))

    # Ensure the order's total price matches
    order.total_price = total_price
    order.save()

    if request.method == 'POST':
        payment_method = request.POST.get('payment')
        if payment_method == 'stripe':
            intent = create_stripe_payment_intent(order)
            return render(request, 'store/stripe_checkout.html', {
                'order': order,
                'order_items': order_items,
                'subtotal': subtotal,
                'shipping': shipping,
                'total_price': total_price,
                'client_secret': intent.client_secret,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            })
        elif payment_method == 'paypal':
            return_url = request.build_absolute_uri(reverse('paypal_return'))
            cancel_url = request.build_absolute_uri(reverse('paypal_cancel'))
            approval_url = create_paypal_payment(order, return_url, cancel_url)
            if approval_url:
                return redirect(approval_url)
            else:
                return redirect('checkout', order_id=order.id)

    return render(request, 'store/checkout.html', {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total_price': total_price,
    })




@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    # Get the values from the query parameters
    subtotal = float(request.GET.get('subtotal', 0))
    shipping = float(request.GET.get('shipping', 100))
    total_price = float(request.GET.get('total', subtotal + shipping))

    # Ensure the order's total price matches
    order.total_price = total_price
    order.save()

    if request.method == 'POST':
        payment_method = request.POST.get('payment')
        if payment_method == 'stripe':
            intent = create_stripe_payment_intent(order)
            return render(request, 'store/stripe_checkout.html', {
                'order': order,
                'order_items': order_items,
                'subtotal': subtotal,
                'shipping': shipping,
                'total_price': total_price,
                'client_secret': intent.client_secret,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            })
        elif payment_method == 'paypal':
            return_url = request.build_absolute_uri(reverse('paypal_return'))
            cancel_url = request.build_absolute_uri(reverse('paypal_cancel'))
            approval_url = create_paypal_payment(order, return_url, cancel_url)
            if approval_url:
                return redirect(approval_url)
            else:
                return redirect('checkout', order_id=order.id)

    return render(request, 'store/checkout.html', {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total_price': total_price,
    })



@login_required
def paypal_return(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if payment_id and payer_id:
        success = execute_paypal_payment(payment_id, payer_id)
        if success:
            order = Order.objects.get(payment_id=payment_id)
            order.status = 'completed'
            order.save()
            return redirect('order_success', order_id=order.id)
        else:
            return redirect('checkout', order_id=order.id)
    else:
        return redirect('checkout', order_id=request.session.get('order_id'))

@login_required
def paypal_cancel(request):
    order_id = request.session.get('order_id')
    return render(request, 'store/paypal_cancel.html', {'order_id': order_id})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


from .models import Notification
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Create a notification for the user
    message = f"Order #{order_id} has been successfully placed."
    Notification.objects.create(user=request.user, message=message)
    return render(request, 'store/order_success.html', {'order': order})


@login_required
def paypal_return(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    if payment_id and payer_id:
        success = execute_paypal_payment(payment_id, payer_id)
        if success:
            order = Order.objects.get(payment_id=payment_id)
            order.status = 'completed'
            order.save()
            return redirect('order_success', order_id=order.id)
        else:
            return redirect('checkout', order_id=order.id)
    else:
        return redirect('checkout', order_id=request.session.get('order_id'))

@login_required
def paypal_cancel(request):
    order_id = request.session.get('order_id')
    return render(request, 'store/paypal_cancel.html', {'order_id': order_id})

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    return render(request, 'store/order_detail.html', {'order': order, 'order_items': order_items})


from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Product, Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Product, Review
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required

@login_required
def leave_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get all reviews for the product
    reviews = Review.objects.filter(product=product)

    # Calculate average rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            # Redirect to the product detail page after saving the review
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'store/leave_review.html', {
        'form': form,
        'product': product,
        'reviews': reviews,  # Pass all reviews to the template
        'average_rating': average_rating  # Pass average rating to the template
    })

from django.shortcuts import render
from .models import Product

from django.shortcuts import render
from .models import Product


from django.contrib.auth.decorators import user_passes_test
from .forms import ProductForm

@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


# Add product (admin)
from django.contrib.auth.decorators import user_passes_test
from .forms import ProductForm

@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

# add to wishlist

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Wishlist

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.product.add(product)
    return redirect('wishlist_detail')

@login_required
def wishlist_detail(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.product.all()
    return render(request, 'store/wishlist_detail.html', {'wishlist': wishlist, 'products': products})

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.product.remove(product)
    return redirect('wishlist_detail')

# views.py

from django.shortcuts import render
from .models import BlogPost, FAQ, PolicyPage

def blog_post_detail(request, blog_post_id):
    # Retrieve the blog post object
    blog_post = BlogPost.objects.get(id=blog_post_id)
    return render(request, 'store/blog_post.html', {'blog_post': blog_post})

def faq_list(request):
    # Retrieve all FAQs
    faqs = FAQ.objects.all()
    return render(request, 'store/faq.html', {'faqs': faqs})

def policy_page_detail(request, policy_page_id):
    # Retrieve the policy page object
    policy_page = PolicyPage.objects.get(id=policy_page_id)
    return render(request, 'store/policy_page.html', {'policy_page': policy_page})
 
 
#  blog_post_detail
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import BlogPost
from .forms import BlogPostForm

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            return redirect('blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'store/blog_post.html', {'form': form})

def blog_list(request):
    blog_posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'store/blog_post.html', {'blog_posts': blog_posts})

def blog_detail(request, blog_post_id):
    blog_post = get_object_or_404(BlogPost, id=blog_post_id)
    return render(request, 'store/blog_detail.html', {'blog_post': blog_post})


# views.py

from django.shortcuts import render, get_object_or_404
from .models import Order

@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})


def recommend_products(user_id):
    # Get user's order history
    orders = Order.objects.filter(user_id=user_id, status='completed')
    products_bought = []

    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        for item in order_items:
            products_bought.append(item.product_id)

    # Find users similar to the current user based on purchased products
    similar_users = OrderItem.objects.filter(product_id__in=products_bought) \
                     .exclude(order__user_id=user_id) \
                     .values('order__user_id').distinct()

    # Aggregate recommendations based on similar users
    recommendations = {}
    for user in similar_users:
        user_orders = OrderItem.objects.filter(order__user_id=user['order__user_id']) \
                      .exclude(product_id__in=products_bought)
        for order_item in user_orders:
            if order_item.product_id not in recommendations:
                recommendations[order_item.product_id] = 0
            recommendations[order_item.product_id] += 1

    # Sort recommendations by count
    recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:5]

    # Get product objects for recommended products
    recommended_products = [Product.objects.get(id=item[0]) for item in recommendations]

    return recommended_products


import numpy as np
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404
from .models import Product, UserProductInteraction, User

def find_similar_users(user_id, num_users=5):
    interactions = UserProductInteraction.objects.filter(user_id=user_id)
    user_ratings = {interaction.product_id: interaction.rating for interaction in interactions}
    all_users = User.objects.exclude(id=user_id)

    similarities = []
    for other_user in all_users:
        other_interactions = UserProductInteraction.objects.filter(user_id=other_user.id)
        other_user_ratings = {interaction.product_id: interaction.rating for interaction in other_interactions}
        similarity = calculate_similarity(user_ratings, other_user_ratings)
        similarities.append((other_user.id, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    similar_users = [user_id for user_id, _ in similarities[:num_users]]
    return similar_users

def calculate_similarity(user_ratings, other_user_ratings):
    common_products = set(user_ratings.keys()) & set(other_user_ratings.keys())
    if not common_products:
        return 0
    user_ratings_vector = np.array([user_ratings[product_id] for product_id in common_products])
    other_ratings_vector = np.array([other_user_ratings[product_id] for product_id in common_products])
    return np.dot(user_ratings_vector, other_ratings_vector) / (np.linalg.norm(user_ratings_vector) * np.linalg.norm(other_ratings_vector))

def aggregate_recommendations(similar_users, user_id, num_recommendations=5):
    similar_users_interactions = UserProductInteraction.objects.filter(user_id__in=similar_users).exclude(user_id=user_id)
    product_recommendations = similar_users_interactions.values('product_id').annotate(avg_rating=Avg('rating')).order_by('-avg_rating')
    recommendations = [interaction['product_id'] for interaction in product_recommendations[:num_recommendations]]
    return Product.objects.filter(id__in=recommendations)

def recommend_products(request, user_id):
    similar_users = find_similar_users(user_id)
    recommendations = aggregate_recommendations(similar_users, user_id)
    recommended_products = Product.objects.filter(id__in=recommendations)
    return render(request, 'store/recommendations.html', {'recommendations': recommended_products})






def get_current_demand(product_id):
    product = Product.objects.get(id=product_id)
    return product.demand

def get_competition_price(product_id):
    product = Product.objects.get(id=product_id)
    return product.competition_price

from decimal import Decimal

def calculate_dynamic_price(demand, competition):
    base_price = 100.0
    demand_factor = 1 + (float(demand) / 100)
    competition_factor = 1 - (float(competition) / 100)
    new_price = base_price * demand_factor * competition_factor
    return round(new_price, 2)


def adjust_price(product_id):
    demand = get_current_demand(product_id)
    competition = get_competition_price(product_id)
    new_price = calculate_dynamic_price(demand, competition)
    return new_price

# views.py
from django.shortcuts import get_object_or_404, redirect
from .models import Product
# from .utils import adjust_price

def dynamic_price_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    new_price = adjust_price(product_id)
    product.price = new_price
    product.save()
    return redirect('product_detail', product_id=product_id)

# management/commands/update_prices.py
from django.core.management.base import BaseCommand
from store.models import Product
# from store.utils import adjust_price

class Command(BaseCommand):
    help = 'Update prices of all products based on dynamic pricing algorithm'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            new_price = adjust_price(product.id)
            product.price = new_price
            product.save()
            self.stdout.write(self.style.SUCCESS(f'Updated price for {product.name} to {new_price}'))



# customer segmentation
from django.db.models import Sum, Count
from django.shortcuts import render
from django.contrib.auth.models import User
from user_app.models import Profile 
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Fetch customer data
def fetch_customer_data():
    customers = User.objects.all().values('id', 'date_joined', 'profile__age')  # Assuming Profile model has age
    customer_data = pd.DataFrame(customers)
    
    # Fetch purchase data
    purchase_data = (
        Order.objects.values('user_id')
        .annotate(total_spent=Sum('total_price'), purchase_count=Count('id'))
        .order_by('user_id')
    )
    purchase_df = pd.DataFrame(purchase_data)
    
    # Merge customer and purchase data
    customer_data = customer_data.merge(purchase_df, left_on='id', right_on='user_id', how='left').fillna(0)
    
    return customer_data

# Segment customers using KMeans
def segment_customers():
    customer_data = fetch_customer_data()
    
    # Features for clustering
    features = ['profile__age', 'total_spent', 'purchase_count']
    
    # Standardizing the features
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(customer_data[features])
    
    # Apply k-means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    customer_data['segment'] = kmeans.fit_predict(standardized_data)
    
    return customer_data

# View for customer segmentation
def customer_segmentation_view(request):
    segments = segment_customers()
    segments_dict = segments.to_dict(orient='records')
    return render(request, 'store/customer_segmentation.html', {'segments': segments_dict})



# churn_predictions
import pandas as pd
from django.contrib.auth.models import User
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import pandas as pd
from django.contrib.auth.models import User

# churn_predictions
import pandas as pd
from django.contrib.auth.models import User
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils import shuffle
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count

from .models import Order
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def fetch_customer_data_with_churn():
    customers = User.objects.all().values('id', 'date_joined', 'profile__age')
    customer_data = pd.DataFrame(customers)
    print("Customer Data:", customer_data)  # Debug print

    purchase_data = (
        Order.objects.values('user_id')
        .annotate(total_spent=Sum('total_price'), purchase_count=Count('id'))
        .order_by('user_id')
    )
    purchase_df = pd.DataFrame(purchase_data)
    print("Purchase Data:", purchase_df)  # Debug print

    churn_data = determine_churn()
    print("Churn Data:", churn_data)  # Debug print

    customer_data = customer_data.merge(purchase_df, left_on='id', right_on='user_id', how='left').fillna(0)
    customer_data = customer_data.merge(churn_data, left_on='id', right_on='user_id', how='left').fillna(0)

    return customer_data


def determine_churn():
    churn_data = []
    six_months_ago = timezone.now() - timedelta(days=180)
    for user in User.objects.all():
        last_order = Order.objects.filter(user=user).order_by('-created_at').first()
        if last_order and last_order.created_at < six_months_ago:
            churn_data.append({'user_id': user.id, 'churn': 1})  # Churned
        else:
            churn_data.append({'user_id': user.id, 'churn': 0})  # Not churned
    
    return pd.DataFrame(churn_data)


def train_churn_model():
    customer_data = fetch_customer_data_with_churn()
    
    churn_counts = customer_data['churn'].value_counts()
    print(churn_counts)
    
    if len(churn_counts) < 2:
        raise ValueError("Not enough classes to train the model.")
    
    customer_data = shuffle(customer_data)
    
    features = ['profile__age', 'total_spent', 'purchase_count']
    X = customer_data[features]
    y = customer_data['churn']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
    
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    return model, scaler


def predict_churn():
    model, scaler = train_churn_model()
    
    customer_data = fetch_customer_data_with_churn()
    
    features = ['profile__age', 'total_spent', 'purchase_count']
    X = customer_data[features]
    X_scaled = scaler.transform(X)
    
    customer_data['churn_risk'] = model.predict_proba(X_scaled)[:, 1]
    
    return customer_data[['id', 'churn_risk']]



@login_required
def churn_prediction_view(request):
    profiles = Profile.objects.all()
    
    churn_data = {
        'profile__age': [profile.age for profile in profiles],
        'total_spent': [profile.total_spent for profile in profiles],
        'purchase_count': [profile.purchase_count for profile in profiles],
        'churn': [profile.churn for profile in profiles],
    }
    
    churn_df = pd.DataFrame(churn_data)
    
    if churn_df.empty:
        return render(request, 'store/error_page.html', {'message': 'No data available for churn prediction.'})
    
    churn_df.fillna(churn_df.mean(), inplace=True)
    
    X = churn_df[['profile__age', 'total_spent', 'purchase_count']]
    y = churn_df['churn']
    
    # Check if the target variable has at least two classes
    if y.nunique() < 2:
        return render(request, 'store/error_page.html', {'message': 'Not enough class diversity to perform churn prediction.'})
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),
        ('logreg', LogisticRegression()),
    ])
    
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    
    return render(request, 'store/churn_prediction.html', {'accuracy': accuracy})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sklearn.ensemble import IsolationForest
import pandas as pd
from .models import Transaction

def fetch_transactions():
    # Fetch transaction data from the database
    transactions = Transaction.objects.all()  # Assuming Transaction is your model
    return transactions

@login_required
def detect_fraud_view(request):
    transactions = fetch_transactions()
    
    if not transactions.exists():
        return render(request, 'store/error_page.html', {'message': 'No transactions available.'})
    
    # Convert transactions into a DataFrame
    transaction_data = {
        'amount': [transaction.total_price for transaction in transactions],
        'product_name': [transaction.product.name for transaction in transactions], 
    }
    
    transactions_df = pd.DataFrame(transaction_data)
    
   
    isolation_forest = IsolationForest(contamination=0.1)
    
  
    isolation_forest.fit(transactions_df[['amount']])
    
    # Predict anomalies (fraudulent transactions)
    transactions_df['fraud_score'] = isolation_forest.decision_function(transactions_df[['amount']])
    
    # Determine fraud based on a threshold
    threshold = -0.5
    transactions_df['is_fraud'] = transactions_df['fraud_score'] < threshold
    
    # Prepare data to pass to template
    fraud_transactions = transactions_df[transactions_df['is_fraud']]
    
    context = {
        'fraud_transactions': fraud_transactions.to_dict(orient='records'),
    }
    
    return render(request, 'store/fraud_detection.html', context)



from django.shortcuts import render
from .models import Review

def analyze_sentiment_view(request):
    reviews = Review.objects.all()
    return render(request, 'store/analyze_sentiment.html', {'reviews': reviews})


import pandas as pd
from sklearn.linear_model import LinearRegression
from .models import Customer, Transaction


clv_model = LinearRegression()

def load_and_prepare_data():
    data = {
        'customer_id': [1, 2, 3],
        'avg_transaction_value': [100, 150, 200],
        'num_transactions': [10, 15, 20],
        'clv': [1000, 2250, 4000]  # Example CLV values
    }
    df = pd.DataFrame(data)
    return df

def train_clv_model():
    df = load_and_prepare_data()
    X = df[['avg_transaction_value', 'num_transactions']]
    y = df['clv']
    clv_model.fit(X, y)

def predict_clv(customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return None

    transactions = Transaction.objects.filter(customer=customer)
    if not transactions.exists():
        return None

    avg_transaction_value = transactions.aggregate(avg_amount=models.Avg('amount'))['avg_amount']
    num_transactions = transactions.count()

    customer_data = pd.DataFrame({
        'avg_transaction_value': [avg_transaction_value],
        'num_transactions': [num_transactions]
    })

    clv = clv_model.predict(customer_data)[0]
    return clv

# Train the model
train_clv_model()


from django.shortcuts import render, get_object_or_404
from .models import Customer

def predict_clv_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    clv = predict_clv(customer_id)

    context = {
        'customer': customer,
        'clv': clv
    }
    return render(request, 'store/predict_clv.html', context)


# views.py

from django.shortcuts import render
from .models import DemandForecast

def forecast_list(request):
    forecasts = DemandForecast.objects.all()
    return render(request, 'store/forecast_list.html', {'forecasts': forecasts})



# views.py

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from prophet import Prophet
from django.shortcuts import render
from .models import SalesData, UserBehavior

def gather_sales_data():
    sales_data = SalesData.objects.all().values()
    return pd.DataFrame(sales_data)

def gather_social_media_data():
    social_data = UserBehavior.objects.all().values()
    return pd.DataFrame(social_data)

def predictive_model(sales_data, social_media_data):
    # Preprocessing
    sales_data['sales_date'] = pd.to_datetime(sales_data['sales_date'])
    sales_data.set_index('sales_date', inplace=True)
    sales_data_resampled = sales_data.resample('M').sum()
    
    # Merge datasets
    social_media_data['query_date'] = pd.to_datetime(social_media_data['created_at'])
    social_media_data.set_index('query_date', inplace=True)
    social_media_resampled = social_media_data.resample('M').sum()

    merged_data = pd.concat([sales_data_resampled, social_media_resampled], axis=1).fillna(0)

    # Scale data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(merged_data)

    # Principal Component Analysis
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(scaled_data)

    # Prepare data for Prophet
    df = pd.DataFrame({
        'ds': merged_data.index,
        'y': principal_components[:, 0]
    })

    # Fit and forecast with Prophet
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=12, freq='M')
    forecast = model.predict(future)

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def predict_trends():
    sales_data = gather_sales_data()
    social_media_data = gather_social_media_data()
    trends = predictive_model(sales_data, social_media_data)
    return trends

def trends_view(request):
    trends = predict_trends()
    return render(request, 'store/product_list.html', {'trends': trends.to_dict(orient='records')})


from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, AbandonedCart
# from .utils import send_recovery_email

def recover_abandoned_cart(request, user_id):
    cart = get_object_or_404(Cart, user_id=user_id)
    abandoned_cart, created = AbandonedCart.objects.get_or_create(cart=cart)

    if created:
        send_recovery_email(abandoned_cart)  # Send recovery email logic goes here

    return render(request, 'store/recovery_success.html', {'cart': cart})

from django.core.mail import send_mail
from django.conf import settings

def send_recovery_email(abandoned_cart):
    user_email = abandoned_cart.user.email
    cart_items = abandoned_cart.cart.cartitem_set.all()

    # Construct the email content
    subject = 'Recover Your Abandoned Cart'
    message = f'Hello {abandoned_cart.user.username},\n\n'
    message += 'You have abandoned the following items in your cart:\n'
    for item in cart_items:
        message += f'- {item.product.name}, Quantity: {item.quantity}\n'
    message += '\nPlease visit our website to complete your purchase.\n\n'
    message += 'Thank you!\n'
    message += 'Your Store Team'

    # Send the email
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])


def get_real_time_profile(user):
    try:
        user_profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        user_profile = None
    
    return user_profile


def personalize_ui(user_profile):
    personalized_content = {}

    if user_profile:
        if user_profile.interests:
            personalized_content['interests'] = user_profile.interests
        if user_profile.bio:
            personalized_content['bio'] = user_profile.bio
    
    return personalized_content

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from .utils import get_real_time_profile, personalize_ui

@login_required
def personalized_view(request):
    user_profile = get_real_time_profile(request.user)
    personalized_content = personalize_ui(user_profile)

    return render(request, 'store/personalized_view.html', {'personalized_content': personalized_content})


from .models import UserBehavior, Product

def adaptive_ranking(query, user_id):
    try:
        user_behavior = UserBehavior.objects.filter(user_id=user_id, query=query).latest('id')
    except UserBehavior.DoesNotExist:
        user_behavior = None

    # Example logic to rank search results based on user behavior
    if user_behavior:
        ranked_results = rank_search_results(query, user_behavior)
    else:
        ranked_results = rank_search_results(query)

    return ranked_results

def rank_search_results(query, user_behavior=None):
    if user_behavior:
        ranked_products = Product.objects.filter(name__icontains=query).order_by('-demand')
    else:
        ranked_products = Product.objects.filter(name__icontains=query).order_by('-created_at')

    return ranked_products


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from .utils import adaptive_ranking
from .models import Product

@login_required
def search_view(request):
    query = request.GET.get('q', '')
    user_id = request.user.id

    ranked_results = adaptive_ranking(query, user_id)

    return render(request, 'store/search_results.html', {'query': query, 'ranked_results': ranked_results})


# utils.py

from .models import Preference

def get_user_preferences(user_id):
    try:
        preferences = Preference.objects.get(user_id=user_id)
    except Preference.DoesNotExist:
        preferences = None
    
    return preferences

def generate_email_content(preferences):
    if preferences:
        email_content = f"Dear {preferences.user.username}, here is your personalized email content."
    else:
        email_content = "Generic email content when preferences are not available."
    
    return email_content

# views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
# from .utils import get_user_preferences, generate_email_content

@login_required
def send_personalized_email(request):
    user_id = request.user.id
    preferences = get_user_preferences(user_id)
    email_content = generate_email_content(preferences)
    
    send_mail(
        'Subject here',
        email_content,
        'from@example.com',
        [request.user.email],
        fail_silently=False,
    )
    
    return render(request, 'store/email_sent.html', {'email_content': email_content})


# views.py

from django.shortcuts import render
from .models import OrderItem, Product

def recommend_bundles(user_id):
    purchase_history = OrderItem.objects.filter(order__user_id=user_id)
    bundle_recommendations = {}

    for order_item in purchase_history:
        related_items = OrderItem.objects.filter(order__orderitem__product=order_item.product).exclude(product=order_item.product)
        
        for related_item in related_items:
            if related_item.product not in bundle_recommendations:
                bundle_recommendations[related_item.product] = 0
            bundle_recommendations[related_item.product] += 1
    
    # Sort bundle recommendations by frequency
    sorted_bundles = sorted(bundle_recommendations.items(), key=lambda x: x[1], reverse=True)[:5]  # Top 5 bundles
    
    return sorted_bundles

def display_bundle_recommendations(request):
    user_id = request.user.id
    bundles = recommend_bundles(user_id)
    return render(request, 'store/bundle_recommendations.html', {'bundles': bundles})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sklearn.linear_model import LinearRegression
import numpy as np

clv_model = LinearRegression()

def predict_clv(customer_id):
    try:
        customer = User.objects.get(pk=customer_id)
        profile = Profile.objects.get(user=customer)

        customer_data = np.array([[profile.purchase_count, profile.age, profile.total_spent]])

        clv_prediction = clv_model.predict(customer_data)

        return clv_prediction

    except User.DoesNotExist:
        return None
    except Profile.DoesNotExist:
        return None

@login_required
def display_clv_prediction(request):
    customer_id = request.user.id
    clv = predict_clv(customer_id)

    return render(request, 'store/clv_prediction.html', {'clv': clv})


import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Product
import cloudinary.uploader
import requests
from io import BytesIO
from PIL import Image

@csrf_exempt
def image_search(request):
    results = None
    if request.method == 'POST' and 'image' in request.FILES:
        image = request.FILES['image']

        # Save the uploaded image to Cloudinary
        upload_result = cloudinary.uploader.upload(image)
        image_url = upload_result.get('url')

        if image_url:
            # Fetch the image from the URL
            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = np.array(Image.open(BytesIO(response.content)))

                if image_data.size > 0:
                    # Extract features from the image data
                    features = extract_image_features(image_data)

                    # Find similar products
                    results = find_similar_products(features)
                else:
                    print("Empty image data received from Cloudinary.")
            else:
                print("Failed to retrieve image from Cloudinary.")
        else:
            print("Failed to upload image to Cloudinary.")

    return render(request, 'store/image_search.html', {'results': results})

def extract_image_features(image_data):
    image = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    image = cv2.resize(image, (100, 100)).flatten()
    return image

def find_similar_products(query_features):
    products = Product.objects.exclude(image__isnull=True).exclude(image__exact='')
    similar_products = []

    for product in products:
        # Fetch the product image from Cloudinary
        response = requests.get(product.image.url)
        if response.status_code == 200:
            product_image_data = np.array(Image.open(BytesIO(response.content)))
            product_features = extract_image_features(product_image_data)

            # Calculate similarity
            similarity = cosine_similarity([query_features], [product_features])

            # If the similarity is above a threshold, add to the similar products list
            if similarity > 0.8:  # Adjust the threshold as needed
                similar_products.append(product)

    return similar_products

from django.shortcuts import render
from .models import Product



# enhnaced security monitoring
from sklearn.ensemble import IsolationForest
import numpy as np

def anomaly_detection(logs):
    if len(logs) < 2:
        return []

    # Convert logs to a feature matrix
    features = np.array([[log.timestamp.timestamp(), len(log.event_description)] for log in logs])

    # Train IsolationForest
    clf = IsolationForest(contamination=0.1)  # Adjust contamination according to your dataset
    clf.fit(features)
    predictions = clf.predict(features)

    # Identify anomalies
    anomalies = [logs[i] for i, pred in enumerate(predictions) if pred == -1]
    return anomalies

def monitor_security():
    logs = list(SecurityLog.objects.all())
    security_alerts = anomaly_detection(logs)
    return security_alerts


from django.shortcuts import render
from .models import SecurityLog

def security_monitor_view(request):
    alerts = monitor_security()
    return render(request, 'store/security_monitor.html', {'alerts': alerts})



# views.py

from django.shortcuts import render
from django.contrib.auth.models import User
from .utils import analyze_behavior

def user_behavior_analysis_view(request, user_id):
    user = User.objects.get(pk=user_id)
    behavior_patterns = analyze_behavior(user_id)
    return render(request, 'store/user_behavior_analysis.html', {'user': user, 'behavior_patterns': behavior_patterns})

# views.py

from django.shortcuts import render
from django.contrib.auth.models import User
from .utils import create_dynamic_page

def dynamic_landing_page_view(request, user_id):
    user = User.objects.get(pk=user_id)
    landing_page = create_dynamic_page(user_id)
    return render(request, 'store/dynamic_landing_page.html', {'user': user, 'landing_page': landing_page})


from django.shortcuts import render
from .models import SalesData, UserBehavior, SocialMediaInteraction, Product

def real_time_analytics(request):
    # Fetch real-time data (example using sales data and user behavior)
    sales_data = SalesData.objects.all()
    user_behavior_data = UserBehavior.objects.all()
    social_media_data = SocialMediaInteraction.objects.all()
    
    # Example analytics processing
    total_sales = sum(data.sales_quantity for data in sales_data)
    top_searches = UserBehavior.objects.order_by('-clicks')[:5]
    top_interactions = SocialMediaInteraction.objects.order_by('-interaction_strength')[:5]
    
    context = {
        'total_sales': total_sales,
        'top_searches': top_searches,
        'top_interactions': top_interactions,
    }
    
    return render(request, 'store/dashboard.html', context)



# views.py

from django.shortcuts import render
from .models import Product  # Adjust the import based on your model
from .utils import process_query  # Import your utility function

def search_view(request):
    query = request.GET.get('q', '')  # Use lowercase 'q' for query parameter
    voice_input = request.GET.get('voice_input', '')

    if voice_input:
        query = voice_input  # Use voice_input directly for simplicity

    print(f"Query: {query}")  # Debugging print statement

    # Process the query using your utility function
    processed_query = process_query(query)

    # Example: Fetch products based on the processed query
    products = Product.objects.filter(name__icontains=processed_query)

    # Group products by category (adjust based on your category logic)
    category_1_products = products.filter(category='1')
    category_2_products = products.filter(category='2')
    category_3_products = products.filter(category='3')
    category_4_products = products.filter(category='4')
    category_5_products = products.filter(category='5')

    context = {
        'query': query,
        'category_1_products': category_1_products,
        'category_2_products': category_2_products,
        'category_3_products': category_3_products,
        'category_4_products': category_4_products,
        'category_5_products': category_5_products,
    }

    return render(request, 'store/search_results.html', context)
