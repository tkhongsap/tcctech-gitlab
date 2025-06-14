#!/usr/bin/env python3
"""Generate executive dashboard with enhanced features - simplified version."""

import sys
import os
import argparse
import json
import html
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback .env parser
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"\'')

# Group name mapping
GROUP_NAMES = {
    1721: "AI-ML-Services",
    1267: "Research Repos",
    1269: "Internal Services",
    119: "iland"
}

def get_env_or_exit(key: str, description: str) -> str:
    """Get environment variable or exit with helpful message."""
    value = os.getenv(key)
    if not value:
        print(f"❌ Missing required environment variable: {key}")
        print(f"   {description}")
        sys.exit(1)
    return value

def simple_gitlab_request(url: str, token: str, endpoint: str, params: Dict = None) -> Any:
    """Make a simple GitLab API request with pagination support."""
    headers = {"Authorization": f"Bearer {token}"}
    full_url = f"{url}/api/v4/{endpoint}"
    
    all_results = []
    page = 1
    per_page = 50  # Reduced page size for stability
    
    try:
        while True:
            request_params = params or {}
            request_params.update({'page': page, 'per_page': per_page})
            
            response = requests.get(full_url, headers=headers, params=request_params, timeout=30)
            response.raise_for_status()
            
            results = response.json()
            if not results:
                break
                
            all_results.extend(results)
            
            # Check if there are more pages
            if len(results) < per_page:
                break
            page += 1
            
            # Limit to prevent infinite loops
            if page > 20:
                break
            
        return all_results
    except requests.exceptions.RequestException as e:
        print(f"❌ GitLab API Error: {e}")
        return []

