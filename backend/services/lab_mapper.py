"""
Lab Value Mapper
Converts medical lab values to model features
"""

import logging
from typing import Dict, List, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class LabValueMapper:
    """Map lab values to model features"""
    
    # Feature names for the model
    FEATURE_NAMES = [
        "age", "sex", "chest_pain_type", "resting_bp", "cholesterol",
        "fasting_blood_sugar", "resting_ecg", "max_heart_rate",
        "exercise_induced_angina", "st_depression", "st_slope",
        "num_major_vessels", "thalassemia"
    ]
    
    # Normal ranges for lab values
    NORMAL_RANGES = {
        "hemoglobin": (12.0, 17.5),  # g/dL
        "cholesterol": (0, 200),  # mg/dL
        "ldl": (0, 100),  # mg/dL
        "hdl": (40, 300),  # mg/dL
        "triglycerides": (0, 150),  # mg/dL
        "glucose": (70, 100),  # mg/dL (fasting)
        "blood_pressure_systolic": (90, 120),  # mmHg
        "blood_pressure_diastolic": (60, 80),  # mmHg
        "creatinine": (0.7, 1.3),  # mg/dL
        "heart_rate": (60, 100),  # bpm
    }
    
    def __init__(self):
        """Initialize mapper"""
        self.feature_names = self.FEATURE_NAMES
    
    def map_lab_values(
        self,
        lab_data: Dict,
        patient_data: Dict = None
    ) -> Tuple[np.ndarray, Dict]:
        """
        Map lab values to model features
        
        Args:
            lab_data: Extracted lab values
            patient_data: Patient demographics (age, sex, etc.)
            
        Returns:
            Tuple of (feature_array, feature_dict)
        """
        features = {}
        
        # Patient demographics
        features["age"] = patient_data.get("age", 50) if patient_data else 50
        features["sex"] = patient_data.get("sex", 1) if patient_data else 1
        features["chest_pain_type"] = patient_data.get("chest_pain_type", 0) if patient_data else 0
        
        # Blood pressure
        bp = lab_data.get("blood_pressure", "120/80")
        if isinstance(bp, str):
            try:
                systolic, diastolic = map(int, bp.split("/"))
            except:
                systolic, diastolic = 120, 80
        else:
            systolic, diastolic = 140, 90
        
        features["resting_bp"] = systolic
        
        # Cholesterol
        features["cholesterol"] = int(lab_data.get("cholesterol", 200))
        
        # Fasting blood sugar
        glucose = lab_data.get("glucose", 100)
        features["fasting_blood_sugar"] = 1 if glucose > 120 else 0
        
        # Resting ECG
        features["resting_ecg"] = patient_data.get("resting_ecg", 0) if patient_data else 0
        
        # Max heart rate
        features["max_heart_rate"] = int(lab_data.get("heart_rate", 150))
        
        # Exercise induced angina
        features["exercise_induced_angina"] = patient_data.get("exercise_induced_angina", 0) if patient_data else 0
        
        # ST depression
        features["st_depression"] = patient_data.get("st_depression", 0) if patient_data else 0
        
        # ST slope
        features["st_slope"] = patient_data.get("st_slope", 1) if patient_data else 1
        
        # Number of major vessels
        features["num_major_vessels"] = patient_data.get("num_major_vessels", 0) if patient_data else 0
        
        # Thalassemia
        features["thalassemia"] = patient_data.get("thalassemia", 0) if patient_data else 0
        
        # Convert to array
        feature_array = np.array([[features[name] for name in self.FEATURE_NAMES]])
        
        return feature_array, features
    
    def get_risk_factors(self, lab_data: Dict) -> List[str]:
        """
        Identify risk factors from lab values
        
        Args:
            lab_data: Extracted lab values
            
        Returns:
            List of identified risk factors
        """
        risk_factors = []
        
        # Cholesterol
        chol = lab_data.get("cholesterol", 0)
        if chol > 240:
            risk_factors.append(f"High cholesterol ({chol} mg/dL)")
        elif chol > 200:
            risk_factors.append(f"Borderline high cholesterol ({chol} mg/dL)")
        
        # LDL
        ldl = lab_data.get("ldl", 0)
        if ldl > 160:
            risk_factors.append(f"High LDL ({ldl} mg/dL)")
        elif ldl > 130:
            risk_factors.append(f"Borderline high LDL ({ldl} mg/dL)")
        
        # HDL
        hdl = lab_data.get("hdl", 0)
        if hdl < 40:
            risk_factors.append(f"Low HDL ({hdl} mg/dL)")
        
        # Triglycerides
        trig = lab_data.get("triglycerides", 0)
        if trig > 200:
            risk_factors.append(f"High triglycerides ({trig} mg/dL)")
        elif trig > 150:
            risk_factors.append(f"Borderline high triglycerides ({trig} mg/dL)")
        
        # Blood pressure
        bp = lab_data.get("blood_pressure", "120/80")
        if isinstance(bp, str):
            try:
                systolic, diastolic = map(int, bp.split("/"))
            except:
                systolic, diastolic = 120, 80
        else:
            systolic, diastolic = 140, 90
        
        if systolic > 140 or diastolic > 90:
            risk_factors.append(f"High blood pressure ({systolic}/{diastolic} mmHg)")
        elif systolic > 130 or diastolic > 80:
            risk_factors.append(f"Elevated blood pressure ({systolic}/{diastolic} mmHg)")
        
        # Glucose
        glucose = lab_data.get("glucose", 0)
        if glucose > 126:
            risk_factors.append(f"High blood glucose ({glucose} mg/dL) - Possible diabetes")
        elif glucose > 100:
            risk_factors.append(f"Elevated blood glucose ({glucose} mg/dL)")
        
        # Hemoglobin
        hgb = lab_data.get("hemoglobin", 0)
        if hgb < 12:
            risk_factors.append(f"Low hemoglobin ({hgb} g/dL) - Possible anemia")
        elif hgb > 17.5:
            risk_factors.append(f"High hemoglobin ({hgb} g/dL)")
        
        # Creatinine
        creat = lab_data.get("creatinine", 0)
        if creat > 1.3:
            risk_factors.append(f"High creatinine ({creat} mg/dL) - Possible kidney issues")
        
        return risk_factors
    
    def validate_lab_values(self, lab_data: Dict) -> Dict:
        """
        Validate lab values
        
        Args:
            lab_data: Lab values to validate
            
        Returns:
            Validation results
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check for missing critical values
        critical_values = ["cholesterol", "blood_pressure", "glucose"]
        missing = [v for v in critical_values if v not in lab_data or lab_data[v] is None]
        
        if missing:
            validation["warnings"].append(f"Missing values: {', '.join(missing)}")
        
        # Check for out-of-range values
        for key, (min_val, max_val) in self.NORMAL_RANGES.items():
            if key in lab_data and lab_data[key] is not None:
                value = lab_data[key]
                
                # Handle blood pressure specially
                if key.startswith("blood_pressure"):
                    continue
                
                if value < min_val or value > max_val:
                    validation["warnings"].append(
                        f"{key}: {value} is outside normal range ({min_val}-{max_val})"
                    )
        
        # Check blood pressure
        bp = lab_data.get("blood_pressure", "120/80")
        if isinstance(bp, str):
            try:
                systolic, diastolic = map(int, bp.split("/"))
                if systolic < 90 or systolic > 180:
                    validation["warnings"].append(f"Systolic BP {systolic} is unusual")
                if diastolic < 60 or diastolic > 120:
                    validation["warnings"].append(f"Diastolic BP {diastolic} is unusual")
            except:
                validation["errors"].append("Invalid blood pressure format")
                validation["valid"] = False
        
        return validation
    
    def get_feature_importance_hints(self, lab_data: Dict) -> Dict:
        """
        Get hints about which features are most important
        
        Args:
            lab_data: Lab values
            
        Returns:
            Feature importance hints
        """
        hints = {}
        
        # Cholesterol is very important
        chol = lab_data.get("cholesterol", 200)
        if chol > 240:
            hints["cholesterol"] = "CRITICAL - Very high"
        elif chol > 200:
            hints["cholesterol"] = "HIGH - Elevated"
        else:
            hints["cholesterol"] = "NORMAL"
        
        # Blood pressure is very important
        bp = lab_data.get("blood_pressure", "120/80")
        if isinstance(bp, str):
            try:
                systolic, _ = map(int, bp.split("/"))
                if systolic > 140:
                    hints["blood_pressure"] = "CRITICAL - Very high"
                elif systolic > 130:
                    hints["blood_pressure"] = "HIGH - Elevated"
                else:
                    hints["blood_pressure"] = "NORMAL"
            except:
                hints["blood_pressure"] = "UNKNOWN"
        
        # Glucose is important
        glucose = lab_data.get("glucose", 100)
        if glucose > 126:
            hints["glucose"] = "CRITICAL - Diabetic range"
        elif glucose > 100:
            hints["glucose"] = "HIGH - Prediabetic range"
        else:
            hints["glucose"] = "NORMAL"
        
        # HDL is important (higher is better)
        hdl = lab_data.get("hdl", 50)
        if hdl < 40:
            hints["hdl"] = "CRITICAL - Very low"
        elif hdl < 50:
            hints["hdl"] = "LOW - Below optimal"
        else:
            hints["hdl"] = "NORMAL"
        
        return hints
    
    def generate_lab_summary(self, lab_data: Dict) -> str:
        """
        Generate human-readable lab summary
        
        Args:
            lab_data: Lab values
            
        Returns:
            Summary text
        """
        summary_parts = []
        
        # Cholesterol
        chol = lab_data.get("cholesterol", 0)
        if chol > 240:
            summary_parts.append(f"⚠️ High cholesterol: {chol} mg/dL")
        elif chol > 200:
            summary_parts.append(f"⚠️ Borderline high cholesterol: {chol} mg/dL")
        else:
            summary_parts.append(f"✓ Normal cholesterol: {chol} mg/dL")
        
        # Blood pressure
        bp = lab_data.get("blood_pressure", "120/80")
        if isinstance(bp, str):
            summary_parts.append(f"Blood pressure: {bp} mmHg")
        
        # Glucose
        glucose = lab_data.get("glucose", 0)
        if glucose > 126:
            summary_parts.append(f"⚠️ High blood glucose: {glucose} mg/dL")
        elif glucose > 100:
            summary_parts.append(f"⚠️ Elevated blood glucose: {glucose} mg/dL")
        else:
            summary_parts.append(f"✓ Normal blood glucose: {glucose} mg/dL")
        
        # Heart rate
        hr = lab_data.get("heart_rate", 0)
        if hr > 100:
            summary_parts.append(f"⚠️ Elevated heart rate: {hr} bpm")
        elif hr < 60:
            summary_parts.append(f"⚠️ Low heart rate: {hr} bpm")
        else:
            summary_parts.append(f"✓ Normal heart rate: {hr} bpm")
        
        return "\n".join(summary_parts)


# Example usage
if __name__ == "__main__":
    mapper = LabValueMapper()
    
    # Example lab data
    lab_data = {
        "cholesterol": 250,
        "ldl": 160,
        "hdl": 35,
        "triglycerides": 200,
        "glucose": 130,
        "blood_pressure": "140/90",
        "heart_rate": 85,
        "hemoglobin": 13.2,
        "creatinine": 1.0
    }
    
    patient_data = {
        "age": 55,
        "sex": 1
    }
    
    # Map values
    features, feature_dict = mapper.map_lab_values(lab_data, patient_data)
    print("Mapped Features:")
    print(features)
    
    # Get risk factors
    risk_factors = mapper.get_risk_factors(lab_data)
    print("\nRisk Factors:")
    for rf in risk_factors:
        print(f"  • {rf}")
    
    # Validate
    validation = mapper.validate_lab_values(lab_data)
    print(f"\nValidation: {validation}")
    
    # Summary
    summary = mapper.generate_lab_summary(lab_data)
    print(f"\nLab Summary:\n{summary}")
