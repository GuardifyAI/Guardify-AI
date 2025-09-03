# 🛡️ Guardify-AI: Advanced Surveillance & Shoplifting Detection System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![React](https://img.shields.io/badge/react-19.1.0-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.8.3-blue.svg)

Guardify-AI is an intelligent surveillance system that leverages cutting-edge computer vision and AI to detect potential shoplifting activities in real-time. The system combines automated video recording, dual-strategy AI analysis, and an intuitive web dashboard to provide comprehensive security monitoring for retail environments.

## 🎯 Problem & Solution

### The Challenge
Traditional retail security systems face significant limitations:
- **Manual monitoring** is labor-intensive and error-prone
- **Basic motion detection** creates too many false positives  
- **Human oversight** is limited by attention span and fatigue
- **Lack of analytics** prevents understanding of theft patterns

### Our Solution
Guardify-AI provides automated, AI-powered surveillance that:
- **Detects suspicious activities** with high accuracy using computer vision
- **Analyzes behavior patterns** through dual AI strategies
- **Provides real-time alerts** and comprehensive analytics
- **Scales efficiently** across multiple retail locations

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │  Backend API    │    │ Data Science    │
│ React + TypeScript │◄─►│ Flask + SQLAlch │◄─►│   Pipeline      │
│ Tailwind + Charts  │  │ PostgreSQL+Redis│    │ Vertex AI + GPT │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └──────────┬─────────────┼───────────────────────┘
                    │             │
            ┌─────────────────┐   │
            │ Video Processing│   │
            │ Playwright Auto │   │
            │ Google Storage  │   │
            │ Celery Tasks    │◄──┘
            └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ 
- Node.js 18+
- PostgreSQL database
- Google Cloud account

### Installation
```bash
# 1. Clone repository
git clone https://github.com/your-org/guardify-ai.git
cd guardify-ai

# 2. Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Frontend setup  
cd UI/Guardify-UI
npm install
cd ../..

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Running the Application
```bash
# Start backend (Terminal 1)
cd backend && python run.py

# Start frontend (Terminal 2)  
cd UI/Guardify-UI && npm run dev

# Run AI analysis (Terminal 3)
python data_science/src/main.py --strategy unified
```

- **Backend**: http://localhost:8574
- **Frontend**: http://localhost:5173

## 🧠 AI Analysis Strategies

### Unified Strategy (Recommended)
- **Direct video→detection** analysis using few-shot learning
- **Faster processing** with immediate confidence scoring
- **Best for**: Real-time production environments

### Agentic Strategy  
- **Two-stage pipeline**: Computer Vision → LLM Analysis
- **Detailed reasoning** with transparent decision making
- **Best for**: Thorough analysis and model debugging

```bash
# Run unified analysis (production)
python data_science/src/main.py --strategy unified --max-videos 50

# Run agentic analysis (detailed)
python data_science/src/main.py --strategy agentic --iterations 3
```

## 📊 Key Features

### 🎨 **Web Dashboard**
- Real-time security event monitoring
- Interactive analytics and charts
- Shop and camera management
- Responsive design for all devices

### 🤖 **AI Detection**
- Dual-strategy analysis pipeline
- Real theft example training
- Confidence scoring and reasoning
- Continuous model improvement

### 📹 **Video Processing**
- Automated camera feed capture
- Intelligent video segmentation  
- Cloud storage with auto-cleanup
- Real-time recording control

### 📈 **Analytics & Insights**
- Event pattern analysis
- Camera performance metrics
- Time-based activity trends
- Custom reporting capabilities

## 🔧 Development

### Project Structure
```
guardify-ai/
├── backend/              # Flask API + services
├── UI/Guardify-UI/       # React frontend  
├── data_science/         # AI analysis pipeline
├── google_client/        # Cloud integration
└── utils/               # Shared utilities
```

### API Documentation
All endpoints use JWT authentication and return:
```json
{
  "result": { /* data */ },
  "errorMessage": null
}
```

**Core Endpoints:**
- `GET/POST /events` - Event management
- `GET /stats` - Analytics data  
- `GET/POST /shops` - Shop management
- `GET/POST /shops/{id}/cameras` - Camera control

### Testing
```bash
# Backend tests
cd backend && python -m pytest tests/

# Frontend linting
cd UI/Guardify-UI && npm run lint

# AI pipeline tests  
cd data_science && python -m pytest tests/
```

## 🛠️ Configuration

Create `.env` file with:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/guardify_db

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-key.json
GOOGLE_CLOUD_BUCKET_NAME=your-bucket

# AI Services
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_API_BASE=your-azure-endpoint

# Camera System
PROVISION_ISR_USERNAME=camera-username
PROVISION_ISR_PASSWORD=camera-password

# Application
JWT_SECRET_KEY=your-jwt-secret
REDIS_URL=redis://localhost:6379/0  # Optional
```

## 🚧 Troubleshooting

### Redis Connection Issues
System automatically falls back to simple memory cache if Redis is unavailable.

### Google Cloud Setup
```bash
# Authenticate service account
export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"

# Test connection
python -c "from google.cloud import storage; print('Success!')"
```

## 📄 License & Support

**License**: MIT License - see [LICENSE](LICENSE) file

**Support**: Create issues in the GitHub repository or check the `logs/` directory for debugging.

## 🗺️ Roadmap

- [ ] Mobile notifications app
- [ ] Advanced ML model improvements  
- [ ] Multi-language support
- [ ] Integration with more camera systems
- [ ] Predictive analytics dashboard

---

**Built for modern retail security and loss prevention** 🛡️