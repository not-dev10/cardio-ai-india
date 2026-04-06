# Next Steps - Implementation Guide
## Cardiac Health AI - From Testing to Production

**Current Status:** All core components tested and working ✓  
**Next Phase:** Hospital data integration and clinical validation  
**Timeline:** 30 days to first hospital deployment

---

## Week 1: OCR Setup & Real Data Testing

### Day 1-2: Install Tesseract OCR

**Windows Installation:**
```powershell
# Download installer
# https://github.com/UB-Mannheim/tesseract/wiki

# Install to default location: C:\Program Files\Tesseract-OCR

# Verify installation
tesseract --version

# Add to Python path (if needed)
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux Installation:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
tesseract --version
```

**macOS Installation:**
```bash
brew install tesseract
tesseract --version
```

### Day 3-4: Test with Real Blood Reports

**Objective:** Validate OCR accuracy on actual medical reports

**Test Process:**
```python
from backend.services.ocr_service import MedicalReportOCR

# Initialize OCR
ocr = MedicalReportOCR()

# Process real blood report
result = ocr.process_medical_report(
    "path/to/blood_report.pdf",
    report_type="blood"
)

# Validate extraction
validation = ocr.validate_extracted_data(result)

# Check accuracy
print(f"Extracted values: {len([v for v in result.values() if v])}")
print(f"Validation status: {validation['is_valid']}")
```

**Expected Accuracy:** 85-95% for clear reports

**Troubleshooting:**
- If accuracy < 80%: Adjust image preprocessing
- If values missing: Check report format
- If errors: Review OCR logs

### Day 5-7: Integrate with Medical Validator

**Objective:** Connect OCR output to medical validation

**Integration Code:**
```python
from backend.services.ocr_service import MedicalReportOCR
from ml_model.medical_validator import MedicalValidator

# Step 1: Extract from report
ocr = MedicalReportOCR()
blood_data = ocr.process_medical_report("report.pdf", "blood")

# Step 2: Validate lab values
validator = MedicalValidator()
lab_validation = validator.validate_lab_values(blood_data)

# Step 3: Create patient profile
patient_data = {
    "age": 55,
    "sex": 1,
    "chest_pain_type": 2,
    "resting_bp": 140,
    "cholesterol": int(blood_data.get('cholesterol_total', 0)),
    # ... other features
}

# Step 4: Validate patient data
validation = validator.validate_input_data(patient_data)

# Step 5: Get clinical recommendation
if validation.is_valid:
    print(f"Data Quality: {validation.data_quality_score:.2%}")
    print(f"Clinical Notes: {validation.clinical_notes}")
```

---

## Week 2: Hospital Data Collection

### Day 8-10: Prepare Data Collection Protocol

**Create Data Collection Form:**
```json
{
  "patient_id": "UNIQUE_ID",
  "date_collected": "2024-04-06",
  "blood_report": {
    "file": "path/to/report.pdf",
    "date": "2024-04-06",
    "lab_name": "Apollo Diagnostics"
  },
  "ecg_report": {
    "file": "path/to/ecg.pdf",
    "date": "2024-04-06"
  },
  "imaging": {
    "file": "path/to/xray.jpg",
    "type": "xray",
    "date": "2024-04-06"
  },
  "cardiologist_diagnosis": {
    "has_disease": true,
    "severity": "moderate",
    "notes": "..."
  }
}
```

**Data Security Checklist:**
- [ ] Encrypt all patient data
- [ ] Use secure file transfer (SFTP/HTTPS)
- [ ] Implement access control
- [ ] Audit all data access
- [ ] Comply with DPDP Act

### Day 11-14: Collect First 100 Patients

**Collection Process:**
1. Patient enrollment (informed consent)
2. Blood report collection
3. ECG report collection (if available)
4. Cardiac imaging (if available)
5. Cardiologist diagnosis
6. Data entry into secure database

**Quality Checks:**
- [ ] All required fields present
- [ ] Images are clear and readable
- [ ] Lab values are within expected ranges
- [ ] Cardiologist diagnosis is documented

---

## Week 3: Validation & Accuracy Testing

### Day 15-17: Calculate Performance Metrics

