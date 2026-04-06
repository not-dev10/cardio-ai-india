"""
Medical-Grade Validation Module
Ensures all predictions meet clinical standards
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels for clinical use"""
    HIGH = "high"  # Use prediction
    MEDIUM = "medium"  # Flag for review
    LOW = "low"  # Reject prediction


@dataclass
class ValidationResult:
    """Result of medical validation"""
    is_valid: bool
    confidence_level: ConfidenceLevel
    errors: List[str]
    warnings: List[str]
    data_quality_score: float
    clinical_notes: str
    timestamp: str


class MedicalValidator:
    """Validates patient data and predictions for clinical use"""
    
    # Normal ranges for Indian population
    NORMAL_RANGES = {
        "age": (18, 100),
        "resting_bp": (60, 250),
        "cholesterol": (100, 400),
        "max_heart_rate": (40, 220),
        "st_depression": (0, 10),
        "fasting_blood_sugar": (40, 400),
    }
    
    # Optimal ranges (for risk assessment)
    OPTIMAL_RANGES = {
        "resting_bp": (90, 120),
        "cholesterol": (150, 200),
        "max_heart_rate": (60, 100),
        "fasting_blood_sugar": (70, 100),
    }
    
    def __init__(self):
        """Initialize validator"""
        self.validation_log = []
    
    def validate_input_data(self, patient_data: Dict) -> ValidationResult:
        """
        Validate patient input data for clinical use
        
        Args:
            patient_data: Dictionary of patient features
            
        Returns:
            ValidationResult with detailed validation info
        """
        errors = []
        warnings = []
        data_quality_score = 1.0
        
        # Check required fields
        required_fields = [
            "age", "sex", "chest_pain_type", "resting_bp", "cholesterol",
            "fasting_blood_sugar", "resting_ecg", "max_heart_rate",
            "exercise_induced_angina", "st_depression", "st_slope",
            "num_major_vessels", "thalassemia"
        ]
        
        for field in required_fields:
            if field not in patient_data:
                errors.append(f"Missing required field: {field}")
                data_quality_score -= 0.1
        
        # Validate ranges
        for field, (min_val, max_val) in self.NORMAL_RANGES.items():
            if field in patient_data:
                value = patient_data[field]
                if not (min_val <= value <= max_val):
                    errors.append(
                        f"{field} out of range: {value} (expected {min_val}-{max_val})"
                    )
                    data_quality_score -= 0.05
        
        # Check for optimal ranges (warnings)
        for field, (min_val, max_val) in self.OPTIMAL_RANGES.items():
            if field in patient_data:
                value = patient_data[field]
                if not (min_val <= value <= max_val):
                    warnings.append(
                        f"{field} outside optimal range: {value} (optimal {min_val}-{max_val})"
                    )
        
        # Logical consistency checks
        consistency_errors = self._check_logical_consistency(patient_data)
        errors.extend(consistency_errors)
        data_quality_score -= len(consistency_errors) * 0.05
        
        # Determine confidence level
        confidence_level = self._determine_confidence_level(
            len(errors), len(warnings), data_quality_score
        )
        
        is_valid = len(errors) == 0 and data_quality_score >= 0.7
        
        clinical_notes = self._generate_clinical_notes(patient_data, warnings)
        
        result = ValidationResult(
            is_valid=is_valid,
            confidence_level=confidence_level,
            errors=errors,
            warnings=warnings,
            data_quality_score=max(0, data_quality_score),
            clinical_notes=clinical_notes,
            timestamp=datetime.now().isoformat()
        )
        
        self.validation_log.append(result)
        return result
    
    def validate_prediction(
        self,
        prediction: float,
        confidence: float,
        ensemble_agreement: float
    ) -> Tuple[ConfidenceLevel, str]:
        """
        Validate prediction for clinical use
        
        Args:
            prediction: Predicted probability (0-1)
            confidence: Model confidence score (0-1)
            ensemble_agreement: Agreement between ensemble models (0-1)
            
        Returns:
            Tuple of (confidence_level, recommendation)
        """
        # High confidence: Use prediction
        if (prediction > 0.85 or prediction < 0.15) and \
           confidence > 0.85 and ensemble_agreement > 0.90:
            return (
                ConfidenceLevel.HIGH,
                "Prediction can be used for clinical decision-making"
            )
        
        # Medium confidence: Flag for review
        elif (prediction > 0.70 or prediction < 0.30) and \
             confidence > 0.70 and ensemble_agreement > 0.70:
            return (
                ConfidenceLevel.MEDIUM,
                "Recommend cardiologist consultation for confirmation"
            )
        
        # Low confidence: Reject prediction
        else:
            return (
                ConfidenceLevel.LOW,
                "Prediction confidence too low. Require manual review by cardiologist"
            )
    
    def _check_logical_consistency(self, patient_data: Dict) -> List[str]:
        """Check logical consistency of patient data"""
        errors = []
        
        # Age vs disease prevalence
        age = patient_data.get("age", 0)
        if age < 30 and patient_data.get("num_major_vessels", 0) > 2:
            errors.append("Young age with multiple vessel disease - verify data")
        
        # Blood pressure consistency
        resting_bp = patient_data.get("resting_bp", 0)
        max_hr = patient_data.get("max_heart_rate", 0)
        if resting_bp > 180 and max_hr > 150:
            errors.append("High BP with high max HR - verify data quality")
        
        # Cholesterol vs blood sugar
        chol = patient_data.get("cholesterol", 0)
        bs = patient_data.get("fasting_blood_sugar", 0)
        if chol > 300 and bs > 200:
            errors.append("Very high cholesterol and blood sugar - verify data")
        
        # ST depression vs max heart rate
        st_dep = patient_data.get("st_depression", 0)
        if st_dep > 5 and max_hr < 60:
            errors.append("High ST depression with low max HR - verify data")
        
        return errors
    
    def _determine_confidence_level(
        self,
        num_errors: int,
        num_warnings: int,
        data_quality_score: float
    ) -> ConfidenceLevel:
        """Determine confidence level based on validation results"""
        if num_errors > 0 or data_quality_score < 0.7:
            return ConfidenceLevel.LOW
        elif num_warnings > 2 or data_quality_score < 0.85:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.HIGH
    
    def _generate_clinical_notes(
        self,
        patient_data: Dict,
        warnings: List[str]
    ) -> str:
        """Generate clinical notes based on patient data"""
        notes = []
        
        # Age-based notes
        age = patient_data.get("age", 0)
        if age > 65:
            notes.append("Elderly patient - higher baseline risk")
        elif age < 40:
            notes.append("Young patient - lower baseline risk")
        
        # Risk factor notes
        resting_bp = patient_data.get("resting_bp", 0)
        if resting_bp > 140:
            notes.append("Hypertension present - significant risk factor")
        
        chol = patient_data.get("cholesterol", 0)
        if chol > 240:
            notes.append("High cholesterol - requires intervention")
        
        bs = patient_data.get("fasting_blood_sugar", 0)
        if bs > 126:
            notes.append("Elevated fasting blood sugar - diabetes risk")
        
        st_dep = patient_data.get("st_depression", 0)
        if st_dep > 2:
            notes.append("Significant ST depression - concerning finding")
        
        return " | ".join(notes) if notes else "No significant clinical notes"
    
    def validate_lab_values(self, lab_data: Dict) -> Dict:
        """
        Validate lab values against normal ranges
        
        Args:
            lab_data: Dictionary of lab values
            
        Returns:
            Dictionary with validation results
        """
        lab_ranges = {
            "cholesterol_total": (150, 200, "mg/dL"),
            "cholesterol_ldl": (0, 100, "mg/dL"),
            "cholesterol_hdl": (40, 100, "mg/dL"),
            "triglycerides": (0, 150, "mg/dL"),
            "blood_sugar_fasting": (70, 100, "mg/dL"),
            "hemoglobin_a1c": (4, 6, "%"),
            "creatinine": (0.7, 1.3, "mg/dL"),
            "potassium": (3.5, 5.0, "mEq/L"),
            "sodium": (135, 145, "mEq/L"),
        }
        
        results = {}
        for lab, (min_val, max_val, unit) in lab_ranges.items():
            if lab in lab_data:
                value = lab_data[lab]
                is_normal = min_val <= value <= max_val
                results[lab] = {
                    "value": value,
                    "unit": unit,
                    "normal_range": f"{min_val}-{max_val}",
                    "is_normal": is_normal,
                    "status": "Normal" if is_normal else "Abnormal"
                }
        
        return results
    
    def get_validation_report(self) -> pd.DataFrame:
        """Get validation report for all logged validations"""
        report_data = []
        for result in self.validation_log:
            report_data.append({
                "timestamp": result.timestamp,
                "is_valid": result.is_valid,
                "confidence_level": result.confidence_level.value,
                "data_quality_score": result.data_quality_score,
                "num_errors": len(result.errors),
                "num_warnings": len(result.warnings),
            })
        
        return pd.DataFrame(report_data)


