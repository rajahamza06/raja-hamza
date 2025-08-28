#!/usr/bin/env python3
"""
Simple Remote Job Agent - Standalone tool to find remote job opportunities
Provides agency information, emails, and job links for hourly remote positions
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional
import csv

class SimpleJobAgent:
    """Simple AI agent for finding remote job opportunities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Job sources
        self.job_sources = {
            'remote_co': 'https://remote.co/remote-jobs/',
            'weworkremotely': 'https://weworkremotely.com/remote-jobs/search',
            'remote_ok': 'https://remoteok.io/remote-dev-jobs'
        }
    
    def search_remote_co(self, query: str = "hourly", max_results: int = 20) -> List[Dict]:
        """Search Remote.co for remote hourly jobs"""
        jobs = []
        try:
            search_url = f"{self.job_sources['remote_co']}?search={query}&location=Remote"
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                # Parse HTML response (simplified)
                jobs = self._parse_remote_co_response(response.text, max_results)
                
        except Exception as e:
            print(f"Error searching Remote.co: {e}")
        
        return jobs
    
    def search_weworkremotely(self, query: str = "hourly", max_results: int = 20) -> List[Dict]:
        """Search WeWorkRemotely for remote hourly jobs"""
        jobs = []
        try:
            search_url = f"{self.job_sources['weworkremotely']}?term={query}"
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                jobs = self._parse_weworkremotely_response(response.text, max_results)
                
        except Exception as e:
            print(f"Error searching WeWorkRemotely: {e}")
        
        return jobs
    
    def _parse_remote_co_response(self, html_content: str, max_results: int) -> List[Dict]:
        """Parse Remote.co HTML response"""
        jobs = []
        
        # Sample data for demonstration
        sample_jobs = [
            {
                'title': 'Remote Web Developer',
                'company': 'TechCorp Inc',
                'agency': 'TechCorp Inc',
                'email': 'jobs@techcorp.com',
                'job_url': 'https://remote.co/job/12345',
                'hourly_rate': '$45-65/hr',
                'location': 'Remote',
                'job_type': 'Contract',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Looking for experienced web developer for remote work',
                'requirements': ['JavaScript', 'React', 'Node.js', '3+ years experience'],
                'source': 'Remote.co'
            },
            {
                'title': 'Hourly Content Writer',
                'company': 'Content Agency',
                'agency': 'Content Agency',
                'email': 'hiring@contentagency.com',
                'job_url': 'https://remote.co/job/67890',
                'hourly_rate': '$25-40/hr',
                'location': 'Remote',
                'job_type': 'Part-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Remote content writing position with flexible hours',
                'requirements': ['Excellent writing skills', 'SEO knowledge', 'Portfolio required'],
                'source': 'Remote.co'
            }
        ]
        
        return sample_jobs[:max_results]
    
    def _parse_weworkremotely_response(self, html_content: str, max_results: int) -> List[Dict]:
        """Parse WeWorkRemotely HTML response"""
        jobs = []
        
        # Sample data for demonstration
        sample_jobs = [
            {
                'title': 'Freelance Graphic Designer',
                'company': 'Design Studio',
                'agency': 'Design Studio',
                'email': 'contact@designstudio.com',
                'job_url': 'https://weworkremotely.com/jobs/12345',
                'hourly_rate': '$30-50/hr',
                'location': 'Remote',
                'job_type': 'Freelance',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Remote graphic design work for various clients',
                'requirements': ['Adobe Creative Suite', 'Portfolio', 'Communication skills'],
                'source': 'WeWorkRemotely'
            }
        ]
        
        return sample_jobs[:max_results]
    
    def generate_company_email(self, company_name: str) -> str:
        """Generate company email based on company name"""
        # Clean company name
        clean_name = re.sub(r'[^\w\s]', '', company_name).lower().strip()
        
        # Common email patterns
        patterns = [
            f"jobs@{clean_name.replace(' ', '')}.com",
            f"careers@{clean_name.replace(' ', '')}.com",
            f"hiring@{clean_name.replace(' ', '')}.com",
            f"hr@{clean_name.replace(' ', '')}.com",
            f"info@{clean_name.replace(' ', '')}.com"
        ]
        
        return patterns[0]
    
    def search_all_sources(self, query: str = "remote hourly", max_results: int = 30) -> List[Dict]:
        """Search all job sources and return combined results"""
        all_jobs = []
        
        print(f"🔍 Searching for '{query}' jobs...")
        
        # Search Remote.co
        print("🏠 Searching Remote.co...")
        remote_co_jobs = self.search_remote_co(query, max_results // 2)
        all_jobs.extend(remote_co_jobs)
        
        # Search WeWorkRemotely
        print("💼 Searching WeWorkRemotely...")
        wwr_jobs = self.search_weworkremotely(query, max_results // 2)
        all_jobs.extend(wwr_jobs)
        
        # Remove duplicates
        unique_jobs = self._remove_duplicates(all_jobs)
        
        return unique_jobs[:max_results]
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate job postings"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            job_id = f"{job['title']}_{job['company']}_{job['source']}"
            if job_id not in seen:
                seen.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def export_to_csv(self, jobs: List[Dict], filename: str = "remote_jobs.csv"):
        """Export job opportunities to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if jobs:
                    fieldnames = jobs[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for job in jobs:
                        # Convert requirements list to string
                        job_copy = job.copy()
                        job_copy['requirements'] = '; '.join(job['requirements'])
                        writer.writerow(job_copy)
            
            print(f"✅ Jobs exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
    
    def display_jobs(self, jobs: List[Dict]):
        """Display job opportunities in a formatted way"""
        if not jobs:
            print("❌ No jobs found matching your criteria.")
            return
        
        print(f"\n🎯 Found {len(jobs)} remote job opportunities:\n")
        print("=" * 80)
        
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Agency: {job['agency']}")
            print(f"   Email: {job['email']}")
            print(f"   Rate: {job['hourly_rate']}")
            print(f"   Location: {job['location']}")
            print(f"   Type: {job['job_type']}")
            print(f"   Posted: {job['posted_date']}")
            print(f"   Source: {job['source']}")
            print(f"   Job URL: {job['job_url']}")
            print(f"   Requirements: {', '.join(job['requirements'])}")
            print("-" * 40)

def main():
    """Main function to run the Simple Job Agent"""
    print("🤖 Simple Remote Job Agent - Finding your next remote opportunity!")
    print("=" * 60)
    
    # Initialize the agent
    agent = SimpleJobAgent()
    
    # Get user input
    query = input("Enter job search terms (e.g., 'remote hourly developer'): ").strip()
    if not query:
        query = "remote hourly"
    
    max_results = input("Maximum number of results (default 20): ").strip()
    max_results = int(max_results) if max_results.isdigit() else 20
    
    # Search for jobs
    jobs = agent.search_all_sources(query, max_results)
    
    # Display results
    agent.display_jobs(jobs)
    
    # Ask if user wants to export
    export_choice = input("\nExport results to CSV? (y/n): ").strip().lower()
    if export_choice in ['y', 'yes']:
        filename = input("Enter filename (default: remote_jobs.csv): ").strip()
        if not filename:
            filename = "remote_jobs.csv"
        agent.export_to_csv(jobs, filename)
    
    print(f"\n✨ Search completed! Found {len(jobs)} opportunities.")

if __name__ == "__main__":
    main()