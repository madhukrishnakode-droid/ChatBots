"""
Job Scraper Module
Fetches job listings from free sources (web scraping + free APIs)
"""

import requests
import json
import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class JobScraper:
    """
    Scrapes job listings from free sources
    Currently uses mock data and can be extended with real APIs
    """
    
    def __init__(self):
        self.jobs = []
    
    def fetch_jobs_by_skills(self, skills: List[str], location: str = "Remote", limit: int = 10) -> List[Dict]:
        """
        Fetch job listings based on required skills
        """
        logger.info(f"Searching jobs for skills: {skills}")
        jobs = self._fetch_from_free_api(skills, location, limit)
        if not jobs or len(jobs) < limit:
            mock_jobs = self._get_mock_jobs(skills, limit)
            jobs.extend(mock_jobs[:limit - len(jobs)])
        self.jobs = jobs[:limit]
        return self.jobs
    
    def _fetch_from_free_api(self, skills: List[str], location: str, limit: int) -> List[Dict]:
        jobs = []
        try:
            for skill in skills[:3]:
                url = f"https://justjoinit.careers/api/offers"
                params = {
                    'limit': 5,
                    'skill': skill.lower()
                }
        except Exception as e:
            logger.warning(f"Free API fetch failed: {str(e)}")
        return jobs
    
    def _parse_job_api(self, job_data: Dict) -> Dict:
        return {
            'title': job_data.get('title', 'Unknown'),
            'company': job_data.get('company', 'Unknown'),
            'location': job_data.get('location', 'Remote'),
            'description': job_data.get('description', ''),
            'required_skills': job_data.get('skills', []),
            'salary': job_data.get('salary', 'Not specified'),
            'url': job_data.get('url', ''),
            'source': 'API'
        }
    
    def _get_mock_jobs(self, skills: List[str], limit: int) -> List[Dict]:
        mock_jobs = [
            {
                'title': 'Senior Frontend Developer',
                'company': 'TechCorp',
                'location': 'San Francisco, CA',
                'description': 'Looking for experienced React developer with 5+ years of experience.',
                'required_skills': ['React', 'JavaScript', 'CSS', 'REST APIs', 'Git'],
                'salary': '$120,000 - $160,000',
                'url': 'https://example.com/job1',
                'source': 'Mock'
            },
            {
                'title': 'Backend Developer - Python',
                'company': 'StartupX',
                'location': 'Remote',
                'description': 'We are hiring Python developers for our FastAPI microservices.',
                'required_skills': ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS'],
                'salary': '$100,000 - $140,000',
                'url': 'https://example.com/job2',
                'source': 'Mock'
            },
            {
                'title': 'Full Stack Developer',
                'company': 'FinTech Solutions',
                'location': 'New York, NY',
                'description': 'Build scalable web applications using modern tech stack.',
                'required_skills': ['JavaScript', 'React', 'Node.js', 'MongoDB', 'Docker'],
                'salary': '$110,000 - $150,000',
                'url': 'https://example.com/job3',
                'source': 'Mock'
            },
            {
                'title': 'Data Scientist',
                'company': 'AI Labs',
                'location': 'Boston, MA',
                'description': 'Work on machine learning models for predictive analytics.',
                'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'pandas', 'SQL'],
                'salary': '$130,000 - $170,000',
                'url': 'https://example.com/job4',
                'source': 'Mock'
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudServices Inc',
                'location': 'Remote',
                'description': 'Manage and optimize cloud infrastructure on AWS and Kubernetes.',
                'required_skills': ['Docker', 'Kubernetes', 'AWS', 'Linux', 'CI/CD'],
                'salary': '$115,000 - $155,000',
                'url': 'https://example.com/job5',
                'source': 'Mock'
            },
            {
                'title': 'Machine Learning Engineer',
                'company': 'DeepTech Corp',
                'location': 'San Jose, CA',
                'description': 'Develop and deploy ML models for computer vision applications.',
                'required_skills': ['Python', 'PyTorch', 'Computer Vision', 'Deep Learning', 'TensorFlow'],
                'salary': '$140,000 - $190,000',
                'url': 'https://example.com/job6',
                'source': 'Mock'
            },
            {
                'title': 'Frontend Engineer (React)',
                'company': 'Design Co',
                'location': 'Austin, TX',
                'description': 'Build beautiful and responsive user interfaces.',
                'required_skills': ['React', 'TypeScript', 'CSS', 'REST APIs', 'Testing'],
                'salary': '$105,000 - $145,000',
                'url': 'https://example.com/job7',
                'source': 'Mock'
            },
            {
                'title': 'Cloud Architect',
                'company': 'Enterprise Systems',
                'location': 'Seattle, WA',
                'description': 'Design and implement cloud infrastructure solutions.',
                'required_skills': ['AWS', 'Azure', 'Terraform', 'CI/CD', 'Kubernetes'],
                'salary': '$150,000 - $200,000',
                'url': 'https://example.com/job8',
                'source': 'Mock'
            },
            {
                'title': 'Junior Python Developer',
                'company': 'Code Academy',
                'location': 'Remote',
                'description': 'Start your career as a Python developer with mentorship.',
                'required_skills': ['Python', 'Flask', 'REST APIs', 'SQL', 'Git'],
                'salary': '$60,000 - $85,000',
                'url': 'https://example.com/job9',
                'source': 'Mock'
            },
            {
                'title': 'QA Automation Engineer',
                'company': 'Quality Systems',
                'location': 'Chicago, IL',
                'description': 'Automate testing for web applications.',
                'required_skills': ['Python', 'Selenium', 'Testing', 'CI/CD', 'Git'],
                'salary': '$80,000 - $120,000',
                'url': 'https://example.com/job10',
                'source': 'Mock'
            },
        ]
        filtered_jobs = []
        for job in mock_jobs:
            job_skills = [s.lower() for s in job['required_skills']]
            if any(skill.lower() in job_skills for skill in skills):
                filtered_jobs.append(job)
        if not filtered_jobs:
            return mock_jobs[:limit]
        return filtered_jobs[:limit]
