#!/usr/bin/env python3
"""Natural Language Issue Creation for GitLab.

This script allows you to describe what you or your team need to do in natural language,
and it will automatically break down the description into tasks and create GitLab issues.
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import GitLabClient
from src.services import NLPIssueService
from src.utils import Config, setup_logging, get_logger
from src.utils.logger import Colors, OperationLogger

logger = get_logger(__name__)


def print_banner():
    """Print a nice banner for the tool."""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}GitLab Natural Language Issue Creator{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")


def print_task_preview(tasks):
    """Print a preview of extracted tasks."""
    print(f"\n{Colors.BOLD}📋 Extracted Tasks ({len(tasks)} total):{Colors.RESET}")
    print("-" * 60)
    
    for i, task in enumerate(tasks, 1):
        # Task header
        print(f"\n{Colors.CYAN}Task {i}:{Colors.RESET} {Colors.BOLD}{task.title}{Colors.RESET}")
        
        # Task details
        print(f"  📌 Type: {task.task_type.value}")
        print(f"  🎯 Priority: {task.priority.value}")
        print(f"  📏 Size: {task.size.value}")
        print(f"  🏷️  Labels: {', '.join(task.labels)}")
        
        if task.dependencies:
            print(f"  🔗 Dependencies: {', '.join(task.dependencies)}")
        
        if task.technologies:
            print(f"  💻 Technologies: {', '.join(task.technologies)}")
        
        if task.confidence_score < 1.0:
            print(f"  🎲 Confidence: {task.confidence_score:.0%}")
        
        # Description preview
        desc_lines = task.description.split('\n')
        print(f"  📝 Description: {desc_lines[0][:60]}...")


def print_results(result):
    """Print the processing results."""
    print(f"\n{Colors.BOLD}📊 Processing Summary:{Colors.RESET}")
    print("-" * 60)
    
    if result.completed_at:
        duration = (result.completed_at - result.started_at).total_seconds()
        print(f"⏱️  Processing time: {duration:.2f} seconds")
    
    print(f"📄 Original text: {len(result.original_description)} characters")
    print(f"✅ Tasks extracted: {result.total_tasks}")
    
    if result.created_issues:
        print(f"{Colors.GREEN}✓ Issues created: {result.tasks_created}{Colors.RESET}")
        if result.tasks_failed > 0:
            print(f"{Colors.RED}✗ Issues failed: {result.tasks_failed}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Created Issues:{Colors.RESET}")
        for issue_result in result.created_issues:
            if issue_result.get('success'):
                issue = issue_result.get('issue')
                if issue:
                    print(f"  {Colors.GREEN}✓{Colors.RESET} #{issue.iid}: {issue.title}")
                    print(f"    🔗 {issue.web_url}")
                elif issue_result.get('preview'):
                    task = issue_result.get('task')
                    print(f"  {Colors.YELLOW}👁️{Colors.RESET} {task.title} (preview)")
            else:
                task = issue_result.get('task')
                error = issue_result.get('error', 'Unknown error')
                print(f"  {Colors.RED}✗{Colors.RESET} {task.title}: {error}")


def load_description_from_file(file_path: str) -> str:
    """Load description from a file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def get_project_context(client: GitLabClient, project_id: str) -> Dict[str, Any]:
    """Get project context for enhanced task extraction."""
    context = {}
    
    try:
        # Get existing issues (last 50)
        logger.info("Fetching project context...")
        issues = list(client._paginated_get(
            f"projects/{project_id}/issues",
            params={"state": "opened", "per_page": 50}
        ))
        context['existing_issues'] = issues
        
        # Get project members
        members = list(client._paginated_get(
            f"projects/{project_id}/members"
        ))
        context['team_members'] = members
        
        # Get active milestones
        milestones = list(client._paginated_get(
            f"projects/{project_id}/milestones",
            params={"state": "active"}
        ))
        context['milestones'] = milestones
        
        logger.info(f"Context loaded: {len(issues)} issues, {len(members)} members, {len(milestones)} milestones")
        
    except Exception as e:
        logger.warning(f"Failed to load some context: {e}")
    
    return context


def interactive_mode(nlp_service: NLPIssueService, project_id: str, project_name: str):
    """Run in interactive mode."""
    print(f"\n{Colors.BOLD}Project:{Colors.RESET} {project_name}")
    print(f"\n{Colors.CYAN}Describe what you or your team need to do:{Colors.RESET}")
    print("(Type 'END' on a new line when finished, or 'QUIT' to exit)\n")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'END':
                break
            elif line.strip().upper() == 'QUIT':
                print("\nExiting...")
                return
            lines.append(line)
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return
    
    description = '\n'.join(lines).strip()
    
    if not description:
        print(f"{Colors.RED}No description provided{Colors.RESET}")
        return
    
    # Get context
    print(f"\n{Colors.CYAN}Loading project context...{Colors.RESET}")
    context = get_project_context(nlp_service.gitlab, project_id)
    
    # Process description
    print(f"\n{Colors.CYAN}Analyzing your description...{Colors.RESET}")
    result = nlp_service.process_description(
        project_id,
        description,
        context=context,
        dry_run=True  # Always preview first in interactive mode
    )
    
    # Show preview
    print_task_preview(result.extracted_tasks)
    
    # Ask for confirmation
    print(f"\n{Colors.YELLOW}Do you want to create these issues? (yes/no):{Colors.RESET} ", end='')
    confirm = input().strip().lower()
    
    if confirm in ['yes', 'y']:
        print(f"\n{Colors.CYAN}Creating issues...{Colors.RESET}")
        result = nlp_service.process_description(
            project_id,
            description,
            context=context,
            dry_run=False
        )
        print_results(result)
    else:
        print("\nIssue creation cancelled.")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Create GitLab issues from natural language descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (recommended)
  %(prog)s myproject --interactive
  
  # Describe directly
  %(prog)s myproject -d "We need to implement user authentication with OAuth support"
  
  # Load from file
  %(prog)s myproject -f requirements.txt
  
  # Preview without creating
  %(prog)s myproject -d "Fix the login bug" --dry-run
  
  # With AI enhancement (requires API key)
  %(prog)s myproject -d "Build a REST API" --use-ai
