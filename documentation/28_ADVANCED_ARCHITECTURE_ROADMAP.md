# 🏗️ Advanced Architecture Roadmap - Complete Implementation

## 🎯 Big Picture Architecture

```
INPUT LAYER
├── Blood Test Reports (PDF/Image)
├── ECG / X-ray / Angio images
└── Manual patient data

PROCESSING LAYER
├── OCR Engine (EasyOCR/PaddleOCR)
├── Image Processing Models
└── Lab Value Extractor (LLM-based)

AI LAYER
├── Risk Prediction Model (98.07% AUC)
├── Explanation Engine (SHAP)
└── Recommendation Engine

OUTPUT LAYER
├── Risk Score (0-1)
├── Disease Insights (SHAP explanations)
└── Doctor / Hospital Suggestions (Google Maps)
```

---

## 📋 Implementation Phases

### Phase 1: Report Assessment (PDF + Images)
**Duration**: Weeks 1-2

#### Step 1: OCR Extraction
```python
# Option 1: EasyOCR (Recommended for balance)
import easyocr
reader = easyocr.Reader(['en'])
result = reader.readtext('report.jpg')
text = "\n".join([res[1] for res in result])

# Option 2: PaddleOCR (Best accuracy)
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')
result = ocr.ocr('report.jpg', cls=True)
text = "\n".join([line[0][1] for line in result])

# Option 3: Tesseract (Basic)
import pytesseract
text = pytesseract.image_to_string('report.jpg')
```

#### Step 2: Structure the Data
```python
# Raw OCR text is messy
raw_text = """
Hemoglobin: 13.2 g/dL
Cholesterol: 240 mg/dL
Blood Pressure: 140/90 mmHg
"""

# Convert to structured JSON using LLM
from openai import OpenAI
client = OpenAI()

prompt = f"""
Extract all medical values from this report into JSON format:
{raw_text}

Return ONLY valid JSON with keys like:
hemoglobin, cholesterol, blood_pressure, glucose, etc.
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)

import json
structured_data = json.loads(response.choices[0].message.content)
```

---

### Phase 2: Blood Test Integration
**Duration**: Weeks 2-3

#### Key Parameters for Heart Risk
```python
# Focus on these parameters
CRITICAL_PARAMETERS = {
    "cholesterol": "Total cholesterol (mg/dL)",
    "ldl": "LDL cholesterol (mg/dL)",
    "hdl": "HDL cholesterol (mg/dL)",
    "triglycerides": "Triglycerides (mg/dL)",
    "glucose": "Blood glucose (mg/dL)",
    "hemoglobin": "Hemoglobin (g/dL)",
    "creatinine": "Creatinine (mg/dL)",
    "blood_pressure": "Blood pressure (mmHg)",
    "heart_rate": "Heart rate (bpm)"
}

# Mapping Layer
def map_lab_values(lab_data):
    """Convert lab values to model features"""
    return {
        "age": lab_data.get("age", 50),
        "sex": lab_data.get("sex", 1),
        "cp": lab_data.get("chest_pain_type", 0),
        "trestbps": lab_data.get("blood_pressure", 120),
        "chol": lab_data.get("cholesterol", 200),
        "fbs": 1 if lab_data.get("glucose", 100) > 120 else 0,
        "restecg": lab_data.get("resting_ecg", 0),
        "thalach": lab_data.get("heart_rate", 70),
        "exang": lab_data.get("exercise_angina", 0),
        "oldpeak": lab_data.get("st_depression", 0),
        "slope": lab_data.get("st_slope", 0),
        "ca": lab_data.get("major_vessels", 0),
        "thal": lab_data.get("thalassemia", 0)
    }

# Example usage
lab_values = {
    "age": 55,
    "sex": 1,
    "blood_pressure": 140,
    "cholesterol": 250,
    "glucose": 130,
    "heart_rate": 85
}

model_features = map_lab_values(lab_values)
```

---

### Phase 3: Image Processing (ECG/X-ray/Angio)
**Duration**: Weeks 3-4

