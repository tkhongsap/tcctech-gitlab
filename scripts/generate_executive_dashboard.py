#!/usr/bin/env python3
"""Generate executive dashboard with shadcn/ui-inspired design for GitLab analytics."""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import math
import re

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Tip: Install python-dotenv to load .env files automatically")
    print("   pip install python-dotenv")

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our services
from src.api.client import GitLabClient
from src.services.group_enhancement import GroupEnhancementService
from src.services.branch_service import BranchService
from src.services.issue_service import IssueService

# Project descriptions (can be expanded with more projects)
PROJECT_DESCRIPTIONS = {
    'llama-index-rag-pipeline': 'Advanced RAG implementation using LlamaIndex for intelligent document retrieval and question answering. Integrates with multiple data sources and supports custom embeddings.',
    'e-recruitment-suite': 'Comprehensive recruitment management system with AI-powered resume screening, candidate tracking, and interview scheduling capabilities.',
    'resume-extractor': 'Machine learning service for extracting structured information from resumes. Supports multiple formats and languages with high accuracy.',
    'dts-code-buddy': 'AI-powered code assistant providing intelligent code suggestions, review automation, and best practices enforcement for development teams.',
    'dts-po-buddy': 'Product owner assistant tool featuring requirement analysis, user story generation, and backlog prioritization using NLP techniques.',
    'mlflow-manager': 'MLOps platform integration for experiment tracking, model versioning, and deployment pipeline management across the organization.',
    'open-webui': 'Modern web interface for interacting with various LLM models. Features chat history, prompt management, and multi-model support.',
    'airflow-pipeline': 'Data orchestration platform for managing complex ETL workflows, ML pipelines, and scheduled data processing tasks.',
    'label-studio': 'Data labeling and annotation platform for creating high-quality training datasets. Supports images, text, audio, and video.',
    'service-status': 'Real-time monitoring dashboard for tracking service health, uptime, and performance metrics across all deployed applications.',
    'azure-ai-foundry': 'Integration framework for Azure AI services including cognitive services, machine learning, and AI-powered automation.',
    'fastapi-claim-detection': 'High-performance API service for detecting and classifying insurance claims using advanced NLP and fraud detection algorithms.',
    'dts-sensei': 'Knowledge management system with AI-powered search, documentation generation, and expertise mapping for technical teams.',
    'rag_knowledge_management': 'Enterprise knowledge base with RAG-powered search, automatic knowledge extraction, and intelligent Q&A capabilities.',
    'copilot-survey-bot': 'Automated survey creation and analysis tool with natural language processing for sentiment analysis and insight extraction.',
    'fine-tune-vision': 'Computer vision model fine-tuning framework supporting custom datasets, transfer learning, and deployment optimization.',
    'logging-handler': 'Centralized logging service with intelligent log parsing, anomaly detection, and automated alert generation.',
    'map-intelligent': 'Geospatial analytics platform with AI-powered location intelligence, route optimization, and demographic analysis.',
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
    import requests
    
    headers = {"Authorization": f"Bearer {token}"}
    full_url = f"{url}/api/v4/{endpoint}"
    
    all_results = []
    page = 1
    per_page = 100
    
    try:
        while True:
            request_params = params or {}
            request_params.update({'page': page, 'per_page': per_page})
            
            response = requests.get(full_url, headers=headers, params=request_params)
            response.raise_for_status()
            
            results = response.json()
            if not results:
                break
                
            all_results.extend(results)
            
            # Check if there are more pages
            if len(results) < per_page:
                break
            page += 1
            
        return all_results
    except requests.exceptions.RequestException as e:
        print(f"❌ GitLab API Error: {e}")
        return []

def calculate_health_score(metrics: Dict[str, Any]) -> Tuple[int, str]:
    """Calculate project health score and grade."""
    score = 100
    
    # Activity scoring
    if metrics['commits_30d'] == 0:
        score -= 30
    elif metrics['commits_30d'] < 5:
        score -= 15
    elif metrics['commits_30d'] > 50:
        score += 5
    
    # Issue management
    if metrics['open_issues'] > 20:
        score -= 20
    elif metrics['open_issues'] > 10:
        score -= 10
    elif metrics['open_issues'] < 5:
        score += 5
    
    # MR efficiency
    if metrics['open_mrs'] > 10:
        score -= 15
    elif metrics['open_mrs'] > 5:
        score -= 5
    
    # Collaboration
    if metrics['contributors_30d'] == 1:
        score -= 10
    elif metrics['contributors_30d'] > 3:
        score += 10
    
    # Recent activity bonus
    if metrics['days_since_last_commit'] < 3:
        score += 5
    elif metrics['days_since_last_commit'] > 14:
        score -= 20
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    # Assign grade
    if score >= 95:
        grade = 'A+'
    elif score >= 90:
        grade = 'A'
    elif score >= 85:
        grade = 'A-'
    elif score >= 80:
        grade = 'B+'
    elif score >= 75:
        grade = 'B'
    elif score >= 70:
        grade = 'B-'
    elif score >= 65:
        grade = 'C+'
    elif score >= 60:
        grade = 'C'
    elif score >= 55:
        grade = 'C-'
    else:
        grade = 'D'
    
    return score, grade

def get_activity_sparkline(daily_commits: List[int]) -> str:
    """Generate sparkline visualization for activity."""
    if not daily_commits:
        return ""
    
    # Normalize to 0-7 range for sparkline characters
    max_val = max(daily_commits) if max(daily_commits) > 0 else 1
    normalized = [int(val / max_val * 7) for val in daily_commits]
    
    # Sparkline characters
    sparks = "▁▂▃▄▅▆▇█"
    
    return ''.join(sparks[n] for n in normalized)

def analyze_project(project: Dict, gitlab_url: str, gitlab_token: str, days: int = 30) -> Dict[str, Any]:
    """Analyze a single project with 30-day metrics including branch and issue analysis."""
    project_id = project['id']
    project_name = project['name']
    
    # Use timezone-aware datetime
    from datetime import timezone
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Initialize metrics
    metrics = {
        'id': project_id,
        'name': project_name,
        'path': project.get('path_with_namespace', ''),
        'description': PROJECT_DESCRIPTIONS.get(project_name, project.get('description', '')),
        'visibility': project.get('visibility', 'private'),
        'default_branch': project.get('default_branch', 'main'),
        'created_at': project.get('created_at', ''),
        'last_activity': project.get('last_activity_at', ''),
        'commits_30d': 0,
        'commits_by_day': defaultdict(int),
        'contributors_30d': 0,
        'contributors': Counter(),
        'mrs_created': 0,
        'mrs_merged': 0,
        'mrs_closed': 0,
        'open_mrs': 0,
        'issues_created': 0,
        'issues_closed': 0,
        'open_issues': 0,
        'languages': {},
        'days_since_last_commit': 999,
        'activity_sparkline': '',
        'health_score': 0,
        'health_grade': 'D',
        'status': 'inactive',
        # New enhanced metrics
        'branch_analysis': {},
        'issue_analysis': {},
        'enhancement_metadata': {
            'has_branch_analysis': False,
            'has_issue_analysis': False,
            'analysis_errors': []
        }
    }
    
    # Initialize enhanced services
    try:
        client = GitLabClient(gitlab_url, gitlab_token)
        branch_service = BranchService(client)
        issue_service = IssueService(client)
        enhanced_services_available = True
    except Exception as e:
        print(f"⚠️ Enhanced services not available for {project_name}: {e}")
        enhanced_services_available = False
        branch_service = None
        issue_service = None
    
    # Get commits
    commits = simple_gitlab_request(
        gitlab_url, gitlab_token,
        f"projects/{project_id}/repository/commits",
        {"since": start_date.isoformat(), "until": end_date.isoformat()}
    )
    
    if commits:
        metrics['commits_30d'] = len(commits)
        
        # Process commits
        for commit in commits:
            author = commit.get('author_name', 'Unknown')
            metrics['contributors'][author] += 1
            
            # Track daily commits
            commit_date = datetime.fromisoformat(commit['created_at'].replace('Z', '+00:00')).date()
            metrics['commits_by_day'][str(commit_date)] += 1
        
        metrics['contributors_30d'] = len(metrics['contributors'])
        
        # Calculate days since last commit
        last_commit_date = datetime.fromisoformat(commits[0]['created_at'].replace('Z', '+00:00'))
        metrics['days_since_last_commit'] = (end_date - last_commit_date).days
    
    # Get merge requests
    all_mrs = simple_gitlab_request(
        gitlab_url, gitlab_token,
        f"projects/{project_id}/merge_requests",
        {"scope": "all"}
    )
    
    # Filter MRs for the time period and count open MRs
    for mr in all_mrs:
        created_at = datetime.fromisoformat(mr['created_at'].replace('Z', '+00:00'))
        
        if mr['state'] == 'opened':
            metrics['open_mrs'] += 1
        
        if start_date <= created_at <= end_date:
            metrics['mrs_created'] += 1
            if mr['state'] == 'merged':
                metrics['mrs_merged'] += 1
            elif mr['state'] == 'closed':
                metrics['mrs_closed'] += 1
    
    # Get issues
    all_issues = simple_gitlab_request(
        gitlab_url, gitlab_token,
        f"projects/{project_id}/issues",
        {"scope": "all"}
    )
    
    # Count open issues and filter for time period
    for issue in all_issues:
        created_at = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
        
        if issue['state'] == 'opened':
            metrics['open_issues'] += 1
        
        if start_date <= created_at <= end_date:
            metrics['issues_created'] += 1
            if issue['state'] == 'closed':
                metrics['issues_closed'] += 1
    
    # Enhanced Branch Analysis
    if enhanced_services_available and branch_service:
        try:
            print(f"    📊 Analyzing branches for {project_name}...")
            branch_analysis = branch_service.analyze_project_branches(project_id, days)
            metrics['branch_analysis'] = branch_analysis
            metrics['enhancement_metadata']['has_branch_analysis'] = True
        except Exception as e:
            print(f"    ⚠️ Branch analysis failed for {project_name}: {e}")
            metrics['enhancement_metadata']['analysis_errors'].append(f"Branch analysis: {str(e)}")
            metrics['branch_analysis'] = {'error': str(e), 'active_branches': [], 'total_branches': 0}
    
    # Enhanced Issue Analysis
    if enhanced_services_available and issue_service:
        try:
            print(f"    📋 Analyzing issues for {project_name}...")
            issue_analysis = issue_service.analyze_project_issues(project_id, days)
            metrics['issue_analysis'] = issue_analysis
            metrics['enhancement_metadata']['has_issue_analysis'] = True
        except Exception as e:
            print(f"    ⚠️ Issue analysis failed for {project_name}: {e}")
            metrics['enhancement_metadata']['analysis_errors'].append(f"Issue analysis: {str(e)}")
            metrics['issue_analysis'] = {'error': str(e), 'recommendations': [], 'total_open': metrics['open_issues']}
    
    # Get languages
    try:
        languages_response = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"projects/{project_id}/languages",
            {}
        )
        if isinstance(languages_response, dict):
            metrics['languages'] = languages_response
    except:
        pass
    
    # Generate activity sparkline for last 14 days
    daily_values = []
    for i in range(14):
        date = (end_date - timedelta(days=13-i)).date()
        daily_values.append(metrics['commits_by_day'].get(str(date), 0))
    
    metrics['activity_sparkline'] = get_activity_sparkline(daily_values)
    
    # Calculate health score and grade
    metrics['health_score'], metrics['health_grade'] = calculate_health_score(metrics)
    
    # Determine status
    if metrics['days_since_last_commit'] < 7:
        metrics['status'] = 'active'
    elif metrics['days_since_last_commit'] < 30:
        metrics['status'] = 'maintenance'
    else:
        metrics['status'] = 'inactive'
    
    return metrics

