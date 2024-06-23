# customer/utils.py
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import numpy as np

def segment_customers(customer_data):
    # Extract relevant features for clustering
    X = np.array([[customer['age'], customer['income'], customer['spending_score']] for customer in customer_data])

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=3, random_state=42)  # Example: 3 clusters
    segments = kmeans.fit_predict(X)

    return segments.tolist()  # Convert numpy array to list for JSON serialization

def predict_churn(customer_features, churn_target):
    # Extract relevant features for churn prediction
    X = np.array([[customer['age'], customer['income'], customer['spending_score']] for customer in customer_features])
    y = np.array(churn_target)

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize logistic regression model
    model = LogisticRegression(random_state=42)

    # Fit the model
    model.fit(X_train, y_train)

    # Predict churn probabilities
    churn_probabilities = model.predict_proba(X_test)[:, 1]

    return churn_probabilities.tolist()  # Convert numpy array to list for JSON serialization

