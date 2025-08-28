# 🤖 Remote Job Agent - Standalone Versions

Simple, independent tools to find remote job opportunities with agency information, emails, and job links for hourly positions.

## 📁 Available Files

### 1. **`simple_job_agent.py`** - Command Line Tool
- **What it is**: A simple Python script that runs in the terminal
- **What it does**: Searches for remote hourly jobs and displays results
- **Dependencies**: Only `requests` library
- **Use case**: Quick job searches from command line

### 2. **`standalone_web_app.py`** - Web Application
- **What it is**: A complete web app with embedded HTML/CSS/JavaScript
- **What it does**: Beautiful web interface for job searching
- **Dependencies**: Only `flask` library
- **Use case**: User-friendly web interface for job searches

## 🚀 Quick Start

### Option 1: Command Line Tool
```bash
# Install requests library
pip install requests

# Run the script
python simple_job_agent.py

# Follow the prompts to search for jobs
```

### Option 2: Web Application
```bash
# Install Flask
pip install flask

# Run the web app
python standalone_web_app.py

# Open browser to http://localhost:5000
```

## ✨ Features

Both versions provide:
- **Job search** across multiple platforms
- **Agency information** and company details
- **Email addresses** for companies
- **Direct job links** to apply
- **Hourly rate information**
- **Export to CSV** functionality
- **Sample job data** for demonstration

## 📊 Sample Output

Each job result includes:
- Job title and company name
- Agency information
- Company email (e.g., `jobs@company.com`)
- Job application URL
- Hourly rate
- Job type and location
- Posted date
- Source platform

## 🔧 Customization

### Adding More Jobs
Edit the `job_templates` list in either file to add more sample jobs:

```python
{
    'title': 'Your Job Title',
    'company': 'Company Name',
    'agency': 'Agency Name',
    'email': 'contact@company.com',
    'job_url': 'https://job-site.com/job/123',
    'hourly_rate': '$30-50/hr',
    'location': 'Remote',
    'job_type': 'Contract',
    'posted_date': '2024-01-15',
    'description': 'Job description here',
    'requirements': ['Skill 1', 'Skill 2', 'Skill 3'],
    'source': 'Job Site Name'
}
```

### Modifying Email Patterns
Change the email generation logic in `simple_job_agent.py`:

```python
def generate_company_email(self, company_name: str) -> str:
    clean_name = re.sub(r'[^\w\s]', '', company_name).lower().strip()
    return f"jobs@{clean_name.replace(' ', '')}.com"
```

## 📝 Usage Examples

### Command Line Tool
```bash
# Basic search
python simple_job_agent.py
# Enter: remote hourly developer
# Enter: 20 (max results)

# Export results
# Enter: y (for CSV export)
# Enter: my_jobs.csv
```

### Web Application
1. Run `python standalone_web_app.py`
2. Open browser to `http://localhost:5000`
3. Enter search terms (e.g., "remote hourly developer")
4. Add skills (optional): "Python, JavaScript"
5. Set rate (optional): "$30+"
6. Click "Search Jobs"
7. Export results to CSV

## 🎯 Why These Versions?

- **Independent**: Each file works completely on its own
- **Lightweight**: Minimal dependencies
- **Portable**: Easy to copy and use anywhere
- **Customizable**: Easy to modify for your needs
- **Demo-ready**: Includes sample data to test immediately

## 🔍 What You Get

- **Company names** and agency information
- **Contact emails** automatically generated
- **Job application links** to apply directly
- **Hourly rates** for remote positions
- **Exportable results** in CSV format
- **Beautiful interface** (web version)

## 💡 Tips

1. **Start with web version** for easiest use
2. **Use command line version** for automation
3. **Customize job templates** for your industry
4. **Export results** to track your job search
5. **Modify email patterns** for better contact info

## 🚨 Note

These versions use **sample data** for demonstration. For real job scraping, you'd need to implement actual web scraping logic and respect website terms of service.

---

**Ready to find your next remote opportunity? 🎉**

Choose the version that fits your needs and start searching!