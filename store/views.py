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

