# Email Setup for GitLab Code Changes Report

This document explains how to set up email credentials to automatically send GitLab code changes reports.

## Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# GitLab Configuration (already configured)
GITLAB_URL=https://your-gitlab-instance.com
GITLAB_TOKEN=your-gitlab-api-token

# Email Configuration (Required for sending reports)
SMTP_USERNAME=your-email@company.com
SMTP_PASSWORD=your-app-password-or-email-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_FROM_EMAIL=your-email@company.com
SMTP_FROM_NAME=GitLab Analytics
```

## Email Provider Examples

### Gmail
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password
```

**Important for Gmail**: You need to use an "App Password" instead of your regular password:
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password for "Mail"
4. Use that App Password in `SMTP_PASSWORD`

### Outlook/Office 365
```bash
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### Corporate Exchange Server
```bash
SMTP_SERVER=mail.yourcompany.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yourcompany.com
SMTP_PASSWORD=your-password
```

## Usage

### Simple Usage (Default Recipients)
```bash
# Generate report and send to default recipients
python scripts/generate_and_send_report.py
```

### Custom Recipients
```bash
# Send to custom email addresses
python scripts/generate_and_send_report.py --recipients user1@company.com,user2@company.com
```

### Generate Report Only (No Email)
```bash
# Generate HTML report without sending email
python scripts/generate_and_send_report.py --no-email
```

### Other Options
```bash
# Generate report for specific groups
python scripts/generate_and_send_report.py --groups 1721,1267

# Use default branch only (faster)
python scripts/generate_and_send_report.py --default-branch-only

# Custom subject line
python scripts/generate_and_send_report.py --subject "Weekly GitLab Report"

# Send inline only (no attachment)
python scripts/generate_and_send_report.py --no-attachment
```

## Default Recipients

The script is pre-configured to send reports to:
- tassawee.t@tspacedigital.com
- totrakool.k@thaibev.com

You can override this with the `--recipients` parameter.

## Troubleshooting

### "Missing SMTP_USERNAME or SMTP_PASSWORD"
- Make sure your `.env` file exists in the root directory
- Check that `SMTP_USERNAME` and `SMTP_PASSWORD` are set correctly
- For Gmail, ensure you're using an App Password

### "Authentication failed"
- Verify your email credentials are correct
- For Gmail, make sure 2FA is enabled and you're using an App Password
- For corporate email, check with your IT department for SMTP settings

### "Connection refused"
- Check the `SMTP_SERVER` and `SMTP_PORT` settings
- Ensure your network allows outbound SMTP connections
- Some corporate networks block external SMTP

## Security Notes

- Never commit your `.env` file to version control
- Use App Passwords instead of regular passwords when possible
- Consider using environment variables instead of `.env` files in production 