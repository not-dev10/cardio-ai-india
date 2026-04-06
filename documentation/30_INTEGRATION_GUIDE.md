# 🔗 Integration Guide - Advanced Architecture

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create `.env` file in backend directory:
```
OPENAI_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
GOOGLE_CLOUD_CREDENTIALS=path/to/credentials.json
```

### 3. Run Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

---

## API Integration Examples

### Python Client
```python
import requests
import json

BASE_URL = "http://localhost:8000"

class CardiacAIClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def analyze_complete_report(self, blood_report_path, age=50, sex=1, 
                               ecg_path=None, xray_path=None, angio_path=None):
        """Analyze complete medical report with images"""
        files = {
            'blood_report': open(blood_report_path, 'rb')
        }
        
        if ecg_path:
            files['ecg_image'] = open(ecg_path, 'rb')
        if xray_path:
            files['xray_image'] = open(xray_path, 'rb')
        if angio_path:
            files['angio_image'] = open(angio_path, 'rb')
        
        data = {'age': age, 'sex': sex}
        
        response = requests.post(
            f"{self.base_url}/api/v2/analyze-complete-report",
            files=files,
            data=data
        )
        
        return response.json()
    
    def process_image(self, image_path, image_type='ecg'):
        """Process cardiac image"""
        files = {'file': open(image_path, 'rb')}
        data = {'image_type': image_type}
        
        response = requests.post(
            f"{self.base_url}/api/v2/process-cardiac-image",
            files=files,
            data=data
        )
        
        return response.json()
    
    def explain_prediction(self, patient_data):
        """Get SHAP explanation for prediction"""
        response = requests.post(
            f"{self.base_url}/api/v2/explain-prediction",
            json=patient_data
        )
        
        return response.json()

# Usage
client = CardiacAIClient()

# Analyze complete report
result = client.analyze_complete_report(
    blood_report_path='blood_report.jpg',
    age=55,
    sex=1,
    ecg_path='ecg.jpg',
    xray_path='xray.jpg'
)

print(f"Risk Score: {result['fusion_score']:.3f}")
print(f"Risk Level: {result['risk_level']}")
print("\nTop Risk Factors:")
for exp in result['explanations']['explanations'][:3]:
    print(f"  • {exp['impact']}")
```

### JavaScript/React Client
```javascript
const BASE_URL = 'http://localhost:8000';

class CardiacAIClient {
  async analyzeCompleteReport(bloodReport, age, sex, ecgImage, xrayImage, angioImage) {
    const formData = new FormData();
    formData.append('blood_report', bloodReport);
    formData.append('age', age);
    formData.append('sex', sex);
    
    if (ecgImage) formData.append('ecg_image', ecgImage);
    if (xrayImage) formData.append('xray_image', xrayImage);
    if (angioImage) formData.append('angio_image', angioImage);
    
    const response = await fetch(
      `${BASE_URL}/api/v2/analyze-complete-report`,
      {
        method: 'POST',
        body: formData
      }
    );
    
    return response.json();
  }
  
  async processImage(imageFile, imageType = 'ecg') {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('image_type', imageType);
    
    const response = await fetch(
      `${BASE_URL}/api/v2/process-cardiac-image`,
      {
        method: 'POST',
        body: formData
      }
    );
    
    return response.json();
  }
  
  async explainPrediction(patientData) {
    const response = await fetch(
      `${BASE_URL}/api/v2/explain-prediction`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(patientData)
      }
    );
    
    return response.json();
  }
}

// Usage in React
import React, { useState } from 'react';

function CardiacAnalysis() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const client = new CardiacAIClient();
  
  const handleAnalyze = async (files) => {
    setLoading(true);
    try {
      const result = await client.analyzeCompleteReport(
        files.bloodReport,
        55,
        1,
        files.ecgImage,
        files.xrayImage,
        files.angioImage
      );
      setResult(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
    setLoading(false);
  };
  
  return (
    <div>
      <h1>Cardiac Health Analysis</h1>
      {loading && <p>Analyzing...</p>}
      {result && (
        <div>
          <h2>Risk Score: {result.fusion_score.toFixed(3)}</h2>
          <p>Risk Level: {result.risk_level}</p>
          <h3>Top Risk Factors:</h3>
          <ul>
            {result.explanations.explanations.map((exp, i) => (
              <li key={i}>{exp.impact}</li>
            ))}
          </ul>
          <h3>Recommendations:</h3>
          <ul>
            {result.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default CardiacAnalysis;
```

