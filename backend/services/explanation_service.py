"""
AI Explanation Service
Converts medical jargon into simple language for Indian users
Uses OpenAI API for natural language generation
"""
import openai
import os
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalExplanationService:
    """Generate simple explanations for medical predictions"""
    
    def __init__(self, api_key=None):
        """
        Initialize explanation service
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("OpenAI API key not provided")
    
    def explain_risk_prediction(self, prediction_data, user_data, language="english"):
        """
        Generate simple explanation for risk prediction
        
        Args:
            prediction_data: Model prediction results
            user_data: User's input data
            language: Output language (english, hindi)
            
        Returns:
            str: Simple explanation
        """
        if not self.api_key:
            return self._generate_template_explanation(prediction_data, user_data)
        
        try:
            prompt = self._create_explanation_prompt(
                prediction_data, user_data, language
            )
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant explaining heart health to Indian patients in simple language."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            explanation = response.choices[0].message.content
            logger.info("Generated AI explanation")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._generate_template_explanation(prediction_data, user_data)
    
    def _create_explanation_prompt(self, prediction_data, user_data, language):
        """Create prompt for OpenAI"""
        risk_level = prediction_data.get("risk_level", "Unknown")
        probability = prediction_data.get("probability", 0)
        
        prompt = f"""
        Explain the following heart disease risk assessment to an Indian patient in simple {language}:
        
        Risk Level: {risk_level}
        Probability: {probability:.1%}
        
        Patient Data:
        - Age: {user_data.get('age', 'N/A')}
        - Blood Pressure: {user_data.get('resting_bp', 'N/A')} mm Hg
        - Cholesterol: {user_data.get('cholesterol', 'N/A')} mg/dl
        - Smoking: {'Yes' if user_data.get('smoking', 0) else 'No'}
        
        Provide:
        1. What this risk level means
        2. Key factors contributing to this risk
        3. Simple lifestyle recommendations for Indian context
        4. When to see a doctor
        
        Keep it simple, empathetic, and culturally appropriate for India.
        """
        
        return prompt
    
    def _generate_template_explanation(self, prediction_data, user_data):
        """Generate explanation without AI (fallback)"""
        risk_level = prediction_data.get("risk_level", "Unknown")
        probability = prediction_data.get("probability", 0)
        
        explanations = {
            "High": f"""
🚨 High Risk Alert ({probability:.1%} probability)

Your heart disease risk is HIGH. This means you have several risk factors that need immediate attention.

Key Concerns:
{self._identify_risk_factors(user_data)}

What You Should Do:
• Consult a cardiologist within 24-48 hours
• Get a complete cardiac evaluation
• Start prescribed medications immediately
• Avoid strenuous activities until cleared by doctor

Lifestyle Changes:
• Stop smoking and tobacco immediately
• Reduce oil and salt in food
• Walk 30 minutes daily (after doctor approval)
• Manage stress through yoga or meditation
• Avoid fried and processed foods

⚠️ If you experience chest pain, shortness of breath, or dizziness, visit emergency immediately.
            """,
            
            "Medium": f"""
⚠️ Moderate Risk ({probability:.1%} probability)

Your heart disease risk is MODERATE. You have some risk factors that need attention.

Key Concerns:
{self._identify_risk_factors(user_data)}

What You Should Do:
• Schedule a cardiology consultation within 2 weeks
• Get regular health checkups
• Monitor blood pressure weekly
• Follow prescribed medications

Lifestyle Changes:
• Reduce oil consumption (use heart-healthy oils)
• Limit salt intake (less than 5g per day)
• Exercise 150 minutes per week
• Quit smoking and limit alcohol
• Include more fruits and vegetables in diet
• Manage stress through relaxation techniques

Regular monitoring and lifestyle changes can significantly reduce your risk.
            """,
            
            "Low": f"""
✅ Low Risk ({probability:.1%} probability)

Good news! Your heart disease risk is LOW. Keep up the healthy lifestyle!

Current Status:
{self._identify_positive_factors(user_data)}

Maintain Your Health:
• Continue regular exercise (30 minutes daily)
• Eat balanced diet with less oil and salt
• Annual health checkups
• Monitor blood pressure monthly
• Maintain healthy weight
• Manage stress effectively

Prevention Tips:
• Avoid smoking and tobacco
• Limit alcohol consumption
• Stay physically active
• Get adequate sleep (7-8 hours)
• Include whole grains, fruits, and vegetables in diet

