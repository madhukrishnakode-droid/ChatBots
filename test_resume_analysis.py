#!/usr/bin/env python3
"""
Test script to verify resume analyzer output matches expected format
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.resume_parser import ResumeParser
from backend.skill_extractor import SkillExtractor
from backend.matching_engine import MatchingEngine
from backend.job_scraper import JobScraper
from backend.chatbot import CareerAdvisorChatbot

# Load sample resume
sample_resume_path = r"C:\Users\HP\AI\ResumeChatBot-main\ResumeChatBot-main\ResumeBot\samples\sample_resume.txt"

print("=" * 80)
print("RESUME ANALYZER TEST")
print("=" * 80)

# Test 1: Parse Resume
print("\n[1] PARSING RESUME...")
parser = ResumeParser()
try:
    text, file_type = parser.parse(sample_resume_path)
    print(f"[OK] Resume parsed successfully (format: {file_type})")
    print(f"     Text length: {len(text)} characters")
except Exception as e:
    print(f"[FAIL] Resume parsing failed: {e}")
    sys.exit(1)

# Test 2: Extract Skills
print("\n[2] EXTRACTING SKILLS...")
extractor = SkillExtractor()
try:
    skills_dict = extractor.extract_skills(text)
    print(f"[OK] Skills extracted successfully")
    print(f"     Categories: {list(skills_dict.keys())}")
    for category, skills in skills_dict.items():
        print(f"       {category}: {skills}")
except Exception as e:
    print(f"[FAIL] Skill extraction failed: {e}")
    sys.exit(1)

# Test 3: Get Skill Summary
print("\n[3] GETTING SKILL SUMMARY...")
try:
    skill_summary = extractor.get_skill_summary(text)
    print(f"[OK] Skill summary generated")
    print(f"     Total skills: {skill_summary.get('total_skills', 0)}")
    print(f"     Experience years: {skill_summary.get('experience_years', 0)}")
    print(f"     Projects: {len(skill_summary.get('projects', []))} found")
    print(f"     Education: {skill_summary.get('education', [])}")
except Exception as e:
    print(f"[FAIL] Skill summary failed: {e}")
    sys.exit(1)

# Test 4: Get Flat Skills
print("\n[4] GETTING FLAT SKILLS LIST...")
try:
    flat_skills = extractor.get_flat_skills()
    print(f"[OK] Flat skills list generated")
    print(f"     Count: {len(flat_skills)}")
    print(f"     Skills: {flat_skills[:10]}...")  # Show first 10
except Exception as e:
    print(f"[FAIL] Flat skills failed: {e}")
    sys.exit(1)

# Test 5: Create User Profile (simulating backend)
print("\n[5] CREATING USER PROFILE...")
try:
    user_profile = {
        'name': 'Job Seeker',
        'resume_text': text[:500],
        'skills': flat_skills,
        'experience_years': skill_summary.get('experience_years', 0),
        'projects': skill_summary.get('projects', []),
        'education': skill_summary.get('education', []),
        'file_type': file_type,
    }
    print(f"[OK] User profile created")
    print(f"     Name: {user_profile['name']}")
    print(f"     Skills count: {len(user_profile['skills'])}")
    print(f"     Experience: {user_profile['experience_years']} years")
    print(f"     Projects: {len(user_profile['projects'])}")
except Exception as e:
    print(f"[FAIL] User profile creation failed: {e}")
    sys.exit(1)

# Test 6: Generate Initial Greeting
print("\n[6] GENERATING INITIAL GREETING...")
try:
    chatbot = CareerAdvisorChatbot()
    chatbot.set_user_profile(user_profile)
    greeting = chatbot.generate_initial_greeting()
    print(f"[OK] Initial greeting generated")
    print(f"     Message: {greeting[:100]}...")
except Exception as e:
    print(f"[FAIL] Greeting generation failed: {e}")
    sys.exit(1)

# Test 7: Search for Jobs
print("\n[7] SEARCHING FOR JOBS...")
try:
    scraper = JobScraper()
    jobs = scraper.fetch_jobs_by_skills(user_profile['skills'], 'Remote', 10)
    print(f"[OK] Jobs fetched")
    print(f"     Count: {len(jobs)}")
    if jobs:
        print(f"     First job: {jobs[0].get('title')} at {jobs[0].get('company')}")
except Exception as e:
    print(f"[FAIL] Job search failed: {e}")
    sys.exit(1)

# Test 8: Calculate Match Scores
print("\n[8] CALCULATING JOB MATCH SCORES...")
try:
    matcher = MatchingEngine()
    if jobs:
        first_job = jobs[0]
        match_result = matcher.calculate_match_score(
            user_profile['skills'],
            first_job.get('required_skills', []),
            user_profile['experience_years'],
            0
        )
        print(f"[OK] Match score calculated")
        print(f"     Overall match: {match_result['overall_match_percentage']}%")
        print(f"     Matched skills: {match_result['matched_skills']}")
        print(f"     Missing skills: {match_result['missing_skills']}")
except Exception as e:
    print(f"[FAIL] Match calculation failed: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("[OK] ALL TESTS PASSED!")
print("=" * 80)
print("\nExpected frontend display should show:")
print(f"  Skills: {len(user_profile['skills'])} total")
print(f"  Experience: {user_profile['experience_years']} years")
print(f"  Projects: {len(user_profile['projects'])} projects")
print(f"  Bot greeting: Personalized message with name and experience")
print(f"  Jobs: Multiple job cards with match percentages")
