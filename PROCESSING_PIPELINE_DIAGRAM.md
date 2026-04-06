# Processing Pipeline Diagrams
## Visual Guide to Image & PDF Processing

---

## 1. COMPLETE WORKFLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER UPLOADS REPORT                          │
│              (JPG, PNG, PDF - Max 50MB)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FILE VALIDATION                               │
│  • Check file type (.jpg, .png, .pdf)                          │
│  • Check file size (< 50MB)                                    │
│  • Scan for malware                                            │
│  • Verify format integrity                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FORMAT CONVERSION                             │
│                                                                 │
│  If PDF:                    If Image:                          │
│  ├─ Convert to images       ├─ Load directly                   │
│  ├─ One image per page      ├─ Validate format                │
│  └─ Process each page       └─ Ready for OCR                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 IMAGE PREPROCESSING                             │
│                                                                 │
│  Original Image                                                │
│       │                                                         │
│       ├─→ Convert to Grayscale                                 │
│       │                                                         │
│       ├─→ Denoise (FastNlMeansDenoising)                       │
│       │                                                         │
│       ├─→ Enhance Contrast (CLAHE)                             │
│       │                                                         │
│       ├─→ Apply Threshold (Otsu's method)                      │
│       │                                                         │
│       └─→ Preprocessed Image (Ready for OCR)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OCR EXTRACTION                               │
│                                                                 │
│  Preprocessed Image                                            │
│       │                                                         │
│       ├─→ Tesseract OCR (Default)                              │
│       │   └─ Extract raw text                                  │
│       │                                                         │
│       └─→ Google Vision API (Optional)                         │
│           └─ Better for handwriting                            │
│                                                                 │
│  Output: Raw Text (85-95% accuracy)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              STRUCTURED DATA EXTRACTION                         │
│                                                                 │
│  Raw Text                                                      │
│       │                                                         │
│       ├─→ Apply Regex Patterns                                 │
│       │   ├─ Blood values (cholesterol, glucose, etc.)        │
│       │   ├─ ECG parameters (HR, PR, QRS, etc.)               │
│       │   └─ Imaging findings (stenosis, etc.)                │
│       │                                                         │
│       ├─→ Clean & Normalize Values                             │
│       │   ├─ Remove units                                      │
│       │   ├─ Convert to numbers                                │
│       │   └─ Handle variations                                 │
│       │                                                         │
│       └─→ Structured Data Dictionary                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DATA VALIDATION                                │
│                                                                 │
│  Structured Data                                               │
│       │                                                         │
│       ├─→ Check Value Ranges                                   │
│       │   ├─ Cholesterol: 100-400 mg/dL                       │
│       │   ├─ Blood Sugar: 40-400 mg/dL                        │
│       │   └─ Heart Rate: 40-220 bpm                           │
│       │                                                         │
│       ├─→ Validate Consistency                                 │
│       │   ├─ LDL + HDL + Triglycerides = Total Chol           │
│       │   ├─ Age vs disease prevalence                         │
│       │   └─ Logical relationships                             │
│       │                                                         │
│       ├─→ Flag Anomalies                                       │
│       │   ├─ Warnings (unusual but possible)                   │
│       │   └─ Errors (impossible values)                        │
│       │                                                         │
│       └─→ Confidence Score (0-1)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CLINICAL INTEGRATION                               │
│                                                                 │
│  Validated Data                                                │
│       │                                                         │
│       ├─→ Map to ML Features                                   │
│       │   └─ Convert to model input format                     │
│       │                                                         │
│       ├─→ Combine with Patient Info                            │
│       │   ├─ Age, sex, smoking, diabetes                       │
│       │   └─ Medical history                                   │
│       │                                                         │
│       ├─→ Generate Prediction                                  │
│       │   ├─ ML model inference                                │
│       │   ├─ Confidence score                                  │
│       │   └─ Risk level                                        │
│       │                                                         │
│       ├─→ Generate Explanations                                │
│       │   ├─ SHAP feature importance                           │
│       │   ├─ Clinical interpretation                           │
│       │   └─ Risk factors                                      │
│       │                                                         │
│       └─→ Clinical Decision                                    │
│           ├─ Risk assessment                                   │
│           ├─ Recommendations                                   │
│           └─ Doctor referral                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. BLOOD REPORT PROCESSING

```
Blood Report (JPG/PNG/PDF)
        │
        ▼
┌──────────────────────────────────┐
│   Image Preprocessing            │
│   • Grayscale conversion         │
│   • Denoising                    │
│   • Contrast enhancement         │
│   • Thresholding                 │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   OCR Extraction                 │
│   • Tesseract OCR                │
│   • Extract raw text             │
│   • 85-95% accuracy              │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   Regex Pattern Matching         │
│                                  │
│   Patterns:                      │
│   • cholesterol[:\s]+(\d+)       │
│   • ldl[:\s]+(\d+)               │
│   • hdl[:\s]+(\d+)               │
│   • triglycerides[:\s]+(\d+)     │
│   • blood.sugar[:\s]+(\d+)       │
│   • hba1c[:\s]+(\d+)             │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   Extracted Values               │
│                                  │
│   {                              │
│     "cholesterol": 250,          │
│     "ldl": 180,                  │
│     "hdl": 35,                   │
│     "triglycerides": 200,        │
│     "blood_sugar": 130,          │
│     "hba1c": 7.2                 │
│   }                              │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   Validation                     │
│                                  │
│   ✓ Range checks                 │
│   ✓ Consistency checks           │
│   ✓ Anomaly detection            │
│   ✓ Confidence scoring           │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   Clinical Interpretation        │
│                                  │
│   • High cholesterol risk        │
│   • Elevated blood sugar         │
│   • Diabetes indication          │
│   • Recommendations              │
└──────────────────────────────────┘
```

---

## 3. ECG REPORT PROCESSING

```
ECG Report (JPG/PNG/PDF)
        │
        ▼
┌──────────────────────────────────┐
│   Image Preprocessing            │
│   • Grayscale conversion         │
│   • Denoising                    │
│   • Contrast enhancement         │
│   • Grid detection               │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   Waveform Analysis              │
│                                  │
│   • Detect P wave                │
│   • Detect QRS complex           │
│   • Detect T wave                │
│   • Measure intervals            │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   Parameter Extraction           │
│                                  │
│   • Heart Rate (bpm)             │
│   • PR Interval (ms)             │
│   • QRS Duration (ms)            │
│   • QT Interval (ms)             │
│   • ST Segment (mm)              │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   Abnormality Detection          │
│                                  │
│   • ST Elevation (STEMI)         │
│   • ST Depression (Ischemia)     │
│   • T Wave Inversion             │
│   • Arrhythmias                  │
│   • Heart Block                  │
│   • Hypertrophy                  │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   Risk Assessment                │
│                                  │
│   • Normal: 0.0-0.2              │
│   • Mild: 0.2-0.5                │
│   • Moderate: 0.5-0.8            │
│   • Severe: 0.8-1.0              │
└──────────────────────────────────┘
```

---

## 4. CARDIAC IMAGING PROCESSING

```
Cardiac Image (JPG/PNG)
        │
        ▼
┌──────────────────────────────────┐
│   Image Type Detection           │
│                                  │
│   • X-Ray                        │
│   • Angiography                  │
│   • Echocardiography             │
│   • CT/MRI                       │
└──────────────────────────────────┘
        │
        ├─────────────────┬─────────────────┬──────────────────┐
        │                 │                 │                  │
        ▼                 ▼                 ▼                  ▼
    X-RAY            ANGIOGRAPHY      ECHOCARDIOGRAPHY      CT/MRI
        │                 │                 │                  │
        ▼                 ▼                 ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Detect Cardiac   │ │ Detect       │ │ Detect       │ │ Detect       │
│ Silhouette       │ │ Coronary     │ │ Chamber      │ │ Plaque       │
│                  │ │ Vessels      │ │ Size         │ │ Buildup      │
│ Calculate        │ │              │ │              │ │              │
│ Cardiothoracic   │ │ Identify     │ │ Measure      │ │ Measure      │
│ Ratio            │ │ Blockages    │ │ Wall Motion  │ │ Stenosis     │
│                  │ │              │ │              │ │              │
│ Detect           │ │ Measure      │ │ Assess       │ │ Identify     │
│ Cardiomegaly     │ │ Stenosis %   │ │ Valve        │ │ Affected     │
│                  │ │              │ │ Function     │ │ Vessels      │
│ Detect Pulmonary │ │ Determine    │ │              │ │              │
│ Edema            │ │ Affected     │ │ Calculate    │ │ Calculate    │
│                  │ │ Vessel       │ │ EF           │ │ Risk Score   │
└──────────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │                 │                 │                  │
        └─────────────────┴─────────────────┴──────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   Risk Score Calculation       │
        │                                │
        │   • Normal: 0.0-0.2            │
        │   • Mild: 0.2-0.5              │
        │   • Moderate: 0.5-0.8          │
        │   • Severe: 0.8-1.0            │
        └────────────────────────────────┘
```

---

## 5. MULTI-REPORT FUSION

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Blood Report   │  │  ECG Report     │  │  Cardiac Image  │
│                 │  │                 │  │                 │
│ • Cholesterol   │  │ • Heart Rate    │  │ • Cardiomegaly  │
│ • Blood Sugar   │  │ • ST Segment    │  │ • Vessel Status │
│ • Triglycerides │  │ • Arrhythmias   │  │ • Stenosis      │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │  Fusion Model        │
                    │                      │
                    │  Combines:           │
                    │  • 60% Tabular Data  │
                    │  • 40% Imaging Data  │
                    │                      │
                    │  Weights:            │
                    │  • Blood: 0.4        │
                    │  • ECG: 0.3          │
                    │  • Imaging: 0.3      │
                    └──────────┬───────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │  Final Prediction    │
                    │                      │
                    │  • Probability       │
                    │  • Risk Level        │
                    │  • Confidence        │
                    │  • Recommendations   │
                    └──────────────────────┘
```

---

## 6. ERROR HANDLING FLOW

```
File Upload
    │
    ▼
┌─────────────────────────────┐
│ Validation Failed?          │
└─────────────────────────────┘
    │
    ├─ YES ──→ Invalid file type
    │          Invalid file size
    │          Corrupted file
    │          ↓
    │          Return Error
    │
    └─ NO ──→ Continue
              │
              ▼
        ┌─────────────────────────────┐
        │ OCR Extraction Failed?      │
        └─────────────────────────────┘
              │
              ├─ YES ──→ Poor image quality
              │          Unsupported format
              │          ↓
              │          Return Error
              │
              └─ NO ──→ Continue
                        │
                        ▼
                  ┌─────────────────────────────┐
                  │ Data Validation Failed?     │
                  └─────────────────────────────┘
                        │
                        ├─ YES ──→ Out of range values
                        │          Inconsistent data
                        │          ↓
                        │          Flag for Review
                        │
                        └─ NO ──→ Success
                                  Return Results
```

---

## 7. PROCESSING SPEED COMPARISON

```
Report Type          Processing Time    Accuracy
─────────────────────────────────────────────────
Blood Report (JPG)   2-5 seconds        85-95%
Blood Report (PDF)   5-15 seconds       85-95%
ECG Report (JPG)     3-8 seconds        90-95%
X-Ray (JPG)          5-10 seconds       85-90%
Angiography (JPG)    8-15 seconds       80-90%
Multi-Report         15-30 seconds      85-92%
```

---

## 8. CONFIDENCE LEVELS

```
Prediction Confidence
        │
        ├─ High (> 0.85)
        │  ├─ Use prediction directly
        │  ├─ Probability > 0.85 OR < 0.15
        │  ├─ Ensemble agreement > 90%
        │  └─ Calibration score > 0.9
        │
        ├─ Medium (0.70-0.85)
        │  ├─ Flag for cardiologist review
        │  ├─ Probability 0.70-0.85 OR 0.15-0.30
        │  ├─ Ensemble agreement 70-90%
        │  └─ Recommend consultation
        │
        └─ Low (< 0.70)
           ├─ Reject prediction
           ├─ Probability 0.30-0.70
           ├─ Ensemble agreement < 70%
           └─ Require manual review
```

---

## 9. DATA FLOW SUMMARY

```
INPUT
  ↓
FILE VALIDATION
  ↓
FORMAT CONVERSION (PDF → Images)
  ↓
IMAGE PREPROCESSING
  ├─ Grayscale
  ├─ Denoise
  ├─ Enhance Contrast
  └─ Threshold
  ↓
OCR EXTRACTION
  ├─ Tesseract
  └─ Google Vision (optional)
  ↓
STRUCTURED DATA EXTRACTION
  ├─ Regex Patterns
  ├─ Value Normalization
  └─ Data Cleaning
  ↓
DATA VALIDATION
  ├─ Range Checks
  ├─ Consistency Checks
  └─ Anomaly Detection
  ↓
CLINICAL INTEGRATION
  ├─ Feature Mapping
  ├─ ML Prediction
  ├─ Explanation Generation
  └─ Recommendation
  ↓
OUTPUT
```

---

This visual guide shows how images and PDFs flow through the system from upload to clinical decision!
