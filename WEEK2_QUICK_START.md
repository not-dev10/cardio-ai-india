# Week 2 Quick Start Guide
## Data Collection & Hospital Integration

**Start Date:** April 13, 2026  
**Duration:** 7 days  
**Goal:** Collect 100 real patient records

---

## Day 8-10: Prepare Data Collection Protocol

### Step 1: Create Data Collection Form
```python
# Save as: data_collection_form.json
{
  "patient_id": "UNIQUE_ID",
  "date_collected": "2024-04-13",
  "demographics": {
    "age": 55,
    "sex": 1,
    "location": "Delhi"
  },
  "blood_report": {
    "file": "path/to/report.pdf",
    "date": "2024-04-13",
    "lab_name": "Apollo Diagnostics"
  },
  "ecg_report": {
    "file": "path/to/ecg.pdf",
    "date": "2024-04-13"
  },
  "imaging": {
    "file": "path/to/xray.jpg",
    "type": "xray",
    "date": "2024-04-13"
  },
  "cardiologist_diagnosis": {
    "has_disease": true,
    "severity": "moderate",
    "notes": "..."
  }
}
```

### Step 2: Set Up Secure Database
```bash
# Install PostgreSQL
# Create database
createdb cardiac_health

# Create tables
psql cardiac_health < schema.sql
```

### Step 3: Prepare Informed Consent
- [ ] Create consent form (Hindi + English)
- [ ] Include: Purpose, risks, benefits, privacy
- [ ] Get ethics board approval
- [ ] Print for hospital use

### Step 4: Create Data Security Checklist
- [ ] Encrypt all patient data
- [ ] Use secure file transfer (SFTP/HTTPS)
- [ ] Implement access control
- [ ] Audit all data access
- [ ] Comply with DPDP Act

---

## Day 11-14: Collect First 100 Patients

### Collection Process
```
1. Patient enrollment (informed consent)
   ↓
2. Blood report collection
   ↓
3. ECG report collection (if available)
   ↓
4. Cardiac imaging (if available)
   ↓
5. Cardiologist diagnosis
   ↓
6. Data entry into secure database
```

### Quality Checks
- [ ] All required fields present
- [ ] Images are clear and readable
- [ ] Lab values are within expected ranges
- [ ] Cardiologist diagnosis is documented
- [ ] No missing data

### Daily Targets
- Day 11: 20 patients
- Day 12: 30 patients
- Day 13: 30 patients
- Day 14: 20 patients
- **Total: 100 patients**

---

## Hospital Partnership Template

### Email Template
```
Subject: Cardiac Health AI - Research Partnership Opportunity

Dear [Hospital Director],

We are developing a medical-grade AI system for cardiac disease prediction.
We would like to partner with [Hospital Name] for clinical validation.

Partnership Benefits:
- Access to advanced AI predictions
- Improved patient outcomes
- Research publication opportunity
- Revenue sharing (if applicable)

We need:
- 100 patient records (blood reports, ECG, imaging)
- Cardiologist validation
- 6-month outcome tracking

Timeline: 6 months
Budget: ₹[amount]

Would you be interested in discussing this opportunity?

Best regards,
[Your Name]
```

### Required Documents
- [ ] Partnership proposal
- [ ] Data sharing agreement
- [ ] Informed consent form
- [ ] Ethics board approval
- [ ] Insurance documentation

---

## Data Collection Checklist

### Before Collection
- [ ] Ethics board approval obtained
- [ ] Hospital partnerships signed
- [ ] Database set up and tested
- [ ] Staff trained on protocol
- [ ] Informed consent forms printed
- [ ] Data security measures in place

### During Collection
- [ ] Patient enrollment tracked
- [ ] Reports collected and scanned
- [ ] Data entered into database
- [ ] Quality checks performed
- [ ] Cardiologist diagnosis recorded
- [ ] Patient privacy maintained

### After Collection
- [ ] Data backed up securely
- [ ] Quality report generated
- [ ] Accuracy metrics calculated
- [ ] Issues documented
- [ ] Next steps planned

---

## Success Metrics (Week 2)

