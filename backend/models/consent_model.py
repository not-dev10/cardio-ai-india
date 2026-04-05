"""
Consent Management Model - DPDP Act Compliant
India's Digital Personal Data Protection Act (DPDP) 2023
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ConsentPurpose(str, Enum):
    """Purposes for which data is collected"""
    RISK_PREDICTION = "risk_prediction"
    REPORT_ANALYSIS = "report_analysis"
    DOCTOR_RECOMMENDATION = "doctor_recommendation"
    PREDICTION_HISTORY = "prediction_history"
    RESEARCH_ANONYMIZED = "research_anonymized"
    SERVICE_IMPROVEMENT = "service_improvement"


class ConsentStatus(str, Enum):
    """Consent status"""
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class UserConsent(BaseModel):
    """
    User consent model compliant with DPDP Act
    
    DPDP Act Requirements:
    1. Explicit consent for each purpose
    2. Clear and plain language
    3. Easy withdrawal mechanism
    4. Purpose limitation
    5. Data minimization
    6. Retention limits
    """
    user_id: str
    consent_id: str = Field(default_factory=lambda: f"consent_{datetime.now().timestamp()}")
    
    # Purpose-specific consents
    purposes: List[ConsentPurpose]
    
    # Consent details
    status: ConsentStatus = ConsentStatus.PENDING
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None  # Auto-expire after 2 years
    
    # Consent text shown to user
    consent_text: str
    consent_version: str = "1.0"
    
    # User acknowledgment
    user_acknowledged: bool = False
    ip_address: Optional[str] = None
    device_info: Optional[str] = None
    
    # Data retention
    data_retention_days: int = 730  # 2 years default
    
    # Audit trail
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class ConsentManager:
    """Manage user consents"""
    
    # Consent texts in English and Hindi
    CONSENT_TEXTS = {
        "english": {
            "risk_prediction": """
We will use your health data (age, blood pressure, cholesterol, etc.) to predict your heart disease risk using AI. This is for screening purposes only, not medical diagnosis.

Your data will be:
✓ Encrypted and stored securely
✓ Used only for risk prediction
✓ Never shared without your permission
✓ Deleted after 2 years or on your request

You can withdraw consent anytime.
            """,
            
            "report_analysis": """
We will analyze your uploaded medical reports (blood tests, ECG) to extract health parameters. 

Your reports will be:
✓ Processed using OCR technology
✓ Stored temporarily (deleted after extraction)
✓ Never shared with third parties
✓ Used only for your risk assessment

Original reports are not stored permanently.
            """,
            
            "doctor_recommendation": """
We will use your location to recommend nearby cardiologists and hospitals.

Your location will be:
✓ Used only for finding nearby doctors
✓ Not stored permanently
✓ Not shared with third parties
✓ Used only when you request recommendations

You can deny location access anytime.
            """,
            
            "prediction_history": """
We will store your prediction history to track your health over time.

Your history will:
✓ Be encrypted and secure
✓ Be accessible only to you
✓ Help track health trends
✓ Be deleted on your request

You can view and delete your history anytime.
            """,
            
            "research_anonymized": """
We may use your anonymized data for medical research to improve our AI model.

Your data will be:
✓ Completely anonymized (no personal info)
✓ Used only for research
✓ Help improve predictions for others
✓ Never linked back to you

This helps make healthcare AI better for everyone.
            """,
        },
        
        "hindi": {
            "risk_prediction": """
हम आपके स्वास्थ्य डेटा (उम्र, रक्तचाप, कोलेस्ट्रॉल, आदि) का उपयोग AI से हृदय रोग के जोखिम की भविष्यवाणी करने के लिए करेंगे। यह केवल स्क्रीनिंग के लिए है, चिकित्सा निदान नहीं।

आपका डेटा:
✓ एन्क्रिप्टेड और सुरक्षित रूप से संग्रहीत
✓ केवल जोखिम भविष्यवाणी के लिए उपयोग
✓ आपकी अनुमति के बिना कभी साझा नहीं
✓ 2 साल बाद या आपके अनुरोध पर हटा दिया जाएगा

आप किसी भी समय सहमति वापस ले सकते हैं।
            """,
        }
    }
    
    @staticmethod
    def create_consent_request(
        user_id: str,
        purposes: List[ConsentPurpose],
        language: str = "english"
    ) -> UserConsent:
        """
        Create a consent request for user
        
        Args:
            user_id: User identifier
            purposes: List of purposes
            language: Language for consent text
            
        Returns:
            UserConsent: Consent object
        """
        # Combine consent texts for all purposes
        consent_texts = []
        for purpose in purposes:
            text = ConsentManager.CONSENT_TEXTS.get(language, {}).get(
                purpose.value,
                ConsentManager.CONSENT_TEXTS["english"][purpose.value]
            )
            consent_texts.append(f"**{purpose.value.replace('_', ' ').title()}**\n{text}")
        
        combined_text = "\n\n".join(consent_texts)
        
        # Add general disclaimer
        disclaimer = """
