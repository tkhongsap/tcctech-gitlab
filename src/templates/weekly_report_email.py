"""HTML email template generator for weekly productivity reports."""

import base64
from io import BytesIO
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WeeklyReportEmailTemplate:
    """Generate professional HTML email templates for weekly reports."""
    
    def __init__(self):
        """Initialize template generator."""
        self.chart_cache = {}
    
    def generate_html_email(
        self,
        report_data: Dict[str, Any],
        team_name: str = "Development Team",
        include_charts: bool = True
    ) -> str:
        """Generate complete HTML email for weekly report.
        
        Args:
            report_data: Report data from WeeklyProductivityReporter
            team_name: Name of the team for the report
            include_charts: Whether to include embedded charts
            
        Returns:
            Complete HTML email content
        """
        metadata = report_data.get('metadata', {})
        executive_summary = report_data.get('executive_summary', {})
        team_activity = report_data.get('team_activity', {})
        project_breakdown = report_data.get('project_breakdown', {})
        individual_metrics = report_data.get('individual_metrics', {})
        insights = report_data.get('insights_and_actions', {})
        
        # Generate charts if requested
        charts_html = ""
        if include_charts:
            charts_html = self._generate_charts_section(report_data)
        
        # Get detailed tables if available
        detailed_tables = report_data.get('detailed_tables', {})
        detailed_tables_html = ""
        if detailed_tables:
            detailed_tables_html = self._generate_detailed_tables_section(detailed_tables)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Productivity Report - {team_name}</title>
    <style>
        {self._get_email_styles()}
    </style>
</head>
<body>
    <div class="email-container">
        {self._generate_header(team_name, metadata)}
        {self._generate_executive_summary_section(executive_summary)}
        {self._generate_team_activity_section(team_activity)}
        {detailed_tables_html}
        {self._generate_project_health_section(project_breakdown)}
        {self._generate_individual_highlights_section(individual_metrics)}
        {charts_html}
        {self._generate_insights_section(insights)}
        {self._generate_footer(metadata)}
    </div>
