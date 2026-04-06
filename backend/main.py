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
from services.image_processor import CardiacImageProcessor
from services.fusion_model import FusionModelService
from services.explanation_service_advanced import SHAPExplanationService
from services.llm_parser import LLMReportParser
from services.lab_mapper import LabValueMapper

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
image_processor = CardiacImageProcessor()
fusion_service = FusionModelService()
shap_service = SHAPExplanationService()
llm_parser = LLMReportParser()
lab_mapper = LabValueMapper()
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


# ============================================================================
# ADVANCED ENDPOINTS - Image Processing, Fusion, and Explanations
# ============================================================================

@app.post("/api/v2/analyze-complete-report")
async def analyze_complete_report(
    blood_report: UploadFile = File(...),
    ecg_image: Optional[UploadFile] = File(None),
    xray_image: Optional[UploadFile] = File(None),
    angio_image: Optional[UploadFile] = File(None),
    age: int = 50,
    sex: int = 1
):
    """
    Comprehensive analysis combining blood report + cardiac images
    
    Args:
        blood_report: Blood test report (PDF/Image)
        ecg_image: ECG image (optional)
        xray_image: X-ray image (optional)
        angio_image: Angiography image (optional)
        age: Patient age
        sex: Patient sex (1=male, 0=female)
        
    Returns:
        Comprehensive analysis with fusion prediction
    """
    try:
        # Process blood report
        blood_path = UPLOAD_DIR / blood_report.filename
        with open(blood_path, "wb") as f:
            f.write(await blood_report.read())
        
        extracted_data = ocr_service.process_medical_report(
            str(blood_path), "blood"
        )
        
        # Map to model features
        tabular_features = {
            "age": age,
            "sex": sex,
            "chest_pain_type": 0,
            "resting_bp": int(extracted_data.get("blood_pressure", "120/80").split("/")[0]),
            "cholesterol": int(extracted_data.get("cholesterol", 200)),
            "fasting_blood_sugar": 1 if extracted_data.get("glucose", 0) > 120 else 0,
            "resting_ecg": 0,
            "max_heart_rate": 150,
            "exercise_induced_angina": 0,
            "st_depression": 0,
            "st_slope": 1,
            "num_major_vessels": 0,
            "thalassemia": 0
        }
        
        # Process images if provided
        ecg_features = None
        xray_features = None
        angio_features = None
        
        if ecg_image:
            ecg_path = UPLOAD_DIR / ecg_image.filename
            with open(ecg_path, "wb") as f:
                f.write(await ecg_image.read())
            ecg_result = image_processor.process_image(str(ecg_path), "ecg")
            ecg_features = ecg_result.features
            os.remove(ecg_path)
        
        if xray_image:
            xray_path = UPLOAD_DIR / xray_image.filename
            with open(xray_path, "wb") as f:
                f.write(await xray_image.read())
            xray_result = image_processor.process_image(str(xray_path), "xray")
            xray_features = xray_result.features
            os.remove(xray_path)
        
        if angio_image:
            angio_path = UPLOAD_DIR / angio_image.filename
            with open(angio_path, "wb") as f:
                f.write(await angio_image.read())
            angio_result = image_processor.process_image(str(angio_path), "angiography")
            angio_features = angio_result.features
            os.remove(angio_path)
        
        # Get tabular prediction
        import numpy as np
        tabular_array = np.array([[
            tabular_features["age"],
            tabular_features["sex"],
            tabular_features["chest_pain_type"],
            tabular_features["resting_bp"],
            tabular_features["cholesterol"],
            tabular_features["fasting_blood_sugar"],
            tabular_features["resting_ecg"],
            tabular_features["max_heart_rate"],
            tabular_features["exercise_induced_angina"],
            tabular_features["st_depression"],
            tabular_features["st_slope"],
            tabular_features["num_major_vessels"],
            tabular_features["thalassemia"]
        ]])
        
        # Fusion prediction
        predictions = fusion_service.predict(
            tabular_array,
            ecg_features=ecg_features,
            xray_features=xray_features,
            angio_features=angio_features,
            tabular_model=predictor.model
        )
        
        # Generate explanations
        explanations = shap_service.explain_prediction(
            tabular_array[0],
            predictions["fusion"]
        )
        
        # Categorize risk
        fusion_score = predictions["fusion"]
        if fusion_score > 0.7:
            risk_level = "HIGH"
        elif fusion_score > 0.4:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        # Generate recommendations
        recommendations = shap_service.generate_recommendations(
            explanations, risk_level
        )
        
        # Generate report
        report = fusion_service.generate_fusion_report(
            predictions,
            tabular_features,
            ecg_features=ecg_features,
            xray_features=xray_features,
            angio_features=angio_features
        )
        
        # Clean up
        os.remove(blood_path)
        
        return {
            "success": True,
            "extracted_data": extracted_data,
            "fusion_score": float(fusion_score),
            "risk_level": risk_level,
            "predictions": predictions,
            "explanations": explanations,
            "recommendations": recommendations,
            "report": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/process-cardiac-image")
async def process_cardiac_image(
    file: UploadFile = File(...),
    image_type: str = "ecg"
):
    """
    Process cardiac image (ECG, X-ray, Angiography)
    
    Args:
        file: Cardiac image file
        image_type: Type of image (ecg, xray, angiography)
        
    Returns:
        Image analysis results
    """
    try:
        # Save image
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Process image
        result = image_processor.process_image(str(file_path), image_type)
        
        # Clean up
        os.remove(file_path)
        
        return {
            "success": True,
            "image_type": result.image_type,
            "abnormality_score": float(result.abnormality_score),
            "confidence": float(result.confidence),
            "findings": result.findings,
            "features": result.features,
            "quality_score": float(result.quality_score)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/explain-prediction")
async def explain_prediction(input_data: PredictionInput):
    """
    Get detailed SHAP explanation for prediction
    
    Args:
        input_data: Patient data
        
    Returns:
        SHAP-based explanation
    """
    try:
        import numpy as np
        
        # Convert to array
        data_array = np.array([[
            input_data.age,
            input_data.sex,
            input_data.chest_pain_type,
            input_data.resting_bp,
            input_data.cholesterol,
            input_data.fasting_blood_sugar,
            input_data.resting_ecg,
            input_data.max_heart_rate,
            input_data.exercise_induced_angina,
            input_data.st_depression,
            input_data.st_slope,
            input_data.num_major_vessels,
            input_data.thalassemia
        ]])
        
        # Make prediction
        prediction = predictor.predict(input_data.dict())
        
        # Generate explanation
        explanation = shap_service.explain_prediction(
            data_array[0],
            prediction["probability"]
        )
        
        # Generate recommendations
        recommendations = shap_service.generate_recommendations(
            explanation,
            prediction["risk_level"]
        )
        
        # Generate clinical summary
        clinical_summary = shap_service.generate_clinical_summary(
            explanation,
            prediction["risk_level"]
        )
        
        return {
            "success": True,
            "prediction": prediction,
            "explanation": explanation,
            "recommendations": recommendations,
            "clinical_summary": clinical_summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/explain-report")
async def explain_report(file: UploadFile = File(...)):
    """
    Explain findings from medical report
    
    Args:
        file: Medical report file
        
    Returns:
        Explanation of findings
    """
    try:
        # Save and process report
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Extract data
        extracted_data = ocr_service.process_medical_report(
            str(file_path), "blood"
        )
        
        # Generate explanations
        findings = shap_service.explain_report_findings(
            extracted_data, extracted_data
        )
        
        # Clean up
        os.remove(file_path)
        
        return {
            "success": True,
            "extracted_data": extracted_data,
            "findings": findings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NEW ENDPOINTS - LLM PARSING & LAB MAPPING
# ============================================================================

@app.post("/api/v2/parse-report-with-llm")
async def parse_report_with_llm(file: UploadFile = File(...)):
    """
    Parse medical report using LLM
    
    Args:
        file: Medical report file (PDF/Image)
        
    Returns:
        Structured medical data extracted by LLM
    """
    try:
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Extract text using OCR
        ocr_text = ocr_service.process_medical_report(str(file_path), "blood")
        
        # Parse with LLM
        structured_data = llm_parser.parse_blood_report(str(ocr_text))
        
        # Validate
        validation = lab_mapper.validate_lab_values(structured_data)
        
        # Get risk factors
        risk_factors = lab_mapper.get_risk_factors(structured_data)
        
        # Get feature importance hints
        importance_hints = lab_mapper.get_feature_importance_hints(structured_data)
        
        # Generate summary
        lab_summary = lab_mapper.generate_lab_summary(structured_data)
        
        # Clean up
        os.remove(file_path)
        
        return {
            "success": True,
            "structured_data": structured_data,
            "validation": validation,
            "risk_factors": risk_factors,
            "importance_hints": importance_hints,
            "lab_summary": lab_summary,
            "confidence": 0.9 if validation["valid"] else 0.6
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/map-lab-values")
async def map_lab_values(
    lab_data: Dict = None,
    age: int = 50,
    sex: int = 1
):
    """
    Map lab values to model features
    
    Args:
        lab_data: Lab values dictionary
        age: Patient age
        sex: Patient sex (1=male, 0=female)
        
    Returns:
        Model features and analysis
    """
    try:
        if not lab_data:
            raise HTTPException(status_code=400, detail="lab_data required")
        
        # Prepare patient data
        patient_data = {"age": age, "sex": sex}
        
        # Map values
        import numpy as np
        features_array, features_dict = lab_mapper.map_lab_values(lab_data, patient_data)
        
        # Validate
        validation = lab_mapper.validate_lab_values(lab_data)
        
        # Get risk factors
        risk_factors = lab_mapper.get_risk_factors(lab_data)
        
        # Get importance hints
        importance_hints = lab_mapper.get_feature_importance_hints(lab_data)
        
        return {
            "success": True,
            "features": features_dict,
            "features_array": features_array.tolist(),
            "validation": validation,
            "risk_factors": risk_factors,
            "importance_hints": importance_hints,
            "feature_names": lab_mapper.FEATURE_NAMES
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/parse-ecg-report")
async def parse_ecg_report(file: UploadFile = File(...)):
    """
    Parse ECG report using LLM
    
    Args:
        file: ECG report file
        
    Returns:
        Structured ECG findings
    """
    try:
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Extract text using OCR
        ocr_text = ocr_service.process_medical_report(str(file_path), "ecg")
        
        # Parse with LLM
        ecg_findings = llm_parser.parse_ecg_report(str(ocr_text))
        
        # Clean up
        os.remove(file_path)
        
        return {
            "success": True,
            "ecg_findings": ecg_findings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/parse-imaging-report")
async def parse_imaging_report(
    file: UploadFile = File(...),
    imaging_type: str = "xray"
):
    """
    Parse imaging report using LLM
    
    Args:
        file: Imaging report file
        imaging_type: Type of imaging (xray, ct, mri, ultrasound)
        
    Returns:
        Structured imaging findings
    """
    try:
        # Save file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Extract text using OCR
        ocr_text = ocr_service.process_medical_report(str(file_path), imaging_type)
        
        # Parse with LLM
        imaging_findings = llm_parser.parse_imaging_report(str(ocr_text), imaging_type)
        
        # Clean up
        os.remove(file_path)
        
        return {
            "success": True,
            "imaging_type": imaging_type,
            "imaging_findings": imaging_findings
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v2/complete-analysis-pipeline")
async def complete_analysis_pipeline(
    blood_report: UploadFile = File(...),
    age: int = 50,
    sex: int = 1,
    ecg_image: UploadFile = File(None),
    xray_image: UploadFile = File(None),
    angio_image: UploadFile = File(None)
):
    """
    Complete analysis pipeline - all 8 components
    
    INPUT LAYER → PROCESSING LAYER → AI LAYER → OUTPUT LAYER
    
    Args:
        blood_report: Blood test report
        age: Patient age
        sex: Patient sex
        ecg_image: ECG image (optional)
        xray_image: X-ray image (optional)
        angio_image: Angiography image (optional)
        
    Returns:
        Complete analysis with all components
    """
    try:
        import numpy as np
        
        # ============================================================
        # STEP 1: OCR EXTRACTION (INPUT LAYER)
        # ============================================================
        blood_path = UPLOAD_DIR / blood_report.filename
        with open(blood_path, "wb") as f:
            f.write(await blood_report.read())
        
        ocr_text = ocr_service.process_medical_report(str(blood_path), "blood")
        
        # ============================================================
        # STEP 2: LLM PARSING (PROCESSING LAYER)
        # ============================================================
        structured_data = llm_parser.parse_blood_report(str(ocr_text))
        validation = lab_mapper.validate_lab_values(structured_data)
        
        # ============================================================
        # STEP 3: LAB VALUE MAPPING (PROCESSING LAYER)
        # ============================================================
        patient_data = {"age": age, "sex": sex}
        tabular_array, features_dict = lab_mapper.map_lab_values(
            structured_data, patient_data
        )
        
        # ============================================================
        # STEP 4: IMAGE PROCESSING (PROCESSING LAYER)
        # ============================================================
        ecg_features = None
        xray_features = None
        angio_features = None
        
        if ecg_image:
            ecg_path = UPLOAD_DIR / ecg_image.filename
            with open(ecg_path, "wb") as f:
                f.write(await ecg_image.read())
            ecg_result = image_processor.process_image(str(ecg_path), "ecg")
            ecg_features = ecg_result.features
            os.remove(ecg_path)
        
        if xray_image:
            xray_path = UPLOAD_DIR / xray_image.filename
            with open(xray_path, "wb") as f:
                f.write(await xray_image.read())
            xray_result = image_processor.process_image(str(xray_path), "xray")
            xray_features = xray_result.features
            os.remove(xray_path)
        
        if angio_image:
            angio_path = UPLOAD_DIR / angio_image.filename
            with open(angio_path, "wb") as f:
                f.write(await angio_image.read())
            angio_result = image_processor.process_image(str(angio_path), "angiography")
            angio_features = angio_result.features
            os.remove(angio_path)
        
        # ============================================================
        # STEP 5: FUSION MODEL (AI LAYER)
        # ============================================================
        predictions = fusion_service.predict(
            tabular_array,
            ecg_features=ecg_features,
            xray_features=xray_features,
            angio_features=angio_features,
            tabular_model=predictor.model
        )
        
        fusion_score = predictions["fusion"]
        
        # ============================================================
        # STEP 6: SHAP EXPLANATIONS (AI LAYER)
        # ============================================================
        explanations = shap_service.explain_prediction(
            tabular_array[0],
            fusion_score
        )
        
        # Categorize risk
        if fusion_score > 0.7:
            risk_level = "HIGH"
        elif fusion_score > 0.4:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        # ============================================================
        # STEP 7: RECOMMENDATIONS (AI LAYER)
        # ============================================================
        recommendations = shap_service.generate_recommendations(
            explanations, risk_level
        )
        
        clinical_summary = shap_service.generate_clinical_summary(
            explanations, risk_level
        )
        
        # ============================================================
        # STEP 8: DOCTOR SUGGESTIONS (OUTPUT LAYER)
        # ============================================================
        doctor_suggestions = {
            "risk_level": risk_level,
            "immediate_actions": [],
            "specialist_needed": "Cardiologist" if fusion_score > 0.5 else "General Practitioner"
        }
        
        if fusion_score > 0.7:
            doctor_suggestions["immediate_actions"] = [
                "🚨 URGENT: Consult cardiologist immediately",
                "📞 Call emergency if experiencing chest pain",
                "🏥 Schedule comprehensive cardiac evaluation"
            ]
        elif fusion_score > 0.4:
            doctor_suggestions["immediate_actions"] = [
                "📅 Schedule cardiologist appointment within 2 weeks",
                "🏥 Get comprehensive cardiac evaluation",
                "💉 Consider stress test or advanced imaging"
            ]
        else:
            doctor_suggestions["immediate_actions"] = [
                "✅ Continue regular health checkups",
                "📋 Monitor risk factors annually"
            ]
        
        # ============================================================
        # GENERATE FINAL REPORT (OUTPUT LAYER)
        # ============================================================
        report = fusion_service.generate_fusion_report(
            predictions,
            features_dict,
            ecg_features=ecg_features,
            xray_features=xray_features,
            angio_features=angio_features
        )
        
        # Clean up
        os.remove(blood_path)
        
        return {
            "success": True,
            "pipeline_status": "COMPLETE",
            
            # INPUT LAYER
            "input_layer": {
                "blood_report": "Processed",
                "ecg_image": "Processed" if ecg_image else "Not provided",
                "xray_image": "Processed" if xray_image else "Not provided",
                "angio_image": "Processed" if angio_image else "Not provided"
            },
            
            # PROCESSING LAYER
            "processing_layer": {
                "ocr_text": ocr_text[:200] + "..." if len(str(ocr_text)) > 200 else ocr_text,
                "structured_data": structured_data,
                "validation": validation,
                "lab_features": features_dict,
                "image_features": {
                    "ecg": ecg_features is not None,
                    "xray": xray_features is not None,
                    "angio": angio_features is not None
                }
            },
            
            # AI LAYER
            "ai_layer": {
                "fusion_score": float(fusion_score),
                "predictions": predictions,
                "explanations": explanations,
                "recommendations": recommendations,
                "clinical_summary": clinical_summary
            },
            
            # OUTPUT LAYER
            "output_layer": {
                "risk_score": float(fusion_score),
                "risk_level": risk_level,
                "disease_insights": explanations,
                "doctor_suggestions": doctor_suggestions,
                "full_report": report
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