def analyze_groups(group_ids: List[int], gitlab_url: str, gitlab_token: str, days: int = 30) -> Dict[str, Any]:
    """Analyze multiple GitLab groups with enhanced group information."""
    print(f"📊 Analyzing {len(group_ids)} groups over {days} days...")
    
    # Initialize GitLab client and group enhancement service
    try:
        client = GitLabClient(gitlab_url, gitlab_token)
        group_service = GroupEnhancementService(client)
    except Exception as e:
        print(f"⚠️ Could not initialize enhanced services, falling back to simple requests: {e}")
        client = None
        group_service = None
    
    report_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'start_date': (datetime.now() - timedelta(days=days)).isoformat(),
            'end_date': datetime.now().isoformat(),
            'groups_analyzed': len(group_ids)
        },
        'summary': {
            'total_projects': 0,
            'active_projects': 0,
            'total_commits': 0,
            'total_mrs': 0,
            'total_issues': 0,
            'unique_contributors': set(),
            'health_distribution': {'A+': 0, 'A': 0, 'A-': 0, 'B+': 0, 'B': 0, 'B-': 0, 'C+': 0, 'C': 0, 'C-': 0, 'D': 0}
        },
        'groups': {},
        'projects': [],
        'contributors': Counter(),
        'daily_activity': defaultdict(int),
        'technology_stack': Counter()
    }
    
    # Add specific iland repository
    iland_repo_url = "https://git.lab.tcctech.app/iland/llama-index-rag-pipeline"
    
    for group_id in group_ids:
        print(f"  📁 Analyzing group {group_id}...")
        
        # Get enhanced group info
        if group_service:
            try:
                enhanced_group = group_service.get_enhanced_group_info(group_id)
                group_name = enhanced_group['business_name']
                group_description = enhanced_group['business_description']
                group_metadata = enhanced_group
            except Exception as e:
                print(f"⚠️ Could not get enhanced group info for {group_id}, using fallback: {e}")
                group_info = simple_gitlab_request(
                    gitlab_url, gitlab_token,
                    f"groups/{group_id}",
                    {}
                )
                group_name = group_info['name'] if isinstance(group_info, dict) else f"Group {group_id}"
                group_description = group_info.get('description', '') if isinstance(group_info, dict) else ''
                group_metadata = group_info if isinstance(group_info, dict) else {}
        else:
            # Fallback to simple request
            group_info = simple_gitlab_request(
                gitlab_url, gitlab_token,
                f"groups/{group_id}",
                {}
            )
            group_name = group_info['name'] if isinstance(group_info, dict) else f"Group {group_id}"
            group_description = group_info.get('description', '') if isinstance(group_info, dict) else ''
            group_metadata = group_info if isinstance(group_info, dict) else {}
        
        # Get projects in group
        projects = simple_gitlab_request(
            gitlab_url, gitlab_token,
            f"groups/{group_id}/projects",
            {"include_subgroups": "true", "archived": "false"}
        )
        
        group_data = {
            'name': group_name,
            'id': group_id,
            'description': group_description,
            'metadata': group_metadata,
            'projects': [],
            'total_commits': 0,
            'total_mrs': 0,
            'total_issues': 0,
            'health_grade': 'B',
            'active_projects': 0,
            'enhancement_info': {
                'has_business_name': group_metadata.get('enhancement_metadata', {}).get('has_business_name', False),
                'has_business_description': group_metadata.get('enhancement_metadata', {}).get('has_business_description', False)
            }
        }
        
        for project in projects:
            print(f"    🔍 Analyzing project: {project['name']}")
            
            project_metrics = analyze_project(project, gitlab_url, gitlab_token, days)
            
            # Update group statistics
            group_data['projects'].append(project_metrics)
            group_data['total_commits'] += project_metrics['commits_30d']
            group_data['total_mrs'] += project_metrics['mrs_created']
            group_data['total_issues'] += project_metrics['issues_created']
            
            if project_metrics['status'] == 'active':
                group_data['active_projects'] += 1
            
            # Update global statistics
            report_data['summary']['total_commits'] += project_metrics['commits_30d']
            report_data['summary']['total_mrs'] += project_metrics['mrs_created']
            report_data['summary']['total_issues'] += project_metrics['issues_created']
            
            if project_metrics['status'] == 'active':
                report_data['summary']['active_projects'] += 1
            
            # Track contributors
            for contributor, count in project_metrics['contributors'].items():
                report_data['contributors'][contributor] += count
                report_data['summary']['unique_contributors'].add(contributor)
            
            # Track daily activity
            for date, commits in project_metrics['commits_by_day'].items():
                report_data['daily_activity'][date] += commits
            
            # Track technology stack
            for lang, percentage in project_metrics['languages'].items():
                report_data['technology_stack'][lang] += 1
            
            # Track health distribution
            report_data['summary']['health_distribution'][project_metrics['health_grade']] += 1
            
            # Add to global projects list
            report_data['projects'].append(project_metrics)
        
        # Calculate group health grade based on projects
        if group_data['projects']:
            avg_score = sum(p['health_score'] for p in group_data['projects']) / len(group_data['projects'])
            group_data['health_grade'] = calculate_health_score({'commits_30d': 10, 'open_issues': 5, 'open_mrs': 2, 'contributors_30d': 3, 'days_since_last_commit': 5})[1]
        
        report_data['groups'][group_id] = group_data
        report_data['summary']['total_projects'] += len(group_data['projects'])
    
    # Convert sets to counts
    report_data['summary']['unique_contributors'] = len(report_data['summary']['unique_contributors'])
    
    # Sort projects by health score
    report_data['projects'].sort(key=lambda x: x['health_score'], reverse=True)
    
    return report_data