| Metric | Target | Status |
|--------|--------|--------|
| Patients enrolled | 100 | [ ] |
| Data quality | ≥95% | [ ] |
| Missing data | <5% | [ ] |
| Report clarity | ≥90% | [ ] |
| Cardiologist agreement | ≥95% | [ ] |
| Data security | 100% | [ ] |

---

## Common Issues & Solutions

### Issue: Low enrollment
**Solution:** Increase recruitment efforts, offer incentives, extend timeline

### Issue: Poor image quality
**Solution:** Request rescans, use better scanning equipment, train staff

### Issue: Missing data
**Solution:** Follow up with patients, request additional tests, document reasons

### Issue: Data security concerns
**Solution:** Implement encryption, audit access, comply with regulations

---

## Budget for Week 2

```
Salaries:
- Clinical coordinator: ₹30,000
- Data analyst: ₹40,000
Subtotal: ₹70,000

Infrastructure:
- Database: ₹20,000
- API hosting: ₹15,000
- Monitoring: ₹10,000
Subtotal: ₹45,000

Miscellaneous:
- Travel to hospitals: ₹20,000
- Training materials: ₹10,000
Subtotal: ₹30,000

TOTAL: ₹145,000 (~$1,740)
```

---

## Quick Commands

### Test OCR with Real Data
```bash
python test_ocr_and_processing_fixed.py
```

### Validate Patient Data
```python
from ml_model.medical_validator import MedicalValidator

validator = MedicalValidator()
result = validator.validate_input_data(patient_data)
print(f"Valid: {result.is_valid}")
print(f"Quality: {result.data_quality_score:.2%}")
```

### Calculate Metrics
```python
from sklearn.metrics import confusion_matrix, roc_auc_score

tn, fp, fn, tp = confusion_matrix(y_true, predictions).ravel()
sensitivity = tp / (tp + fn)
specificity = tn / (tn + fp)
auc = roc_auc_score(y_true, predictions)

print(f"Sensitivity: {sensitivity:.2%}")
print(f"Specificity: {specificity:.2%}")
print(f"AUC: {auc:.2%}")
```

---

## Hospital Contact Template

### Initial Outreach
```
Hospital: [Name]
Contact: [Director Name]
Email: [Email]
Phone: [Phone]
Status: [ ] Not contacted [ ] Interested [ ] Signed

Notes:
- [Key discussion points]
- [Next steps]
- [Follow-up date]
```

---

## Week 2 Timeline

```
Day 8-10: Prepare Protocol
├── Create data collection form
├── Set up database
├── Prepare consent forms
└── Create security checklist

Day 11-14: Collect Patients
├── Day 11: 20 patients
├── Day 12: 30 patients
├── Day 13: 30 patients
└── Day 14: 20 patients

Total: 100 patients
```

---

## Next Week Preview (Week 3)

### Objectives
1. Calculate performance metrics
2. Verify sensitivity ≥ 90%
3. Verify specificity ≥ 95%
4. Complete fairness analysis

### Timeline
- Day 15-17: Calculate metrics
- Day 18-21: Fairness analysis

---

## Resources

### Documentation
- `NEXT_STEPS_IMPLEMENTATION.md` - Full roadmap
- `IMMEDIATE_ACTION_PLAN.md` - 30-day plan
- `MEDICAL_GRADE_IMPLEMENTATION.md` - Framework

### Code
- `test_ocr_and_processing_fixed.py` - Test suite
- `ml_model/medical_validator.py` - Validator
- `backend/monitoring/clinical_monitor.py` - Monitoring

### Contacts
- Technical: tech@cardiachealthai.com
- Clinical: clinical@cardiachealthai.com
- Compliance: compliance@cardiachealthai.com

---

## Final Checklist

- [ ] Week 1 complete
- [ ] All tests passed
- [ ] EasyOCR installed
- [ ] Medical validator working
- [ ] Ready for Week 2
- [ ] Hospital partnerships identified
- [ ] Data collection protocol prepared
- [ ] Database set up
- [ ] Staff trained
- [ ] Ethics approval obtained

---

**Week 2 Start Date:** April 13, 2026  
**Week 2 Goal:** 100 patient records  
**Week 2 Budget:** ₹145,000  
**Status:** Ready to begin
