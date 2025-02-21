from flask import Flask, request, jsonify, render_template
from sklearn.ensemble import RandomForestClassifier
from data.dataset import load_and_preprocess_data
import numpy as np
import joblib
import os

app = Flask(__name__)

# Load and preprocess data
data = load_and_preprocess_data()

# Train or load model
MODEL_PATH = 'models/disease_predictor.joblib'
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    # Use Random Forest with optimized parameters
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(data['X_train'], data['y_train'])
    
    # Save the model
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, MODEL_PATH)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/predict')
def predict_page():
    return render_template('index.html')

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify({'symptoms': data['feature_names']})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        request_data = request.json
        user_symptoms = request_data.get('symptoms', [])
        age = request_data.get('age', 30)  # Default age if not provided
        gender = request_data.get('gender', 'M')  # Default gender if not provided
        
        # Create feature vector
        feature_vector = np.zeros(len(data['feature_names']))
        
        # Set symptom features
        for symptom in user_symptoms:
            try:
                symptom_idx = data['feature_names'].index(symptom.lower().replace(' ', '_'))
                feature_vector[symptom_idx] = 1
            except ValueError:
                continue
        
        # Set age and gender features
        age_idx = data['feature_names'].index('age')
        gender_idx = data['feature_names'].index('gender')
        
        feature_vector[age_idx] = data['age_scaler'].transform([[age]])[0]
        feature_vector[gender_idx] = data['gender_encoder'].transform([gender])[0]
        
        # Get prediction and probabilities
        prediction_proba = model.predict_proba([feature_vector])[0]
        predicted_idx = np.argmax(prediction_proba)
        confidence = prediction_proba[predicted_idx]
        
        # Get top 3 predictions
        top_3_idx = np.argsort(prediction_proba)[-3:][::-1]
        predictions = []
        for idx in top_3_idx:
            disease = data['label_encoder'].inverse_transform([idx])[0]
            prob = prediction_proba[idx]
            predictions.append({
                'disease': disease,
                'probability': float(prob),
                'recommendations': get_recommendations(disease)
            })
        
        return jsonify({
            'predictions': predictions,
            'input_summary': {
                'age': age,
                'gender': gender,
                'symptoms': user_symptoms
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_recommendations(disease):
    """Enhanced disease-specific recommendations with severity levels."""
    recommendations_db = {
        'COVID-19': {
            'urgent_actions': [
                'Isolate immediately in a well-ventilated room',
                'Monitor oxygen levels every 4 hours (target >94%)',
                'Track temperature and symptoms using a diary'
            ],
            'treatment': [
                'Take Paracetamol for fever (as directed)',
                'Practice prone positioning 2-3 times daily',
                'Use prescribed medications exactly as directed'
            ],
            'home_care': [
                'Maintain hydration (3L water daily)',
                'Rest in prone position when possible',
                'Use steam inhalation with caution'
            ],
            'warning_signs': [
                'Oxygen levels below 94%',
                'Persistent chest pain',
                'Difficulty breathing or shortness of breath',
                'Blue lips or face'
            ],
            'follow_up': [
                'Schedule telemedicine consultation',
                'Get RT-PCR test if not done',
                'Monitor close contacts for symptoms'
            ]
        },
        'Pneumonia': {
            'urgent_actions': [
                'Seek medical attention immediately',
                'Start prescribed antibiotics without delay',
                'Monitor breathing rate and difficulty'
            ],
            'treatment': [
                'Complete full course of antibiotics',
                'Use prescribed bronchodilators if given',
                'Practice deep breathing exercises'
            ],
            'home_care': [
                'Maintain semi-sitting position',
                'Perform chest physiotherapy as directed',
                'Avoid lying flat for long periods'
            ],
            'warning_signs': [
                'Increased breathing difficulty',
                'High fever persisting > 3 days',
                'Chest pain worsening',
                'Coughing blood'
            ],
            'follow_up': [
                'Chest X-ray after treatment course',
                'Regular temperature monitoring',
                'Weekly doctor check-up'
            ]
        },
        'Tuberculosis': {
            'urgent_actions': [
                'Start DOTS treatment immediately',
                'Isolate until sputum negative',
                'Identify close contacts for screening'
            ],
            'treatment': [
                'Take all medications as prescribed',
                'Complete full 6-month treatment course',
                'Regular liver function monitoring'
            ],
            'home_care': [
                'Maintain good ventilation',
                'Use mask when in company',
                'High-protein diet recommended'
            ],
            'warning_signs': [
                'Coughing blood',
                'Severe weight loss',
                'Persistent fever',
                'Yellow skin or eyes'
            ],
            'follow_up': [
                'Monthly sputum tests',
                'Regular weight monitoring',
                'Chest X-ray as scheduled'
            ]
        }
        # ... Add more diseases with specific recommendations ...
    }

    # Get disease-specific recommendations or default
    recs = recommendations_db.get(disease, {
        'urgent_actions': [
            'Record detailed symptoms',
            'Contact healthcare provider',
            'Avoid self-medication'
        ],
        'treatment': [
            'Rest and recovery',
            'Stay hydrated',
            'Monitor symptoms'
        ],
        'home_care': [
            'Maintain good hygiene',
            'Balanced nutrition',
            'Adequate rest'
        ],
        'warning_signs': [
            'Symptoms worsening',
            'New symptoms appearing',
            'Persistent fever'
        ],
        'follow_up': [
            'Schedule doctor consultation',
            'Keep symptom diary',
            'Follow preventive measures'
        ]
    })

    # Format with severity indicators and timing
    formatted_recs = []
    severity_icons = {
        'urgent_actions': '🔴',
        'warning_signs': '⚠️',
        'treatment': '💊',
        'home_care': '🏠',
        'follow_up': '📋'
    }

    for category, items in recs.items():
        icon = severity_icons.get(category, '•')
        formatted_recs.append(f"\n{icon} {category.replace('_', ' ').upper()}:")
        formatted_recs.extend([f"  ▪ {item}" for item in items])

    return formatted_recs

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)  # Change port if needed

