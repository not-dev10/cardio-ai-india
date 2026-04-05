"""
Advanced OCR Service with Format-Specific Parsers
Handles major Indian lab formats: SRL, Thyrocare, Metropolis, Dr. Lal PathLabs, local labs
"""
import re
import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Dict, Optional, List, Tuple
from fuzzywuzzy import fuzz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabFormatDetector:
    """Detect which lab format the report belongs to"""
    
    LAB_SIGNATURES = {
        'srl': ['srl diagnostics', 'srl limited', 'www.srldiagnostics.in'],
        'thyrocare': ['thyrocare', 'aarogyam', 'www.thyrocare.com'],
        'metropolis': ['metropolis healthcare', 'www.metropolisindia.com'],
        'dr_lal': ['dr lal pathlabs', 'dr. lal', 'lalpathlabs.com'],
        'apollo': ['apollo diagnostics', 'apollo hospitals'],
        'local': []  # Fallback for unrecognized formats
    }
    
    def detect_lab_format(self, text: str) -> str:
        """
        Detect lab format from OCR text
        
        Args:
            text: OCR extracted text
            
        Returns:
            str: Lab format identifier
        """
        text_lower = text.lower()
        
        for lab, signatures in self.LAB_SIGNATURES.items():
            for signature in signatures:
                if signature in text_lower:
                    logger.info(f"Detected lab format: {lab}")
                    return lab
        
        logger.info("Lab format not recognized, using generic parser")
        return 'local'


