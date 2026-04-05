# Multi-stage Dockerfile for production deployment

# Stage 1: Base image with dependencies
FROM python:3.9-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Stage 2: ML Model
FROM base as ml-model

# Copy ML model requirements
COPY ml_model/requirements.txt /app/ml_model/
RUN pip install --no-cache-dir -r ml_model/requirements.txt

# Copy ML model code
COPY ml_model/ /app/ml_model/

# Stage 3: Backend
FROM ml-model as backend

# Copy backend requirements
COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Create uploads directory
RUN mkdir -p /app/backend/uploads

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
