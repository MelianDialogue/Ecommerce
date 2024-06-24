from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Order, OrderItem, Review, Wishlist
from .forms import ReviewForm
from .payments import create_stripe_payment_intent, create_paypal_payment, execute_paypal_payment

# Views for product display and cart management
def index(request):
    products = Product.objects.all()[:4]
    return render(request, 'store/index.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


# views.py
def product_list(request):
    products = Product.objects.all()
    user_id = request.user.id if request.user.is_authenticated else None
    return render(request, 'store/product_list.html', {
        'products': products,
        'recommend_url': reverse('recommend_products', args=[user_id]) if user_id else None
    })



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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Cart, Order


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

# Views for handling checkout and payments
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


from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Order, OrderItem, Review, Wishlist
from .forms import ReviewForm
from .payments import create_stripe_payment_intent, create_paypal_payment, execute_paypal_payment



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

# views.py
@login_required
def leave_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    return render(request, 'store/leave_review.html', {'form': form, 'product': product})

def search(request):
    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains(query) if query else [])
    return render(request, 'store/product_list.html', {'query': query, 'results': results})

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
# views.py
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
# views.py
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



from sklearn.metrics.pairwise import cosine_similarity
from .models import Order, OrderItem, Product
import numpy as np

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




# machine learning implementation
# ecommerce/views.py
import requests
import logging
from django.conf import settings
from django.shortcuts import render
from .models import Product
import os


# Machine learning API
ML_API_URL = 'http://127.0.0.1:8000//ml'

logger = logging.getLogger(__name__)

def _make_ml_request(url, method="GET", data=None):
    try:
        if method == "POST":
            response = requests.post(url, json=data)
        else:
            response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error with ML API request: {e}")
        return {}
    except ValueError as e:
        logger.error(f"Error decoding JSON response: {e}")
        return {}

