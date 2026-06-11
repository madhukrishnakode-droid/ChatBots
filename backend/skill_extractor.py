"""
Skill Extractor Module
Extracts technical and soft skills from resume text using NLP and keyword matching
"""

import re
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

# Comprehensive skill database
SKILL_DATABASE = {
    "python": ["python", "py"],
    "javascript": ["javascript", "js", "typescript", "ts"],
    "java": ["java"],
    "cpp": ["c++", "c plus plus", "cpp"],
    "csharp": ["c#", "csharp", "c sharp"],
    "php": ["php"],
    "ruby": ["ruby"],
    "go": ["golang", "go"],
    "rust": ["rust"],
    "scala": ["scala"],
    "kotlin": ["kotlin"],
    "react": ["react", "reactjs"],
    "vue": ["vuejs", "vue"],
    "angular": ["angular", "angularjs"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "express": ["express", "expressjs"],
    "spring": ["spring", "springboot"],
    "asp.net": ["asp.net", "aspnet"],
    "laravel": ["laravel"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "firebase": ["firebase"],
    "elasticsearch": ["elasticsearch"],
    "cassandra": ["cassandra"],
    "dynamodb": ["dynamodb"],
    "oracle": ["oracle"],
    "sql": ["sql", "pl/sql"],
    "aws": ["aws", "amazon web services"],
    "google cloud": ["google cloud", "gcp", "cloud"],
    "azure": ["azure", "microsoft azure"],
    "heroku": ["heroku"],
    "digitalocean": ["digitalocean"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "jenkins": ["jenkins"],
    "github": ["github", "git"],
    "gitlab": ["gitlab"],
    "git": ["git"],
    "gitlab ci": ["gitlab ci"],
    "cicd": ["ci/cd", "ci cd", "continuous integration", "continuous deployment"],
    "terraform": ["terraform"],
    "ansible": ["ansible"],
    "linux": ["linux", "ubuntu", "centos"],
    "windows": ["windows"],
    "mac": ["macos", "mac"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "nlp": ["nlp", "natural language processing"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "computer vision": ["computer vision", "cv"],
    "data science": ["data science"],
    "rest": ["rest", "restful"],
    "graphql": ["graphql"],
    "soap": ["soap"],
    "json": ["json"],
    "xml": ["xml"],
    "grpc": ["grpc"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "sass", "scss"],
    "tailwind": ["tailwind", "tailwindcss"],
    "bootstrap": ["bootstrap"],
    "webpack": ["webpack"],
    "npm": ["npm"],
    "yarn": ["yarn"],
    "communication": ["communication", "communicate"],
    "teamwork": ["teamwork", "team work", "collaboration", "collaborative"],
    "leadership": ["leadership", "lead"],
    "problem solving": ["problem solving", "problem solver"],
    "project management": ["project management", "pm"],
    "agile": ["agile", "scrum"],
    "time management": ["time management"],
    "adaptability": ["adaptability", "adaptable"],
}

SKILL_NORMALIZATION = {key: key for key in SKILL_DATABASE.keys()}


class SkillExtractor:
    def __init__(self):
        self.skills_found = set()
        self.skill_categories = {}

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        self.skills_found = set()
        self.skill_categories = {
            'technical': [],
            'soft': [],
            'frameworks': [],
            'tools': [],
            'languages': []
        }
        text_lower = text.lower()
        for skill_name, keywords in SKILL_DATABASE.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    self._add_skill(skill_name)
                    break
        self._categorize_skills()
        return self.skill_categories

    def _add_skill(self, skill: str):
        normalized = SKILL_NORMALIZATION.get(skill, skill)
        self.skills_found.add(normalized)

    def _categorize_skills(self):
        technical_keywords = ['python', 'javascript', 'java', 'cpp', 'csharp', 'php', 'ruby', 'go', 'rust']
        framework_keywords = ['react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express', 'spring']
        tools_keywords = ['docker', 'kubernetes', 'jenkins', 'github', 'gitlab', 'git', 'terraform']
        soft_keywords = ['communication', 'teamwork', 'leadership', 'problem solving', 'agile']
        language_keywords = ['python', 'javascript', 'java', 'cpp', 'csharp', 'php', 'ruby', 'go', 'rust', 'sql']
        for skill in self.skills_found:
            if any(keyword in skill.lower() for keyword in soft_keywords):
                self.skill_categories['soft'].append(skill)
            elif any(keyword in skill.lower() for keyword in framework_keywords):
                self.skill_categories['frameworks'].append(skill)
            elif any(keyword in skill.lower() for keyword in tools_keywords):
                self.skill_categories['tools'].append(skill)
            elif any(keyword in skill.lower() for keyword in language_keywords):
                self.skill_categories['languages'].append(skill)
            else:
                self.skill_categories['technical'].append(skill)

    def get_flat_skills(self) -> List[str]:
        all_skills = []
        for category_skills in self.skill_categories.values():
            all_skills.extend(category_skills)
        return list(set(all_skills))

    def extract_projects(self, text: str) -> List[Dict[str, str]]:
        projects = []
        
        # Pattern 1: Lines with project names and technologies in parentheses
        project_pattern = r'([A-Z][a-zA-Z\s\-]+?)\s*\(([^)]+)\)'
        
        # Pattern 2: Lines starting with keywords
        keyword_pattern = r'(?:^|\n)\s*(?:project|worked on|built|developed)[:\s]*([^\n]+)'
        
        # Extract projects from pattern 1 (Project Name (Tech1, Tech2))
        matches = re.finditer(project_pattern, text, re.MULTILINE)
        seen_projects = set()
        for match in matches:
            project_name = match.group(1).strip()
            tech_string = match.group(2).strip()
            
            # Skip if it's a common non-project pattern
            if len(project_name) > 3 and len(project_name) < 150 and '(' not in project_name:
                if project_name not in seen_projects and len(project_name) > 5:
                    seen_projects.add(project_name)
                    projects.append({
                        'name': project_name,
                        'skills': self._extract_project_skills(tech_string)
                    })
        
        # Extract from pattern 2 (keyword-based)
        matches = re.finditer(keyword_pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            project_text = match.group(1).strip()
            if len(project_text) > 5 and project_text not in seen_projects:
                seen_projects.add(project_text)
                projects.append({
                    'name': project_text[:100],
                    'skills': self._extract_project_skills(project_text)
                })
        
        return projects

    def _extract_project_skills(self, project_text: str) -> List[str]:
        skills = []
        text_lower = project_text.lower()
        for skill_name, keywords in SKILL_DATABASE.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    skills.append(SKILL_NORMALIZATION.get(skill_name, skill_name))
                    break
        return list(set(skills))

    def extract_experience_years(self, text: str) -> int:
        patterns = [
            r'(\d+)\s*(?:\+|-\d+)?\s*(?:years?|yrs?)',
            r'(?:since|from)\s+(\d{4})',
        ]
        years = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    year = int(match.group(1))
                    if year < 50:
                        years.append(year)
                    elif year > 1900:
                        years.append(2024 - year)
                except ValueError:
                    pass
        return int(sum(years) / len(years)) if years else 0

    def extract_education(self, text: str) -> List[str]:
        education = []
        
        # Pattern: Full degree patterns (must have word boundaries)
        degree_pattern = r'\b(?:B\.?A\.?|B\.?S\.?|B\.?Sc\.?|M\.?A\.?|M\.?S\.?|M\.?Sc\.?|Ph\.?D\.?|M\.?B\.?A\.?|Bachelor\'?s?|Master\'?s?|Diploma|Associate|Certificate)\b[^,;\n]*?(?:in\s+(?:[A-Za-z\s&]+))?(?=,|;|\n|$)'
        
        matches = re.finditer(degree_pattern, text, re.IGNORECASE)
        for match in matches:
            degree = match.group(0).strip()
            if len(degree) > 5:
                # Clean up the degree text
                degree = re.sub(r'\s+', ' ', degree)  # Remove extra whitespace
                degree = re.sub(r'[•\-\*]$', '', degree)  # Remove trailing bullets
                if len(degree) > 5 and degree not in education:
                    education.append(degree)
        
        return education

    def get_skill_summary(self, text: str) -> Dict:
        skills = self.extract_skills(text)
        projects = self.extract_projects(text)
        experience_years = self.extract_experience_years(text)
        education = self.extract_education(text)
        return {
            'skills': skills,
            'all_skills': self.get_flat_skills(),
            'projects': projects,
            'experience_years': experience_years,
            'education': education,
            'total_skills': len(self.get_flat_skills())
        }


if __name__ == "__main__":
    extractor = SkillExtractor()
    sample_text = """
    Software Engineer with 5+ years of experience in Python, JavaScript, and React.
    Skilled in Docker, Kubernetes, and AWS. Worked on machine learning projects using TensorFlow.
    Strong communication and leadership skills. Bachelor's in Computer Science.
    """
    summary = extractor.get_skill_summary(sample_text)
    print("Extracted Skills:", summary['skills'])
    print("Total Skills:", summary['total_skills'])