#!/usr/bin/env python3
"""Enhanced branch rename script with dry-run mode and progress tracking."""

import sys
import argparse
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api import GitLabClient
from src.utils import Config, setup_logging, get_logger, ProgressTracker, progress_context
from src.utils.logger import OperationLogger, Colors


logger = get_logger(__name__)


class BranchRenamer:
    """Handles branch renaming operations across multiple projects."""
    
    def __init__(self, client: GitLabClient, config: Config):
        """Initialize branch renamer.
        
        Args:
            client: GitLab API client
            config: Configuration instance
        """
        self.client = client
        self.config = config
        self.dry_run = config.is_dry_run()
        self.stats = {
            'total': 0,
            'renamed': 0,
            'skipped': 0,
            'failed': 0
        }
    
    def rename_branch_in_project(
        self, 
        project: dict, 
        old_branch: str, 
        new_branch: str
    ) -> bool:
        """Rename branch in a single project.
        
        Args:
            project: Project data
            old_branch: Current branch name
            new_branch: New branch name
            
        Returns:
            True if successful or skipped, False if failed
        """
        project_name = project['name']
        project_id = project['id']
        
        with OperationLogger(logger, "branch rename", project=project_name):
            try:
                # Check if old branch exists
                if not self.client.branch_exists(project_id, old_branch):
                    logger.info(f"Branch '{old_branch}' not found - skipping")
                    self.stats['skipped'] += 1
                    return True
                
                # Check if new branch already exists
                if self.client.branch_exists(project_id, new_branch):
                    logger.info(f"Branch '{new_branch}' already exists - skipping")
                    self.stats['skipped'] += 1
                    return True
                
                # Check if it's a protected branch
                if self.config.get('branch_operations.skip_protected', True):
                    branch_info = self.client.get_branch(project_id, old_branch)
                    if branch_info.get('protected', False):
                        logger.warning(f"Branch '{old_branch}' is protected - skipping")
                        self.stats['skipped'] += 1
                        return True
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would rename '{old_branch}' to '{new_branch}'")
                    self.stats['renamed'] += 1
                    return True
                
                # Perform the rename
                success = self.client.rename_branch(
                    project_id, 
                    old_branch, 
                    new_branch,
                    update_default=True
                )
                
                if success:
                    logger.info(f"Successfully renamed '{old_branch}' to '{new_branch}'")
                    self.stats['renamed'] += 1
                    return True
                else:
                    logger.error(f"Failed to rename branch")
                    self.stats['failed'] += 1
                    return False
                    
            except Exception as e:
                logger.error(f"Error processing project '{project_name}': {e}")
                self.stats['failed'] += 1
                return False
    
    def process_group(
        self, 
        group_name: str, 
        old_branch: str, 
        new_branch: str
    ) -> bool:
        """Process all projects in a group.
        
        Args:
            group_name: Name of the group
            old_branch: Current branch name
            new_branch: New branch name
            
        Returns:
            True if any projects were processed successfully
        """
        logger.info(f"Processing group: {group_name}")
        
        # Find group
        group = self.client.search_group_by_name(group_name)
        if not group:
            logger.error(f"Group '{group_name}' not found")
            return False
        
        # Get group configuration
        group_config = None
        for g in self.config.get_groups():
            if g['name'] == group_name:
                group_config = g
                break
        
        # Get projects
        filters = {}
        if group_config and 'filters' in group_config:
            if group_config['filters'].get('exclude_archived'):
                filters['archived'] = False
        
        with progress_context(f"Fetching projects from {group_name}"):
            projects = list(self.client.get_projects(
                group_id=group['id'],
                include_subgroups=True,
                **filters
            ))
        
        if not projects:
            logger.warning(f"No projects found in group '{group_name}'")
            return False
        
        logger.info(f"Found {len(projects)} projects in group '{group_name}'")
        
        # Process each project with progress tracking
        success_count = 0
        show_progress = self.config.get('features.show_progress', True) and not logger.isEnabledFor(logging.DEBUG)
        
        progress_tracker = ProgressTracker(
            enumerate(projects, 1),
            total=len(projects),
            description=f"Processing {group_name}",
            unit="projects",
            disable=not show_progress
        )
        
        for i, project in progress_tracker:
            self.stats['total'] += 1
            if not show_progress:
                logger.info(f"\n[{i}/{len(projects)}] Processing: {project['name']}")
            
            if self.rename_branch_in_project(project, old_branch, new_branch):
                success_count += 1
        
        return success_count > 0
    
    def print_summary(self):
        """Print operation summary."""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Operation Summary{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
        
        if self.dry_run:
            print(f"{Colors.YELLOW}DRY RUN MODE - No actual changes were made{Colors.RESET}")
        
        print(f"Total projects processed: {self.stats['total']}")
        print(f"{Colors.GREEN}Successfully renamed: {self.stats['renamed']}{Colors.RESET}")
        print(f"{Colors.YELLOW}Skipped: {self.stats['skipped']}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.stats['failed']}{Colors.RESET}")
        
        if self.stats['failed'] > 0:
            print(f"\n{Colors.RED}Warning: Some operations failed. Check the logs for details.{Colors.RESET}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Rename branches across multiple GitLab projects"
    )
    parser.add_argument(
        '--old-branch', '-o',
        default='trunk',
        help='Current branch name (default: trunk)'
    )
    parser.add_argument(
        '--new-branch', '-n',
        default='main',
        help='New branch name (default: main)'
    )
    parser.add_argument(
        '--groups', '-g',
        nargs='+',
        help='Groups to process (overrides config file)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making them'
    )
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
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    # Override dry-run if specified
    if args.dry_run:
        import os
        os.environ['GITLAB_DRY_RUN'] = 'true'
    
    # Setup logging
    setup_logging(
        config.get_log_config(),
        console_level=args.log_level,
        use_colors=not args.no_color
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
        
        # Create renamer
        renamer = BranchRenamer(client, config)
        
        # Get groups to process
        if args.groups:
            groups = [{'name': g} for g in args.groups]
        else:
            groups = config.get_groups()
            if not groups:
                logger.error("No groups configured. Use --groups or update config file.")
                return 1
        
        # Process each group
        logger.info(f"Branch Rename Tool: '{args.old_branch}' → '{args.new_branch}'")
        if renamer.dry_run:
            logger.info("Running in DRY RUN mode - no changes will be made")
        
        success_count = 0
        for group in groups:
            if renamer.process_group(group['name'], args.old_branch, args.new_branch):
                success_count += 1
        
        # Print summary
        renamer.print_summary()
        
        # Exit code based on results
        if renamer.stats['failed'] > 0:
            return 2  # Some failures
        elif success_count == 0:
            return 1  # No groups processed
        else:
            return 0  # Success
            
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())