**Metrics to Calculate:**
```python
from sklearn.metrics import (
    confusion_matrix, roc_auc_score, 
    sensitivity_score, specificity_score,
    precision_score, recall_score, f1_score
)

# Get predictions from model
predictions = model.predict(test_data)

# Calculate metrics
tn, fp, fn, tp = confusion_matrix(y_true, predictions).ravel()

sensitivity = tp / (tp + fn)  # Target: >= 0.90
specificity = tn / (tn + fp)  # Target: >= 0.95
ppv = tp / (tp + fp)          # Target: >= 0.90
npv = tn / (tn + fn)          # Target: >= 0.95
auc = roc_auc_score(y_true, predictions)  # Target: >= 0.95

print(f"Sensitivity: {sensitivity:.2%}")
print(f"Specificity: {specificity:.2%}")
print(f"PPV: {ppv:.2%}")
print(f"NPV: {npv:.2%}")
print(f"AUC: {auc:.2%}")
```

**Target Metrics (Medical-Grade):**
- Sensitivity ≥ 90%
- Specificity ≥ 95%
- PPV ≥ 90%
- NPV ≥ 95%
- AUC ≥ 0.95

### Day 18-21: Fairness Analysis

**Check for Bias:**
```python
# Performance by age group
for age_group in ['18-40', '40-60', '60+']:
    mask = (df['age'] >= age_min) & (df['age'] < age_max)
    group_data = df[mask]
    
    sensitivity = calculate_sensitivity(group_data)
    specificity = calculate_specificity(group_data)
    
    print(f"{age_group}: Sensitivity={sensitivity:.2%}, Specificity={specificity:.2%}")

# Performance by gender
for gender in ['M', 'F']:
    mask = df['sex'] == gender
    group_data = df[mask]
    
    sensitivity = calculate_sensitivity(group_data)
    specificity = calculate_specificity(group_data)
    
    print(f"{gender}: Sensitivity={sensitivity:.2%}, Specificity={specificity:.2%}")
```

**Fairness Criteria:**
- Sensitivity difference < 5% across groups
- Specificity difference < 5% across groups
- No systematic bias detected

---

## Week 4: Production Preparation

### Day 22-24: Set Up Production Infrastructure

**Database Setup:**
```python
# Use PostgreSQL with encryption
import psycopg2
from cryptography.fernet import Fernet

# Create encrypted connection
conn = psycopg2.connect(
    host="secure-db.example.com",
    database="cardiac_health",
    user="app_user",
    password="secure_password",
    sslmode="require"
)

# Create tables
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE patients (
        patient_id UUID PRIMARY KEY,
        age INT,
        sex INT,
        created_at TIMESTAMP,
        encrypted_data BYTEA
    )
""")
```

**API Deployment:**
```bash
# Using Docker
docker build -t cardiac-health-api .
docker run -p 8000:8000 cardiac-health-api

# Using AWS Lambda
aws lambda create-function \
    --function-name cardiac-health-predict \
    --runtime python3.9 \
    --handler backend.main.handler
```

### Day 25-27: Monitoring & Alerts

**Set Up Monitoring:**
```python
from backend.monitoring.clinical_monitor import ClinicalMonitor

monitor = ClinicalMonitor()

# Log prediction
monitor.log_prediction(
    patient_id="P123",
    prediction=0.73,
    confidence=0.85,
    model_version="1.0"
)

# Check for drift
drift_detected = monitor.detect_drift()
if drift_detected:
    print("WARNING: Model drift detected!")
    # Trigger retraining

# Generate report
report = monitor.generate_daily_report()
print(report)
```

**Alerts to Set Up:**
- [ ] Model accuracy drops below 90%
- [ ] Prediction latency > 5 seconds
- [ ] Data quality score < 70%
- [ ] Fairness metrics violated
- [ ] System errors > 1%

### Day 28-30: Documentation & Training

**Create Documentation:**
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Deployment guide
- [ ] Troubleshooting guide
- [ ] Clinical guidelines
- [ ] Data privacy policy

**Train Hospital Staff:**
- [ ] How to use the system
- [ ] How to interpret results
- [ ] When to override predictions
- [ ] How to report issues
- [ ] Data security practices

---

## Implementation Checklist

