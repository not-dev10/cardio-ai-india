# Medical-Grade Deployment Guide
## Cardiac Health AI - Production Deployment

---

## PHASE 1: PRE-DEPLOYMENT CHECKLIST (Week 1-2)

### Regulatory & Compliance
- [ ] Ethics board approval obtained
- [ ] DPDP Act compliance certified
- [ ] Data sharing agreements signed with hospitals
- [ ] Informed consent forms prepared
- [ ] Privacy policy reviewed by legal
- [ ] Terms of service finalized

### Clinical Validation
- [ ] Validation study completed (1000+ patients)
- [ ] Sensitivity ≥ 90% verified
- [ ] Specificity ≥ 95% verified
- [ ] AUC ≥ 0.95 verified
- [ ] Cardiologist review completed
- [ ] Clinical validation report signed

### Technical Requirements
- [ ] All unit tests passing (100% coverage)
- [ ] Integration tests passing
- [ ] Security audit completed
- [ ] Performance benchmarks met (< 500ms)
- [ ] Load testing completed (1000 concurrent users)
- [ ] Disaster recovery plan tested

### Documentation
- [ ] User manual completed
- [ ] API documentation complete
- [ ] Training materials prepared
- [ ] Troubleshooting guide created
- [ ] Regulatory documentation packaged
- [ ] Clinical decision support guide ready

---

## PHASE 2: INFRASTRUCTURE SETUP (Week 2-3)

### AWS Infrastructure
```bash
# 1. Create VPC (isolated network)
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# 2. Create RDS PostgreSQL (encrypted)
aws rds create-db-instance \
  --db-instance-identifier cardiac-health-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --storage-encrypted \
  --backup-retention-period 30

# 3. Create S3 bucket (encrypted)
aws s3api create-bucket \
  --bucket cardiac-health-data \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# 4. Create EC2 instances (Multi-AZ)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.large \
  --key-name cardiac-health-key \
  --security-groups cardiac-health-sg \
  --count 2
```

### Security Configuration
```bash
# 1. Create security group
aws ec2 create-security-group \
  --group-name cardiac-health-sg \
  --description "Security group for Cardiac Health AI"

# 2. Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-name cardiac-health-sg \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# 3. Enable VPC Flow Logs
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxxxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs
```

### Database Setup
```sql
-- Create main tables
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) UNIQUE NOT NULL,
    age INT NOT NULL,
    sex INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) NOT NULL,
    predicted_prob FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    patient_id VARCHAR(50),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_patient_id ON predictions(patient_id);
CREATE INDEX idx_created_at ON predictions(created_at);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
```

---

## PHASE 3: APPLICATION DEPLOYMENT (Week 3-4)

### Docker Setup
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/cardiac_health
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=cardiac_health
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:6-alpine
    restart: always

volumes:
  postgres_data:
```

### Deployment Commands
```bash
# 1. Build Docker image
docker build -t cardiac-health:latest .

# 2. Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag cardiac-health:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/cardiac-health:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/cardiac-health:latest

# 3. Deploy to ECS
aws ecs create-service \
  --cluster cardiac-health-cluster \
  --service-name cardiac-health-service \
  --task-definition cardiac-health-task \
  --desired-count 2 \
  --launch-type FARGATE
```

---

## PHASE 4: MONITORING & ALERTING (Week 4)

### CloudWatch Setup
```python
# backend/monitoring/cloudwatch_setup.py
import boto3

cloudwatch = boto3.client('cloudwatch')

# Create custom metrics
cloudwatch.put_metric_alarm(
    AlarmName='HighErrorRate',
    MetricName='ErrorRate',
    Namespace='CardiacHealth',
    Statistic='Average',
    Period=300,
    EvaluationPeriods=2,
    Threshold=5.0,
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=['arn:aws:sns:us-east-1:123456789:alerts']
)

# Monitor prediction latency
cloudwatch.put_metric_alarm(
    AlarmName='HighLatency',
    MetricName='PredictionLatency',
    Namespace='CardiacHealth',
    Statistic='Average',
    Period=60,
    EvaluationPeriods=3,
    Threshold=500,  # 500ms
    ComparisonOperator='GreaterThanThreshold'
)

