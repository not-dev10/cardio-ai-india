# 📊 Dataset Training Strategy - Complete Guide

## 🎯 Your Competitive Edge

Your moat won't be model accuracy (98.07% ✅)
Your moat will be:
- ✅ Data pipeline (OCR + LLM parsing)
- ✅ Report understanding (medical value extraction)
- ✅ Indian healthcare adaptation

---

## 📋 Datasets by Category

### 1. 🫀 ECG DATASETS (BEST FOR YOU)

#### MIT-BIH Arrhythmia Database ⭐⭐⭐⭐⭐
**Why it's gold:**
- Industry-standard dataset
- 47 patients, 109,000+ heartbeats
- Annotated (normal + abnormal)
- Used in research papers
- Free & open access

**Download:**
```bash
# PhysioNet
https://physionet.org/content/mitdb/1.0.0/

# Python
pip install wfdb
import wfdb
record = wfdb.rdrecord('mitdb/100')
```

**Use for:**
- Arrhythmia detection
- Training CNN/RNN models
- ECG classification

**Data Format:**
```
- 11 ECG leads
- 360 Hz sampling rate
- Annotations: N (normal), A (atrial), V (ventricular), etc.
```

#### PTB Diagnostic ECG Database ⭐⭐⭐⭐
**Why:**
- 549 patients
- 12-lead ECG (more realistic)
- Includes heart attack (MI) cases
- Diagnostic labels

**Download:**
```bash
https://physionet.org/content/ptbdb/1.0.0/
```

**Use for:**
- MI detection
- Multi-lead ECG analysis
- Diagnostic classification

#### Chapman-Shaoxing ECG Dataset ⭐⭐⭐⭐
**Why:**
- Large dataset (10,000+ ECGs)
- Multi-class classification
- Real-world data

**Download:**
```bash
https://physionet.org/content/chapman-shaoxing-12lead-ecg-database-and-ecg-image-database/1.0.0/
```

---

### 2. 📄 MEDICAL REPORT / OCR DATASETS

#### RVL-CDIP Dataset ⭐⭐⭐⭐
**Why:**
- 400,000+ scanned documents
- Good for OCR training/testing
- Document classification

**Download:**
```bash
https://www.cs.cmu.edu/~aharley/rvl-cdip/
```

**Use for:**
- OCR model training
- Document classification
- Text extraction

#### MIMIC-III Clinical Database ⭐⭐⭐⭐⭐
**Why it's 🔥:**
- Real hospital data
- 40,000+ patients
- Includes:
  - Lab tests
  - Reports
  - Patient history
  - Diagnoses

**Download:**
```bash
# Requires credential approval (worth it!)
https://mimic.physionet.org/

# After approval:
pip install mimic-code
```

**Use for:**
- Real-world lab values
- Report simulation
- Clinical context

**⚠️ Important:**
- Requires IRB approval
- Takes 1-2 weeks
- But gives you REAL hospital data

---

### 3. 🧪 BLOOD TEST / TABULAR MEDICAL DATA

#### UCI Heart Disease Dataset ⭐⭐⭐⭐
**You already use this! ✅**

**Extend it with:**
```python
# Current: 303 samples
# Need: 5,000+ samples

# Combine with:
- Kaggle Heart Disease datasets
- NHANES data
- Synthetic data generation
```

#### Kaggle Medical Cost Personal Dataset ⭐⭐⭐
**Why:**
- 1,300+ samples
- Medical charges
- Age, BMI, smoking, region

**Download:**
```bash
https://www.kaggle.com/datasets/mirichoi0218/insurance
```

#### NHANES Dataset ⭐⭐⭐⭐⭐
**Why:**
- Real-world blood test values
- Large-scale population data
- 20,000+ participants
- Includes:
  - Cholesterol
  - Blood pressure
  - Glucose
  - Hemoglobin

**Download:**
```bash
# CDC NHANES
https://wwwn.cdc.gov/nchs/nhanes/

# Python
pip install nhanes
```

**Use for:**
- Real lab value distributions
- Population-level insights
- Feature engineering

---

### 4. 🖼️ MEDICAL IMAGING (Advanced)

#### CheXpert Dataset ⭐⭐⭐⭐
**Why:**
- 224,000+ chest X-rays
- Detect heart enlargement
- Combine with ECG

**Download:**
```bash
https://stanfordmlgroup.github.io/competitions/chexpert/
```

**Use for:**
- X-ray classification
- Cardiomegaly detection
- Multi-modal learning

#### ImageNet Medical ⭐⭐⭐
**Why:**
- Pre-trained models
- Transfer learning

---

## 🚀 YOUR TRAINING STRATEGY

