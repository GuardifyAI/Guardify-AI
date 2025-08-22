# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Guardify-AI is a surveillance system that detects potential shoplifting activities using computer vision and AI analysis. The system consists of three main components:

### Architecture Components

**Frontend (UI/Guardify-UI/)**: React + TypeScript + Vite application that provides a dashboard for viewing security events, analytics, and managing shops. Uses Tailwind CSS for styling and Chart.js for data visualization.

**Backend (backend/)**: Flask REST API with SQLAlchemy ORM, providing endpoints for events, shops, users, stats, and real-time video recording control. Uses PostgreSQL database and includes caching with Flask-Caching.

**Data Science Pipeline (data_science/)**: Core AI analysis system with two detection strategies:
- **Unified Strategy**: Single-model direct video→detection analysis using few-shot learning
- **Agentic Strategy**: Two-step pipeline with computer vision analysis followed by LLM-based decision making

**Video Processing (backend/video/)**: Automated video recording from security cameras using Playwright to capture streams from Provision ISR platform, with automatic upload to Google Cloud Storage.

## Development Commands

### Frontend (UI/Guardify-UI/)
```bash
cd UI/Guardify-UI
npm install                    # Install dependencies
npm run dev                    # Start development server
npm run build                  # Build for production
npm run lint                   # Run ESLint
npm run preview               # Preview production build
npm run convert-videos        # Convert video files
```

### Backend
```bash
cd backend
python run.py                  # Start Flask server on port 8574

# Testing
python -m pytest tests/       # Run all tests
python -m pytest tests/test_sanity.py  # Run sanity tests
python -m pytest tests/test_endpoints.py  # Run API endpoint tests
```

### Data Science Pipeline
```bash
cd data_science/src
python main.py --strategy unified    # Run unified analysis strategy
python main.py --strategy agentic    # Run agentic analysis strategy
python main.py --continuous-mode --camera-name CAMERA_01 --start-timestamp "2025-08-14 15:18:28"  # Real-time monitoring

# Common options:
--max-videos 20               # Limit number of videos to analyze
--iterations 3                # Analysis iterations per video
--threshold 0.45              # Detection confidence threshold
--diagnostic                  # Enable enhanced logging
--export                      # Export results to CSV
```

### Video Recording
```bash
cd backend/video
python main.py                # Start video recording system
```

### Celery Task Processing

The system uses Celery for asynchronous video analysis tasks. To run the complete system:

```bash
# 1. Start Redis (message broker)
redis-server

# 2. Start Celery worker for analysis tasks (Windows compatible)
celery -A backend.celery_app worker --loglevel=info --pool=solo --queues=analysis

# 3. Start Flower monitoring UI (optional)
celery -A backend.celery_app flower --port=5555

# 4. View task monitoring at http://localhost:5555
```

#### Celery Commands
```bash
# Check worker status
celery -A backend.celery_app status

# Inspect active tasks
celery -A backend.celery_app inspect active

# Purge all tasks from queue
celery -A backend.celery_app purge

# Test task dispatch
celery -A backend.celery_app call backend.celery_tasks.analysis_tasks.health_check
```

## Key Technical Details

### Database Models
Located in `backend/app/entities/`: User, Shop, Company, Camera, Event, Analysis entities with corresponding DTOs in `backend/app/dtos/`.

### AI Analysis Pipeline
The system supports two analysis approaches:
- **Unified Model** (`data_science/src/model/unified/`): Direct video analysis using few-shot learning with real theft examples
- **Agentic Model** (`data_science/src/model/agentic/`): Two-stage pipeline with computer vision observation followed by LLM analysis

### Authentication & Environment
- Uses Google Cloud Storage for video storage and Vertex AI for ML models
- Requires environment variables for Google credentials, database URL, and Provision ISR authentication
- Service account authentication via JSON key file

### API Structure
REST endpoints follow pattern `/app/{resource}` with consistent response format:
```json
{
  "result": <data>,
  "errorMessage": <error_string_or_null>
}
```

### Video Processing Flow
1. Playwright automation captures camera streams from Provision ISR
2. Videos saved locally then uploaded to Google Cloud Storage
3. AI pipeline monitors bucket for new videos and analyzes automatically
4. Results stored in database and displayed in UI dashboard

### Testing Strategy
- Backend: Pytest with Flask test client for API endpoints and database operations
- Data Science: Integration tests with actual Google Cloud bucket analysis
- Frontend: ESLint for code quality

## Important File Locations

- Frontend entry: `UI/Guardify-UI/src/main.tsx`
- Backend entry: `backend/run.py`
- AI analysis entry: `data_science/src/main.py`
- Video recording entry: `backend/video/main.py`
- Database config: `backend/db.py`
- Environment utilities: `utils/env_utils.py`
- Logging utilities: `utils/logger_utils.py`