# Monitor model performance drift
cloudwatch.put_metric_alarm(
    AlarmName='PerformanceDrift',
    MetricName='Sensitivity',
    Namespace='CardiacHealth',
    Statistic='Average',
    Period=3600,
    EvaluationPeriods=1,
    Threshold=0.90,
    ComparisonOperator='LessThanThreshold'
)
```

### Logging Setup
```python
# backend/logging_config.py
import logging
import logging.handlers

# Configure logging
logger = logging.getLogger('cardiac_health')
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.handlers.RotatingFileHandler(
    'logs/cardiac_health.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

# CloudWatch handler
cloudwatch_handler = logging.handlers.WatchedFileHandler('logs/cloudwatch.log')

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

file_handler.setFormatter(formatter)
cloudwatch_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(cloudwatch_handler)
```

---

## PHASE 5: TESTING & VALIDATION (Week 4-5)

### Smoke Tests
```bash
# Test API endpoints
curl -X GET http://localhost:8000/health
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

### Load Testing
```bash
# Using Apache Bench
ab -n 10000 -c 100 http://localhost:8000/health

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/health
```

### Security Testing
```bash
# OWASP ZAP scan
zaproxy -cmd -quickurl http://localhost:8000 -quickout report.html

# SSL/TLS check
nmap --script ssl-enum-ciphers -p 443 localhost
```

---

## PHASE 6: PRODUCTION LAUNCH (Week 5-6)

### Blue-Green Deployment
```bash
# 1. Deploy to green environment
docker-compose -f docker-compose.green.yml up -d

# 2. Run smoke tests on green
./run_smoke_tests.sh http://green-env:8000

# 3. Switch traffic to green
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=green-instance-1 Id=green-instance-2

# 4. Monitor for 24 hours
# If issues, switch back to blue
```

### Canary Release
```bash
# 1. Route 5% traffic to new version
aws elbv2 modify-listener-rule \
  --rule-arn arn:aws:elasticloadbalancing:... \
  --conditions Field=path-pattern,Values="/api/*" \
  --actions Type=forward,TargetGroupArn=arn:...,Weight=5

# 2. Monitor metrics
# 3. Gradually increase to 100%
```

---

## PHASE 7: POST-DEPLOYMENT (Week 6+)

### Daily Monitoring
```
- [ ] Check system uptime (target: 99.9%)
- [ ] Review error logs
- [ ] Monitor prediction latency (target: < 500ms)
- [ ] Check database performance
- [ ] Review user feedback
```

### Weekly Monitoring
```
- [ ] Generate performance report
- [ ] Check for performance drift
- [ ] Review security logs
- [ ] Validate model metrics
- [ ] Check fairness across demographics
```

### Monthly Monitoring
```
- [ ] Full validation study update
- [ ] Regulatory compliance audit
- [ ] Security audit
- [ ] Capacity planning
- [ ] Cost optimization
```

---

## ROLLBACK PROCEDURE

If critical issues occur:

```bash
# 1. Immediate rollback
aws elbv2 modify-listener-rule \
  --rule-arn arn:aws:elasticloadbalancing:... \
  --actions Type=forward,TargetGroupArn=arn:old-version

# 2. Notify stakeholders
# 3. Investigate root cause
# 4. Document incident
# 5. Fix and redeploy
```

---

## COMPLIANCE CHECKLIST

- [ ] DPDP Act compliance verified
- [ ] Data encryption enabled (AES-256)
- [ ] Access control implemented (RBAC)
- [ ] Audit logging enabled
- [ ] Backup & recovery tested
- [ ] Disaster recovery plan tested
- [ ] Security patches applied
- [ ] Penetration testing completed
- [ ] Compliance audit passed

---

## SUCCESS CRITERIA

✓ System uptime ≥ 99.9%
✓ Response time < 500ms (p95)
✓ Sensitivity ≥ 90%
✓ Specificity ≥ 95%
✓ Zero critical security issues
✓ User satisfaction ≥ 4.5/5
✓ Hospital adoption ≥ 80%

---

**This is production. Every decision matters. Every metric is monitored. Every failure is logged.**

Deploy with confidence. Monitor with vigilance. Improve continuously.