---

## Docker Deployment

### Build Image
```bash
docker build -f deployment/Dockerfile -t cardiac-ai:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e GOOGLE_MAPS_API_KEY=your_key \
  -v /path/to/uploads:/app/uploads \
  cardiac-ai:latest
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: deployment/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_MAPS_API_KEY=${GOOGLE_MAPS_API_KEY}
    volumes:
      - ./uploads:/app/uploads
    networks:
      - cardiac-network

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
    networks:
      - cardiac-network

networks:
  cardiac-network:
    driver: bridge
```

---

## Testing

### Unit Tests
```python
import pytest
from backend.services.image_processor import CardiacImageProcessor
from backend.services.fusion_model import FusionModelService

def test_image_processor():
    processor = CardiacImageProcessor()
    # Test with sample image
    result = processor.process_image('test_ecg.jpg', 'ecg')
    assert result.abnormality_score >= 0
    assert result.abnormality_score <= 1

def test_fusion_model():
    fusion = FusionModelService()
    import numpy as np
    
    tabular = np.array([[55, 1, 3, 140, 250, 1, 0, 85, 0, 2.5, 1, 0, 2]])
    predictions = fusion.predict(tabular)
    
    assert 'fusion' in predictions
    assert predictions['fusion'] >= 0
    assert predictions['fusion'] <= 1

# Run tests
pytest tests/
```

### Integration Tests
```bash
# Test all endpoints
python tests/test_integration.py

# Test with sample data
curl -X POST http://localhost:8000/api/v2/explain-prediction \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55,
    "sex": 1,
    "chest_pain_type": 3,
    "resting_bp": 140,
    "cholesterol": 250,
    "fasting_blood_sugar": 1,
    "resting_ecg": 0,
    "max_heart_rate": 85,
    "exercise_induced_angina": 0,
    "st_depression": 2.5,
    "st_slope": 1,
    "num_major_vessels": 0,
    "thalassemia": 2
  }'
```

---

## Monitoring & Logging

### Enable Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cardiac_ai.log'),
        logging.StreamHandler()
    ]
)
```

### Monitor Performance
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper
```

---

## Troubleshooting

### Issue: OCR not extracting text
**Solution**: 
- Check image quality
- Try different OCR method (EasyOCR vs PaddleOCR)
- Preprocess image (contrast, rotation)

### Issue: Image processing slow
**Solution**:
- Enable GPU acceleration
- Reduce image resolution
- Use async processing

### Issue: SHAP explanations not working
**Solution**:
- Install SHAP: `pip install shap`
- Check model compatibility
- Use fallback explanation method

### Issue: API timeout
**Solution**:
- Increase timeout in client
- Process large files asynchronously
- Use message queue (Celery)

---

## Performance Optimization

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_model_prediction(features_tuple):
    # Cached predictions
    pass
```

### Async Processing
```python
from fastapi import BackgroundTasks

@app.post("/api/v2/analyze-async")
async def analyze_async(file: UploadFile, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_report, file)
    return {"status": "processing"}
```

### Database Caching
```python
# Cache results in database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://user:password@localhost/cardiac_ai')
Session = sessionmaker(bind=engine)
```

---

## Production Checklist

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] API keys set up
- [ ] Database initialized
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Security hardened
- [ ] Rate limiting enabled
- [ ] CORS configured
- [ ] SSL/TLS enabled
- [ ] Backup strategy in place
- [ ] Disaster recovery plan
- [ ] Documentation complete
- [ ] Team trained

---

**Ready to Deploy!** 🚀

