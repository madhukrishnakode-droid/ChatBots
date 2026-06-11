# Quick Start - Unified AI Platform

## 30-Second Setup

### Terminal 1: Start Backend
```bash
cd unified-ai-project/backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
python -m uvicorn main:app --reload
```

Backend runs on: `http://localhost:8000`

### Terminal 2: Start Frontend
```bash
cd unified-ai-project/frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

## Access Points

| Feature | URL |
|---------|-----|
| Unified App | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## Features

**Choose One of 3 Apps:**
1. 💬 **General AI Chat** - Talk to Gemini or Ollama
2. 🧠 **Mental Health** - CBT-based support with crisis detection
3. 📄 **Resume Analyzer** - Upload resume, find matching jobs

---

## Demo Without API Key

If you don't have a Gemini API key, the app will use demo responses. Get one free at https://aistudio.google.com/app/apikey

---

## Troubleshooting

**Backend won't start?**
```bash
# Make sure Python 3.8+ is installed
python --version

# Install dependencies again
pip install -r requirements.txt
```

**Frontend won't connect?**
```bash
# Make sure backend is running on port 8000
# Check in main.py that CORS is enabled (it is by default)
```

**Resume upload issues?**
```bash
# Make sure this directory exists
mkdir -p backend/uploaded_resumes
```

---

For full documentation, see [README.md](README.md)
