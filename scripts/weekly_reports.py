#!/usr/bin/env python3
"""Generate and send weekly productivity reports for team syncs."""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import GitLabClient
from src.services.weekly_reports import WeeklyProductivityReporter
from src.services.email_service import WeeklyReportEmailSender
from src.templates.weekly_report_email import WeeklyReportEmailTemplate
from src.utils import Config, setup_logging, get_logger
from src.utils.logger import Colors

logger = get_logger(__name__)


def _format_table(headers: List[str], rows: List[List[str]], title: str = "") -> str:
    """Format data as a table."""
    if not rows:
        return f"\n{title}\nNo data available."
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Create separator
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    
    # Format header
    header_row = "|" + "|".join(f" {headers[i]:<{col_widths[i]}} " for i in range(len(headers))) + "|"
    
    # Format rows
    formatted_rows = []
    for row in rows:
        formatted_row = "|" + "|".join(f" {str(row[i]):<{col_widths[i]}} " for i in range(len(row))) + "|"
        formatted_rows.append(formatted_row)
    
    # Combine everything
    result = []
    if title:
        result.append(f"\n{title}")
    result.append(separator)
    result.append(header_row)
    result.append(separator)
    result.extend(formatted_rows)
    result.append(separator)
    
    return "\n".join(result)


