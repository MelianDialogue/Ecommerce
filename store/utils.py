from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np

def segment_customers(customer_data):
    X = np.array([[customer['age'], customer['income'], customer['spending_score']] for customer in customer_data])

    
    kmeans = KMeans(n_clusters=3, random_state=42)
    segments = kmeans.fit_predict(X)

    return segments.tolist()

def predict_churn(customer_features, churn_target):
    
    X = np.array([[customer['age'], customer['income'], customer['spending_score']] for customer in customer_features])
    y = np.array(churn_target)

    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

   
    model = LogisticRegression(random_state=42)

   
    model.fit(X_train, y_train)

  
    churn_probabilities = model.predict_proba(X_test)[:, 1]

    return churn_probabilities.tolist()  # Convert numpy array to list for JSON serialization





# utils.py

import numpy as np
from .models import UserBehavior

def behavior_model(user_behavior_data):
    # Example: Compute average clicks and time spent
    if not user_behavior_data:
        return {'average_clicks': 0, 'average_time_spent': 0}
    
    clicks = [behavior.clicks for behavior in user_behavior_data]
    time_spent = [behavior.time_spent for behavior in user_behavior_data]
    
    average_clicks = np.mean(clicks)
    average_time_spent = np.mean(time_spent)
    
    return {
        'average_clicks': average_clicks,
        'average_time_spent': average_time_spent
    }

def analyze_behavior(user_id):
    user_behavior_data = UserBehavior.objects.filter(user_id=user_id)
    behavior_patterns = behavior_model(user_behavior_data)
    return behavior_patterns


# utils.py

from .models import UserInterest

def get_user_interests(user_id):
    interests = UserInterest.objects.filter(user_id=user_id).values_list('interest', flat=True)
    return list(interests)

def generate_landing_page(interests):
    content = f"<h1>Welcome!</h1><p>Based on your interests in {', '.join(interests)}, we recommend the following:</p>"
    # Add more logic to generate content dynamically based on interests
    return content

def create_dynamic_page(user_id):
    interests = get_user_interests(user_id)
    landing_page = generate_landing_page(interests)
    return landing_page


# utils.py
def process_query(query):
    # Example processing logic (replace with your actual processing logic)
    processed_query = query.lower()  # Convert query to lowercase
    return processed_query