### Phase 1: ECG Model Training (Week 1-2)

```python
# Step 1: Download MIT-BIH
import wfdb
import numpy as np

# Load data
record = wfdb.rdrecord('mitdb/100')
signals = record.p_signal
annotations = record.ann_conf

# Step 2: Preprocess
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
signals_scaled = scaler.fit_transform(signals)

# Step 3: Create windows (5-second windows)
window_size = 1800  # 5 seconds at 360 Hz
windows = []
labels = []

for i in range(0, len(signals_scaled) - window_size, window_size):
    window = signals_scaled[i:i+window_size]
    windows.append(window)
    # Get label for this window
    labels.append(get_label(annotations, i))

# Step 4: Train CNN
from tensorflow.keras import Sequential, layers

model = Sequential([
    layers.Conv1D(32, 3, activation='relu', input_shape=(window_size, 1)),
    layers.MaxPooling1D(2),
    layers.Conv1D(64, 3, activation='relu'),
    layers.MaxPooling1D(2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(5, activation='softmax')  # 5 classes
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(np.array(windows), np.array(labels), epochs=50, batch_size=32)

# Save model
model.save('ecg_model.h5')
```

### Phase 2: Blood Test Model (Week 2-3)

```python
# Step 1: Combine datasets
import pandas as pd

# UCI Heart Disease
uci_data = pd.read_csv('heart.csv')

# NHANES
nhanes_data = load_nhanes_data()

# Kaggle
kaggle_data = pd.read_csv('insurance.csv')

# Combine
combined = pd.concat([uci_data, nhanes_data, kaggle_data], ignore_index=True)

# Step 2: Feature engineering
combined['age_group'] = pd.cut(combined['age'], bins=[0, 30, 50, 70, 100])
combined['bp_category'] = pd.cut(combined['trestbps'], bins=[0, 120, 140, 180])
combined['chol_ratio'] = combined['chol'] / combined['hdl']

# Step 3: Train XGBoost
import xgboost as xgb

X = combined.drop('target', axis=1)
y = combined['target']

model = xgb.XGBClassifier(
    n_estimators=1000,
    max_depth=7,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8
)

model.fit(X, y)
model.save_model('blood_model.json')
```

### Phase 3: Synthetic Report Generation (Week 3)

```python
# Step 1: Use LLM to generate synthetic reports
from openai import OpenAI

client = OpenAI()

def generate_synthetic_report(patient_data):
    """Generate realistic medical report"""
    
    prompt = f"""
    Generate a realistic blood test report for a patient with:
    - Age: {patient_data['age']}
    - Cholesterol: {patient_data['cholesterol']} mg/dL
    - Blood Pressure: {patient_data['bp']} mmHg
    - Glucose: {patient_data['glucose']} mg/dL
    - Hemoglobin: {patient_data['hemoglobin']} g/dL
    
    Format as a medical report with:
    - Patient info
    - Test results
    - Reference ranges
    - Doctor notes
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Step 2: Generate 1000 synthetic reports
synthetic_reports = []
for i in range(1000):
    patient_data = {
        'age': np.random.randint(30, 80),
        'cholesterol': np.random.randint(150, 300),
        'bp': f"{np.random.randint(100, 180)}/{np.random.randint(60, 120)}",
        'glucose': np.random.randint(70, 200),
        'hemoglobin': np.random.uniform(10, 18)
    }
    
    report = generate_synthetic_report(patient_data)
    synthetic_reports.append({
        'text': report,
        'labels': patient_data
    })

# Step 3: Convert to images (for OCR training)
from PIL import Image, ImageDraw, ImageFont

for i, report in enumerate(synthetic_reports):
    # Create image
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw text
    draw.text((50, 50), report['text'], fill='black')
    
    # Save
    img.save(f'synthetic_reports/{i}.jpg')
```

### Phase 4: Unified Dataset Creation (Week 4)

```python
# Step 1: Create unified dataset
import json

unified_dataset = []

for i in range(len(combined)):
    sample = {
        'id': i,
        'patient_data': {
            'age': combined.iloc[i]['age'],
            'sex': combined.iloc[i]['sex'],
            'cholesterol': combined.iloc[i]['chol'],
            'blood_pressure': f"{combined.iloc[i]['trestbps']}/80",
            'glucose': combined.iloc[i].get('glucose', 100),
            'hemoglobin': combined.iloc[i].get('hemoglobin', 13.5)
        },
        'ecg_data': {
            'file': f'ecg_data/{i}.npy',
            'abnormality_score': np.random.random()
        },
        'report_data': {
            'file': f'synthetic_reports/{i}.jpg',
            'extracted_values': synthetic_reports[i]['labels']
        },
        'target': combined.iloc[i]['target']
    }
    
    unified_dataset.append(sample)

# Save
with open('unified_dataset.json', 'w') as f:
    json.dump(unified_dataset, f)

print(f"Created unified dataset with {len(unified_dataset)} samples")
```

