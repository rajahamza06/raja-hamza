#!/usr/bin/env python3
"""
Remote Job Agent - AI-powered tool to find remote job opportunities
Provides agency information, emails, and job links for hourly remote positions
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
import argparse
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import csv

@dataclass
class JobOpportunity:
    """Data class for job opportunity information"""
    title: str
    company: str
    agency: str
    email: str
    job_url: str
    hourly_rate: Optional[str]
    location: str
    job_type: str
    posted_date: str
    description: str
    requirements: List[str]

class RemoteJobAgent:
    """AI agent for finding remote job opportunities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Job board APIs and endpoints
        self.job_sources = {
            'indeed': 'https://www.indeed.com/jobs',
            'upwork': 'https://www.upwork.com/search/jobs/',
            'fiverr': 'https://www.fiverr.com/search/gigs',
            'freelancer': 'https://www.freelancer.com/jobs/',
            'guru': 'https://www.guru.com/freelancers/',
            'toptal': 'https://www.toptal.com/freelancers',
            'remote_co': 'https://remote.co/remote-jobs/',
            'flexjobs': 'https://www.flexjobs.com/search',
            'weworkremotely': 'https://weworkremotely.com/remote-jobs/search',
            'remote_ok': 'https://remoteok.io/remote-dev-jobs'
        }
        
        # Keywords for hourly/remote jobs
        self.hourly_keywords = [
            'hourly', 'per hour', '$/hr', 'hourly rate', 'hourly pay',
            'remote', 'work from home', 'telecommute', 'virtual',
            'freelance', 'contract', 'part-time', 'flexible hours'
        ]
    
    def search_indeed_jobs(self, query: str = "remote hourly", location: str = "Remote") -> List[JobOpportunity]:
        """Search Indeed for remote hourly jobs"""
        jobs = []
        try:
            params = {
                'q': query,
                'l': location,
                'sc': '0kf%3Aattr(DSQF7)%3B',  # Remote filter
                'sort': 'date'
            }
            
            response = self.session.get(self.job_sources['indeed'], params=params)
            if response.status_code == 200:
                # Parse HTML response for job listings
                # This is a simplified version - in production you'd use BeautifulSoup
                jobs = self._parse_indeed_jobs(response.text)
                
        except Exception as e:
            print(f"Error searching Indeed: {e}")
        
        return jobs
    
    def search_upwork_jobs(self, query: str = "remote hourly") -> List[JobOpportunity]:
        """Search Upwork for remote hourly jobs"""
        jobs = []
        try:
            params = {
                'q': query,
                'hourly_rate': 'true',
                'work_type': 'remote'
            }
            
            response = self.session.get(self.job_sources['upwork'], params=params)
            if response.status_code == 200:
                jobs = self._parse_upwork_jobs(response.text)
                
        except Exception as e:
            print(f"Error searching Upwork: {e}")
        
        return jobs
    
    def search_remote_co_jobs(self, query: str = "hourly") -> List[JobOpportunity]:
        """Search Remote.co for hourly remote jobs"""
        jobs = []
        try:
            params = {
                'search': query,
                'location': 'Remote',
                'type': 'hourly'
            }
            
            response = self.session.get(self.job_sources['remote_co'], params=params)
            if response.status_code == 200:
                jobs = self._parse_remote_co_jobs(response.text)
                
        except Exception as e:
            print(f"Error searching Remote.co: {e}")
        
        return jobs
    
    def _parse_indeed_jobs(self, html_content: str) -> List[JobOpportunity]:
        """Parse Indeed HTML for job listings"""
        jobs = []
        # This is a placeholder - in production you'd use BeautifulSoup to parse HTML
        # For now, we'll return sample data
        sample_jobs = [
            JobOpportunity(
                title="Remote Web Developer",
                company="TechCorp Inc",
                agency="TechCorp Inc",
                email="jobs@techcorp.com",
                job_url="https://indeed.com/viewjob?jk=12345",
                hourly_rate="$45-65/hr",
                location="Remote",
                job_type="Contract",
                posted_date="2024-01-15",
                description="Looking for experienced web developer for remote work",
                requirements=["JavaScript", "React", "Node.js", "3+ years experience"]
            ),
            JobOpportunity(
                title="Hourly Content Writer",
                company="Content Agency",
                agency="Content Agency",
                email="hiring@contentagency.com",
                job_url="https://indeed.com/viewjob?jk=67890",
                hourly_rate="$25-40/hr",
                location="Remote",
                job_type="Part-time",
                posted_date="2024-01-14",
                description="Remote content writing position with flexible hours",
                requirements=["Excellent writing skills", "SEO knowledge", "Portfolio required"]
            )
        ]
        return sample_jobs
    
    def _parse_upwork_jobs(self, html_content: str) -> List[JobOpportunity]:
        """Parse Upwork HTML for job listings"""
        jobs = []
        # Placeholder for Upwork parsing
        sample_jobs = [
            JobOpportunity(
                title="Freelance Graphic Designer",
                company="Design Studio",
                agency="Design Studio",
                email="contact@designstudio.com",
                job_url="https://upwork.com/jobs/~0123456789",
                hourly_rate="$30-50/hr",
                location="Remote",
                job_type="Freelance",
                posted_date="2024-01-15",
                description="Remote graphic design work for various clients",
                requirements=["Adobe Creative Suite", "Portfolio", "Communication skills"]
            )
        ]
        return sample_jobs
    
    def _parse_remote_co_jobs(self, html_content: str) -> List[JobOpportunity]:
        """Parse Remote.co HTML for job listings"""
        jobs = []
        # Placeholder for Remote.co parsing
        sample_jobs = [
            JobOpportunity(
                title="Remote Customer Support",
                company="Support Solutions",
                agency="Support Solutions",
                email="careers@supportsolutions.com",
                job_url="https://remote.co/job/12345",
                hourly_rate="$18-25/hr",
                location="Remote",
                job_type="Full-time",
                posted_date="2024-01-15",
                description="Remote customer support position with flexible scheduling",
                requirements=["Customer service experience", "Good communication", "Computer skills"]
            )
        ]
        return sample_jobs
    
    def extract_company_info(self, company_name: str) -> Dict[str, str]:
        """Extract company/agency information including email"""
        company_info = {
            'name': company_name,
            'email': '',
            'website': '',
            'phone': ''
        }
        
        # Try to find company website and contact info
        try:
            # This would typically involve searching company databases
            # For now, we'll use some common patterns
            if 'tech' in company_name.lower():
                company_info['email'] = f"jobs@{company_name.lower().replace(' ', '')}.com"
            elif 'agency' in company_name.lower():
                company_info['email'] = f"hiring@{company_name.lower().replace(' ', '')}.com"
            else:
                company_info['email'] = f"careers@{company_name.lower().replace(' ', '')}.com"
                
        except Exception as e:
            print(f"Error extracting company info: {e}")
        
        return company_info
    
    def search_all_sources(self, query: str = "remote hourly", max_results: int = 50) -> List[JobOpportunity]:
        """Search all job sources and return combined results"""
        all_jobs = []
        
        print(f"🔍 Searching for '{query}' jobs across multiple platforms...")
        
        # Search Indeed
        print("📊 Searching Indeed...")
        indeed_jobs = self.search_indeed_jobs(query)
        all_jobs.extend(indeed_jobs)
        
        # Search Upwork
        print("💼 Searching Upwork...")
        upwork_jobs = self.search_upwork_jobs(query)
        all_jobs.extend(upwork_jobs)
        
        # Search Remote.co
        print("🏠 Searching Remote.co...")
        remote_co_jobs = self.search_remote_co_jobs(query)
        all_jobs.extend(remote_co_jobs)
        
        # Remove duplicates and sort by date
        unique_jobs = self._remove_duplicates(all_jobs)
        sorted_jobs = sorted(unique_jobs, key=lambda x: x.posted_date, reverse=True)
        
        return sorted_jobs[:max_results]
    
    def _remove_duplicates(self, jobs: List[JobOpportunity]) -> List[JobOpportunity]:
        """Remove duplicate job postings"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a unique identifier for each job
            job_id = f"{job.title}_{job.company}_{job.job_url}"
            if job_id not in seen:
                seen.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def export_to_csv(self, jobs: List[JobOpportunity], filename: str = "remote_jobs.csv"):
        """Export job opportunities to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'title', 'company', 'agency', 'email', 'job_url', 
                    'hourly_rate', 'location', 'job_type', 'posted_date', 
                    'description', 'requirements'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for job in jobs:
                    writer.writerow({
                        'title': job.title,
                        'company': job.company,
                        'agency': job.agency,
                        'email': job.email,
                        'job_url': job.job_url,
                        'hourly_rate': job.hourly_rate,
                        'location': job.location,
                        'job_type': job.job_type,
                        'posted_date': job.posted_date,
                        'description': job.description,
                        'requirements': '; '.join(job.requirements)
                    })
            
            print(f"✅ Jobs exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
    
    def display_jobs(self, jobs: List[JobOpportunity], detailed: bool = False):
        """Display job opportunities in a formatted way"""
        if not jobs:
            print("❌ No jobs found matching your criteria.")
            return
        
        print(f"\n🎯 Found {len(jobs)} remote job opportunities:\n")
        print("=" * 80)
        
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Agency: {job.agency}")
            print(f"   Email: {job.email}")
            print(f"   Rate: {job.hourly_rate or 'Not specified'}")
            print(f"   Location: {job.location}")
            print(f"   Type: {job.job_type}")
            print(f"   Posted: {job.posted_date}")
            print(f"   Job URL: {job.job_url}")
            
            if detailed:
                print(f"   Description: {job.description}")
                print(f"   Requirements: {', '.join(job.requirements)}")
            
            print("-" * 40)
    
    def get_job_recommendations(self, skills: List[str], preferred_rate: str = None) -> List[JobOpportunity]:
        """Get personalized job recommendations based on skills"""
        print(f"🎯 Getting personalized recommendations for skills: {', '.join(skills)}")
        
        # Search with relevant keywords
        query = f"remote {' '.join(skills)} hourly"
        jobs = self.search_all_sources(query, max_results=30)
        
        # Filter by preferred rate if specified
        if preferred_rate:
            filtered_jobs = []
            for job in jobs:
                if job.hourly_rate and self._rate_matches_preference(job.hourly_rate, preferred_rate):
                    filtered_jobs.append(job)
            jobs = filtered_jobs
        
        return jobs
    
    def _rate_matches_preference(self, job_rate: str, preferred_rate: str) -> bool:
        """Check if job rate matches preferred rate range"""
        try:
            # Extract numeric values from rate strings
            job_nums = re.findall(r'\d+', job_rate)
            pref_nums = re.findall(r'\d+', preferred_rate)
            
            if job_nums and pref_nums:
                job_min = min(map(int, job_nums))
                pref_min = min(map(int, pref_nums))
                return job_min >= pref_min
        except:
            pass
        
        return True

def main():
    """Main function to run the Remote Job Agent"""
    parser = argparse.ArgumentParser(description='Remote Job Agent - Find remote hourly job opportunities')
    parser.add_argument('--query', default='remote hourly', help='Search query for jobs')
    parser.add_argument('--skills', nargs='+', help='Your skills for personalized recommendations')
    parser.add_argument('--rate', help='Preferred hourly rate (e.g., "$30+")')
    parser.add_argument('--export', help='Export results to CSV file')
    parser.add_argument('--detailed', action='store_true', help='Show detailed job information')
    parser.add_argument('--max-results', type=int, default=20, help='Maximum number of results')
    
    args = parser.parse_args()
    
    # Initialize the agent
    agent = RemoteJobAgent()
    
    print("🤖 Remote Job Agent - Finding your next remote opportunity!")
    print("=" * 60)
    
    if args.skills:
        # Get personalized recommendations
        jobs = agent.get_job_recommendations(args.skills, args.rate)
    else:
        # General search
        jobs = agent.search_all_sources(args.query, args.max_results)
    
    # Display results
    agent.display_jobs(jobs, args.detailed)
    
    # Export if requested
    if args.export:
        agent.export_to_csv(jobs, args.export)
    
    print(f"\n✨ Search completed! Found {len(jobs)} opportunities.")
    print("💡 Tip: Use --skills and --rate for personalized recommendations")

if __name__ == "__main__":
    main()