def generate_shadcn_dashboard(report_data: Dict[str, Any], team_name: str = "Development Team") -> str:
    """Generate enhanced executive dashboard with new features."""
    metadata = report_data['metadata']
    summary = report_data['summary']
    groups = report_data['groups']
    projects = report_data['projects']
    contributors = report_data['contributors']
    
    # Prepare data for charts
    chart_dates = []
    chart_values = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).strftime('%Y-%m-%d')
        chart_dates.append(date)
        chart_values.append(report_data['daily_activity'].get(date, 0))
    
    # Calculate aggregate issue analysis
    aggregate_issues = calculate_aggregate_issues(projects)
    
    # Generate health score methodology
    health_methodology = generate_health_score_methodology()
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Dashboard - {team_name}</title>
    {generate_shadcn_styles()}
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <header class="header">
            <div class="header-content">
                <h1 class="dashboard-title">Executive Dashboard</h1>
                <p class="dashboard-subtitle">{team_name} • {metadata['period_days']} Day Analysis</p>
                <div class="header-meta">
                    <span class="meta-item">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</span>
                    <span class="meta-item">{summary['total_projects']} Projects Analyzed</span>
                </div>
            </div>
        </header>

        <!-- KPI Overview -->
        <section class="section">
            <h2 class="section-title">Key Performance Indicators</h2>
            <div class="kpi-grid">
                {generate_kpi_card('Total Commits', summary['total_commits'], 12.5, 'commits')}
                {generate_kpi_card('Merge Requests', summary['total_mrs'], 8.2, 'mrs')}
                {generate_kpi_card('Issues Resolved', summary['total_issues'], -5.1, 'issues')}
                {generate_kpi_card('Active Projects', summary['active_projects'], 0, 'projects', show_change=False)}
            </div>
            
            <!-- Activity Chart -->
            <div class="card chart-card">
                <h3 class="chart-title">30-Day Activity Trend</h3>
                <div class="chart-container">
                    {generate_activity_chart(chart_dates, chart_values)}
                </div>
            </div>
        </section>

        <!-- Group Analysis -->
        <section class="section">
            <h2 class="section-title">Group Analysis</h2>
            <div class="group-grid">
                {generate_group_cards(groups)}
            </div>
        </section>

        <!-- Issues Analysis & AI Recommendations -->
        <section class="section">
            <h2 class="section-title">Issues Analysis & AI Recommendations</h2>
            <div class="issues-analysis-container">
                {generate_issues_analysis_section(aggregate_issues)}
            </div>
        </section>

        <!-- Health Score Documentation -->
        <section class="section">
            <h2 class="section-title">Health Score Methodology</h2>
            <div class="health-methodology-container">
                {health_methodology}
            </div>
        </section>

        <!-- Project Portfolio -->
        <section class="section">
            <h2 class="section-title">Project Portfolio</h2>
            <div class="project-filters">
                <input type="text" class="search-input" placeholder="Search projects..." onkeyup="filterProjects(this.value)">
                <select class="filter-select" onchange="filterByStatus(this.value)">
                    <option value="">All Status</option>
                    <option value="active">Active</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="inactive">Inactive</option>
                </select>
            </div>
            <div class="project-grid" id="projectGrid">
                {generate_enhanced_project_cards(projects[:20])}  <!-- Enhanced project cards -->
            </div>
        </section>

        <!-- Team Performance -->
        <section class="section">
            <h2 class="section-title">Team Performance</h2>
            <div class="contributor-grid">
                {generate_contributor_cards(contributors.most_common(10))}
            </div>
            <div class="tech-stack-section">
                <h3 class="subsection-title">Technology Stack</h3>
                <div class="tech-stack-badges">
                    {generate_tech_stack_badges(report_data['technology_stack'].most_common(15))}
                </div>
            </div>
        </section>
    </div>

    {generate_dashboard_scripts()}
