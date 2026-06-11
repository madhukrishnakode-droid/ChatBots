"""
Configuration file for Resume Bot backend (now used by unified project)
"""

# Flask/FastAPI Configuration
DEBUG = True
HOST = "0.0.0.0"
# Later when running the unified backend we use port 8000 (mental-health port)
PORT = 8000

# File Upload Configuration
UPLOAD_FOLDER = "uploaded_resumes"
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# NLP Configuration
SPACY_MODEL = "en_core_web_sm"
SKILL_MATCH_THRESHOLD = 0.6  # 60% confidence threshold

# Job Scraping Configuration
JOB_SEARCH_LIMIT = 10  # Number of jobs to fetch per search
WEB_SCRAPING_TIMEOUT = 10  # seconds

# Skill Database
TECHNICAL_SKILLS = {
    "programming_languages": ["Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Rust"],
    "web_frameworks": ["React", "Vue", "Angular", "Django", "Flask", "FastAPI", "Express", "Spring"],
    "databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Firebase"],
    "cloud_platforms": ["AWS", "Google Cloud", "Azure", "Heroku", "DigitalOcean"],
    "devops": ["Docker", "Kubernetes", "Jenkins", "GitHub Actions", "CI/CD", "Terraform"],
    "ai_ml": ["TensorFlow", "PyTorch", "scikit-learn", "NLP", "Machine Learning", "Deep Learning"],
    "tools": ["Git", "Jira", "Confluence", "Linux", "REST APIs", "GraphQL"],
}

SOFT_SKILLS = [
    "Communication",
    "Team Collaboration",
    "Problem Solving",
    "Leadership",
    "Project Management",
    "Time Management",
    "Critical Thinking",
    "Adaptability",
]

# Sample Job Titles for Matching
JOB_TITLES = [
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Scientist",
    "DevOps Engineer",
    "Machine Learning Engineer",
    "Cloud Architect",
    "Software Engineer",
    "Web Developer",
    "Python Developer",
]