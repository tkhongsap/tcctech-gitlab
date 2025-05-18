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


def get_available_projects() -> List[Dict[str, Any]]:
    """
    Get list of available GitLab projects the user has access to.
    
    Returns:
        List of project dictionaries containing id, name, and path_with_namespace
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        # Get projects the authenticated user is a member of
        url = f"{base_url}/api/v4/projects"
        params = {'membership': True, 'per_page': 100}  # Limit to 100 projects
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        projects = response.json()
        
        # Sort projects by name for easier browsing
        projects.sort(key=lambda x: x['name'].lower())
        
        return projects
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching available projects: {e}")
        return []


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
        # Skip empty sections
        if not section.strip():
            continue
        
        # Find title and type
        title_line = ""
        issue_type = ""
        description = ""
        acceptance = ""
        labels = []
        
        lines = section.strip().split('\n')
        
        # Find the feature/task line
        for line in lines:
            if "[Feature]" in line:
                title_line = line.strip()
                issue_type = "Feature"
                title = title_line.split("[Feature]")[1].strip()
                break
            elif "[Task]" in line:
                title_line = line.strip()
                issue_type = "Task"
                title = title_line.split("[Task]")[1].strip()
                break
        
        # Skip if no valid title found
        if not title_line:
            continue
        
        # Extract description, acceptance, and labels
        description_line = next((line for line in lines if line.strip().startswith("Description:")), "")
        acceptance_line = next((line for line in lines if line.strip().startswith("Acceptance:") or 
                                line.strip().startswith("Acceptance Criteria:")), "")
        labels_line = next((line for line in lines if line.strip().startswith("Labels:")), "")
        
        # Process description
        if description_line:
            description_text = description_line.split("Description:", 1)[1].strip()
            description = f"- {description_text}\n"
        
        # Process acceptance
        if acceptance_line:
            if acceptance_line.startswith("Acceptance Criteria:"):
                acceptance_text = acceptance_line.split("Acceptance Criteria:", 1)[1].strip()
            else:
                acceptance_text = acceptance_line.split("Acceptance:", 1)[1].strip()
            acceptance = f"- {acceptance_text}\n"
        
        # Process labels
        if labels_line:
            labels_text = labels_line.split("Labels:", 1)[1].strip()
            labels = [label.strip() for label in labels_text.split(',')]
            # Add issue type as a label
            if issue_type:
                labels.append(issue_type.lower())
        
        # Format the description for GitLab
        formatted_description = "## Description\n"
        if description:
            formatted_description += description
        else:
            formatted_description += "- No description provided.\n"
        
        formatted_description += "\n## Acceptance Criteria\n"
        if acceptance:
            formatted_description += acceptance
        else:
            formatted_description += "- No acceptance criteria provided.\n"
        
        # Create issue dict
        issue = {
            'title': title,
            'description': formatted_description,
            'labels': labels,
            'type': issue_type,
            'raw_description': description,
            'raw_acceptance': acceptance
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
    project_id = None
    if args.project:
        project_name = args.project
    else:
        # Fetch and display available projects
        print("\nFetching available GitLab projects...")
        projects = get_available_projects()
        
        if not projects:
            print("No projects found or couldn't fetch projects. Please enter the project name manually.")
            project_name = input("Enter project name: ")
        else:
            print("\nAvailable GitLab projects:")
            for i, project in enumerate(projects, 1):
                print(f" {i}. {project['name']} ({project['path_with_namespace']})")
            print()
            
            project_choice = input("Enter project number from the list or project name only: ")
            
            # If user entered a number, get the corresponding project
            if project_choice.isdigit() and 1 <= int(project_choice) <= len(projects):
                project_name = projects[int(project_choice) - 1]['name']
                project_id = projects[int(project_choice) - 1]['id']
            else:
                # Try to find project by name
                project_found = False
                for project in projects:
                    if project['name'].lower() == project_choice.lower():
                        project_name = project['name']
                        project_id = project['id']
                        project_found = True
                        break
                
                if not project_found:
                    # User entered a name we couldn't find exactly
                    project_name = project_choice
    
    # Get project ID if not already set from list selection
    if project_id is None:
        project_id = get_project_id(project_name)
    
    if not project_id:
        print(f"Error: Project '{project_name}' not found.")
        sys.exit(1)
    
    print(f"Found project '{project_name}' with ID: {project_id}")
    
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