</body>
</html>
"""

def calculate_aggregate_issues(projects: List[Dict]) -> Dict[str, Any]:
    """Calculate aggregate issue analysis across all projects."""
    total_open = 0
    total_recommendations = []
    projects_with_issues = 0
    issue_types = defaultdict(int)
    issue_priorities = defaultdict(int)
    
    for project in projects:
        issue_analysis = project.get('issue_analysis', {})
        if issue_analysis and not issue_analysis.get('error'):
            projects_with_issues += 1
            total_open += issue_analysis.get('total_open', 0)
            
            # Aggregate recommendations
            for rec in issue_analysis.get('recommendations', []):
                total_recommendations.append({
                    'project': project['name'],
                    'project_id': project['id'],
                    **rec
                })
            
            # Aggregate issue types and priorities
            by_type = issue_analysis.get('by_type', {})
            by_priority = issue_analysis.get('by_priority', {})
            
            for issue_type, count in by_type.items():
                issue_types[issue_type] += count
            
            for priority, count in by_priority.items():
                issue_priorities[priority] += count
    
    # Sort recommendations by priority
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    total_recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'info'), 5))
    
    return {
        'total_open_issues': total_open,
        'projects_with_analysis': projects_with_issues,
        'total_projects': len(projects),
        'recommendations': total_recommendations[:10],  # Top 10 recommendations
        'all_recommendations': total_recommendations,
        'issue_types': dict(issue_types),
        'issue_priorities': dict(issue_priorities)
    }

def generate_issues_analysis_section(issues_data: Dict[str, Any]) -> str:
    """Generate the Issues Analysis & AI Recommendations section."""
    recommendations_html = ""
    
    for rec in issues_data['recommendations']:
        priority_class = f"recommendation-{rec.get('priority', 'info')}"
        type_icon = {
            'alert': '⚠️',
            'warning': '⚠️', 
            'critical': '🚨',
            'optimization': '🔧',
            'process': '📋',
            'maintenance': '🧹',
            'success': '✅'
        }.get(rec.get('type', 'info'), '💡')
        
        recommendations_html += f"""
        <div class="recommendation-card {priority_class}">
            <div class="recommendation-header">
                <span class="recommendation-icon">{type_icon}</span>
                <h4 class="recommendation-title">{rec.get('title', 'Recommendation')}</h4>
                <span class="recommendation-priority">{rec.get('priority', 'info').upper()}</span>
            </div>
            <p class="recommendation-message">{rec.get('message', '')}</p>
            <p class="recommendation-action"><strong>Action:</strong> {rec.get('action', '')}</p>
            <p class="recommendation-project"><strong>Project:</strong> {rec.get('project', 'System-wide')}</p>
        </div>
        """
    
    return f"""
    <div class="issues-overview-grid">
        <div class="issue-card total-open">
            <h3>Total Open Issues</h3>
            <span class="count">{issues_data['total_open_issues']}</span>
            <p class="card-subtitle">Across {issues_data['projects_with_analysis']} projects</p>
        </div>
        <div class="issue-card recommendations">
            <h3>AI Recommendations</h3>
            <span class="count">{len(issues_data['recommendations'])}</span>
            <p class="card-subtitle">Strategic insights generated</p>
        </div>
        <div class="issue-card projects-analyzed">
            <h3>Projects Analyzed</h3>
            <span class="count">{issues_data['projects_with_analysis']}</span>
            <p class="card-subtitle">Of {issues_data['total_projects']} total projects</p>
        </div>
    </div>
    
    <div class="recommendations-panel">
        <h3>Strategic Recommendations</h3>
        <div class="recommendations-list">
            {recommendations_html}
        </div>
    </div>
    """

def generate_health_score_methodology() -> str:
    """Generate the Health Score Methodology documentation."""
    return """
    <div class="health-methodology">
        <div class="methodology-tabs">
            <div class="tab-nav">
                <button class="tab-button active" onclick="showTab('components')">Scoring Components</button>
                <button class="tab-button" onclick="showTab('grading')">Grading Scale</button>
                <button class="tab-button" onclick="showTab('example')">Calculation Example</button>
            </div>
            
            <div id="components" class="tab-content active">
                <h4>Health Score Components</h4>
                <div class="component-grid">
                    <div class="component-card">
                        <h5>Activity (40%)</h5>
                        <ul>
                            <li>Commits in last 30 days (0-50+ commits)</li>
                            <li>Days since last commit (0-30+ days)</li>
                            <li>Contributor diversity (1-10+ contributors)</li>
                        </ul>
                    </div>
                    <div class="component-card">
                        <h5>Maintenance (30%)</h5>
                        <ul>
                            <li>Open issues count (0-20+ issues)</li>
                            <li>Issue resolution rate</li>
                            <li>Average issue age</li>
                        </ul>
                    </div>
                    <div class="component-card">
                        <h5>Collaboration (20%)</h5>
                        <ul>
                            <li>Merge request activity</li>
                            <li>Code review participation</li>
                            <li>Branch management practices</li>
                        </ul>
                    </div>
                    <div class="component-card">
                        <h5>Quality (10%)</h5>
                        <ul>
                            <li>CI/CD pipeline success rate</li>
                            <li>Test coverage (if available)</li>
                            <li>Documentation completeness</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div id="grading" class="tab-content">
                <h4>Grading Scale</h4>
                <div class="grading-scale">
                    <div class="grade-item grade-a-plus"><span class="grade">A+</span><span class="range">95-100 points</span><span class="description">Exceptional project health</span></div>
                    <div class="grade-item grade-a"><span class="grade">A</span><span class="range">90-94 points</span><span class="description">Excellent project health</span></div>
                    <div class="grade-item grade-a-minus"><span class="grade">A-</span><span class="range">85-89 points</span><span class="description">Very good project health</span></div>
                    <div class="grade-item grade-b-plus"><span class="grade">B+</span><span class="range">80-84 points</span><span class="description">Good project health</span></div>
                    <div class="grade-item grade-b"><span class="grade">B</span><span class="range">75-79 points</span><span class="description">Satisfactory project health</span></div>
                    <div class="grade-item grade-b-minus"><span class="grade">B-</span><span class="range">70-74 points</span><span class="description">Adequate project health</span></div>
                    <div class="grade-item grade-c-plus"><span class="grade">C+</span><span class="range">65-69 points</span><span class="description">Needs attention</span></div>
                    <div class="grade-item grade-c"><span class="grade">C</span><span class="range">60-64 points</span><span class="description">Requires improvement</span></div>
                    <div class="grade-item grade-c-minus"><span class="grade">C-</span><span class="range">55-59 points</span><span class="description">Poor project health</span></div>
                    <div class="grade-item grade-d"><span class="grade">D</span><span class="range">0-54 points</span><span class="description">Critical issues require immediate action</span></div>
                </div>
            </div>
            
            <div id="example" class="tab-content">
                <h4>Calculation Example</h4>
                <div class="calculation-example">
                    <div class="example-project">
                        <h5>Sample Project: "AI Assistant API"</h5>
                        <div class="calculation-steps">
                            <div class="step">
                                <strong>Activity Score (40%)</strong>
                                <p>• 25 commits in 30 days: +35 points</p>
                                <p>• 2 days since last commit: +5 points</p>
                                <p>• 4 contributors: +0 points</p>
                                <p><strong>Subtotal: 40/40 points</strong></p>
                            </div>
                            <div class="step">
                                <strong>Maintenance Score (30%)</strong>
                                <p>• 8 open issues: +25 points</p>
                                <p>• Good resolution rate: +5 points</p>
                                <p><strong>Subtotal: 30/30 points</strong></p>
                            </div>
                            <div class="step">
                                <strong>Collaboration Score (20%)</strong>
                                <p>• 5 MRs this period: +15 points</p>
                                <p>• Active code reviews: +5 points</p>
                                <p><strong>Subtotal: 20/20 points</strong></p>
                            </div>
                            <div class="step">
                                <strong>Quality Score (10%)</strong>
                                <p>• No pipeline data: +5 points</p>
                                <p><strong>Subtotal: 5/10 points</strong></p>
                            </div>
                            <div class="final-score">
                                <strong>Final Score: 95/100 = A+</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def generate_enhanced_project_cards(projects: List[Dict]) -> str:
    """Generate enhanced project cards with branch and issue information."""
    cards = []
    
    for project in projects:
        status_class = f"badge-{project['status']}"
        grade_class = f"badge-grade-{project['health_grade'].lower().replace('+', '-plus').replace('-', '-minus')}"
        
        description = project.get('description', '')
        if not description:
            description = f"A {project['visibility']} GitLab project with {project['commits_30d']} commits in the last 30 days."
        
        # Branch information
        branch_info = ""
        branch_analysis = project.get('branch_analysis', {})
        if branch_analysis and not branch_analysis.get('error'):
            active_branches = branch_analysis.get('active_branches', [])[:3]  # Top 3 branches
            branch_pills = []
            for branch in active_branches:
                activity_class = f"branch-{branch.get('activity_level', 'minimal')}"
                branch_pills.append(f'<span class="branch-pill {activity_class}">{branch["name"]}</span>')
            
            if branch_pills:
                branch_info = f'<div class="branch-section"><span class="branch-label">Active Branches:</span> {" ".join(branch_pills)}</div>'
        
        # Issue recommendations
        issue_info = ""
        issue_analysis = project.get('issue_analysis', {})
        if issue_analysis and not issue_analysis.get('error'):
            recommendations = issue_analysis.get('recommendations', [])
            if recommendations:
                high_priority_recs = [r for r in recommendations if r.get('priority') in ['critical', 'high']]
                if high_priority_recs:
                    rec_count = len(high_priority_recs)
                    issue_info = f'<div class="issue-alert">⚠️ {rec_count} high priority recommendation{"s" if rec_count > 1 else ""}</div>'
        
        cards.append(f"""
        <div class="card project-card enhanced-project-card" data-status="{project['status']}" data-name="{project['name'].lower()}">
            <div class="project-header">
                <h3 class="project-name">{project['name']}</h3>
                <div class="project-badges">
                    <span class="badge {status_class}">{project['status'].title()}</span>
                    <span class="badge badge-grade {grade_class}">{project['health_grade']}</span>
                </div>
            </div>
            <p class="project-description">{description}</p>
            
            {branch_info}
            {issue_info}
            
            <div class="project-stats">
                <div class="stat">
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>{project['commits_30d']} commits</span>
                </div>
                <div class="stat">
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
                    </svg>
                    <span>{project['mrs_created']} MRs</span>
                </div>
                <div class="stat">
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                    <span>{project['contributors_30d']} contributors</span>
                </div>
                <div class="stat">
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>{project.get('open_issues', 0)} issues</span>
                </div>
            </div>
            <div class="project-activity">
                {project['activity_sparkline']}
            </div>
        </div>
        """)
    
    return '\n'.join(cards)

