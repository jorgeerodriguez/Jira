# Jira Daily Reporting System

An automated system for generating and distributing daily Jira reports via email and Slack.

## Features

- 📊 **Comprehensive Jira Reports**: Status summaries, blocked issues, in-progress tracking, and backlog analysis
- 📧 **Email Integration**: Send formatted HTML and plain text reports via Gmail or any SMTP server
- 💬 **Slack Integration**: Post formatted reports to Slack channels using webhooks
- 🔄 **Automated Daily Reports**: Consolidates multiple report types into a single daily digest
- ⚙️ **Modular Architecture**: Clean, maintainable code with separation of concerns
- 🎨 **Multiple Formats**: Generate reports in plain text, HTML, and Slack Block Kit formats

## Project Structure

```
.
├── src/
│   ├── config_manager.py      # Configuration management
│   ├── jira_client.py          # Jira API wrapper
│   ├── report_generator.py    # Report generation logic
│   ├── email_sender.py         # Email sending functionality
│   └── slack_notifier.py       # Slack notification handling
├── templates/                  # (Future) Report templates
├── daily_report.py            # Main script for daily reports
├── requirements.txt           # Python dependencies
├── config.example.json        # Example configuration file
└── README.md                  # This file
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Jira
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure credentials**
   ```bash
   cp config.example.json config.json
   # Edit config.json with your credentials (see Configuration section)
   ```

## Configuration

### config.json Structure

Create a `config.json` file based on `config.example.json`:

```json
{
  "jira_server": "https://your-company.atlassian.net",
  "jira_email": "your.email@company.com",
  "jira_api_token": "your_jira_api_token",
  
  "email_address": "your.email@gmail.com",
  "email_password": "your_gmail_app_password",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  
  "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "slack_channel": "#jira-reports",
  
  "report_projects": ["DEVOPS", "EIT"],
  "email_recipients": ["recipient@company.com"]
}
```

### Getting Credentials

#### Jira API Token
1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a name and copy the token
4. Add to `config.json` as `jira_api_token`

#### Gmail App Password
1. Enable 2-factor authentication on your Google account
2. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app-specific password
4. Add to `config.json` as `email_password`

#### Slack Webhook
1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Create a new app or use existing
3. Enable "Incoming Webhooks"
4. Create a webhook for your channel
5. Copy the webhook URL to `config.json`

## Usage

### Running a Daily Report

```bash
python daily_report.py
```

This will:
1. Connect to Jira
2. Generate reports for configured projects
3. Send reports via email (if configured)
4. Post reports to Slack (if configured)

### Specifying Projects

```bash
# Report on specific projects
python daily_report.py DEVOPS,EIT,AWPOD

# Or configure in config.json
"report_projects": ["DEVOPS", "EIT", "AWPOD"]
```

### Scheduling Daily Reports

#### Using cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add line to run daily at 9 AM
0 9 * * * cd /path/to/Jira && /usr/bin/python3 daily_report.py >> /var/log/jira_reports.log 2>&1
```

#### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to Daily at your preferred time
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `daily_report.py`
7. Start in: Path to your Jira directory

#### Using Python schedule library

Create a `scheduler.py` file:

```python
import schedule
import time
from daily_report import DailyReporter
from src.config_manager import ConfigManager

def run_daily_report():
    config_manager = ConfigManager()
    reporter = DailyReporter(config_manager)
    reporter.run()

# Schedule for 9 AM every day
schedule.every().day.at("09:00").do(run_daily_report)

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run with:
```bash
python scheduler.py
```

## Report Types

The system generates the following reports:

### 1. Status Summary
- Total issue count per project
- Breakdown by status with percentages

### 2. Blocked Issues
- List of all blocked issues
- Assignee and priority information
- Creation date and age

### 3. In-Progress Issues
- Current work items
- Items without due dates (⚠️)
- Items behind schedule (⚠️)

### 4. Old Backlog Items
- Issues older than 50 days (configurable)
- Sorted by age (oldest first)
- Helps identify stale items

### 5. Assignee Distribution
- Workload distribution across team members
- Helps identify capacity issues

## Customization

### Adding Custom Reports

Edit `src/report_generator.py` to add new report methods:

```python
def generate_custom_report(self, project_key: str) -> Dict:
    """Your custom report logic"""
    # Implementation here
    return report_data
```

### Customizing Email Templates

HTML formatting is in `report_generator.py`'s `format_digest_as_html()` method. Modify the CSS and structure as needed.

### Customizing Slack Messages

Slack formatting is in `slack_notifier.py`'s `send_report()` method. Use [Slack Block Kit](https://api.slack.com/block-kit) for rich formatting.

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests (when available)
pytest tests/
```

### Code Style

The codebase follows PEP 8 style guidelines. Use:

```bash
# Install formatting tools
pip install black flake8

# Format code
black src/ *.py

# Check style
flake8 src/ *.py
```

## Troubleshooting

### Email Issues

**Problem**: Gmail authentication fails
- **Solution**: Make sure you're using an App Password, not your regular password
- Enable 2-factor authentication first
- Generate a new App Password at https://myaccount.google.com/apppasswords

**Problem**: SMTP connection timeout
- **Solution**: Check firewall settings
- Verify SMTP server and port are correct
- For Gmail: `smtp.gmail.com:587`

### Slack Issues

**Problem**: Slack webhook returns 404
- **Solution**: Verify webhook URL is correct
- Make sure the webhook is still active in Slack app settings
- Check if the app has been removed from the workspace

**Problem**: Message not appearing in Slack
- **Solution**: Check channel permissions
- Verify the webhook is configured for the correct channel
- Try sending a test message using curl

### Jira Issues

**Problem**: Authentication fails
- **Solution**: Verify API token is valid
- Check Jira server URL is correct (include https://)
- Ensure email address matches Jira account

**Problem**: No issues returned
- **Solution**: Check project keys are correct
- Verify you have permissions to view the projects
- Try a simpler JQL query first

## Security Best Practices

1. **Never commit config.json**: It's in .gitignore by default
2. **Use environment variables**: For production deployments
3. **Rotate credentials**: Regularly update API tokens and passwords
4. **Limit permissions**: Use read-only Jira accounts if possible
5. **Secure webhook URLs**: Treat Slack webhooks as secrets

## Migration from Notebook

This refactored system replaces the monolithic `Jira.ipynb` notebook with:
- ✅ Modular, reusable code
- ✅ Proper error handling
- ✅ Logging and monitoring
- ✅ Automated delivery (email + Slack)
- ✅ Easy scheduling
- ✅ Better maintainability

## Future Enhancements

Potential improvements:
- [ ] Dashboard web interface
- [ ] Historical trend analysis
- [ ] Chart/graph generation
- [ ] PDF report exports
- [ ] MS Teams integration
- [ ] Jira webhook listeners for real-time updates
- [ ] Custom alert thresholds
- [ ] Multi-language support

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Specify your license here]

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review existing issues in the repository
3. Create a new issue with detailed information

---

**Note**: This system requires valid Jira, email, and/or Slack credentials to function. Ensure all sensitive information is kept secure and never committed to version control.
