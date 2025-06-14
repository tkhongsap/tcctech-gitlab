"""Tests for generate_executive_dashboard script."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestExecutiveDashboard:
    """Test executive dashboard generation."""
    
    @patch('scripts.generate_executive_dashboard.GitLabClient')
    def test_analyze_groups(self, mock_client_class):
        """Test analyzing GitLab groups."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock group data
        mock_groups = [
            {'id': 1, 'name': 'Group 1', 'full_path': 'group1'},
            {'id': 2, 'name': 'Group 2', 'full_path': 'group2'}
        ]
        mock_client.get_groups.return_value = mock_groups
        
        # Mock projects for each group
        mock_projects_g1 = [
            {
                'id': 101,
                'name': 'Project 1',
                'description': 'Test project 1',
                'created_at': '2024-01-01T00:00:00Z',
                'last_activity_at': '2024-01-15T00:00:00Z',
                'star_count': 5,
                'forks_count': 2,
                'open_issues_count': 10
            }
        ]
        mock_projects_g2 = [
            {
                'id': 102,
                'name': 'Project 2',
                'description': 'Test project 2',
                'created_at': '2024-01-02T00:00:00Z',
                'last_activity_at': '2024-01-16T00:00:00Z',
                'star_count': 3,
                'forks_count': 1,
                'open_issues_count': 5
            }
        ]
        
        def get_group_projects(group_id):
            if group_id == 1:
                return mock_projects_g1
            return mock_projects_g2
        
        mock_client.get_group_projects.side_effect = get_group_projects
        
        # Import after mocking
        from scripts.generate_executive_dashboard import analyze_groups
        
        # Test
        group_ids = [1, 2]
        result = analyze_groups(mock_client, group_ids, days=30)
        
        assert 'groups' in result
        assert len(result['groups']) == 2
        assert result['summary']['total_projects'] == 2
        assert result['summary']['total_issues'] == 15
        assert result['summary']['total_stars'] == 8
    
    @patch('scripts.generate_executive_dashboard.GitLabClient')
    def test_calculate_health_score(self, mock_client_class):
        """Test health score calculation."""
        from scripts.generate_executive_dashboard import calculate_health_score
        
        # Active project
        active_project = {
            'last_activity_at': datetime.now().isoformat(),
            'open_issues_count': 5,
            'has_readme': True,
            'has_ci': True,
            'commit_count': 100,
            'contributor_count': 5
        }
        
        score = calculate_health_score(active_project)
        assert score > 80  # Should be healthy
        
        # Inactive project
        inactive_project = {
            'last_activity_at': (datetime.now() - timedelta(days=100)).isoformat(),
            'open_issues_count': 50,
            'has_readme': False,
            'has_ci': False,
            'commit_count': 10,
            'contributor_count': 1
        }
        
        score = calculate_health_score(inactive_project)
        assert score < 50  # Should be unhealthy
    
    def test_get_health_grade(self):
        """Test health grade assignment."""
        from scripts.generate_executive_dashboard import get_health_grade
        
        assert get_health_grade(95) == 'A+'
        assert get_health_grade(85) == 'A'
        assert get_health_grade(75) == 'B'
        assert get_health_grade(65) == 'C'
        assert get_health_grade(55) == 'D'
        assert get_health_grade(45) == 'F'
    
    @patch('scripts.generate_executive_dashboard.GitLabClient')
    def test_collect_commit_activity(self, mock_client_class):
        """Test collecting commit activity."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock commits
        mock_commits = [
            {
                'id': 'abc123',
                'short_id': 'abc123',
                'created_at': datetime.now().isoformat(),
                'author_name': 'John Doe',
                'author_email': 'john@example.com',
                'message': 'Fix bug'
            },
            {
                'id': 'def456',
                'short_id': 'def456',
                'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'author_name': 'Jane Smith',
                'author_email': 'jane@example.com',
                'message': 'Add feature'
            }
        ]
        
        mock_client._paginated_get.return_value = iter(mock_commits)
        
        from scripts.generate_executive_dashboard import collect_commit_activity
        
        project = {'id': 123}
        activity = collect_commit_activity(mock_client, project, days=7)
        
        assert activity['total_commits'] == 2
        assert activity['unique_authors'] == 2
        assert len(activity['daily_commits']) > 0
        assert len(activity['author_stats']) == 2
    
    def test_generate_html_dashboard(self):
        """Test HTML dashboard generation."""
        from scripts.generate_executive_dashboard import generate_shadcn_dashboard
        
        analysis_data = {
            'groups': [
                {
                    'id': 1,
                    'name': 'Test Group',
                    'projects': [
                        {
                            'name': 'Test Project',
                            'health_score': 85,
                            'health_grade': 'A',
                            'last_activity_at': datetime.now().isoformat()
                        }
                    ],
                    'total_projects': 1,
                    'active_projects': 1
                }
            ],
            'summary': {
                'total_projects': 1,
                'active_projects': 1,
                'total_commits': 10,
                'unique_contributors': 2,
                'avg_health_score': 85
            },
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'analysis_period_days': 30,
                'gitlab_url': 'https://gitlab.example.com'
            }
        }
        
        html = generate_shadcn_dashboard(analysis_data)
        
        # Check key elements
        assert '<html' in html
        assert 'Test Group' in html
        assert 'Test Project' in html
        assert 'Health Score' in html
        assert 'Total Projects: 1' in html
    
    @patch('scripts.generate_executive_dashboard.GitLabClient')
    def test_collect_issue_analytics(self, mock_client_class):
        """Test issue analytics collection."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Mock issues
        mock_issues = [
            {
                'id': 1,
                'iid': 1,
                'title': 'Critical Bug',
                'labels': ['bug', 'critical'],
                'state': 'opened',
                'created_at': datetime.now().isoformat(),
                'assignee': {'name': 'John Doe'}
            },
            {
                'id': 2,
                'iid': 2,
                'title': 'New Feature',
                'labels': ['feature'],
                'state': 'opened',
                'created_at': (datetime.now() - timedelta(days=5)).isoformat(),
                'assignee': None
            }
        ]
        
        mock_client._paginated_get.return_value = iter(mock_issues)
        
        from scripts.generate_executive_dashboard import collect_issue_analytics
        
        projects = [{'id': 123, 'name': 'Test Project'}]
        analytics = collect_issue_analytics(mock_client, projects)
        
        assert analytics['total_open_issues'] == 2
        assert analytics['issues_by_priority']['critical'] == 1
        assert analytics['issues_by_type']['bug'] == 1
        assert analytics['issues_by_type']['feature'] == 1
        assert analytics['unassigned_issues'] == 1
    
    def test_generate_ai_recommendations(self):
        """Test AI recommendation generation."""
        from scripts.generate_executive_dashboard import generate_ai_recommendations
        
        issue_analytics = {
            'total_open_issues': 50,
            'issues_by_priority': {
                'critical': 10,
                'high': 15,
                'medium': 20,
                'low': 5
            },
            'unassigned_issues': 25,
            'overdue_issues': 8,
            'issues_by_type': {
                'bug': 30,
                'feature': 20
            }
        }
        
        recommendations = generate_ai_recommendations(issue_analytics)
        
        # Should generate recommendations based on the data
        assert len(recommendations) > 0
        
        # Should have high priority recommendations for critical issues
        critical_recs = [r for r in recommendations if r['priority'] == 'critical']
        assert len(critical_recs) > 0
        
        # Should recommend addressing unassigned issues
        unassigned_recs = [r for r in recommendations if 'unassigned' in r['message'].lower()]
        assert len(unassigned_recs) > 0