def generate_health_score_methodology() -> str:
    """Generate the Health Score Methodology documentation."""
    return """
    <div class="health-methodology">
        <div class="methodology-tabs">
            <div class="tab-nav">
                <button class="tab-button active" onclick="showTab('components')">Scoring Components</button>
                <button class="tab-button" onclick="showTab('grading')">Grading Scale</button>
                <button class="tab-button" onclick="showTab('example')">Calculation Example</button>
            </div>
            
            <div id="components" class="tab-content active">
                <h4>Health Score Components</h4>
                <div class="component-grid">
                    <div class="component-card">
                        <h5>Activity (40%)</h5>
                        <ul>
                            <li>Commits in last 30 days (0-50+ commits)</li>
                            <li>Days since last commit (0-30+ days)</li>
                            <li>Contributor diversity (1-10+ contributors)</li>
                        </ul>
                    </div>
                    <div class="component-card">
                        <h5>Maintenance (30%)</h5>
                        <ul>
                            <li>Open issues count (0-20+ issues)</li>
                            <li>Issue resolution rate</li>
                            <li>Average issue age</li>
                        </ul>
                    </div>
                    <div class="component-card">
                        <h5>Collaboration (20%)</h5>
                        <ul>
                            <li>Merge request activity</li>
                            <li>Code review participation</li>
                            <li>Branch management practices</li>
                        </ul>
                    </div>
                    <div class="component-card">
                        <h5>Quality (10%)</h5>
                        <ul>
                            <li>CI/CD pipeline success rate</li>
                            <li>Test coverage (if available)</li>
                            <li>Documentation completeness</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div id="grading" class="tab-content">
                <h4>Grading Scale</h4>
                <div class="grading-scale">
                    <div class="grade-item grade-a-plus"><span class="grade">A+</span><span class="range">95-100 points</span><span class="description">Exceptional project health</span></div>
                    <div class="grade-item grade-a"><span class="grade">A</span><span class="range">90-94 points</span><span class="description">Excellent project health</span></div>
                    <div class="grade-item grade-a-minus"><span class="grade">A-</span><span class="range">85-89 points</span><span class="description">Very good project health</span></div>
                    <div class="grade-item grade-b-plus"><span class="grade">B+</span><span class="range">80-84 points</span><span class="description">Good project health</span></div>
                    <div class="grade-item grade-b"><span class="grade">B</span><span class="range">75-79 points</span><span class="description">Satisfactory project health</span></div>
                    <div class="grade-item grade-b-minus"><span class="grade">B-</span><span class="range">70-74 points</span><span class="description">Adequate project health</span></div>
                    <div class="grade-item grade-c-plus"><span class="grade">C+</span><span class="range">65-69 points</span><span class="description">Needs attention</span></div>
                    <div class="grade-item grade-c"><span class="grade">C</span><span class="range">60-64 points</span><span class="description">Requires improvement</span></div>
                    <div class="grade-item grade-c-minus"><span class="grade">C-</span><span class="range">55-59 points</span><span class="description">Poor project health</span></div>
                    <div class="grade-item grade-d"><span class="grade">D</span><span class="range">0-54 points</span><span class="description">Critical issues require immediate action</span></div>
                </div>
            </div>
            
            <div id="example" class="tab-content">
                <h4>Calculation Example</h4>
                <div class="calculation-example">
                    <div class="example-project">
                        <h5>Sample Project: "AI Assistant API"</h5>
                        <div class="calculation-steps">
                            <div class="step">
                                <strong>Activity Score (40%)</strong>
                                <p>• 25 commits in 30 days: +35 points</p>
                                <p>• 2 days since last commit: +5 points</p>
                                <p>• 4 contributors: +0 points</p>
                                <p><strong>Subtotal: 40/40 points</strong></p>
                            </div>
                            <div class="step">
                                <strong>Maintenance Score (30%)</strong>
                                <p>• 8 open issues: +25 points</p>
                                <p>• Good resolution rate: +5 points</p>
                                <p><strong>Subtotal: 30/30 points</strong></p>
                            </div>
                            <div class="step">
                                <strong>Collaboration Score (20%)</strong>
                                <p>• 5 MRs this period: +15 points</p>
                                <p>• Active code reviews: +5 points</p>
                                <p><strong>Subtotal: 20/20 points</strong></p>
                            </div>
                            <div class="step">
                                <strong>Quality Score (10%)</strong>
                                <p>• No pipeline data: +5 points</p>
                                <p><strong>Subtotal: 5/10 points</strong></p>
                            </div>
                            <div class="final-score">
                                <strong>Final Score: 95/100 = A+</strong>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """

