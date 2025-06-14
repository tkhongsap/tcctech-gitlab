"""Weekly productivity report generation service."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

from ..api import GitLabClient
from ..utils.logger import OperationLogger
from .analytics_advanced import AdvancedAnalytics

logger = logging.getLogger(__name__)


class WeeklyProductivityReporter:
    """Generate comprehensive weekly productivity reports for team syncs."""
    
    def __init__(self, client: GitLabClient):
        """Initialize weekly reporter.
        
        Args:
            client: GitLab API client
        """
        self.client = client
        self.analytics = AdvancedAnalytics(client)
        
    def generate_team_report(
        self,
        group_ids: List[int],
        team_members: Optional[List[str]] = None,
        weeks_back: int = 1
    ) -> Dict[str, Any]:
        """Generate comprehensive weekly team productivity report.
        
        Args:
            group_ids: List of GitLab group IDs to analyze
            team_members: List of usernames/emails to focus on (optional)
            weeks_back: Number of weeks to look back (default: 1)
            
        Returns:
            Comprehensive report data
        """
        with OperationLogger(logger, "weekly report generation"):
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks_back)
            
            logger.info(f"Generating report for {weeks_back} week(s) ending {end_date.date()}")
            
            report = {
                'metadata': {
                    'generated_at': end_date.isoformat(),
                    'period_start': start_date.isoformat(),
                    'period_end': end_date.isoformat(),
                    'weeks_analyzed': weeks_back,
                    'groups_analyzed': len(group_ids),
                    'team_size': len(team_members) if team_members else 'All contributors'
                },
                'executive_summary': {},
                'team_activity': {},
                'project_breakdown': {},
                'individual_metrics': {},
                'insights_and_actions': {}
            }
            
            # Collect all projects from groups
            all_projects = []
            for group_id in group_ids:
                projects = list(self.client.get_projects(
                    group_id=group_id,
                    include_subgroups=True,
                    archived=False
                ))
                all_projects.extend(projects)
            
            logger.info(f"Analyzing {len(all_projects)} projects across {len(group_ids)} groups")
            
            # Generate each section
            report['team_activity'] = self._generate_team_activity(
                all_projects, start_date, end_date, team_members
            )
            
            report['project_breakdown'] = self._generate_project_breakdown(
                all_projects, start_date, end_date
            )
            
            report['individual_metrics'] = self._generate_individual_metrics(
                all_projects, start_date, end_date, team_members
            )
            
            report['executive_summary'] = self._generate_executive_summary(
                report['team_activity'], 
                report['project_breakdown'],
                report['individual_metrics']
            )
            
            report['insights_and_actions'] = self._generate_insights_and_actions(
                report
            )
            
            return report
    
    def _generate_team_activity(
        self,
        projects: List[Dict],
        start_date: datetime,
        end_date: datetime,
        team_members: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate overall team activity metrics."""
        activity = {
            'commits': {'total': 0, 'by_day': defaultdict(int), 'by_author': defaultdict(int)},
            'merge_requests': {'total': 0, 'opened': 0, 'merged': 0, 'closed': 0},
            'issues': {'total': 0, 'opened': 0, 'closed': 0, 'in_progress': 0},
            'velocity_trends': {},
            'collaboration_metrics': {}
        }
        
        for project in projects:
            try:
                project_id = project['id']
                
                # Commits
                commits = list(self.client._paginated_get(
                    f'projects/{project_id}/repository/commits',
                    params={
                        'since': start_date.isoformat(),
                        'until': end_date.isoformat()
                    }
                ))
                
                for commit in commits:
                    author = commit.get('author_name', 'Unknown')
                    # Filter by team members if specified
                    if team_members and author not in team_members:
                        continue
                    
                    activity['commits']['total'] += 1
                    activity['commits']['by_author'][author] += 1
                    
                    # Group by day
                    commit_date = datetime.fromisoformat(
                        commit['created_at'].replace('Z', '+00:00')
                    ).date()
                    activity['commits']['by_day'][str(commit_date)] += 1
                
                # Merge Requests
                merge_requests = list(self.client._paginated_get(
                    f'projects/{project_id}/merge_requests',
                    params={
                        'created_after': start_date.isoformat(),
                        'created_before': end_date.isoformat(),
                        'scope': 'all'
                    }
                ))
                
                for mr in merge_requests:
                    author = mr.get('author', {}).get('username', 'Unknown')
                    if team_members and author not in team_members:
                        continue
                    
                    activity['merge_requests']['total'] += 1
                    if mr['state'] == 'opened':
                        activity['merge_requests']['opened'] += 1
                    elif mr['state'] == 'merged':
                        activity['merge_requests']['merged'] += 1
                    elif mr['state'] == 'closed':
                        activity['merge_requests']['closed'] += 1
                
                # Issues
                issues = list(self.client._paginated_get(
                    f'projects/{project_id}/issues',
                    params={
                        'created_after': start_date.isoformat(),
                        'created_before': end_date.isoformat(),
                        'scope': 'all'
                    }
                ))
                
                for issue in issues:
                    assignee = issue.get('assignee', {})
                    if assignee:
                        assignee_username = assignee.get('username', 'Unknown')
                        if team_members and assignee_username not in team_members:
                            continue
                    
                    activity['issues']['total'] += 1
                    if issue['state'] == 'opened':
                        activity['issues']['opened'] += 1
                    elif issue['state'] == 'closed':
                        activity['issues']['closed'] += 1
                
            except Exception as e:
                logger.warning(f"Failed to analyze project {project.get('name', project['id'])}: {e}")
        
        # Calculate velocity trends
        activity['velocity_trends'] = self._calculate_velocity_trends(activity)
        
        # Calculate collaboration metrics
        activity['collaboration_metrics'] = self._calculate_collaboration_metrics(activity)
        
        return activity
    
    def _generate_project_breakdown(
        self,
        projects: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate project-by-project breakdown with health indicators."""
        breakdown = {
            'projects': [],
            'health_summary': {'healthy': 0, 'warning': 0, 'critical': 0},
            'activity_distribution': {}
        }
        
        for project in projects:
            try:
                project_data = {
                    'id': project['id'],
                    'name': project['name'],
                    'path': project['path_with_namespace'],
                    'last_activity': project.get('last_activity_at'),
                    'default_branch': project.get('default_branch'),
                    'visibility': project.get('visibility'),
                    'metrics': {},
                    'health_status': 'unknown',
                    'health_score': 0,
                    'recommendations': []
                }
                
                # Get activity metrics for this project
                project_id = project['id']
                
                # Recent commits (past 7 days for activity check)
                recent_commits = list(self.client._paginated_get(
                    f'projects/{project_id}/repository/commits',
                    params={
                        'since': (datetime.now() - timedelta(days=7)).isoformat()
                    }
                ))
                
                # Issues in the analysis period
                issues = list(self.client._paginated_get(
                    f'projects/{project_id}/issues',
                    params={'scope': 'all'}
                ))
                
                # Open issues
                open_issues = [i for i in issues if i['state'] == 'opened']
                
                # Issues created in period
                period_issues = [
                    i for i in issues
                    if start_date <= datetime.fromisoformat(
                        i['created_at'].replace('Z', '+00:00')
                    ) <= end_date
                ]
                
                # Merge requests
                merge_requests = list(self.client._paginated_get(
                    f'projects/{project_id}/merge_requests',
                    params={'scope': 'all'}
                ))
                
                open_mrs = [mr for mr in merge_requests if mr['state'] == 'opened']
                
                project_data['metrics'] = {
                    'commits_this_week': len(recent_commits),
                    'open_issues': len(open_issues),
                    'issues_created_period': len(period_issues),
                    'open_merge_requests': len(open_mrs),
                    'last_commit_days_ago': self._days_since_last_commit(project_id)
                }
                
                # Calculate health status
                health_score = self._calculate_project_health(project_data['metrics'])
                project_data['health_score'] = health_score
                
                if health_score >= 80:
                    project_data['health_status'] = 'healthy'
                    breakdown['health_summary']['healthy'] += 1
                elif health_score >= 60:
                    project_data['health_status'] = 'warning'
                    breakdown['health_summary']['warning'] += 1
                else:
                    project_data['health_status'] = 'critical'
                    breakdown['health_summary']['critical'] += 1
                
                # Generate recommendations
                project_data['recommendations'] = self._generate_project_recommendations(
                    project_data['metrics']
                )
                
                breakdown['projects'].append(project_data)
                
            except Exception as e:
                logger.warning(f"Failed to analyze project {project.get('name', project['id'])}: {e}")
        
        # Sort projects by health score (worst first for attention)
        breakdown['projects'].sort(key=lambda x: x['health_score'])
        
        return breakdown
    
    def _generate_individual_metrics(
        self,
        projects: List[Dict],
        start_date: datetime,
        end_date: datetime,
        team_members: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate individual contributor metrics."""
        individuals = defaultdict(lambda: {
            'commits': 0,
            'lines_added': 0,
            'lines_removed': 0,
            'merge_requests_created': 0,
            'merge_requests_merged': 0,
            'issues_created': 0,
            'issues_resolved': 0,
            'code_reviews': 0,
            'active_projects': set(),
            'collaboration_score': 0
        })
        
        for project in projects:
            try:
                project_id = project['id']
                
                # Commits with stats
                commits = list(self.client._paginated_get(
                    f'projects/{project_id}/repository/commits',
                    params={
                        'since': start_date.isoformat(),
                        'until': end_date.isoformat(),
                        'with_stats': True
                    }
                ))
                
                for commit in commits:
                    author = commit.get('author_name', 'Unknown')
                    if team_members and author not in team_members:
                        continue
                    
                    individuals[author]['commits'] += 1
                    individuals[author]['active_projects'].add(project['name'])
                    
                    # Add line stats if available
                    stats = commit.get('stats', {})
                    individuals[author]['lines_added'] += stats.get('additions', 0)
                    individuals[author]['lines_removed'] += stats.get('deletions', 0)
                
                # Merge Requests
                merge_requests = list(self.client._paginated_get(
                    f'projects/{project_id}/merge_requests',
                    params={
                        'created_after': start_date.isoformat(),
                        'created_before': end_date.isoformat(),
                        'scope': 'all'
                    }
                ))
                
                for mr in merge_requests:
                    author = mr.get('author', {}).get('username', 'Unknown')
                    if team_members and author not in team_members:
                        continue
                    
                    individuals[author]['merge_requests_created'] += 1
                    if mr['state'] == 'merged':
                        individuals[author]['merge_requests_merged'] += 1
                
                # Issues
                issues = list(self.client._paginated_get(
                    f'projects/{project_id}/issues',
                    params={
                        'created_after': start_date.isoformat(),
                        'created_before': end_date.isoformat(),
                        'scope': 'all'
                    }
                ))
                
                for issue in issues:
                    # Issue creator
                    author = issue.get('author', {}).get('username', 'Unknown')
                    if not team_members or author in team_members:
                        individuals[author]['issues_created'] += 1
                    
                    # Issue assignee
                    assignee = issue.get('assignee')
                    if assignee:
                        assignee_username = assignee.get('username', 'Unknown')
                        if not team_members or assignee_username in team_members:
                            if issue['state'] == 'closed':
                                individuals[assignee_username]['issues_resolved'] += 1
                
            except Exception as e:
                logger.warning(f"Failed to analyze individual metrics for project {project.get('name')}: {e}")
        
        # Convert to regular dict and calculate derived metrics
        result = {}
        for username, metrics in individuals.items():
            metrics['active_projects'] = list(metrics['active_projects'])
            metrics['project_count'] = len(metrics['active_projects'])
            
            # Calculate collaboration score
            metrics['collaboration_score'] = self._calculate_individual_collaboration_score(metrics)
            
            # Calculate overall productivity score
            metrics['productivity_score'] = self._calculate_productivity_score(metrics)
            
            result[username] = metrics
        
        return {
            'contributors': result,
            'team_stats': self._calculate_team_distribution_stats(result)
        }
    
    def _generate_executive_summary(
        self,
        team_activity: Dict,
        project_breakdown: Dict,
        individual_metrics: Dict
    ) -> Dict[str, Any]:
        """Generate executive summary with key insights."""
        summary = {
            'key_metrics': {},
            'trends': {},
            'highlights': [],
            'concerns': []
        }
        
        # Key metrics
        summary['key_metrics'] = {
            'total_commits': team_activity['commits']['total'],
            'total_merge_requests': team_activity['merge_requests']['total'],
            'merge_rate': (
                team_activity['merge_requests']['merged'] / 
                max(team_activity['merge_requests']['total'], 1) * 100
            ),
            'total_issues': team_activity['issues']['total'],
            'active_contributors': len(individual_metrics['contributors']),
            'healthy_projects': project_breakdown['health_summary']['healthy'],
            'projects_needing_attention': (
                project_breakdown['health_summary']['warning'] + 
                project_breakdown['health_summary']['critical']
            ),
            'average_commits_per_contributor': (
                team_activity['commits']['total'] / 
                max(len(individual_metrics['contributors']), 1)
            )
        }
        
        # Highlights
        if summary['key_metrics']['merge_rate'] > 80:
            summary['highlights'].append("🎯 Excellent merge request acceptance rate")
        
        if summary['key_metrics']['healthy_projects'] > project_breakdown['health_summary']['critical']:
            summary['highlights'].append("💚 More healthy projects than critical ones")
        
        top_contributor = max(
            individual_metrics['contributors'].items(),
            key=lambda x: x[1]['commits'],
            default=(None, {'commits': 0})
        )
        if top_contributor[0]:
            summary['highlights'].append(
                f"⭐ Top contributor: {top_contributor[0]} with {top_contributor[1]['commits']} commits"
            )
        
        # Concerns
        if project_breakdown['health_summary']['critical'] > 0:
            summary['concerns'].append(
                f"🚨 {project_breakdown['health_summary']['critical']} projects in critical health"
            )
        
        if summary['key_metrics']['merge_rate'] < 50:
            summary['concerns'].append("⚠️ Low merge request acceptance rate")
        
        if team_activity['commits']['total'] < 10:
            summary['concerns'].append("📉 Very low commit activity this week")
        
        return summary
    
    def _generate_insights_and_actions(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights and recommended actions."""
        insights = {
            'recommended_actions': [],
            'team_focus_areas': [],
            'individual_coaching': [],
            'process_improvements': []
        }
        
        # Analyze patterns and generate recommendations
        project_breakdown = report['project_breakdown']
        individual_metrics = report['individual_metrics']
        team_activity = report['team_activity']
        
        # Project-based recommendations
        critical_projects = [
            p for p in project_breakdown['projects'] 
            if p['health_status'] == 'critical'
        ]
        
        if critical_projects:
            insights['recommended_actions'].append({
                'priority': 'high',
                'action': f"Address {len(critical_projects)} critical health projects",
                'projects': [p['name'] for p in critical_projects[:3]],
                'rationale': "These projects may be blocking team progress"
            })
        
        # Individual coaching opportunities
        contributors = individual_metrics['contributors']
        if contributors:
            # Find contributors with low collaboration
            low_collaboration = [
                name for name, metrics in contributors.items()
                if metrics['collaboration_score'] < 50
            ]
            
            if low_collaboration:
                insights['individual_coaching'].append({
                    'focus': 'collaboration',
                    'individuals': low_collaboration[:3],
                    'suggestion': 'Encourage more code reviews and cross-project work'
                })
        
        # Process improvements
        if team_activity['merge_requests']['total'] > 0:
            merge_rate = (
                team_activity['merge_requests']['merged'] / 
                team_activity['merge_requests']['total']
            )
            if merge_rate < 0.7:
                insights['process_improvements'].append({
                    'area': 'code_review',
                    'issue': f"Only {merge_rate*100:.1f}% of MRs are being merged",
                    'suggestion': 'Review MR approval process and requirements'
                })
        
        return insights
    
    def _calculate_velocity_trends(self, activity: Dict) -> Dict:
        """Calculate velocity trends from activity data."""
        # Simple trend calculation based on daily commits
        daily_commits = list(activity['commits']['by_day'].values())
        if len(daily_commits) < 2:
            return {'trend': 'insufficient_data', 'direction': 'neutral'}
        
        # Calculate simple trend
        recent_avg = statistics.mean(daily_commits[-3:]) if len(daily_commits) >= 3 else daily_commits[-1]
        early_avg = statistics.mean(daily_commits[:3]) if len(daily_commits) >= 3 else daily_commits[0]
        
        if recent_avg > early_avg * 1.2:
            direction = 'increasing'
        elif recent_avg < early_avg * 0.8:
            direction = 'decreasing'
        else:
            direction = 'stable'
        
        return {
            'trend': 'calculated',
            'direction': direction,
            'recent_average': recent_avg,
            'early_average': early_avg
        }
    
    def _calculate_collaboration_metrics(self, activity: Dict) -> Dict:
        """Calculate team collaboration metrics."""
        total_authors = len(activity['commits']['by_author'])
        if total_authors == 0:
            return {'collaboration_score': 0, 'distribution': 'no_activity'}
        
        # Calculate contribution distribution
        commit_counts = list(activity['commits']['by_author'].values())
        
        if len(commit_counts) == 1:
            distribution = 'single_contributor'
        else:
            # Gini coefficient for distribution equality
            sorted_counts = sorted(commit_counts)
            n = len(sorted_counts)
            cumsum = [sum(sorted_counts[:i+1]) for i in range(n)]
            gini = (n + 1 - 2 * sum((n + 1 - i) * count for i, count in enumerate(sorted_counts))) / (n * sum(sorted_counts))
            
            if gini < 0.3:
                distribution = 'well_distributed'
            elif gini < 0.6:
                distribution = 'moderately_distributed'
            else:
                distribution = 'concentrated'
        
        collaboration_score = max(0, 100 - (len(commit_counts) * 10))  # Simple scoring
        
        return {
            'collaboration_score': collaboration_score,
            'distribution': distribution,
            'active_contributors': total_authors,
            'gini_coefficient': gini if 'gini' in locals() else 0
        }
    
    def _calculate_project_health(self, metrics: Dict) -> float:
        """Calculate project health score based on activity metrics."""
        score = 100
        
        # Penalize based on various factors
        if metrics['commits_this_week'] == 0:
            score -= 30
        elif metrics['commits_this_week'] < 3:
            score -= 15
        
        if metrics['open_issues'] > 20:
            score -= 20
        elif metrics['open_issues'] > 10:
            score -= 10
        
        if metrics['last_commit_days_ago'] > 7:
            score -= 25
        elif metrics['last_commit_days_ago'] > 3:
            score -= 10
        
        if metrics['open_merge_requests'] > 10:
            score -= 15
        
        return max(0, min(100, score))
    
    def _days_since_last_commit(self, project_id: int) -> int:
        """Calculate days since last commit in project."""
        try:
            commits = list(self.client._paginated_get(
                f'projects/{project_id}/repository/commits',
                params={'per_page': 1}
            ))
            
            if commits:
                last_commit_date = datetime.fromisoformat(
                    commits[0]['created_at'].replace('Z', '+00:00')
                )
                return (datetime.now(last_commit_date.tzinfo) - last_commit_date).days
            
            return 999  # Very old or no commits
            
        except Exception:
            return 999
    
    def _generate_project_recommendations(self, metrics: Dict) -> List[str]:
        """Generate specific recommendations for a project."""
        recommendations = []
        
        if metrics['commits_this_week'] == 0:
            recommendations.append("No commits this week - check if project is active")
        
        if metrics['open_issues'] > 20:
            recommendations.append("High issue count - consider triaging and prioritizing")
        
        if metrics['last_commit_days_ago'] > 14:
            recommendations.append("No recent activity - verify project status")
        
        if metrics['open_merge_requests'] > 5:
            recommendations.append("Review backlog of merge requests")
        
        return recommendations
    
    def _calculate_individual_collaboration_score(self, metrics: Dict) -> float:
        """Calculate individual collaboration score."""
        score = 0
        
        # Points for different activities
        score += min(metrics['code_reviews'] * 5, 25)  # Up to 25 points
        score += min(metrics['project_count'] * 10, 30)  # Up to 30 points
        score += min(metrics['merge_requests_created'] * 3, 20)  # Up to 20 points
        score += min(metrics['issues_created'] * 2, 15)  # Up to 15 points
        score += min(metrics['issues_resolved'] * 3, 10)  # Up to 10 points
        
        return min(100, score)
    
    def _calculate_productivity_score(self, metrics: Dict) -> float:
        """Calculate overall productivity score for individual."""
        # Weighted scoring
        score = 0
        score += metrics['commits'] * 2
        score += metrics['merge_requests_merged'] * 5
        score += metrics['issues_resolved'] * 3
        score += metrics['project_count'] * 5
        
        # Normalize to 0-100 scale (adjust divisor based on your team's typical output)
        return min(100, score / 2)
    
    def _calculate_team_distribution_stats(self, contributors: Dict) -> Dict:
        """Calculate team distribution statistics."""
        if not contributors:
            return {}
        
        commit_counts = [m['commits'] for m in contributors.values()]
        productivity_scores = [m['productivity_score'] for m in contributors.values()]
        
        return {
            'total_contributors': len(contributors),
            'avg_commits': statistics.mean(commit_counts) if commit_counts else 0,
            'median_commits': statistics.median(commit_counts) if commit_counts else 0,
            'avg_productivity': statistics.mean(productivity_scores) if productivity_scores else 0,
            'top_performer': max(contributors.items(), key=lambda x: x[1]['productivity_score'], default=(None, {}))[0],
            'most_collaborative': max(contributors.items(), key=lambda x: x[1]['collaboration_score'], default=(None, {}))[0]
        }