#### ECG Image Processing
```python
import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load pre-trained ECG model
ecg_model = load_model("models/ecg_classifier.h5")

def process_ecg_image(image_path):
    """Process ECG image and extract features"""
    # Read image
    img = cv2.imread(image_path)
    
    # Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Resize to model input
    resized = cv2.resize(enhanced, (224, 224))
    normalized = resized / 255.0
    
    # Add batch dimension
    input_data = np.expand_dims(normalized, axis=0)
    input_data = np.expand_dims(input_data, axis=-1)  # Add channel
    
    # Predict
    prediction = ecg_model.predict(input_data)
    
    return {
        "ecg_abnormality_score": float(prediction[0][0]),
        "ecg_normal_probability": float(prediction[0][1]),
        "ecg_features": extract_ecg_features(enhanced)
    }

def extract_ecg_features(image):
    """Extract ECG-specific features"""
    # Detect peaks (QRS complex)
    edges = cv2.Canny(image, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    return {
        "num_peaks": len(contours),
        "peak_variance": float(np.var([cv2.contourArea(c) for c in contours])),
        "signal_quality": float(np.mean(image) / 255.0)
    }
```

#### X-ray/Angiography Processing
```python
def process_cardiac_image(image_path, image_type="xray"):
    """Process cardiac imaging (X-ray, Angio, etc.)"""
    img = cv2.imread(image_path)
    
    # Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Histogram equalization
    equalized = cv2.equalizeHist(gray)
    
    # Resize
    resized = cv2.resize(equalized, (256, 256))
    normalized = resized / 255.0
    
    # Load appropriate model
    if image_type == "xray":
        model = load_model("models/xray_classifier.h5")
    elif image_type == "angio":
        model = load_model("models/angio_segmentation.h5")
    else:
        model = load_model("models/cardiac_generic.h5")
    
    # Predict
    input_data = np.expand_dims(normalized, axis=0)
    input_data = np.expand_dims(input_data, axis=-1)
    
    prediction = model.predict(input_data)
    
    return {
        "image_type": image_type,
        "abnormality_score": float(prediction[0][0]),
        "confidence": float(np.max(prediction[0])),
        "findings": interpret_findings(prediction, image_type)
    }

def interpret_findings(prediction, image_type):
    """Interpret model predictions"""
    if image_type == "xray":
        findings = {
            "cardiomegaly": float(prediction[0][0]),
            "pulmonary_edema": float(prediction[0][1]),
            "normal": float(prediction[0][2])
        }
    elif image_type == "angio":
        findings = {
            "blockage_detected": float(prediction[0][0]) > 0.5,
            "blockage_severity": float(prediction[0][0]),
            "vessel_affected": ["LAD", "RCA", "LCx"][np.argmax(prediction[0][1:])]
        }
    else:
        findings = {"abnormality": float(prediction[0][0])}
    
    return findings
```

---

### Phase 4: Combine Everything (Fusion Model)
**Duration**: Week 4

#### Option A: Simple Fusion
```python
def simple_fusion_prediction(tabular_data, ecg_features, xray_features):
    """Simple weighted combination"""
    # Normalize features
    tabular_pred = tabular_model.predict(tabular_data)[0][0]
    ecg_pred = ecg_features["ecg_abnormality_score"]
    xray_pred = xray_features["abnormality_score"]
    
    # Weighted average
    final_score = (
        0.5 * tabular_pred +
        0.3 * ecg_pred +
        0.2 * xray_pred
    )
    
    return final_score
```

#### Option B: Advanced Fusion (Recommended)
```python
from tensorflow.keras import layers, Model
import numpy as np

def create_fusion_model():
    """Create advanced fusion model"""
    
    # Tabular input
    tabular_input = layers.Input(shape=(18,), name="tabular")
    tabular_branch = layers.Dense(64, activation="relu")(tabular_input)
    tabular_branch = layers.Dense(32, activation="relu")(tabular_branch)
    tabular_branch = layers.Dense(16, activation="relu")(tabular_branch)
    
    # ECG input
    ecg_input = layers.Input(shape=(10,), name="ecg")
    ecg_branch = layers.Dense(32, activation="relu")(ecg_input)
    ecg_branch = layers.Dense(16, activation="relu")(ecg_branch)
    
    # X-ray input
    xray_input = layers.Input(shape=(5,), name="xray")
    xray_branch = layers.Dense(32, activation="relu")(xray_input)
    xray_branch = layers.Dense(16, activation="relu")(xray_branch)
    
    # Concatenate
    concatenated = layers.Concatenate()([tabular_branch, ecg_branch, xray_branch])
    
    # Fusion layers
    fusion = layers.Dense(64, activation="relu")(concatenated)
    fusion = layers.Dropout(0.3)(fusion)
    fusion = layers.Dense(32, activation="relu")(fusion)
    fusion = layers.Dropout(0.3)(fusion)
    
    # Output
    output = layers.Dense(1, activation="sigmoid")(fusion)
    
    model = Model(
        inputs=[tabular_input, ecg_input, xray_input],
        outputs=output
    )
    
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["auc"]
    )
    
    return model

# Usage
fusion_model = create_fusion_model()

# Prepare inputs
tabular_features = np.array([...])  # 18 features
ecg_features = np.array([...])      # 10 ECG features
xray_features = np.array([...])     # 5 X-ray features

# Predict
risk_score = fusion_model.predict([tabular_features, ecg_features, xray_features])
```

