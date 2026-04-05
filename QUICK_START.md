# Quick Start Guide - Cardiac Health AI Platform

## 🚀 Get Started in 30 Minutes

### Prerequisites
- Python 3.9+
- Git
- Tesseract OCR
- (Optional) OpenAI API key
- (Optional) Google Maps API key

---

## Step 1: Clone and Setup (5 minutes)

```bash
# Clone repository
git clone https://github.com/not-dev10/psu-changes.git
cd psu-changes

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

---

## Step 2: Install Dependencies (5 minutes)

### ML Model Dependencies
```bash
cd ml_model
pip install -r requirements.txt
cd ..
```

### Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

---

## Step 3: Install Tesseract OCR (5 minutes)

### Windows
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH

### Linux
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Mac
```bash
brew install tesseract
```

---

## Step 4: Download Dataset (5 minutes)

### Option 1: UCI Heart Disease Dataset
1. Visit: https://archive.ics.uci.edu/ml/datasets/heart+disease
2. Download: `processed.cleveland.data`
3. Save as: `ml_model/data/heart_disease_data.csv`

### Option 2: Kaggle Dataset
1. Visit: https://www.kaggle.com/datasets/johnsmith88/heart-disease-dataset
2. Download: `heart.csv`
3. Save as: `ml_model/data/heart_disease_data.csv`

---

## Step 5: Train ML Model (5 minutes)

```bash
cd ml_model

# Train basic models
python train_model.py

# Or train advanced ensemble model
python advanced_training.py
```

Expected output:
```
Training XGBoost model...
Training Random Forest model...
Training Logistic Regression model...
Ensemble model trained!
Recall: 0.95 ✅
Model saved to models/indian_cardiac_ensemble_v1.joblib
```

---

## Step 6: Test Services (5 minutes)

### Test ML Prediction
```bash
cd ml_model
python predict.py
```

### Test OCR Service
```bash
cd backend/services
python ocr_service.py
```

### Test Advanced OCR
```bash
python advanced_ocr_service.py
```

### Test Explanation Service
```bash
python explanation_service.py
```

---

## Step 7: Setup API Keys (Optional)

```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/cardio_db
```

---

## Step 8: Run Backend Server (5 minutes)

```bash
cd backend
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload
```

Server will start at: http://localhost:8000

---

## Step 9: Test API (5 minutes)

### Open API Documentation
Visit: http://localhost:8000/docs

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

### Test Prediction
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55,
    "sex": 1,
    "chest_pain_type": 2,
    "resting_bp": 140,
    "cholesterol": 250,
    "fasting_blood_sugar": 1,
    "resting_ecg": 1,
    "max_heart_rate": 150,
    "exercise_induced_angina": 0,
    "st_depression": 1.5,
    "st_slope": 1,
    "num_major_vessels": 1,
    "thalassemia": 2
  }'
```

---

## 🎉 You're Ready!

### What You Have Now
✅ ML model trained and ready
✅ OCR service configured
✅ Backend API running
✅ All services tested

### Next Steps
1. **Collect sample medical reports** for OCR testing
2. **Get API keys** (OpenAI, Google Maps) for full functionality
3. **Start Android app development** (see android_app/README.md)
4. **Setup database** (PostgreSQL) for production
5. **Deploy to cloud** (AWS EC2) when ready

---

## 📖 Documentation

- **Full Roadmap**: See `UPDATED_ROADMAP.md`
- **Production Summary**: See `PRODUCTION_READY_SUMMARY.md`
- **Critical Gaps**: See `docs/CRITICAL_GAPS_AND_SOLUTIONS.md`
- **Dataset Strategy**: See `docs/DATASET_STRATEGY.md`
- **ML Model**: See `ml_model/README.md`
- **Backend API**: See `backend/README.md`

---

## 🐛 Troubleshooting

### Issue: Tesseract not found
**Solution**: 
```python
# In ocr_service.py, uncomment and set path:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Issue: Model not found
**Solution**: Train the model first:
```bash
cd ml_model
python train_model.py
```

### Issue: Import errors
**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

### Issue: Dataset not found
**Solution**: Download dataset and place in `ml_model/data/heart_disease_data.csv`

---

## 💬 Need Help?

- **GitHub Issues**: https://github.com/not-dev10/psu-changes/issues
- **Documentation**: Check README files in each directory
- **Email**: [Your Email]

---

## 🎯 Quick Commands Reference

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Train model
cd ml_model && python train_model.py

# Run backend
cd backend && python main.py

# Test prediction
cd ml_model && python predict.py

# Test OCR
cd backend/services && python advanced_ocr_service.py

# View API docs
# Open browser: http://localhost:8000/docs
```

---

**Happy Coding! Ganpati Bapa Morya!** 🙏