def get_recommendations(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/recommend_products/{user_id}/") or []

def get_dynamic_pricing(product_id):
    return _make_ml_request(f"{settings.ML_API_URL}/dynamic_pricing/{product_id}/")

def get_customer_segments():
    return _make_ml_request(f"{settings.ML_API_URL}/customer_segmentation/")

def get_churn_predictions():
    return _make_ml_request(f"{settings.ML_API_URL}/churn_prediction/")

def detect_fraud(transaction):
    return _make_ml_request(f"{settings.ML_API_URL}/fraud_detection/", method="POST", data=transaction)

def analyze_sentiment(review):
    return _make_ml_request(f"{settings.ML_API_URL}/sentiment_analysis/", method="POST", data={"review": review})

def get_demand_forecast():
    return _make_ml_request(f"{settings.ML_API_URL}/forecast_demand/")

def understand_user_query(query):
    return _make_ml_request(f"{settings.ML_API_URL}/understand_query/", method="POST", data={"query": query})

def image_based_search(image):
    return _make_ml_request(f"{settings.ML_API_URL}/image_search/", method="POST", data={"image": image})

def predict_customer_lifetime_value(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/predict_clv/{user_id}/")

def recommend_product_bundles(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/recommend_bundles/{user_id}/")

def personalize_email_content(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/personalize_email/{user_id}/")

def adaptive_search_ranking(query, user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/adaptive_ranking/", method="POST", data={"query": query, "user_id": user_id})

def personalize_user_experience(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/personalize_experience/{user_id}/")

def recover_abandoned_cart(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/recover_abandoned_cart/{user_id}/")

def process_voice_search(voice_input):
    return _make_ml_request(f"{settings.ML_API_URL}/voice_search/", method="POST", data={"voice_input": voice_input})

def predict_trends():
    return _make_ml_request(f"{settings.ML_API_URL}/predict_trends/")

def chatbot_support(user_query):
    return _make_ml_request(f"{settings.ML_API_URL}/support_chatbot/", method="POST", data={"query": user_query})

def monitor_website_security():
    return _make_ml_request(f"{settings.ML_API_URL}/monitor_security/")

def analyze_user_behavior(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/analyze_behavior/{user_id}/")

def create_dynamic_landing_page(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/create_dynamic_page/{user_id}/")

def analyze_social_media_activity(user_id):
    return _make_ml_request(f"{settings.ML_API_URL}/analyze_social_media/{user_id}/")

def optimize_supply_chain():
    return _make_ml_request(f"{settings.ML_API_URL}/optimize_supply_chain/")

def fetch_analytics_dashboard():
    return _make_ml_request(f"{settings.ML_API_URL}/analytics_dashboard/")

def product_list(request):
    products = Product.objects.all()
    context = {
        'products': products
    }

    if request.user.is_authenticated:
        user_id = request.user.id
        context.update({
            'recommended_products': Product.objects.filter(id__in=get_recommendations(user_id)),
            'bundled_recommendations': recommend_product_bundles(user_id),
            'personalized_email': personalize_email_content(user_id),
            'adaptive_ranking_results': adaptive_search_ranking(request.GET.get('query', ''), user_id),
            'personalized_experience': personalize_user_experience(user_id),
            'abandoned_cart_recovery': recover_abandoned_cart(user_id),
            'user_behavior': analyze_user_behavior(user_id),
            'dynamic_landing_page': create_dynamic_landing_page(user_id),
            'social_media_analysis': analyze_social_media_activity(user_id),
        })
    
    product_id = request.GET.get('product_id')
    customer_id = request.GET.get('customer_id')
    if product_id:
        context['dynamic_pricing'] = get_dynamic_pricing(product_id)
    if customer_id:
        context['predicted_clv'] = predict_customer_lifetime_value(customer_id)
    
    post_data = request.POST
    if post_data:
        if 'review' in post_data:
            context['sentiment_analysis'] = analyze_sentiment(post_data['review'])
        if 'query' in post_data:
            context['understood_query'] = understand_user_query(post_data['query'])
        if 'image' in post_data:
            context['image_search_results'] = image_based_search(post_data['image'])
        if 'voice_input' in post_data:
            context['voice_search_results'] = process_voice_search(post_data['voice_input'])
        if 'user_query' in post_data:
            context['chatbot_response'] = chatbot_support(post_data['user_query'])
        if 'transaction' in post_data:
            context['fraud_detection'] = detect_fraud(post_data['transaction'])
    
    context.update({
        'customer_segments': get_customer_segments(),
        'churn_predictions': get_churn_predictions(),
        'demand_forecast': get_demand_forecast(),
        'predicted_trends': predict_trends(),
        'security_alerts': monitor_website_security(),
        'supply_chain_optimization': optimize_supply_chain(),
        'real_time_analytics': fetch_analytics_dashboard(),
    })
    
    return render(request, 'store/product_list.html', context)


from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()
    recommended_products = []
    dynamic_pricing = {}
    voice_search_results = ""
    real_time_analytics = ""

    # Assuming user authentication and ID retrieval
    if request.user.is_authenticated:
        user_id = request.user.id
        # Fetch recommended products
        recommended_products = Product.objects.filter(id__in=(get_recommendations(user_id) or []))
    
    # Fetch dynamic pricing for each product
    for product in products:
        dynamic_pricing[product.id] = get_dynamic_pricing(product.id) or product.price

    # Handle POST request for voice search
    if request.method == "POST":
        query = request.POST.get('query', '')
        voice_search_results = process_voice_search(query) if query else ""

    # Fetch real-time analytics data
    real_time_analytics = fetch_analytics_dashboard()

    # Prepare context dictionary
    context = {
        'products': products,
        'recommended_products': recommended_products,
        'dynamic_pricing': dynamic_pricing,
        'voice_search_results': voice_search_results,
        'real_time_analytics': real_time_analytics,
        'customer_segments': get_customer_segments(),
        'churn_predictions': get_churn_predictions(),
        'fraud_detection': detect_fraud({'transaction_id': 1, 'amount': 100.0, 'fraud': 0}),
        'sentiment_analysis': analyze_sentiment("Great product, very satisfied."),
        'demand_forecast': get_demand_forecast(),
        'understood_query': understand_user_query("How can I help you today?"),
        'image_search_results': image_based_search("image_file.jpg"),
        'predicted_clv': predict_customer_lifetime_value(user_id),
        'bundled_recommendations': recommend_product_bundles(user_id),
        'personalized_email': personalize_email_content(user_id),
        'adaptive_ranking_results': adaptive_search_ranking("product query", user_id),
        'personalized_experience': personalize_user_experience(user_id),
        'abandoned_cart_recovery': recover_abandoned_cart(user_id),
        'predicted_trends': predict_trends(),
        'chatbot_response': chatbot_support("How can I assist you?"),
        'security_alerts': monitor_website_security(),
        'user_behavior': analyze_user_behavior(user_id),
        'dynamic_landing_page': create_dynamic_landing_page(user_id),
        'social_media_analysis': analyze_social_media_activity(user_id),
        'supply_chain_optimization': optimize_supply_chain(),
    }
    
    return render(request, 'store/product_list.html', context)


# views.py
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
    return render(request, 'store/recommendations.html', {'recommendations': recommendations})

# utils.py
def get_current_demand(product_id):
    # Placeholder logic for current demand
    # Implement the logic to fetch current demand for the product
    product = Product.objects.get(id=product_id)
    return product.demand

def get_competition_price(product_id):
    # Placeholder logic for competition price
    # Implement the logic to fetch competition price for the product
    product = Product.objects.get(id=product_id)
    return product.competition_price

from decimal import Decimal

def calculate_dynamic_price(demand, competition):
    # Placeholder logic for calculating dynamic price
    # Implement the actual pricing algorithm here
    base_price = 100.0  # Example base price as float
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

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count


def fetch_customer_data_with_churn():
    customers = User.objects.all().values('id', 'date_joined', 'profile__age')
    customer_data = pd.DataFrame(customers)
    
    purchase_data = (
        Order.objects.values('user_id')
        .annotate(total_spent=Sum('total_price'), purchase_count=Count('id'))
        .order_by('user_id')
    )
    purchase_df = pd.DataFrame(purchase_data)
    
    # Assuming you have a way to determine if a customer has churned
    # For example, customers who haven't made a purchase in the last 6 months
    churn_data = determine_churn()  # This function needs to be implemented
    
    customer_data = customer_data.merge(purchase_df, left_on='id', right_on='user_id', how='left').fillna(0)
    customer_data = customer_data.merge(churn_data, left_on='id', right_on='user_id', how='left').fillna(0)
    
    return customer_data



from sklearn.metrics import classification_report
from sklearn.utils import shuffle

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
    customer_data = determine_churn()
    
    # Check the distribution of churn labels
    print(customer_data['churn'].value_counts())
    
    # Shuffle the dataset to ensure randomness
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
    print(classification_report(y_test, y_pred))  # Use classification report for evaluation
    
    return model, scaler




# Predict churn for all customers
def predict_churn():
    model, scaler = train_churn_model()
    
    customer_data = fetch_customer_data_with_churn()
    
    features = ['profile__age', 'total_spent', 'purchase_count']
    X = customer_data[features]
    X_scaled = scaler.transform(X)
    
    customer_data['churn_risk'] = model.predict_proba(X_scaled)[:, 1]
    
    return customer_data[['id', 'churn_risk']]


from django.shortcuts import render

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.utils import timezone

from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from .models import Order

@login_required
def churn_prediction_view(request):
    profiles = Profile.objects.all()
    
    # Create a DataFrame for churn prediction
    churn_data = {
        'profile__age': [profile.age for profile in profiles],
        'total_spent': [profile.total_spent for profile in profiles],
        'purchase_count': [profile.purchase_count for profile in profiles],
        'churn': [profile.churn for profile in profiles],
    }
    
    import pandas as pd
    churn_df = pd.DataFrame(churn_data)
    
    if churn_df.empty:
        return render(request, 'store/error_page.html', {'message': 'No data available for churn prediction.'})
    
    # Replace NaN values in churn_df with the mean of each column
    churn_df.fillna(churn_df.mean(), inplace=True)
    
    X = churn_df[['profile__age', 'total_spent', 'purchase_count']]  # Adjust columns as per your DataFrame structure
    y = churn_df['churn']
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create a pipeline with an imputer and logistic regression model
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='mean')),  # Replace NaN with mean of each column
        ('logreg', LogisticRegression()),
    ])
    
    # Fit the pipeline on training data
    pipeline.fit(X_train, y_train)
    
    # Predict churn on test data
    y_pred = pipeline.predict(X_test)
    
    # Evaluate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    
    return render(request, 'store/churn_prediction.html', {'accuracy': accuracy})


# Assuming necessary imports and models are already defined

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sklearn.ensemble import IsolationForest
import pandas as pd
from .models import Order, CartItem
from .models import Transaction 

# store/views.py

def fetch_transactions():
    # Replace with your logic to fetch transaction data from database or API
    transactions = Transaction.objects.all()  # Example: Assuming Transaction is your model
    return transactions


@login_required
def detect_fraud_view(request):
    transactions = fetch_transactions()  # Assuming you implement this function to fetch transaction data
    
    if transactions is None or len(transactions) == 0:
        return render(request, 'store/error_page.html', {'message': 'No transactions available.'})
    
    # Convert transactions into a DataFrame
    transaction_data = {
        'amount': [transaction.total_price for transaction in transactions],  # Adjust based on your transaction model
        'product_name': [transaction.product.name for transaction in transactions],  # Example of additional data you might include
    }
    
    transactions_df = pd.DataFrame(transaction_data)
    
    # Implement Isolation Forest for anomaly detection
    isolation_forest = IsolationForest(contamination=0.1)  # Adjust contamination based on expected fraud rate
    
    # Fit the model
    isolation_forest.fit(transactions_df[['amount']])
    
    # Predict anomalies (fraudulent transactions)
    transactions_df['fraud_score'] = isolation_forest.decision_function(transactions_df[['amount']])
    
    # Determine fraud based on a threshold
    threshold = -0.5  # Adjust threshold as needed
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
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def forecast_demand(sales_data):
    # Convert sales data to a DataFrame
    df = pd.DataFrame(sales_data)
    df['sales_date'] = pd.to_datetime(df['sales_date'])
    df = df.set_index('sales_date')

    # Perform time series analysis
    model = ExponentialSmoothing(df['sales_quantity'], trend='add', seasonal='add', seasonal_periods=12)
    fit = model.fit()

    # Forecast for the next 12 periods
    forecast = fit.forecast(12)
    return forecast

from django.shortcuts import render
from django.http import HttpResponse
from .models import SalesData
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def forecast_demand(sales_data):
    # Convert sales data to a DataFrame
    df = pd.DataFrame(sales_data)
    
    # Debugging: Print the first few rows of the DataFrame
    print(df.head())
    
    df['sales_date'] = pd.to_datetime(df['sales_date'])
    df = df.set_index('sales_date')

    # Perform time series analysis
    model = ExponentialSmoothing(df['sales_quantity'], trend='add', seasonal='add', seasonal_periods=12)
    fit = model.fit()

    # Forecast for the next 12 periods
    forecast = fit.forecast(12)
    return forecast

def forecast_demand_view(request):
    # Fetch sales data from the database
    sales_data = SalesData.objects.all().values('sales_date', 'sales_quantity')

    # Debugging: Print the first few rows of the sales_data
    print(list(sales_data))
    
    # Forecast demand
    try:
        demand_forecast = forecast_demand(sales_data)
    except KeyError as e:
        return HttpResponse(f"KeyError: {e}", status=400)
    
    context = {
        'demand_forecast': demand_forecast
    }
    return render(request, 'store/forecast_demand.html', context)



import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def understand_query(query):
    doc = nlp(query)
    keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]
    return keywords

from django.shortcuts import render
from .models import Product

def search_view(request):
    query = request.GET.get('q', '')
    keywords = understand_query(query)
    
    # Search for products containing any of the keywords in their name or description
    products = Product.objects.filter(
        name__icontains=keywords[0]  # Simplified for demonstration; refine as needed
    )
    for keyword in keywords[1:]:
        products = products | Product.objects.filter(
            name__icontains=keyword
        )

    context = {
        'query': query,
        'keywords': keywords,
        'products': products
    }
    return render(request, 'store/search_results.html', context)


import numpy as np
import tensorflow as tf
import cv2
from sklearn.neighbors import NearestNeighbors
from .models import Product

# Load MobileNet model
model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, pooling='avg')

def preprocess_image(image):
    # Convert image to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Resize image to 224x224
    image = cv2.resize(image, (224, 224))
    # Convert to array and expand dimensions
    image = tf.keras.preprocessing.image.img_to_array(image)
    image = np.expand_dims(image, axis=0)
    # Preprocess the image
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    return image

def extract_image_features(image):
    preprocessed_image = preprocess_image(image)
    features = model.predict(preprocessed_image)
    return features

def find_similar_products(features, n_neighbors=5):
    # Load all product images and extract features
    products = Product.objects.all()
    product_features = []
    product_ids = []

    for product in products:
        if product.image:
            image_path = product.image.url
            image = cv2.imread(image_path)
            if image is not None:
                product_features.append(extract_image_features(image))
                product_ids.append(product.id)

    # Stack features and fit NearestNeighbors model
    product_features = np.vstack(product_features)
    nn_model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine').fit(product_features)
    distances, indices = nn_model.kneighbors(features)

    # Get product IDs of similar products
    similar_products = [products[idx] for idx in indices[0]]
    return similar_products


from django.shortcuts import render
from django.core.files.uploadedfile import UploadedFile
from .utils import extract_image_features, find_similar_products

def image_search_view(request):
    if request.method == 'POST' and request.FILES['image']:
        uploaded_image = request.FILES['image']
        image = cv2.imdecode(np.fromstring(uploaded_image.read(), np.uint8), cv2.IMREAD_UNCHANGED)

        # Extract features and find similar products
        features = extract_image_features(image)
        similar_products = find_similar_products(features)

        context = {
            'similar_products': similar_products
        }
        return render(request, 'store/image_search_results.html', context)

    return render(request, 'store/image_search.html')


import pandas as pd
from sklearn.linear_model import LinearRegression
from .models import Customer, Transaction

# Dummy model for example purposes
# In practice, replace with your pre-trained model
clv_model = LinearRegression()

def load_and_prepare_data():
    # Load your historical customer data and prepare it for training
    # This is a dummy example with random data
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

# Train the model (in practice, this would be done offline and the model would be loaded)
train_clv_model()


from django.shortcuts import render, get_object_or_404
from .models import Customer
from .utils import predict_clv

def predict_clv_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    clv = predict_clv(customer_id)

    context = {
        'customer': customer,
        'clv': clv
    }
    return render(request, 'store/predict_clv.html', context)


import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from .models import Customer, Transaction, Product

def load_purchase_history():
    transactions = Transaction.objects.all()
    data = []
    for transaction in transactions:
        data.append({
            'transaction_id': transaction.id,
            'product_id': transaction.product.id,
            'customer_id': transaction.customer.id
        })
    df = pd.DataFrame(data)
    return df

def association_rule_mining(purchase_history):
    basket = (purchase_history.groupby(['transaction_id', 'product_id'])['product_id']
              .count().unstack().reset_index().fillna(0).set_index('transaction_id'))
    basket = basket.applymap(lambda x: 1 if x > 0 else 0)
    
    frequent_itemsets = apriori(basket, min_support=0.01, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
    
    rules = rules.sort_values(['confidence', 'lift'], ascending=[False, False])
    
    return rules

def recommend_bundles(user_id):
    try:
        customer = Customer.objects.get(id=user_id)
    except Customer.DoesNotExist:
        return None

    purchase_history = load_purchase_history()
    rules = association_rule_mining(purchase_history)
    
    user_transactions = purchase_history[purchase_history['customer_id'] == user_id]
    user_products = user_transactions['product_id'].unique()
    
    recommendations = []
    for product in user_products:
        antecedents = rules[rules['antecedents'].apply(lambda x: product in x)]
        for _, row in antecedents.iterrows():
            recommendations.extend(list(row['consequents']))
    
    recommendations = list(set(recommendations) - set(user_products))
    recommended_products = Product.objects.filter(id__in=recommendations)
    
    return recommended_products

from django.shortcuts import render, get_object_or_404
from .models import Customer
from .utils import recommend_bundles

def recommend_bundles_view(request, user_id):
    customer = get_object_or_404(Customer, id=user_id)
    bundles = recommend_bundles(user_id)

    context = {
        'customer': customer,
        'bundles': bundles
    }
    return render(request, 'store/recommend_bundles.html', context)
