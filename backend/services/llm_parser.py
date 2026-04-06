"""
LLM-Based Medical Report Parser
Extracts structured medical data from OCR text using OpenAI
"""

import json
import logging
from typing import Dict, Optional
import re

logger = logging.getLogger(__name__)


class LLMReportParser:
    """Parse medical reports using LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM parser
        
        Args:
            api_key: OpenAI API key (optional, uses env var if not provided)
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.available = True
        except ImportError:
            logger.warning("OpenAI not installed - using fallback parser")
            self.available = False
    
    def parse_blood_report(self, ocr_text: str) -> Dict:
        """
        Parse blood report using LLM
        
        Args:
            ocr_text: Raw OCR text from report
            
        Returns:
            Structured medical data
        """
        if not self.available:
            return self._parse_fallback(ocr_text)
        
        try:
            prompt = f"""
Extract all medical values from this blood test report into JSON format.
Return ONLY valid JSON with these keys (if available):
- hemoglobin (g/dL)
- cholesterol (mg/dL)
- ldl (mg/dL)
- hdl (mg/dL)
- triglycerides (mg/dL)
- glucose (mg/dL)
- blood_pressure (mmHg, format: "systolic/diastolic")
- creatinine (mg/dL)
- heart_rate (bpm)
- sodium (mEq/L)
- potassium (mEq/L)
- calcium (mg/dL)
- magnesium (mg/dL)
- phosphorus (mg/dL)
- albumin (g/dL)
- total_protein (g/dL)
- ast (U/L)
- alt (U/L)
- bilirubin (mg/dL)
- alkaline_phosphatase (U/L)

Report text:
{ocr_text}

Return ONLY JSON, no other text.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            data = self._extract_json(result_text)
            
            if data:
                return data
            else:
                logger.warning("LLM returned invalid JSON, using fallback")
                return self._parse_fallback(ocr_text)
        
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return self._parse_fallback(ocr_text)
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from text"""
        try:
            # Try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    return None
            return None
    
    def _parse_fallback(self, ocr_text: str) -> Dict:
        """Fallback regex-based parsing"""
        data = {}
        
        # Define patterns for common medical values
        patterns = {
            "hemoglobin": r"hemoglobin[:\s]+(\d+\.?\d*)",
            "cholesterol": r"(?:total\s+)?cholesterol[:\s]+(\d+\.?\d*)",
            "ldl": r"ldl[:\s]+(\d+\.?\d*)",
            "hdl": r"hdl[:\s]+(\d+\.?\d*)",
            "triglycerides": r"triglycerides[:\s]+(\d+\.?\d*)",
            "glucose": r"(?:blood\s+)?glucose[:\s]+(\d+\.?\d*)",
            "blood_pressure": r"(?:bp|blood\s+pressure)[:\s]+(\d+)\s*[/\\]\s*(\d+)",
            "creatinine": r"creatinine[:\s]+(\d+\.?\d*)",
            "heart_rate": r"(?:heart\s+rate|hr|pulse)[:\s]+(\d+\.?\d*)",
            "sodium": r"sodium[:\s]+(\d+\.?\d*)",
            "potassium": r"potassium[:\s]+(\d+\.?\d*)",
            "calcium": r"calcium[:\s]+(\d+\.?\d*)",
            "magnesium": r"magnesium[:\s]+(\d+\.?\d*)",
            "phosphorus": r"phosphorus[:\s]+(\d+\.?\d*)",
            "albumin": r"albumin[:\s]+(\d+\.?\d*)",
            "total_protein": r"total\s+protein[:\s]+(\d+\.?\d*)",
            "ast": r"ast[:\s]+(\d+\.?\d*)",
            "alt": r"alt[:\s]+(\d+\.?\d*)",
            "bilirubin": r"bilirubin[:\s]+(\d+\.?\d*)",
            "alkaline_phosphatase": r"alkaline\s+phosphatase[:\s]+(\d+\.?\d*)"
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                if key == "blood_pressure":
                    data[key] = f"{match.group(1)}/{match.group(2)}"
                else:
                    try:
                        data[key] = float(match.group(1))
                    except (ValueError, IndexError):
                        pass
        
        return data
    
    def parse_ecg_report(self, ocr_text: str) -> Dict:
        """
        Parse ECG report
        
        Args:
            ocr_text: Raw OCR text from ECG report
            
        Returns:
            ECG findings
        """
        if not self.available:
            return self._parse_ecg_fallback(ocr_text)
        
        try:
            prompt = f"""
