"""
Image Processing Service for Cardiac Images
Supports: ECG, X-ray, Angiography
"""

import cv2
import numpy as np
from pathlib import Path
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ImageFeatures:
    """Container for extracted image features"""
    image_type: str
    abnormality_score: float
    confidence: float
    findings: Dict
    features: Dict
    quality_score: float


class CardiacImageProcessor:
    """Process cardiac images (ECG, X-ray, Angiography)"""
    
    def __init__(self):
        """Initialize image processor"""
        self.supported_types = ["ecg", "xray", "angiography"]
    
    def process_image(
        self,
        image_path: str,
        image_type: str = "ecg"
    ) -> ImageFeatures:
        """
        Process cardiac image
        
        Args:
            image_path: Path to image file
            image_type: Type of image (ecg, xray, angiography)
            
        Returns:
            ImageFeatures object with extracted features
        """
        if image_type not in self.supported_types:
            raise ValueError(f"Unsupported image type: {image_type}")
        
        # Read and preprocess image
        image = self._read_image(image_path)
        preprocessed = self._preprocess_image(image)
        
        # Extract features based on type
        if image_type == "ecg":
            features = self._process_ecg(preprocessed)
        elif image_type == "xray":
            features = self._process_xray(preprocessed)
        else:  # angiography
            features = self._process_angiography(preprocessed)
        
        return features
    
    def _read_image(self, image_path: str) -> np.ndarray:
        """Read image from file"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        return image
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for analysis"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
        
        return denoised
    
    def _process_ecg(self, image: np.ndarray) -> ImageFeatures:
        """
        Process ECG image
        
        Returns:
            ImageFeatures with ECG-specific analysis
        """
        # Detect edges (QRS complex)
        edges = cv2.Canny(image, 100, 200)
        
        # Find contours (peaks)
        contours, _ = cv2.findContours(
            edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Extract ECG features
        num_peaks = len(contours)
        peak_areas = [cv2.contourArea(c) for c in contours] if contours else [0]
        peak_variance = float(np.var(peak_areas)) if peak_areas else 0.0
        
        # Calculate signal quality
        signal_quality = float(np.mean(image) / 255.0)
        
        # Detect abnormalities based on peak patterns
        abnormality_score = self._detect_ecg_abnormalities(
            num_peaks, peak_variance, signal_quality
        )
        
        findings = {
            "num_peaks": int(num_peaks),
            "peak_variance": float(peak_variance),
            "signal_quality": float(signal_quality),
            "abnormality_detected": abnormality_score > 0.5,
            "possible_conditions": self._interpret_ecg_findings(
                num_peaks, peak_variance, abnormality_score
            )
        }
        
        return ImageFeatures(
            image_type="ecg",
            abnormality_score=abnormality_score,
            confidence=min(1.0, signal_quality),
            findings=findings,
            features={
                "num_peaks": num_peaks,
                "peak_variance": peak_variance,
                "signal_quality": signal_quality,
                "abnormality_score": abnormality_score
            },
            quality_score=signal_quality
        )
    
    def _process_xray(self, image: np.ndarray) -> ImageFeatures:
        """
        Process X-ray image
        
        Returns:
            ImageFeatures with X-ray analysis
        """
        # Histogram equalization for better contrast
        equalized = cv2.equalizeHist(image)
        
        # Detect regions of interest
        _, binary = cv2.threshold(equalized, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Analyze cardiac silhouette
        cardiac_area = sum([cv2.contourArea(c) for c in contours])
        total_area = image.shape[0] * image.shape[1]
        cardiac_ratio = cardiac_area / total_area if total_area > 0 else 0
        
        # Detect cardiomegaly (enlarged heart)
        cardiomegaly_score = self._detect_cardiomegaly(cardiac_ratio)
        
        # Detect pulmonary edema
        edema_score = self._detect_pulmonary_edema(equalized)
        
        # Overall abnormality score
        abnormality_score = max(cardiomegaly_score, edema_score)
        
        findings = {
            "cardiac_ratio": float(cardiac_ratio),
            "cardiomegaly": {
                "detected": cardiomegaly_score > 0.5,
                "score": float(cardiomegaly_score)
            },
            "pulmonary_edema": {
                "detected": edema_score > 0.5,
                "score": float(edema_score)
            },
            "image_quality": float(np.std(equalized) / 255.0)
        }
        
        return ImageFeatures(
            image_type="xray",
            abnormality_score=abnormality_score,
            confidence=min(1.0, np.std(equalized) / 255.0),
            findings=findings,
            features={
                "cardiac_ratio": cardiac_ratio,
                "cardiomegaly_score": cardiomegaly_score,
                "edema_score": edema_score,
                "abnormality_score": abnormality_score
            },
            quality_score=np.std(equalized) / 255.0
        )
    
    def _process_angiography(self, image: np.ndarray) -> ImageFeatures:
        """
        Process Angiography image
        
        Returns:
            ImageFeatures with angiography analysis
        """
        # Enhance vessel visibility
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        # Detect vessels using edge detection
        edges = cv2.Canny(enhanced, 50, 150)
        
        # Detect blockages (dark regions in vessels)
        _, binary = cv2.threshold(enhanced, 100, 255, cv2.THRESH_BINARY)
        
        # Find contours (vessels)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Analyze vessel patterns
        num_vessels = len(contours)
        vessel_areas = [cv2.contourArea(c) for c in contours] if contours else [0]
        
        # Detect blockages
        blockage_score = self._detect_vessel_blockage(enhanced, contours)
        
        # Determine affected vessel
        affected_vessel = self._determine_affected_vessel(contours, image.shape)
        
        findings = {
            "num_vessels_detected": int(num_vessels),
            "blockage_detected": blockage_score > 0.5,
            "blockage_severity": float(blockage_score),
            "affected_vessel": affected_vessel,
            "vessel_quality": float(np.mean(vessel_areas) / (image.shape[0] * image.shape[1])) if vessel_areas else 0.0
        }
        
        return ImageFeatures(
            image_type="angiography",
            abnormality_score=blockage_score,
            confidence=min(1.0, num_vessels / 10.0),
            findings=findings,
            features={
                "num_vessels": num_vessels,
                "blockage_score": blockage_score,
                "affected_vessel_index": ["LAD", "RCA", "LCx"].index(affected_vessel) if affected_vessel in ["LAD", "RCA", "LCx"] else 0,
                "abnormality_score": blockage_score
            },
            quality_score=min(1.0, num_vessels / 10.0)
        )
    
    def _detect_ecg_abnormalities(
        self,
        num_peaks: int,
        peak_variance: float,
        signal_quality: float
    ) -> float:
        """Detect ECG abnormalities"""
        # Abnormal if too few or too many peaks
        if num_peaks < 3 or num_peaks > 20:
            return 0.8
        
        # Abnormal if high variance in peak sizes
        if peak_variance > 1000:
            return 0.6
        
        # Abnormal if poor signal quality
        if signal_quality < 0.3:
            return 0.5
        
        return 0.2  # Normal
    
    def _interpret_ecg_findings(
        self,
        num_peaks: int,
        peak_variance: float,
        abnormality_score: float
    ) -> list:
        """Interpret ECG findings"""
        findings = []
        
        if num_peaks < 3:
            findings.append("Possible bradycardia or signal loss")
        elif num_peaks > 20:
            findings.append("Possible tachycardia or noise")
        
        if peak_variance > 1000:
            findings.append("Irregular peak patterns detected")
        
        if abnormality_score > 0.7:
            findings.append("Significant abnormalities detected - consult cardiologist")
        
        return findings if findings else ["Normal ECG pattern"]
    
    def _detect_cardiomegaly(self, cardiac_ratio: float) -> float:
        """Detect cardiomegaly (enlarged heart)"""
        # Normal cardiac ratio is < 0.5
        # Cardiomegaly if > 0.5
        if cardiac_ratio > 0.55:
            return min(1.0, (cardiac_ratio - 0.5) * 2)
        return 0.0
    
    def _detect_pulmonary_edema(self, image: np.ndarray) -> float:
        """Detect pulmonary edema"""
        # Edema appears as increased density in lungs
        # Calculate image variance as indicator
        variance = np.var(image) / 255.0
        
        # High variance indicates edema
        if variance > 0.3:
            return min(1.0, variance)
        return 0.0
    
    def _detect_vessel_blockage(
        self,
        image: np.ndarray,
        contours: list
    ) -> float:
        """Detect vessel blockage"""
        if not contours:
            return 0.0
        
        # Analyze vessel continuity
        # Blockage appears as discontinuity or narrowing
        vessel_areas = [cv2.contourArea(c) for c in contours]
        
        if not vessel_areas:
            return 0.0
        
        # High variance in vessel areas indicates blockage
        area_variance = np.var(vessel_areas)
        mean_area = np.mean(vessel_areas)
        
        if mean_area > 0:
            blockage_score = min(1.0, area_variance / (mean_area ** 2))
        else:
            blockage_score = 0.0
        
        return blockage_score
    
    def _determine_affected_vessel(
        self,
        contours: list,
        image_shape: Tuple
    ) -> str:
        """Determine which vessel is affected"""
        if not contours:
            return "Unknown"
        
        # Analyze contour positions
        # LAD: left anterior descending (left side)
        # RCA: right coronary artery (right side)
        # LCx: left circumflex (left side, lower)
        
        centroids = []
        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centroids.append((cx, cy))
        
        if not centroids:
            return "Unknown"
        
        # Determine vessel based on position
        avg_x = np.mean([c[0] for c in centroids])
        avg_y = np.mean([c[1] for c in centroids])
        
        if avg_x < image_shape[1] / 3:
            return "LAD"
        elif avg_x > 2 * image_shape[1] / 3:
            return "RCA"
        else:
            return "LCx"


# Example usage
if __name__ == "__main__":
    processor = CardiacImageProcessor()
    
    # Process ECG
    # ecg_features = processor.process_image("ecg.jpg", "ecg")
    # print(f"ECG Abnormality Score: {ecg_features.abnormality_score}")
    # print(f"Findings: {ecg_features.findings}")
