document.addEventListener('DOMContentLoaded', async function() {
    const symptomGrid = document.getElementById('symptomGrid');
    const resultSection = document.getElementById('resultSection');
    const predictionForm = document.getElementById('predictionForm');
    const resetBtn = document.getElementById('resetBtn');

    // Enhanced symptom categories
    const symptomCategories = {
        common: [
            'fever', 'fatigue', 'headache', 'body_aches', 'chills', 
            'weakness', 'sweating', 'malaise'
        ],
        respiratory: [
            'cough', 'shortness_of_breath', 'chest_pain', 'wheezing', 
            'sore_throat', 'runny_nose', 'nasal_congestion', 'sneezing',
            'difficulty_breathing', 'rapid_breathing', 'shallow_breathing',
            'chest_tightness', 'coughing_blood'
        ],
        digestive: [
            'nausea', 'vomiting', 'diarrhea', 'abdominal_pain', 
            'loss_of_appetite', 'bloating', 'constipation', 'heartburn',
            'indigestion', 'stomach_cramps', 'excessive_thirst'
        ],
        cardiovascular: [
            'chest_pain', 'palpitations', 'rapid_heartbeat', 'irregular_heartbeat',
            'shortness_of_breath', 'dizziness', 'fainting', 'swollen_ankles',
            'cold_extremities', 'cyanosis'
        ],
        neurological: [
            'headache', 'dizziness', 'confusion', 'memory_loss', 
            'difficulty_speaking', 'tremors', 'seizures', 'numbness',
            'tingling', 'loss_of_balance', 'blurred_vision', 'sensitivity_to_light'
        ],
        musculoskeletal: [
            'joint_pain', 'muscle_pain', 'back_pain', 'neck_pain',
            'stiffness', 'swelling', 'reduced_mobility', 'muscle_weakness',
            'muscle_cramps', 'bone_pain'
        ],
        other: [
            'rash', 'skin_changes', 'itching', 'weight_loss', 'weight_gain',
            'night_sweats', 'anxiety', 'depression', 'insomnia', 'hair_loss',
            'vision_changes', 'hearing_changes', 'taste_changes', 'smell_changes'
        ]
    };

    // Search functionality
    const searchBox = document.getElementById('symptomSearch');
    searchBox.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const symptoms = document.querySelectorAll('.symptom-item');
        
        symptoms.forEach(symptom => {
            const text = symptom.textContent.toLowerCase();
            symptom.style.display = text.includes(searchTerm) ? 'block' : 'none';
        });
    });

    // Category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            document.querySelectorAll('.category-tab').forEach(t => 
                t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');
            // Show symptoms for selected category
            const category = tab.dataset.category;
            filterSymptomsByCategory(category);
        });
    });

    function filterSymptomsByCategory(category) {
        const symptoms = document.querySelectorAll('.symptom-item');
        symptoms.forEach(symptom => {
            const belongsToCategory = symptomCategories[category].includes(
                symptom.dataset.symptom
            );
            symptom.style.display = belongsToCategory ? 'block' : 'none';
        });
    }

    // Fetch symptoms from backend
    try {
        const response = await fetch('/symptoms');
        const data = await response.json();
        const symptoms = data.symptoms.map(s => 
            s.split('_')
             .map(word => word.charAt(0).toUpperCase() + word.slice(1))
             .join(' ')
        );

        // Populate symptoms
        symptoms.forEach(symptom => {
            const div = document.createElement('div');
            div.className = 'symptom-check symptom-item';
            div.dataset.symptom = symptom.toLowerCase().replace(/ /g, '_');
            div.innerHTML = `
                <input type="checkbox" id="${symptom}" name="symptoms" value="${symptom}">
                <label for="${symptom}">${symptom}</label>
            `;
            symptomGrid.appendChild(div);
        });
    } catch (error) {
        console.error('Error fetching symptoms:', error);
    }

    // Handle form reset
    resetBtn.addEventListener('click', () => {
        predictionForm.reset();
        resultSection.style.display = 'none';
    });

    // Handle form submission
    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const selectedSymptoms = [...document.querySelectorAll('input[name="symptoms"]:checked')]
            .map(input => input.value);
            
        const age = document.getElementById('age').value;
        const gender = document.getElementById('gender').value;

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    symptoms: selectedSymptoms,
                    age: parseInt(age),
                    gender: gender
                }),
            });

            const result = await response.json();
            
            resultSection.style.display = 'block';
            resultSection.innerHTML = `
                <h3>Prediction Results</h3>
                ${result.predictions.map((pred, index) => `
                    <div class="prediction-card ${index === 0 ? 'primary' : ''}">
                        <h4>${pred.disease}</h4>
                        <div class="confidence-bar">
                            <div class="confidence-bar-fill" style="width: ${pred.probability * 100}%"></div>
                        </div>
                        <p>Confidence: ${(pred.probability * 100).toFixed(1)}%</p>
                        <div class="recommendations">
                            ${renderRecommendations(pred.recommendations)}
                        </div>
                    </div>
                `).join('')}
                <div class="input-summary">
                    <h4>Patient Information</h4>
                    <p>Age: ${result.input_summary.age}</p>
                    <p>Gender: ${result.input_summary.gender}</p>
                    <p>Reported Symptoms: ${result.input_summary.symptoms.join(', ')}</p>
                </div>
                <div class="disclaimer">
                    <p>This is an AI-based prediction and should not be considered as a final diagnosis. 
                    Please consult with a healthcare professional for proper medical advice.</p>
                </div>
            `;
        } catch (error) {
            console.error('Error:', error);
            resultSection.innerHTML = '<p class="error">An error occurred. Please try again.</p>';
        }
    });

    function renderRecommendations(recommendations) {
        const sections = {
            'URGENT ACTIONS': { icon: '🔴', class: 'urgent' },
            'TREATMENT': { icon: '💊', class: 'treatment' },
            'HOME CARE': { icon: '🏠', class: 'home-care' },
            'WARNING SIGNS': { icon: '⚠️', class: 'warning' },
            'FOLLOW UP': { icon: '📋', class: 'follow-up' }
        };

        let html = '<div class="recommendations-container">';
        let currentSection = '';
        
        recommendations.forEach(rec => {
            if (rec.startsWith('\n')) {
                if (currentSection) {
                    html += '</ul></div>';
                }
                const sectionTitle = rec.replace(/[\n:]/g, '').trim();
                const section = sections[sectionTitle] || { icon: '•', class: 'default' };
                
                html += `
                    <div class="recommendation-section ${section.class}">
                        <div class="recommendation-header">
                            <span class="recommendation-icon">${section.icon}</span>
                            <h4 class="recommendation-title">${sectionTitle}</h4>
                        </div>
                        <ul class="recommendation-list">
                `;
                currentSection = sectionTitle;
            } else if (rec.trim()) {
                const item = rec.replace('▪', '').trim();
                html += `<li class="recommendation-item">${item}</li>`;
            }
        });
        
        if (currentSection) {
            html += '</ul></div>';
        }
        html += '</div>';
        
        return html;
    }

    // Add these functions after the existing code
    document.getElementById('findHospital').addEventListener('click', async (e) => {
        e.preventDefault();
        findNearestHospital();
    });

    async function findNearestHospital() {
        if ("geolocation" in navigator) {
            try {
                const position = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject);
                });
                
                const { latitude, longitude } = position.coords;
                
                // Google Maps search URL for nearby hospitals
                const mapsUrl = `https://www.google.com/maps/search/hospitals/@${latitude},${longitude},14z`;
                
                // Open in new tab
                window.open(mapsUrl, '_blank');
            } catch (error) {
                // If user denies location access or other error
                console.error('Error getting location:', error);
                // Fallback to general hospital search in the user's area
                window.open('https://www.google.com/maps/search/hospitals/', '_blank');
            }
        } else {
            // Fallback for browsers that don't support geolocation
            window.open('https://www.google.com/maps/search/hospitals/', '_blank');
        }
    }
});
