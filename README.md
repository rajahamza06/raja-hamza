# 🤖 Remote Job Agent

An AI-powered tool to find remote job opportunities with agency information, emails, and job links, specifically designed for hourly positions.

## ✨ Features

- **Multi-Platform Search**: Searches across multiple job boards including Indeed, Upwork, Remote.co, WeWorkRemotely, and more
- **Real-Time Scraping**: Actually scrapes real job data (not just sample data)
- **Agency Information**: Provides company/agency details and contact information
- **Email Generation**: Automatically generates company email addresses based on company names
- **Hourly Rate Focus**: Specifically designed to find hourly/remote positions
- **Export Options**: Export results to CSV or Excel format
- **Web Interface**: Beautiful, responsive web interface for easy use
- **Command Line**: Command-line interface for automation and scripting

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for Selenium-based scraping)
- Linux/Windows/macOS

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the web interface**:
   ```bash
   python web_interface.py
   ```

4. **Open your browser** and go to `http://localhost:5000`

## 📖 Usage

### Web Interface

1. **Search for Jobs**:
   - Enter job keywords (e.g., "remote hourly developer")
   - Add your skills for personalized recommendations
   - Set preferred hourly rate
   - Choose maximum number of results

2. **View Results**:
   - See job title, company, agency, and email
   - View hourly rate, location, and job type
   - Click job links to view full descriptions
   - Export results to CSV or Excel

### Command Line

#### Basic Search
```bash
python advanced_remote_job_agent.py --query "remote hourly developer" --max-results 20
```

#### Personalized Recommendations
```bash
python advanced_remote_job_agent.py --skills Python JavaScript React --rate "$30+" --max-results 30
```

#### Export Results
```bash
python advanced_remote_job_agent.py --query "remote hourly" --export-csv jobs.csv --export-excel jobs.xlsx
```

#### Detailed Output
```bash
python advanced_remote_job_agent.py --query "remote hourly" --detailed
```

### Command Line Options

- `--query`: Search query for jobs (default: "remote hourly")
- `--skills`: Your skills for personalized recommendations
- `--rate`: Preferred hourly rate (e.g., "$30+")
- `--export-csv`: Export results to CSV file
- `--export-excel`: Export results to Excel file
- `--detailed`: Show detailed job information
- `--max-results`: Maximum number of results (default: 20)
- `--headless`: Run browser in headless mode (default: True)

## 🔧 Configuration

### Job Sources

The agent searches across these platforms:

- **Indeed**: Large job board with remote filters
- **Upwork**: Freelance platform with hourly rates
- **Remote.co**: Dedicated remote job site
- **WeWorkRemotely**: Remote-first job board
- **Remote OK**: Developer-focused remote jobs
- **FlexJobs**: Curated remote opportunities

### Rate Filtering

The agent can filter jobs by hourly rate:
- Use `--rate "$30+"` to find jobs paying $30/hour or more
- Supports various rate formats: "$25-40/hr", "$50+", etc.

## 📊 Output Format

Each job result includes:

- **Title**: Job position title
- **Company**: Hiring company name
- **Agency**: Agency/company (same as company for direct hires)
- **Email**: Generated company email address
- **Job URL**: Direct link to job posting
- **Hourly Rate**: Hourly pay rate if specified
- **Location**: Job location (usually "Remote")
- **Job Type**: Full-time, part-time, contract, etc.
- **Posted Date**: When the job was posted
- **Source**: Which platform the job was found on
- **Description**: Job description (if detailed mode)
- **Requirements**: Required skills and experience

## 🛠️ Technical Details

### Architecture

- **Python 3.8+**: Modern Python with type hints
- **Selenium**: For dynamic content scraping (Indeed, Upwork)
- **BeautifulSoup**: For HTML parsing
- **Requests**: For HTTP requests
- **Pandas**: For data manipulation and Excel export
- **Flask**: Web interface backend

### Scraping Strategy

1. **Static Sites**: Use requests + BeautifulSoup for sites like Remote.co
2. **Dynamic Sites**: Use Selenium for JavaScript-heavy sites like Indeed
3. **Rate Limiting**: Built-in delays to respect website policies
4. **User Agents**: Rotating user agents to avoid detection
5. **Error Handling**: Graceful fallbacks when scraping fails

### Email Generation

The agent generates company emails using common patterns:
- `jobs@companyname.com`
- `careers@companyname.com`
- `hiring@companyname.com`
- `hr@companyname.com`
- `info@companyname.com`

## ⚠️ Important Notes

### Legal and Ethical Considerations

- **Respect robots.txt**: The agent respects website robots.txt files
- **Rate limiting**: Built-in delays to avoid overwhelming servers
- **Terms of service**: Check each website's terms before scraping
- **Personal use only**: Intended for personal job searching

### Limitations

- **Anti-bot measures**: Some sites may block automated access
- **Site changes**: Website structure changes may break scraping
- **Rate limits**: Some sites may limit request frequency
- **Captcha**: Some sites may require human verification

## 🚀 Advanced Usage

### Custom Job Sources

Add new job sources by modifying the `job_sources` dictionary in `AdvancedRemoteJobAgent`:

```python
'new_site': {
    'url': 'https://newsite.com/jobs',
    'search_params': {'q': '', 'location': 'Remote'},
    'requires_selenium': False
}
```

### Custom Parsers

Implement custom parsing logic for new sites:

```python
def search_new_site_jobs(self, query: str, max_results: int = 20):
    # Your custom scraping logic here
    pass
```

### API Integration

The agent can be easily integrated with other applications:

```python
from advanced_remote_job_agent import AdvancedRemoteJobAgent

agent = AdvancedRemoteJobAgent()
jobs = agent.search_all_sources("remote hourly", max_results=50)

for job in jobs:
    print(f"Found: {job.title} at {job.company}")
```

## 🔍 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   ```bash
   # Reinstall Chrome driver
   pip uninstall webdriver-manager
   pip install webdriver-manager
   ```

2. **Selenium Errors**:
   - Ensure Chrome browser is installed
   - Try running without headless mode: `--headless false`

3. **No Results**:
   - Check your internet connection
   - Try different search terms
   - Some sites may be temporarily unavailable

4. **Export Errors**:
   - Ensure you have write permissions
   - Check if the file is open in another application

### Debug Mode

Run with verbose output:
```bash
python advanced_remote_job_agent.py --query "remote hourly" --detailed
```

## 📈 Performance Tips

- **Limit results**: Use `--max-results` to control search time
- **Headless mode**: Keep `--headless true` for faster execution
- **Specific queries**: More specific searches are faster than broad ones
- **Batch processing**: Run searches during off-peak hours

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Additional job sources
- Better parsing algorithms
- Rate filtering improvements
- UI/UX enhancements
- Performance optimizations

## 📄 License

This project is for educational and personal use. Please respect website terms of service and robots.txt files.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section
2. Ensure all dependencies are installed
3. Try running with different parameters
4. Check if target websites are accessible

## 🎯 Use Cases

- **Job seekers**: Find remote hourly opportunities
- **Recruiters**: Research job market and rates
- **Researchers**: Analyze remote work trends
- **Developers**: Learn about job requirements
- **Freelancers**: Find hourly contract work

---

**Happy job hunting! 🎉**

*Remember to respect website terms of service and use this tool responsibly.*