class ClinicalThresholds:
    """Clinical decision thresholds for different risk levels"""
    
    # Sensitivity/Specificity targets
    SENSITIVITY_TARGET = 0.90  # Catch 90% of disease cases
    SPECIFICITY_TARGET = 0.95  # Avoid 95% of false alarms
    
    # Risk stratification thresholds
    LOW_RISK_THRESHOLD = 0.10
    MEDIUM_RISK_THRESHOLD = 0.50
    HIGH_RISK_THRESHOLD = 0.90
    
    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD = 0.70
    
    # Ensemble agreement threshold
    ENSEMBLE_AGREEMENT_THRESHOLD = 0.90
    
    @staticmethod
    def get_risk_category(probability: float) -> str:
        """Get risk category based on probability"""
        if probability < ClinicalThresholds.LOW_RISK_THRESHOLD:
            return "Low Risk"
        elif probability < ClinicalThresholds.MEDIUM_RISK_THRESHOLD:
            return "Medium Risk"
        else:
            return "High Risk"
    
    @staticmethod
    def get_clinical_recommendation(risk_category: str) -> str:
        """Get clinical recommendation based on risk category"""
        recommendations = {
            "Low Risk": "Routine follow-up in 1 year. Maintain healthy lifestyle.",
            "Medium Risk": "Cardiology consultation within 2-4 weeks. Consider additional testing.",
            "High Risk": "Urgent cardiology consultation (< 1 week). Comprehensive evaluation needed."
        }
        return recommendations.get(risk_category, "Unknown risk category")


