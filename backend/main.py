from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import os
import google.generativeai as genai

# Import modules from the original projects. We'll either duplicate them here or adjust import paths later.
# For now, copy logic from the mental-health and resume backends into this unified entrypoint.

# --- Mental health dependencies ---
from database import engine, get_db, Base
import models, schemas
import chat_service
import crisis_monitor

# --- Resume-related imports will be added below ---

# Create tables for mental health models
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration (allow unified frontend origins by default)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Unified AI Platform backend is running"}

# ----------------- Mental health endpoints -----------------
@app.get("/debug/chat_service_path")
def debug_chat_service_path():
    try:
        return {"chat_service_file": chat_service.__file__}
    except Exception as e:
        return {"error": str(e)}

@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        return db_user
    new_user = models.User(username=user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/chat", response_model=schemas.ChatResponse)
async def chat_endpoint(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    # Crisis detection and logging
    if crisis_monitor.detect_crisis(request.message):
        crisis_log = models.ChatHistory(
            user_id=request.user_id,
            role="user",
            content=request.message,
            sentiment="crisis"
        )
        db.add(crisis_log)
        system_log = models.ChatHistory(
            user_id=request.user_id,
            role="assistant",
            content=crisis_monitor.HELPLINE_MESSAGE,
            sentiment="crisis"
        )
        db.add(system_log)
        db.commit()
        return schemas.ChatResponse(
            response=crisis_monitor.HELPLINE_MESSAGE,
            sentiment="crisis",
            crisis_detected=True
        )

    ai_response_text = await chat_service.get_ai_response(request.message)

    user_msg = models.ChatHistory(
        user_id=request.user_id,
        role="user",
        content=request.message,
        sentiment="neutral"
    )
    ai_msg = models.ChatHistory(
        user_id=request.user_id,
        role="assistant",
        content=ai_response_text,
        sentiment="positive"
    )
    db.add(user_msg)
    db.add(ai_msg)
    db.commit()

    return schemas.ChatResponse(
        response=ai_response_text,
        sentiment="positive",
        crisis_detected=False
    )

@app.get("/recommendations", response_model=list[str])
async def get_recommendations(db: Session = Depends(get_db)):
    recent_msgs = db.query(models.ChatHistory.content)\
        .filter(models.ChatHistory.role == "user")\
        .order_by(models.ChatHistory.timestamp.desc())\
        .limit(20)\
        .all()
    history_texts = [msg[0] for msg in recent_msgs]
    recommendations = await chat_service.get_recommendations(history_texts)
    return recommendations

# ----------------- General Chat Endpoint (replaces Node service) -----------------
# --- General Chat Configuration ---
GENERAL_SYSTEM_PROMPT = """
You are a highly structured and professional AI assistant. 
When responding to ANY prompt:
1. Start with a clear Markdown header (###) for the main topic.
2. Use Markdown tables for comparisons, lists of items, or data.
3. Use clean code blocks (```language) for all technical examples.
4. Use bold text for key terms.
5. Avoid long paragraphs; use bullet points for clarity.
6. Keep the tone professional and helpful.
"""

@app.post("/chat-general")
async def general_chat(request: dict):
    """Simple generic AI chat endpoint. Accepts {'message': str}."""
    message = request.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    provider = os.getenv("AI_PROVIDER", "gemini")
    reply_text = ""

    if provider == "ollama":
        try:
            import requests
            resp = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={"model": os.getenv("OLLAMA_MODEL", "mistral"), "prompt": f"{GENERAL_SYSTEM_PROMPT}\n\nUser: {message}", "stream": False},
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            reply_text = data.get("response", "")
        except Exception:
            reply_text = f"[Demo Response] You asked: \"{message}\"\n\nOllama is not reachable."
    else:
        if not os.getenv("GEMINI_API_KEY"):
            reply_text = f"Demo Response: You asked \"{message}\"\n\nAPI key not configured."
        else:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                # Inject system prompt
                resp = model.generate_content(f"{GENERAL_SYSTEM_PROMPT}\n\nUser: {message}")
                reply_text = resp.text
            except Exception as e:
                reply_text = f"Error: {str(e)}"

    return {"reply": reply_text}


# ----------------- Resume Chatbot Endpoints -----------------
# The following logic is adapted from the original resume backend main.py

# initialize resume modules
from resume_parser import ResumeParser
from skill_extractor import SkillExtractor
from job_scraper import JobScraper
from matching_engine import MatchingEngine
from chatbot import CareerAdvisorChatbot
from config import *

resume_parser = ResumeParser()
skill_extractor = SkillExtractor()
job_scraper = JobScraper()
matching_engine = MatchingEngine()
resume_chatbot = CareerAdvisorChatbot()

# make upload directory
import os
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        file_ext = file.filename.split('.')[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        text, file_type = resume_parser.parse(file_path)
        skill_extractor.extract_skills(text)
        skill_summary = skill_extractor.get_skill_summary(text)
        flat_skills = skill_extractor.get_flat_skills()
        user_profile = {
            'name': 'Job Seeker',
            'resume_text': text[:500],
            'skills': flat_skills,
            'experience_years': skill_summary.get('experience_years', 0),
            'projects': skill_summary.get('projects', []),
            'education': skill_summary.get('education', []),
            'file_type': file_type,
            'upload_time': datetime.now().isoformat()
        }
        resume_chatbot.set_user_profile(user_profile)
        greeting = resume_chatbot.generate_initial_greeting()
        return {
            "message": "Resume uploaded and analyzed successfully!",
            "resume_data": user_profile,
            "initial_greeting": greeting
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-resume")
async def analyze_resume(request: dict):
    try:
        analysis = {
            "skills": request.get('skills', []),
            "experience_years": request.get('experience_years', 0),
            "location": request.get('location', 'Remote'),
            "skill_count": len(request.get('skills', [])),
            "analysis_timestamp": datetime.now().isoformat()
        }
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search-jobs")
async def search_jobs(request: dict):
    try:
        resume_skills = request.get('skills', [])
        resume_experience = request.get('experience_years', 0)
        location = request.get('location', 'Remote')
        
        jobs = job_scraper.fetch_jobs_by_skills(
            resume_skills,
            location,
            limit=10
        )
        
        # Calculate match score for each job
        enriched_jobs = []
        for job in jobs:
            job_required_skills = job.get('required_skills', [])
            job_experience_required = 0
            
            # Try to extract experience requirement from job description
            try:
                import re
                description = job.get('description', '').lower()
                exp_match = re.search(r'(\d+)\+?\s*(?:to\s+\d+)?\s*(?:years?|yrs?)', description)
                if exp_match:
                    job_experience_required = int(exp_match.group(1))
            except:
                pass
            
            # Calculate match using matching engine
            match_result = matching_engine.calculate_match_score(
                resume_skills,
                job_required_skills,
                resume_experience,
                job_experience_required
            )
            
            # Enrich job with match data
            enriched_job = {
                **job,
                'match_percentage': match_result['overall_match_percentage'],
                'matched_skills': match_result['matched_skills'],
                'missing_skills': match_result['missing_skills'],
                'match_strength': match_result['match_strength'],
                'recommendation': match_result['recommendation']
            }
            enriched_jobs.append(enriched_job)
        
        # Sort by match percentage (descending)
        enriched_jobs.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return {"jobs": enriched_jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match-job")
async def match_job(request: dict):
    try:
        resume_skills = request.get('resume_skills', [])
        job_required_skills = request.get('job_required_skills', [])
        resume_experience = request.get('resume_experience_years', 0)
        job_experience = request.get('job_experience_required', 0)
        
        match_result = matching_engine.calculate_match_score(
            resume_skills,
            job_required_skills,
            resume_experience,
            job_experience
        )
        
        explanation = resume_chatbot.explain_job_match(
            request.get('job_title', 'Unknown'),
            request.get('company', 'Unknown'),
            match_result['overall_match_percentage'],
            match_result['matched_skills'],
            match_result['missing_skills']
        )
        
        return {
            "match_percentage": match_result['overall_match_percentage'],
            "matched_skills": match_result['matched_skills'],
            "missing_skills": match_result['missing_skills'],
            "match_strength": match_result['match_strength'],
            "explanation": explanation,
            "recommendation": match_result['recommendation']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def resume_chat(request: dict):
    try:
        user_message = request.get('message', '').lower()
        context = request.get('context', {})
        
        resume_chatbot.add_user_message(request.get('message', ''))
        
        if any(word in user_message for word in ['why', 'score', 'low', 'percentage']):
            response = resume_chatbot.answer_follow_up(request.get('message', ''), context)
        elif any(word in user_message for word in ['improve', 'better', 'learn', 'increase']):
            response = resume_chatbot.suggest_improvement(context.get('missing_skills', []))
        elif any(word in user_message for word in ['role', 'position', 'job', 'similar']):
            response = resume_chatbot.answer_follow_up(request.get('message', ''), context)
        else:
            response = resume_chatbot.answer_follow_up(request.get('message', ''), context)
        
        if len(resume_chatbot.get_conversation_history()) % 5 == 0:
            response += "\n\n" + resume_chatbot.generate_encouragement()
        
        return {
            "bot_reply": response,
            "conversation_history": resume_chatbot.get_conversation_history()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