def analyze_simple_groups(group_ids: List[int], gitlab_url: str, gitlab_token: str, days: int = 30) -> Dict[str, Any]:
    """Analyze GitLab groups with simplified approach."""
    print(f"📊 Analyzing {len(group_ids)} groups...")
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    report_data = {
        'metadata': {
            'generated_at': end_date.isoformat(),
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'groups': {},
        'projects': [],
        'contributors': Counter(),
        'technology_stack': Counter(),
        'daily_activity': defaultdict(int),
        'summary': {
            'total_projects': 0,
            'active_projects': 0,
            'total_commits': 0,
            'total_mrs': 0,
            'total_issues': 0,
            'unique_contributors': 0,
            'health_distribution': defaultdict(int)
        },
        'issue_analytics': {
            'total_open': 0,
            'by_priority': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'by_type': {'bug': 0, 'feature': 0, 'enhancement': 0, 'other': 0},
            'overdue': 0,
            'unassigned': 0,
            'assignee_workload': defaultdict(int),
            'project_issues': defaultdict(int)
        },
        'ai_recommendations': [],
        'team_analytics': {},
        'all_issues': []
    }
    
    for group_id in group_ids:
        print(f"  📁 Processing group {group_id} ({GROUP_NAMES.get(group_id, f'Group {group_id}')})...")
        
        # Get group projects
        projects = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"groups/{group_id}/projects",
            {"include_subgroups": "true", "archived": "false"}
        )
        
        group_data = {
            'id': group_id,
            'name': GROUP_NAMES.get(group_id, f'Group {group_id}'),
            'projects': projects,  # Store the full list for compatibility
            'commits': 0,
            'total_commits': 0,
            'contributors': 0,
            'open_issues': 0,
            'open_mrs': 0,
            'avg_health_score': 75,
            'health_grade': 'B',
            'active_projects': 0,
            'total_issues': 0,
            'unique_contributors': 0
        }
        
        # Process each project
        for project in projects[:10]:  # Limit to first 10 projects
            try:
                print(f"    📋 Analyzing project: {project['name']}")
                
                # Basic project metrics
                project_metrics = {
                    'id': project['id'],
                    'name': project['name'],
                    'description': project.get('description', ''),
                    'health_score': 75,
                    'commits_30d': 0,
                    'open_issues': 0,
                    'open_mrs': 0,
                    'contributors_30d': 0,
                    'days_since_last_commit': 0,
                    'status': 'active',  # Default status
                    'grade': 'B',  # Default grade
                    'health_grade': 'B'  # Default health grade
                }
                
                # Get recent commits
                commits = simple_gitlab_request(
                    gitlab_url, gitlab_token,
                    f"projects/{project['id']}/repository/commits",
                    {"since": start_date.isoformat()}
                )
                
                project_metrics['commits_30d'] = len(commits)
                group_data['commits'] += len(commits)
                group_data['total_commits'] += len(commits)
                report_data['summary']['total_commits'] += len(commits)
                
                # Process contributors
                contributors = set()
                for commit in commits:
                    author = commit.get('author_name', 'Unknown')
                    contributors.add(author)
                    report_data['contributors'][author] += 1
                    
                    # Track daily activity
                    commit_date = datetime.fromisoformat(commit['created_at'].replace('Z', '+00:00')).date()
                    report_data['daily_activity'][str(commit_date)] += 1
                
                project_metrics['contributors_30d'] = len(contributors)
                
                # Get issues
                issues = simple_gitlab_request(
                    gitlab_url, gitlab_token,
                    f"projects/{project['id']}/issues",
                    {"state": "opened"}
                )
                
                project_metrics['open_issues'] = len(issues)
                group_data['open_issues'] += len(issues)
                report_data['summary']['total_issues'] += len(issues)
                report_data['issue_analytics']['total_open'] += len(issues)
                report_data['issue_analytics']['project_issues'][project['name']] = len(issues)
                
                # Process issues for analytics
                for issue in issues:
                    labels = issue.get('labels', [])
                    
                    # Determine priority
                    if any(label.lower() in ['critical', 'priority::critical'] for label in labels):
                        report_data['issue_analytics']['by_priority']['critical'] += 1
                    elif any(label.lower() in ['high', 'priority::high'] for label in labels):
                        report_data['issue_analytics']['by_priority']['high'] += 1
                    elif any(label.lower() in ['low', 'priority::low'] for label in labels):
                        report_data['issue_analytics']['by_priority']['low'] += 1
                    else:
                        report_data['issue_analytics']['by_priority']['medium'] += 1
                    
                    # Determine type
                    if 'bug' in labels:
                        report_data['issue_analytics']['by_type']['bug'] += 1
                    elif 'feature' in labels:
                        report_data['issue_analytics']['by_type']['feature'] += 1
                    elif 'enhancement' in labels:
                        report_data['issue_analytics']['by_type']['enhancement'] += 1
                    else:
                        report_data['issue_analytics']['by_type']['other'] += 1
                    
                    # Track assignee workload
                    assignee = issue.get('assignee')
                    if assignee:
                        report_data['issue_analytics']['assignee_workload'][assignee['name']] += 1
                    else:
                        report_data['issue_analytics']['unassigned'] += 1
                    
                    # Add to all issues list
                    priority = 'medium'
                    for p in ['critical', 'high', 'low']:
                        if any(p in label.lower() for label in labels):
                            priority = p
                            break
                    
                    created_at = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                    age_days = (datetime.now(timezone.utc) - created_at).days
                    
                    report_data['all_issues'].append({
                        'id': issue['id'],
                        'iid': issue['iid'],
                        'title': issue['title'],
                        'project_name': project['name'],
                        'priority': priority,
                        'type': 'bug' if 'bug' in labels else 'feature' if 'feature' in labels else 'other',
                        'assignee': assignee,
                        'labels': labels,
                        'due_date': issue.get('due_date'),
                        'is_overdue': False,
                        'age_days': age_days,
                        'web_url': issue['web_url']
                    })
                
                # Get merge requests
                mrs = simple_gitlab_request(
                    gitlab_url, gitlab_token,
                    f"projects/{project['id']}/merge_requests",
                    {"state": "opened"}
                )
                
                project_metrics['open_mrs'] = len(mrs)
                group_data['open_mrs'] += len(mrs)
                report_data['summary']['total_mrs'] += len(mrs)
                
                report_data['projects'].append(project_metrics)
                
            except Exception as e:
                print(f"    ⚠️ Error analyzing project {project['name']}: {e}")
                continue
        
        group_data['contributors'] = len(set(report_data['contributors'].keys()))
        group_data['unique_contributors'] = group_data['contributors']
        group_data['active_projects'] = len(projects)  # Simplified
        group_data['total_issues'] = group_data['open_issues']
        report_data['groups'][group_id] = group_data
    
    # Generate summary
    report_data['summary']['total_projects'] = len(report_data['projects'])
    report_data['summary']['active_projects'] = len([p for p in report_data['projects'] if p['commits_30d'] > 0])
    report_data['summary']['unique_contributors'] = len(report_data['contributors'])
    
    # Generate simple team analytics
    for contributor, commits in report_data['contributors'].most_common(20):
        report_data['team_analytics'][contributor] = {
            'commits': commits,
            'projects': set([p['name'] for p in report_data['projects'] if any(contributor in c.get('author_name', '') for c in simple_gitlab_request(gitlab_url, gitlab_token, f"projects/{p['id']}/repository/commits", {"since": start_date.isoformat(), "author": contributor}) or [])]),
            'issues_assigned': report_data['issue_analytics']['assignee_workload'].get(contributor, 0),
            'issues_resolved': 0,
            'merge_requests': 0,
            'recent_activity': []
        }
    
    # Generate AI recommendations
    recommendations = []
    if report_data['issue_analytics']['by_priority']['critical'] > 0:
        recommendations.append({
            'type': 'critical',
            'title': 'Critical Issues Require Immediate Attention',
            'message': f"{report_data['issue_analytics']['by_priority']['critical']} critical issues are open",
            'action': 'Allocate senior developers to resolve critical issues immediately'
        })
    
    if report_data['issue_analytics']['unassigned'] > 5:
        recommendations.append({
            'type': 'medium',
            'title': 'Many Unassigned Issues',
            'message': f"{report_data['issue_analytics']['unassigned']} issues are unassigned",
            'action': 'Review and assign issues to appropriate team members'
        })
    
    workload = report_data['issue_analytics']['assignee_workload']
    if workload:
        max_load = max(workload.values())
        avg_load = sum(workload.values()) / len(workload)
        if max_load > avg_load * 2:
            overloaded = [k for k, v in workload.items() if v == max_load][0]
            recommendations.append({
                'type': 'high',
                'title': 'Workload Imbalance Detected',
                'message': f"{overloaded} has {max_load} issues (significantly above average)",
                'action': 'Redistribute issues to balance team workload'
            })
    
    report_data['ai_recommendations'] = recommendations
    
    return report_data

