import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# Define the path for the model file
# MODEL_FILE_PATH = 'random_forest_model.pkl'
# DATA_FILE_PATH = 'hemophilia_patient_data.csv'
# Define the path for the model file and data file
MODEL_FILE_PATH = os.path.join(os.path.dirname(__file__), 'random_forest_model.pkl')
DATA_FILE_PATH = os.path.join(os.path.dirname(__file__), 'hemophilia_patient_data.csv')


# Function to train the model
def train_model(data_path):
    # Load the data from the CSV file
    data = pd.read_csv(data_path)
    
    # Prepare the features and target variable
    X = data[['age', 'weight', 'severity', 'factor']]
    y = data['priority']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the Random Forest model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the trained model
    joblib.dump(model, MODEL_FILE_PATH)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Model trained. Mean Squared Error: {mse}, R^2 Score: {r2}")
    return model

# Function to load the model
def load_model():
    if os.path.exists(MODEL_FILE_PATH):
        model = joblib.load(MODEL_FILE_PATH)
        print("Model loaded from file.")
    else:
        model = train_model(DATA_FILE_PATH)
    return model

# Function to predict priority for new data
def predict_priority(data_list):
    model = load_model()
    
    # Extract required keys from input data
    required_keys = ['age', 'weight', 'severity', 'factor']
    input_data = pd.DataFrame([{k: d[k] for k in required_keys} for d in data_list])
    
    # Predict priorities
    predicted_priorities = model.predict(input_data)
    
    # Sort the list of dicts by the predicted priority
    sorted_indices = np.argsort(predicted_priorities)
    
    # Assign the priority based on sorted order
    for rank, index in enumerate(sorted_indices, start=1):
        data_list[index]['priority'] = rank
    
    return data_list

# # Example usage
# new_patients = [
#     {'age': 25, 'weight': 70, 'severity': 5.0, 'factor': 8},
#     {'age': 10, 'weight': 40, 'severity': 2.5, 'factor': 9},
#     {'age': 65, 'weight': 80, 'severity': 7.0, 'factor': 8},
# ]

# updated_patients = predict_priority(new_patients)
# print(updated_patients)
