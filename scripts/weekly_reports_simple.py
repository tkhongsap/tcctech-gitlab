#!/usr/bin/env python3
"""Simplified weekly productivity reports that works without additional dependencies."""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def get_env_or_exit(key: str, description: str) -> str:
    """Get environment variable or exit with helpful message."""
    value = os.getenv(key)
    if not value:
        print(f"❌ Missing required environment variable: {key}")
        print(f"   {description}")
        print(f"   Please set it in your environment or .env file")
        sys.exit(1)
    return value

def simple_gitlab_request(url: str, token: str, endpoint: str, params: Dict = None) -> List[Dict]:
    """Make a simple GitLab API request."""
    import requests
    
    headers = {"Authorization": f"Bearer {token}"}
    full_url = f"{url}/api/v4/{endpoint}"
    
    try:
        response = requests.get(full_url, headers=headers, params=params or {})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ GitLab API Error: {e}")
        return []

def generate_simple_report(groups: List[int], gitlab_url: str, gitlab_token: str, weeks: int = 1) -> Dict[str, Any]:
    """Generate a simplified weekly report."""
    print(f"📊 Generating report for {len(groups)} groups over {weeks} week(s)...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)
    
    report = {
        'metadata': {
            'generated_at': end_date.isoformat(),
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'weeks_analyzed': weeks,
            'groups_analyzed': len(groups)
        },
        'summary': {
            'total_projects': 0,
            'total_commits': 0,
            'total_merge_requests': 0,
            'total_issues': 0,
            'active_projects': 0
        },
        'projects': [],
        'top_contributors': {}
    }
    
    contributors = defaultdict(int)
    
    for group_id in groups:
        print(f"  📁 Analyzing group {group_id}...")
        
        # Get projects in group
        projects = simple_gitlab_request(
            gitlab_url, gitlab_token, 
            f"groups/{group_id}/projects",
            {"include_subgroups": "true", "archived": "false"}
        )
        
        report['summary']['total_projects'] += len(projects)
        
        for project in projects[:10]:  # Limit to first 10 projects to avoid rate limits
            project_id = project['id']
            project_name = project['name']
            
            print(f"    🔍 Analyzing project: {project_name}")
            
            # Get recent commits
            commits = simple_gitlab_request(
                gitlab_url, gitlab_token,
                f"projects/{project_id}/repository/commits",
                {"since": start_date.isoformat(), "until": end_date.isoformat()}
            )
            
            # Get merge requests
            merge_requests = simple_gitlab_request(
                gitlab_url, gitlab_token,
                f"projects/{project_id}/merge_requests",
                {"created_after": start_date.isoformat(), "created_before": end_date.isoformat()}
            )
            
            # Get issues
            issues = simple_gitlab_request(
                gitlab_url, gitlab_token,
                f"projects/{project_id}/issues",
                {"created_after": start_date.isoformat(), "created_before": end_date.isoformat()}
            )
            
            # Count contributors
            for commit in commits:
                author = commit.get('author_name', 'Unknown')
                contributors[author] += 1
            
            project_data = {
                'name': project_name,
                'id': project_id,
                'commits': len(commits),
                'merge_requests': len(merge_requests),
                'issues': len(issues),
                'last_activity': project.get('last_activity_at', 'Unknown')
            }
            
            report['projects'].append(project_data)
            report['summary']['total_commits'] += len(commits)
            report['summary']['total_merge_requests'] += len(merge_requests)
            report['summary']['total_issues'] += len(issues)
            
            if len(commits) > 0:
                report['summary']['active_projects'] += 1
    
    # Sort contributors by activity
    report['top_contributors'] = dict(sorted(contributors.items(), key=lambda x: x[1], reverse=True)[:10])
    
    return report

def generate_simple_html_report(report_data: Dict[str, Any], team_name: str = "Development Team") -> str:
    """Generate a simple HTML report."""
    metadata = report_data['metadata']
    summary = report_data['summary']
    projects = report_data['projects']
    contributors = report_data['top_contributors']
    
    start_date = datetime.fromisoformat(metadata['period_start']).strftime('%B %d')
    end_date = datetime.fromisoformat(metadata['period_end']).strftime('%B %d, %Y')
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Weekly Productivity Report - {team_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .section {{ margin: 20px 0; padding: 20px; border-left: 4px solid #667eea; background: #f9f9f9; }}
        .metrics {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
        .metric {{ background: white; padding: 15px; border-radius: 6px; text-align: center; flex: 1; min-width: 150px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ color: #666; font-size: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Weekly Productivity Report</h1>
        <p>{team_name} • {start_date} - {end_date}</p>
    </div>
    
    <div class="section">
        <h2>📈 Summary Metrics</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{summary['total_commits']}</div>
                <div class="metric-label">Total Commits</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary['total_merge_requests']}</div>
                <div class="metric-label">Merge Requests</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary['total_issues']}</div>
                <div class="metric-label">Issues</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary['active_projects']}</div>
                <div class="metric-label">Active Projects</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🏆 Top Contributors</h2>
        <table>
            <tr><th>Developer</th><th>Commits</th></tr>
    """
    
    for contributor, commits in contributors.items():
        html += f"<tr><td>{contributor}</td><td>{commits}</td></tr>"
    
    html += """
        </table>
    </div>
    
    <div class="section">
        <h2>📁 Project Activity</h2>
        <table>
            <tr><th>Project</th><th>Commits</th><th>MRs</th><th>Issues</th></tr>
    """
    
    for project in sorted(projects, key=lambda x: x['commits'], reverse=True)[:15]:
        html += f"""
        <tr>
            <td>{project['name']}</td>
            <td>{project['commits']}</td>
            <td>{project['merge_requests']}</td>
            <td>{project['issues']}</td>
        </tr>
        """
    
    html += """
        </table>
    </div>
    
    <div class="section">
        <h2>💡 Quick Insights</h2>
        <ul>
    """
    
    if summary['total_commits'] > 50:
        html += "<li>🎯 High team activity with strong commit volume</li>"
    elif summary['total_commits'] < 10:
        html += "<li>⚠️ Low commit activity - consider checking project status</li>"
    
    if len(contributors) > 5:
        html += "<li>👥 Good team collaboration with multiple active contributors</li>"
    elif len(contributors) < 3:
        html += "<li>👤 Limited contributor diversity - consider knowledge sharing</li>"
    
    active_rate = (summary['active_projects'] / max(summary['total_projects'], 1)) * 100
    if active_rate > 70:
        html += "<li>🚀 Most projects showing recent activity</li>"
    else:
        html += "<li>📉 Some projects may need attention or archiving</li>"
    
    html += """
        </ul>
    </div>
    
    <div style="text-align: center; margin: 40px 0; color: #666; font-size: 12px;">
        Generated by GitLab Analytics - Weekly Productivity Reports
    </div>
</body>
</html>
    """
    
    return html

def send_simple_email(html_content: str, recipient: str, subject: str) -> bool:
    """Send email using simple SMTP (requires email config in environment)."""
    try:
        import smtplib
        import ssl
        from email.mime.text import MimeText
        from email.mime.multipart import MimeMultipart
    except ImportError as e:
        print(f"❌ Email functionality not available: {e}")
        return False
    
    # Get email configuration from environment
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = get_env_or_exit('SMTP_USERNAME', 'Your email username')
        smtp_password = get_env_or_exit('SMTP_PASSWORD', 'Your email password or app password')
        from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
        from_name = os.getenv('SMTP_FROM_NAME', 'GitLab Analytics')
        
        # Create message
        message = MimeMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{from_name} <{from_email}>"
        message['To'] = recipient
        
        # Add HTML content
        html_part = MimeText(html_content, 'html', 'utf-8')
        message.attach(html_part)
        
        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, [recipient], message.as_string())
        
        return True
        
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        print("💡 Make sure to set SMTP_USERNAME and SMTP_PASSWORD environment variables")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate simplified weekly productivity reports")
    
    parser.add_argument('--groups', '-g', required=True, help='Comma-separated GitLab group IDs')
    parser.add_argument('--email', help='Email recipient')
    parser.add_argument('--output', '-o', help='Output HTML file')
    parser.add_argument('--weeks', type=int, default=1, help='Number of weeks (default: 1)')
    parser.add_argument('--team-name', default='Development Team', help='Team name')
    parser.add_argument('--dry-run', action='store_true', help='Generate but don\'t send email')
    
    args = parser.parse_args()
    
    # Parse group IDs
    try:
        group_ids = [int(gid.strip()) for gid in args.groups.split(',')]
    except ValueError:
        print("❌ Invalid group IDs. Please provide comma-separated integers.")
        return 1
    
    # Get GitLab configuration
    gitlab_url = get_env_or_exit('GITLAB_URL', 'Your GitLab instance URL (e.g., https://gitlab.com)')
    gitlab_token = get_env_or_exit('GITLAB_TOKEN', 'Your GitLab API token')
    
    try:
        print(f"🚀 Starting weekly report generation...")
        
        # Generate report data
        report_data = generate_simple_report(group_ids, gitlab_url, gitlab_token, args.weeks)
        
        # Generate HTML
        html_content = generate_simple_html_report(report_data, args.team_name)
        
        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ Report saved to: {output_path}")
        
        # Send email if requested
        if args.email and not args.dry_run:
            subject = f"Weekly Productivity Report - {args.team_name}"
            success = send_simple_email(html_content, args.email, subject)
            if success:
                print(f"✅ Email sent successfully to: {args.email}")
            else:
                print(f"❌ Failed to send email to: {args.email}")
                return 1
        elif args.email and args.dry_run:
            print(f"🔍 Dry run: Would send email to {args.email}")
        
        # Print summary
        summary = report_data['summary']
        print(f"\n📊 Report Summary:")
        print(f"   Total Projects: {summary['total_projects']}")
        print(f"   Total Commits: {summary['total_commits']}")
        print(f"   Active Projects: {summary['active_projects']}")
        print(f"   Top Contributors: {len(report_data['top_contributors'])}")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())