def generate_enhanced_project_cards(projects: List[Dict]) -> str:
    """Generate enhanced project cards with branch and issue information."""
    cards = []
    
    for project in projects:
        status_class = f"badge-{project['status']}"
        grade_class = f"badge-grade-{project['health_grade'].lower().replace('+', '-plus').replace('-', '-minus')}"
        
        description = project.get('description', '')
        if not description:
            description = f"A {project['visibility']} GitLab project with {project['commits_30d']} commits in the last 30 days."
        
        # Branch information
        branch_info = ""
        branch_analysis = project.get('branch_analysis', {})
        if branch_analysis and not branch_analysis.get('error'):
            active_branches = branch_analysis.get('active_branches', [])[:3]  # Top 3 branches
            branch_pills = []
            for branch in active_branches:
                activity_class = f"branch-{branch.get('activity_level', 'minimal')}"
                branch_pills.append(f'<span class="branch-pill {activity_class}">{branch["name"]}</span>')
            
            if branch_pills:
                branch_info = f'<div class="branch-section"><span class="branch-label">Active Branches:</span> {" ".join(branch_pills)}</div>'
        
        # Issue recommendations
        issue_info = ""
        issue_analysis = project.get('issue_analysis', {})
        if issue_analysis and not issue_analysis.get('error'):
            recommendations = issue_analysis.get('recommendations', [])
            if recommendations:
                high_priority_recs = [r for r in recommendations if r.get('priority') in ['critical', 'high']]
                if high_priority_recs:
                    rec_count = len(high_priority_recs)
                    issue_info = f'<div class="issue-alert">⚠️ {rec_count} high priority recommendation{"s" if rec_count > 1 else ""}</div>'
        
        cards.append(f"""
        <div class="card project-card enhanced-project-card" data-status="{project['status']}" data-name="{project['name'].lower()}">
            <div class="project-header">
                <h3 class="project-name">{project['name']}</h3>
                <div class="project-badges">
                    <span class="badge {status_class}">{project['status'].title()}</span>
                    <span class="badge badge-grade {grade_class}">{project['health_grade']}</span>
                </div>
            </div>
            <p class="project-description">{description}</p>
            
            {branch_info}
            {issue_info}
            
            <div class="project-stats">
                <div class="stat">
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>{project['commits_30d']} commits</span>
                </div>
                <div class="stat">
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
                    </svg>
                    <span>{project['mrs_created']} MRs</span>
                </div>
                <div class="stat">
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                    <span>{project['contributors_30d']} contributors</span>
                </div>
                <div class="stat">
                    <svg class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span>{project.get('open_issues', 0)} issues</span>
                </div>
            </div>
            <div class="project-activity">
                {project['activity_sparkline']}
            </div>
        </div>
        """)
    
    return '\n'.join(cards)

