# Ultra Model - Quick Reference

## 🎯 Key Numbers

| Metric | Value |
|--------|-------|
| **AUC** | 98.07% |
| **Accuracy** | 94.4% |
| **Recall** | 90.1% |
| **Precision** | 93.3% |
| **F1-Score** | 91.7% |
| **MCC** | 0.8743 |
| **Kappa** | 0.8739 |

## 📁 Files

| File | Purpose |
|------|---------|
| `models/heart_disease_model_ultra.joblib` | Main model |
| `models/scaler_ultra.joblib` | Data scaler |
| `predict.py` | Prediction API |

## 🚀 Quick Start

```python
from predict import HeartDiseasePredictor

predictor = HeartDiseasePredictor()
result = predictor.predict({
    "age": 55, "sex": 1, "chest_pain_type": 2,
    "resting_bp": 140, "cholesterol": 250,
    "fasting_blood_sugar": 1, "resting_ecg": 1,
    "max_heart_rate": 150, "exercise_induced_angina": 0,
    "st_depression": 1.5, "st_slope": 1,
    "num_major_vessels": 1, "thalassemia": 2
})

print(f"Risk: {result['risk_level']}")
print(f"Probability: {result['probability']:.2%}")
```

## 🏗️ Architecture

- **5 Base Models**: XGBoost, RF, GB, ExtraTrees, AdaBoost
- **Meta-Learner**: LogisticRegression
- **Calibration**: Platt Sigmoid
- **Features**: 18 (13 original + 5 engineered)

## ⚙️ Configuration

- **Optimal Threshold**: 0.445
- **Training Samples**: 5,401
- **Test Samples**: 1,081
- **Training Time**: ~5 minutes

## 📊 Confusion Matrix

```
                Predicted
              Healthy  Disease
Actual Healthy   685      24
       Disease    37     335
```

## ✅ What's Included

- ✅ Stacking ensemble (5 base models)
- ✅ Feature engineering (6 new features)
- ✅ Outlier removal (168 samples)
- ✅ Advanced scaling (QuantileTransformer)
- ✅ Platt calibration
- ✅ Threshold optimization

## 🎯 Performance

- **Disease Detection**: 90.1% (335/372 caught)
- **False Alarm Rate**: 3.4% (24/709)
- **Specificity**: 96.6%
- **Sensitivity**: 90.1%

## 📝 Usage

```bash
# Test model
cd ml_model
python predict.py

# Use in code
from predict import HeartDiseasePredictor
predictor = HeartDiseasePredictor()
result = predictor.predict(data)
```

## 🚀 Deployment

1. Copy model files to backend
2. Update backend config
3. Test predictions
4. Deploy to production

## 📞 Support

- Model not loading? Check file paths
- Wrong predictions? Verify input features
- Performance issues? Check data quality

---

**Status**: ✅ Production Ready
**Performance**: 98.07% AUC
**Next**: Deploy to backend

