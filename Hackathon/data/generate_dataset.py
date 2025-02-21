import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_medical_dataset(num_records=10000):
    # Define common symptoms and diseases with their associated probabilities
    disease_symptoms = {
        'COVID-19': {
            'symptoms': ['fever', 'cough', 'fatigue', 'loss_of_taste', 'loss_of_smell', 'difficulty_breathing'],
            'probability': 0.15
        },
        'Influenza': {
            'symptoms': ['fever', 'cough', 'body_aches', 'fatigue', 'headache', 'sore_throat'],
            'probability': 0.2
        },
        'Pneumonia': {
            'symptoms': ['high_fever', 'severe_cough', 'difficulty_breathing', 'chest_pain', 'fatigue'],
            'probability': 0.1
        },
        'Tuberculosis': {
            'symptoms': ['persistent_cough', 'weight_loss', 'night_sweats', 'fatigue', 'fever'],
            'probability': 0.05
        },
        'Bronchitis': {
            'symptoms': ['cough', 'mucus_production', 'wheezing', 'chest_discomfort', 'fatigue'],
            'probability': 0.15
        },
        'Asthma': {
            'symptoms': ['wheezing', 'shortness_of_breath', 'chest_tightness', 'cough'],
            'probability': 0.1
        },
        'Common Cold': {
            'symptoms': ['runny_nose', 'sore_throat', 'cough', 'congestion', 'mild_fever'],
            'probability': 0.15
        },
        'Malaria': {
            'symptoms': ['high_fever', 'chills', 'headache', 'fatigue', 'muscle_pain'],
            'probability': 0.05
        },
        'Dengue': {
            'symptoms': ['high_fever', 'severe_headache', 'joint_pain', 'rash', 'fatigue'],
            'probability': 0.03
        },
        'Typhoid': {
            'symptoms': ['high_fever', 'headache', 'abdominal_pain', 'fatigue', 'loss_of_appetite'],
            'probability': 0.02
        }
    }

    data = []
    
    for _ in range(num_records):
        # Select disease based on probability
        disease = np.random.choice(
            list(disease_symptoms.keys()),
            p=[d['probability'] for d in disease_symptoms.values()]
        )
        
        # Get base symptoms for the disease
        base_symptoms = disease_symptoms[disease]['symptoms']
        
        # Add some randomness to symptoms
        num_symptoms = np.random.randint(max(2, len(base_symptoms)-2), len(base_symptoms)+1)
        selected_symptoms = list(np.random.choice(base_symptoms, num_symptoms, replace=False))
        
        # Add some random noise (false symptoms) with low probability
        all_symptoms = set([sym for d in disease_symptoms.values() for sym in d['symptoms']])
        other_symptoms = list(all_symptoms - set(selected_symptoms))
        if np.random.random() < 0.1:  # 10% chance of additional symptoms
            num_extra = np.random.randint(1, 3)
            selected_symptoms.extend(np.random.choice(other_symptoms, num_extra, replace=False))
        
        # Add severity levels
        severity = np.random.choice(['mild', 'moderate', 'severe'], p=[0.5, 0.3, 0.2])
        
        # Generate random age and gender
        age = np.random.randint(1, 100)
        gender = np.random.choice(['M', 'F'])
        
        data.append({
            'patient_id': f'P{len(data):05d}',
            'age': age,
            'gender': gender,
            'symptoms': '|'.join(selected_symptoms),
            'severity': severity,
            'disease': disease,
            'date_recorded': (datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
        })
    
    df = pd.DataFrame(data)
    
    # Create data directory if it doesn't exist
    output_path = os.path.join(os.path.dirname(__file__), 'medical_dataset.csv')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the dataset
    df.to_csv(output_path, index=False)
    print(f"Generated {num_records} medical records and saved to {output_path}")
    return df

if __name__ == "__main__":
    generate_medical_dataset()
