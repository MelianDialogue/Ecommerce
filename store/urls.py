from django.urls import path
from .views import (
    paypal_cancel,paypal_return,order_success,blog_detail,blog_list,create_blog_post,index, search, order_detail, leave_review, wishlist_detail,
    add_to_wishlist, remove_from_wishlist, cart_detail, add_to_cart,
    update_cart_item,blog_post_detail,faq_list,policy_page_detail, product_list, product_detail, add_product, checkout, order_history, remove_cart_item  # Import the new view
)
from ml.urls import urlpatterns as ml_urls

urlpatterns = [
    path('', index, name='home-url'),
    path('product_list/', product_list, name='product_list'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('add-product/', add_product, name='add_product'),
    path('checkout/<int:order_id>/', checkout, name='checkout'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order-history/', order_history, name='order_history'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:cart_item_id>/', update_cart_item, name='update_cart_item'),
    path('remove-cart-item/<int:cart_item_id>/', remove_cart_item, name='remove_cart_item'),  # New URL pattern
    path('cart/', cart_detail, name='cart_detail'),
    path('add_to_wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', wishlist_detail, name='wishlist_detail'),
    path('remove_from_wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('product/<int:product_id>/review/', leave_review, name='leave_review'),
    path('search/', search, name='search'),
    path('blog/<int:blog_post_id>/', blog_post_detail, name='blog_post_detail'),
    path('faq/', faq_list, name='faq_list'),
    path('policy/<int:policy_page_id>/', policy_page_detail, name='policy_page_detail'),

    path('create_blog_post/', create_blog_post, name='create_blog_post'),
    path('blog/', blog_list, name='blog_list'),

    path('create_blog_post/', create_blog_post, name='create_blog_post'),
    path('blog/<int:blog_post_id>/', blog_detail, name='blog_detail'),

    path('order-success/<int:order_id>/', order_success, name='order_success'),
    path('paypal-return/', paypal_return, name='paypal_return'),
    path('paypal-cancel/', paypal_cancel, name='paypal_cancel'),
]
urlpatterns += ml_urls