def _display_detailed_tables(tables: Dict[str, List[Dict]]):
    """Display detailed activity tables separated by active/inactive."""
    
    # Project Branch Activity Table
    if tables.get('project_branch_activity'):
        branch_data = tables['project_branch_activity']
        
        # Separate active and inactive branches (use commits_total for backwards compatibility)
        active_branches = [item for item in branch_data if item.get('commits_total', item.get('commits', 0)) > 0]
        inactive_branches = [item for item in branch_data if item.get('commits_total', item.get('commits', 0)) == 0]
        
        # Sort active branches by total activity (commits + contributors)
        active_branches.sort(key=lambda x: (
            x.get('commits_total', x.get('commits', 0)), 
            x['contributors'], 
            x.get('net_lines', 0)
        ), reverse=True)
        
        # Enhanced headers with new metrics
        headers = ["Group", "Project", "Branch", "Total", "Unique", "Contributors", "Lines±(Own)", "Lines±(Diff)", "Status"]
        
        # Display Active Projects
        if active_branches:
            print(f"\n{Colors.BOLD}📊 ACTIVE Projects & Branch Activity (Ranked by Activity){Colors.RESET}")
            active_rows = []
            
            for item in active_branches[:30]:  # Show top 30 active
                # Backwards compatibility for field names
                total_commits = item.get('commits_total', item.get('commits', 0))
                unique_commits = item.get('commits_unique', 0)
                
                # Line changes with ownership method
                net_lines_own = item.get('net_lines', 0)
                lines_own_str = f"+{net_lines_own}" if net_lines_own > 0 else str(net_lines_own)
                
                # Line changes with git diff method
                net_lines_diff = item.get('net_lines_git_diff', 0)
                if net_lines_diff == 0 and total_commits > 0:
                    lines_diff_str = "N/A"  # Couldn't calculate diff
                else:
                    lines_diff_str = f"+{net_lines_diff}" if net_lines_diff > 0 else str(net_lines_diff)
                
                active_rows.append([
                    item['group'][:15],
                    item['project'][:20],
                    item['branch'][:12],
                    str(total_commits),
                    str(unique_commits),
                    str(item['contributors']),
                    lines_own_str,
                    lines_diff_str,
                    f"{Colors.GREEN}Active{Colors.RESET}"
                ])
            
            active_table = _format_table(headers, active_rows)
            print(active_table)
            
            # Add legend for new columns
            print(f"\n{Colors.BOLD}📖 Legend:{Colors.RESET}")
            print(f"  Total: All commits on this branch")
            print(f"  Unique: Commits only on this branch (not shared with others)")  
            print(f"  Lines±(Own): Line changes using commit ownership method")
            print(f"  Lines±(Diff): Line changes using git diff vs base branch method")
            
            if len(active_branches) > 30:
                print(f"... and {len(active_branches) - 30} more active branches")
        
        # Display Inactive Projects
        if inactive_branches:
            print(f"\n{Colors.BOLD}📋 INACTIVE Projects (No Commits This Week){Colors.RESET}")
            inactive_rows = []
            
            # Sort inactive by project name for easy scanning
            inactive_branches.sort(key=lambda x: (x['group'], x['project']))
            
            for item in inactive_branches[:20]:  # Show up to 20 inactive
                inactive_rows.append([
                    item['group'][:15],
                    item['project'][:20],
                    item['branch'][:12],
                    "0",  # Total commits
                    "0",  # Unique commits
                    "0",  # Contributors
                    "0",  # Lines±(Own)
                    "0",  # Lines±(Diff)
                    f"{Colors.RED}Inactive{Colors.RESET}"
                ])
            
            inactive_table = _format_table(headers, inactive_rows)
            print(inactive_table)
            
            if len(inactive_branches) > 20:
                print(f"... and {len(inactive_branches) - 20} more inactive branches")
    
    # Project Contributor Activity Table
    if tables.get('project_contributor_activity'):
        contrib_data = tables['project_contributor_activity']
        
        # Separate active and inactive projects - filter out pure issue-only activity
        active_contribs = [item for item in contrib_data if item['commits'] > 0 or item['mrs'] > 0 or item['net_lines'] != 0]
        inactive_contribs = [item for item in contrib_data if item['commits'] == 0 and item['mrs'] == 0 and item['net_lines'] == 0]
        
        # Sort by contributor name (primary), then by commits+MRs within each contributor (secondary)
        active_contribs.sort(key=lambda x: (x['contributor'], -(x['commits'] + x['mrs'])))
        
        headers = ["Contributor", "Project", "Group", "Commits", "MRs", "Lines±", "Issues±", "Total"]
        
        # Display Active Contributors
        if active_contribs:
            print(f"\n{Colors.BOLD}👥 ACTIVE Contributors (Grouped by Person){Colors.RESET}")
            active_rows = []
            
            for item in active_contribs[:40]:  # Show top 40 active
                # Format net lines
                net_lines = item['net_lines']
                lines_str = f"+{net_lines}" if net_lines > 0 else str(net_lines)
                
                # Format issues
                issues_opened = item['issues_opened']
                issues_closed = item['issues_closed']
                if issues_opened > 0 or issues_closed > 0:
                    issues_str = f"+{issues_opened}/-{issues_closed}"
                else:
                    issues_str = "0"
                
                active_rows.append([
                    item['contributor'][:15] if item['contributor'] != '-' else '-',
                    item['project'][:20],
                    item['group'][:15],
                    str(item['commits']),
                    str(item['mrs']),
                    lines_str,
                    issues_str,
                    str(item['total_activity'])
                ])
            
            active_table = _format_table(headers, active_rows)
            print(active_table)
            
            if len(active_contribs) > 40:
                print(f"... and {len(active_contribs) - 40} more active contributors")
        
        # Display Inactive Projects Summary
        if inactive_contribs:
            print(f"\n{Colors.BOLD}📋 INACTIVE Projects (No Activity This Week){Colors.RESET}")
            # Group inactive projects by group for summary
            inactive_by_group = {}
            for item in inactive_contribs:
                group = item['group']
                if group not in inactive_by_group:
                    inactive_by_group[group] = []
                inactive_by_group[group].append(item['project'])
            
            for group, projects in inactive_by_group.items():
                unique_projects = list(set(projects))
                unique_projects.sort()
                print(f"  {Colors.RED}{group}{Colors.RESET}: {len(unique_projects)} inactive projects")
                # Show first few project names
                if len(unique_projects) <= 5:
                    print(f"    → {', '.join(unique_projects)}")
                else:
                    print(f"    → {', '.join(unique_projects[:5])} ... and {len(unique_projects) - 5} more")
        
        # Enhanced Summary stats
        active_projects = len(set([(p['group'], p['project']) for p in active_contribs]))
        inactive_projects = len(set([(p['group'], p['project']) for p in inactive_contribs]))
        total_projects = active_projects + inactive_projects
        
        print(f"\n{Colors.BOLD}📊 Project Activity Summary:{Colors.RESET}")
        print(f"  {Colors.GREEN}Active projects: {active_projects}{Colors.RESET} ({active_projects/total_projects*100:.1f}%)")
        print(f"  {Colors.RED}Inactive projects: {inactive_projects}{Colors.RESET} ({inactive_projects/total_projects*100:.1f}%)")
        
        if active_contribs:
            most_active = active_contribs[0]
            print(f"  🏆 Most active: {most_active['project']} (Activity score: {most_active['total_activity']})")


