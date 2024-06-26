from django.urls import path
from .views import (
    RecommendProducts, DynamicPricing, CustomerSegmentation, ChurnPrediction,
    FraudDetection, SentimentAnalysis, ForecastDemand, UnderstandQuery, ImageSearch,
    PredictCLV, RecommendBundles, PersonalizeEmail, AdaptiveRanking, PersonalizeExperience,
    RecoverAbandonedCart, VoiceSearch, PredictTrends, SupportChatbot, MonitorSecurity,
    AnalyzeBehavior, CreateDynamicPage, AnalyzeSocialMedia, OptimizeSupplyChain,
    AnalyticsDashboard
)

urlpatterns = [
    path('recommend_products/<int:user_id>/', RecommendProducts.as_view(), name='recommend_products'),
    path('dynamic_pricing/<int:product_id>/', DynamicPricing.as_view(), name='dynamic_pricing'),
    path('customer_segmentation/', CustomerSegmentation.as_view(), name='customer_segmentation'),
    path('churn_prediction/', ChurnPrediction.as_view(), name='churn_prediction'),
    path('fraud_detection/', FraudDetection.as_view(), name='fraud_detection'),
    path('sentiment_analysis/', SentimentAnalysis.as_view(), name='sentiment_analysis'),
    path('forecast_demand/', ForecastDemand.as_view(), name='forecast_demand'),
    path('understand_query/', UnderstandQuery.as_view(), name='understand_query'),
    path('image_search/', ImageSearch.as_view(), name='image_search'),
    path('predict_clv/<int:customer_id>/', PredictCLV.as_view(), name='predict_clv'),
    path('recommend_bundles/<int:user_id>/', RecommendBundles.as_view(), name='recommend_bundles'),
    path('personalize_email/<int:user_id>/', PersonalizeEmail.as_view(), name='personalize_email'),
    path('adaptive_ranking/', AdaptiveRanking.as_view(), name='adaptive_ranking'),
    path('personalize_experience/<int:user_id>/', PersonalizeExperience.as_view(), name='personalize_experience'),
    path('recover_abandoned_cart/<int:user_id>/', RecoverAbandonedCart.as_view(), name='recover_abandoned_cart'),
    path('voice_search/', VoiceSearch.as_view(), name='voice_search'),
    path('predict_trends/', PredictTrends.as_view(), name='predict_trends'),
    path('support_chatbot/', SupportChatbot.as_view(), name='support_chatbot'),
    path('monitor_security/', MonitorSecurity.as_view(), name='monitor_security'),
    path('analyze_behavior/<int:user_id>/', AnalyzeBehavior.as_view(), name='analyze_behavior'),
    path('create_dynamic_page/<int:user_id>/', CreateDynamicPage.as_view(), name='create_dynamic_page'),
    path('analyze_social_media/<int:user_id>/', AnalyzeSocialMedia.as_view(), name='analyze_social_media'),
    path('optimize_supply_chain/', OptimizeSupplyChain.as_view(), name='optimize_supply_chain'),
    path('analytics_dashboard/', AnalyticsDashboard.as_view(), name='analytics_dashboard'),
]
