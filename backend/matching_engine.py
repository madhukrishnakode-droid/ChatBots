"""
Skill Matching Engine
Calculates match percentage between resume skills and job requirements
"""

from typing import List, Dict, Tuple
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Calculates how well a resume matches job requirements
    """
    
    WEIGHTS = {
        'exact_match': 1.0,
        'category_match': 0.8,
        'partial_match': 0.6,
        'related_match': 0.4,
    }
    
    SKILL_CATEGORIES = {
        'frontend': ['react', 'vue', 'angular', 'html', 'css', 'javascript', 'typescript'],
        'backend': ['python', 'java', 'cpp', 'php', 'ruby', 'go', 'nodejs', 'express', 'django', 'flask'],
        'databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'firebase', 'dynamodb'],
        'cloud': ['aws', 'azure', 'google cloud', 'heroku'],
        'devops': ['docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform', 'ansible'],
        'ml': ['tensorflow', 'pytorch', 'scikit-learn', 'nlp', 'machine learning'],
    }
    
    def __init__(self):
        self.resume_skills = []
        self.job_requirements = []
    
    def calculate_match_score(self, resume_skills: List[str], job_required_skills: List[str],
                             resume_experience_years: int = 0, job_experience_required: int = 0) -> Dict:
        self.resume_skills = [s.lower() for s in resume_skills]
        self.job_requirements = [s.lower() for s in job_required_skills]
        skill_match_pct = self._calculate_skill_match()
        experience_match_pct = self._calculate_experience_match(resume_experience_years, job_experience_required)
        overall_match = (skill_match_pct * 0.7) + (experience_match_pct * 0.3)
        overall_match = min(overall_match, 100)
        matched_skills, missing_skills, bonus_skills = self._get_skill_details()
        return {
            'overall_match_percentage': round(overall_match, 1),
            'skill_match_percentage': round(skill_match_pct, 1),
            'experience_match_percentage': round(experience_match_pct, 1),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'bonus_skills': bonus_skills,
            'match_strength': self._get_match_strength(overall_match),
            'recommendation': self._get_recommendation(overall_match, matched_skills, missing_skills)
        }
    
    def _calculate_skill_match(self) -> float:
        if not self.job_requirements:
            return 100.0
        total_matched = 0.0
        for required_skill in self.job_requirements:
            best_match_score = 0.0
            for resume_skill in self.resume_skills:
                match_score = self._calculate_individual_match(resume_skill, required_skill)
                best_match_score = max(best_match_score, match_score)
            total_matched += best_match_score
        return (total_matched / len(self.job_requirements)) * 100
    
    def _calculate_individual_match(self, resume_skill: str, required_skill: str) -> float:
        if resume_skill == required_skill:
            return self.WEIGHTS['exact_match']
        category_match = self._check_category_match(resume_skill, required_skill)
        if category_match:
            return self.WEIGHTS['category_match']
        similarity = SequenceMatcher(None, resume_skill, required_skill).ratio()
        if similarity > 0.8:
            return self.WEIGHTS['partial_match']
        if self._check_related_skills(resume_skill, required_skill):
            return self.WEIGHTS['related_match']
        return 0.0
    
    def _check_category_match(self, skill1: str, skill2: str) -> bool:
        for category, skills in self.SKILL_CATEGORIES.items():
            skill1_in_cat = any(s in skill1 or skill1 in s for s in skills)
            skill2_in_cat = any(s in skill2 or skill2 in s for s in skills)
            if skill1_in_cat and skill2_in_cat:
                return True
        return False
    
    def _check_related_skills(self, skill1: str, skill2: str) -> bool:
        related_pairs = [
            ('node', 'express'),
            ('docker', 'kubernetes'),
            ('python', 'django'),
            ('python', 'flask'),
            ('react', 'javascript'),
            ('vue', 'javascript'),
            ('angular', 'javascript'),
            ('aws', 'cloud'),
            ('azure', 'cloud'),
            ('postgres', 'sql'),
            ('mysql', 'sql'),
            ('tensorflow', 'ml'),
            ('pytorch', 'ml'),
        ]
        for skill_a, skill_b in related_pairs:
            if (skill_a in skill1 and skill_b in skill2) or (skill_a in skill2 and skill_b in skill1):
                return True
        return False
    
    def _calculate_experience_match(self, resume_years: int, required_years: int) -> float:
        if required_years == 0:
            return 100.0
        if resume_years >= required_years:
            return 100.0
        match_pct = (resume_years / required_years) * 100
        return min(match_pct, 100.0)
    
    def _get_skill_details(self) -> Tuple[List[str], List[str], List[str]]:
        matched_skills = []
        missing_skills = []
        bonus_skills = list(self.resume_skills)
        
        for required_skill in self.job_requirements:
            best_match_score = 0.0
            best_match_skill = None
            found = False
            
            # Find the best matching skill from resume
            for resume_skill in self.resume_skills:
                match_score = self._calculate_individual_match(resume_skill, required_skill)
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_match_skill = resume_skill
                    found = True
            
            if found and best_match_skill:
                matched_skills.append(best_match_skill)
                if best_match_skill in bonus_skills:
                    bonus_skills.remove(best_match_skill)
            else:
                missing_skills.append(required_skill)
        
        return list(set(matched_skills)), missing_skills, bonus_skills
    
    def _get_match_strength(self, percentage: float) -> str:
        if percentage >= 80:
            return "Excellent"
        elif percentage >= 60:
            return "Good"
        elif percentage >= 40:
            return "Fair"
        elif percentage >= 20:
            return "Weak"
        else:
            return "Very Weak"
    
    def _get_recommendation(self, match_pct: float, matched_skills: List[str], missing_skills: List[str]) -> str:
        if match_pct >= 80:
            return f"Excellent match! You have {len(matched_skills)} of the required skills. Apply now!"
        elif match_pct >= 60:
            missing_str = ", ".join(missing_skills[:2])
            return f"Good match! Consider learning {missing_str} to increase your chances."
        elif match_pct >= 40:
            missing_str = ", ".join(missing_skills[:3])
            return f"Fair match. You're missing some key skills: {missing_str}. Consider upskilling."
        else:
            return "This role requires significant additional skills. Consider roles that better match your current skill set."
    
    def get_match_report(self, resume_data: Dict, job_data: Dict) -> Dict:
        match_result = self.calculate_match_score(
            resume_data.get('skills', []),
            job_data.get('required_skills', []),
            resume_data.get('experience_years', 0),
            self._extract_experience_from_job(job_data)
        )
        return {
            'job_title': job_data.get('title', 'Unknown'),
            'company': job_data.get('company', 'Unknown'),
            'match_details': match_result,
            'job_url': job_data.get('url', ''),
        }
    
    def _extract_experience_from_job(self, job_data: Dict) -> int:
        description = job_data.get('description', '').lower()
        import re
        match = re.search(r'(\d+)\+?\s*(?:to\s+\d+)?\s*(?:years?|yrs?)', description)
        if match:
            return int(match.group(1))
        return 0


if __name__ == "__main__":
    engine = MatchingEngine()
    resume_skills = ['Python', 'JavaScript', 'React', 'Docker', 'AWS']
    job_skills = ['Python', 'React', 'Node.js', 'Docker', 'PostgreSQL']
    result = engine.calculate_match_score(resume_skills, job_skills, resume_experience_years=3, job_experience_required=2)
    print(f"Match Score: {result['overall_match_percentage']}%")
    print(f"Match Strength: {result['match_strength']}")
    print(f"Matched Skills: {result['matched_skills']}")
    print(f"Missing Skills: {result['missing_skills']}")
    print(f"Recommendation: {result['recommendation']}")