def parse_groups(groups_arg: str) -> List[int]:
    """Parse group IDs from command line argument.
    
    Args:
        groups_arg: Comma-separated group IDs or names
        
    Returns:
        List of group IDs
    """
    if not groups_arg:
        return []
    
    group_items = [item.strip() for item in groups_arg.split(',')]
    group_ids = []
    
    for item in group_items:
        if item.isdigit():
            group_ids.append(int(item))
        else:
            # TODO: Look up group by name
            logger.warning(f"Group name lookup not implemented yet: {item}")
    
    return group_ids


def parse_team_members(members_arg: str) -> List[str]:
    """Parse team member list from command line argument.
    
    Args:
        members_arg: Comma-separated usernames or emails
        
    Returns:
        List of team member identifiers
    """
    if not members_arg:
        return []
    
    return [member.strip() for member in members_arg.split(',')]


def parse_recipients(recipients_arg: str) -> List[str]:
    """Parse email recipients from command line argument.
    
    Args:
        recipients_arg: Comma-separated email addresses
        
    Returns:
        List of email addresses
    """
    if not recipients_arg:
        return []
    
    return [email.strip() for email in recipients_arg.split(',')]


def save_report_to_file(report_data: Dict[str, Any], output_path: Path, format_type: str) -> None:
    """Save report data to file.
    
    Args:
        report_data: Report data to save
        output_path: Output file path
        format_type: Format (json, html, markdown)
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format_type == 'json':
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        logger.info(f"Report saved as JSON: {output_path}")
    
    elif format_type == 'html':
        template = WeeklyReportEmailTemplate()
        html_content = template.generate_html_email(report_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Report saved as HTML: {output_path}")
    
    elif format_type == 'markdown':
        markdown_content = generate_markdown_report(report_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"Report saved as Markdown: {output_path}")


def generate_markdown_report(report_data: Dict[str, Any]) -> str:
    """Generate markdown version of the report.
    
    Args:
        report_data: Report data
        
    Returns:
        Markdown content
    """
    metadata = report_data.get('metadata', {})
    executive_summary = report_data.get('executive_summary', {})
    team_activity = report_data.get('team_activity', {})
    project_breakdown = report_data.get('project_breakdown', {})
    individual_metrics = report_data.get('individual_metrics', {})
    insights = report_data.get('insights_and_actions', {})
    
    # Format dates
    start_date = datetime.fromisoformat(metadata.get('period_start', '')).strftime('%B %d')
    end_date = datetime.fromisoformat(metadata.get('period_end', '')).strftime('%B %d, %Y')
    generated_at = datetime.fromisoformat(metadata.get('generated_at', '')).strftime('%Y-%m-%d %H:%M')
    
    markdown = f"""# Weekly Productivity Report

**Period:** {start_date} - {end_date}  
**Generated:** {generated_at}  
**Groups Analyzed:** {metadata.get('groups_analyzed', 0)}  
**Team Size:** {metadata.get('team_size', 'All contributors')}

## Executive Summary

### Key Metrics
"""
    
    # Key metrics
    key_metrics = executive_summary.get('key_metrics', {})
    if key_metrics:
        markdown += f"""
| Metric | Value |
|--------|-------|
| Total Commits | {key_metrics.get('total_commits', 0)} |
| Total Merge Requests | {key_metrics.get('total_merge_requests', 0)} |
| Merge Rate | {key_metrics.get('merge_rate', 0):.1f}% |
| Active Contributors | {key_metrics.get('active_contributors', 0)} |
| Healthy Projects | {key_metrics.get('healthy_projects', 0)} |
| Projects Needing Attention | {key_metrics.get('projects_needing_attention', 0)} |
"""
    
    # Highlights and concerns
    highlights = executive_summary.get('highlights', [])
    concerns = executive_summary.get('concerns', [])
    
    if highlights:
        markdown += "\n### ✨ Highlights\n"
        for highlight in highlights:
            markdown += f"- {highlight}\n"
    
    if concerns:
        markdown += "\n### ⚠️ Attention Needed\n"
        for concern in concerns:
            markdown += f"- {concern}\n"
    
    # Team Activity
    markdown += "\n## Team Activity\n"
    commits = team_activity.get('commits', {})
    merge_requests = team_activity.get('merge_requests', {})
    issues = team_activity.get('issues', {})
    
    markdown += f"""
