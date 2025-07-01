#!/usr/bin/env python3
"""Test script to demonstrate GitLab board service functionality."""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.api.client import GitLabClient
from src.services.board_service import BoardService
from src.utils import Config, setup_logging, get_logger


def main():
    """Test board service functionality."""
    parser = argparse.ArgumentParser(
        description="Test GitLab board service functionality"
    )
    parser.add_argument(
        "project_id",
        help="GitLab project ID or path (e.g., 12345 or group/project)"
    )
    parser.add_argument(
        "--board-id",
        type=int,
        help="Specific board ID to analyze (uses default board if not specified)"
    )
    parser.add_argument(
        "--show-issues",
        action="store_true",
        help="Show detailed issue breakdown by workflow state"
    )
    
    args = parser.parse_args()
    
    # Setup
    config = Config()
    setup_logging(config.get_log_config())
    logger = get_logger(__name__)
    
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
        
        # Create board service
        board_service = BoardService(client, config.to_dict())
        
        print(f"\n📋 Testing Board Service for Project: {args.project_id}")
        print("=" * 60)
        
        # 1. List available boards
        print("\n1. Available Boards:")
        boards = board_service.get_project_boards(args.project_id)
        
        if not boards:
            print("   No boards found for this project")
            return
        
        for board in boards:
            print(f"   - ID: {board['id']}, Name: {board.get('name', 'Unnamed')}")
        
        # 2. Get default board or use specified board
        if args.board_id:
            board_id = args.board_id
            board_name = f"Board {board_id}"
            print(f"\n2. Using Specified Board: {board_name}")
        else:
            default_board = board_service.get_default_board(args.project_id)
            if not default_board:
                print("\n2. No default board found")
                return
            
            board_id = default_board['id']
            board_name = default_board.get('name', 'Unnamed')
            print(f"\n2. Using Default Board: {board_name} (ID: {board_id})")
        
        # 3. Get board workflow labels
        print("\n3. Board Workflow Labels:")
        workflow_labels = board_service.get_board_workflow_labels(args.project_id, board_id)
        
        if not workflow_labels:
            print("   No workflow labels found on this board")
        else:
            for state, labels in workflow_labels.items():
                if labels:
                    print(f"   {state.replace('_', ' ').title()}: {', '.join(labels)}")
        
        # 4. Get workflow statistics
        print("\n4. Workflow Statistics:")
        stats = board_service.get_workflow_statistics(args.project_id, board_id)
        
        print(f"   Total Open Issues: {stats['total_issues']}")
        
        if stats['by_state']:
            print("   By Workflow State:")
            for state, count in stats['by_state'].items():
                if count > 0:
                    state_display = state.replace('_', ' ').title()
                    print(f"     {state_display}: {count}")
        
        # 5. Show detailed issues if requested
        if args.show_issues and stats['total_issues'] > 0:
            print("\n5. Issues by Workflow State:")
            
            # Get all open issues
            issues = list(client.get_issues(project_id=args.project_id, state='opened'))
            categorized = board_service.categorize_issues_by_workflow(issues, workflow_labels)
            
            for state, issue_list in categorized.items():
                if issue_list:
                    state_display = state.replace('_', ' ').title()
                    print(f"\n   {state_display} ({len(issue_list)} issues):")
                    
                    for issue in issue_list[:5]:  # Show first 5 issues
                        labels_str = ', '.join(issue.get('labels', []))
                        assignee = issue.get('assignee', {}).get('name', 'Unassigned')
                        print(f"     - #{issue['iid']}: {issue['title'][:50]}...")
                        print(f"       Labels: [{labels_str}], Assignee: {assignee}")
                    
                    if len(issue_list) > 5:
                        print(f"     ... and {len(issue_list) - 5} more issues")
        
        print("\n✅ Board service test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error testing board service: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()