---

### Phase 5: Explanation Layer (SHAP)
**Duration**: Week 4

```python
import shap
import numpy as np

def explain_prediction(model, input_data, feature_names):
    """Generate SHAP explanations"""
    
    # Create explainer
    explainer = shap.Explainer(model)
    
    # Calculate SHAP values
    shap_values = explainer(input_data)
    
    # Get feature importance
    feature_importance = np.abs(shap_values.values).mean(axis=0)
    
    # Sort by importance
    sorted_idx = np.argsort(feature_importance)[::-1]
    
    explanations = []
    for idx in sorted_idx[:5]:  # Top 5 features
        feature = feature_names[idx]
        importance = feature_importance[idx]
        direction = "increased" if shap_values.values[0][idx] > 0 else "decreased"
        
        explanations.append({
            "feature": feature,
            "importance": float(importance),
            "direction": direction,
            "impact": f"{feature} {direction} risk by {importance*100:.1f}%"
        })
    
    return explanations

# Example
feature_names = [
    "age", "sex", "chest_pain_type", "resting_bp", "cholesterol",
    "fasting_blood_sugar", "resting_ecg", "max_heart_rate",
    "exercise_angina", "st_depression", "st_slope", "major_vessels",
    "thalassemia", "ecg_abnormality", "xray_abnormality", "ldl",
    "hdl", "triglycerides"
]

explanations = explain_prediction(fusion_model, input_data, feature_names)

for exp in explanations:
    print(f"🔴 {exp['impact']}")
```

---

### Phase 6: Doctor Recommendation Engine
**Duration**: Week 5

```python
from geopy.geocoders import Nominatim
import googlemaps

def generate_recommendations(risk_score, explanations, patient_location):
    """Generate doctor recommendations based on risk"""
    
    recommendations = {
        "risk_level": categorize_risk(risk_score),
        "immediate_actions": [],
        "lifestyle_changes": [],
        "medical_consultation": [],
        "nearby_hospitals": []
    }
    
    # Risk categorization
    if risk_score > 0.7:
        recommendations["risk_level"] = "HIGH"
        recommendations["immediate_actions"] = [
            "⚠️ URGENT: Consult a cardiologist immediately",
            "📞 Call emergency services if experiencing chest pain",
            "🏥 Schedule comprehensive cardiac evaluation",
            "💊 Discuss medication options with doctor"
        ]
    elif risk_score > 0.4:
        recommendations["risk_level"] = "MODERATE"
        recommendations["immediate_actions"] = [
            "📅 Schedule cardiologist appointment within 2 weeks",
            "🏥 Get comprehensive cardiac evaluation",
            "💉 Consider stress test or ECG"
        ]
    else:
        recommendations["risk_level"] = "LOW"
        recommendations["immediate_actions"] = [
            "✅ Continue regular health checkups",
            "📋 Monitor risk factors annually"
        ]
    
    # Lifestyle recommendations based on explanations
    for exp in explanations:
        if "cholesterol" in exp["feature"].lower():
            recommendations["lifestyle_changes"].append(
                "🥗 Reduce saturated fat intake, increase fiber"
            )
        if "blood_pressure" in exp["feature"].lower():
            recommendations["lifestyle_changes"].append(
                "🧂 Reduce salt intake, manage stress"
            )
        if "heart_rate" in exp["feature"].lower():
            recommendations["lifestyle_changes"].append(
                "🏃 Increase physical activity (30 min/day)"
            )
    
    # Find nearby hospitals
    if patient_location:
        recommendations["nearby_hospitals"] = find_nearby_hospitals(
            patient_location,
            radius_km=10
        )
    
    return recommendations

def categorize_risk(score):
    """Categorize risk level"""
    if score > 0.7:
        return "HIGH"
    elif score > 0.4:
        return "MODERATE"
    else:
        return "LOW"

def find_nearby_hospitals(location, radius_km=10):
    """Find nearby hospitals using Google Maps API"""
    gmaps = googlemaps.Client(key="YOUR_GOOGLE_MAPS_API_KEY")
    
    # Search for hospitals
    places_result = gmaps.places_nearby(
        location=location,
        radius=radius_km * 1000,
        type="hospital",
        keyword="cardiology"
    )
    
    hospitals = []
    for place in places_result.get("results", [])[:5]:
        hospitals.append({
            "name": place["name"],
            "address": place.get("vicinity", ""),
            "rating": place.get("rating", 0),
            "distance_km": calculate_distance(location, place["geometry"]["location"]),
            "phone": place.get("formatted_phone_number", ""),
            "website": place.get("website", "")
        })
    
    return sorted(hospitals, key=lambda x: x["distance_km"])

def calculate_distance(loc1, loc2):
    """Calculate distance between two locations"""
    from math import radians, cos, sin, asin, sqrt
    
    lon1, lat1 = loc1
    lon2, lat2 = loc2["lat"], loc2["lng"]
    
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    
    return c * r
```