Extract ECG findings from this report into JSON format.
Return ONLY valid JSON with these keys (if available):
- heart_rate (bpm)
- rhythm (e.g., "normal sinus rhythm", "atrial fibrillation")
- pr_interval (ms)
- qrs_duration (ms)
- qt_interval (ms)
- st_segment (e.g., "normal", "elevated", "depressed")
- t_wave (e.g., "normal", "inverted", "flattened")
- abnormalities (list of findings)
- interpretation (overall interpretation)

Report text:
{ocr_text}

Return ONLY JSON, no other text.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            data = self._extract_json(result_text)
            
            return data if data else self._parse_ecg_fallback(ocr_text)
        
        except Exception as e:
            logger.error(f"ECG parsing failed: {e}")
            return self._parse_ecg_fallback(ocr_text)
    
    def _parse_ecg_fallback(self, ocr_text: str) -> Dict:
        """Fallback ECG parsing"""
        data = {}
        
        # Extract heart rate
        hr_match = re.search(r"heart\s+rate[:\s]+(\d+)", ocr_text, re.IGNORECASE)
        if hr_match:
            data["heart_rate"] = int(hr_match.group(1))
        
        # Extract rhythm
        if "normal sinus rhythm" in ocr_text.lower():
            data["rhythm"] = "normal sinus rhythm"
        elif "atrial fibrillation" in ocr_text.lower():
            data["rhythm"] = "atrial fibrillation"
        elif "sinus tachycardia" in ocr_text.lower():
            data["rhythm"] = "sinus tachycardia"
        elif "sinus bradycardia" in ocr_text.lower():
            data["rhythm"] = "sinus bradycardia"
        
        # Extract abnormalities
        abnormalities = []
        if "st elevation" in ocr_text.lower():
            abnormalities.append("ST elevation")
        if "st depression" in ocr_text.lower():
            abnormalities.append("ST depression")
        if "t wave inversion" in ocr_text.lower():
            abnormalities.append("T wave inversion")
        if "left ventricular hypertrophy" in ocr_text.lower():
            abnormalities.append("Left ventricular hypertrophy")
        
        if abnormalities:
            data["abnormalities"] = abnormalities
        
        return data
    
    def parse_imaging_report(self, ocr_text: str, imaging_type: str = "xray") -> Dict:
        """
        Parse imaging report (X-ray, CT, etc.)
        
        Args:
            ocr_text: Raw OCR text from imaging report
            imaging_type: Type of imaging (xray, ct, mri, ultrasound)
            
        Returns:
            Imaging findings
        """
        if not self.available:
            return self._parse_imaging_fallback(ocr_text, imaging_type)
        
        try:
            prompt = f"""
Extract findings from this {imaging_type.upper()} report into JSON format.
Return ONLY valid JSON with these keys (if available):
- findings (list of findings)
- abnormalities (list of abnormalities)
- impression (overall impression)
- recommendation (recommended follow-up)
- severity (e.g., "mild", "moderate", "severe")

Report text:
{ocr_text}

Return ONLY JSON, no other text.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            data = self._extract_json(result_text)
            
            return data if data else self._parse_imaging_fallback(ocr_text, imaging_type)
        
        except Exception as e:
            logger.error(f"Imaging parsing failed: {e}")
            return self._parse_imaging_fallback(ocr_text, imaging_type)
    
    def _parse_imaging_fallback(self, ocr_text: str, imaging_type: str) -> Dict:
        """Fallback imaging parsing"""
        data = {}
        
        # Extract findings
        findings = []
        if "cardiomegaly" in ocr_text.lower():
            findings.append("Cardiomegaly")
        if "pulmonary edema" in ocr_text.lower():
            findings.append("Pulmonary edema")
        if "pleural effusion" in ocr_text.lower():
            findings.append("Pleural effusion")
        if "pneumonia" in ocr_text.lower():
            findings.append("Pneumonia")
        
        if findings:
            data["findings"] = findings
        
        # Extract severity
        if "severe" in ocr_text.lower():
            data["severity"] = "severe"
        elif "moderate" in ocr_text.lower():
            data["severity"] = "moderate"
        elif "mild" in ocr_text.lower():
            data["severity"] = "mild"
        
        return data


# Example usage
if __name__ == "__main__":
    parser = LLMReportParser()
    
    # Example blood report text
    sample_text = """
    Blood Test Results
    Hemoglobin: 13.2 g/dL
    Cholesterol: 240 mg/dL
    LDL: 160 mg/dL
    HDL: 35 mg/dL
    Triglycerides: 200 mg/dL
    Glucose: 130 mg/dL
    Blood Pressure: 140/90 mmHg
    """
    
    result = parser.parse_blood_report(sample_text)
    print("Parsed Blood Report:")
    print(json.dumps(result, indent=2))