class TestDashboardFormatting:
    """Test dashboard formatting functions."""
    
    def test_format_number(self):
        """Test number formatting."""
        from scripts.generate_executive_dashboard import format_number
        
        assert format_number(1000) == "1,000"
        assert format_number(1000000) == "1,000,000"
        assert format_number(999) == "999"
    
    def test_format_date(self):
        """Test date formatting."""
        from scripts.generate_executive_dashboard import format_date
        
        date_str = "2024-01-15T10:30:00Z"
        formatted = format_date(date_str)
        assert "2024-01-15" in formatted
    
    def test_get_time_ago(self):
        """Test relative time calculation."""
        from scripts.generate_executive_dashboard import get_time_ago
        
        # Recent
        recent = datetime.now().isoformat()
        assert "just now" in get_time_ago(recent).lower() or "minute" in get_time_ago(recent).lower()
        
        # Days ago
        days_ago = (datetime.now() - timedelta(days=5)).isoformat()
        assert "5 days ago" in get_time_ago(days_ago)
        
        # Months ago
        months_ago = (datetime.now() - timedelta(days=65)).isoformat()
        assert "2 months ago" in get_time_ago(months_ago)


class TestDashboardCharts:
    """Test chart generation functions."""
    
    def test_generate_commit_chart_data(self):
        """Test commit chart data generation."""
        from scripts.generate_executive_dashboard import generate_commit_chart_data
        
        commit_data = {
            'daily_commits': {
                '2024-01-01': 5,
                '2024-01-02': 8,
                '2024-01-03': 3
            }
        }
        
        chart_data = generate_commit_chart_data(commit_data, days=7)
        
        assert 'labels' in chart_data
        assert 'datasets' in chart_data
        assert len(chart_data['datasets']) > 0
        assert chart_data['datasets'][0]['data'] == [5, 8, 3]
    
    def test_generate_issue_chart_data(self):
        """Test issue chart data generation."""
        from scripts.generate_executive_dashboard import generate_issue_chart_data
        
        issue_data = {
            'issues_by_type': {
                'bug': 10,
                'feature': 15,
                'enhancement': 5
            }
        }
        
        chart_data = generate_issue_chart_data(issue_data)
        
        assert 'labels' in chart_data
        assert 'datasets' in chart_data
        assert set(chart_data['labels']) == {'bug', 'feature', 'enhancement'}
        assert sum(chart_data['datasets'][0]['data']) == 30