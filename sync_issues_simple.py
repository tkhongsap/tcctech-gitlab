#!/usr/bin/env python3
"""
Simple script to sync markdown files to GitLab issues.
Specifically configured for: ds-and-ml-research-sandbox/research-repos/issues-generator-automation
"""

import os
import sys
import re
import subprocess
import json
from pathlib import Path

# Configuration - Update these values
GITLAB_URL = "https://git.lab.tcctech.app"
PROJECT_PATH = "ds-and-ml-research-sandbox/research-repos/issues-generator-automation"
ISSUES_FOLDER = "issues"

# Get token from environment or .env file
def get_token():
    """Get GitLab token from environment or .env file."""
    token = os.getenv('GITLAB_API_TOKEN')
    
    if not token and os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('GITLAB_API_TOKEN='):
                    token = line.split('=', 1)[1].strip()
                    break
    
    if not token:
        print("ERROR: GitLab token not found!")
        print("Please set GITLAB_API_TOKEN in your environment or .env file")
        sys.exit(1)
    
    return token


def parse_markdown_file(filepath):
    """Parse a markdown file and extract issue data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Default values
    title = filepath.stem.replace('-', ' ').replace('_', ' ').title()
    labels = []
    description = content
    
    # Check for YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            description = parts[2].strip()
            
            # Parse frontmatter
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'title':
                        title = value.strip('"\'')
                    elif key == 'labels':
                        # Handle both [label1, label2] and label1, label2 formats
                        value = value.strip('[]')
                        labels = [l.strip().strip('"\'') for l in value.split(',')]
    
    # Extract hashtags as additional labels
    hashtags = re.findall(r'#(\w+)', description)
    labels.extend(hashtags)
    
    # Remove duplicates
    labels = list(set(labels))
    
    # If title wasn't in frontmatter, try to extract from first heading
    if not title and description:
        heading_match = re.search(r'^#\s+(.+)$', description, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1).strip()
            description = description.replace(heading_match.group(0), '', 1).strip()
    
    return {
        'title': title,
        'description': description,
        'labels': ','.join(labels) if labels else ''
    }


def create_issue_with_curl(issue_data, project_path, token, dry_run=False):
    """Create an issue using curl."""
    # URL encode the project path
    encoded_path = project_path.replace('/', '%2F')
    api_url = f"{GITLAB_URL}/api/v4/projects/{encoded_path}/issues"
    
    # Build curl command
    cmd = [
        'curl',
        '--request', 'POST',
        api_url,
        '--header', f'PRIVATE-TOKEN: {token}',
        '--silent',
        '--show-error'
    ]
    
    # Add form data
    for key, value in issue_data.items():
        if value:  # Only add non-empty values
            cmd.extend(['--form', f'{key}={value}'])
    
    if dry_run:
        print(f"DRY RUN - Would execute: {' '.join(cmd[:6])}...")
        return True, "Dry run - no issue created"
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse response
        response = json.loads(result.stdout)
        issue_url = response.get('web_url', '')
        issue_id = response.get('iid', '')
        
        return True, f"Created issue #{issue_id}: {issue_url}"
        
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr
        if e.stdout:
            try:
                error_data = json.loads(e.stdout)
                error_msg = error_data.get('message', e.stderr)
            except:
                pass
        return False, f"Error: {error_msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main function."""
    print(f"GitLab Issue Sync Tool")
    print(f"Project: {PROJECT_PATH}")
    print(f"GitLab: {GITLAB_URL}")
    print("=" * 60)
    
    # Check for dry run
    dry_run = '--dry-run' in sys.argv
    if dry_run:
        print("🔍 DRY RUN MODE - No issues will be created\n")
    
    # Get token
    token = get_token()
    
    # Get issues folder
    issues_dir = Path(ISSUES_FOLDER)
    if not issues_dir.exists():
        print(f"\nCreating issues folder: {issues_dir}")
        issues_dir.mkdir(exist_ok=True)
        
        # Create example file
        example_file = issues_dir / "example-issue.md"
        with open(example_file, 'w') as f:
            f.write("""---
title: Example Issue
labels: [documentation, example]
---

# Description

This is an example issue file. Create your own markdown files in this folder and run the script to sync them to GitLab.

## Features

- Supports YAML frontmatter for metadata
- Extracts hashtags as labels
- Simple and easy to use

#automation #gitlab
""")
        print(f"Created example: {example_file}")
        print("\nAdd your issue files to the 'issues' folder and run this script again.")
        return
    
    # Find all markdown files
    issue_files = list(issues_dir.glob('*.md')) + list(issues_dir.glob('*.txt'))
    
    if not issue_files:
        print(f"\nNo issue files found in {issues_dir}")
        print("Create .md or .txt files in the issues folder and run again.")
        return
    
    print(f"\nFound {len(issue_files)} issue files\n")
    
    # Process each file
    success_count = 0
    for i, filepath in enumerate(issue_files, 1):
        print(f"[{i}/{len(issue_files)}] Processing: {filepath.name}")
        
        try:
            # Parse file
            issue_data = parse_markdown_file(filepath)
            print(f"  Title: {issue_data['title']}")
            if issue_data['labels']:
                print(f"  Labels: {issue_data['labels']}")
            
            # Create issue
            success, message = create_issue_with_curl(issue_data, PROJECT_PATH, token, dry_run)
            
            if success:
                success_count += 1
                print(f"  ✓ {message}")
            else:
                print(f"  ✗ {message}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"Summary: {success_count}/{len(issue_files)} issues {'would be' if dry_run else ''} created successfully")
    
    if dry_run:
        print("\nRun without --dry-run to actually create the issues.")


if __name__ == "__main__":
    main()