"""
Prediction module for heart disease risk assessment
"""
import numpy as np
import joblib
from config import MODELS_DIR, RISK_THRESHOLDS


class HeartDiseasePredictor:
    """Handle predictions for heart disease risk"""
    
    def __init__(self):
        """Initialize predictor"""
        self.model_data = None
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.optimal_threshold = 0.5
        self.load_model()
    
    def load_model(self):
        """Load trained model bundle"""
        model_path = MODELS_DIR / "heart_disease_model.joblib"
        try:
            self.model_data = joblib.load(model_path)
            self.model = self.model_data["model"]
            self.scaler = self.model_data["scaler"]
            self.feature_names = self.model_data["feature_names"]
            self.optimal_threshold = self.model_data["optimal_threshold"]
            print(f"Model loaded: {model_path}")
            print(f"Optimal threshold: {self.optimal_threshold:.3f}")
        except FileNotFoundError:
            print(f"Error: Model not found at {model_path}")
            print("Please train the model first using train.py")
    
    def preprocess_input(self, input_data):
        """
        Preprocess input data
        
        Args:
            input_data: Dictionary or array of input features
            
        Returns:
            np.array: Preprocessed features
        """
        if isinstance(input_data, dict):
            # Convert dict to array (ensure correct order)
            input_array = np.array(list(input_data.values())).reshape(1, -1)
        else:
            input_array = np.array(input_data).reshape(1, -1)
        
        # Scale features
        if self.scaler:
            input_scaled = self.scaler.transform(input_array)
        else:
            input_scaled = input_array
        
        return input_scaled
    
    def predict(self, input_data):
        """
        Make prediction
        
        Args:
            input_data: Input features (dict or array)
            
        Returns:
            dict: Prediction results
        """
        if self.model is None:
            return {"error": "Model not loaded"}
        
        # Preprocess
        input_processed = self.preprocess_input(input_data)
        
        # Get probability
        probability = self.model.predict_proba(input_processed)[0]
        risk_prob = probability[1]  # Probability of heart disease
        
        # Use optimal threshold for prediction
        prediction = 1 if risk_prob >= self.optimal_threshold else 0
        
        # Determine risk level
        risk_level = self._get_risk_level(risk_prob)
        
        # Get recommendations
        recommendations = self._get_recommendations(risk_level, input_data)
        
        return {
            "prediction": int(prediction),
            "probability": float(risk_prob),
            "risk_level": risk_level,
            "confidence": float(max(probability)),
            "recommendations": recommendations
        }
    
    def _get_risk_level(self, probability):
        """
        Determine risk level based on probability
        
        Args:
            probability: Prediction probability
            
        Returns:
            str: Risk level (Low, Medium, High)
        """
        if probability < RISK_THRESHOLDS["low"]:
            return "Low"
        elif probability < RISK_THRESHOLDS["medium"]:
            return "Medium"
        else:
            return "High"
    
    def _get_recommendations(self, risk_level, input_data):
        """
        Generate health recommendations based on risk level
        
        Args:
            risk_level: Predicted risk level
            input_data: Input features
            
        Returns:
            list: Health recommendations
        """
        recommendations = []
        
        if risk_level == "Low":
            recommendations = [
                "Maintain a healthy lifestyle with regular exercise",
                "Continue balanced diet with low salt and saturated fats",
                "Regular health checkups every 6-12 months",
                "Monitor blood pressure and cholesterol levels"
            ]
        elif risk_level == "Medium":
            recommendations = [
                "Consult a cardiologist within 2-4 weeks",
                "Increase physical activity to 150 minutes per week",
                "Reduce salt intake and avoid processed foods",
                "Monitor blood pressure weekly",
                "Consider stress management techniques like yoga or meditation",
                "Quit smoking and limit alcohol consumption"
            ]
        else:  # High risk
            recommendations = [
                "⚠️ URGENT: Consult a cardiologist immediately",
                "Schedule comprehensive cardiac evaluation",
                "Strictly follow prescribed medications",
                "Daily blood pressure monitoring",
                "Adopt heart-healthy diet (DASH diet recommended)",
                "Avoid strenuous activities until cleared by doctor",
                "Quit smoking immediately",
                "Manage stress through professional guidance"
            ]
        
        return recommendations
    
    def predict_batch(self, input_list):
        """
        Make predictions for multiple inputs
        
        Args:
            input_list: List of input features
            
        Returns:
            list: List of prediction results
        """
        results = []
        for input_data in input_list:
            result = self.predict(input_data)
            results.append(result)
        return results


def example_prediction():
    """Example usage of predictor"""
    predictor = HeartDiseasePredictor()
    
    # Example input (13 standard features)
    sample_input = {
        "age": 55,
        "sex": 1,  # male
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
    
    result = predictor.predict(sample_input)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print("\n" + "="*50)
    print("PREDICTION RESULT")
    print("="*50)
    print(f"Risk Level: {result['risk_level']}")
    print(f"Probability: {result['probability']:.2%}")
    print(f"Confidence: {result['confidence']:.2%}")
    print("\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec}")
    print("="*50)


if __name__ == "__main__":
    example_prediction()
