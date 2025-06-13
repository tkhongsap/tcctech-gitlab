#!/usr/bin/env python3
"""Simplified branch rename script that works with available system packages."""

import os
import sys
import json
import requests
import argparse
from pathlib import Path

# Simple color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'

# Load environment variables from .env file
def load_env():
    env = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env[key] = value
    return env

class GitLabClient:
    def __init__(self, url, token):
        self.url = url.rstrip('/')
        self.token = token
        self.headers = {'PRIVATE-TOKEN': token}
        self.api_base = f"{self.url}/api/v4"
    
    def get_group_by_name(self, name):
        """Find group by name."""
        response = requests.get(
            f"{self.api_base}/groups",
            headers=self.headers,
            params={'search': name}
        )
        if response.status_code == 200:
            groups = response.json()
            for group in groups:
                if group['name'] == name or group['full_name'] == name:
                    return group
        return None
    
    def get_projects(self, group_id):
        """Get all projects in a group."""
        projects = []
        page = 1
        while True:
            response = requests.get(
                f"{self.api_base}/groups/{group_id}/projects",
                headers=self.headers,
                params={'per_page': 100, 'page': page, 'include_subgroups': True}
            )
            if response.status_code == 200:
                batch = response.json()
                if not batch:
                    break
                projects.extend(batch)
                page += 1
            else:
                break
        return projects
    
    def branch_exists(self, project_id, branch_name):
        """Check if branch exists."""
        response = requests.get(
            f"{self.api_base}/projects/{project_id}/repository/branches/{branch_name}",
            headers=self.headers
        )
        return response.status_code == 200
    
    def get_branch(self, project_id, branch_name):
        """Get branch info."""
        response = requests.get(
            f"{self.api_base}/projects/{project_id}/repository/branches/{branch_name}",
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def create_branch(self, project_id, branch_name, ref):
        """Create a new branch."""
        response = requests.post(
            f"{self.api_base}/projects/{project_id}/repository/branches",
            headers=self.headers,
            json={'branch': branch_name, 'ref': ref}
        )
        return response.status_code == 201
    
    def delete_branch(self, project_id, branch_name):
        """Delete a branch."""
        response = requests.delete(
            f"{self.api_base}/projects/{project_id}/repository/branches/{branch_name}",
            headers=self.headers
        )
        return response.status_code == 204
    
    def update_default_branch(self, project_id, branch_name):
        """Update default branch."""
        response = requests.put(
            f"{self.api_base}/projects/{project_id}",
            headers=self.headers,
            json={'default_branch': branch_name}
        )
        return response.status_code == 200

def rename_branch(client, project, old_branch, new_branch, dry_run=False):
    """Rename branch in a project."""
    project_name = project['name']
    project_id = project['id']
    
    # Check if old branch exists
    if not client.branch_exists(project_id, old_branch):
        print(f"  → Branch '{old_branch}' not found - skipping")
        return 'skipped'
    
    # Check if new branch already exists
    if client.branch_exists(project_id, new_branch):
        print(f"  → Branch '{new_branch}' already exists - skipping")
        return 'skipped'
    
    # Get branch info
    branch_info = client.get_branch(project_id, old_branch)
    if branch_info and branch_info.get('protected'):
        print(f"  → Branch '{old_branch}' is protected - skipping")
        return 'skipped'
    
    if dry_run:
        print(f"  → [DRY RUN] Would rename '{old_branch}' to '{new_branch}'")
        return 'renamed'
    
    # Get the commit SHA from old branch
    commit_sha = branch_info['commit']['id']
    
    # Create new branch
    if not client.create_branch(project_id, new_branch, commit_sha):
        print(f"  → Failed to create branch '{new_branch}'")
        return 'failed'
    
    # Update default branch if needed
    if project.get('default_branch') == old_branch:
        if client.update_default_branch(project_id, new_branch):
            print(f"  → Updated default branch to '{new_branch}'")
        else:
            print(f"  → Warning: Failed to update default branch")
    
    # Delete old branch
    if client.delete_branch(project_id, old_branch):
        print(f"  → Successfully renamed '{old_branch}' to '{new_branch}'")
        return 'renamed'
    else:
        print(f"  → Warning: Created '{new_branch}' but failed to delete '{old_branch}'")
        return 'partial'

def main():
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
        help='Groups to process'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without making them'
    )
    
    args = parser.parse_args()
    
    # Load environment
    env = load_env()
    gitlab_url = env.get('GITLAB_URL', os.environ.get('GITLAB_URL'))
    gitlab_token = env.get('GITLAB_API_TOKEN', os.environ.get('GITLAB_API_TOKEN'))
    
    if not gitlab_url or not gitlab_token:
        print(f"{Colors.RED}Error: GITLAB_URL and GITLAB_API_TOKEN must be set{Colors.RESET}")
        print("Create a .env file with:")
        print("  GITLAB_URL=https://your-gitlab.com")
        print("  GITLAB_API_TOKEN=your-token")
        return 1
    
    # Create client
    client = GitLabClient(gitlab_url, gitlab_token)
    
    # Default groups if none specified
    if not args.groups:
        # Load from config.yaml if it exists
        config_path = 'config/config.yaml'
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    groups = [g['name'] for g in config.get('groups', [])]
                    args.groups = groups
            except:
                pass
        
        if not args.groups:
            print(f"{Colors.RED}Error: No groups specified{Colors.RESET}")
            print("Use --groups to specify groups to process")
            return 1
    
    print(f"{Colors.BOLD}Branch Rename Tool{Colors.RESET}")
    print(f"Renaming: '{args.old_branch}' → '{args.new_branch}'")
    if args.dry_run:
        print(f"{Colors.YELLOW}DRY RUN MODE - No changes will be made{Colors.RESET}")
    print()
    
    # Statistics
    stats = {
        'total': 0,
        'renamed': 0,
        'skipped': 0,
        'failed': 0,
        'partial': 0
    }
    
    # Process each group
    for group_name in args.groups:
        print(f"{Colors.BOLD}Processing group: {group_name}{Colors.RESET}")
        
        group = client.get_group_by_name(group_name)
        if not group:
            print(f"  {Colors.RED}→ Group not found{Colors.RESET}")
            continue
        
        projects = client.get_projects(group['id'])
        if not projects:
            print(f"  → No projects found")
            continue
        
        print(f"  → Found {len(projects)} projects")
        
        for i, project in enumerate(projects, 1):
            stats['total'] += 1
            print(f"\n  [{i}/{len(projects)}] {project['name']}")
            
            result = rename_branch(
                client, 
                project, 
                args.old_branch, 
                args.new_branch, 
                args.dry_run
            )
            
            stats[result] = stats.get(result, 0) + 1
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Operation Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    
    if args.dry_run:
        print(f"{Colors.YELLOW}DRY RUN MODE - No actual changes were made{Colors.RESET}")
    
    print(f"Total projects processed: {stats['total']}")
    print(f"{Colors.GREEN}Successfully renamed: {stats['renamed']}{Colors.RESET}")
    print(f"{Colors.YELLOW}Skipped: {stats['skipped']}{Colors.RESET}")
    if stats.get('partial', 0) > 0:
        print(f"{Colors.YELLOW}Partially completed: {stats['partial']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {stats['failed']}{Colors.RESET}")
    
    if stats['failed'] > 0:
        return 2
    elif stats['total'] == 0:
        return 1
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())