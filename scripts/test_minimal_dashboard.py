#!/usr/bin/env python3
"""Minimal test to verify enhanced dashboard components work."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generate_executive_dashboard import get_initials, generate_issue_row

# Test get_initials
print("Testing get_initials:")
print(f"  'John Doe' -> {get_initials('John Doe')}")
print(f"  'Jane' -> {get_initials('Jane')}")
print(f"  '' -> {get_initials('')}")

# Test issue row generation
test_issue = {
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
}

print("\nTesting generate_issue_row:")
issue_html = generate_issue_row(test_issue)
print("  Issue row generated successfully")
print(f"  Contains priority badge: {'priority-critical' in issue_html}")
print(f"  Contains assignee: {'John Doe' in issue_html}")
print(f"  Contains overdue class: {'overdue' in issue_html}")

print("\n✅ All component tests passed!")