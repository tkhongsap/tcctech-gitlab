#!/usr/bin/env python3
"""Test script to generate enhanced dashboard with simulated data."""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from collections import Counter
from generate_executive_dashboard import (
    generate_shadcn_dashboard,
    generate_enhanced_team_cards,
    generate_issue_row,
    generate_issues_management_section,
    get_initials
)

# Create test data
test_report_data = {
    'metadata': {
        'period_days': 30,
        'start_date': '2024-01-01',
        'end_date': '2024-01-31'
    },
    'summary': {
        'total_commits': 1234,
        'total_mrs': 156,
        'total_issues': 89,
        'active_projects': 24,
        'unique_contributors': 15,
        'total_projects': 24,
        'health_distribution': {'A+': 2, 'A': 5, 'B': 10, 'C': 5, 'D': 2}
    },
    'groups': {
        1721: {
            'id': 1721,
            'name': 'AI-ML-Services',
            'projects': 12,
            'commits': 456,
            'contributors': 8,
            'open_issues': 23,
            'open_mrs': 5,
            'avg_health_score': 85,
            'health_grade': 'A'
        },
        1267: {
            'id': 1267,
            'name': 'Research Repos',
            'projects': 8,
            'commits': 234,
            'contributors': 5,
            'open_issues': 15,
            'open_mrs': 3,
            'avg_health_score': 78,
            'health_grade': 'B+'
        }
    },
    'projects': [
        {
            'id': 1,
            'name': 'ai-assistant-api',
            'health_score': 92,
            'commits_30d': 45,
            'open_issues': 5,
            'open_mrs': 2,
            'contributors_30d': 3,
            'days_since_last_commit': 1,
            'branch_analysis': {'active_branches': ['main', 'develop', 'feature/auth'], 'total_branches': 5}
        }
    ],
    'contributors': Counter({
        'John Doe': 234,
        'Jane Smith': 189,
        'Bob Johnson': 156,
        'Alice Williams': 134,
        'Charlie Brown': 98
    }),
    'technology_stack': Counter({
        'Python': 45,
        'JavaScript': 32,
        'TypeScript': 28,
        'Go': 15,
        'Docker': 12
    }),
    'daily_activity': {
        '2024-01-01': 45,
        '2024-01-02': 52,
        '2024-01-03': 38
    },
    'issue_analytics': {
        'total_open': 89,
        'by_priority': {'critical': 5, 'high': 12, 'medium': 45, 'low': 27},
        'by_type': {'bug': 34, 'feature': 28, 'enhancement': 20, 'other': 7},
        'by_state': {'opened': 89, 'in_progress': 23, 'blocked': 5},
        'overdue': 8,
        'unassigned': 15,
        'project_issues': {'ai-assistant-api': 12, 'ml-pipeline': 8},
        'assignee_workload': {'John Doe': 15, 'Jane Smith': 12, 'Bob Johnson': 18}
    },
    'ai_recommendations': [
        {
            'type': 'critical',
            'title': 'Critical Issues Require Immediate Attention',
            'message': '5 critical issues are open across 3 projects',
            'action': 'Allocate senior developers to resolve critical issues immediately',
            'projects': ['ai-assistant-api', 'ml-pipeline', 'data-processor']
        },
        {
            'type': 'high',
            'title': 'Workload Imbalance Detected',
            'message': 'Bob Johnson has 18 issues (2x average)',
            'action': 'Redistribute issues to balance team workload',
            'team_member': 'Bob Johnson'
        },
        {
            'type': 'medium',
            'title': 'Stale Issues Need Review',
            'message': '15 issues haven\'t been updated in 30+ days',
            'action': 'Review and close or reprioritize stale issues'
        }
    ],
    'team_analytics': {
        'John Doe': {
            'commits': 234,
            'projects': {'ai-assistant-api', 'ml-pipeline', 'data-processor', 'auth-service', 'analytics-dashboard'},
            'issues_assigned': 15,
            'issues_resolved': 23,
            'merge_requests': 12,
            'recent_activity': []
        },
        'Jane Smith': {
            'commits': 189,
            'projects': {'frontend-app', 'design-system', 'component-library'},
            'issues_assigned': 12,
            'issues_resolved': 18,
            'merge_requests': 8,
            'recent_activity': []
        },
        'Bob Johnson': {
            'commits': 156,
            'projects': {'backend-api', 'database-migrations', 'cache-service', 'queue-processor'},
            'issues_assigned': 18,
            'issues_resolved': 14,
            'merge_requests': 6,
            'recent_activity': []
        }
    },
    'all_issues': [
        {
            'id': 1,
            'iid': 123,
            'title': 'Critical: API endpoint returns 500 error under high load',
            'project_name': 'ai-assistant-api',
            'priority': 'critical',
            'type': 'bug',
            'assignee': {'name': 'John Doe'},
            'labels': ['bug', 'critical', 'backend'],
            'due_date': '2024-01-15',
            'is_overdue': True,
            'age_days': 15,
            'web_url': 'https://gitlab.com/group/project/issues/123'
        },
        {
            'id': 2,
            'iid': 124,
            'title': 'Feature: Implement OAuth2 authentication',
            'project_name': 'auth-service',
            'priority': 'high',
            'type': 'feature',
            'assignee': {'name': 'Jane Smith'},
            'labels': ['feature', 'high', 'security'],
            'due_date': '2024-02-01',
            'is_overdue': False,
            'age_days': 8,
            'web_url': 'https://gitlab.com/group/project/issues/124'
        },
        {
            'id': 3,
            'iid': 125,
            'title': 'Enhancement: Add caching layer to improve performance',
            'project_name': 'backend-api',
            'priority': 'medium',
            'type': 'enhancement',
            'assignee': None,
            'labels': ['enhancement', 'performance'],
            'due_date': None,
            'is_overdue': False,
            'age_days': 5,
            'web_url': 'https://gitlab.com/group/project/issues/125'
        }
    ]
}

# Generate the dashboard
html_content = generate_shadcn_dashboard(test_report_data, 'TCC Tech Development Team')

# Save to file
with open('test_enhanced_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Test dashboard generated successfully: test_enhanced_dashboard.html")

# Test individual components
print("\n🧪 Testing individual components:")

# Test get_initials
print(f"get_initials('John Doe'): {get_initials('John Doe')}")
print(f"get_initials('Jane'): {get_initials('Jane')}")
print(f"get_initials(''): {get_initials('')}")

# Test issue row generation
print("\n📋 Sample issue row:")
test_issue = test_report_data['all_issues'][0]
issue_row = generate_issue_row(test_issue)
print("Issue row generated successfully (HTML content not shown for brevity)")

print("\n✅ All tests completed successfully!")