#!/usr/bin/env python3
"""
Integration test for resume analyzer API endpoints
Tests the complete flow from resume upload to job matching
"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from backend.resume_parser import ResumeParser
from backend.skill_extractor import SkillExtractor
from backend.matching_engine import MatchingEngine
from backend.job_scraper import JobScraper
from backend.chatbot import CareerAdvisorChatbot

# Load sample resume
sample_resume_path = r"C:\Users\HP\AI\ResumeChatBot-main\ResumeChatBot-main\ResumeBot\samples\sample_resume.txt"

print("=" * 100)
print("INTEGRATION TEST: RESUME ANALYZER API ENDPOINTS")
print("=" * 100)

# Simulate the /api/upload-resume endpoint
print("\n[TEST 1] Simulating POST /api/upload-resume")
print("-" * 100)

try:
    parser = ResumeParser()
    text, file_type = parser.parse(sample_resume_path)
    
    skill_extractor = SkillExtractor()
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
    
    chatbot = CareerAdvisorChatbot()
    chatbot.set_user_profile(user_profile)
    greeting = chatbot.generate_initial_greeting()
    
    # Simulate API response
    response = {
        "message": "Resume uploaded and analyzed successfully!",
        "resume_data": user_profile,
        "initial_greeting": greeting
    }
    
    print(f"[OK] Response structure:")
    print(f"     Message: {response['message']}")
    print(f"     Resume Data:")
    print(f"       - Skills: {len(user_profile['skills'])} total")
    print(f"       - Experience: {user_profile['experience_years']} years")
    print(f"       - Projects: {len(user_profile['projects'])} found")
    print(f"       - Education: {len(user_profile['education'])} entries")
    print(f"     Initial Greeting: {greeting[:80]}...")
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    sys.exit(1)

# Simulate the /api/search-jobs endpoint
print("\n[TEST 2] Simulating POST /api/search-jobs")
print("-" * 100)

try:
    scraper = JobScraper()
    jobs = scraper.fetch_jobs_by_skills(user_profile['skills'], 'Remote', 10)
    
    # Enrich jobs with match scores
    matcher = MatchingEngine()
    enriched_jobs = []
    
    for job in jobs:
        job_required_skills = job.get('required_skills', [])
        match_result = matcher.calculate_match_score(
            user_profile['skills'],
            job_required_skills,
            user_profile['experience_years'],
            0
        )
        
        enriched_job = {
            **job,
            'match_percentage': match_result['overall_match_percentage'],
            'matched_skills': match_result['matched_skills'],
            'missing_skills': match_result['missing_skills'],
            'match_strength': match_result['match_strength'],
            'recommendation': match_result['recommendation']
        }
        enriched_jobs.append(enriched_job)
    
    # Sort by match percentage
    enriched_jobs.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    # Simulate API response
    response = {"jobs": enriched_jobs}
    
    print(f"[OK] Found {len(response['jobs'])} matching jobs")
    print(f"     Top 3 matches:")
    for i, job in enumerate(response['jobs'][:3], 1):
        print(f"       {i}. {job['title']} @ {job['company']}")
        print(f"          Match: {job['match_percentage']}% ({job['match_strength']})")
        print(f"          Skills: {job['matched_skills'][:3]}... (+{len(job['matched_skills'])-3})")
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    sys.exit(1)

# Simulate the /api/chat endpoint (resume chat)
print("\n[TEST 3] Simulating POST /api/chat")
print("-" * 100)

try:
    # Test various chat scenarios
    test_queries = [
        "Why did I get a 86% match on this job?",
        "What skills should I improve?",
        "What similar roles would be good for me?"
    ]
    
    for query in test_queries:
        # Simulate user message
        chatbot.add_user_message(query)
        
        # Generate response
        if any(word in query.lower() for word in ['why', 'score', 'low', 'percentage']):
            response_text = chatbot.answer_follow_up(query, {'match_percentage': 86, 'missing_skills': ['REST APIs'], 'matched_skills': ['React', 'JavaScript']})
        elif any(word in query.lower() for word in ['improve', 'better', 'learn', 'increase']):
            response_text = chatbot.suggest_improvement(['TypeScript', 'REST APIs'])
        else:
            response_text = chatbot.answer_follow_up(query, {})
        
        response = {
            "bot_reply": response_text,
            "conversation_history": chatbot.get_conversation_history()
        }
        
        print(f"[OK] Query: {query}")
        print(f"     Response: {response_text[:100]}...")
        print()
    
except Exception as e:
    print(f"[FAIL] Error: {e}")
    sys.exit(1)

print("=" * 100)
print("[OK] ALL INTEGRATION TESTS PASSED!")
print("=" * 100)

print("\n[SUMMARY] Expected frontend behavior:")
print("  1. User uploads resume")
print("  2. Left panel displays: Skills, Experience, Projects")
print("  3. Center displays: Bot greeting + chat area")
print("  4. Right panel displays: Job matches with percentages")
print("  5. User can ask follow-up questions in chat")
print("  6. All responses are personalized based on resume data")
