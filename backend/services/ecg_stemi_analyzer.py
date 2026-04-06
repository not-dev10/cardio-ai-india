"""
Enhanced ECG STEMI Analysis Module
Based on standard STEMI interpretation criteria
Improves accuracy of ECG report analysis
"""
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class STEMIFindings:
    """STEMI findings from ECG analysis"""
    is_stemi: bool
    confidence: float
    st_elevation_leads: List[str]
    st_depression_leads: List[str]
    t_wave_changes: List[str]
    reciprocal_changes: bool
    affected_artery: str
    risk_level: str
    clinical_notes: str


class ECGSTEMIAnalyzer:
    """
    Analyzes ECG for STEMI (ST-Elevation Myocardial Infarction)
    Based on standard ECG interpretation criteria
    """
    
    # Standard ECG leads and their territories
    LEAD_TERRITORIES = {
        # Anterior wall
        "V1": "anterior",
        "V2": "anterior",
        "V3": "anterior",
        "V4": "anterior",
        
        # Lateral wall
        "I": "lateral",
        "aVL": "lateral",
        "V5": "lateral",
        "V6": "lateral",
        
        # Inferior wall
        "II": "inferior",
        "III": "inferior",
        "aVF": "inferior",
        
        # Right ventricle
        "V4R": "right_ventricle",
        "V5R": "right_ventricle",
    }
    
    # ST elevation thresholds (in mm)
    ST_ELEVATION_THRESHOLD = 1.0  # ≥1mm in limb leads, ≥2mm in precordial
    ST_DEPRESSION_THRESHOLD = 0.5
    
    # T wave inversion threshold (in mm)
    T_WAVE_THRESHOLD = 0.5
    
    def __init__(self):
        """Initialize ECG STEMI analyzer"""
        self.findings = None
    
    def analyze_ecg(self, ecg_data: Dict) -> STEMIFindings:
        """
        Analyze ECG for STEMI
        
        Args:
            ecg_data: Dictionary with ECG measurements
                {
                    "heart_rate": 78,
                    "pr_interval": 160,
                    "qrs_duration": 100,
                    "qt_interval": 420,
                    "st_elevation": {"V1": 2.5, "V2": 3.0, ...},
                    "st_depression": {"II": 0.5, ...},
                    "t_wave_inversion": {"V1": 1.2, ...},
                    "q_waves": ["V1", "V2"],
                    "leads": ["I", "II", "III", "aVR", "aVL", "aVF", "V1-V6"]
                }
        
        Returns:
            STEMIFindings with analysis results
        """
        
        st_elevation_leads = self._detect_st_elevation(ecg_data)
        st_depression_leads = self._detect_st_depression(ecg_data)
        t_wave_changes = self._detect_t_wave_changes(ecg_data)
        reciprocal_changes = self._detect_reciprocal_changes(st_elevation_leads, st_depression_leads)
        
        # Determine if STEMI
        is_stemi = len(st_elevation_leads) >= 2  # ≥2 contiguous leads
        
        # Determine affected artery
        affected_artery = self._determine_affected_artery(st_elevation_leads)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            st_elevation_leads, st_depression_leads, t_wave_changes, reciprocal_changes
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(is_stemi, confidence, st_elevation_leads)
        
        # Generate clinical notes
        clinical_notes = self._generate_clinical_notes(
            is_stemi, affected_artery, st_elevation_leads, reciprocal_changes
        )
        
        self.findings = STEMIFindings(
            is_stemi=is_stemi,
            confidence=confidence,
            st_elevation_leads=st_elevation_leads,
            st_depression_leads=st_depression_leads,
            t_wave_changes=t_wave_changes,
            reciprocal_changes=reciprocal_changes,
            affected_artery=affected_artery,
            risk_level=risk_level,
            clinical_notes=clinical_notes
        )
        
        return self.findings
    
    def _detect_st_elevation(self, ecg_data: Dict) -> List[str]:
        """Detect ST elevation in leads"""
        st_elevation_leads = []
        st_elevation = ecg_data.get("st_elevation", {})
        
        for lead, value in st_elevation.items():
            # Different thresholds for different leads
            if lead in ["V1", "V2", "V3", "V4"]:
                threshold = 2.0  # Precordial leads
            else:
                threshold = 1.0  # Limb leads
            
            if value >= threshold:
                st_elevation_leads.append(lead)
        
        return st_elevation_leads
    
    def _detect_st_depression(self, ecg_data: Dict) -> List[str]:
        """Detect ST depression in leads"""
        st_depression_leads = []
        st_depression = ecg_data.get("st_depression", {})
        
        for lead, value in st_depression.items():
            if value >= self.ST_DEPRESSION_THRESHOLD:
                st_depression_leads.append(lead)
        
        return st_depression_leads
    
    def _detect_t_wave_changes(self, ecg_data: Dict) -> List[str]:
        """Detect T wave changes"""
        t_wave_changes = []
        t_wave_inversion = ecg_data.get("t_wave_inversion", {})
        
        for lead, value in t_wave_inversion.items():
            if value >= self.T_WAVE_THRESHOLD:
                t_wave_changes.append(f"{lead} (inverted)")
        
        return t_wave_changes
    
    def _detect_reciprocal_changes(self, st_elevation_leads: List[str], 
                                   st_depression_leads: List[str]) -> bool:
        """Detect reciprocal ST changes"""
        # Reciprocal changes are ST depression in opposite wall
        anterior_leads = {"V1", "V2", "V3", "V4"}
        inferior_leads = {"II", "III", "aVF"}
        lateral_leads = {"I", "aVL", "V5", "V6"}
        
        st_elev_set = set(st_elevation_leads)
        st_depr_set = set(st_depression_leads)
        
        # Check for reciprocal changes
        if st_elev_set & anterior_leads and st_depr_set & inferior_leads:
            return True
        if st_elev_set & inferior_leads and st_depr_set & anterior_leads:
            return True
        if st_elev_set & lateral_leads and st_depr_set & (anterior_leads | inferior_leads):
            return True
        
        return False
    
    def _determine_affected_artery(self, st_elevation_leads: List[str]) -> str:
        """Determine which coronary artery is affected"""
        st_elev_set = set(st_elevation_leads)
        
        # Anterior wall (LAD - Left Anterior Descending)
        if st_elev_set & {"V1", "V2", "V3", "V4"}:
            if "V1" in st_elev_set and "V2" in st_elev_set:
                return "LAD (Left Anterior Descending)"
        
        # Inferior wall (RCA - Right Coronary Artery)
        if st_elev_set & {"II", "III", "aVF"}:
            if len(st_elev_set & {"II", "III", "aVF"}) >= 2:
                return "RCA (Right Coronary Artery)"
        
        # Lateral wall (LCx - Left Circumflex)
        if st_elev_set & {"I", "aVL", "V5", "V6"}:
            if len(st_elev_set & {"I", "aVL", "V5", "V6"}) >= 2:
                return "LCx (Left Circumflex)"
        
        # Posterior wall (RCA or LCx)
        if st_elev_set & {"V7", "V8", "V9"}:
            return "Posterior (RCA or LCx)"
        
        return "Unknown"
    
    def _calculate_confidence(self, st_elevation_leads: List[str],
                             st_depression_leads: List[str],
                             t_wave_changes: List[str],
                             reciprocal_changes: bool) -> float:
        """Calculate confidence score for STEMI diagnosis"""
        confidence = 0.0
        
        # ST elevation in ≥2 contiguous leads (most important)
        if len(st_elevation_leads) >= 2:
            confidence += 0.4
        elif len(st_elevation_leads) == 1:
            confidence += 0.2
        
        # ST depression (reciprocal changes)
        if len(st_depression_leads) >= 2:
            confidence += 0.2
        elif len(st_depression_leads) == 1:
            confidence += 0.1
        
        # T wave changes
        if len(t_wave_changes) >= 2:
            confidence += 0.2
        elif len(t_wave_changes) == 1:
            confidence += 0.1
        
        # Reciprocal changes
        if reciprocal_changes:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _determine_risk_level(self, is_stemi: bool, confidence: float,
                             st_elevation_leads: List[str]) -> str:
        """Determine clinical risk level"""
        if not is_stemi:
            return "Low Risk"
        
        if confidence >= 0.8:
            return "High Risk - Definite STEMI"
        elif confidence >= 0.6:
            return "Moderate-High Risk - Probable STEMI"
        else:
            return "Moderate Risk - Possible STEMI"
    
    def _generate_clinical_notes(self, is_stemi: bool, affected_artery: str,
                                st_elevation_leads: List[str],
                                reciprocal_changes: bool) -> str:
        """Generate clinical notes"""
        notes = []
        
        if is_stemi:
            notes.append(f"STEMI detected in {affected_artery}")
            notes.append(f"ST elevation in leads: {', '.join(st_elevation_leads)}")
            
            if reciprocal_changes:
                notes.append("Reciprocal ST depression present")
            
            notes.append("URGENT: Activate STEMI protocol")
            notes.append("Recommend: Immediate cardiology consultation")
            notes.append("Consider: Primary PCI or thrombolytic therapy")
        else:
            notes.append("No STEMI pattern detected")
            notes.append("Consider other diagnoses")
        
        return " | ".join(notes)
    
    def get_summary(self) -> Dict:
        """Get summary of findings"""
        if not self.findings:
            return {}
        
        return {
            "is_stemi": self.findings.is_stemi,
            "confidence": f"{self.findings.confidence:.2%}",
            "affected_artery": self.findings.affected_artery,
            "risk_level": self.findings.risk_level,
            "st_elevation_leads": self.findings.st_elevation_leads,
            "st_depression_leads": self.findings.st_depression_leads,
            "t_wave_changes": self.findings.t_wave_changes,
            "reciprocal_changes": self.findings.reciprocal_changes,
            "clinical_notes": self.findings.clinical_notes
        }