### Week 1: OCR Setup
- [ ] Install Tesseract OCR
- [ ] Test with sample reports
- [ ] Achieve 85%+ accuracy
- [ ] Integrate with validator

### Week 2: Data Collection
- [ ] Create data collection protocol
- [ ] Set up secure database
- [ ] Collect 100 patient records
- [ ] Validate data quality

### Week 3: Validation
- [ ] Calculate performance metrics
- [ ] Verify sensitivity ≥ 90%
- [ ] Verify specificity ≥ 95%
- [ ] Complete fairness analysis

### Week 4: Production
- [ ] Set up production infrastructure
- [ ] Deploy API
- [ ] Set up monitoring
- [ ] Train hospital staff

---

## Success Criteria

**Week 1:**
- ✓ Tesseract installed and working
- ✓ OCR accuracy ≥ 85%
- ✓ Integration complete

**Week 2:**
- ✓ 100 patients enrolled
- ✓ Data quality ≥ 95%
- ✓ No data breaches

**Week 3:**
- ✓ Sensitivity ≥ 90%
- ✓ Specificity ≥ 95%
- ✓ No fairness issues

**Week 4:**
- ✓ API deployed
- ✓ Monitoring active
- ✓ Staff trained

---

## Common Issues & Solutions

### Issue: OCR Accuracy Low (< 80%)
**Solution:**
1. Check image quality
2. Adjust preprocessing parameters
3. Use Google Vision API as fallback
4. Manually review and correct

### Issue: Data Quality Issues
**Solution:**
1. Implement validation rules
2. Flag incomplete records
3. Request resubmission
4. Manual review process

### Issue: Performance Metrics Below Target
**Solution:**
1. Collect more training data
2. Retrain model with new data
3. Adjust decision thresholds
4. Investigate failure cases

### Issue: Fairness Metrics Violated
**Solution:**
1. Analyze bias source
2. Collect more data from underrepresented groups
3. Retrain with balanced data
4. Implement fairness constraints

---

## Budget for 30-Day Implementation

```
Salaries:
- OCR Specialist: ₹50,000
- Data Analyst: ₹40,000
- DevOps Engineer: ₹60,000
Subtotal: ₹150,000

Infrastructure:
- Database: ₹20,000
- API Hosting: ₹15,000
- Monitoring: ₹10,000
Subtotal: ₹45,000

Software:
- Tesseract: Free
- Google Vision API: ₹5,000
- AWS Services: ₹10,000
Subtotal: ₹15,000

Miscellaneous:
- Training: ₹10,000
- Documentation: ₹5,000
Subtotal: ₹15,000

TOTAL: ₹225,000 (~$2,700 USD)
```

---

## Timeline

```
Week 1: OCR Setup & Testing
├── Day 1-2: Install Tesseract
├── Day 3-4: Test with real reports
└── Day 5-7: Integrate with validator

Week 2: Data Collection
├── Day 8-10: Prepare protocol
└── Day 11-14: Collect 100 patients

Week 3: Validation
├── Day 15-17: Calculate metrics
└── Day 18-21: Fairness analysis

Week 4: Production
├── Day 22-24: Infrastructure setup
├── Day 25-27: Monitoring setup
└── Day 28-30: Documentation & training
```

---

## Next Immediate Actions

**Today:**
1. [ ] Install Tesseract OCR
2. [ ] Test with sample blood report
3. [ ] Verify OCR accuracy

**Tomorrow:**
1. [ ] Integrate OCR with validator
2. [ ] Test complete workflow
3. [ ] Document any issues

**This Week:**
1. [ ] Collect first 10 real patient reports
2. [ ] Test OCR on real data
3. [ ] Calculate accuracy metrics
4. [ ] Plan hospital partnerships

---

## Contact & Support

**Technical Issues:**
- Email: tech@cardiachealthai.com
- Slack: #technical-support

**Clinical Questions:**
- Email: clinical@cardiachealthai.com
- Phone: +91-XXX-XXXX-XXXX

**Regulatory Questions:**
- Email: compliance@cardiachealthai.com
- Phone: +91-XXX-XXXX-XXXX

---

**Document Version:** 1.0  
**Last Updated:** April 6, 2026  
**Next Review:** April 13, 2026
