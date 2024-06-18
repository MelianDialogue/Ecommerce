# ml/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MLModels

class RecommendProducts(APIView):
    def get(self, request, user_id, format=None):
        recommendations = MLModels.recommend_products(user_id)
        return Response(recommendations, status=status.HTTP_200_OK)

class DynamicPricing(APIView):
    def get(self, request, product_id, format=None):
        price = MLModels.dynamic_pricing(product_id)
        return Response({"price": price}, status=status.HTTP_200_OK)

class CustomerSegmentation(APIView):
    def get(self, request, format=None):
        segments = MLModels.customer_segmentation()
        return Response(segments, status=status.HTTP_200_OK)

class ChurnPrediction(APIView):
    def get(self, request, format=None):
        predictions = MLModels.churn_prediction()
        return Response(predictions, status=status.HTTP_200_OK)

class FraudDetection(APIView):
    def post(self, request, format=None):
        transaction = request.data
        is_fraud = MLModels.fraud_detection(transaction)
        return Response({"is_fraud": is_fraud}, status=status.HTTP_200_OK)

class SentimentAnalysis(APIView):
    def post(self, request, format=None):
        review = request.data.get("review")
        sentiment = MLModels.sentiment_analysis(review)
        return Response({"sentiment": sentiment}, status=status.HTTP_200_OK)

class ForecastDemand(APIView):
    def get(self, request, format=None):
        forecast = MLModels.forecast_demand()
        return Response(forecast, status=status.HTTP_200_OK)

class UnderstandQuery(APIView):
    def post(self, request, format=None):
        query = request.data.get("query")
        keywords = MLModels.understand_query(query)
        return Response(keywords, status=status.HTTP_200_OK)

class ImageSearch(APIView):
    def post(self, request, format=None):
        image = request.data.get("image")
        results = MLModels.image_search(image)
        return Response(results, status=status.HTTP_200_OK)

class PredictCLV(APIView):
    def get(self, request, customer_id, format=None):
        clv = MLModels.predict_clv(customer_id)
        return Response({"clv": clv}, status=status.HTTP_200_OK)

class RecommendBundles(APIView):
    def get(self, request, user_id, format=None):
        bundles = MLModels.recommend_bundles(user_id)
        return Response(bundles, status=status.HTTP_200_OK)

class PersonalizeEmail(APIView):
    def get(self, request, user_id, format=None):
        email_content = MLModels.personalize_email(user_id)
        return Response({"email_content": email_content}, status=status.HTTP_200_OK)

class AdaptiveRanking(APIView):
    def post(self, request, format=None):
        query = request.data.get("query")
        user_id = request.data.get("user_id")
        ranked_results = MLModels.adaptive_ranking(query, user_id)
        return Response(ranked_results, status=status.HTTP_200_OK)

class PersonalizeExperience(APIView):
    def get(self, request, user_id, format=None):
        ui_content = MLModels.personalize_experience(user_id)
        return Response({"ui_content": ui_content}, status=status.HTTP_200_OK)

class RecoverAbandonedCart(APIView):
    def get(self, request, user_id, format=None):
        recovery_email = MLModels.recover_abandoned_cart(user_id)
        return Response({"recovery_email": recovery_email}, status=status.HTTP_200_OK)

class VoiceSearch(APIView):
    def post(self, request, format=None):
        voice_input = request.data.get("voice_input")
        results = MLModels.voice_search(voice_input)
        return Response(results, status=status.HTTP_200_OK)

class PredictTrends(APIView):
    def get(self, request, format=None):
        trends = MLModels.predict_trends()
        return Response(trends, status=status.HTTP_200_OK)

class SupportChatbot(APIView):
    def post(self, request, format=None):
        user_query = request.data.get("query")
        response = MLModels.support_chatbot(user_query)
        return Response({"response": response}, status=status.HTTP_200_OK)

class MonitorSecurity(APIView):
    def get(self, request, format=None):
        security_alerts = MLModels.monitor_security()
        return Response(security_alerts, status=status.HTTP_200_OK)

class AnalyzeBehavior(APIView):
    def get(self, request, user_id, format=None):
        behavior_patterns = MLModels.analyze_behavior(user_id)
        return Response(behavior_patterns, status=status.HTTP_200_OK)

class CreateDynamicPage(APIView):
    def get(self, request, user_id, format=None):
        landing_page = MLModels.create_dynamic_page(user_id)
        return Response({"landing_page": landing_page}, status=status.HTTP_200_OK)

class AnalyzeSocialMedia(APIView):
    def get(self, request, user_id, format=None):
        recommendations = MLModels.analyze_social_media(user_id)
        return Response(recommendations, status=status.HTTP_200_OK)

class OptimizeSupplyChain(APIView):
    def get(self, request, format=None):
        forecast = MLModels.optimize_supply_chain()
        return Response(forecast, status=status.HTTP_200_OK)

class AnalyticsDashboard(APIView):
    def get(self, request, format=None):
        metrics = MLModels.analytics_dashboard()
        return Response(metrics, status=status.HTTP_200_OK)
