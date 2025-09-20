# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Medical persona generation AI system with multi-department support. The application generates fictional patient personas for healthcare institutions, featuring RAG-powered data integration and timeline analysis capabilities.

## Key Commands

### Local Development
```bash
# Backend development (use python module syntax on Windows)
cd backend
python -m uvicorn main:app --reload --port 8000 --host 0.0.0.0

# Alternative for Unix-like systems
uvicorn main:app --reload --port 8000
```

### Testing & Validation
```bash
# Check JavaScript syntax for a single file
node -c frontend/medical/persona/script.js

# Test all department scripts for syntax errors
for dir in medical dental others user; do
  echo "Checking $dir:"
  node -c frontend/$dir/persona/script.js
done

# Verify file synchronization between departments
diff frontend/medical/persona/script.js frontend/dental/persona/script.js
```

### File Synchronization (Critical)
```bash
# Sync persona scripts across all departments
for dir in dental others user; do
  cp frontend/medical/persona/script.js frontend/$dir/persona/script.js
done

# Sync competitive analysis scripts
for dir in dental others user; do
  cp frontend/medical/competitive/script.js frontend/$dir/competitive/script.js
done

# Sync HTML files if modified
for dir in dental others user; do
  cp frontend/medical/persona/index.html frontend/$dir/persona/index.html
done
```

### Deployment
```bash
# Commit with standard message format
git add -A
git commit -m "Feature: description

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
git push
```

## Architecture

### Multi-Department Structure
- **4 parallel department paths**: `/medical`, `/dental`, `/others`, `/user`
- Each department has identical functionality but separate authentication
- **CRITICAL**: Scripts must be synchronized across all departments when changes are made
- Medical department serves as the primary development path - changes should be made here first then synced

### Backend Structure
```
backend/
├── api/                  # API configuration
├── services/             # Business logic
│   ├── timeline_analyzer.py        # Timeline search and analysis
│   ├── rag_processor.py           # RAG data processing
│   ├── competitive_analysis_service.py  # Competitor analysis
│   ├── google_maps_service.py     # Maps integration
│   └── cache_manager.py           # Chief complaints caching
├── models/               # Data models
├── middleware/           # Auth & CORS
└── main.py              # FastAPI application entry point
```

### Core API Endpoints

**Persona Generation**
- `POST /api/generate` - Generate persona with AI
- `POST /api/download/pdf` - Export persona as PDF
- `POST /api/download/ppt` - Export persona as PowerPoint

**Timeline Analysis**
- `POST /api/search-timeline` - Search timeline keywords
- `POST /api/search-timeline-analysis` - Get AI analysis of timeline

**Chief Complaints**
- `GET /api/chief-complaints/{category}/{department}` - Get department-specific complaints
- Cached in memory for 15 minutes for performance

**Competitive Analysis**
- `POST /api/analyze-competitors` - Analyze competitor clinics
- `GET /api/google-maps-static` - Get static map image

**Department Routes**
- `GET /{department}/persona` - Persona generation page
- `GET /{department}/competitive` - Competitive analysis page
- Each department requires Basic Auth credentials

### Frontend Architecture

**Key JavaScript Files**
- `frontend/{department}/persona/script.js` - Main persona generation logic
  - Timeline chart rendering with Chart.js
  - Label collision detection in `optimizeLabelsAfterRender()`
  - Tab switching between persona and timeline views
  - Chief complaints caching in localStorage

- `frontend/{department}/competitive/script.js` - Competitive analysis
  - Google Maps integration
  - Clinic data visualization

**Shared Resources**
- `frontend/shared/chief-complaints-cache.js` - Global complaint data caching
- `frontend/shared/department-preloader.js` - Department data preloading

### Critical Implementation Details

**Canvas Size Issue Fix**
- `optimizeLabelsAfterRender()` now validates canvas size before processing
- Automatically resizes chart if canvas dimensions are 0x0
- Defers label optimization with setTimeout if canvas not ready

**Tab Switching**
- Timeline tab requires explicit chart resize on first display
- Chart instance stored in `window.timelineChartInstance`

**Authentication Flow**
- Basic Auth headers required for all department endpoints
- Credentials pattern: `{DEPARTMENT}_USERNAME` / `{DEPARTMENT}_PASSWORD`
- Admin access through separate `/admin` endpoint

**Import Structure**
- Backend uses absolute imports (not relative) when run with uvicorn
- Example: `from services import timeline_analyzer` not `from .services`

## Data Flow

**Persona Generation Pipeline**
1. User fills multi-step form with chief complaint selection
2. Form data sent to `/api/generate` with AI model selection
3. Backend includes RAG data from CSV files in prompt
4. AI response parsed and formatted
5. Results displayed with option to generate timeline

**Timeline Analysis Pipeline**
1. Chief complaint triggers CSV data load from `rag/各診療科/`
2. Keywords filtered by age/gender demographics
3. Chart.js scatter plot renders with collision detection
4. AI generates analysis of search patterns

**RAG Data Structure**
- CSV files located in `rag/各診療科/{department}/主訴/`
- SQLite database used for keyword searching
- 15-minute cache for performance optimization

## Environment Variables

Required for production (Render.com):
```
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
ADMIN_USERNAME=admin
ADMIN_PASSWORD=...
MEDICAL_USERNAME=medical
MEDICAL_PASSWORD=...
DENTAL_USERNAME=dental
DENTAL_PASSWORD=...
OTHERS_USERNAME=others
OTHERS_PASSWORD=...
USER_USERNAME=user
USER_PASSWORD=...
```

## Known Issues & Solutions

1. **Canvas size 0x0**: Chart resize forced on tab switch, validation added in `optimizeLabelsAfterRender()`
2. **Import errors**: Use absolute imports in backend when running with uvicorn
3. **Variable declarations**: Always check with `node -c script.js` before syncing
4. **forEach with break**: Use `for...of` loops instead
5. **Label collision**: Adjust margins and patterns in `optimizeLabelsAfterRender()`
6. **PDF Japanese fonts**: Requires IPAGothic font in container
7. **Cache invalidation**: Clear with `_timeline_cache.clear()` in Python

## Dependencies

**Python** (requirements.txt):
- FastAPI, uvicorn for backend server
- openai, anthropic, google-generativeai for AI
- fpdf2, python-pptx for document generation
- pandas, matplotlib for data processing

**JavaScript** (CDN):
- Chart.js for timeline visualization
- chartjs-plugin-datalabels for label management
- Google Maps API for competitive analysis

## Testing Approach

No formal test framework is configured. Use these validation methods:
- JavaScript syntax: `node -c [file]`
- Python syntax: `python -m py_compile [file]`
- API testing: Manual testing with browser DevTools
- File sync verification: `diff` command between departments