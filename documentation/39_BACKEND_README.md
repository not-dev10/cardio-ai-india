# Backend API - Cardiac Health Assistant

## Overview
FastAPI backend with OCR, ML prediction, and healthcare recommendations.

## Features
- Medical report OCR (images and PDFs)
- Heart disease risk prediction
- AI-powered explanations
- Doctor and hospital recommendations
- Location-based services

## Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

#### Windows
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
Add to PATH: `C:\Program Files\Tesseract-OCR`

#### Linux
```bash
sudo apt-get install tesseract-ocr
```

#### Mac
```bash
brew install tesseract
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run Server
```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check
```
GET /health
```

### Predict Risk (Manual Input)
```
POST /api/v1/predict
Content-Type: application/json

{
  "age": 55,
  "sex": 1,
  "chest_pain_type": 2,
  "resting_bp": 140,
  "cholesterol": 250,
  ...
}
```

### Upload Medical Report
```
POST /api/v1/upload-report
Content-Type: multipart/form-data

file: <image or PDF>
report_type: blood
```

### Predict from Report
```
POST /api/v1/predict-from-report
Content-Type: multipart/form-data

file: <blood report>
age: 55
sex: 1
smoking: 0
diabetes: 0
```

### Find Nearby Doctors
```
POST /api/v1/find-doctors
Content-Type: application/json

{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "risk_level": "High"
}
```

## API Documentation
Once server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Test OCR Service
```bash
python services/ocr_service.py
```

### Test Explanation Service
```bash
python services/explanation_service.py
```

### Test Recommendation Service
```bash
python services/recommendation_service.py
```

## Project Structure
```
backend/
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── .env.example           # Environment template
├── services/              # Business logic
│   ├── ocr_service.py
│   ├── explanation_service.py
│   └── recommendation_service.py
├── models/                # Database models (future)
├── routes/                # API routes (future)
└── uploads/               # Temporary file storage
```

## Next Steps
- Add user authentication (JWT)
- Implement database (PostgreSQL)
- Add prediction history
- Implement caching (Redis)
- Add rate limiting
- Write unit tests