def example_validation():
    """Example usage of medical validator"""
    validator = MedicalValidator()
    
    # Example patient data
    patient_data = {
        "age": 55,
        "sex": 1,
        "chest_pain_type": 2,
        "resting_bp": 140,
        "cholesterol": 250,
        "fasting_blood_sugar": 1,
        "resting_ecg": 1,
        "max_heart_rate": 150,
        "exercise_induced_angina": 0,
        "st_depression": 1.5,
        "st_slope": 1,
        "num_major_vessels": 1,
        "thalassemia": 2
    }
    
    # Validate input
    validation_result = validator.validate_input_data(patient_data)
    
    print("\n" + "="*60)
    print("MEDICAL VALIDATION REPORT")
    print("="*60)
    print(f"Valid: {validation_result.is_valid}")
    print(f"Confidence Level: {validation_result.confidence_level.value}")
    print(f"Data Quality Score: {validation_result.data_quality_score:.2%}")
    print(f"Clinical Notes: {validation_result.clinical_notes}")
    
    if validation_result.errors:
        print("\nErrors:")
        for error in validation_result.errors:
            print(f"  - {error}")
    
    if validation_result.warnings:
        print("\nWarnings:")
        for warning in validation_result.warnings:
            print(f"  - {warning}")
    
    # Validate prediction
    prediction_prob = 0.73
    confidence = 0.73
    ensemble_agreement = 0.92
    
    conf_level, recommendation = validator.validate_prediction(
        prediction_prob, confidence, ensemble_agreement
    )
    
    print(f"\nPrediction Validation:")
    print(f"  Confidence Level: {conf_level.value}")
    print(f"  Recommendation: {recommendation}")
    
    # Get risk category
    risk_category = ClinicalThresholds.get_risk_category(prediction_prob)
    clinical_rec = ClinicalThresholds.get_clinical_recommendation(risk_category)
    
    print(f"\nClinical Decision:")
    print(f"  Risk Category: {risk_category}")
    print(f"  Recommendation: {clinical_rec}")
    
    print("="*60)


if __name__ == "__main__":
    example_validation()
