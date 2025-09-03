# 🛡️ Guardify-AI: Advanced Surveillance & Shoplifting Detection System

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![React](https://img.shields.io/badge/react-19.1.0-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.8.3-blue.svg)

Guardify-AI is an intelligent surveillance system that leverages cutting-edge computer vision and AI to detect potential shoplifting activities in real-time. The system combines automated video recording, dual-strategy AI analysis, and an intuitive web dashboard to provide comprehensive security monitoring for retail environments.

## 🎯 Problem Statement

Traditional retail security relies on manual monitoring of camera feeds or basic motion detection systems, which are:
- **Labor-intensive** and expensive to scale
- **Error-prone** due to human fatigue and attention limitations
- **Reactive** rather than proactive in threat detection
- **Limited** in analytical capabilities for understanding patterns

Guardify-AI addresses these challenges by providing automated, AI-powered surveillance that can detect suspicious activities with high accuracy while offering detailed analytics and insights.

## 🏗️ System Architecture

### High-Level Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │  Backend API    │    │ Data Science    │
│                 │    │                 │    │   Pipeline      │
│ React + TS      │◄──►│ Flask + SQLAlch │◄──►│ AI Analysis     │
│ Tailwind CSS    │    │ PostgreSQL      │    │ Vertex AI       │
│ Chart.js        │    │ Redis Cache     │    │ Google Cloud    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │ Video Processing│              │
         │              │                 │              │
         └──────────────►│ Playwright      │◄─────────────┘
                        │ GCS Upload      │
                        │ Celery Tasks    │
                        └─────────────────┘
```

### Core Components

#### 🎨 **Frontend (UI/Guardify-UI/)**
- **Technology**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS with custom design system
- **Features**:
  - Real-time security dashboard
  - Event analytics and visualization
  - Shop and camera management
  - User authentication and settings
  - Responsive design for multiple devices

#### ⚙️ **Backend (backend/)**
- **Technology**: Flask + SQLAlchemy + PostgreSQL
- **Features**:
  - RESTful API with consistent response format
  - User authentication with JWT
  - Real-time statistics with caching
  - Event and shop management
  - Video recording control
  - Celery for background tasks

#### 🧠 **Data Science Pipeline (data_science/)**
- **Dual Analysis Strategy**:
  - **Unified Model**: Direct video-to-detection analysis using few-shot learning
  - **Agentic Model**: Two-stage pipeline with computer vision + LLM decision making
- **Technology**: Google Vertex AI, OpenAI GPT-4 Vision
- **Features**:
  - Real theft example training
  - Confidence scoring
  - Detailed analysis reasoning

#### 📹 **Video Processing (backend/video/)**
- **Technology**: Playwright automation + Google Cloud Storage
- **Features**:
  - Automated camera feed capture from Provision ISR
  - Intelligent video segmentation
  - Cloud storage with automatic cleanup
  - Real-time recording status monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL database
- Redis (optional, falls back to simple cache)
- Google Cloud account with Vertex AI enabled

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/guardify-ai.git
   cd guardify-ai
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend dependencies**
   ```bash
   cd UI/Guardify-UI
   npm install
   cd ../..
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