**Important Disclaimer**
This is an AI-based screening tool, NOT a medical diagnosis. Always consult a qualified doctor for medical advice. We are not liable for any medical decisions made based on this tool.

**Your Rights (DPDP Act 2023)**
✓ Right to access your data
✓ Right to correct your data
✓ Right to delete your data
✓ Right to withdraw consent
✓ Right to data portability

For questions: support@cardioai.in
        """
        
        combined_text += "\n\n" + disclaimer
        
        return UserConsent(
            user_id=user_id,
            purposes=purposes,
            consent_text=combined_text,
            expires_at=datetime.now().replace(year=datetime.now().year + 2)
        )
    
    @staticmethod
    def grant_consent(consent: UserConsent, ip_address: str, device_info: str) -> UserConsent:
        """Grant consent"""
        consent.status = ConsentStatus.GRANTED
        consent.granted_at = datetime.now()
        consent.user_acknowledged = True
        consent.ip_address = ip_address
        consent.device_info = device_info
        consent.updated_at = datetime.now()
        return consent
    
    @staticmethod
    def withdraw_consent(consent: UserConsent) -> UserConsent:
        """Withdraw consent"""
        consent.status = ConsentStatus.WITHDRAWN
        consent.withdrawn_at = datetime.now()
        consent.updated_at = datetime.now()
        return consent
    
    @staticmethod
    def check_consent_valid(consent: UserConsent, purpose: ConsentPurpose) -> bool:
        """
        Check if consent is valid for a purpose
        
        Args:
            consent: User consent
            purpose: Purpose to check
            
        Returns:
            bool: Whether consent is valid
        """
        # Check status
        if consent.status != ConsentStatus.GRANTED:
            return False
        
        # Check purpose
        if purpose not in consent.purposes:
            return False
        
        # Check expiry
        if consent.expires_at and datetime.now() > consent.expires_at:
            return False
        
        return True


class DataDeletionRequest(BaseModel):
    """Data deletion request (Right to be forgotten)"""
    user_id: str
    request_id: str = Field(default_factory=lambda: f"del_{datetime.now().timestamp()}")
    requested_at: datetime = Field(default_factory=datetime.now)
    reason: Optional[str] = None
    status: str = "pending"  # pending, processing, completed
    completed_at: Optional[datetime] = None
    
    # What to delete
    delete_predictions: bool = True
    delete_reports: bool = True
    delete_profile: bool = True
    delete_all: bool = False


class DataAccessRequest(BaseModel):
    """Data access request (Right to access)"""
    user_id: str
    request_id: str = Field(default_factory=lambda: f"access_{datetime.now().timestamp()}")
    requested_at: datetime = Field(default_factory=datetime.now)
    status: str = "pending"
    data_package_url: Optional[str] = None
    completed_at: Optional[datetime] = None


# Example consent flow
def example_consent_flow():
    """Example of consent flow"""
    
    # 1. User signs up
    user_id = "user_12345"
    
    # 2. Create consent request
    consent = ConsentManager.create_consent_request(
        user_id=user_id,
        purposes=[
            ConsentPurpose.RISK_PREDICTION,
            ConsentPurpose.REPORT_ANALYSIS,
            ConsentPurpose.PREDICTION_HISTORY
        ],
        language="english"
    )
    
    print("Consent Request Created:")
    print(f"Consent ID: {consent.consent_id}")
    print(f"Purposes: {consent.purposes}")
    print(f"\nConsent Text:\n{consent.consent_text}")
    
    # 3. User grants consent
    consent = ConsentManager.grant_consent(
        consent,
        ip_address="192.168.1.1",
        device_info="Android 12, Samsung Galaxy"
    )
    
    print(f"\n✅ Consent Granted at {consent.granted_at}")
    
    # 4. Check if consent is valid for a purpose
    is_valid = ConsentManager.check_consent_valid(
        consent,
        ConsentPurpose.RISK_PREDICTION
    )
    print(f"\nConsent valid for risk prediction: {is_valid}")
    
    # 5. User withdraws consent
    consent = ConsentManager.withdraw_consent(consent)
    print(f"\n❌ Consent Withdrawn at {consent.withdrawn_at}")
    
    # 6. User requests data deletion
    deletion_request = DataDeletionRequest(
        user_id=user_id,
        reason="No longer using the app",
        delete_all=True
    )
    print(f"\n🗑️ Data Deletion Request: {deletion_request.request_id}")


if __name__ == "__main__":
    example_consent_flow()
