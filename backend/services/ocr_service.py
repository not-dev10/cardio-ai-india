"""
OCR Service for extracting medical data from reports
Supports: Blood reports, ECG reports, Angiography reports
"""
import re
import pytesseract
from PIL import Image
import pdf2image
import cv2
import numpy as np
from typing import Dict, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalReportOCR:
    """Extract structured medical data from images and PDFs"""
    
    def __init__(self, use_google_vision=False):
        """
        Initialize OCR service
        
        Args:
            use_google_vision: Use Google Cloud Vision API (requires credentials)
        """
        self.use_google_vision = use_google_vision
        
        # Configure Tesseract (adjust path for Windows if needed)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
    def preprocess_image(self, image):
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            numpy array: Preprocessed image
        """
        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def extract_text_from_image(self, image_path):
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
            
        Returns:
            str: Extracted text
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Preprocess
            processed = self.preprocess_image(image)
            
            # OCR
            if self.use_google_vision:
                text = self._google_vision_ocr(image_path)
            else:
                text = pytesseract.image_to_string(processed, lang='eng')
            
            logger.info(f"Extracted {len(text)} characters from image")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            str: Extracted text from all pages
        """
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            
            all_text = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{len(images)}")
                
                # Preprocess and OCR
                processed = self.preprocess_image(image)
                text = pytesseract.image_to_string(processed, lang='eng')
                all_text.append(text)
            
            combined_text = "\n\n".join(all_text)
            logger.info(f"Extracted {len(combined_text)} characters from PDF")
            return combined_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def _google_vision_ocr(self, image_path):
        """
        Use Google Cloud Vision API for OCR
        
        Args:
            image_path: Path to image
            
        Returns:
            str: Extracted text
        """
        try:
            from google.cloud import vision
            
            client = vision.ImageAnnotatorClient()
            
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                return texts[0].description
            return ""
            
        except Exception as e:
            logger.error(f"Google Vision API error: {e}")
            return ""
    
    def extract_blood_report_data(self, text):
        """
        Extract structured data from blood report text
        
        Args:
            text: OCR extracted text
            
        Returns:
            dict: Structured blood report data
        """
        data = {
            "cholesterol_total": None,
            "ldl": None,
            "hdl": None,
            "triglycerides": None,
            "blood_sugar_fasting": None,
            "blood_sugar_pp": None,
            "hba1c": None,
        }
        
        # Patterns for extraction
        patterns = {
            "cholesterol_total": r"(?:total\s+)?cholesterol[:\s]+(\d+\.?\d*)",
            "ldl": r"ldl[:\s]+(\d+\.?\d*)",
            "hdl": r"hdl[:\s]+(\d+\.?\d*)",
            "triglycerides": r"triglycerides?[:\s]+(\d+\.?\d*)",
            "blood_sugar_fasting": r"(?:fasting\s+)?(?:blood\s+)?(?:glucose|sugar)[:\s]+(\d+\.?\d*)",
            "blood_sugar_pp": r"pp[:\s]+(\d+\.?\d*)",
            "hba1c": r"hba1c[:\s]+(\d+\.?\d*)",
        }
        
        # Extract values
        text_lower = text.lower()
        for key, pattern in patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                try:
                    data[key] = float(match.group(1))
                    logger.info(f"Extracted {key}: {data[key]}")
                except ValueError:
                    pass
        
        return data
    
    def extract_ecg_report_data(self, text):
        """
        Extract structured data from ECG report text
        
        Args:
            text: OCR extracted text
            
        Returns:
            dict: Structured ECG data
        """
        data = {
            "heart_rate": None,
            "pr_interval": None,
            "qrs_duration": None,
            "qt_interval": None,
            "interpretation": None,
        }
        
        patterns = {
            "heart_rate": r"(?:heart\s+rate|hr)[:\s]+(\d+)",
            "pr_interval": r"pr\s+interval[:\s]+(\d+)",
            "qrs_duration": r"qrs[:\s]+(\d+)",
            "qt_interval": r"qt[:\s]+(\d+)",
        }
        
        text_lower = text.lower()
        for key, pattern in patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                try:
                    data[key] = int(match.group(1))
                except ValueError:
                    pass
        
        # Extract interpretation
        interp_match = re.search(r"interpretation[:\s]+(.+?)(?:\n|$)", text_lower)
        if interp_match:
            data["interpretation"] = interp_match.group(1).strip()
        
        return data
    
    def process_medical_report(self, file_path, report_type="blood"):
        """
        Complete pipeline to process medical report
        
        Args:
            file_path: Path to report file (image or PDF)
            report_type: Type of report ('blood', 'ecg', 'angiography')
            
        Returns:
            dict: Extracted structured data
        """
        logger.info(f"Processing {report_type} report: {file_path}")
        
        # Extract text
        if file_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        else:
            text = self.extract_text_from_image(file_path)
        
        # Extract structured data based on report type
        if report_type == "blood":
            data = self.extract_blood_report_data(text)
        elif report_type == "ecg":
            data = self.extract_ecg_report_data(text)
        else:
            data = {"raw_text": text}
        
        data["raw_text"] = text
        data["report_type"] = report_type
        
        return data
    
    def validate_extracted_data(self, data):
        """
        Validate extracted medical data
        
        Args:
            data: Extracted data dictionary
            
        Returns:
            dict: Validation results
        """
        validation = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Blood report validation ranges
        if "cholesterol_total" in data and data["cholesterol_total"]:
            if data["cholesterol_total"] > 500:
                validation["warnings"].append("Total cholesterol seems unusually high")
            elif data["cholesterol_total"] < 50:
                validation["warnings"].append("Total cholesterol seems unusually low")
        
        if "ldl" in data and data["ldl"]:
            if data["ldl"] > 400:
                validation["warnings"].append("LDL seems unusually high")
        
        if "blood_sugar_fasting" in data and data["blood_sugar_fasting"]:
            if data["blood_sugar_fasting"] > 500:
                validation["warnings"].append("Blood sugar seems unusually high")
        
        # Check if any data was extracted
        extracted_values = [v for k, v in data.items() 
                          if k not in ["raw_text", "report_type"] and v is not None]
        
        if not extracted_values:
            validation["is_valid"] = False
            validation["errors"].append("No medical data could be extracted from the report")
        
        return validation


# Example usage
if __name__ == "__main__":
    ocr = MedicalReportOCR()
    
    # Test with sample report
    # result = ocr.process_medical_report("sample_blood_report.jpg", "blood")
    # print(result)
    
    print("OCR Service initialized successfully")