</body>
</html>
        """
        
        return html_content.strip()
    
    def _get_email_styles(self) -> str:
        """Get CSS styles optimized for email clients."""
        return """
        /* Reset and base styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f4f6f9;
        }
        
        .email-container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #ffffff;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .header .period {
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 4px;
        }
        
        .header .generated {
            font-size: 14px;
            opacity: 0.8;
        }
        
        /* Sections */
        .section {
            padding: 25px 30px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .section:last-child {
            border-bottom: none;
        }
        
        .section-title {
            font-size: 20px;
            color: #2c3e50;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
        }
        
        .section-title .icon {
            margin-right: 8px;
            font-size: 22px;
        }
        
        /* Metrics grid */
        .metrics-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 15px 0;
        }
        
        .metric-card {
            flex: 1;
            min-width: 140px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 4px;
        }
        
        .metric-label {
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-change {
            font-size: 11px;
            margin-top: 4px;
        }
        
        .change-positive { color: #28a745; }
        .change-negative { color: #dc3545; }
        .change-neutral { color: #6c757d; }
        
        /* Project health */
        .project-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 15px 0;
        }
        
        .project-card {
            flex: 1;
            min-width: 200px;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 12px;
        }
        
        .project-name {
            font-weight: 600;
            color: #495057;
            margin-bottom: 6px;
            font-size: 14px;
        }
        
        .project-health {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
        }
        
        .health-badge {
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .health-healthy { background: #d4edda; color: #155724; }
        .health-warning { background: #fff3cd; color: #856404; }
        .health-critical { background: #f8d7da; color: #721c24; }
        
        .project-metrics {
            font-size: 12px;
            color: #6c757d;
        }
        
        /* Contributors */
        .contributors-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }
        
        .contributor-card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 10px;
            min-width: 140px;
        }
        
        .contributor-name {
            font-weight: 600;
            color: #495057;
            margin-bottom: 4px;
            font-size: 13px;
        }
        
        .contributor-stats {
            font-size: 11px;
            color: #6c757d;
        }
        
        /* Insights */
        .insights-list {
            list-style: none;
            margin: 15px 0;
        }
        
        .insights-list li {
            background: #f8f9fa;
            padding: 10px 15px;
            margin-bottom: 8px;
            border-radius: 6px;
            border-left: 3px solid #17a2b8;
            font-size: 14px;
        }
        
        .priority-high {
            border-left-color: #dc3545;
            background: #f8d7da;
        }
        
        .priority-medium {
            border-left-color: #ffc107;
            background: #fff3cd;
        }
        
        .priority-low {
            border-left-color: #28a745;
            background: #d4edda;
        }
        
        /* Charts */
        .chart-container {
            text-align: center;
            margin: 20px 0;
        }
        
        .chart-image {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Activity Tables */
        .activity-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 13px;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .activity-table th {
            background: #f8f9fa;
            color: #495057;
            font-weight: 600;
            padding: 12px 8px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-size: 12px;
        }
        
        .activity-table td {
            padding: 10px 8px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: middle;
        }
        
        .activity-table tr:hover {
            background-color: #f8f9fa;
        }
        
        .activity-table .status-active {
            color: #28a745;
            font-weight: 600;
        }
        
        .activity-table .status-inactive {
            color: #dc3545;
            font-weight: 600;
        }
        
        .activity-table .lines-positive {
            color: #28a745;
        }
        
        .activity-table .lines-negative {
            color: #dc3545;
        }
        
        .inactive-summary {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #dc3545;
        }
        
        .inactive-group {
            margin-bottom: 12px;
        }
        
        .inactive-group h5 {
            color: #dc3545;
            margin: 0 0 5px 0;
            font-size: 14px;
        }
        
        .inactive-projects {
            color: #6c757d;
            font-size: 12px;
            line-height: 1.4;
        }
        
        /* Footer */
        .footer {
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
        }
        
        /* Responsive */
        @media (max-width: 600px) {
            .email-container {
                margin: 0;
                box-shadow: none;
            }
            
            .header, .section {
                padding: 20px;
            }
            
            .metrics-grid {
                flex-direction: column;
            }
            
            .metric-card {
                min-width: auto;
            }
            
            .project-grid,
            .contributors-list {
                flex-direction: column;
            }
            
            .activity-table {
                font-size: 11px;
            }
            
            .activity-table th,
            .activity-table td {
                padding: 8px 4px;
            }
        }
        """
    
    def _generate_header(self, team_name: str, metadata: Dict) -> str:
        """Generate email header section."""
        period_start = datetime.fromisoformat(metadata.get('period_start', '')).strftime('%B %d')
        period_end = datetime.fromisoformat(metadata.get('period_end', '')).strftime('%B %d, %Y')
        generated_at = datetime.fromisoformat(metadata.get('generated_at', '')).strftime('%Y-%m-%d %H:%M')
        
        return f"""
        <div class="header">
            <h1>📊 Weekly Productivity Report</h1>
            <div class="period">{team_name} • {period_start} - {period_end}</div>
            <div class="generated">Generated on {generated_at}</div>
        </div>
        """
    
    def _generate_executive_summary_section(self, summary: Dict) -> str:
        """Generate executive summary section."""
        key_metrics = summary.get('key_metrics', {})
        highlights = summary.get('highlights', [])
        concerns = summary.get('concerns', [])
        
        # Format metrics
        metrics_html = ""
        if key_metrics:
            metrics_html = f"""
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{key_metrics.get('total_commits', 0)}</div>
                    <div class="metric-label">Total Commits</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{key_metrics.get('total_merge_requests', 0)}</div>
                    <div class="metric-label">Merge Requests</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{key_metrics.get('merge_rate', 0):.1f}%</div>
                    <div class="metric-label">Merge Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{key_metrics.get('active_contributors', 0)}</div>
                    <div class="metric-label">Contributors</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{key_metrics.get('healthy_projects', 0)}</div>
                    <div class="metric-label">Healthy Projects</div>
                </div>
            </div>
            """
        
        # Format highlights and concerns
        status_html = ""
        if highlights or concerns:
            status_html = "<div style='margin-top: 15px;'>"
            
            if highlights:
                status_html += "<div style='margin-bottom: 10px;'><strong>✨ Highlights:</strong><ul style='margin: 5px 0 0 20px;'>"
                for highlight in highlights[:3]:  # Limit to top 3
                    status_html += f"<li style='color: #28a745; margin-bottom: 3px;'>{highlight}</li>"
                status_html += "</ul></div>"
            
            if concerns:
                status_html += "<div><strong>⚠️ Attention Needed:</strong><ul style='margin: 5px 0 0 20px;'>"
                for concern in concerns[:3]:  # Limit to top 3
                    status_html += f"<li style='color: #dc3545; margin-bottom: 3px;'>{concern}</li>"
                status_html += "</ul></div>"
            
            status_html += "</div>"
        
        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">📋</span>
                Executive Summary
            </h2>
            {metrics_html}
            {status_html}
        </div>
        """
    
    def _generate_team_activity_section(self, activity: Dict) -> str:
        """Generate team activity metrics section."""
        commits = activity.get('commits', {})
        merge_requests = activity.get('merge_requests', {})
        issues = activity.get('issues', {})
        
        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">👥</span>
                Team Activity
            </h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{commits.get('total', 0)}</div>
                    <div class="metric-label">Commits</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{merge_requests.get('opened', 0)}</div>
                    <div class="metric-label">MRs Opened</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{merge_requests.get('merged', 0)}</div>
                    <div class="metric-label">MRs Merged</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{issues.get('opened', 0)}</div>
                    <div class="metric-label">Issues Created</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{issues.get('closed', 0)}</div>
                    <div class="metric-label">Issues Resolved</div>
                </div>
            </div>
            
            <div style="margin-top: 15px;">
                <h4 style="color: #495057; margin-bottom: 8px;">Top Contributors This Week</h4>
                <div style="font-size: 13px;">
                    {self._format_top_contributors(commits.get('by_author', {}))}
                </div>
            </div>
        </div>
        """
    
    def _generate_project_health_section(self, breakdown: Dict) -> str:
        """Generate project health breakdown section."""
        projects = breakdown.get('projects', [])
        health_summary = breakdown.get('health_summary', {})
        
        # Sort projects by health status (critical first for attention)
        critical_projects = [p for p in projects if p['health_status'] == 'critical'][:3]
        healthy_projects = [p for p in projects if p['health_status'] == 'healthy'][:3]
        
        projects_html = ""
        if critical_projects:
            projects_html += "<h4 style='color: #dc3545; margin-bottom: 8px;'>🚨 Needs Attention</h4>"
            projects_html += "<div class='project-grid'>"
            for project in critical_projects:
                projects_html += self._format_project_card(project)
            projects_html += "</div>"
        
        if healthy_projects:
            projects_html += "<h4 style='color: #28a745; margin: 15px 0 8px 0;'>💚 Performing Well</h4>"
            projects_html += "<div class='project-grid'>"
            for project in healthy_projects:
                projects_html += self._format_project_card(project)
            projects_html += "</div>"
        
        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">🏥</span>
                Project Health
            </h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{health_summary.get('healthy', 0)}</div>
                    <div class="metric-label">Healthy</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{health_summary.get('warning', 0)}</div>
                    <div class="metric-label">Warning</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{health_summary.get('critical', 0)}</div>
                    <div class="metric-label">Critical</div>
                </div>
            </div>
            {projects_html}
        </div>
        """
    
    def _generate_individual_highlights_section(self, individual_metrics: Dict) -> str:
        """Generate individual contributor highlights section."""
        contributors = individual_metrics.get('contributors', {})
        team_stats = individual_metrics.get('team_stats', {})
        
        # Get top performers
        top_commits = max(contributors.items(), key=lambda x: x[1]['commits'], default=(None, {}))
        top_productivity = max(contributors.items(), key=lambda x: x[1]['productivity_score'], default=(None, {}))
        top_collaboration = max(contributors.items(), key=lambda x: x[1]['collaboration_score'], default=(None, {}))
        
        highlights_html = ""
        if top_commits[0]:
            highlights_html += f"""
            <div style="margin-bottom: 15px;">
                <h4 style="color: #495057; margin-bottom: 8px;">🌟 Team Highlights</h4>
                <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; font-size: 13px;">
                    <div style="margin-bottom: 5px;"><strong>Most Active:</strong> {top_commits[0]} ({top_commits[1]['commits']} commits)</div>
                    <div style="margin-bottom: 5px;"><strong>Top Productivity:</strong> {top_productivity[0]} (Score: {top_productivity[1]['productivity_score']:.1f})</div>
                    <div><strong>Best Collaborator:</strong> {top_collaboration[0]} (Score: {top_collaboration[1]['collaboration_score']:.1f})</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">👤</span>
                Team Performance
            </h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{team_stats.get('total_contributors', 0)}</div>
                    <div class="metric-label">Active Contributors</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{team_stats.get('avg_commits', 0):.1f}</div>
                    <div class="metric-label">Avg Commits</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{team_stats.get('avg_productivity', 0):.1f}</div>
                    <div class="metric-label">Avg Productivity</div>
                </div>
            </div>
            {highlights_html}
        </div>
        """
    
    def _generate_charts_section(self, report_data: Dict) -> str:
        """Generate charts section with embedded chart images."""
        try:
            # Try to generate charts using matplotlib
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime, timedelta
            
            charts_html = '<div class="section"><h2 class="section-title"><span class="icon">📊</span>Visual Analytics</h2>'
            
            # Commit activity chart
            team_activity = report_data.get('team_activity', {})
            commits_by_day = team_activity.get('commits', {}).get('by_day', {})
            
            if commits_by_day:
                chart_html = self._create_commits_chart(commits_by_day)
                if chart_html:
                    charts_html += chart_html
            
            charts_html += '</div>'
            return charts_html
            
        except ImportError:
            # Fallback: text-based charts
            return self._generate_text_charts_section(report_data)
    
    def _create_commits_chart(self, commits_by_day: Dict) -> str:
        """Create embedded commit activity chart."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime
            
            # Prepare data
            dates = []
            commits = []
            for date_str, count in sorted(commits_by_day.items()):
                dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
                commits.append(count)
            
            if not dates:
                return ""
            
            # Create chart
            plt.style.use('default')
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(dates, commits, marker='o', linewidth=2, markersize=6, color='#667eea')
            ax.fill_between(dates, commits, alpha=0.3, color='#667eea')
            
            ax.set_title('Daily Commit Activity', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Date', fontsize=10)
            ax.set_ylabel('Commits', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Format dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f'''
            <div class="chart-container">
                <img src="data:image/png;base64,{chart_base64}" alt="Daily Commit Activity" class="chart-image">
            </div>
            '''
            
        except Exception as e:
            logger.warning(f"Failed to generate commits chart: {e}")
            return ""
    
    def _generate_text_charts_section(self, report_data: Dict) -> str:
        """Generate text-based charts as fallback."""
        team_activity = report_data.get('team_activity', {})
        commits_by_day = team_activity.get('commits', {}).get('by_day', {})
        
        if not commits_by_day:
            return ""
        
        # Create simple ASCII chart
        max_commits = max(commits_by_day.values()) if commits_by_day else 1
        chart_html = '<div class="section"><h2 class="section-title"><span class="icon">📊</span>Activity Trends</h2>'
        chart_html += '<div style="font-family: monospace; font-size: 12px; background: #f8f9fa; padding: 15px; border-radius: 6px; overflow-x: auto;">'
        
        for date_str, count in sorted(commits_by_day.items())[-7:]:  # Last 7 days
            bar_length = int((count / max_commits) * 20) if max_commits > 0 else 0
            bar = '█' * bar_length + '░' * (20 - bar_length)
            chart_html += f'{date_str}: {bar} {count}<br>'
        
        chart_html += '</div></div>'
        return chart_html
    
    def _generate_insights_section(self, insights: Dict) -> str:
        """Generate insights and recommendations section."""
        actions = insights.get('recommended_actions', [])
        focus_areas = insights.get('team_focus_areas', [])
        coaching = insights.get('individual_coaching', [])
        
        content_html = ""
        
        if actions:
            content_html += "<h4 style='color: #495057; margin-bottom: 8px;'>🎯 Recommended Actions</h4>"
            content_html += "<ul class='insights-list'>"
            for action in actions[:3]:  # Top 3 actions
                priority_class = f"priority-{action.get('priority', 'medium')}"
                content_html += f"<li class='{priority_class}'>{action.get('action', 'Action needed')}</li>"
            content_html += "</ul>"
        
        if focus_areas:
            content_html += "<h4 style='color: #495057; margin: 15px 0 8px 0;'>🎯 Team Focus Areas</h4>"
            content_html += "<ul style='margin: 5px 0 0 20px; font-size: 13px;'>"
            for area in focus_areas[:3]:
                content_html += f"<li style='margin-bottom: 5px;'>{area}</li>"
            content_html += "</ul>"
        
        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">💡</span>
                Insights & Next Steps
            </h2>
            {content_html}
        </div>
        """
    
    def _generate_footer(self, metadata: Dict) -> str:
        """Generate email footer."""
        return """
        <div class="footer">
            <p>This report was automatically generated by GitLab Tools.</p>
            <p>For questions or feedback, please contact your team lead.</p>
        </div>
        """
    
    def _format_top_contributors(self, by_author: Dict) -> str:
        """Format top contributors list."""
        if not by_author:
            return "<em>No activity this week</em>"
        
        sorted_authors = sorted(by_author.items(), key=lambda x: x[1], reverse=True)[:5]
        result = ""
        for author, commits in sorted_authors:
            result += f"<div style='margin-bottom: 3px;'><strong>{author}</strong>: {commits} commits</div>"
        
        return result
    
    def _format_project_card(self, project: Dict) -> str:
        """Format individual project card."""
        health_class = f"health-{project['health_status']}"
        metrics = project.get('metrics', {})
        
        return f"""
        <div class="project-card">
            <div class="project-name">{project['name']}</div>
            <div class="project-health">
                <span class="health-badge {health_class}">{project['health_status'].title()}</span>
                <span style="font-size: 11px; color: #6c757d;">Score: {project['health_score']}</span>
            </div>
            <div class="project-metrics">
                {metrics.get('commits_this_week', 0)} commits • 
                {metrics.get('open_issues', 0)} open issues
            </div>
        </div>
        """
    
    def _generate_detailed_tables_section(self, tables: Dict[str, List[Dict]]) -> str:
        """Generate detailed activity tables section for email."""
        branch_data = tables.get('project_branch_activity', [])
        contrib_data = tables.get('project_contributor_activity', [])
        
        # Separate active and inactive data
        active_branches = [item for item in branch_data if item.get('commits_total', item.get('commits', 0)) > 0]
        inactive_branches = [item for item in branch_data if item.get('commits_total', item.get('commits', 0)) == 0]
        active_contribs = [item for item in contrib_data if item['commits'] > 0 or item['mrs'] > 0 or item['net_lines'] != 0]
        inactive_contribs = [item for item in contrib_data if item['commits'] == 0 and item['mrs'] == 0 and item['net_lines'] == 0]
        
        # Sort active data
        active_branches.sort(key=lambda x: (x.get('commits_total', x.get('commits', 0)), x['contributors'], x['net_lines']), reverse=True)
        active_contribs.sort(key=lambda x: (x['contributor'], -(x['commits'] + x['mrs'])))
        
        content_html = ""
        
        # Active Projects & Branches Table
        if active_branches:
            content_html += "<h3 style='color: #28a745; margin: 20px 0 10px 0; font-size: 18px;'>🟢 Active Projects & Branches</h3>"
            content_html += "<table class='activity-table'>"
            content_html += """
            <thead>
                <tr>
                    <th>Group</th>
                    <th>Project</th>
                    <th>Branch</th>
                    <th>Commits</th>
                    <th>Contributors</th>
                    <th>Lines±</th>
                </tr>
            </thead>
            <tbody>
            """
            
            # Limit to top 15 for email
            for item in active_branches[:15]:
                net_lines = item['net_lines']
                lines_str = f"+{net_lines}" if net_lines > 0 else str(net_lines)
                lines_class = "lines-positive" if net_lines > 0 else "lines-negative"
                
                content_html += f"""
                <tr>
                    <td>{item['group'][:12]}</td>
                    <td>{item['project'][:18]}</td>
                    <td>{item['branch'][:10]}</td>
                    <td style="text-align: center;">{item.get('commits_total', item.get('commits', 0))}</td>
                    <td style="text-align: center;">{item['contributors']}</td>
                    <td style="text-align: center;" class="{lines_class}">{lines_str}</td>
                </tr>
                """
            
            content_html += "</tbody></table>"
            
            if len(active_branches) > 15:
                content_html += f"<p style='font-size: 12px; color: #6c757d; margin: 5px 0;'>... and {len(active_branches) - 15} more active branches</p>"
        
        # Active Contributors by Project Table
        if active_contribs:
            content_html += "<h3 style='color: #007bff; margin: 25px 0 10px 0; font-size: 18px;'>👥 Active Contributors</h3>"
            content_html += "<table class='activity-table'>"
            content_html += """
            <thead>
                <tr>
                    <th>Contributor</th>
                    <th>Project</th>
                    <th>Group</th>
                    <th>Commits</th>
                    <th>MRs</th>
                    <th>Lines±</th>
                    <th>Issues±</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
            """
            
            # Limit to top 20 for email
            for item in active_contribs[:20]:
                net_lines = item['net_lines']
                lines_str = f"+{net_lines}" if net_lines > 0 else str(net_lines)
                lines_class = "lines-positive" if net_lines > 0 else "lines-negative"
                
                issues_opened = item['issues_opened']
                issues_closed = item['issues_closed']
                if issues_opened > 0 or issues_closed > 0:
                    issues_str = f"+{issues_opened}/-{issues_closed}"
                else:
                    issues_str = "0"
                
                content_html += f"""
                <tr>
                    <td>{item['contributor'][:12] if item['contributor'] != '-' else '-'}</td>
                    <td>{item['project'][:15]}</td>
                    <td>{item['group'][:12]}</td>
                    <td style="text-align: center;">{item['commits']}</td>
                    <td style="text-align: center;">{item['mrs']}</td>
                    <td style="text-align: center;" class="{lines_class}">{lines_str}</td>
                    <td style="text-align: center;">{issues_str}</td>
                    <td style="text-align: center;"><strong>{item['total_activity']}</strong></td>
                </tr>
                """
            
            content_html += "</tbody></table>"
            
            if len(active_contribs) > 20:
                content_html += f"<p style='font-size: 12px; color: #6c757d; margin: 5px 0;'>... and {len(active_contribs) - 20} more active contributors</p>"
        
        # Inactive Projects Summary
        if inactive_contribs:
            content_html += "<h3 style='color: #dc3545; margin: 25px 0 10px 0; font-size: 18px;'>🔴 Inactive Projects Summary</h3>"
            content_html += "<div class='inactive-summary'>"
            
            # Group inactive projects by group
            inactive_by_group = {}
            for item in inactive_contribs:
                group = item['group']
                if group not in inactive_by_group:
                    inactive_by_group[group] = set()
                inactive_by_group[group].add(item['project'])
            
            for group, projects in inactive_by_group.items():
                unique_projects = sorted(list(projects))
                content_html += f"""
                <div class="inactive-group">
                    <h5>{group}</h5>
                    <div class="inactive-projects">
                        {len(unique_projects)} inactive projects: {', '.join(unique_projects[:6])}
                        {'...' if len(unique_projects) > 6 else ''}
                    </div>
                </div>
                """
            
            content_html += "</div>"
        
        # Activity summary
        active_projects_count = len(set([(p['group'], p['project']) for p in active_contribs]))
        inactive_projects_count = len(set([(p['group'], p['project']) for p in inactive_contribs]))
        total_projects = active_projects_count + inactive_projects_count
        
        if total_projects > 0:
            content_html += f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #495057;">📊 Activity Summary</h4>
                <div style="display: flex; justify-content: space-around; font-size: 14px;">
                    <div><strong style="color: #28a745;">{active_projects_count}</strong> Active Projects ({active_projects_count/total_projects*100:.1f}%)</div>
                    <div><strong style="color: #dc3545;">{inactive_projects_count}</strong> Inactive Projects ({inactive_projects_count/total_projects*100:.1f}%)</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2 class="section-title">
                <span class="icon">📊</span>
                Project Activity Details
            </h2>
            {content_html}
        </div>
        """ if content_html else ""