---

## 🔌 Backend API Design (FastAPI)

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os

app = FastAPI(title="Cardiac Health AI Platform")

@app.post("/api/v1/analyze-report")
async def analyze_report(
    file: UploadFile = File(...),
    patient_data: dict = None
):
    """
    Analyze medical report and predict cardiac risk
    
    Input:
    - file: Medical report (PDF/Image)
    - patient_data: Optional patient demographics
    
    Output:
    - risk_score: 0-1 probability
    - risk_level: LOW/MODERATE/HIGH
    - explanations: SHAP-based feature importance
    - recommendations: Doctor suggestions
    """
    try:
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text using OCR
        ocr_text = extract_ocr_text(file_path)
        
        # Parse with LLM
        structured_data = parse_with_llm(ocr_text)
        
        # Map to model features
        model_features = map_lab_values(structured_data)
        
        # Process images if present
        ecg_features = process_ecg_image(file_path) if is_ecg(file_path) else None
        xray_features = process_cardiac_image(file_path) if is_xray(file_path) else None
        
        # Predict
        if ecg_features and xray_features:
            risk_score = fusion_model.predict([
                np.array([model_features]),
                np.array([ecg_features]),
                np.array([xray_features])
            ])[0][0]
        else:
            risk_score = tabular_model.predict(np.array([model_features]))[0][0]
        
        # Explain
        explanations = explain_prediction(
            fusion_model if (ecg_features and xray_features) else tabular_model,
            np.array([model_features]),
            feature_names
        )
        
        # Recommend
        recommendations = generate_recommendations(
            risk_score,
            explanations,
            patient_data.get("location") if patient_data else None
        )
        
        # Clean up
        os.remove(file_path)
        
        return {
            "status": "success",
            "risk_score": float(risk_score),
            "risk_level": recommendations["risk_level"],
            "explanations": explanations,
            "recommendations": recommendations,
            "structured_data": structured_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/predict")
async def predict(data: dict):
    """Direct prediction from structured data"""
    try:
        model_features = map_lab_values(data)
        risk_score = tabular_model.predict(np.array([model_features]))[0][0]
        
        explanations = explain_prediction(
            tabular_model,
            np.array([model_features]),
            feature_names
        )
        
        recommendations = generate_recommendations(
            risk_score,
            explanations,
            data.get("location")
        )
        
        return {
            "status": "success",
            "risk_score": float(risk_score),
            "risk_level": recommendations["risk_level"],
            "explanations": explanations,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0"}
```

---

## 📊 Updated Requirements

```
# requirements.txt

# Core ML
scikit-learn>=1.0.0
xgboost>=1.5.0
tensorflow>=2.10.0
torch>=1.10.0

# OCR
easyocr>=1.6.0
paddleocr>=2.7.0
pytesseract>=0.3.10

# Image Processing
opencv-python>=4.5.0
Pillow>=9.0.0

# Explanations
shap>=0.41.0

# LLM Integration
openai>=1.0.0
anthropic>=0.7.0

# Backend
fastapi>=0.95.0
uvicorn>=0.21.0
python-multipart>=0.0.6

# Maps
googlemaps>=4.10.0
geopy>=2.3.0

# Data
pandas>=1.5.0
numpy>=1.23.0

# Utilities
python-dotenv>=0.21.0
pydantic>=1.10.0
```

---

## 🚀 5-Week Implementation Roadmap

### Week 1: OCR + Text Extraction
- [ ] Set up EasyOCR/PaddleOCR
- [ ] Create OCR pipeline
- [ ] Test on sample reports
- [ ] Handle different formats

### Week 2: LLM-based Parsing
- [ ] Integrate OpenAI API
- [ ] Create parsing prompts
- [ ] Validate extracted data
- [ ] Handle edge cases

### Week 3: Lab Value Mapping
- [ ] Create mapping layer
- [ ] Test with real lab values
- [ ] Validate feature engineering
- [ ] Integrate with model

### Week 4: Image Processing + Fusion
- [ ] Implement ECG processing
- [ ] Implement X-ray processing
- [ ] Create fusion model
- [ ] Test combined predictions

### Week 5: API + Recommendations
- [ ] Build FastAPI endpoints
- [ ] Integrate SHAP explanations
- [ ] Add doctor recommendations
- [ ] Deploy and test

---

## 💡 Smart Shortcuts (Use APIs)

```python
# Instead of building from scratch:

# 1. OCR → Google Vision API
from google.cloud import vision

def ocr_with_google(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    return response.full_text_annotation.text

# 2. LLM → OpenAI/Anthropic
from openai import OpenAI

def parse_with_llm(text):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Extract medical values: {text}"
        }]
    )
    return json.loads(response.choices[0].message.content)

