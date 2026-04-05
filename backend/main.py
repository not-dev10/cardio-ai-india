"""
FastAPI Main Application
Cardiac Health Assistant Platform
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from services.ocr_service import MedicalReportOCR
from services.explanation_service import MedicalExplanationService
from services.recommendation_service import HealthcareRecommendationService

# Import ML model
from ml_model.predict import HeartDiseasePredictor

# Initialize FastAPI app
app = FastAPI(
    title="Cardiac Health Assistant API",
    description="AI-powered cardiac health platform for India",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_service = MedicalReportOCR()
explanation_service = MedicalExplanationService()
recommendation_service = HealthcareRecommendationService()
predictor = HeartDiseasePredictor(model_type="xgboost")

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# Pydantic models
class PredictionInput(BaseModel):
    """Manual input for prediction"""
    age: int
    sex: int  # 1=male, 0=female
    chest_pain_type: int  # 0-3
    resting_bp: int
    cholesterol: int
    fasting_blood_sugar: int  # 1=true, 0=false
    resting_ecg: int  # 0-2
    max_heart_rate: int
    exercise_induced_angina: int  # 1=yes, 0=no
    st_depression: float
    st_slope: int  # 0-2
    num_major_vessels: int  # 0-3
    thalassemia: int  # 0-3
    
    # Optional Indian context (for future)
    smoking: Optional[int] = 0
    diabetes: Optional[int] = 0
    stress_level: Optional[int] = 5


class LocationInput(BaseModel):
    """User location for recommendations"""
    latitude: float
    longitude: float


class PredictionResponse(BaseModel):
    """Prediction response"""
    prediction: int
    probability: float
    risk_level: str
    confidence: float
    recommendations: List[str]
    explanation: str


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cardiac Health Assistant API",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "ocr": "active",
            "ml_model": "active" if predictor.model else "inactive",
            "explanation": "active",
            "recommendation": "active"
        }
    }


@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_risk(input_data: PredictionInput):
    """
    Predict heart disease risk from manual input
    
    Args:
        input_data: Patient data
        
    Returns:
        Prediction results with explanation
    """
    try:
        # Convert to dict
        data_dict = input_data.dict()
        
        # Make prediction
        result = predictor.predict(data_dict)
        
        # Generate explanation
        explanation = explanation_service.explain_risk_prediction(
            result, data_dict
        )
        
        result["explanation"] = explanation
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/upload-report")
async def upload_medical_report(
    file: UploadFile = File(...),
    report_type: str = "blood"
):
    """
    Upload and process medical report (image or PDF)
    
    Args:
        file: Medical report file
        report_type: Type of report (blood, ecg, angiography)
        
    Returns:
        Extracted data from report
    """
    try:
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {allowed_extensions}"
            )
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process report
        extracted_data = ocr_service.process_medical_report(
            str(file_path), report_type
        )
        
        # Validate extracted data
        validation = ocr_service.validate_extracted_data(extracted_data)
        
        # Generate explanations for blood report
        explanations = {}
        if report_type == "blood":
            explanations = explanation_service.explain_blood_report(extracted_data)
        
        # Clean up
        os.remove(file_path)
        
        return {
            "success": True,
            "report_type": report_type,
            "extracted_data": extracted_data,
            "validation": validation,
            "explanations": explanations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict-from-report")
async def predict_from_report(
    file: UploadFile = File(...),
    age: int = 50,
    sex: int = 1,
    smoking: int = 0,
    diabetes: int = 0
):
    """
    Upload report and get risk prediction
    
    Args:
        file: Blood report file
        age: Patient age
        sex: Patient sex (1=male, 0=female)
        smoking: Smoking status
        diabetes: Diabetes status
        
    Returns:
        Risk prediction based on report data
    """
    try:
        # Save and process report
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract data
        extracted_data = ocr_service.process_medical_report(
            str(file_path), "blood"
        )
        
        # Map extracted data to prediction input
        prediction_input = {
            "age": age,
            "sex": sex,
            "chest_pain_type": 0,  # Default
            "resting_bp": 120,  # Default, should be extracted
            "cholesterol": int(extracted_data.get("cholesterol_total", 200)),
            "fasting_blood_sugar": 1 if extracted_data.get("blood_sugar_fasting", 0) > 120 else 0,
            "resting_ecg": 0,
            "max_heart_rate": 150,  # Default
            "exercise_induced_angina": 0,
            "st_depression": 0,
            "st_slope": 1,
            "num_major_vessels": 0,
            "thalassemia": 0,
            "smoking": smoking,
            "diabetes": diabetes
        }
        
        # Make prediction
        result = predictor.predict(prediction_input)
        
        # Generate explanation
        explanation = explanation_service.explain_risk_prediction(
            result, prediction_input
        )
        
        # Clean up
        os.remove(file_path)
        
        return {
            "success": True,
            "extracted_data": extracted_data,
            "prediction": result,
            "explanation": explanation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/find-doctors")
async def find_nearby_doctors(location: LocationInput, risk_level: str = "Medium"):
    """
    Find nearby cardiologists and hospitals
    
    Args:
        location: User's location
        risk_level: Risk level (Low, Medium, High)
        
    Returns:
        Nearby healthcare providers
    """
    try:
        recommendations = recommendation_service.get_recommendations_by_risk(
            risk_level,
            location.latitude,
            location.longitude
        )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/cardiologists")
async def get_cardiologists(lat: float, lng: float, radius: int = 5000):
    """
    Get nearby cardiologists
    
    Args:
        lat: Latitude
        lng: Longitude
        radius: Search radius in meters
        
    Returns:
        List of cardiologists
    """
    try:
        cardiologists = recommendation_service.find_nearby_cardiologists(
            lat, lng, radius
        )
        return {"cardiologists": cardiologists}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/hospitals")
async def get_hospitals(lat: float, lng: float, radius: int = 10000):
    """
    Get nearby hospitals
    
    Args:
        lat: Latitude
        lng: Longitude
        radius: Search radius in meters
        
    Returns:
        List of hospitals
    """
    try:
        hospitals = recommendation_service.find_nearby_hospitals(
            lat, lng, radius
        )
        return {"hospitals": hospitals}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
