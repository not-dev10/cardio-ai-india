"""
Fusion Model Service
Combines tabular data + image features for enhanced predictions
"""

import numpy as np
import joblib
from typing import Dict, Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FusionModelService:
    """Fusion model for combining multiple data sources"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize fusion model
        
        Args:
            model_path: Path to pre-trained fusion model
        """
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        if model_path and Path(model_path).exists():
            self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Load pre-trained fusion model"""
        try:
            self.model = joblib.load(model_path)
            logger.info(f"Loaded fusion model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load fusion model: {e}")
            self.model = None
    
    def predict(
        self,
        tabular_features: np.ndarray,
        ecg_features: Optional[Dict] = None,
        xray_features: Optional[Dict] = None,
        angio_features: Optional[Dict] = None,
        tabular_model=None
    ) -> Dict:
        """
        Make prediction using fusion approach
        
        Args:
            tabular_features: Tabular patient data (18 features)
            ecg_features: ECG image features
            xray_features: X-ray image features
            angio_features: Angiography image features
            tabular_model: Pre-trained tabular model for baseline prediction
            
        Returns:
            Fusion prediction with confidence
        """
        predictions = {}
        
        # Get tabular prediction
        if tabular_model is not None:
            try:
                tabular_pred = float(tabular_model.predict_proba(
                    tabular_features.reshape(1, -1)
                )[0][1])
                predictions["tabular"] = tabular_pred
                predictions["tabular_confidence"] = 0.9
            except Exception as e:
                logger.error(f"Tabular prediction failed: {e}")
                predictions["tabular"] = 0.5
                predictions["tabular_confidence"] = 0.0
        
        # Get image predictions
        image_predictions = []
        image_weights = []
        
        if ecg_features is not None:
            ecg_pred = self._predict_from_ecg(ecg_features)
            predictions["ecg"] = ecg_pred
            image_predictions.append(ecg_pred)
            image_weights.append(0.3)  # ECG weight
        
        if xray_features is not None:
            xray_pred = self._predict_from_xray(xray_features)
            predictions["xray"] = xray_pred
            image_predictions.append(xray_pred)
            image_weights.append(0.25)  # X-ray weight
        
        if angio_features is not None:
            angio_pred = self._predict_from_angio(angio_features)
            predictions["angio"] = angio_pred
            image_predictions.append(angio_pred)
            image_weights.append(0.25)  # Angio weight
        
        # Combine predictions
        if "tabular" in predictions and image_predictions:
            # Weighted fusion
            image_pred = np.average(image_predictions, weights=image_weights[:len(image_predictions)])
            
            # Combine tabular and image predictions
            fusion_pred = (
                0.6 * predictions["tabular"] +
                0.4 * image_pred
            )
            
            predictions["fusion"] = fusion_pred
            predictions["fusion_confidence"] = min(
                predictions.get("tabular_confidence", 0.9),
                np.mean([0.8] * len(image_predictions))
            )
        elif "tabular" in predictions:
            predictions["fusion"] = predictions["tabular"]
            predictions["fusion_confidence"] = predictions.get("tabular_confidence", 0.9)
        elif image_predictions:
            predictions["fusion"] = np.mean(image_predictions)
            predictions["fusion_confidence"] = 0.7
        else:
            predictions["fusion"] = 0.5
            predictions["fusion_confidence"] = 0.0
        
        return predictions
    
    def _predict_from_ecg(self, ecg_features: Dict) -> float:
        """
        Predict risk from ECG features
        
        Args:
            ecg_features: ECG feature dictionary
            
        Returns:
            Risk prediction (0-1)
        """
        abnormality_score = ecg_features.get("abnormality_score", 0.0)
        signal_quality = ecg_features.get("signal_quality", 0.5)
        
        # Adjust for signal quality
        if signal_quality < 0.3:
            # Poor quality - reduce confidence
            return abnormality_score * 0.5
        
        return min(1.0, abnormality_score)
    
    def _predict_from_xray(self, xray_features: Dict) -> float:
        """
        Predict risk from X-ray features
        
        Args:
            xray_features: X-ray feature dictionary
            
        Returns:
            Risk prediction (0-1)
        """
        cardiomegaly_score = xray_features.get("cardiomegaly_score", 0.0)
        edema_score = xray_features.get("edema_score", 0.0)
        
        # Combine findings
        risk = max(cardiomegaly_score, edema_score)
        
        return min(1.0, risk)
    
    def _predict_from_angio(self, angio_features: Dict) -> float:
        """
        Predict risk from Angiography features
        
        Args:
            angio_features: Angiography feature dictionary
            
        Returns:
            Risk prediction (0-1)
        """
        blockage_score = angio_features.get("blockage_score", 0.0)
        
        return min(1.0, blockage_score)
    
    def get_feature_importance(self, predictions: Dict) -> Dict:
        """
        Get feature importance from predictions
        
        Args:
            predictions: Prediction dictionary
            
        Returns:
            Feature importance scores
        """
        importance = {}
        
        if "tabular" in predictions:
            importance["tabular_data"] = predictions["tabular"]
        
        if "ecg" in predictions:
            importance["ecg_findings"] = predictions["ecg"]
        
        if "xray" in predictions:
            importance["xray_findings"] = predictions["xray"]
        
        if "angio" in predictions:
            importance["angiography_findings"] = predictions["angio"]
        
        # Normalize
        total = sum(importance.values()) if importance else 1.0
        if total > 0:
            importance = {k: v / total for k, v in importance.items()}
        
        return importance
    
    def generate_fusion_report(
        self,
        predictions: Dict,
        tabular_data: Dict,
        ecg_features: Optional[Dict] = None,
        xray_features: Optional[Dict] = None,
        angio_features: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive fusion report
        
        Args:
            predictions: Prediction dictionary
            tabular_data: Tabular patient data
            ecg_features: ECG features
            xray_features: X-ray features
            angio_features: Angiography features
            
        Returns:
            Comprehensive report
        """
        fusion_score = predictions.get("fusion", 0.5)
        
        # Categorize risk
        if fusion_score > 0.7:
            risk_level = "HIGH"
            risk_category = "High Risk - Immediate Consultation Required"
        elif fusion_score > 0.4:
            risk_level = "MODERATE"
            risk_category = "Moderate Risk - Schedule Consultation"
        else:
            risk_level = "LOW"
            risk_category = "Low Risk - Regular Monitoring"
        
        # Build report
        report = {
            "fusion_score": float(fusion_score),
            "risk_level": risk_level,
            "risk_category": risk_category,
            "confidence": float(predictions.get("fusion_confidence", 0.0)),
            "predictions": predictions,
            "feature_importance": self.get_feature_importance(predictions),
            "data_sources": self._get_data_sources(
                ecg_features, xray_features, angio_features
            ),
            "findings": self._compile_findings(
                tabular_data, ecg_features, xray_features, angio_features
            )
        }
        
        return report
    
    def _get_data_sources(
        self,
        ecg_features: Optional[Dict],
        xray_features: Optional[Dict],
        angio_features: Optional[Dict]
    ) -> list:
        """Get list of data sources used"""
        sources = ["Tabular Data"]
        
        if ecg_features is not None:
            sources.append("ECG Image")
        
        if xray_features is not None:
            sources.append("X-ray Image")
        
        if angio_features is not None:
            sources.append("Angiography Image")
        
        return sources
    
    def _compile_findings(
        self,
        tabular_data: Dict,
        ecg_features: Optional[Dict],
        xray_features: Optional[Dict],
        angio_features: Optional[Dict]
    ) -> Dict:
        """Compile findings from all sources"""
        findings = {
            "tabular": self._summarize_tabular(tabular_data),
            "imaging": []
        }
        
        if ecg_features is not None:
            findings["imaging"].append({
                "type": "ECG",
                "findings": ecg_features.get("findings", {})
            })
        
        if xray_features is not None:
            findings["imaging"].append({
                "type": "X-ray",
                "findings": xray_features.get("findings", {})
            })
        
        if angio_features is not None:
            findings["imaging"].append({
                "type": "Angiography",
                "findings": angio_features.get("findings", {})
            })
        
        return findings
    
    def _summarize_tabular(self, tabular_data: Dict) -> Dict:
        """Summarize tabular findings"""
        summary = {}
        
        # Key risk factors
        if tabular_data.get("cholesterol", 0) > 240:
            summary["high_cholesterol"] = True
        
        if tabular_data.get("resting_bp", 0) > 140:
            summary["high_blood_pressure"] = True
        
        if tabular_data.get("fasting_blood_sugar", 0) == 1:
            summary["high_blood_sugar"] = True
        
        if tabular_data.get("age", 0) > 60:
            summary["advanced_age"] = True
        
        return summary


# Example usage
if __name__ == "__main__":
    fusion_service = FusionModelService()
    
    # Example data
    tabular_features = np.array([[55, 1, 3, 140, 250, 1, 0, 85, 0, 2.5, 1, 0, 2]])
    
    ecg_features = {
        "abnormality_score": 0.3,
        "signal_quality": 0.8
    }
    
    xray_features = {
        "cardiomegaly_score": 0.2,
        "edema_score": 0.1
    }
    
    # Make prediction
    predictions = fusion_service.predict(
        tabular_features,
        ecg_features=ecg_features,
        xray_features=xray_features
    )
    
    print(f"Fusion Score: {predictions['fusion']:.3f}")
    print(f"Confidence: {predictions['fusion_confidence']:.3f}")