def generate_shadcn_styles() -> str:
    """Generate shadcn/ui-inspired CSS styles."""
    return """
        /* CSS Variables */
        :root {
            --background: 0 0% 100%;
            --foreground: 222.2 84% 4.9%;
            --card: 0 0% 100%;
            --card-foreground: 222.2 84% 4.9%;
            --popover: 0 0% 100%;
            --popover-foreground: 222.2 84% 4.9%;
            --primary: 222.2 47.4% 11.2%;
            --primary-foreground: 210 40% 98%;
            --secondary: 210 40% 96.1%;
            --secondary-foreground: 222.2 47.4% 11.2%;
            --muted: 210 40% 96.1%;
            --muted-foreground: 215.4 16.3% 46.9%;
            --accent: 210 40% 96.1%;
            --accent-foreground: 222.2 47.4% 11.2%;
            --destructive: 0 84.2% 60.2%;
            --destructive-foreground: 210 40% 98%;
            --border: 214.3 31.8% 91.4%;
            --input: 214.3 31.8% 91.4%;
            --ring: 222.2 84% 4.9%;
            --radius: 0.5rem;
        }

        /* Reset and Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            line-height: 1.5;
            color: hsl(var(--foreground));
            background-color: hsl(var(--background));
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 1rem;
        }

        /* Header */
        .header {
            border-bottom: 1px solid hsl(var(--border));
            background-color: hsl(var(--background));
            position: sticky;
            top: 0;
            z-index: 50;
            backdrop-filter: blur(8px);
            background-color: hsla(var(--background), 0.8);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 0;
        }

        .header-title {
            font-size: 1.875rem;
            font-weight: 700;
            color: hsl(var(--foreground));
        }

        .header-subtitle {
            color: hsl(var(--muted-foreground));
            margin-top: 0.25rem;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .date-range {
            color: hsl(var(--muted-foreground));
            font-size: 0.875rem;
        }

        /* Main Content */
        .main-content {
            padding: 2rem 0 4rem;
        }

        .section {
            margin-bottom: 3rem;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: hsl(var(--foreground));
        }

        /* Cards */
        .card {
            background-color: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 1.5rem;
            box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
            transition: all 0.2s ease;
        }

        .card:hover {
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            transform: translateY(-1px);
        }

        /* KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .kpi-card {
            background-color: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
        }

        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5rem;
        }

        .kpi-label {
            color: hsl(var(--muted-foreground));
            font-size: 0.875rem;
            font-weight: 500;
        }

        .kpi-icon {
            width: 1.25rem;
            height: 1.25rem;
            color: hsl(var(--muted-foreground));
        }

        .kpi-value {
            font-size: 2.25rem;
            font-weight: 700;
            color: hsl(var(--foreground));
            line-height: 1;
            margin-bottom: 0.5rem;
        }

        .kpi-change {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.875rem;
        }

        .kpi-change.positive {
            color: #10b981;
        }

        .kpi-change.negative {
            color: #ef4444;
        }

        .kpi-change.neutral {
            color: hsl(var(--muted-foreground));
        }

        /* Activity Chart */
        .chart-card {
            margin-top: 1.5rem;
        }

        .chart-title {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .chart-container {
            height: 200px;
            position: relative;
            overflow: hidden;
        }

        /* Group Cards */
        .group-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }

        .group-card {
            cursor: pointer;
        }

        .group-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .group-name {
            font-size: 1.125rem;
            font-weight: 600;
        }

        .group-stats {
            display: flex;
            gap: 1.5rem;
            margin-top: 0.75rem;
        }

        .group-stat {
            display: flex;
            flex-direction: column;
        }

        .stat-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: hsl(var(--foreground));
        }

        .stat-label {
            font-size: 0.75rem;
            color: hsl(var(--muted-foreground));
        }

        /* Project Cards */
        .project-filters {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .search-input, .filter-select {
            padding: 0.5rem 0.75rem;
            border: 1px solid hsl(var(--border));
            border-radius: calc(var(--radius) - 2px);
            background-color: hsl(var(--background));
            font-size: 0.875rem;
            transition: all 0.2s;
        }

        .search-input:focus, .filter-select:focus {
            outline: none;
            border-color: hsl(var(--ring));
            box-shadow: 0 0 0 3px hsla(var(--ring), 0.1);
        }

        .search-input {
            flex: 1;
            max-width: 400px;
        }

        .project-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1rem;
        }

        .project-card {
            position: relative;
        }

        .project-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.75rem;
        }

        .project-name {
            font-size: 1rem;
            font-weight: 600;
            color: hsl(var(--foreground));
            margin: 0;
        }

        .project-badges {
            display: flex;
            gap: 0.5rem;
        }

        .badge {
            padding: 0.125rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }

        .badge-active {
            background-color: #10b981;
            color: white;
        }

        .badge-maintenance {
            background-color: #f59e0b;
            color: white;
        }

        .badge-inactive {
            background-color: #6b7280;
            color: white;
        }

        .badge-grade {
            background-color: hsl(var(--secondary));
            color: hsl(var(--secondary-foreground));
            font-weight: 700;
        }

        .badge-grade-a-plus { color: #10b981; }
        .badge-grade-a { color: #22c55e; }
        .badge-grade-b { color: #3b82f6; }
        .badge-grade-c { color: #f59e0b; }
        .badge-grade-d { color: #ef4444; }

        .project-description {
            color: hsl(var(--muted-foreground));
            font-size: 0.875rem;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .project-stats {
            display: flex;
            gap: 1rem;
            margin-bottom: 0.75rem;
            font-size: 0.875rem;
        }

        .stat {
            display: flex;
            align-items: center;
            gap: 0.25rem;
            color: hsl(var(--muted-foreground));
        }

        .stat .icon {
            width: 1rem;
            height: 1rem;
        }

        .project-activity {
            font-family: monospace;
            font-size: 1.25rem;
            color: hsl(var(--muted-foreground));
            letter-spacing: -0.05em;
        }

        /* Contributor Cards */
        .contributor-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
        }

        .contributor-card {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .contributor-avatar {
            width: 3rem;
            height: 3rem;
            border-radius: 9999px;
            background-color: hsl(var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            color: hsl(var(--secondary-foreground));
            flex-shrink: 0;
        }

        .contributor-info {
            flex: 1;
            min-width: 0;
        }

        .contributor-name {
            font-weight: 600;
            color: hsl(var(--foreground));
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .contributor-stats {
            color: hsl(var(--muted-foreground));
            font-size: 0.875rem;
        }

        /* Technology Stack */
        .tech-stack-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .tech-badge {
            padding: 0.375rem 0.75rem;
            background-color: hsl(var(--secondary));
            color: hsl(var(--secondary-foreground));
            border-radius: calc(var(--radius) - 2px);
            font-size: 0.875rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .tech-count {
            background-color: hsla(var(--foreground), 0.1);
            padding: 0.125rem 0.375rem;
            border-radius: 9999px;
            font-size: 0.75rem;
        }

        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: calc(var(--radius) - 2px);
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s;
            cursor: pointer;
            border: none;
            outline: none;
        }

        .btn-outline {
            background-color: transparent;
            border: 1px solid hsl(var(--border));
            color: hsl(var(--foreground));
        }

        .btn-outline:hover {
            background-color: hsl(var(--accent));
            color: hsl(var(--accent-foreground));
        }

        .btn .icon {
            width: 1rem;
            height: 1rem;
        }

        /* Footer */
        .footer {
            border-top: 1px solid hsl(var(--border));
            padding: 2rem 0;
            text-align: center;
            color: hsl(var(--muted-foreground));
            font-size: 0.875rem;
        }

        /* Utilities */
        .icon {
            width: 1.25rem;
            height: 1.25rem;
            flex-shrink: 0;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }

            .kpi-grid {
                grid-template-columns: 1fr;
            }

            .group-grid {
                grid-template-columns: 1fr;
            }

            .project-grid {
                grid-template-columns: 1fr;
            }

            .contributor-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Animations */
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }

        .loading {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }

        /* Issues Analysis Styles */
        .issues-analysis-container {
            margin-bottom: 2rem;
        }

        .issues-overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .issue-card {
            background: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 1.5rem;
            text-align: center;
        }

        .issue-card h3 {
            font-size: 0.875rem;
            font-weight: 500;
            color: hsl(var(--muted-foreground));
            margin-bottom: 0.5rem;
        }

        .issue-card .count {
            font-size: 2rem;
            font-weight: 700;
            color: hsl(var(--foreground));
            display: block;
            margin-bottom: 0.25rem;
        }

        .issue-card .card-subtitle {
            font-size: 0.75rem;
            color: hsl(var(--muted-foreground));
        }

        .recommendations-panel {
            background: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 1.5rem;
        }

        .recommendation-card {
            border: 1px solid hsl(var(--border));
            border-radius: calc(var(--radius) - 2px);
            padding: 1rem;
            margin-bottom: 1rem;
            background: hsl(var(--background));
        }

        .recommendation-card:last-child {
            margin-bottom: 0;
        }

        .recommendation-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }

        .recommendation-icon {
            font-size: 1.25rem;
        }

        .recommendation-title {
            font-size: 1rem;
            font-weight: 600;
            flex: 1;
        }

        .recommendation-priority {
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.5rem;
            border-radius: calc(var(--radius) - 4px);
            text-transform: uppercase;
        }

        .recommendation-critical .recommendation-priority {
            background: hsl(var(--destructive));
            color: hsl(var(--destructive-foreground));
        }

        .recommendation-high .recommendation-priority {
            background: hsl(0 85% 60%);
            color: white;
        }

        .recommendation-medium .recommendation-priority {
            background: hsl(38 95% 60%);
            color: white;
        }

        .recommendation-low .recommendation-priority {
            background: hsl(200 85% 60%);
            color: white;
        }

        .recommendation-info .recommendation-priority {
            background: hsl(var(--muted));
            color: hsl(var(--muted-foreground));
        }

        .recommendation-success .recommendation-priority {
            background: hsl(120 85% 40%);
            color: white;
        }

        .recommendation-message,
        .recommendation-action,
        .recommendation-project {
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
        }

        .recommendation-project {
            margin-bottom: 0;
            color: hsl(var(--muted-foreground));
        }

        /* Health Methodology Styles */
        .health-methodology-container {
            background: hsl(var(--card));
            border: 1px solid hsl(var(--border));
            border-radius: var(--radius);
            padding: 1.5rem;
        }

        .methodology-tabs {
            width: 100%;
        }

        .tab-nav {
            display: flex;
            border-bottom: 1px solid hsl(var(--border));
            margin-bottom: 1.5rem;
        }

        .tab-button {
            background: none;
            border: none;
            padding: 0.75rem 1rem;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            color: hsl(var(--muted-foreground));
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }

        .tab-button.active {
            color: hsl(var(--foreground));
            border-bottom-color: hsl(var(--primary));
        }

        .tab-button:hover {
            color: hsl(var(--foreground));
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .component-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        .component-card {
            background: hsl(var(--background));
            border: 1px solid hsl(var(--border));
            border-radius: calc(var(--radius) - 2px);
            padding: 1rem;
        }

        .component-card h5 {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: hsl(var(--foreground));
        }

        .component-card ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .component-card li {
            font-size: 0.875rem;
            color: hsl(var(--muted-foreground));
            margin-bottom: 0.5rem;
            padding-left: 1rem;
            position: relative;
        }

        .component-card li:before {
            content: "•";
            color: hsl(var(--primary));
            position: absolute;
            left: 0;
        }

        /* Enhanced Project Card Styles */
        .enhanced-project-card {
            position: relative;
        }

        .branch-section {
            margin: 0.75rem 0;
            padding: 0.5rem;
            background: hsl(var(--muted) / 0.5);
            border-radius: calc(var(--radius) - 4px);
        }

        .branch-label {
            font-size: 0.75rem;
            font-weight: 500;
            color: hsl(var(--muted-foreground));
            margin-right: 0.5rem;
        }

        .branch-pill {
            display: inline-block;
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: calc(var(--radius) - 4px);
            margin-right: 0.25rem;
            background: hsl(var(--secondary));
            color: hsl(var(--secondary-foreground));
        }

        .branch-pill.branch-high {
            background: hsl(120 85% 40%);
            color: white;
        }

        .branch-pill.branch-medium {
            background: hsl(38 95% 60%);
            color: white;
        }

        .branch-pill.branch-low {
            background: hsl(200 85% 60%);
            color: white;
        }

        .branch-pill.branch-minimal {
            background: hsl(var(--muted));
            color: hsl(var(--muted-foreground));
        }

        .issue-alert {
            background: hsl(0 85% 95%);
            border: 1px solid hsl(0 85% 80%);
            color: hsl(0 85% 40%);
            padding: 0.5rem;
            border-radius: calc(var(--radius) - 4px);
            font-size: 0.75rem;
            font-weight: 500;
            margin: 0.5rem 0;
        }
    """

