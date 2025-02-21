import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import os

def load_and_preprocess_data():
    # Get absolute path to the data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, 'medical_dataset.csv')
    
    # Check if dataset exists, if not generate it
    if not os.path.exists(dataset_path):
        from .generate_dataset import generate_medical_dataset
        generate_medical_dataset()
    
    # Load the dataset
    df = pd.read_csv(dataset_path)
    
    # Convert symptoms string to list
    symptoms = df['symptoms'].str.split('|')
    
    # Get unique symptoms
    all_symptoms = set()
    for symptom_list in symptoms:
        all_symptoms.update(symptom_list)
    all_symptoms = sorted(list(all_symptoms))
    
    # Create feature matrix
    X = np.zeros((len(df), len(all_symptoms)))
    for i, symptom_list in enumerate(symptoms):
        for symptom in symptom_list:
            symptom_idx = all_symptoms.index(symptom)
            X[i, symptom_idx] = 1
    
    # Add age as a feature
    age_scaler = StandardScaler()
    ages = age_scaler.fit_transform(df[['age']])
    X = np.column_stack((X, ages))
    
    # Add gender as a feature
    gender_encoder = LabelEncoder()
    genders = gender_encoder.fit_transform(df['gender'])
    X = np.column_stack((X, genders))
    
    # Encode disease labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df['disease'])
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    feature_names = all_symptoms + ['age', 'gender']
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'feature_names': feature_names,
        'label_encoder': label_encoder,
        'age_scaler': age_scaler,
        'gender_encoder': gender_encoder
    }