# Import the HTML generation functions from the main script
sys.path.insert(0, os.path.dirname(__file__))
from generate_executive_dashboard import generate_shadcn_dashboard

def main():
    parser = argparse.ArgumentParser(description='Generate simplified executive dashboard')
    parser.add_argument('--groups', '-g', required=True, help='Comma-separated list of GitLab group IDs')
    parser.add_argument('--output', '-o', default='simple_dashboard.html', help='Output file path')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    parser.add_argument('--team-name', default='Development Team', help='Team name for the report')
    
    args = parser.parse_args()
    
    # Parse group IDs
    try:
        group_ids = [int(gid.strip()) for gid in args.groups.split(',')]
    except ValueError:
        print("❌ Invalid group IDs. Please provide comma-separated integers.")
        return 1
    
    # Get GitLab configuration
    gitlab_url = get_env_or_exit('GITLAB_URL', 'Your GitLab instance URL')
    gitlab_token = get_env_or_exit('GITLAB_TOKEN', 'Your GitLab API token')
    
    try:
        print(f"🚀 Starting simplified dashboard generation...")
        
        # Analyze groups
        report_data = analyze_simple_groups(group_ids, gitlab_url, gitlab_token, args.days)
        
        # Generate dashboard
        html_content = generate_shadcn_dashboard(report_data, args.team_name)
        
        # Save to file
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard saved to: {output_path}")
        
        # Print summary
        summary = report_data['summary']
        print(f"\n📊 Analysis Summary:")
        print(f"   Total Projects: {summary['total_projects']}")
        print(f"   Active Projects: {summary['active_projects']}")
        print(f"   Total Commits: {summary['total_commits']}")
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   Unique Contributors: {summary['unique_contributors']}")
        print(f"   AI Recommendations: {len(report_data['ai_recommendations'])}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())