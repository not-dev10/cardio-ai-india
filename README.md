# AI-Powered Cardiac Health Assistant Platform for India

## Project Overview
A production-ready healthcare platform that analyzes medical reports (images/PDF), predicts heart disease risk, and recommends nearby doctors and hospitals - specifically tailored for the Indian population.

## Project Timeline (1 Year)

### Stage 1: Foundation & ML Model (Months 1-2) ✓ Current Stage
- Data collection and preprocessing
- Basic ML model development
- Model evaluation and optimization

### Stage 2: Backend API Development (Months 3-4)
- FastAPI REST API
- Model integration
- Basic testing

### Stage 3: Frontend Development (Months 5-6)
- React UI
- Form validation
- Results visualization

### Stage 4: Indian Context & Advanced Features (Months 7-8)
- Custom Indian lifestyle factors
- Personalized recommendations
- ECG integration (optional)

### Stage 5: Database & Authentication (Months 9-10)
- User authentication
- Prediction history
- Data security

### Stage 6: Deployment & Optimization (Months 11-12)
- Docker containerization
- Cloud deployment
- Performance optimization

## Tech Stack

### Machine Learning
- Python 3.9+
- scikit-learn
- XGBoost
- pandas, numpy
- SHAP (explainability)

### OCR & Document Processing
- Tesseract OCR
- pdf2image
- Pillow (PIL)
- Google Cloud Vision API (optional)

### Backend
- FastAPI
- Pydantic
- uvicorn
- SQLAlchemy

### Frontend
- Android (Java)
- Retrofit (API calls)
- Material Design

### Database
- PostgreSQL (production)
- Redis (caching)

### External APIs
- Google Maps API (doctor/hospital search)
- OpenAI API (explanations)
- Infermedica API (optional symptom triage)

### Deployment
- Docker
- AWS EC2
- Nginx
- GitHub Actions (CI/CD)

## Project Structure
```
cardio-ai-india/
├── ml_model/              # ML model development
├── backend/               # FastAPI backend
│   ├── services/          # Business logic
│   │   ├── ocr_service.py
│   │   ├── prediction_service.py
│   │   ├── recommendation_service.py
│   │   └── explanation_service.py
│   ├── models/            # Database models
│   ├── routes/            # API endpoints
│   └── utils/             # Helper functions
├── android_app/           # Android frontend
├── data/                  # Datasets
├── docs/                  # Documentation
├── tests/                 # Test files
├── deployment/            # Docker & deployment configs
└── notebooks/             # Jupyter notebooks for research
```

## Current Stage: Stage 1 Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git

### Setup Instructions (Stage 1)
```bash
# Clone repository
git clone https://github.com/not-dev10/psu-changes.git
cd psu-changes

# Setup Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install ML dependencies
pip install -r ml_model/requirements.txt

# Run initial model training
cd ml_model
python train_model.py
```

## Features

### A. Report Analysis (OCR)
- ⏳ Upload blood reports, ECG reports, angiography reports
- ⏳ OCR extraction (Tesseract + Google Cloud Vision)
- ⏳ Extract: cholesterol, LDL, HDL, triglycerides, BP, sugar
- ⏳ Support images and PDFs
- ⏳ Handle noisy/low-quality inputs

### B. AI Risk Prediction
- ✓ Heart disease risk prediction (Low, Medium, High)
- ✓ Multiple input parameters (age, BP, cholesterol, etc.)
- ✓ Probability scores
- ⏳ Feature importance (explainability)
- ⏳ Key contributing factors

### C. AI Explanation Layer
- ⏳ Convert medical jargon to simple language
- ⏳ India-specific health recommendations
- ⏳ OpenAI API integration for explanations

### D. Doctor & Hospital Recommendations
- ⏳ Location-based search (Google Maps API)
- ⏳ Nearby cardiologists and hospitals
- ⏳ Ratings, distance, contact info
- ⏳ Emergency consultation alerts

### E. Indian Context Features
- ⏳ Indian dietary habits (oil type, consumption patterns)
- ⏳ Stress levels and work patterns
- ⏳ Tobacco/gutka usage
- ⏳ Regional health recommendations
- ⏳ Multi-language support (Hindi, Gujarati)

### F. Security & Compliance
- ⏳ User authentication (JWT)
- ⏳ Prediction history tracking
- ⏳ Data encryption
- ⏳ Medical disclaimer
- ⏳ HIPAA-inspired privacy practices

## License
MIT

## Author
not-dev10

## Project Status
🚀 Stage 1: In Progress
