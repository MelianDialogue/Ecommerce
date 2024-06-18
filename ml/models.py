# ml/models.py

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from django.conf import settings

class MLModels:
    @staticmethod
    def recommend_products(user_id):
        user_item_matrix = pd.DataFrame(settings.USER_ITEM_INTERACTIONS)
        user_index = user_item_matrix.index.get_loc(user_id)
        similarity_matrix = cosine_similarity(user_item_matrix)
        similar_users = similarity_matrix[user_index]
        
        similar_users_indices = similar_users.argsort()[-2:-11:-1]
        recommended_products = []
        for index in similar_users_indices:
            top_products = user_item_matrix.iloc[index].sort_values(ascending=False).index.tolist()
            recommended_products.extend(top_products)
        
        return list(set(recommended_products))

    @staticmethod
    def dynamic_pricing(product_id):
        historical_data = pd.DataFrame(settings.HISTORICAL_PRICES)
        demand_data = pd.DataFrame(settings.DEMAND_DATA)
        
        current_demand = demand_data[demand_data['product_id'] == product_id]['demand'].values[0]
        competitor_prices = historical_data[historical_data['product_id'] == product_id]['competitor_price'].values
        
        base_price = np.mean(competitor_prices)
        dynamic_price = base_price * (1 + (current_demand / 100))
        
        return round(dynamic_price, 2)

    @staticmethod
    def customer_segmentation():
        data = pd.DataFrame(settings.CUSTOMER_DATA)
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        kmeans = KMeans(n_clusters=5)
        segments = kmeans.fit_predict(data_scaled)
        return segments.tolist()

    @staticmethod
    def churn_prediction():
        data = pd.DataFrame(settings.CUSTOMER_FEATURES)
        target = settings.CUSTOMER_CHURN_TARGET
        model = LogisticRegression()
        model.fit(data, target)
        predictions = model.predict(data)
        return predictions.tolist()

    @staticmethod
    def fraud_detection(transaction):
        data = pd.DataFrame(settings.TRANSACTION_DATA)
        model = IsolationForest(contamination=0.01)
        model.fit(data)
        transaction_df = pd.DataFrame([transaction])
        fraud_score = model.predict(transaction_df)
        return fraud_score[0] == -1

    @staticmethod
    def sentiment_analysis(review):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(settings.REVIEWS)
        review_vec = vectorizer.transform([review])
        sentiment_scores = cosine_similarity(review_vec, tfidf_matrix).flatten()
        avg_sentiment = np.mean(sentiment_scores)
        return "positive" if avg_sentiment > 0.5 else "negative"

    @staticmethod
    def forecast_demand():
        demand_data = pd.DataFrame(settings.DEMAND_DATA)
        demand_data['date'] = pd.to_datetime(demand_data['date'])
        demand_data.set_index('date', inplace=True)
        demand_series = demand_data['demand']
        
        model = Sequential([
            Dense(10, activation='relu', input_shape=(1,)),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        
        x = np.arange(len(demand_series)).reshape(-1, 1)
        y = demand_series.values
        
        model.fit(x, y, epochs=100, verbose=0)
        
        future = np.arange(len(demand_series), len(demand_series) + 10).reshape(-1, 1)
        forecast = model.predict(future)
        
        return forecast.flatten().tolist()

    @staticmethod
    def understand_query(query):
        vectorizer = TfidfVectorizer()
        query_vec = vectorizer.fit_transform([query])
        features = vectorizer.get_feature_names_out()
        
        important_keywords = [features[i] for i in query_vec.toarray()[0].argsort()[-2:][::-1]]
        return important_keywords

    @staticmethod
    def image_search(image):
        model = tf.keras.applications.VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        image_features = model.predict(image)
        
        return ["product1", "product2"]

    @staticmethod
    def predict_clv(customer_id):
        customer_data = pd.DataFrame(settings.CUSTOMER_DATA)
        clv_model = RandomForestRegressor()
        clv_model.fit(customer_data.drop(columns=['clv']), customer_data['clv'])
        clv = clv_model.predict([customer_data.loc[customer_id]])
        return clv[0]

    @staticmethod
    def recommend_bundles(user_id):
        purchase_history = pd.DataFrame(settings.PURCHASE_HISTORY)
        from mlxtend.frequent_patterns import apriori, association_rules
        
        frequent_itemsets = apriori(purchase_history, min_support=0.01, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1.0)
        user_history = purchase_history.loc[user_id]
        bundle_recommendations = []
        
        for _, row in rules.iterrows():
            if any(item in user_history for item in row['antecedents']):
                bundle_recommendations.extend(row['consequents'])
        
        return list(set(bundle_recommendations))

    @staticmethod
    def personalize_email(user_id):
        preferences = settings.USER_PREFERENCES[user_id]
        email_content = f"Hi! Based on your preferences for {preferences}, we have some exciting offers for you!"
        return email_content

    @staticmethod
    def adaptive_ranking(query, user_id):
        user_behavior = pd.DataFrame(settings.USER_BEHAVIOR)
        query_vector = TfidfVectorizer().fit_transform([query]).toarray()
        
        results = pd.DataFrame(settings.SEARCH_RESULTS)
        results['score'] = cosine_similarity(results['features'].tolist(), query_vector).flatten()
        results = results.sort_values(by=['score'], ascending=False)
        
        return results['product_id'].tolist()

    @staticmethod
    def personalize_experience(user_id):
        user_profile = settings.REAL_TIME_PROFILES[user_id]
        personalized_ui = f"Displaying personalized UI for user {user_id} with profile {user_profile}"
        return personalized_ui

    @staticmethod
    def recover_abandoned_cart(user_id):
        abandoned_cart = settings.ABANDONED_CARTS[user_id]
        recovery_email = f"Hi! You left items in your cart: {abandoned_cart}. Come back and complete your purchase!"
        return recovery_email

    @staticmethod
    def voice_search(voice_input):
        from speech_recognition import Recognizer, AudioFile
        
        recognizer = Recognizer()
        with AudioFile(voice_input) as source:
            audio = recognizer.record(source)
        
        query = recognizer.recognize_google(audio)
        results = MLModels.adaptive_ranking(query, None)
        
        return results

    @staticmethod
    def predict_trends():
        sales_data = pd.DataFrame(settings.SALES_DATA)
        social_media_data = pd.DataFrame(settings.SOCIAL_MEDIA_DATA)
        
        combined_data = pd.concat([sales_data, social_media_data], axis=1)
        trend_model = RandomForestRegressor()
        trend_model.fit(combined_data.drop(columns=['trend']), combined_data['trend'])
        trends = trend_model.predict(combined_data)
        
        return trends.tolist()

    @staticmethod
    def support_chatbot(user_query):
        responses = settings.CHATBOT_RESPONSES
        response = responses.get(user_query, "I'm sorry, I didn't understand that. Can you rephrase?")
        return response

    @staticmethod
    def monitor_security():
        security_logs = pd.DataFrame(settings.SECURITY_LOGS)
        anomaly_detection_model = IsolationForest(contamination=0.01)
        anomaly_detection_model.fit(security_logs)
        
        anomalies = anomaly_detection_model.predict(security_logs)
        security_alerts = security_logs[anomalies == -1]
        
        return security_alerts.tolist()

    @staticmethod
    def analyze_behavior(user_id):
        user_data = pd.DataFrame(settings.USER_DATA)
        behavior_model = KMeans(n_clusters=5)
        behavior_patterns = behavior_model.fit_predict(user_data)
        
        return behavior_patterns[user_id]

    @staticmethod
    def create_dynamic_page(user_id):
        interests = settings.USER_INTERESTS[user_id]
        landing_page = f"Dynamic landing page for user {user_id} with interests {interests}"
        return landing_page

    @staticmethod
    def analyze_social_media(user_id):
        social_data = pd.DataFrame(settings.SOCIAL_MEDIA_DATA)
        social_media_model = RandomForestRegressor()
        social_media_model.fit(social_data.drop(columns=['recommendations']), social_data['recommendations'])
        recommendations = social_media_model.predict([social_data.loc[user_id]])
        
        return recommendations.tolist()

    @staticmethod
    def optimize_supply_chain():
        supply_chain_data = pd.DataFrame(settings.SUPPLY_CHAIN_DATA)
        supply_chain_model = RandomForestRegressor()
        supply_chain_model.fit(supply_chain_data.drop(columns=['forecast']), supply_chain_data['forecast'])
        supply_chain_forecast = supply_chain_model.predict(supply_chain_data)
        
        return supply_chain_forecast.tolist()

    @staticmethod
    def analytics_dashboard():
        analytics_data = pd.DataFrame(settings.ANALYTICS_DATA)
        dashboard_model = RandomForestRegressor()
        dashboard_model.fit(analytics_data.drop(columns=['metrics']), analytics_data['metrics'])
        metrics = dashboard_model.predict(analytics_data)
        
        return metrics.tolist()
