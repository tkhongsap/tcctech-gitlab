#!/usr/bin/env python3
"""
GitLab Tools Menu Interface - Simple numbered menu for GitLab operations.

This provides an alternative to the command-line interface with a simple
numbered menu system.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import get_logger
from src.utils.config import Config

logger = get_logger(__name__)


class Colors:
    """ANSI color codes matching Claude Code's theme."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Primary colors
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    
    # Status colors
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    
    # Muted colors
    GRAY = '\033[90m'
    DARK_GRAY = '\033[37m'
    
    @classmethod
    def disable_if_no_color(cls):
        """Disable colors if stdout is not a TTY."""
        if not sys.stdout.isatty():
            for attr in dir(cls):
                if not attr.startswith('_') and attr != 'disable_if_no_color':
                    setattr(cls, attr, '')


class GitLabMenu:
    """Simple menu interface for GitLab tools."""
    
    def __init__(self):
        """Initialize the menu system."""
        self.config = Config()
        self.dry_run = False
        
        # Initialize colors
        Colors.disable_if_no_color()
        
        # Define menu options with emojis, descriptions, and handlers
        self.menu_options = [
            ("🔄", "Rename Branches", "Rename branches across multiple projects in groups", self.rename_branches),
            ("📊", "Generate Executive Dashboard", "Create HTML dashboards with analytics and metrics", self.generate_dashboard),
            ("📅", "Generate Weekly Report", "Create team productivity reports for weekly syncs", self.weekly_report),
            ("📧", "Send Report Email", "Email HTML reports to team members", self.send_email),
            ("📝", "Sync Issues from Markdown", "Create GitLab issues from markdown files in issues/ folder", self.sync_issues),
            ("🎯", "Create Issues", "Create GitLab issues interactively or from templates", self.create_issues),
            ("📈", "Analyze Projects", "Deep analysis of projects and groups with insights", self.analyze_projects),
            ("💾", "Export Analytics", "Export project data to Excel or JSON formats", self.export_analytics),
            ("📋", "Generate Code Changes Report", "Analyze code changes with lines added/removed metrics", self.code_changes_report),
            ("✨ ", "Generate and Send Report", "Generate and email code changes report in one step", self.generate_and_send),
            ("🔧", "Toggle Dry-Run Mode", "Enable/disable dry-run mode for safe testing", self.toggle_dry_run),
            ("👋", "Exit", "Exit the program", self.exit_program)
        ]
    
    def clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Display the menu header."""
        border = "═" * 64
        print(f"\n{Colors.CYAN}{border}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.WHITE} GitLab Tools Menu Interface{Colors.RESET}")
        print(f"{Colors.CYAN}{border}{Colors.RESET}")
        if self.dry_run:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  DRY-RUN MODE ENABLED{Colors.RESET} {Colors.GRAY}- No changes will be made{Colors.RESET}")
            print(f"{Colors.CYAN}{border}{Colors.RESET}")
    
    def show_menu(self):
        """Display the menu options."""
        print(f"\n{Colors.WHITE}Please select an option:{Colors.RESET}\n")
        for idx, (emoji, name, desc, _) in enumerate(self.menu_options, 1):
            print(f"  {Colors.BLUE}{Colors.BOLD}{idx:2d}.{Colors.RESET} {emoji} {Colors.WHITE}{name}{Colors.RESET}")
            print(f"      {Colors.GRAY}→ {desc}{Colors.RESET}\n")
        print(f"{Colors.CYAN}{'─' * 64}{Colors.RESET}")
    
    def get_choice(self) -> Optional[int]:
        """Get user's menu choice."""
        try:
            choice = input(f"\n{Colors.CYAN}Enter your choice (1-{len(self.menu_options)}): {Colors.RESET}")
            choice_num = int(choice)
            if 1 <= choice_num <= len(self.menu_options):
                return choice_num
            else:
                print(f"{Colors.RED}❌ Invalid choice. Please enter a number between 1 and {len(self.menu_options)}.{Colors.RESET}")
                return None
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input. Please enter a number.{Colors.RESET}")
            return None
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
            sys.exit(0)
    
    def run_script(self, script_path: str, args: List[str]):
        """Run a Python script with arguments."""
        cmd = [sys.executable, script_path] + args
        
        if self.dry_run and '--dry-run' not in args:
            cmd.append('--dry-run')
        
        print(f"\n{Colors.CYAN}🔧 Executing:{Colors.RESET} {Colors.GRAY}{' '.join(cmd)}{Colors.RESET}")
        print(f"{Colors.CYAN}{'─' * 64}{Colors.RESET}")
        
        try:
            result = subprocess.run(cmd, check=False)
            if result.returncode == 0:
                print(f"\n{Colors.GREEN}✅ Command completed successfully!{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}❌ Command failed with exit code: {result.returncode}{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏹️  Command cancelled by user{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}❌ Error running command: {e}{Colors.RESET}")
        
        input(f"\n{Colors.GRAY}Press Enter to continue...{Colors.RESET}")
    
    def get_input(self, prompt: str, required: bool = True) -> Optional[str]:
        """Get input from user with optional requirement."""
        try:
            value = input(f"{Colors.CYAN}{prompt}{Colors.RESET}").strip()
            if required and not value:
                print(f"{Colors.RED}❌ This field is required.{Colors.RESET}")
                return None
            return value if value else None
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏹️  Cancelled{Colors.RESET}")
            return None
    
    def rename_branches(self):
        """Handle branch renaming."""
        print(f"\n{Colors.BOLD}{Colors.WHITE}🔄 Rename Branches{Colors.RESET}")
        print(f"{Colors.GRAY}{'─' * 40}{Colors.RESET}")
        
        groups = self.get_input("Enter group names (comma-separated, or press Enter for all): ", required=False)
        old_branch = self.get_input("Enter old branch name (default: trunk): ", required=False) or "trunk"
        new_branch = self.get_input("Enter new branch name (default: main): ", required=False) or "main"
        
        args = []
        if groups:
            args.extend(['--groups'] + groups.split(','))
        args.extend(['--old-branch', old_branch, '--new-branch', new_branch])
        
        self.run_script('scripts/rename_branches.py', args)
    
    def generate_dashboard(self):
        """Generate executive dashboard."""
        print(f"\n{Colors.BOLD}{Colors.WHITE}📊 Generate Executive Dashboard{Colors.RESET}")
        print(f"{Colors.GRAY}{'─' * 40}{Colors.RESET}")
        print(f"\n{Colors.GRAY}Available Group IDs:{Colors.RESET}")
        print(f"  {Colors.BLUE}1721{Colors.RESET} = AI-ML-Services")
        print(f"  {Colors.BLUE}1267{Colors.RESET} = Research Repos")
        print(f"  {Colors.BLUE}1269{Colors.RESET} = Internal Services")
        
        groups = self.get_input("\nEnter group IDs (comma-separated): ")
        if not groups:
            return
        
        output = self.get_input("Enter output filename (default: dashboard.html): ", required=False) or "dashboard.html"
        days = self.get_input("Enter number of days to analyze (default: 30): ", required=False) or "30"
        team_name = self.get_input("Enter team name (optional): ", required=False)
        
        args = ['--groups', groups, '--output', output, '--days', days]
        if team_name:
            args.extend(['--team-name', team_name])
        
        self.run_script('scripts/generate_executive_dashboard.py', args)
    
    def weekly_report(self):
        """Generate weekly report."""
        print(f"\n{Colors.BOLD}{Colors.WHITE}📅 Generate Weekly Report{Colors.RESET}")
        print(f"{Colors.GRAY}{'─' * 40}{Colors.RESET}")
        print(f"\n{Colors.GRAY}Available Group IDs:{Colors.RESET}")
        print(f"  {Colors.BLUE}1721{Colors.RESET} = AI-ML-Services")
        print(f"  {Colors.BLUE}1267{Colors.RESET} = Research Repos")
        print(f"  {Colors.BLUE}1269{Colors.RESET} = Internal Services")
        
        groups = self.get_input("\nEnter group IDs (comma-separated): ")
        if not groups:
            return
        
        output = self.get_input("Enter output filename (optional): ", required=False)
        email = self.get_input("Enter email recipients (comma-separated, default: totrakool.k@thaibev.com): ", required=False) or "totrakool.k@thaibev.com"
        weeks = self.get_input("Enter number of weeks (default: 1): ", required=False) or "1"
        team = self.get_input("Enter team members (comma-separated, optional): ", required=False)
        
        args = ['--groups', groups, '--weeks', weeks]
        if output:
            args.extend(['--output', output])
        if email:
            args.extend(['--email', email])
        if team:
            args.extend(['--team', team])
        
        self.run_script('scripts/weekly_reports.py', args)
    
    def send_email(self):
        """Send report via email."""
        print("\n📧 Send Report Email")
        print("-" * 40)
        
        report_file = self.get_input("Enter report file path: ")
        if not report_file:
            return
        
        recipients = self.get_input("Enter email recipients (comma-separated): ")
        if not recipients:
            return
        
        subject = self.get_input("Enter email subject: ")
        if not subject:
            return
        
        args = [report_file, recipients, subject]
        self.run_script('scripts/send_report_email.py', args)
    
    def sync_issues(self):
        """Sync issues from markdown files."""
        print("\n📝 Sync Issues from Markdown")
        print("-" * 40)
        
        project_id = self.get_input("Enter project ID: ")
        if not project_id:
            return
        
        use_api = input("Use API instead of curl? (y/N): ").lower() == 'y'
        
        args = [project_id]
        if use_api:
            args.append('--use-api')
        
        self.run_script('scripts/sync_issues.py', args)
    
    def create_issues(self):
        """Create GitLab issues."""
        print("\n🎯 Create Issues")
        print("-" * 40)
        
        project = self.get_input("Enter project name or ID: ")
        if not project:
            return
        
        print("\nOptions:")
        print("1. Interactive mode (default)")
        print("2. Create from template")
        print("3. Import from CSV")
        
        mode = self.get_input("\nSelect mode (1-3, default: 1): ", required=False) or "1"
        
        args = [project]
        
        if mode == "2":
            template = self.get_input("Enter template name (e.g., feature, bug, epic): ")
            if template:
                args.extend(['--template', template])
        elif mode == "3":
            csv_file = self.get_input("Enter CSV file path: ")
            if csv_file:
                args.extend(['--import', csv_file])
        
        self.run_script('scripts/create_issues.py', args)
    
    def analyze_projects(self):
        """Analyze projects."""
        print("\n📈 Analyze Projects")
        print("-" * 40)
        
        print("\nAnalysis types:")
        print("1. Single project")
        print("2. Entire group")
        print("3. Compare multiple projects")
        
        analysis_type = self.get_input("\nSelect type (1-3): ")
        if not analysis_type or analysis_type not in ['1', '2', '3']:
            return
        
        if analysis_type == "1":
            project_id = self.get_input("Enter project ID: ")
            if not project_id:
                return
            args = ['project', project_id]
        elif analysis_type == "2":
            group_id = self.get_input("Enter group ID: ")
            if not group_id:
                return
            args = ['group', group_id]
        else:
            project_ids = self.get_input("Enter project IDs (comma-separated): ")
            if not project_ids:
                return
            args = ['compare', project_ids]
        
        output = self.get_input("Enter output filename (optional): ", required=False)
        if output:
            args.extend(['--output', output])
        
        self.run_script('scripts/analyze_projects.py', args)
    
    def export_analytics(self):
        """Export analytics to Excel."""
        print("\n📊 Export Analytics")
        print("-" * 40)
        
        projects = self.get_input("Enter project IDs (comma-separated): ")
        if not projects:
            return
        
        output = self.get_input("Enter output filename (default: analytics.xlsx): ", required=False) or "analytics.xlsx"
        
        args = ['projects', projects, '--output', output]
        self.run_script('scripts/export_analytics.py', args)
    
    def code_changes_report(self):
        """Generate code changes report."""
        print("\n📝 Generate Code Changes Report")
        print("-" * 40)
        
        groups = self.get_input("Enter group IDs (comma-separated): ")
        if not groups:
            return
        
        output = self.get_input("Enter output filename (default: code_changes.html): ", required=False) or "code_changes.html"
        days = self.get_input("Enter number of days (default: 30): ", required=False) or "30"
        
        args = ['--groups', groups, '--output', output, '--days', days]
        self.run_script('scripts/generate_code_changes_report.py', args)
    
    def generate_and_send(self):
        """Generate and send report."""
        print("\n📧 Generate and Send Report")
        print("-" * 40)
        
        groups = self.get_input("Enter group IDs (comma-separated): ")
        if not groups:
            return
        
        recipients = self.get_input("Enter email recipients (comma-separated): ")
        if not recipients:
            return
        
        subject = self.get_input("Enter email subject (optional): ", required=False)
        days = self.get_input("Enter number of days (default: 7): ", required=False) or "7"
        
        args = ['--groups', groups, '--recipients', recipients, '--days', days]
        if subject:
            args.extend(['--subject', subject])
        
        self.run_script('scripts/generate_and_send_report.py', args)
    
    def toggle_dry_run(self):
        """Toggle dry-run mode."""
        self.dry_run = not self.dry_run
        status = f"{Colors.GREEN}enabled{Colors.RESET}" if self.dry_run else f"{Colors.RED}disabled{Colors.RESET}"
        print(f"\n{Colors.BOLD}{Colors.WHITE}🔧 Dry-run mode {status}{Colors.RESET}")
        input(f"\n{Colors.GRAY}Press Enter to continue...{Colors.RESET}")
    
    def exit_program(self):
        """Exit the program."""
        print(f"\n{Colors.YELLOW}👋 Goodbye!{Colors.RESET}")
        sys.exit(0)
    
    def run(self):
        """Run the menu interface."""
        while True:
            self.clear_screen()
            self.show_header()
            self.show_menu()
            
            choice = self.get_choice()
            if choice is not None:
                _, _, _, handler = self.menu_options[choice - 1]
                handler()


def main():
    """Main entry point."""
    try:
        menu = GitLabMenu()
        menu.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())