# Standard ECG interpretation criteria
ECG_CRITERIA = {
    "STEMI": {
        "anterior": {
            "st_elevation": "≥2mm in V1-V4",
            "reciprocal": "ST depression in II, III, aVF",
            "artery": "LAD"
        },
        "inferior": {
            "st_elevation": "≥1mm in II, III, aVF",
            "reciprocal": "ST depression in V1-V3",
            "artery": "RCA"
        },
        "lateral": {
            "st_elevation": "≥1mm in I, aVL, V5-V6",
            "reciprocal": "ST depression in II, III",
            "artery": "LCx"
        },
        "posterior": {
            "st_elevation": "ST elevation in V7-V9",
            "reciprocal": "ST depression in V1-V3",
            "artery": "RCA or LCx"
        }
    },
    "NSTEMI": {
        "st_depression": "≥1mm in ≥2 leads",
        "t_wave_inversion": "≥1mm in ≥2 leads",
        "troponin": "Elevated"
    },
    "Unstable Angina": {
        "st_changes": "None or minimal",
        "t_wave_changes": "Possible",
        "troponin": "Normal"
    }
}


def example_stemi_analysis():
    """Example STEMI analysis"""
    analyzer = ECGSTEMIAnalyzer()
    
    # Example ECG data - Anterior STEMI
    ecg_data = {
        "heart_rate": 95,
        "pr_interval": 160,
        "qrs_duration": 100,
        "qt_interval": 420,
        "st_elevation": {
            "V1": 2.5,
            "V2": 3.0,
            "V3": 2.8,
            "V4": 2.2,
            "I": 1.5,
            "aVL": 1.2
        },
        "st_depression": {
            "II": 0.8,
            "III": 0.9,
            "aVF": 0.7
        },
        "t_wave_inversion": {
            "V1": 0.6,
            "V2": 0.7
        },
        "q_waves": ["V1", "V2"]
    }
    
    # Analyze
    findings = analyzer.analyze_ecg(ecg_data)
    
    print("\n" + "=" * 80)
    print("ECG STEMI ANALYSIS RESULTS")
    print("=" * 80)
    print(f"\nIs STEMI: {findings.is_stemi}")
    print(f"Confidence: {findings.confidence:.2%}")
    print(f"Affected Artery: {findings.affected_artery}")
    print(f"Risk Level: {findings.risk_level}")
    print(f"\nST Elevation Leads: {', '.join(findings.st_elevation_leads)}")
    print(f"ST Depression Leads: {', '.join(findings.st_depression_leads)}")
    print(f"T Wave Changes: {', '.join(findings.t_wave_changes)}")
    print(f"Reciprocal Changes: {findings.reciprocal_changes}")
    print(f"\nClinical Notes:\n{findings.clinical_notes}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    example_stemi_analysis()
