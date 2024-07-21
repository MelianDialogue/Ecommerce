from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from store.custom_admin import custom_admin_site
from store.views import admin_customer_segmentation_view, churn_prediction_view, detect_fraud_view, \
    analyze_sentiment_view, display_bundle_recommendations, security_monitor_view, user_behavior_analysis_view, \
    real_time_analytics, forecast_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', custom_admin_site.urls),
    path('user_app/', include('user_app.urls')),
    path('', include('store.urls')),
    path('customer-segmentation/', admin_customer_segmentation_view, name='admin_customer_segmentation'),
    path('churn-prediction/', churn_prediction_view, name='churn_prediction'),
    path('detect_fraud/', detect_fraud_view, name='detect_fraud'),
    path('analyze_sentiment/', analyze_sentiment_view, name='analyze_sentiment'),
    path('recommend-bundles/', display_bundle_recommendations, name='recommend_bundles'),
    path('security-monitor/', security_monitor_view, name='security_monitor'),
    path('user-behavior/', user_behavior_analysis_view, name='user_behavior_analysis'),
    path('analytics/', real_time_analytics, name='real_time_analytics'),
    path('forecasts/', forecast_list, name='forecast_list'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
