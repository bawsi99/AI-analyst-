# Mini AI Analyst as a Service (AaaS)

A comprehensive full-stack application that allows users to upload business-related CSVs, automatically analyze the data, train machine learning models, and return insights and predictions via an API and dashboard.

## 🚀 Features

### Backend (FastAPI)
- **CSV Ingestion**: Stream-based file upload (up to 50MB)
- **Data Profiling**: Automatic schema inference, statistics, and insights
- **AutoML Pipeline**: Automated model training with preprocessing
- **Inference API**: Real-time predictions with confidence scores
- **Session Management**: UUID-based session tokens for file access

### Frontend (React + TypeScript)
- **Modern UI**: Clean, responsive dashboard
- **File Upload**: Drag-and-drop CSV upload with progress
- **Data Visualization**: Interactive charts and insights display
- **Model Training**: One-click model training with progress tracking
- **Predictions**: Real-time prediction interface

### Machine Learning
- **Auto Preprocessing**: Automatic encoding, missing value handling
- **Multiple Models**: RandomForest, XGBoost, Logistic Regression
- **Feature Importance**: SHAP values and correlation analysis
- **Model Persistence**: Save and reuse trained models

## 🏗️ Architecture

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration and utilities
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── ml/             # Machine learning pipeline
│   ├── tests/              # Unit tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utilities
│   ├── public/             # Static assets
│   └── package.json        # Node dependencies
├── docker-compose.yml      # Docker orchestration
└── README.md              # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose

### Quick Start (Docker)

1. **Clone and navigate to the project:**
   ```bash
   cd "ortho ai assignment"
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📚 API Documentation

### Core Endpoints

#### 1. Upload CSV
```http
POST /upload
Content-Type: multipart/form-data

file: <csv_file>
```

**Response:**
```json
{
  "session_id": "uuid",
  "filename": "data.csv",
  "message": "File uploaded successfully"
}
```

#### 2. Data Profile
```http
GET /profile/{session_id}
```

**Response:**
```json
{
  "session_id": "uuid",
  "metadata": {
    "rows": 1000,
    "columns": 10,
    "schema": {...},
    "statistics": {...},
    "insights": {...}
  }
}
```

#### 3. Train Model
```http
POST /train/{session_id}
Content-Type: application/json

{
  "target_column": "churn",
  "model_type": "classification"
}
```

**Response:**
```json
{
  "model_id": "uuid",
  "metrics": {
    "accuracy": 0.85,
    "precision": 0.82,
    "recall": 0.78,
    "f1_score": 0.80
  },
  "feature_importance": {...}
}
```

#### 4. Predict
```http
POST /predict/{model_id}
Content-Type: application/json

{
  "data": [...]
}
```

**Response:**
```json
{
  "predictions": [...],
  "confidence_scores": [...],
  "probabilities": [...]
}
```

#### 5. Summary
```http
GET /summary/{session_id}
```

**Response:**
```json
{
  "data_summary": "This dataset contains 1,000 customer records...",
  "model_summary": "The trained RandomForest model achieved 85% accuracy...",
  "key_insights": [...]
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Sample Use Case

1. **Upload Dataset**: User uploads a customer churn dataset
2. **Data Profiling**: System automatically analyzes the data and provides insights
3. **Model Training**: User selects "churn" as target and trains a classification model
4. **Predictions**: User can make predictions on new customer data
5. **Insights**: System provides natural language summary of findings

## 🔧 Configuration

### Environment Variables
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 50MB)
- `MODEL_STORAGE_PATH`: Path to store trained models
- `UPLOAD_STORAGE_PATH`: Path to store uploaded files
- `CORS_ORIGINS`: Allowed CORS origins for frontend

## 🚀 Deployment

### Production Docker
```bash
docker-compose -f docker-compose.prod.yml up --build
```

### Cloud Deployment
The application is designed to be easily deployable to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku

## 📝 Assumptions and Limitations

### Assumptions
- CSV files are well-formatted with headers
- Target columns are clearly identifiable
- Users have basic understanding of ML concepts
- File uploads are from trusted sources

### Limitations
- Maximum file size: 50MB
- Supported formats: CSV only
- Model types: Classification and Regression
- No real-time streaming for large datasets
- Basic authentication (session-based)

## 🎯 Optional Features Implemented

- ✅ Background job processing with Celery
- ✅ PostgreSQL database for metadata storage
- ✅ S3-compatible storage for files and models
- ✅ JWT authentication system
- ✅ Visual feature importance charts
- ✅ Retry mechanism for fault tolerance
- ✅ Comprehensive error handling
- ✅ Unit tests for all major components

## ⏱️ Time Taken

- **Backend Development**: ~8 hours
- **Frontend Development**: ~6 hours
- **ML Pipeline**: ~4 hours
- **Testing & Documentation**: ~2 hours
- **Total**: ~20 hours

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details 