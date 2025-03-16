#!/usr/bin/env python3
"""
GitLab Issue Creator

This script creates issues in a GitLab project based on a structured text file.
"""

import os
import sys
import requests
import time
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
    •	Description: Description text
    •	Acceptance: Acceptance criteria
    •	Labels: label1, label2, label3
    
    Args:
        content: Text containing issue descriptions
        
    Returns:
        List of dictionaries containing issue details
    """
    issues = []
    
    # Skip the header line
    if content.startswith("High-Level GitLab Issues"):
        content = content.split('\n', 1)[1]
    
    # Split content by main numbered sections
    sections = []
    current_section = ""
    
    for line in content.split('\n'):
        if line.strip() and line[0].isdigit() and '. ' in line:
            if current_section:
                sections.append(current_section)
            current_section = line
        else:
            current_section += '\n' + line
    
    if current_section:
        sections.append(current_section)
    
    # Process each section (category of issues)
    for section in sections:
        lines = section.split('\n')
        if not lines:
            continue
            
        # Find the section title/number
        section_title = lines[0].strip() if lines else ""
        
        # Variables to accumulate issue data
        current_issue_title = ""
        current_issue_type = ""
        current_description = ""
        current_acceptance = ""
        current_labels = []
        
        # Flags to track what we're parsing
        parsing_feature = False
        parse_mode = None
        
        for line in lines[1:]:  # Skip the section header line
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a new issue (begins with [Feature] or [Task] pattern)
            if ('[Feature]' in line or '[Task]' in line) and '•' not in line:
                # If we were parsing an issue before, save it
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
                
                # Start a new issue
                if '[Feature]' in line:
                    current_issue_type = 'Feature'
                    current_issue_title = line.split('[Feature]')[1].strip()
                elif '[Task]' in line:
                    current_issue_type = 'Task'
                    current_issue_title = line.split('[Task]')[1].strip()
                else:
                    current_issue_type = ""
                    current_issue_title = line.strip()
                
                # Reset other fields
                current_description = ""
                current_acceptance = ""
                current_labels = []
                parsing_feature = True
                parse_mode = None
            
            # Check for description, acceptance, or labels markers
            elif parsing_feature and line.startswith('•'):
                line = line[1:].strip()  # Remove the bullet point
                
                if "Description:" in line:
                    parse_mode = "description"
                    # Get any text after "Description:" as the first line
                    desc_text = line.split("Description:", 1)[1].strip()
                    if desc_text:
                        current_description += f"- {desc_text}\n"
                
                elif "Acceptance Criteria:" in line or "Acceptance:" in line:
                    parse_mode = "acceptance"
                    # Get any text after "Acceptance:" as the first line
                    if "Acceptance Criteria:" in line:
                        accept_text = line.split("Acceptance Criteria:", 1)[1].strip()
                    else:
                        accept_text = line.split("Acceptance:", 1)[1].strip()
                    if accept_text:
                        current_acceptance += f"- {accept_text}\n"
                
                elif "Labels:" in line:
                    parse_mode = None  # No multi-line parsing for labels
                    labels_text = line.split("Labels:", 1)[1].strip()
                    current_labels = [label.strip() for label in labels_text.split(',')]
                    # Add issue type as a label if it exists
                    if current_issue_type:
                        current_labels.append(current_issue_type.lower())
            
            # Handle continuation lines for description or acceptance criteria
            elif parsing_feature and parse_mode and (line.startswith('-') or line.startswith('\t') or line.startswith('  ')):
                line = line.lstrip('\t -').strip()
                if line:
                    if parse_mode == "description":
                        current_description += f"- {line}\n"
                    elif parse_mode == "acceptance":
                        current_acceptance += f"- {line}\n"
                        
        # Don't forget to add the last issue in the section
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
    # Load environment variables from .env file
    load_dotenv()
    
    # Validate required environment variables
    validate_env_vars()
    
    print("GitLab Issue Creator")
    print("=" * 50)
    
    # Get project name from command line or use default
    project_name = "flow-speech-to-text"
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    
    # Get issues file from command line or use default
    issues_file = "issues-flow-speech-to-text.txt"
    if len(sys.argv) > 2:
        issues_file = sys.argv[2]
    
    # Get project ID
    project_id = get_project_id(project_name)
    
    if not project_id:
        print(f"Error: Project '{project_name}' not found.")
        sys.exit(1)
    
    print(f"Found project '{project_name}' with ID: {project_id}")
    
    # Parse issues from file
    if not os.path.exists(issues_file):
        print(f"Error: Issues file '{issues_file}' not found.")
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