"""
    )
    
    # Required arguments
    parser.add_argument(
        'project',
        help='GitLab project ID or path (e.g., "123" or "group/project")'
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '-d', '--description',
        help='Natural language description of tasks'
    )
    input_group.add_argument(
        '-f', '--file',
        help='Read description from file'
    )
    input_group.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Interactive mode (recommended)'
    )
    
    # Processing options
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview tasks without creating issues'
    )
    parser.add_argument(
        '--no-context',
        action='store_true',
        help='Skip loading project context (faster but less accurate)'
    )
    parser.add_argument(
        '--use-ai',
        action='store_true',
        help='Use AI for enhanced task extraction (requires API key)'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        help='Save results to file (JSON format)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    # Configuration
    parser.add_argument(
        '--config',
        help='Configuration file path'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Print banner unless quiet
    if not args.quiet:
        print_banner()
    
    # Load configuration
    config = Config(args.config)
    
    # Setup logging
    setup_logging(
        config.get_log_config(),
        console_level=args.log_level if not args.quiet else 'ERROR'
    )
    
    try:
        # Validate configuration
        config.validate()
        
        # Create GitLab client
        gitlab_config = config.get_gitlab_config()
        client = GitLabClient(
            url=gitlab_config['url'],
            token=gitlab_config['token'],
            config=gitlab_config
        )
        
        # Create NLP service
        ai_client = None
        if args.use_ai:
            # Try to create AI client
            try:
                from src.services.ai_service import create_ai_service
                
                # Determine AI provider (could be made configurable)
                ai_provider = os.getenv('AI_PROVIDER', 'openai')
                ai_client = create_ai_service(ai_provider)
                
                if not args.quiet:
                    print(f"{Colors.GREEN}✓ AI service enabled:{Colors.RESET} {ai_provider}\n")
            except Exception as e:
                logger.warning(f"Failed to initialize AI service: {e}")
                if not args.quiet:
                    print(f"{Colors.YELLOW}⚠ AI service unavailable:{Colors.RESET} {e}")
                    print("Falling back to pattern-based extraction\n")
        
        nlp_service = NLPIssueService(client, ai_client)
        
        # Get project info
        try:
            project = client.get_project(args.project)
            project_id = project['id']
            project_name = project['name_with_namespace']
            
            if not args.quiet:
                print(f"{Colors.GREEN}✓ Connected to project:{Colors.RESET} {project_name}\n")
        except Exception as e:
            logger.error(f"Failed to access project: {e}")
            return 1
        
        # Handle different modes
        if args.interactive:
            interactive_mode(nlp_service, project_id, project_name)
        
        elif args.description or args.file:
            # Get description
            if args.description:
                description = args.description
            else:
                description = load_description_from_file(args.file)
            
            # Get context unless disabled
            context = None
            if not args.no_context:
                if not args.quiet:
                    print(f"{Colors.CYAN}Loading project context...{Colors.RESET}")
                context = get_project_context(client, project_id)
            
            # Process description
            if not args.quiet:
                print(f"{Colors.CYAN}Processing description...{Colors.RESET}")
            
            with OperationLogger(logger, "process NLP description"):
                result = nlp_service.process_description(
                    project_id,
                    description,
                    context=context,
                    dry_run=args.dry_run,
                    use_ai=args.use_ai
                )
            
            # Show results
            if not args.quiet:
                if args.dry_run:
                    print_task_preview(result.extracted_tasks)
                print_results(result)
            
            # Save output if requested
            if args.output:
                output_data = {
                    'timestamp': datetime.now().isoformat(),
                    'project': project_name,
                    'original_description': result.original_description,
                    'extracted_tasks': [
                        {
                            'title': task.title,
                            'type': task.task_type.value,
                            'priority': task.priority.value,
                            'size': task.size.value,
                            'labels': task.labels,
                            'dependencies': task.dependencies
                        }
                        for task in result.extracted_tasks
                    ],
                    'results': [
                        {
                            'success': r.get('success'),
                            'message': r.get('message'),
                            'issue_url': r.get('issue', {}).get('web_url') if r.get('issue') else None
                        }
                        for r in result.created_issues
                    ],
                    'summary': {
                        'total_tasks': result.total_tasks,
                        'created': result.tasks_created,
                        'failed': result.tasks_failed
                    }
                }
                
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2)
                
                if not args.quiet:
                    print(f"\n{Colors.GREEN}✓ Results saved to:{Colors.RESET} {args.output}")
        
        else:
            # No input provided, show help
            parser.print_help()
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        if not args.quiet:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())