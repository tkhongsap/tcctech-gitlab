#!/usr/bin/env python3
"""Generate analytics reports for GitLab projects and groups."""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import GitLabClient
from src.services import GitLabAnalytics
from src.utils import Config, setup_logging, get_logger
from src.utils.logger import Colors

logger = get_logger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate analytics reports for GitLab projects"
    )
    
    # Target selection
    target_group = parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        '--project', '-p',
        help='Project ID or path to analyze'
    )
    target_group.add_argument(
        '--group', '-g',
        help='Group ID or name to analyze'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['markdown', 'json', 'text'],
        default='markdown',
        help='Output format (default: markdown)'
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
        
        # Create GitLab client
        gitlab_config = config.get_gitlab_config()
        client = GitLabClient(
            url=gitlab_config['url'],
            token=gitlab_config['token'],
            config=gitlab_config
        )
        
        # Create analytics service
        analytics = GitLabAnalytics(client)
        
        # Get metrics
        print(f"{Colors.BOLD}Generating analytics report...{Colors.RESET}")
        
        if args.project:
            logger.info(f"Analyzing project: {args.project}")
            metrics = analytics.get_project_metrics(args.project)
        else:
            logger.info(f"Analyzing group: {args.group}")
            
            # Find group by name if needed
            if not args.group.isdigit():
                group = client.search_group_by_name(args.group)
                if not group:
                    print(f"{Colors.RED}Error: Group '{args.group}' not found{Colors.RESET}")
                    return 1
                group_id = group['id']
            else:
                group_id = args.group
            
            metrics = analytics.get_group_metrics(group_id)
        
        # Generate report
        report = analytics.generate_summary_report(metrics, format=args.format)
        
        # Output report
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(report)
            
            print(f"{Colors.GREEN}Report saved to: {output_path}{Colors.RESET}")
        else:
            print(f"\n{report}")
        
        # Summary statistics
        if args.project and args.format != 'json':
            print(f"\n{Colors.BOLD}Quick Summary:{Colors.RESET}")
            print(f"- Commits (30 days): {metrics['commits']['total']}")
            print(f"- Active branches: {metrics['branches']['active']}")
            print(f"- Open issues: {metrics['issues']['open']}")
            print(f"- Contributors: {metrics['contributors']['total']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to generate analytics: {e}", exc_info=True)
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())