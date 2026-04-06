"""
Advanced OCR Service for Medical Reports
Supports: EasyOCR, PaddleOCR, Google Vision API
"""

import easyocr
import cv2
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class AdvancedOCRService:
    """Advanced OCR service for medical reports"""
    
    def __init__(self, method: str = "easyocr"):
        """
        Initialize OCR service
        
        Args:
            method: "easyocr", "paddleocr", or "google"
        """
        self.method = method
        
        if method == "easyocr":
            self.reader = easyocr.Reader(['en'], gpu=True)
        elif method == "paddleocr":
            try:
                from paddleocr import PaddleOCR
                self.reader = PaddleOCR(use_angle_cls=True, lang='en')
            except ImportError:
                logger.warning("PaddleOCR not installed, falling back to EasyOCR")
                self.reader = easyocr.Reader(['en'], gpu=True)
                self.method = "easyocr"
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from medical report image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        # Preprocess image
        image = self._preprocess_image(image_path)
        
        # Extract text based on method
        if self.method == "easyocr":
            text = self._extract_easyocr(image)
        elif self.method == "paddleocr":
            text = self._extract_paddleocr(image_path)
        else:
            text = self._extract_google_vision(image_path)
        
        return text
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR"""
        # Read image
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        
        # Threshold
        _, binary = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)
        
        return binary
    
    def _extract_easyocr(self, image: np.ndarray) -> str:
        """Extract text using EasyOCR"""
        result = self.reader.readtext(image)
        text = "\n".join([res[1] for res in result])
        return text
    
    def _extract_paddleocr(self, image_path: str) -> str:
        """Extract text using PaddleOCR"""
        result = self.reader.ocr(image_path, cls=True)
        text = "\n".join([line[0][1] for line in result])
        return text
    
    def _extract_google_vision(self, image_path: str) -> str:
        """Extract text using Google Vision API"""
        try:
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = client.document_text_detection(image=image)
            
            return response.full_text_annotation.text
        except ImportError:
            logger.warning("Google Vision not available, using EasyOCR")
            return self._extract_easyocr(cv2.imread(image_path))
    
    def extract_structured_data(self, text: str) -> Dict:
        """
        Extract structured medical data from OCR text
        
        Args:
            text: Raw OCR text
            
        Returns:
            Structured medical data
        """
        data = {}
        
        # Extract common medical parameters
        patterns = {
            "hemoglobin": r"hemoglobin[:\s]+(\d+\.?\d*)",
            "cholesterol": r"cholesterol[:\s]+(\d+\.?\d*)",
            "blood_pressure": r"(?:bp|blood\s+pressure)[:\s]+(\d+)\s*[/\\]\s*(\d+)",
            "glucose": r"glucose[:\s]+(\d+\.?\d*)",
            "ldl": r"ldl[:\s]+(\d+\.?\d*)",
            "hdl": r"hdl[:\s]+(\d+\.?\d*)",
            "triglycerides": r"triglycerides[:\s]+(\d+\.?\d*)",
            "creatinine": r"creatinine[:\s]+(\d+\.?\d*)",
            "heart_rate": r"(?:heart\s+rate|hr|pulse)[:\s]+(\d+\.?\d*)"
        }
        
        import re
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if key == "blood_pressure":
                    data[key] = f"{match.group(1)}/{match.group(2)}"
                else:
                    data[key] = float(match.group(1))
        
        return data
    
    def extract_with_llm(self, text: str) -> Dict:
        """
        Extract structured data using LLM
        
        Args:
            text: Raw OCR text
            
        Returns:
            Structured medical data
        """
        try:
            from openai import OpenAI
            
            client = OpenAI()
            
            prompt = f"""
            Extract all medical values from this medical report into JSON format.
            Return ONLY valid JSON with keys like:
            hemoglobin, cholesterol, blood_pressure, glucose, ldl, hdl, 
            triglycerides, creatinine, heart_rate, etc.
            
            Report text:
            {text}
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self.extract_structured_data(text)


class ReportAnalyzer:
    """Analyze medical reports"""
    
    def __init__(self):
        self.ocr_service = AdvancedOCRService(method="easyocr")
    
    def analyze_report(self, image_path: str, use_llm: bool = True) -> Dict:
        """
        Analyze medical report
        
        Args:
            image_path: Path to report image
            use_llm: Use LLM for parsing
            
        Returns:
            Analyzed report data
        """
        # Extract text
        text = self.ocr_service.extract_text(image_path)
        
        # Extract structured data
        if use_llm:
            data = self.ocr_service.extract_with_llm(text)
        else:
            data = self.ocr_service.extract_structured_data(text)
        
        return {
            "raw_text": text,
            "structured_data": data,
            "confidence": self._calculate_confidence(data)
        }
    
    def _calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score for extracted data"""
        # More fields extracted = higher confidence
        total_fields = 9  # Total possible fields
        extracted_fields = len(data)
        
        return min(1.0, extracted_fields / total_fields)


# Example usage
if __name__ == "__main__":
    analyzer = ReportAnalyzer()
    
    # Analyze report
    result = analyzer.analyze_report("sample_report.jpg", use_llm=True)
    
    print("Raw Text:")
    print(result["raw_text"][:200])
    print("\nStructured Data:")
    print(json.dumps(result["structured_data"], indent=2))
    print(f"\nConfidence: {result['confidence']:.2%}")
