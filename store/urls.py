from django.urls import path
from .views import ( analyze_sentiment_view,
                     detect_fraud_view, churn_prediction_view, customer_segmentation_view, dynamic_price_update, recommend_products, paypal_cancel,paypal_return,order_success,blog_detail,blog_list,create_blog_post,index, search, order_detail, leave_review, wishlist_detail,
                     add_to_wishlist, remove_from_wishlist, cart_detail, add_to_cart,
                     update_cart_item,blog_post_detail,faq_list,policy_page_detail,
                     product_list, product_detail, add_product,
                     checkout, order_history, remove_cart_item, security_monitor_view, user_behavior_analysis_view

                     )
from . import views



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
    path('recommendations/<int:user_id>/', recommend_products, name='recommend_products'),
    path('dynamic_price_update/<int:product_id>/', dynamic_price_update, name='dynamic_price_update'),
    path('customer_segmentation/', customer_segmentation_view, name='customer_segmentation'),
    path('churn_prediction/', churn_prediction_view, name='churn_prediction'),
    path('detect_fraud/', detect_fraud_view, name='detect_fraud'),
    path('analyze_sentiment/', analyze_sentiment_view, name='analyze_sentiment'),
    path('forecasts/', views.forecast_list, name='forecast_list'),
    path('trends/', views.trends_view, name='trends'),

    path('recover/<int:user_id>/', views.recover_abandoned_cart, name='recover_abandoned_cart'),

    path('personalized/', views.personalized_view, name='personalized_view'),


    path('send-email/', views.send_personalized_email, name='send_personalized_email'),

    path('recommend-bundles/', views.display_bundle_recommendations, name='recommend_bundles'),

    path('predict-clv/', views.display_clv_prediction, name='predict_clv'),

    path('image-search/', views.image_search, name='image_search'),

    path('search/', views.search_products, name='search_products'),

    path('security-monitor/', security_monitor_view, name='security_monitor'),

    path('user-behavior/<int:user_id>/', user_behavior_analysis_view, name='user_behavior_analysis'),

    path('dynamic-landing-page/<int:user_id>/', views.dynamic_landing_page_view, name='dynamic_landing_page'),

    path('analytics/', views.real_time_analytics, name='real_time_analytics'),

    path('voice_search/', views.voice_search, name='voice_search'),

    path('search/', views.search_view, name='search'),
]