"""
Help System for GitLab Tools CLI.

Provides contextual help and command documentation.
"""

from typing import List, Optional
from .command_parser import CommandParser
from .command_registry import CommandPattern


class HelpSystem:
    """Provides help and documentation for CLI commands."""
    
    def __init__(self, command_parser: CommandParser):
        """Initialize the help system."""
        self.command_parser = command_parser
    
    def show_general_help(self):
        """Show general help information."""
        help_text = """
📚 GitLab Tools CLI Help

Available Commands:
"""
        
        # Get all unique commands
        commands = self.command_parser.get_all_commands()
        seen_scripts = set()
        
        for command in commands:
            if command.script_path not in seen_scripts:
                seen_scripts.add(command.script_path)
                print(f"  🔹 {command.description}")
                
                # Show first example
                if command.examples:
                    print(f"     Example: {command.examples[0]}")
                print()
        
        print("""
Special Commands:
  🔹 help [command]     - Show help for a specific command
  🔹 history           - Show command execution history
  🔹 dry-run          - Toggle dry-run mode
  🔹 status           - Show current status
  🔹 clear            - Clear screen
  🔹 exit             - Exit the CLI

Tips:
  💡 Use Tab for auto-completion
  💡 Use ↑/↓ arrows for command history
  💡 Use Ctrl+C to cancel running commands
  💡 Type 'help <command>' for detailed help on specific commands

Examples:
  > create issues for project 123
  > generate dashboard for groups 1,2,3
  > weekly report for group 5 email to team@company.com
  > rename branches in AI-ML-Services from trunk to main
  > help create
""")
    
    def show_command_help(self, command_name: str):
        """
        Show help for a specific command.
        
        Args:
            command_name: Name of the command to show help for
        """
        # Find the command
        command_info = self.command_parser.get_command_help(command_name)
        
        if not command_info:
            print(f"❌ No help found for '{command_name}'")
            
            # Show suggestions
            suggestions = self.command_parser.get_suggestions(command_name)
            if suggestions:
                print("\n💡 Did you mean:")
                for suggestion in suggestions[:5]:
                    print(f"  • {suggestion}")
            
            print("\nType 'help' to see all available commands.")
            return
        
        # Show detailed help
        self._show_detailed_command_help(command_info)
    
    def _show_detailed_command_help(self, command: CommandPattern):
        """Show detailed help for a specific command."""
        print(f"\n📖 Help for: {command.description}")
        print("=" * 60)
        
        # Script information
        print(f"Script: {command.script_path}")
        
        # Aliases
        if command.aliases:
            print(f"Aliases: {', '.join(command.aliases)}")
        
        # Parameters
        if command.required_params or command.optional_params:
            print("\nParameters:")
            
            if command.required_params:
                print("  Required:")
                for param in command.required_params:
                    print(f"    • {param}")
            
            if command.optional_params:
                print("  Optional:")
                for param in command.optional_params:
                    print(f"    • {param}")
        
        # Examples
        if command.examples:
            print("\nExamples:")
            for i, example in enumerate(command.examples, 1):
                print(f"  {i}. {example}")
        
        # Usage tips
        self._show_usage_tips(command)
        
        print()
    
    def _show_usage_tips(self, command: CommandPattern):
        """Show usage tips for a command."""
        script_name = command.script_path.split('/')[-1]
        
        tips = {
            'create_issues.py': [
                "💡 Issues are created from markdown files in the 'issues' folder by default",
                "💡 Use project ID for specific project, or omit to use default from config",
                "💡 Each .md file becomes a separate issue with title from filename"
            ],
            'rename_branches.py': [
                "💡 Specify group name to rename branches across all projects in group",
                "💡 Use 'from X to Y' to specify exact branch names",
                "💡 Common usage: 'rename branches from master to main'"
            ],
            'generate_executive_dashboard.py': [
                "💡 Generates HTML dashboard with project metrics and analytics",
                "💡 Use group IDs to focus on specific teams or departments",
                "💡 Dashboard includes commit activity, merge requests, and issue stats"
            ],
            'weekly_reports.py': [
                "💡 Generates productivity reports for specified time period",
                "💡 Add 'email to <address>' to automatically send the report",
                "💡 Group IDs help focus the report on specific teams"
            ],
            'analyze_projects.py': [
                "💡 Provides detailed analysis of project health and activity",
                "💡 Use multiple project IDs separated by commas",
                "💡 Analysis includes code quality metrics and team productivity"
            ],
            'export_analytics.py': [
                "💡 Exports raw analytics data for external processing",
                "💡 Data includes commits, issues, merge requests, and user activity",
                "💡 Export format is JSON by default"
            ],
            'sync_issues.py': [
                "💡 Synchronizes local issue files with GitLab issues",
                "💡 Updates existing issues and creates new ones as needed",
                "💡 Maintains bidirectional sync between local files and GitLab"
            ],
            'send_report_email.py': [
                "💡 Sends generated reports via email",
                "💡 Supports multiple recipients separated by commas",
                "💡 Automatically detects report format based on file extension"
            ]
        }
        
        if script_name in tips:
            print("\nUsage Tips:")
            for tip in tips[script_name]:
                print(f"  {tip}")
    
    def show_interactive_tutorial(self):
        """Show an interactive tutorial for new users."""
        print("""
🎓 GitLab Tools CLI Tutorial

Welcome to the GitLab Tools CLI! This tutorial will show you the basics.

Step 1: Basic Commands
Try typing: help
This shows all available commands.

Step 2: Create Issues
Try typing: create issues for project 123
This creates GitLab issues from markdown files.

Step 3: Generate Reports  
Try typing: weekly report for groups 1,2,3
This generates a productivity report.

Step 4: Get Command Help
Try typing: help create
This shows detailed help for the create command.

Step 5: Use Tab Completion
Start typing 'creat' and press Tab - it will auto-complete!

Step 6: Command History
Use ↑ and ↓ arrows to navigate through previous commands.

Step 7: Dry Run Mode
Type: dry-run
This toggles dry-run mode to test commands without executing them.

🎉 You're ready to use the GitLab Tools CLI!
Type 'exit' when you're done.
""")
    
    def show_command_reference(self):
        """Show a comprehensive command reference."""
        print("\n📚 Command Reference")
        print("=" * 60)
        
        commands = self.command_parser.get_all_commands()
        seen_scripts = set()
        
        for command in commands:
            if command.script_path not in seen_scripts:
                seen_scripts.add(command.script_path)
                print(f"\n{command.description}")
                print("-" * len(command.description))
                
                # Pattern
                print(f"Pattern: {command.pattern}")
                
                # Examples
                if command.examples:
                    print("Examples:")
                    for example in command.examples:
                        print(f"  • {example}")
                
                # Aliases
                if command.aliases:
                    print(f"Aliases: {', '.join(command.aliases)}")
    
    def get_command_documentation(self, command_name: str) -> Optional[str]:
        """
        Get formatted documentation for a command.
        
        Args:
            command_name: Name of the command
            
        Returns:
            Formatted documentation string or None
        """
        command_info = self.command_parser.get_command_help(command_name)
        
        if not command_info:
            return None
        
        lines = []
        lines.append(f"Command: {command_info.description}")
        lines.append(f"Script: {command_info.script_path}")
        
        if command_info.aliases:
            lines.append(f"Aliases: {', '.join(command_info.aliases)}")
        
        if command_info.examples:
            lines.append("Examples:")
            for example in command_info.examples:
                lines.append(f"  {example}")
        
        return '\n'.join(lines) 