class AdvancedMedicalOCR:
    """Advanced OCR with format-specific parsers"""
    
    def __init__(self):
        self.format_detector = LabFormatDetector()
        
        # Parameter name variations (for fuzzy matching)
        self.parameter_aliases = {
            'cholesterol_total': [
                'total cholesterol', 'cholesterol total', 'cholesterol', 
                'serum cholesterol', 'chol total', 't.cholesterol'
            ],
            'ldl': [
                'ldl cholesterol', 'ldl-cholesterol', 'ldl-c', 'ldl chol',
                'low density lipoprotein', 'ldl direct', 'ldl-direct'
            ],
            'hdl': [
                'hdl cholesterol', 'hdl-cholesterol', 'hdl-c', 'hdl chol',
                'high density lipoprotein', 'hdl direct', 'hdl-direct'
            ],
            'triglycerides': [
                'triglycerides', 'triglyceride', 'trig', 'tg', 'serum triglycerides'
            ],
            'blood_sugar_fasting': [
                'fasting blood sugar', 'fbs', 'fasting glucose', 'glucose fasting',
                'blood glucose fasting', 'fasting blood glucose', 'fbg'
            ],
            'blood_sugar_pp': [
                'pp blood sugar', 'ppbs', 'post prandial', 'pp glucose',
                'post prandial blood sugar', 'post prandial glucose', 'ppbg'
            ],
            'hba1c': [
                'hba1c', 'hb a1c', 'glycated hemoglobin', 'glycosylated hemoglobin',
                'hemoglobin a1c', 'a1c'
            ],
            'blood_pressure': [
                'blood pressure', 'bp', 'systolic', 'diastolic'
            ]
        }
    
    def fuzzy_match_parameter(self, text: str, threshold: int = 80) -> Optional[str]:
        """
        Fuzzy match parameter name
        
        Args:
            text: Text to match
            threshold: Matching threshold (0-100)
            
        Returns:
            str: Matched parameter name or None
        """
        text_lower = text.lower().strip()
        
        for param, aliases in self.parameter_aliases.items():
            for alias in aliases:
                score = fuzz.ratio(text_lower, alias)
                if score >= threshold:
                    logger.debug(f"Fuzzy matched '{text}' to '{param}' (score: {score})")
                    return param
        
        return None
    
    def extract_value_near_parameter(self, text: str, parameter_line: str) -> Optional[float]:
        """
        Extract numeric value near parameter name
        
        Args:
            text: Full OCR text
            parameter_line: Line containing parameter name
            
        Returns:
            float: Extracted value or None
        """
        # Look for numbers in the same line or next line
        lines = text.split('\n')
        
        try:
            param_idx = lines.index(parameter_line)
            search_lines = lines[param_idx:param_idx+3]  # Current + next 2 lines
        except ValueError:
            search_lines = [parameter_line]
        
        # Extract all numbers from search area
        numbers = []
        for line in search_lines:
            # Match decimal numbers
            matches = re.findall(r'\d+\.?\d*', line)
            numbers.extend([float(m) for m in matches])
        
        # Return first reasonable value (filter out dates, IDs, etc.)
        for num in numbers:
            if 10 <= num <= 1000:  # Reasonable range for most blood parameters
                return num
        
        return None
    
    def parse_srl_format(self, text: str) -> Dict:
        """
        Parse SRL Diagnostics format
        
        SRL typically has:
        - Parameter name in left column
        - Value in middle column
        - Reference range in right column
        """
        data = {}
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            # Try to match parameter
            param = self.fuzzy_match_parameter(line)
            if param:
                # Extract value from same or next line
                value = self.extract_value_near_parameter(text, line)
                if value:
                    data[param] = value
                    logger.info(f"SRL: Extracted {param} = {value}")
        
        return data
    
    def parse_thyrocare_format(self, text: str) -> Dict:
        """
        Parse Thyrocare format
        
        Thyrocare typically has:
        - Test name followed by value on same line
        - Format: "TEST NAME    VALUE    UNIT    RANGE"
        """
        data = {}
        lines = text.split('\n')
        
        for line in lines:
            # Try to match parameter
            param = self.fuzzy_match_parameter(line)
            if param:
                # Thyrocare usually has value immediately after parameter
                # Extract first number after parameter name
                parts = line.split()
                for part in parts:
                    try:
                        value = float(part)
                        if 10 <= value <= 1000:
                            data[param] = value
                            logger.info(f"Thyrocare: Extracted {param} = {value}")
                            break
                    except ValueError:
                        continue
        
        return data
    
    def parse_metropolis_format(self, text: str) -> Dict:
        """
        Parse Metropolis Healthcare format
        
        Similar to SRL but with different layout
        """
        # Metropolis format is similar to SRL
        return self.parse_srl_format(text)
    
    def parse_dr_lal_format(self, text: str) -> Dict:
        """
        Parse Dr. Lal PathLabs format
        """
        # Dr. Lal format is similar to SRL
        return self.parse_srl_format(text)
    
    def parse_generic_format(self, text: str) -> Dict:
        """
        Generic parser for unknown formats
        Uses aggressive pattern matching and fuzzy search
        """
        data = {}
        
        # Try all parameter aliases with regex
        for param, aliases in self.parameter_aliases.items():
            for alias in aliases:
                # Create flexible pattern
                pattern = alias.replace(' ', r'\s*')
                pattern = rf'{pattern}\s*[:\-]?\s*(\d+\.?\d*)'
                
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        if 10 <= value <= 1000:
                            data[param] = value
                            logger.info(f"Generic: Extracted {param} = {value}")
                            break
                    except (ValueError, IndexError):
                        continue
                
                if param in data:
                    break
        
        return data
    
    def process_report_with_format_detection(self, image_path: str) -> Dict:
        """
        Complete pipeline with format detection
        
        Args:
            image_path: Path to report image
            
        Returns:
            dict: Extracted data with metadata
        """
        logger.info(f"Processing report: {image_path}")
        
        # Load and preprocess image
        image = Image.open(image_path)
        processed = self.preprocess_image(image)
        
        # OCR
        text = pytesseract.image_to_string(processed, lang='eng')
        logger.info(f"Extracted {len(text)} characters")
        
        # Detect lab format
        lab_format = self.format_detector.detect_lab_format(text)
        
        # Parse based on format
        parsers = {
            'srl': self.parse_srl_format,
            'thyrocare': self.parse_thyrocare_format,
            'metropolis': self.parse_metropolis_format,
            'dr_lal': self.parse_dr_lal_format,
            'local': self.parse_generic_format
        }
        
        parser = parsers.get(lab_format, self.parse_generic_format)
        extracted_data = parser(text)
        
        # If format-specific parser failed, try generic
        if not extracted_data and lab_format != 'local':
            logger.warning(f"{lab_format} parser failed, trying generic parser")
            extracted_data = self.parse_generic_format(text)
        
        return {
            'lab_format': lab_format,
            'extracted_data': extracted_data,
            'raw_text': text,
            'confidence': self.calculate_extraction_confidence(extracted_data)
        }
    
    def preprocess_image(self, image):
        """Enhanced image preprocessing"""
        if isinstance(image, Image.Image):
            image = np.array(image)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Adaptive thresholding (better for varying lighting)
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Deskew if needed
        binary = self.deskew_image(binary)
        
        return binary
    
    def deskew_image(self, image):
        """Deskew image if it's tilted"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
        
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only deskew if angle is significant
        if abs(angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated
        
        return image
    
    def calculate_extraction_confidence(self, data: Dict) -> float:
        """
        Calculate confidence score for extraction
        
        Args:
            data: Extracted data
            
        Returns:
            float: Confidence score (0-1)
        """
        # Key parameters for cardiac health
        key_params = ['cholesterol_total', 'ldl', 'hdl', 'triglycerides']
        
        extracted_key_params = sum(1 for p in key_params if p in data and data[p])
        total_params = len(data)
        
        if total_params == 0:
            return 0.0
        
        # Confidence based on:
        # 1. Number of key parameters extracted (60% weight)
        # 2. Total parameters extracted (40% weight)
        key_confidence = extracted_key_params / len(key_params)
        total_confidence = min(total_params / 7, 1.0)  # 7 is ideal number
        
        confidence = 0.6 * key_confidence + 0.4 * total_confidence
        
        return round(confidence, 2)
    
    def manual_correction_interface(self, extracted_data: Dict) -> Dict:
        """
        Placeholder for manual correction UI
        In production, this would be an Android UI where users can correct values
        
        Args:
            extracted_data: Auto-extracted data
            
        Returns:
            dict: Corrected data
        """
        # This would be implemented in the Android app
        # Users see extracted values and can correct them
        return extracted_data


# Example usage
if __name__ == "__main__":
    ocr = AdvancedMedicalOCR()
    
    print("Advanced OCR Service with Format-Specific Parsers")
    print("\nSupported formats:")
    print("- SRL Diagnostics")
    print("- Thyrocare")
    print("- Metropolis Healthcare")
    print("- Dr. Lal PathLabs")
    print("- Apollo Diagnostics")
    print("- Generic/Local labs (fallback)")
    print("\nFeatures:")
    print("- Fuzzy parameter matching")
    print("- Format auto-detection")
    print("- Multiple extraction strategies")
    print("- Confidence scoring")
    print("- Manual correction support")
