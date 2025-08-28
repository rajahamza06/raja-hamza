#!/usr/bin/env python3
"""
Web Interface for Remote Job Agent
Simple Flask web app to search for remote job opportunities
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
from datetime import datetime
from advanced_remote_job_agent import AdvancedRemoteJobAgent

app = Flask(__name__)

# Global agent instance
agent = None

def get_agent():
    """Get or create the job agent instance"""
    global agent
    if agent is None:
        agent = AdvancedRemoteJobAgent(headless=True)
    return agent

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_jobs():
    """Search for jobs"""
    try:
        data = request.get_json()
        query = data.get('query', 'remote hourly')
        skills = data.get('skills', [])
        rate = data.get('rate', '')
        max_results = int(data.get('max_results', 20))
        
        agent = get_agent()
        
        if skills:
            jobs = agent.get_job_recommendations(skills, rate)
        else:
            jobs = agent.search_all_sources(query, max_results)
        
        # Convert jobs to dict for JSON serialization
        jobs_data = []
        for job in jobs:
            job_dict = {
                'title': job.title,
                'company': job.company,
                'agency': job.agency,
                'email': job.email,
                'job_url': job.job_url,
                'hourly_rate': job.hourly_rate,
                'location': job.location,
                'job_type': job.job_type,
                'posted_date': job.posted_date,
                'source': job.source,
                'description': job.description,
                'requirements': job.requirements
            }
            jobs_data.append(job_dict)
        
        return jsonify({
            'success': True,
            'jobs': jobs_data,
            'count': len(jobs_data)
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
            import csv
            if jobs_data:
                fieldnames = jobs_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for job in jobs_data:
                    writer.writerow(job)
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

@app.route('/export/excel', methods=['POST'])
def export_excel():
    """Export jobs to Excel"""
    try:
        data = request.get_json()
        jobs_data = data.get('jobs', [])
        
        if not jobs_data:
            return jsonify({'success': False, 'error': 'No jobs to export'}), 400
        
        # Create temporary Excel file
        import pandas as pd
        df = pd.DataFrame(jobs_data)
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            df.to_excel(f.name, index=False, engine='openpyxl')
            temp_file = f.name
        
        # Send file
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=f'remote_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)