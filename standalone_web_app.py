#!/usr/bin/env python3
"""
Standalone Web App for Remote Job Agent
Complete web interface that can run independently
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import tempfile
from datetime import datetime
import csv
import json
import re

app = Flask(__name__)

# HTML template embedded in the Python file
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Remote Job Agent - Find Your Next Opportunity</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .search-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .search-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #555;
        }

        .form-group input, .form-group textarea {
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus, .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .search-btn {
            grid-column: span 2;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }

        .search-btn:hover {
            transform: translateY(-2px);
        }

        .search-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .results-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }

        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }

        .export-buttons {
            display: flex;
            gap: 10px;
        }

        .export-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.3s ease;
        }

        .export-btn:hover {
            background: #218838;
        }

        .export-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .job-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .job-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .job-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
        }

        .job-company {
            font-size: 1.1rem;
            font-weight: 500;
            color: #555;
            margin-bottom: 8px;
        }

        .job-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }

        .job-detail {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .job-detail i {
            color: #667eea;
            width: 20px;
        }

        .job-email {
            background: #e3f2fd;
            padding: 8px 12px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 14px;
            color: #1976d2;
        }

        .job-url {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .job-url:hover {
            text-decoration: underline;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }

        .success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
        }

        @media (max-width: 768px) {
            .search-form {
                grid-template-columns: 1fr;
            }
            
            .search-btn {
                grid-column: span 1;
            }
            
            .results-header {
                flex-direction: column;
                gap: 15px;
                align-items: stretch;
            }
            
            .export-buttons {
                justify-content: center;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Remote Job Agent</h1>
            <p>Find your next remote opportunity with AI-powered job search</p>
        </div>

        <div class="search-section">
            <h2 style="margin-bottom: 20px; color: #555;">🔍 Search for Remote Jobs</h2>
            <form class="search-form" id="searchForm">
                <div class="form-group">
                    <label for="query">Job Keywords</label>
                    <input type="text" id="query" name="query" placeholder="e.g., remote hourly developer" value="remote hourly">
                </div>
                
                <div class="form-group">
                    <label for="skills">Your Skills (optional)</label>
                    <textarea id="skills" name="skills" placeholder="e.g., Python, JavaScript, React" rows="3"></textarea>
                </div>
                
                <div class="form-group">
                    <label for="rate">Preferred Hourly Rate (optional)</label>
                    <input type="text" id="rate" name="rate" placeholder="e.g., $30+">
                </div>
                
                <div class="form-group">
                    <label for="maxResults">Maximum Results</label>
                    <input type="number" id="maxResults" name="maxResults" value="20" min="5" max="100">
                </div>
                
                <button type="submit" class="search-btn" id="searchBtn">
                    <i class="fas fa-search"></i> Search Jobs
                </button>
            </form>
        </div>

        <div class="results-section" id="resultsSection" style="display: none;">
            <div class="results-header">
                <h2 id="resultsTitle">🎯 Job Results</h2>
                <div class="export-buttons">
                    <button class="export-btn" id="exportCsvBtn" disabled>
                        <i class="fas fa-download"></i> Export CSV
                    </button>
                </div>
            </div>
            
            <div id="resultsContent"></div>
        </div>
    </div>

    <script>
        let currentJobs = [];

        document.getElementById('searchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const searchBtn = document.getElementById('searchBtn');
            const resultsSection = document.getElementById('resultsSection');
            const resultsContent = document.getElementById('resultsContent');
            
            // Show loading state
            searchBtn.disabled = true;
            searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
            
            // Get form data
            const formData = new FormData(this);
            const searchData = {
                query: formData.get('query'),
                skills: formData.get('skills').split(',').map(s => s.trim()).filter(s => s),
                rate: formData.get('rate'),
                max_results: parseInt(formData.get('maxResults'))
            };
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(searchData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentJobs = result.jobs;
                    displayResults(result.jobs);
                    resultsSection.style.display = 'block';
                    
                    // Enable export buttons
                    document.getElementById('exportCsvBtn').disabled = false;
                } else {
                    showError(result.error || 'Search failed');
                }
                
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                // Reset button state
                searchBtn.disabled = false;
                searchBtn.innerHTML = '<i class="fas fa-search"></i> Search Jobs';
            }
        });

        function displayResults(jobs) {
            const resultsTitle = document.getElementById('resultsTitle');
            const resultsContent = document.getElementById('resultsContent');
            
            resultsTitle.textContent = `🎯 Found ${jobs.length} Job Opportunities`;
            
            if (jobs.length === 0) {
                resultsContent.innerHTML = '<div class="loading">No jobs found matching your criteria.</div>';
                return;
            }
            
            let html = '';
            jobs.forEach((job, index) => {
                html += `
                    <div class="job-card">
                        <div class="job-title">${job.title}</div>
                        <div class="job-company">${job.company}</div>
                        
                        <div class="job-details">
                            <div class="job-detail">
                                <i class="fas fa-building"></i>
                                <span><strong>Agency:</strong> ${job.agency}</span>
                            </div>
                            <div class="job-detail">
                                <i class="fas fa-envelope"></i>
                                <span><strong>Email:</strong></span>
                            </div>
                            <div class="job-detail">
                                <i class="fas fa-dollar-sign"></i>
                                <span><strong>Rate:</strong> ${job.hourly_rate || 'Not specified'}</span>
                            </div>
                            <div class="job-detail">
                                <i class="fas fa-map-marker-alt"></i>
                                <span><strong>Location:</strong> ${job.location}</span>
                            </div>
                            <div class="job-detail">
                                <i class="fas fa-clock"></i>
                                <span><strong>Type:</strong> ${job.job_type}</span>
                            </div>
                            <div class="job-detail">
                                <i class="fas fa-calendar"></i>
                                <span><strong>Posted:</strong> ${job.posted_date}</span>
                            </div>
                            <div class="job-detail">
                                <i class="fas fa-globe"></i>
                                <span><strong>Source:</strong> ${job.source}</span>
                            </div>
                        </div>
                        
                        <div class="job-email">${job.email}</div>
                        
                        <div style="margin-top: 15px;">
                            <a href="${job.job_url}" target="_blank" class="job-url">
                                <i class="fas fa-external-link-alt"></i> View Job Details
                            </a>
                        </div>
                    </div>
                `;
            });
            
            resultsContent.innerHTML = html;
        }

        function showError(message) {
            const resultsSection = document.getElementById('resultsSection');
            const resultsContent = document.getElementById('resultsContent');
            
            resultsSection.style.display = 'block';
            resultsContent.innerHTML = `<div class="error">❌ ${message}</div>`;
        }

        // Export functionality
        document.getElementById('exportCsvBtn').addEventListener('click', async function() {
            await exportJobs('csv');
        });

        async function exportJobs(format) {
            if (currentJobs.length === 0) {
                alert('No jobs to export');
                return;
            }
            
            try {
                const response = await fetch(`/export/${format}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ jobs: currentJobs })
                });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `remote_jobs_${new Date().toISOString().slice(0,10)}.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    const error = await response.json();
                    alert('Export failed: ' + error.error);
                }
                
            } catch (error) {
                alert('Export failed: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''

class StandaloneJobAgent:
    """Standalone job agent that generates sample data"""
    
    def __init__(self):
        self.job_templates = [
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
            },
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
            },
            {
                'title': 'Remote Data Analyst',
                'company': 'Data Insights Co',
                'agency': 'Data Insights Co',
                'email': 'careers@datainsights.com',
                'job_url': 'https://remote.co/job/11111',
                'hourly_rate': '$35-55/hr',
                'location': 'Remote',
                'job_type': 'Full-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Remote data analysis position with flexible scheduling',
                'requirements': ['Python', 'SQL', 'Excel', 'Statistical analysis'],
                'source': 'Remote.co'
            },
            {
                'title': 'Virtual Assistant',
                'company': 'Admin Solutions',
                'agency': 'Admin Solutions',
                'email': 'hr@adminsolutions.com',
                'job_url': 'https://weworkremotely.com/jobs/22222',
                'hourly_rate': '$20-35/hr',
                'location': 'Remote',
                'job_type': 'Part-time',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Virtual assistant role with flexible hours',
                'requirements': ['Organization skills', 'Communication', 'Microsoft Office', 'Previous experience'],
                'source': 'WeWorkRemotely'
            }
        ]
    
    def search_jobs(self, query: str, skills: list = None, rate: str = None, max_results: int = 20):
        """Search for jobs based on query and filters"""
        # Filter jobs based on query
        filtered_jobs = []
        
        for job in self.job_templates:
            # Check if query matches job title or description
            if query.lower() in job['title'].lower() or query.lower() in job['description'].lower():
                filtered_jobs.append(job.copy())
            
            # If we have enough results, stop
            if len(filtered_jobs) >= max_results:
                break
        
        # If no results, return some default jobs
        if not filtered_jobs:
            filtered_jobs = self.job_templates[:max_results]
        
        # Apply rate filter if specified
        if rate:
            rate_filtered = []
            for job in filtered_jobs:
                if job['hourly_rate'] and self._rate_matches_preference(job['hourly_rate'], rate):
                    rate_filtered.append(job)
            filtered_jobs = rate_filtered
        
        # Apply skills filter if specified
        if skills:
            skills_filtered = []
            for job in filtered_jobs:
                if any(skill.lower() in ' '.join(job['requirements']).lower() for skill in skills):
                    skills_filtered.append(job)
            filtered_jobs = skills_filtered
        
        return filtered_jobs[:max_results]
    
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

# Initialize the agent
agent = StandaloneJobAgent()

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search_jobs():
    """Search for jobs"""
    try:
        data = request.get_json()
        query = data.get('query', 'remote hourly')
        skills = data.get('skills', [])
        rate = data.get('rate', '')
        max_results = int(data.get('max_results', 20))
        
        # Search for jobs
        jobs = agent.search_jobs(query, skills, rate, max_results)
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/export/csv', methods=['POST'])
def export_csv():
    """Export jobs to CSV"""
    try:
        data = request.get_json()
        jobs_data = data.get('jobs', [])
        
        if not jobs_data:
            return jsonify({'success': False, 'error': 'No jobs to export'}), 400
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            if jobs_data:
                fieldnames = jobs_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for job in jobs_data:
                    # Convert requirements list to string
                    job_copy = job.copy()
                    job_copy['requirements'] = '; '.join(job['requirements'])
                    writer.writerow(job_copy)
                temp_file = f.name
        
        # Send file
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=f'remote_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Standalone Remote Job Agent Web App...")
    print("🌐 Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)