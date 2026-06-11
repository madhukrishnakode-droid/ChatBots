"""
Chatbot Module
Generates conversational responses like a career advisor
"""

from typing import List, Dict
import random
import logging

logger = logging.getLogger(__name__)


class CareerAdvisorChatbot:
    """
    AI Career Advisor - Generates human-like conversational responses
    """
    
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {}
    
    def set_user_profile(self, profile: Dict):
        """Set user profile from parsed resume"""
        self.user_profile = profile
    
    def generate_initial_greeting(self) -> str:
        name = self.user_profile.get('name', 'there')
        skills_count = len(self.user_profile.get('skills', []))
        experience = self.user_profile.get('experience_years', 0)
        greetings = [
            f"Hey {name}! 👋 Thanks for sharing your resume. I can see you have {skills_count} great skills and {experience} years of experience. Let's find you the perfect job!",
            f"Welcome {name}! I've reviewed your resume - impressive! With your {skills_count} skills, I found some awesome opportunities. Let me show you the best matches.",
            f"Hi {name}! 🚀 Your resume looks strong with {experience}+ years of experience. Let's discover roles that align with your skills.",
        ]
        response = random.choice(greetings)
        self.conversation_history.append({'role': 'bot', 'message': response})
        return response
    
    def explain_job_match(self, job_title: str, company: str, match_pct: float, 
                         matched_skills: List[str], missing_skills: List[str]) -> str:
        matched_str = ", ".join(matched_skills[:3])
        missing_str = ", ".join(missing_skills[:2]) if missing_skills else "nothing major"
        if match_pct >= 80:
            explanations = [
                f"🎯 This is an excellent fit! {company} is looking for someone with your exact skill set. You have {matched_str}, which are core requirements. I'd recommend applying ASAP!",
                f"Perfect match! 💪 The {job_title} role at {company} aligns beautifully with your skills ({matched_str}). You're a strong candidate here.",
                f"This is it! 🔥 {company} needs your expertise. You have all the key skills ({matched_str}) they're looking for. Apply now!",
            ]
        elif match_pct >= 60:
            explanations = [
                f"Good opportunity! 📊 You match {match_pct}% of requirements for {job_title} at {company}. You have {matched_str}, but consider learning {missing_str} to strengthen your candidacy.",
                f"Solid match! You're a viable candidate for {company}'s {job_title} role. You have {matched_str}, just missing some familiarity with {missing_str}.",
                f"This could work! 👍 {match_pct}% alignment with the {job_title} position. Your {matched_str} skills are valued, but upskilling in {missing_str} would help.",
            ]
        elif match_pct >= 40:
            explanations = [
                f"Moderate fit. You have some relevant skills ({matched_str}) for the {job_title} role, but you're missing {missing_str}. Consider this as a learning opportunity if interested.",
                f"Fair match ({match_pct}%). The {job_title} at {company} could be a stretch, but not impossible. Focus on learning {missing_str} first.",
                f"Possible, but challenging. You'd need to develop skills in {missing_str} for the {job_title} role. Use this as motivation to upskill!",
            ]
        else:
            explanations = [
                f"This might be a reach. The {job_title} at {company} requires significant skills you're still developing. I'd suggest roles that better match your current skill set.",
                f"Not quite ready yet. While {company} is great, this {job_title} role requires {missing_str}. Let's find more aligned opportunities.",
                f"This one's a stretch for now. Focus on gaining more experience with {missing_str}, then revisit similar roles.",
            ]
        response = random.choice(explanations)
        self.conversation_history.append({'role': 'bot', 'message': response})
        return response
    
    def suggest_improvement(self, missing_skills: List[str]) -> str:
        if not missing_skills:
            response = "You're already well-equipped! 🌟 Your current skill set is competitive. Focus on gaining practical experience and you'll be unstoppable!"
        else:
            top_skills = missing_skills[:3]
            skill_str = ", ".join(top_skills)
            suggestions = [
                f"To unlock more opportunities, I'd recommend learning: {skill_str}. These are highly in-demand! Consider online courses, projects, or certifications.",
                f"Your next power moves: Master {skill_str}. These skills would dramatically increase your market value and job prospects.",
                f"Level up with: {skill_str}. These are the missing pieces that could unlock senior positions and higher salaries.",
            ]
            response = random.choice(suggestions)
        self.conversation_history.append({'role': 'bot', 'message': response})
        return response
    
    def answer_follow_up(self, question: str, user_context: Dict) -> str:
        question_lower = question.lower()
        if any(word in question_lower for word in ['why', 'score', 'low', 'percentage']):
            missing = user_context.get('missing_skills', [])
            matched = user_context.get('matched_skills', [])
            match_pct = user_context.get('match_percentage', 0)
            response = f"Your {match_pct}% match reflects the overlap between your skills ({', '.join(matched)}) and the job's requirements. To boost this, focus on: {', '.join(missing[:2])}. Every skill you add increases your competitiveness!"
        elif any(word in question_lower for word in ['improve', 'better', 'increase', 'higher']):
            response = "Great question! Here's my advice: 1) Pick 2-3 high-demand skills aligned with your role, 2) Build 1-2 projects using these skills, 3) Update your resume with concrete examples. This typically boosts your match score by 20-30%!"
        elif any(word in question_lower for word in ['should i learn', 'what', 'skill', 'recommend']):
            response = "Based on your profile, I recommend learning skills that complement what you already know. JavaScript if you know React, or PostgreSQL if you do backend work. This creates a more cohesive skill set employers love!"
        elif any(word in question_lower for word in ['role', 'position', 'job', 'similar']):
            response = "Looking at your profile, you'd be great for roles like: Senior Developer, Technical Lead, or Specialist in your field. Want me to search for specific titles?"
        else:
            default_responses = [
                "That's a great question! Based on what I see in your resume, here's my thinking...",
                "Good point! Let me break this down for you based on your skills and experience...",
                "Interesting! This is where your background really shines. Here's what I'd suggest...",
            ]
            response = random.choice(default_responses)
        self.conversation_history.append({'role': 'bot', 'message': response})
        return response
    
    def generate_job_summary(self, jobs: List[Dict]) -> str:
        if not jobs:
            return "I didn't find any matching jobs right now. Let's upskill and try again soon! 💪"
        excellent = len([j for j in jobs if j.get('match_percentage', 0) >= 80])
        good = len([j for j in jobs if 60 <= j.get('match_percentage', 0) < 80])
        fair = len([j for j in jobs if j.get('match_percentage', 0) < 60])
        response = f"📋 Job Market Summary:\n"
        response += f"🟢 Excellent Matches: {excellent} jobs (80%+)\n"
        response += f"🟡 Good Matches: {good} jobs (60-80%)\n"
        response += f"🟠 Fair Matches: {fair} jobs (<60%)\n\n"
        response += f"Start with the green ones - you're highly qualified for those! ✨"
        self.conversation_history.append({'role': 'bot', 'message': response})
        return response
    
    def generate_encouragement(self) -> str:
        encouragements = [
            "Remember, every expert was once a beginner. Keep learning and growing! 🚀",
            "Your unique combination of skills makes you valuable. Keep pushing! 💪",
            "The job market rewards persistence and continuous learning. You've got this! 🌟",
            "Small progress is still progress. Keep building your skills and opportunities will follow! 📈",
            "Your potential is unlimited. Every skill you learn opens new doors! 🚪✨",
        ]
        response = random.choice(encouragements)
        self.conversation_history.append({'role': 'bot', 'message': response})
        return response
    
    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_history
    
    def clear_conversation(self):
        self.conversation_history = []
    
    def add_user_message(self, message: str):
        self.conversation_history.append({'role': 'user', 'message': message})


if __name__ == "__main__":
    chatbot = CareerAdvisorChatbot()
    profile = {'name': 'Alex', 'skills': ['Python', 'React', 'AWS'], 'experience_years': 3}
    chatbot.set_user_profile(profile)
    print(chatbot.generate_initial_greeting())
    print("\n" + chatbot.explain_job_match("Frontend Developer", "TechCorp", 85, ['React', 'JavaScript'], []))
    print("\n" + chatbot.suggest_improvement(['TypeScript', 'CSS']))