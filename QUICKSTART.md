# Quick Start Guide

Get started with the Jira Daily Reporting System in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Credentials

1. Copy the example config file:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` and add your credentials:
   ```json
   {
     "jira_server": "https://your-company.atlassian.net",
     "jira_email": "your.email@company.com",
     "jira_api_token": "your_jira_api_token",
     
     "report_projects": ["DEVOPS", "EIT"]
   }
   ```

### Getting Your Jira API Token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Daily Reporter")
4. Copy the token and paste it into `config.json`

## Step 3: Test the System

Run the test script to verify everything works:

```bash
python test_system.py
```

This will:
- ✓ Verify configuration is valid
- ✓ Test Jira connection
- ✓ Generate sample reports
- ✓ Save sample reports to `/tmp/sample_report.txt` and `/tmp/sample_report.html`

## Step 4: Configure Email (Optional)

### For Gmail:

1. Enable 2-factor authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an app password
4. Add to `config.json`:
   ```json
   {
     "email_address": "your.email@gmail.com",
     "email_password": "your_16_character_app_password",
     "email_recipients": ["recipient@company.com"]
   }
   ```

### For Other SMTP:

```json
{
  "email_address": "your.email@company.com",
  "email_password": "your_password",
  "smtp_server": "smtp.company.com",
  "smtp_port": 587,
  "email_recipients": ["recipient@company.com"]
}
```

## Step 5: Configure Slack (Optional)

1. Go to: https://api.slack.com/apps
2. Create a new app (or use existing)
3. Enable "Incoming Webhooks"
4. Add webhook for your channel
5. Copy webhook URL to `config.json`:
   ```json
   {
     "slack_webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
     "slack_channel": "#jira-reports"
   }
   ```

## Step 6: Run Your First Report

```bash
python daily_report.py
```

This will generate and send reports via all configured channels (email, Slack).

## Step 7: Set Up Automation

### Option A: Using the Built-in Scheduler

```bash
# Add schedule time to config.json
{
  "report_schedule_time": "09:00"
}

# Run the scheduler (keeps running)
python scheduler.py
```

### Option B: Using Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/Jira && python daily_report.py >> /var/log/jira_reports.log 2>&1
```

### Option C: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task → Daily
3. Set time (e.g., 9:00 AM)
4. Start a Program: `python.exe`
5. Add arguments: `daily_report.py`
6. Start in: `C:\path\to\Jira`

## Customization

### Select Specific Projects

Edit `config.json`:
```json
{
  "report_projects": ["DEVOPS", "EIT", "AWPOD"]
}
```

Or pass via command line:
```bash
python daily_report.py DEVOPS,EIT,AWPOD
```

### Add More Email Recipients

```json
{
  "email_recipients": [
    "team@company.com",
    "manager@company.com",
    "stakeholder@company.com"
  ]
}
```

### Change Slack Channel

```json
{
  "slack_channel": "#engineering-reports"
}
```

## Troubleshooting

### "Configuration file not found"
- Make sure `config.json` exists in the project directory
- Check you're running from the correct directory

### "Failed to connect to Jira"
- Verify Jira server URL is correct (include `https://`)
- Check API token is valid
- Ensure email matches your Jira account

### "SMTP Authentication Error"
- For Gmail: Use an App Password, not your regular password
- Verify 2-factor authentication is enabled
- Try generating a new App Password

### "Slack webhook returns 404"
- Verify webhook URL is complete and correct
- Check the webhook hasn't been deleted in Slack
- Ensure app is still installed in workspace

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🔧 Customize reports in `src/report_generator.py`
- 📊 Add custom metrics and visualizations
- 🤖 Set up alerts for specific conditions

## Support

Having issues? Check:
1. The test output: `python test_system.py`
2. Log files: `jira_reports.log`
3. Sample reports: `/tmp/sample_report.txt`

---

**Ready to go?** Run `python daily_report.py` and check your email/Slack! 🚀
