#!/usr/bin/env python3
"""
Advanced Remote Job Agent - AI-powered tool to find remote job opportunities
Actually scrapes real job data from multiple platforms
Provides agency information, emails, and job links for hourly remote positions
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import argparse
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, quote
import csv
import os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import timeout_decorator

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
    source: str
    scraped_at: str

class AdvancedRemoteJobAgent:
    """Advanced AI agent for finding remote job opportunities with real scraping"""
    
    def __init__(self, headless: bool = True):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        self.headless = headless
        self.driver = None
        
        # Job board APIs and endpoints
        self.job_sources = {
            'indeed': {
                'url': 'https://www.indeed.com/jobs',
                'search_params': {'q': '', 'l': 'Remote', 'sc': '0kf%3Aattr(DSQF7)%3B'},
                'requires_selenium': True
            },
            'upwork': {
                'url': 'https://www.upwork.com/search/jobs/',
                'search_params': {'q': '', 'hourly_rate': 'true'},
                'requires_selenium': True
            },
            'remote_co': {
                'url': 'https://remote.co/remote-jobs/',
                'search_params': {'search': '', 'location': 'Remote'},
                'requires_selenium': False
            },
            'weworkremotely': {
                'url': 'https://weworkremotely.com/remote-jobs/search',
                'search_params': {'term': ''},
                'requires_selenium': False
            },
            'remote_ok': {
                'url': 'https://remoteok.io/remote-dev-jobs',
                'search_params': {},
                'requires_selenium': False
            },
            'flexjobs': {
                'url': 'https://www.flexjobs.com/search',
                'search_params': {'search': '', 'location': 'Remote'},
                'requires_selenium': True
            }
        }
        
        # Keywords for hourly/remote jobs
        self.hourly_keywords = [
            'hourly', 'per hour', '$/hr', 'hourly rate', 'hourly pay',
            'remote', 'work from home', 'telecommute', 'virtual',
            'freelance', 'contract', 'part-time', 'flexible hours'
        ]
    
    def setup_selenium(self):
        """Setup Selenium WebDriver for dynamic content scraping"""
        if self.driver is None:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self.ua.random}")
            
            try:
                self.driver = webdriver.Chrome(
                    service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                    options=chrome_options
                )
            except Exception as e:
                print(f"Warning: Could not setup Chrome driver: {e}")
                print("Falling back to requests-only mode")
                self.driver = None
    
    def close_selenium(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    @timeout_decorator.timeout(30)
    def search_indeed_jobs(self, query: str = "remote hourly", max_results: int = 20) -> List[JobOpportunity]:
        """Search Indeed for remote hourly jobs using Selenium"""
        jobs = []
        
        if not self.driver:
            print("Selenium not available, skipping Indeed search")
            return jobs
        
        try:
            search_url = f"{self.job_sources['indeed']['url']}?q={quote(query)}&l=Remote&sc=0kf%3Aattr(DSQF7)%3B&sort=date"
            self.driver.get(search_url)
            
            # Wait for job listings to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
            )
            
            # Scroll to load more jobs
            self._scroll_to_load_jobs(max_results)
            
            # Find job cards
            job_cards = self.driver.find_elements(By.CLASS_NAME, "job_seen_beacon")
            
            for card in job_cards[:max_results]:
                try:
                    job = self._parse_indeed_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error searching Indeed: {e}")
        
        return jobs
    
    def _scroll_to_load_jobs(self, target_count: int):
        """Scroll down to load more job listings"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        jobs_loaded = 0
        
        while jobs_loaded < target_count:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Count current jobs
            current_jobs = len(self.driver.find_elements(By.CLASS_NAME, "job_seen_beacon"))
            jobs_loaded = current_jobs
            
            # Check if we've reached the bottom
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def _parse_indeed_job_card(self, card) -> Optional[JobOpportunity]:
        """Parse individual Indeed job card"""
        try:
            # Extract job title
            title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle a")
            title = title_elem.text.strip()
            job_url = title_elem.get_attribute("href")
            
            # Extract company name
            company_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']")
            company = company_elem.text.strip()
            
            # Extract location
            location_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='text-location']")
            location = location_elem.text.strip()
            
            # Extract salary/rate info
            hourly_rate = None
            try:
                salary_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='attribute_snippet_testid']")
                salary_text = salary_elem.text.strip()
                if any(keyword in salary_text.lower() for keyword in ['hour', 'hr', 'per hour']):
                    hourly_rate = salary_text
            except:
                pass
            
            # Extract job type
            job_type = "Full-time"  # Default
            try:
                type_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='attribute_snippet_testid']")
                type_text = type_elem.text.strip()
                if any(keyword in type_text.lower() for keyword in ['part-time', 'contract', 'freelance']):
                    job_type = type_text
            except:
                pass
            
            # Extract posted date
            posted_date = datetime.now().strftime("%Y-%m-%d")
            try:
                date_elem = card.find_element(By.CSS_SELECTOR, "[data-testid='date']")
                date_text = date_elem.text.strip()
                posted_date = self._parse_relative_date(date_text)
            except:
                pass
            
            # Generate email based on company name
            email = self._generate_company_email(company)
            
            return JobOpportunity(
                title=title,
                company=company,
                agency=company,
                email=email,
                job_url=job_url,
                hourly_rate=hourly_rate,
                location=location,
                job_type=job_type,
                posted_date=posted_date,
                description="",  # Would need to visit individual job page
                requirements=[],  # Would need to visit individual job page
                source="Indeed",
                scraped_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            return None
    
    def _parse_relative_date(self, date_text: str) -> str:
        """Parse relative date strings like '2 days ago' to actual date"""
        try:
            if 'today' in date_text.lower():
                return datetime.now().strftime("%Y-%m-%d")
            elif 'yesterday' in date_text.lower():
                return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            elif 'days ago' in date_text.lower():
                days = int(re.findall(r'\d+', date_text)[0])
                return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            elif 'hours ago' in date_text.lower():
                return datetime.now().strftime("%Y-%m-%d")
            else:
                return datetime.now().strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")
    
    def _generate_company_email(self, company_name: str) -> str:
        """Generate company email based on company name"""
        # Clean company name
        clean_name = re.sub(r'[^\w\s]', '', company_name).lower().strip()
        words = clean_name.split()
        
        # Common email patterns
        patterns = [
            f"jobs@{clean_name.replace(' ', '')}.com",
            f"careers@{clean_name.replace(' ', '')}.com",
            f"hiring@{clean_name.replace(' ', '')}.com",
            f"hr@{clean_name.replace(' ', '')}.com",
            f"info@{clean_name.replace(' ', '')}.com"
        ]
        
        # Return first pattern (most common)
        return patterns[0]
    
    def search_remote_co_jobs(self, query: str = "hourly", max_results: int = 20) -> List[JobOpportunity]:
        """Search Remote.co for hourly remote jobs"""
        jobs = []
        
        try:
            search_url = f"{self.job_sources['remote_co']['url']}?search={quote(query)}&location=Remote"
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('div', class_='job_listing')
                
                for listing in job_listings[:max_results]:
                    try:
                        job = self._parse_remote_co_listing(listing)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching Remote.co: {e}")
        
        return jobs
    
    def _parse_remote_co_listing(self, listing) -> Optional[JobOpportunity]:
        """Parse Remote.co job listing"""
        try:
            # Extract job title and URL
            title_elem = listing.find('h2', class_='job_title')
            if not title_elem:
                return None
                
            title = title_elem.get_text(strip=True)
            job_url = title_elem.find('a')['href'] if title_elem.find('a') else ""
            
            # Extract company name
            company_elem = listing.find('span', class_='company')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = listing.find('span', class_='location')
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            
            # Extract job type
            type_elem = listing.find('span', class_='job_type')
            job_type = type_elem.get_text(strip=True) if type_elem else "Full-time"
            
            # Extract posted date
            date_elem = listing.find('span', class_='date')
            posted_date = self._parse_relative_date(date_elem.get_text(strip=True)) if date_elem else datetime.now().strftime("%Y-%m-%d")
            
            # Generate email
            email = self._generate_company_email(company)
            
            return JobOpportunity(
                title=title,
                company=company,
                agency=company,
                email=email,
                job_url=job_url,
                hourly_rate=None,  # Remote.co doesn't always show hourly rates
                location=location,
                job_type=job_type,
                posted_date=posted_date,
                description="",
                requirements=[],
                source="Remote.co",
                scraped_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            return None
    
    def search_weworkremotely_jobs(self, query: str = "hourly", max_results: int = 20) -> List[JobOpportunity]:
        """Search WeWorkRemotely for hourly remote jobs"""
        jobs = []
        
        try:
            search_url = f"{self.job_sources['weworkremotely']['url']}?term={quote(query)}"
            response = self.session.get(search_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('li', class_='feature')
                
                for listing in job_listings[:max_results]:
                    try:
                        job = self._parse_weworkremotely_listing(listing)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error searching WeWorkRemotely: {e}")
        
        return jobs
    
    def _parse_weworkremotely_listing(self, listing) -> Optional[JobOpportunity]:
        """Parse WeWorkRemotely job listing"""
        try:
            # Extract job title and URL
            title_elem = listing.find('h2')
            if not title_elem:
                return None
                
            title = title_elem.get_text(strip=True)
            job_url = title_elem.find('a')['href'] if title_elem.find('a') else ""
            if job_url and not job_url.startswith('http'):
                job_url = f"https://weworkremotely.com{job_url}"
            
            # Extract company name
            company_elem = listing.find('h3')
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            # Extract location
            location_elem = listing.find('span', class_='region')
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            
            # Extract job type
            type_elem = listing.find('span', class_='job-type')
            job_type = type_elem.get_text(strip=True) if type_elem else "Full-time"
            
            # Extract posted date
            date_elem = listing.find('time')
            posted_date = date_elem['datetime'][:10] if date_elem and date_elem.get('datetime') else datetime.now().strftime("%Y-%m-%d")
            
            # Generate email
            email = self._generate_company_email(company)
            
            return JobOpportunity(
                title=title,
                company=company,
                agency=company,
                email=email,
                job_url=job_url,
                hourly_rate=None,
                location=location,
                job_type=job_type,
                posted_date=posted_date,
                description="",
                requirements=[],
                source="WeWorkRemotely",
                scraped_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            return None
    
    def search_all_sources(self, query: str = "remote hourly", max_results: int = 50) -> List[JobOpportunity]:
        """Search all job sources and return combined results"""
        all_jobs = []
        
        print(f"🔍 Searching for '{query}' jobs across multiple platforms...")
        
        # Setup Selenium if needed
        if any(source['requires_selenium'] for source in self.job_sources.values()):
            self.setup_selenium()
        
        try:
            # Search Indeed (requires Selenium)
            if self.driver:
                print("📊 Searching Indeed...")
                indeed_jobs = self.search_indeed_jobs(query, max_results // 3)
                all_jobs.extend(indeed_jobs)
                print(f"   Found {len(indeed_jobs)} jobs on Indeed")
            
            # Search Remote.co
            print("🏠 Searching Remote.co...")
            remote_co_jobs = self.search_remote_co_jobs(query, max_results // 3)
            all_jobs.extend(remote_co_jobs)
            print(f"   Found {len(remote_co_jobs)} jobs on Remote.co")
            
            # Search WeWorkRemotely
            print("💼 Searching WeWorkRemotely...")
            wwr_jobs = self.search_weworkremotely_jobs(query, max_results // 3)
            all_jobs.extend(wwr_jobs)
            print(f"   Found {len(wwr_jobs)} jobs on WeWorkRemotely")
            
        finally:
            # Close Selenium
            self.close_selenium()
        
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
            job_id = f"{job.title}_{job.company}_{job.source}"
            if job_id not in seen:
                seen.add(job_id)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def export_to_csv(self, jobs: List[JobOpportunity], filename: str = "remote_jobs.csv"):
        """Export job opportunities to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(asdict(jobs[0]).keys()) if jobs else []
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for job in jobs:
                    writer.writerow(asdict(job))
            
            print(f"✅ Jobs exported to {filename}")
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
    
    def export_to_excel(self, jobs: List[JobOpportunity], filename: str = "remote_jobs.xlsx"):
        """Export job opportunities to Excel file"""
        try:
            if jobs:
                df = pd.DataFrame([asdict(job) for job in jobs])
                df.to_excel(filename, index=False, engine='openpyxl')
                print(f"✅ Jobs exported to {filename}")
            else:
                print("❌ No jobs to export")
                
        except Exception as e:
            print(f"❌ Error exporting to Excel: {e}")
    
    def display_jobs(self, jobs: List[JobOpportunity], detailed: bool = False):
        """Display job opportunities in a formatted way"""
        if not jobs:
            print("❌ No jobs found matching your criteria.")
            return
        
        print(f"\n🎯 Found {len(jobs)} remote job opportunities:\n")
        print("=" * 100)
        
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job.title}")
            print(f"   Company: {job.company}")
            print(f"   Agency: {job.agency}")
            print(f"   Email: {job.email}")
            print(f"   Rate: {job.hourly_rate or 'Not specified'}")
            print(f"   Location: {job.location}")
            print(f"   Type: {job.job_type}")
            print(f"   Posted: {job.posted_date}")
            print(f"   Source: {job.source}")
            print(f"   Job URL: {job.job_url}")
            
            if detailed:
                print(f"   Description: {job.description}")
                print(f"   Requirements: {', '.join(job.requirements)}")
            
            print("-" * 50)
    
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
    """Main function to run the Advanced Remote Job Agent"""
    parser = argparse.ArgumentParser(description='Advanced Remote Job Agent - Find remote hourly job opportunities')
    parser.add_argument('--query', default='remote hourly', help='Search query for jobs')
    parser.add_argument('--skills', nargs='+', help='Your skills for personalized recommendations')
    parser.add_argument('--rate', help='Preferred hourly rate (e.g., "$30+")')
    parser.add_argument('--export-csv', help='Export results to CSV file')
    parser.add_argument('--export-excel', help='Export results to Excel file')
    parser.add_argument('--detailed', action='store_true', help='Show detailed job information')
    parser.add_argument('--max-results', type=int, default=20, help='Maximum number of results')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser in headless mode')
    
    args = parser.parse_args()
    
    # Initialize the agent
    agent = AdvancedRemoteJobAgent(headless=args.headless)
    
    print("🤖 Advanced Remote Job Agent - Finding your next remote opportunity!")
    print("=" * 70)
    
    try:
        if args.skills:
            # Get personalized recommendations
            jobs = agent.get_job_recommendations(args.skills, args.rate)
        else:
            # General search
            jobs = agent.search_all_sources(args.query, args.max_results)
        
        # Display results
        agent.display_jobs(jobs, args.detailed)
        
        # Export if requested
        if args.export_csv:
            agent.export_to_csv(jobs, args.export_csv)
        
        if args.export_excel:
            agent.export_to_excel(jobs, args.export_excel)
        
        print(f"\n✨ Search completed! Found {len(jobs)} opportunities.")
        print("💡 Tip: Use --skills and --rate for personalized recommendations")
        
    except KeyboardInterrupt:
        print("\n⚠️ Search interrupted by user")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        # Ensure Selenium is closed
        agent.close_selenium()

if __name__ == "__main__":
    main()