| Activity | Count |
|----------|-------|
| Commits | {commits.get('total', 0)} |
| Merge Requests Opened | {merge_requests.get('opened', 0)} |
| Merge Requests Merged | {merge_requests.get('merged', 0)} |
| Issues Created | {issues.get('opened', 0)} |
| Issues Resolved | {issues.get('closed', 0)} |
"""
    
    # Top contributors
    by_author = commits.get('by_author', {})
    if by_author:
        markdown += "\n### Top Contributors\n"
        for author, count in sorted(by_author.items(), key=lambda x: x[1], reverse=True)[:5]:
            markdown += f"- **{author}**: {count} commits\n"
    
    # Project Health
    markdown += "\n## Project Health\n"
    health_summary = project_breakdown.get('health_summary', {})
    
    markdown += f"""
| Status | Count |
|--------|-------|
| Healthy | {health_summary.get('healthy', 0)} |
| Warning | {health_summary.get('warning', 0)} |
| Critical | {health_summary.get('critical', 0)} |
"""
    
    # Critical projects
    projects = project_breakdown.get('projects', [])
    critical_projects = [p for p in projects if p['health_status'] == 'critical']
    
    if critical_projects:
        markdown += "\n### 🚨 Projects Needing Attention\n"
        for project in critical_projects[:5]:
            metrics = project.get('metrics', {})
            markdown += f"- **{project['name']}** (Score: {project['health_score']})\n"
            markdown += f"  - {metrics.get('commits_this_week', 0)} commits this week\n"
            markdown += f"  - {metrics.get('open_issues', 0)} open issues\n"
            if project.get('recommendations'):
                markdown += f"  - Recommendations: {', '.join(project['recommendations'][:2])}\n"
    
    # Team Performance
    markdown += "\n## Team Performance\n"
    team_stats = individual_metrics.get('team_stats', {})
    
    if team_stats:
        markdown += f"""
| Metric | Value |
|--------|-------|
| Active Contributors | {team_stats.get('total_contributors', 0)} |
| Average Commits | {team_stats.get('avg_commits', 0):.1f} |
| Average Productivity Score | {team_stats.get('avg_productivity', 0):.1f} |
"""
        
        if team_stats.get('top_performer'):
            markdown += f"\n**🌟 Top Performer:** {team_stats['top_performer']}\n"
        if team_stats.get('most_collaborative'):
            markdown += f"**🤝 Most Collaborative:** {team_stats['most_collaborative']}\n"
    
    # Insights and Actions
    markdown += "\n## Insights & Next Steps\n"
    
    actions = insights.get('recommended_actions', [])
    if actions:
        markdown += "\n### Recommended Actions\n"
        for action in actions:
            priority = action.get('priority', 'medium').upper()
            markdown += f"- **[{priority}]** {action.get('action', 'Action needed')}\n"
            if action.get('rationale'):
                markdown += f"  - {action['rationale']}\n"
    
    focus_areas = insights.get('team_focus_areas', [])
    if focus_areas:
        markdown += "\n### Team Focus Areas\n"
        for area in focus_areas:
            markdown += f"- {area}\n"
    
    coaching = insights.get('individual_coaching', [])
    if coaching:
        markdown += "\n### Individual Coaching Opportunities\n"
        for item in coaching:
            markdown += f"- **{item.get('focus', 'Focus area')}**: {item.get('suggestion', 'No suggestion')}\n"
    
    markdown += "\n---\n*Generated by GitLab Analytics - Weekly Productivity Reports*"
    
    return markdown


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate and send weekly productivity reports for team syncs",
        epilog="""
