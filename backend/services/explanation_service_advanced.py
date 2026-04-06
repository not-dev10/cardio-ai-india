"""
Advanced Explanation Service using SHAP
Provides interpretable AI explanations for cardiac risk predictions
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class SHAPExplanationService:
    """Generate SHAP-based explanations for predictions"""
    
    def __init__(self, model=None, feature_names: Optional[List[str]] = None):
        """
        Initialize SHAP explanation service
        
        Args:
            model: Pre-trained model for explanation
            feature_names: List of feature names
        """
        self.model = model
        self.feature_names = feature_names or self._get_default_feature_names()
        self.explainer = None
        
        if model is not None:
            self._initialize_explainer()
    
    def _get_default_feature_names(self) -> List[str]:
        """Get default feature names for cardiac model"""
        return [
            "age", "sex", "chest_pain_type", "resting_bp", "cholesterol",
            "fasting_blood_sugar", "resting_ecg", "max_heart_rate",
            "exercise_induced_angina", "st_depression", "st_slope",
            "num_major_vessels", "thalassemia", "smoking", "diabetes",
            "ecg_abnormality", "xray_abnormality", "angio_abnormality"
        ]
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer"""
        try:
            import shap
            
            # Use TreeExplainer for tree-based models
            if hasattr(self.model, 'predict_proba'):
                self.explainer = shap.TreeExplainer(self.model)
            else:
                # Fallback to KernelExplainer
                self.explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    np.zeros((1, len(self.feature_names)))
                )
            
            logger.info("SHAP explainer initialized successfully")
        except ImportError:
            logger.warning("SHAP not installed - using fallback explanations")
            self.explainer = None
        except Exception as e:
            logger.error(f"Failed to initialize SHAP explainer: {e}")
            self.explainer = None
    
    def explain_prediction(
        self,
        input_data: np.ndarray,
        prediction: float,
        top_n: int = 5
    ) -> Dict:
        """
        Generate SHAP explanation for prediction
        
        Args:
            input_data: Input features (1D array)
            prediction: Model prediction
            top_n: Number of top features to explain
            
        Returns:
            Explanation dictionary
        """
        if self.explainer is not None:
            return self._explain_with_shap(input_data, prediction, top_n)
        else:
            return self._explain_with_fallback(input_data, prediction, top_n)
    
    def _explain_with_shap(
        self,
        input_data: np.ndarray,
        prediction: float,
        top_n: int
    ) -> Dict:
        """Generate explanation using SHAP"""
        try:
            import shap
            
            # Reshape input
            if input_data.ndim == 1:
                input_data = input_data.reshape(1, -1)
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(input_data)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                # For binary classification, take positive class
                shap_values = shap_values[1]
            
            # Get feature importance
            feature_importance = np.abs(shap_values[0])
            
            # Sort by importance
            sorted_idx = np.argsort(feature_importance)[::-1][:top_n]
            
            # Build explanations
            explanations = []
            for idx in sorted_idx:
                feature_name = self.feature_names[idx] if idx < len(self.feature_names) else f"Feature_{idx}"
                importance = float(feature_importance[idx])
                direction = "increased" if shap_values[0][idx] > 0 else "decreased"
                value = float(input_data[0][idx])
                
                explanations.append({
                    "feature": feature_name,
                    "importance": importance,
                    "direction": direction,
                    "value": value,
                    "impact": f"{feature_name} ({value:.1f}) {direction} risk by {importance*100:.1f}%",
                    "shap_value": float(shap_values[0][idx])
                })
            
            return {
                "method": "SHAP",
                "prediction": float(prediction),
                "explanations": explanations,
                "base_value": float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else 0.5,
                "confidence": 0.95
            }
        
        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            return self._explain_with_fallback(input_data, prediction, top_n)
    
    def _explain_with_fallback(
        self,
        input_data: np.ndarray,
        prediction: float,
        top_n: int
    ) -> Dict:
        """Fallback explanation method"""
        if input_data.ndim == 1:
            input_data = input_data.reshape(1, -1)
        
        # Simple feature importance based on deviation from mean
        mean_values = np.array([50, 1, 2, 130, 200, 0, 1, 150, 0, 1, 1, 0, 0, 0, 0, 0.2, 0.1, 0.1])
        
        # Normalize features
        normalized = np.abs(input_data[0] - mean_values[:len(input_data[0])])
        
        # Get top features
        sorted_idx = np.argsort(normalized)[::-1][:top_n]
        
        explanations = []
        for idx in sorted_idx:
            feature_name = self.feature_names[idx] if idx < len(self.feature_names) else f"Feature_{idx}"
            value = float(input_data[0][idx])
            deviation = float(normalized[idx])
            
            # Determine direction
            if value > mean_values[idx]:
                direction = "increased"
            else:
                direction = "decreased"
            
            explanations.append({
                "feature": feature_name,
                "importance": float(deviation / np.max(normalized)) if np.max(normalized) > 0 else 0.0,
                "direction": direction,
                "value": value,
                "impact": f"{feature_name} ({value:.1f}) {direction} risk",
                "shap_value": float(deviation)
            })
        
        return {
            "method": "Fallback",
            "prediction": float(prediction),
            "explanations": explanations,
            "base_value": 0.5,
            "confidence": 0.7
        }
    
    def generate_clinical_summary(
        self,
        explanations: Dict,
        risk_level: str
    ) -> str:
        """
        Generate clinical summary from explanations
        
        Args:
            explanations: Explanation dictionary
            risk_level: Risk level (LOW, MODERATE, HIGH)
            
        Returns:
            Clinical summary text
        """
        summary_parts = []
        
        # Risk level summary
        if risk_level == "HIGH":
            summary_parts.append(
                "⚠️ HIGH RISK: This patient shows significant cardiac risk factors and requires immediate medical attention."
            )
        elif risk_level == "MODERATE":
            summary_parts.append(
                "⚠️ MODERATE RISK: This patient has notable cardiac risk factors that warrant close monitoring and consultation."
            )
        else:
            summary_parts.append(
                "✅ LOW RISK: This patient shows minimal cardiac risk factors. Continue regular health monitoring."
            )
        
        # Key findings
        summary_parts.append("\nKey Risk Factors:")
        for exp in explanations.get("explanations", [])[:3]:
            summary_parts.append(f"  • {exp['impact']}")
        
        return "\n".join(summary_parts)
    
    def generate_recommendations(
        self,
        explanations: Dict,
        risk_level: str
    ) -> List[str]:
        """
        Generate recommendations based on explanations
        
        Args:
            explanations: Explanation dictionary
            risk_level: Risk level
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Risk-based recommendations
        if risk_level == "HIGH":
            recommendations.extend([
                "🚨 URGENT: Schedule immediate consultation with a cardiologist",
                "📞 Call emergency services if experiencing chest pain or shortness of breath",
                "🏥 Consider comprehensive cardiac evaluation including stress test",
                "💊 Discuss medication options with your healthcare provider"
            ])
        elif risk_level == "MODERATE":
            recommendations.extend([
                "📅 Schedule cardiologist appointment within 2 weeks",
                "🏥 Get comprehensive cardiac evaluation",
                "💉 Consider stress test or advanced imaging"
            ])
        else:
            recommendations.extend([
                "✅ Continue regular health checkups",
                "📋 Monitor risk factors annually"
            ])
        
        # Feature-specific recommendations
        for exp in explanations.get("explanations", []):
            feature = exp["feature"].lower()
            
            if "cholesterol" in feature and exp["direction"] == "increased":
                recommendations.append("🥗 Reduce saturated fat intake, increase fiber and omega-3 fatty acids")
            
            if "blood_pressure" in feature and exp["direction"] == "increased":
                recommendations.append("🧂 Reduce salt intake, manage stress, practice relaxation techniques")
            
            if "heart_rate" in feature and exp["direction"] == "increased":
                recommendations.append("🏃 Increase physical activity (30 min/day), practice meditation")
            
            if "blood_sugar" in feature and exp["direction"] == "increased":
                recommendations.append("🍎 Manage blood sugar through diet and exercise")
            
            if "smoking" in feature:
                recommendations.append("🚭 Quit smoking immediately - critical for cardiac health")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def explain_report_findings(
        self,
        extracted_data: Dict,
        structured_data: Dict
    ) -> Dict:
        """
        Explain findings from medical report
        
        Args:
            extracted_data: Raw extracted data
            structured_data: Structured medical data
            
        Returns:
            Explanation of findings
        """
        findings = {
            "blood_work": self._explain_blood_work(structured_data),
            "vital_signs": self._explain_vital_signs(structured_data),
            "risk_factors": self._identify_risk_factors(structured_data)
        }
        
        return findings
    
    def _explain_blood_work(self, data: Dict) -> Dict:
        """Explain blood work findings"""
        findings = {}
        
        # Cholesterol
        chol = data.get("cholesterol", 0)
        if chol > 240:
            findings["cholesterol"] = f"High ({chol} mg/dL) - Increased cardiac risk"
        elif chol > 200:
            findings["cholesterol"] = f"Borderline high ({chol} mg/dL) - Monitor closely"
        else:
            findings["cholesterol"] = f"Normal ({chol} mg/dL)"
        
        # Blood sugar
        glucose = data.get("glucose", 0)
        if glucose > 126:
            findings["glucose"] = f"High ({glucose} mg/dL) - Possible diabetes"
        elif glucose > 100:
            findings["glucose"] = f"Elevated ({glucose} mg/dL) - Prediabetic range"
        else:
            findings["glucose"] = f"Normal ({glucose} mg/dL)"
        
        # Hemoglobin
        hgb = data.get("hemoglobin", 0)
        if hgb < 12:
            findings["hemoglobin"] = f"Low ({hgb} g/dL) - Possible anemia"
        elif hgb > 17:
            findings["hemoglobin"] = f"High ({hgb} g/dL) - Possible polycythemia"
        else:
            findings["hemoglobin"] = f"Normal ({hgb} g/dL)"
        
        return findings
    
    def _explain_vital_signs(self, data: Dict) -> Dict:
        """Explain vital signs"""
        findings = {}
        
        # Blood pressure
        bp = data.get("blood_pressure", "120/80")
        if isinstance(bp, str):
            try:
                systolic, diastolic = map(int, bp.split("/"))
            except:
                systolic, diastolic = 120, 80
        else:
            systolic, diastolic = 140, 90
        
        if systolic > 140 or diastolic > 90:
            findings["blood_pressure"] = f"{systolic}/{diastolic} - High (Stage 2 Hypertension)"
        elif systolic > 130 or diastolic > 80:
            findings["blood_pressure"] = f"{systolic}/{diastolic} - Elevated (Stage 1 Hypertension)"
        else:
            findings["blood_pressure"] = f"{systolic}/{diastolic} - Normal"
        
        # Heart rate
        hr = data.get("heart_rate", 70)
        if hr > 100:
            findings["heart_rate"] = f"{hr} bpm - Tachycardia"
        elif hr < 60:
            findings["heart_rate"] = f"{hr} bpm - Bradycardia"
        else:
            findings["heart_rate"] = f"{hr} bpm - Normal"
        
        return findings
    
    def _identify_risk_factors(self, data: Dict) -> List[str]:
        """Identify cardiac risk factors"""
        risk_factors = []
        
        # Age
        age = data.get("age", 50)
        if age > 60:
            risk_factors.append(f"Advanced age ({age} years)")
        
        # Cholesterol
        if data.get("cholesterol", 0) > 240:
            risk_factors.append("High cholesterol")
        
        # Blood pressure
        bp = data.get("blood_pressure", "120/80")
        if isinstance(bp, str):
            try:
                systolic, _ = map(int, bp.split("/"))
                if systolic > 140:
                    risk_factors.append("High blood pressure")
            except:
                pass
        
        # Blood sugar
        if data.get("glucose", 0) > 126:
            risk_factors.append("High blood sugar/Diabetes")
        
        # Smoking
        if data.get("smoking", 0) == 1:
            risk_factors.append("Smoking")
        
        # Diabetes
        if data.get("diabetes", 0) == 1:
            risk_factors.append("Diabetes")
        
        return risk_factors if risk_factors else ["No major risk factors identified"]


# Example usage
if __name__ == "__main__":
    explanation_service = SHAPExplanationService()
    
    # Example input
    input_data = np.array([55, 1, 3, 140, 250, 1, 0, 85, 0, 2.5, 1, 0, 2, 0, 0, 0.3, 0.2, 0.1])
    prediction = 0.75
    
    # Generate explanation
    explanation = explanation_service.explain_prediction(input_data, prediction)
    print(json.dumps(explanation, indent=2))
    
    # Generate recommendations
    recommendations = explanation_service.generate_recommendations(explanation, "HIGH")
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"  {rec}")