Keep up the good work! Regular checkups help catch any issues early.
            """
        }
        
        return explanations.get(risk_level, "Unable to generate explanation")
    
    def _identify_risk_factors(self, user_data):
        """Identify and explain risk factors"""
        factors = []
        
        age = user_data.get('age', 0)
        if age > 55:
            factors.append(f"• Age ({age} years) - Higher risk as age increases")
        
        bp = user_data.get('resting_bp', 0)
        if bp > 140:
            factors.append(f"• High blood pressure ({bp} mm Hg) - Strains your heart")
        
        cholesterol = user_data.get('cholesterol', 0)
        if cholesterol > 240:
            factors.append(f"• High cholesterol ({cholesterol} mg/dl) - Blocks arteries")
        
        if user_data.get('smoking', 0):
            factors.append("• Smoking - Damages blood vessels and heart")
        
        if user_data.get('diabetes', 0):
            factors.append("• Diabetes - Increases heart disease risk")
        
        if not factors:
            factors.append("• Multiple factors detected - Detailed evaluation needed")
        
        return "\n".join(factors)
    
    def _identify_positive_factors(self, user_data):
        """Identify positive health factors"""
        factors = []
        
        bp = user_data.get('resting_bp', 0)
        if bp <= 120:
            factors.append(f"• Normal blood pressure ({bp} mm Hg)")
        
        cholesterol = user_data.get('cholesterol', 0)
        if cholesterol <= 200:
            factors.append(f"• Healthy cholesterol ({cholesterol} mg/dl)")
        
        if not user_data.get('smoking', 0):
            factors.append("• Non-smoker")
        
        if not user_data.get('diabetes', 0):
            factors.append("• No diabetes")
        
        return "\n".join(factors) if factors else "• Overall healthy parameters"
    
    def explain_blood_report(self, blood_data):
        """
        Explain blood report values in simple terms
        
        Args:
            blood_data: Extracted blood report data
            
        Returns:
            dict: Explanations for each parameter
        """
        explanations = {}
        
        # Total Cholesterol
        cholesterol = blood_data.get('cholesterol_total')
        if cholesterol:
            if cholesterol < 200:
                explanations['cholesterol'] = f"✅ Your total cholesterol ({cholesterol} mg/dl) is healthy. Keep it up!"
            elif cholesterol < 240:
                explanations['cholesterol'] = f"⚠️ Your cholesterol ({cholesterol} mg/dl) is borderline high. Reduce oily foods."
            else:
                explanations['cholesterol'] = f"🚨 Your cholesterol ({cholesterol} mg/dl) is high. Consult a doctor and change diet."
        
        # LDL (Bad Cholesterol)
        ldl = blood_data.get('ldl')
        if ldl:
            if ldl < 100:
                explanations['ldl'] = f"✅ Your LDL ({ldl} mg/dl) is optimal."
            elif ldl < 160:
                explanations['ldl'] = f"⚠️ Your LDL ({ldl} mg/dl) is high. This is 'bad' cholesterol that blocks arteries."
            else:
                explanations['ldl'] = f"🚨 Your LDL ({ldl} mg/dl) is very high. Immediate action needed."
        
        # HDL (Good Cholesterol)
        hdl = blood_data.get('hdl')
        if hdl:
            if hdl >= 60:
                explanations['hdl'] = f"✅ Your HDL ({hdl} mg/dl) is good. This 'good' cholesterol protects your heart."
            elif hdl >= 40:
                explanations['hdl'] = f"⚠️ Your HDL ({hdl} mg/dl) is acceptable but could be better."
            else:
                explanations['hdl'] = f"🚨 Your HDL ({hdl} mg/dl) is low. Increase exercise and healthy fats."
        
        # Triglycerides
        trig = blood_data.get('triglycerides')
        if trig:
            if trig < 150:
                explanations['triglycerides'] = f"✅ Your triglycerides ({trig} mg/dl) are normal."
            elif trig < 200:
                explanations['triglycerides'] = f"⚠️ Your triglycerides ({trig} mg/dl) are borderline high."
            else:
                explanations['triglycerides'] = f"🚨 Your triglycerides ({trig} mg/dl) are high. Reduce sugar and refined carbs."
        
        # Blood Sugar
        sugar = blood_data.get('blood_sugar_fasting')
        if sugar:
            if sugar < 100:
                explanations['blood_sugar'] = f"✅ Your fasting blood sugar ({sugar} mg/dl) is normal."
            elif sugar < 126:
                explanations['blood_sugar'] = f"⚠️ Your blood sugar ({sugar} mg/dl) is pre-diabetic. Control sugar intake."
            else:
                explanations['blood_sugar'] = f"🚨 Your blood sugar ({sugar} mg/dl) indicates diabetes. See a doctor."
        
        return explanations


# Example usage
if __name__ == "__main__":
    service = MedicalExplanationService()
    
    # Test explanation
    prediction = {"risk_level": "High", "probability": 0.75}
    user = {"age": 58, "resting_bp": 150, "cholesterol": 260, "smoking": 1}
    
    explanation = service.explain_risk_prediction(prediction, user)
    print(explanation)
