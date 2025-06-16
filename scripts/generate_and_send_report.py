#!/usr/bin/env python3
"""Generate GitLab code changes report and send via email."""

import os
import sys
import smtplib
import ssl
import argparse
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Import the report generation functions
sys.path.append(str(Path(__file__).parent))
from generate_code_changes_report import analyze_groups_code_changes, generate_html_report, get_env_or_exit, GROUP_NAMES

def send_report_email(html_file_path: str, recipients: list, subject: str, attach_file: bool = True) -> bool:
    """Send HTML report via email to multiple recipients."""
    try:
        # Get email configuration from environment
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
        from_name = os.getenv('SMTP_FROM_NAME', 'GitLab Analytics')
        
        if not smtp_username or not smtp_password:
            print("❌ Missing SMTP_USERNAME or SMTP_PASSWORD environment variables")
            print("   Please set these in your .env file:")
            print("   SMTP_USERNAME=your-email@company.com")
            print("   SMTP_PASSWORD=your-app-password")
            print("   SMTP_SERVER=smtp.gmail.com (optional)")
            print("   SMTP_PORT=587 (optional)")
            return False
        
        # Read HTML content for inline display
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Create email body
        email_body = f"""
Hi Team,

Please find the latest GitLab code changes report showing activity across all our projects and branches.

📊 Report Summary:
• Branch-level analysis for all active branches
• Code changes for 7d, 15d, 30d, 60d, and 90d periods  
• Net code changes summary for each time period
• Activity breakdown by Group, Project, and Branch
• Case-insensitive sorting by Group → Project → Branch

The report is {'attached as an HTML file and also ' if attach_file else ''}displayed below for your convenience.

Best regards,
Development Team

Generated on: {datetime.now().strftime('%Y-%m-%d at %I:%M %p')}
        """.strip()
        
        # Create message
        message = MIMEMultipart('mixed')
        message['Subject'] = subject
        message['From'] = f"{from_name} <{from_email}>"
        message['To'] = ", ".join(recipients)
        
        # Create multipart alternative for text and HTML
        msg_alternative = MIMEMultipart('alternative')
        
        # Add plain text version
        text_part = MIMEText(email_body, 'plain', 'utf-8')
        msg_alternative.attach(text_part)
        
        # Add HTML version (inline report)
        full_html = f"""
        <div style="font-family: Arial, sans-serif; margin-bottom: 2rem;">
            <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{email_body}</pre>
        </div>
        <hr style="margin: 2rem 0;">
        {html_content}
        """
        html_part = MIMEText(full_html, 'html', 'utf-8')
        msg_alternative.attach(html_part)
        
        # Attach the alternative part to main message
        message.attach(msg_alternative)
        
        # Attach HTML file if requested
        if attach_file and Path(html_file_path).exists():
            with open(html_file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename=gitlab_code_changes_report_{datetime.now().strftime("%Y%m%d")}.html',
            )
            message.attach(part)
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, recipients, message.as_string())
        
        print(f"✅ Email sent successfully!")
        print(f"📧 Recipients: {', '.join(recipients)}")
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate GitLab code changes report and send via email",
        epilog="""
Examples:
  # Generate report and send to default recipients
  python scripts/generate_and_send_report.py

  # Generate report for specific groups and send
  python scripts/generate_and_send_report.py --groups 1721,1267

  # Send to custom recipients
  python scripts/generate_and_send_report.py --recipients user1@company.com,user2@company.com

  # Generate report only (no email)
  python scripts/generate_and_send_report.py --no-email

  # Use default branch only (faster)
  python scripts/generate_and_send_report.py --default-branch-only
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--groups', '-g',
        help='Comma-separated list of GitLab group IDs to analyze (default: all known groups)'
    )
    parser.add_argument(
        '--recipients', '-r',
        default='tassawee.t@tspacedigital.com,totrakool.k@thaibev.com,jirakit.b@tcc-technology.com',
        help='Comma-separated list of email recipients (default: tassawee.t@tspacedigital.com,totrakool.k@thaibev.com,jirakit.b@tcc-technology.com)'
    )
    parser.add_argument(
        '--subject', '-s',
        help='Email subject (default: auto-generated with date)'
    )
    parser.add_argument(
        '--output', '-o',
        default='gitlab_code_changes_report.html',
        help='Output HTML file name (default: gitlab_code_changes_report.html)'
    )
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Generate report only, do not send email'
    )
    parser.add_argument(
        '--no-attachment',
        action='store_true',
        help='Send email without HTML file attachment (inline only)'
    )
    parser.add_argument(
        '--default-branch-only',
        action='store_true',
        help='Only count commits from default branch (faster, but may miss feature branch activity)'
    )
    
    args = parser.parse_args()
    
    # Parse group IDs
    if args.groups:
        try:
            group_ids = [int(gid.strip()) for gid in args.groups.split(',')]
        except ValueError:
            print("❌ Invalid group IDs. Please provide comma-separated integers.")
            return 1
    else:
        # Use all known groups by default
        group_ids = list(GROUP_NAMES.keys())
        print(f"📋 No groups specified, using all known groups: {', '.join(f'{gid} ({name})' for gid, name in GROUP_NAMES.items())}")
    
    # Parse recipients
    recipients = [email.strip() for email in args.recipients.split(',')]
    
    # Generate subject if not provided
    if not args.subject:
        subject = f"GitLab Code Changes Report - {datetime.now().strftime('%Y-%m-%d')}"
    else:
        subject = args.subject
    
    # Get GitLab configuration
    try:
        gitlab_url = get_env_or_exit('GITLAB_URL', 'Your GitLab instance URL')
        gitlab_token = get_env_or_exit('GITLAB_TOKEN', 'Your GitLab API token')
    except SystemExit:
        return 1
    
    try:
        print(f"🚀 Starting GitLab code changes analysis...")
        
        if args.default_branch_only:
            print("📋 Mode: Default branch only (faster, but may miss feature branch activity)")
        else:
            print("🌿 Mode: All active branches (comprehensive analysis including feature branches)")
        
        # Analyze groups
        projects_data = analyze_groups_code_changes(group_ids, gitlab_url, gitlab_token, args.default_branch_only)
        
        if not projects_data:
            print("❌ No project data collected. Check your group IDs and permissions.")
            return 1
        
        # Generate HTML report
        print(f"📄 Generating HTML report: {args.output}")
        generate_html_report(projects_data, args.output)
        print(f"✅ HTML report saved to: {args.output}")
        
        # Send email if requested
        if not args.no_email:
            print(f"📧 Sending email to: {', '.join(recipients)}")
            success = send_report_email(
                args.output, 
                recipients, 
                subject, 
                attach_file=not args.no_attachment
            )
            
            if not success:
                return 1
        else:
            print("📋 Email sending skipped (--no-email flag used)")
        
        print(f"✅ Process completed successfully!")
        print(f"📊 Analyzed {len(projects_data)} branch entries")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 