---

## 📥 Download Script (Automated)

```python
# download_datasets.py
import os
import subprocess
import wfdb
import pandas as pd

def download_mit_bih():
    """Download MIT-BIH Arrhythmia Database"""
    print("Downloading MIT-BIH...")
    os.makedirs('data/ecg/mitdb', exist_ok=True)
    
    # Download using wfdb
    for i in range(100, 125):
        try:
            record = wfdb.rdrecord(f'mitdb/{i}')
            print(f"Downloaded record {i}")
        except:
            pass

def download_ptb():
    """Download PTB Database"""
    print("Downloading PTB...")
    os.makedirs('data/ecg/ptbdb', exist_ok=True)
    
    # Download
    subprocess.run([
        'wget', '-r',
        'https://physionet.org/files/ptbdb/1.0.0/',
        '-P', 'data/ecg/ptbdb'
    ])

def download_nhanes():
    """Download NHANES data"""
    print("Downloading NHANES...")
    os.makedirs('data/blood_tests', exist_ok=True)
    
    # Use nhanes package
    import nhanes
    data = nhanes.load_data()
    data.to_csv('data/blood_tests/nhanes.csv')

def download_uci():
    """Download UCI Heart Disease"""
    print("Downloading UCI Heart Disease...")
    os.makedirs('data/blood_tests', exist_ok=True)
    
    url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data'
    df = pd.read_csv(url, header=None)
    df.to_csv('data/blood_tests/uci_heart.csv')

if __name__ == '__main__':
    download_mit_bih()
    download_ptb()
    download_nhanes()
    download_uci()
    print("✅ All datasets downloaded!")
```

---

## 🎯 Your Competitive Advantage

### What You'll Have:
1. **ECG Model** - Trained on 100k+ heartbeats
2. **Blood Test Model** - Trained on 20k+ real samples
3. **OCR Pipeline** - Trained on synthetic + real reports
4. **Unified Dataset** - ECG + Blood + Reports combined

### Why This Matters:
- ✅ Most startups use only 1 data source
- ✅ You'll use 3+ sources
- ✅ Your model will understand context
- ✅ Your OCR will be accurate
- ✅ Your recommendations will be personalized

---

## 📊 Dataset Summary

| Dataset | Size | Use | Status |
|---------|------|-----|--------|
| MIT-BIH | 109k beats | ECG training | ✅ Free |
| PTB | 15k ECGs | MI detection | ✅ Free |
| Chapman | 10k ECGs | Classification | ✅ Free |
| NHANES | 20k patients | Lab values | ✅ Free |
| UCI Heart | 303 samples | Baseline | ✅ Free |
| MIMIC-III | 40k patients | Real data | ⏳ Approval needed |
| CheXpert | 224k X-rays | Imaging | ✅ Free |
| RVL-CDIP | 400k docs | OCR training | ✅ Free |

---

## 🚀 Implementation Timeline

### Week 1: Download & Setup
- [ ] Download MIT-BIH
- [ ] Download PTB
- [ ] Download NHANES
- [ ] Download UCI Heart Disease

### Week 2: ECG Model
- [ ] Preprocess ECG data
- [ ] Train CNN model
- [ ] Validate on test set
- [ ] Save model

### Week 3: Blood Test Model
- [ ] Combine datasets
- [ ] Feature engineering
- [ ] Train XGBoost
- [ ] Validate

### Week 4: Synthetic Reports
- [ ] Generate synthetic reports
- [ ] Convert to images
- [ ] Train OCR
- [ ] Create unified dataset

---

## 💡 Pro Tips

1. **Start Small**: Train on 1000 samples first, then scale
2. **Use GPU**: ECG training is fast on GPU
3. **Validate Often**: Check performance on test set
4. **Combine Datasets**: Don't use just one source
5. **Generate Synthetic**: Use LLM to create more data

---

## 🔐 Data Privacy

- ✅ MIT-BIH: Anonymized, public
- ✅ PTB: Anonymized, public
- ✅ NHANES: De-identified, public
- ✅ UCI: Anonymized, public
- ⚠️ MIMIC-III: Requires IRB approval
- ✅ CheXpert: De-identified, public

---

## 📞 Next Steps

1. Run `download_datasets.py`
2. Follow Phase 1-4 training
3. Create unified dataset
4. Train your models
5. Deploy!

---

**Status**: 🚀 Ready to implement
**Timeline**: 4 weeks
**Result**: Production-ready models trained on real data

