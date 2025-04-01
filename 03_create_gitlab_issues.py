#!/usr/bin/env python3
"""
GitLab Issue Creator

This script creates issues in a GitLab project based on a structured text file.
"""

import os
import sys
import requests
import time
import argparse
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


def validate_env_vars() -> None:
    """Validate that required environment variables exist."""
    required_vars = ['GITLAB_URL', 'GITLAB_API_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file.")
        sys.exit(1)


def get_gitlab_headers() -> Dict[str, str]:
    """Create headers for GitLab API requests with authentication."""
    return {
        'Private-Token': os.getenv('GITLAB_API_TOKEN'),
        'Content-Type': 'application/json'
    }


def get_project_id(project_name: str) -> Optional[int]:
    """
    Get project ID by name.
    
    Args:
        project_name: The name of the project to find
        
    Returns:
        Project ID if found, None otherwise
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        search_url = f"{base_url}/api/v4/projects"
        params = {'search': project_name}
        
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        
        projects = response.json()
        
        # Find exact match for the project name
        for project in projects:
            if project['name'].lower() == project_name.lower():
                return project['id']
        
        print(f"Project '{project_name}' not found.")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching project: {e}")
        return None


def create_issue(project_id: int, title: str, description: str, labels: List[str]) -> bool:
    """
    Create a new issue in a GitLab project.
    
    Args:
        project_id: The ID of the project
        title: The title of the issue
        description: The description of the issue
        labels: List of labels to apply to the issue
        
    Returns:
        True if issue was created successfully, False otherwise
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        url = f"{base_url}/api/v4/projects/{project_id}/issues"
        
        # Debug: Print the description that will be sent to GitLab
        print(f"Creating issue '{title}' with description:")
        print("-" * 40)
        print(description)
        print("-" * 40)
        
        data = {
            'title': title,
            'description': description,
            'labels': ','.join(labels)
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        issue = response.json()
        print(f"✓ Created issue #{issue['iid']}: {title}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"× Error creating issue '{title}': {e}")
        return False


def parse_issues_from_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse issues from a text file.
    
    Args:
        file_path: Path to the file containing issue descriptions
        
    Returns:
        List of dictionaries containing issue details
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return parse_issues_from_text(content)
    
    except Exception as e:
        print(f"Error reading or parsing file {file_path}: {e}")
        return []


def parse_issues_from_text(content: str) -> List[Dict[str, Any]]:
    """
    Parse issues from text content.
    
    The expected format is:
    [Feature/Task] Title
    Description: Description text
    Acceptance: Acceptance criteria
    Labels: label1, label2, label3
    
    Args:
        content: Text containing issue descriptions
        
    Returns:
        List of dictionaries containing issue details
    """
    issues = []
    
    # Skip the header line
    if content.startswith("High-Level GitLab Issues"):
        content = content.split('\n', 1)[1]
    
    # Split content by separator lines (underscores)
    sections = content.split('________________________________________')
    
    # Process each section
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        # Find the first line which should contain issue type and title
        first_line = lines[0].strip()
        
        # Variables to accumulate issue data
        current_issue_title = ""
        current_issue_type = ""
        current_description = ""
        current_acceptance = ""
        current_labels = []
        
        # Parse issue type and title from the first line
        if "[Feature]" in first_line:
            current_issue_type = "Feature"
            current_issue_title = first_line.split("[Feature]")[1].strip()
        elif "[Task]" in first_line:
            current_issue_type = "Task"
            current_issue_title = first_line.split("[Task]")[1].strip()
        else:
            # Not a valid issue line, skip this section
            continue
        
        # Flags to track what we're parsing
        parse_mode = None
        
        # Process the remaining lines
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            # Check for section markers
            if line == "Description:":
                parse_mode = "description"
            elif line in ["Acceptance Criteria:", "Acceptance:"]:
                parse_mode = "acceptance"
            elif line.startswith("Labels:"):
                parse_mode = None  # No multi-line parsing for labels
                labels_text = line.split("Labels:", 1)[1].strip()
                current_labels = [label.strip() for label in labels_text.split(',')]
                # Add issue type as a label if it exists
                if current_issue_type:
                    current_labels.append(current_issue_type.lower())
            # Handle content lines
            elif parse_mode == "description":
                if line.startswith('•'):
                    line = line[1:].strip()
                current_description += f"- {line}\n"
            elif parse_mode == "acceptance":
                if line.startswith('•'):
                    line = line[1:].strip()
                current_acceptance += f"- {line}\n"
        
        # If we found a valid issue, add it to the list
        if current_issue_title:
            # Format the description for GitLab
            formatted_description = "## Description\n"
            if current_description.strip():
                formatted_description += current_description
            else:
                formatted_description += "- No description provided.\n"
            
            formatted_description += "\n## Acceptance Criteria\n"
            if current_acceptance.strip():
                formatted_description += current_acceptance
            else:
                formatted_description += "- No acceptance criteria provided.\n"
            
            # Create issue dict
            issue = {
                'title': current_issue_title,
                'description': formatted_description,
                'labels': current_labels,
                'type': current_issue_type,
                'raw_description': current_description,
                'raw_acceptance': current_acceptance
            }
            
            issues.append(issue)
    
    return issues


def display_issues(issues: List[Dict[str, Any]]) -> None:
    """
    Display a summary of issues to be created.
    
    Args:
        issues: List of issue dictionaries
    """
    print("\nIssues to be created:")
    print("=" * 80)
    
    for i, issue in enumerate(issues, 1):
        issue_type = f"[{issue.get('type', 'Issue')}]" if issue.get('type') else ""
        print(f"{i}. {issue_type} {issue['title']}")
        
        # Show labels
        if issue['labels']:
            print(f"   Labels: {', '.join(issue['labels'])}")
        
        # Show description preview
        if issue.get('raw_description'):
            desc_lines = issue['raw_description'].strip().split('\n')
            if desc_lines:
                # Take up to 2 lines for preview
                preview_lines = desc_lines[:min(2, len(desc_lines))]
                for j, line in enumerate(preview_lines):
                    print(f"   {'Description:' if j == 0 else '            '} {line}")
        
        # Show acceptance criteria preview
        if issue.get('raw_acceptance'):
            acc_lines = issue['raw_acceptance'].strip().split('\n')
            if acc_lines:
                # Take 1 line for preview
                print(f"   Acceptance: {acc_lines[0]}")
        
        print()
    
    print("=" * 80)


def display_full_issue(issue: Dict[str, Any]) -> None:
    """
    Display full details of a single issue.
    
    Args:
        issue: Dictionary containing issue details
    """
    print("\nFull Issue Details:")
    print("=" * 80)
    
    # Display title with type
    issue_type = f"[{issue.get('type', 'Issue')}]" if issue.get('type') else ""
    print(f"Title: {issue_type} {issue['title']}")
    
    # Display labels
    if issue['labels']:
        print(f"Labels: {', '.join(issue['labels'])}")
    
    # Display full description that will be sent to GitLab
    print("\nDescription that will be sent to GitLab:")
    print("-" * 80)
    print(issue['description'])
    print("-" * 80)


def main() -> None:
    """Main function to run the script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="GitLab Issue Creator - Creates issues in GitLab from text files")
    parser.add_argument("project", nargs="?", help="GitLab project name")
    parser.add_argument("issues_file", nargs="?", help="Path to the issues file")
    parser.add_argument("--list", action="store_true", help="List available issue files")
    args = parser.parse_args()
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Validate required environment variables
    validate_env_vars()
    
    print("GitLab Issue Creator")
    print("=" * 50)
    
    # If --list flag is used, just show available issue files and exit
    if args.list:
        print("\nAvailable issue files:")
        try:
            issues_dir_files = os.listdir("issues")
            for i, file in enumerate(issues_dir_files, 1):
                print(f" {i}. {file}")
        except Exception as e:
            print(f"Error listing issues directory: {e}")
        sys.exit(0)
    
    # Prompt for project name or get from command line
    if args.project:
        project_name = args.project
    else:
        project_name = input("Enter project name: ")
    
    # Prompt for issues file or get from command line
    if args.issues_file:
        issues_file = args.issues_file
    else:
        # Show available issue files
        print("\nAvailable issue files:")
        try:
            issues_dir_files = os.listdir("issues")
            for i, file in enumerate(issues_dir_files, 1):
                print(f" {i}. {file}")
            print()
            
            file_choice = input("Enter issue file name or number from the list: ")
            
            # If user entered a number, get the corresponding file
            if file_choice.isdigit() and 1 <= int(file_choice) <= len(issues_dir_files):
                issues_file = os.path.join("issues", issues_dir_files[int(file_choice) - 1])
            else:
                # If user entered a filename, ensure it's in the issues directory
                if not file_choice.startswith("issues/"):
                    issues_file = os.path.join("issues", file_choice)
                else:
                    issues_file = file_choice
        except Exception as e:
            print(f"Error listing issues directory: {e}")
            issues_file = input("Enter issues file path: ")
    
    # Get project ID
    project_id = get_project_id(project_name)
    
    if not project_id:
        print(f"Error: Project '{project_name}' not found.")
        sys.exit(1)
    
    print(f"Found project '{project_name}' with ID: {project_id}")
    
    # Parse issues from file
    if not os.path.exists(issues_file):
        print(f"Error: Issues file '{issues_file}' not found.")
        print(f"Current directory: {os.getcwd()}")
        print("Available files in issues directory:")
        try:
            issues_dir_files = os.listdir("issues")
            for file in issues_dir_files:
                print(f" - {file}")
        except Exception as e:
            print(f"Error listing issues directory: {e}")
        sys.exit(1)
    
    issues = parse_issues_from_file(issues_file)
    
    # Remove any empty or invalid issues
    issues = [issue for issue in issues if issue.get('title') and issue.get('title').strip()]
    
    if not issues:
        print("No valid issues found in the file. Exiting.")
        sys.exit(1)
    
    print(f"Found {len(issues)} issues to create.")
    
    # Display issues for confirmation
    display_issues(issues)
    
    # Allow user to view full details of each issue
    while True:
        view_option = input("\nEnter issue number to view full details, 'all' to view all issues, or 'c' to continue: ")
        
        if view_option.lower() == 'c':
            break
        elif view_option.lower() == 'all':
            for issue in issues:
                display_full_issue(issue)
                print("\n")
                input("Press Enter to view next issue...")
        elif view_option.isdigit() and 1 <= int(view_option) <= len(issues):
            issue_idx = int(view_option) - 1
            display_full_issue(issues[issue_idx])
        else:
            print("Invalid option. Please enter a valid issue number, 'all', or 'c'.")
    
    # Confirm with the user
    confirmation = input("\nDo you want to create these issues? [y/N]: ")
    
    if confirmation.lower() != 'y':
        print("Operation canceled.")
        sys.exit(0)
    
    print("\nCreating issues...")
    
    # Create issues
    success_count = 0
    
    for issue in issues:
        # Remove the extra keys not needed for the API call
        issue_copy = issue.copy()
        for key in ['type', 'raw_description', 'raw_acceptance']:
            if key in issue_copy:
                del issue_copy[key]
            
        if create_issue(project_id, issue_copy['title'], issue_copy['description'], issue_copy['labels']):
            success_count += 1
            # Add a small delay to avoid rate limiting
            time.sleep(0.5)
    
    print(f"\nSummary: Created {success_count} out of {len(issues)} issues.")


if __name__ == "__main__":
    main() 