def generate_kpi_card(label: str, value: int, change: float, type: str, show_change: bool = True) -> str:
    """Generate KPI card HTML."""
    change_class = 'positive' if change > 0 else 'negative' if change < 0 else 'neutral'
    change_icon = '↑' if change > 0 else '↓' if change < 0 else '→'
    
    icon_svgs = {
        'commits': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>',
        'mrs': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>',
        'issues': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>',
        'projects': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>'
    }
    
    return f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span class="kpi-label">{label}</span>
            <svg class="kpi-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                {icon_svgs.get(type, icon_svgs['commits'])}
            </svg>
        </div>
        <div class="kpi-value">{value:,}</div>
        {f'<div class="kpi-change {change_class}"><span>{change_icon}</span><span>{abs(change):.1f}% from last period</span></div>' if show_change else ''}
    </div>
    """

def generate_activity_chart(dates: List[str], values: List[int]) -> str:
    """Generate activity chart visualization."""
    max_value = max(values) if values else 1
    chart_height = 180
    
    bars = []
    bar_width = 100 / len(dates)
    
    for i, (date, value) in enumerate(zip(dates, values)):
        height = (value / max_value) * chart_height if max_value > 0 else 0
        bars.append(f"""
            <div style="position: absolute; bottom: 20px; left: {i * bar_width}%; width: {bar_width - 0.5}%; height: {height}px; background: linear-gradient(to top, #3b82f6, #60a5fa); opacity: 0.8; border-radius: 2px 2px 0 0;">
                <div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: 10px; color: #6b7280; white-space: nowrap;">{value}</div>
            </div>
        """)
    
    # Add date labels for every 5th date
    labels = []
    for i, date in enumerate(dates):
        if i % 5 == 0:
            labels.append(f'<div style="position: absolute; bottom: 0; left: {i * bar_width}%; font-size: 11px; color: #6b7280;">{date}</div>')
    
    return f"""
        <div style="position: relative; height: 100%;">
            {''.join(bars)}
            {''.join(labels)}
        </div>
    """

def generate_group_cards(groups: Dict) -> str:
    """Generate group analysis cards."""
    cards = []
    
    for group_id, group_data in groups.items():
        health_colors = {
            'A+': '#10b981', 'A': '#22c55e', 'A-': '#34d399',
            'B+': '#3b82f6', 'B': '#60a5fa', 'B-': '#93bbfc',
            'C+': '#f59e0b', 'C': '#fbbf24', 'C-': '#fcd34d',
            'D': '#ef4444'
        }
        
        health_color = health_colors.get(group_data['health_grade'], '#6b7280')
        
        cards.append(f"""
        <div class="card group-card">
            <div class="group-header">
                <h3 class="group-name">{group_data['name']}</h3>
                <span class="badge badge-grade" style="color: {health_color};">
                    Health: {group_data['health_grade']}
                </span>
            </div>
            <div class="group-stats">
                <div class="group-stat">
                    <span class="stat-value">{len(group_data['projects'])}</span>
                    <span class="stat-label">Projects</span>
                </div>
                <div class="group-stat">
                    <span class="stat-value">{group_data['total_commits']}</span>
                    <span class="stat-label">Commits</span>
                </div>
                <div class="group-stat">
                    <span class="stat-value">{group_data['active_projects']}</span>
                    <span class="stat-label">Active</span>
                </div>
            </div>
        </div>
        """)
    
    return '\n'.join(cards)

def generate_contributor_cards(contributors: List[Tuple[str, int]]) -> str:
    """Generate contributor performance cards."""
    cards = []
    
    for name, commits in contributors:
        initials = ''.join(word[0].upper() for word in name.split()[:2])
        
        cards.append(f"""
        <div class="card contributor-card">
            <div class="contributor-avatar">{initials}</div>
            <div class="contributor-info">
                <div class="contributor-name">{name}</div>
                <div class="contributor-stats">{commits} commits</div>
            </div>
        </div>
        """)
    
    return '\n'.join(cards)

def generate_tech_stack_badges(tech_stack: List[Tuple[str, int]]) -> str:
    """Generate technology stack badges."""
    badges = []
    
    for tech, count in tech_stack:
        badges.append(f"""
        <div class="tech-badge">
            <span>{tech}</span>
            <span class="tech-count">{count}</span>
        </div>
        """)
    
    return '\n'.join(badges)

def generate_dashboard_scripts() -> str:
    """Generate JavaScript for dashboard interactivity."""
    return """
    function filterProjects(searchTerm) {
        const projects = document.querySelectorAll('.project-card');
        const term = searchTerm.toLowerCase();
        
        projects.forEach(project => {
            const name = project.getAttribute('data-name');
            if (name.includes(term)) {
                project.style.display = '';
            } else {
                project.style.display = 'none';
            }
        });
    }
    
    function filterByStatus(status) {
        const projects = document.querySelectorAll('.project-card');
        
        projects.forEach(project => {
            if (status === '' || project.getAttribute('data-status') === status) {
                project.style.display = '';
            } else {
                project.style.display = 'none';
            }
        });
    }
    """

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate executive dashboard for GitLab analytics",
        epilog="""
Examples:
  # Generate dashboard for specific groups
  python scripts/generate_executive_dashboard.py --groups 1721,1267,1269 --output dashboard.html

  # Generate 60-day analysis
  python scripts/generate_executive_dashboard.py --groups 1721,1267,1269 --days 60 --output dashboard.html

  # Custom team name
  python scripts/generate_executive_dashboard.py --groups 1721,1267,1269 --team-name "AI Development Team"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--groups', '-g',
        required=True,
        help='Comma-separated list of GitLab group IDs to analyze'
    )
    parser.add_argument(
        '--output', '-o',
        default='executive_dashboard.html',
        help='Output file path (default: executive_dashboard.html)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to analyze (default: 30)'
    )
    parser.add_argument(
        '--team-name',
        default='Development Team',
        help='Name of the team for the report'
    )
    
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
        print(f"🚀 Starting executive dashboard generation...")
        print(f"   Analyzing {len(group_ids)} groups over {args.days} days")
        
        # Analyze groups
        report_data = analyze_groups(group_ids, gitlab_url, gitlab_token, args.days)
        
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
        print(f"   Unique Contributors: {summary['unique_contributors']}")
        print(f"   Health Distribution: A+({summary['health_distribution']['A+']}) A({summary['health_distribution']['A']}) B({summary['health_distribution']['B']}) C({summary['health_distribution']['C']}) D({summary['health_distribution']['D']})")
        
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