Examples:
  # Generate report for groups 1,2,3 and save as HTML
  python scripts/weekly_reports.py --groups 1,2,3 --output report.html

  # Send email report to team
  python scripts/weekly_reports.py --groups 1,2,3 --email team@company.com,manager@company.com

  # Generate report for specific team members
  python scripts/weekly_reports.py --groups 1,2,3 --team john.doe,jane.smith --output report.json

  # Generate 2-week report with email delivery
  python scripts/weekly_reports.py --groups 1,2,3 --weeks 2 --email team@company.com
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Target groups
    parser.add_argument(
        '--groups', '-g',
        required=True,
        help='Comma-separated list of GitLab group IDs to analyze'
    )
    
    # Team configuration
    parser.add_argument(
        '--team',
        help='Comma-separated list of team member usernames to focus on (optional)'
    )
    parser.add_argument(
        '--team-name',
        default='Development Team',
        help='Name of the team for the report (default: Development Team)'
    )
    
    # Time period
    parser.add_argument(
        '--weeks',
        type=int,
        default=1,
        help='Number of weeks to analyze (default: 1)'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output file path (format determined by extension: .json, .html, .md)'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'html', 'markdown'],
        default='html',
        help='Output format when no extension in output path (default: html)'
    )
    
    # Email options
    parser.add_argument(
        '--email',
        help='Comma-separated list of email recipients'
    )
    parser.add_argument(
        '--email-cc',
        help='Comma-separated list of CC recipients'
    )
    parser.add_argument(
        '--email-attachments',
        help='Comma-separated list of file paths to attach to email'
    )
    parser.add_argument(
        '--no-charts',
        action='store_true',
        help='Disable chart generation in email reports'
    )
    
    # Email testing
    parser.add_argument(
        '--test-email',
        help='Send test email to specified address to verify configuration'
    )
    
    # Configuration
    parser.add_argument(
        '--config', '-c',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Generate report but do not send emails'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    # Setup logging
    setup_logging(
        config.get_log_config(),
        console_level=args.log_level
    )
    
    try:
        # Validate configuration
        config.validate()
        
        # Handle test email
        if args.test_email:
            print(f"{Colors.BOLD}Sending test email to {args.test_email}...{Colors.RESET}")
            email_sender = WeeklyReportEmailSender()
            if email_sender.send_test_email(args.test_email):
                print(f"{Colors.GREEN}Test email sent successfully!{Colors.RESET}")
                return 0
            else:
                print(f"{Colors.RED}Failed to send test email. Check configuration and logs.{Colors.RESET}")
                return 1
        
        # Validate required arguments
        if not args.groups:
            print(f"{Colors.RED}Error: --groups is required{Colors.RESET}")
            return 1
        
        if not args.output and not args.email:
            print(f"{Colors.RED}Error: Either --output or --email must be specified{Colors.RESET}")
            return 1
        
        # Parse arguments
        group_ids = parse_groups(args.groups)
        team_members = parse_team_members(args.team) if args.team else None
        
        if not group_ids:
            print(f"{Colors.RED}Error: No valid group IDs provided{Colors.RESET}")
            return 1
        
        # Create GitLab client
        gitlab_config = config.get_gitlab_config()
        client = GitLabClient(
            url=gitlab_config['url'],
            token=gitlab_config['token'],
            config=gitlab_config
        )
        
        # Create weekly reporter
        reporter = WeeklyProductivityReporter(client)
        
        print(f"{Colors.BOLD}Generating weekly productivity report...{Colors.RESET}")
        print(f"Groups: {group_ids}")
        print(f"Team: {args.team_name}")
        print(f"Period: {args.weeks} week(s)")
        if team_members:
            print(f"Team members: {len(team_members)} specified")
        
        # Generate report
        report_data = reporter.generate_team_report(
            group_ids=group_ids,
            team_members=team_members,
            weeks_back=args.weeks
        )
        
        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            
            # Determine format from extension or argument
            if output_path.suffix:
                if output_path.suffix == '.json':
                    format_type = 'json'
                elif output_path.suffix in ['.html', '.htm']:
                    format_type = 'html'
                elif output_path.suffix in ['.md', '.markdown']:
                    format_type = 'markdown'
                else:
                    format_type = args.format
            else:
                format_type = args.format
                # Add appropriate extension
                extensions = {'json': '.json', 'html': '.html', 'markdown': '.md'}
                output_path = output_path.with_suffix(extensions[format_type])
            
            save_report_to_file(report_data, output_path, format_type)
            print(f"{Colors.GREEN}Report saved: {output_path}{Colors.RESET}")
        
        # Send email if requested
        if args.email and not args.dry_run:
            recipients = parse_recipients(args.email)
            cc_recipients = parse_recipients(args.email_cc) if args.email_cc else None
            attachments = args.email_attachments.split(',') if args.email_attachments else None
            
            print(f"{Colors.BOLD}Sending email report to {len(recipients)} recipients...{Colors.RESET}")
            
            email_sender = WeeklyReportEmailSender()
            success = email_sender.send_team_report(
                report_data=report_data,
                recipients=recipients,
                team_name=args.team_name,
                include_charts=not args.no_charts,
                attachments=attachments
            )
            
            if success:
                print(f"{Colors.GREEN}Email report sent successfully!{Colors.RESET}")
            else:
                print(f"{Colors.RED}Failed to send email report. Check configuration and logs.{Colors.RESET}")
                return 1
        
        elif args.email and args.dry_run:
            recipients = parse_recipients(args.email)
            print(f"{Colors.YELLOW}Dry run: Would send email to {len(recipients)} recipients{Colors.RESET}")
        
        # Print summary
        executive_summary = report_data.get('executive_summary', {})
        key_metrics = executive_summary.get('key_metrics', {})
        
        print(f"\n{Colors.BOLD}Report Summary:{Colors.RESET}")
        print(f"  Total Commits: {key_metrics.get('total_commits', 0)}")
        print(f"  Active Contributors: {key_metrics.get('active_contributors', 0)}")
        print(f"  Healthy Projects: {key_metrics.get('healthy_projects', 0)}")
        print(f"  Projects Needing Attention: {key_metrics.get('projects_needing_attention', 0)}")
        
        # Add code and issue metrics if available
        contributors = report_data.get('individual_metrics', {}).get('contributors', {})
        if contributors:
            total_net_lines = sum(c.get('net_lines_changed', 0) for c in contributors.values())
            total_issues_opened = sum(c.get('issues_opened_this_week', 0) for c in contributors.values())
            total_issues_closed = sum(c.get('issues_closed_this_week', 0) for c in contributors.values())
            
            lines_str = f"+{total_net_lines}" if total_net_lines > 0 else str(total_net_lines)
            print(f"  Net Lines Changed: {lines_str}")
            print(f"  Issues Opened: {total_issues_opened}")
            print(f"  Issues Closed: {total_issues_closed}")
            
            if total_issues_opened > 0:
                resolution_rate = (total_issues_closed / total_issues_opened) * 100
                print(f"  Issue Resolution Rate: {resolution_rate:.1f}%")
        
        # Display contributor list
        contributors = report_data.get('individual_metrics', {}).get('contributors', {})
        if contributors and not args.dry_run:
            print(f"\n{Colors.BOLD}Contributors List (Total: {len(contributors)}):{Colors.RESET}")
            sorted_contributors = sorted(contributors.items(), key=lambda x: x[1]['commits'], reverse=True)
            
            # Show all contributors if 56 or less, otherwise top 30
            limit = len(contributors) if len(contributors) <= 56 else 30
            
            for i, (name, stats) in enumerate(sorted_contributors[:limit], 1):
                emails = list(stats.get('emails', set()))[:2]  # Show first 2 emails
                emails_str = f" ({', '.join(emails)})" if emails else ""
                
                usernames = list(stats.get('usernames', set()))
                username_str = f" [@{', @'.join(usernames)}]" if usernames else ""
                
                print(f"  {i:2d}. {name}{emails_str}{username_str}: {stats['commits']} commits, "
                      f"{stats.get('merge_requests_created', 0)} MRs")
                
            if len(contributors) > limit:
                print(f"  ... and {len(contributors) - limit} more contributors")
                
            # Show potential duplicates
            print(f"\n{Colors.YELLOW}Potential duplicate entries to check:{Colors.RESET}")
            email_to_names = defaultdict(set)
            for name, stats in contributors.items():
                for email in stats.get('emails', set()):
                    email_to_names[email].add(name)
            
            duplicates_found = False
            for email, names in email_to_names.items():
                if len(names) > 1:
                    print(f"  {email}: {', '.join(sorted(names))}")
                    duplicates_found = True
            
            if not duplicates_found:
                print("  No obvious duplicates found based on email addresses")
        
        # Display detailed tables
        detailed_tables = report_data.get('detailed_tables', {})
        if detailed_tables and not args.dry_run:
            _display_detailed_tables(detailed_tables)
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user{Colors.RESET}")
        return 1
    except Exception as e:
        logger.error(f"Failed to generate weekly report: {e}", exc_info=True)
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())