# 3. ECG Models → Kaggle Pre-trained
# Download from: https://www.kaggle.com/datasets/...
```

---

## 🎯 Your Competitive Advantage

**"Upload ANY medical report → AI explains + predicts + suggests doctor"**

### Why This Works in India:
✅ Huge market (1.4B people)
✅ Limited access to cardiologists
✅ Rising heart disease rates
✅ Mobile-first population
✅ Government health initiatives

### Revenue Model:
- B2C: ₹99-499 per report analysis
- B2B: Hospitals/clinics integration
- B2G: Government health programs
- API: For other health apps

---

## 📁 Updated Project Structure

```
cardiac-health-ai/
├── backend/
│   ├── services/
│   │   ├── ocr_service.py          (NEW)
│   │   ├── image_processor.py      (NEW)
│   │   ├── fusion_model.py         (NEW)
│   │   ├── explanation_service.py  (UPDATED)
│   │   └── recommendation_service.py (UPDATED)
│   ├── models/
│   │   ├── ecg_classifier.h5       (NEW)
│   │   ├── xray_classifier.h5      (NEW)
│   │   └── fusion_model.h5         (NEW)
│   └── main.py                     (UPDATED)
│
├── ml_model/
│   ├── models/
│   │   ├── heart_disease_model_ultra.joblib
│   │   └── fusion_model.joblib     (NEW)
│   ├── image_processing/           (NEW)
│   │   ├── ecg_trainer.py
│   │   ├── xray_trainer.py
│   │   └── fusion_trainer.py
│   └── train_fusion_model.py       (NEW)
│
└── docs/
    ├── ADVANCED_ARCHITECTURE.md    (NEW)
    ├── OCR_GUIDE.md                (NEW)
    ├── IMAGE_PROCESSING_GUIDE.md   (NEW)
    └── FUSION_MODEL_GUIDE.md       (NEW)
```

---

## 🎓 Next Steps

**Choose one:**

1. **FastAPI Backend Code** - Complete implementation
2. **Android App Structure** - Full app architecture
3. **Dataset Sources** - ECG + reports + images
4. **Pre-trained Models** - Ready-to-use models

Just tell me which one! 👍

---

**Status**: Ready for Implementation
**Complexity**: Advanced
**Timeline**: 5 weeks
**Impact**: Game-changing for Indian healthcare 🔥
