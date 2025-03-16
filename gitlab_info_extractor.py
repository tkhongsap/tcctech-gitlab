#!/usr/bin/env python3
"""
GitLab Information Extractor

This script extracts information about groups and subgroups from a GitLab instance.
"""

import os
import sys
import json
import csv
import requests
from typing import Dict, List, Any, Optional, Set, Tuple
from dotenv import load_dotenv
from datetime import datetime


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


def get_group_by_name(group_name: str) -> Optional[Dict[str, Any]]:
    """
    Find a group by its name.
    
    Args:
        group_name: The name of the group to find
        
    Returns:
        Dictionary containing group information or None if not found
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        # Search for the group by name
        search_url = f"{base_url}/api/v4/groups"
        params = {'search': group_name}
        
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        
        groups = response.json()
        
        # Find exact match for the group name
        for group in groups:
            if group['name'] == group_name:
                return group
        
        print(f"Group '{group_name}' not found.")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching group: {e}")
        return None


def get_subgroups(group_id: int) -> List[Dict[str, Any]]:
    """
    Get all subgroups for a given group ID.
    
    Args:
        group_id: The ID of the parent group
        
    Returns:
        List of subgroups
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        subgroups_url = f"{base_url}/api/v4/groups/{group_id}/subgroups"
        # Get all subgroups (GitLab API typically paginates results)
        params = {'per_page': 100}
        
        response = requests.get(subgroups_url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching subgroups: {e}")
        return []


def get_projects(group_id: int) -> List[Dict[str, Any]]:
    """
    Get all projects for a given group ID.
    
    Args:
        group_id: The ID of the group
        
    Returns:
        List of projects
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        projects_url = f"{base_url}/api/v4/groups/{group_id}/projects"
        # Get all projects (GitLab API typically paginates results)
        params = {'per_page': 100, 'include_subgroups': True}
        
        response = requests.get(projects_url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}")
        return []


def get_project_branches(project_id: int) -> List[Dict[str, Any]]:
    """
    Get all branches for a given project ID.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        List of branches
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        branches_url = f"{base_url}/api/v4/projects/{project_id}/repository/branches"
        params = {'per_page': 100}
        
        response = requests.get(branches_url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching branches for project {project_id}: {e}")
        return []


def get_branch_info(project_id: int, branch_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific branch.
    
    Args:
        project_id: The ID of the project
        branch_name: The name of the branch
        
    Returns:
        Dictionary containing branch information or None if not found
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        branch_url = f"{base_url}/api/v4/projects/{project_id}/repository/branches/{branch_name}"
        
        response = requests.get(branch_url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching branch {branch_name} for project {project_id}: {e}")
        return None


def get_last_commit(project_id: int, branch_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the last commit for a specific branch.
    
    Args:
        project_id: The ID of the project
        branch_name: The name of the branch
        
    Returns:
        Dictionary containing commit information or None if not found
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        commits_url = f"{base_url}/api/v4/projects/{project_id}/repository/commits"
        params = {'ref_name': branch_name, 'per_page': 1}
        
        response = requests.get(commits_url, headers=headers, params=params)
        response.raise_for_status()
        
        commits = response.json()
        
        if commits:
            return commits[0]
        
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching last commit for branch {branch_name} in project {project_id}: {e}")
        return None


def get_project_contributors(project_id: int) -> List[Dict[str, Any]]:
    """
    Get all contributors for a given project.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        List of contributors
    """
    base_url = os.getenv('GITLAB_URL')
    headers = get_gitlab_headers()
    
    try:
        contributors_url = f"{base_url}/api/v4/projects/{project_id}/repository/contributors"
        params = {'per_page': 100}
        
        response = requests.get(contributors_url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching contributors for project {project_id}: {e}")
        return []


def count_unique_contributors(project_id: int) -> int:
    """
    Count the number of unique contributors to a project.
    
    Args:
        project_id: The ID of the project
        
    Returns:
        Number of unique contributors
    """
    contributors = get_project_contributors(project_id)
    return len(contributors)


def find_main_branch(project_id: int, default_branch: str) -> str:
    """
    Find the main/trunk branch of a project.
    
    Args:
        project_id: The ID of the project
        default_branch: The default branch of the project
        
    Returns:
        Name of the main branch
    """
    # First try the default branch
    if default_branch and default_branch != 'N/A':
        return default_branch
    
    # Check for common main branch names
    common_main_branches = ['main', 'master', 'trunk', 'develop']
    branches = get_project_branches(project_id)
    branch_names = [branch['name'] for branch in branches]
    
    for branch_name in common_main_branches:
        if branch_name in branch_names:
            return branch_name
    
    # If no common main branch found, return the first branch or empty string
    return branch_names[0] if branch_names else ""


def format_datetime(datetime_str: str) -> str:
    """
    Format a datetime string from GitLab API to a more readable format.
    
    Args:
        datetime_str: The datetime string from GitLab API
        
    Returns:
        Formatted datetime string
    """
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return datetime_str


def print_group_info(group: Dict[str, Any], level: int = 0) -> None:
    """
    Print information about a group.
    
    Args:
        group: Dictionary containing group information
        level: Indentation level for display hierarchy
    """
    indent = "  " * level
    print(f"{indent}Group: {group['name']}")
    print(f"{indent}ID: {group['id']}")
    print(f"{indent}Path: {group['full_path']}")
    print(f"{indent}Description: {group.get('description', 'N/A')}")
    print(f"{indent}Visibility: {group['visibility']}")
    print(f"{indent}Web URL: {group['web_url']}")
    print()


def print_project_info(project: Dict[str, Any], level: int = 0) -> None:
    """
    Print information about a project.
    
    Args:
        project: Dictionary containing project information
        level: Indentation level for display hierarchy
    """
    indent = "  " * level
    print(f"{indent}Project: {project['name']}")
    print(f"{indent}ID: {project['id']}")
    print(f"{indent}Path: {project['path_with_namespace']}")
    print(f"{indent}Description: {project.get('description', 'N/A')}")
    print(f"{indent}Default Branch: {project.get('default_branch', 'N/A')}")
    print(f"{indent}Web URL: {project['web_url']}")
    
    # Get branches for the project
    branches = get_project_branches(project['id'])
    
    # Print project summary
    print(f"{indent}SUMMARY:")
    print(f"{indent}  Total branches: {len(branches)}")
    
    # Find main branch and its latest update
    main_branch_name = find_main_branch(project['id'], project.get('default_branch', ''))
    if main_branch_name:
        main_branch_commit = get_last_commit(project['id'], main_branch_name)
        if main_branch_commit:
            commit_date = format_datetime(main_branch_commit.get('committed_date', 'N/A'))
            author_name = main_branch_commit.get('author_name', 'N/A')
            print(f"{indent}  Latest update on '{main_branch_name}': {commit_date} by {author_name}")
        else:
            print(f"{indent}  No update information available for '{main_branch_name}'")
    else:
        print(f"{indent}  No main branch found")
    
    # Get contributor count
    contributor_count = count_unique_contributors(project['id'])
    print(f"{indent}  Number of contributors: {contributor_count}")
    print()
    
    # List all branches with details
    if branches:
        print(f"{indent}Branches:")
        for branch in branches:
            branch_name = branch['name']
            print(f"{indent}  - {branch_name}")
            
            # Get the last commit for this branch
            last_commit = get_last_commit(project['id'], branch_name)
            
            if last_commit:
                commit_date = format_datetime(last_commit.get('committed_date', 'N/A'))
                author_name = last_commit.get('author_name', 'N/A')
                commit_msg = last_commit.get('message', '').split('\n')[0]  # First line of commit message
                
                print(f"{indent}    Last updated: {commit_date}")
                print(f"{indent}    Updated by: {author_name}")
                print(f"{indent}    Commit message: {commit_msg}")
    
    print()


def collect_branch_info(project_id: int, branch_name: str) -> Dict[str, Any]:
    """
    Collect detailed information about a branch.
    
    Args:
        project_id: The ID of the project
        branch_name: The name of the branch
        
    Returns:
        Dictionary with branch information
    """
    branch_info = {"name": branch_name}
    
    # Get the last commit for this branch
    last_commit = get_last_commit(project_id, branch_name)
    
    if last_commit:
        commit_date = format_datetime(last_commit.get('committed_date', 'N/A'))
        author_name = last_commit.get('author_name', 'N/A')
        commit_msg = last_commit.get('message', '').split('\n')[0]  # First line of commit message
        
        branch_info.update({
            "last_update": commit_date,
            "updated_by": author_name,
            "commit_message": commit_msg,
            "commit_id": last_commit.get('id', 'N/A')
        })
    
    return branch_info


def collect_project_info(project: Dict[str, Any]) -> Dict[str, Any]:
    """
    Collect detailed information about a project.
    
    Args:
        project: Dictionary containing project information
        
    Returns:
        Dictionary with processed project information
    """
    project_id = project['id']
    
    # Get branches
    branches = get_project_branches(project_id)
    
    # Find main branch
    main_branch_name = find_main_branch(project_id, project.get('default_branch', ''))
    main_branch_info = None
    
    if main_branch_name:
        last_commit = get_last_commit(project_id, main_branch_name)
        if last_commit:
            commit_date = format_datetime(last_commit.get('committed_date', 'N/A'))
            author_name = last_commit.get('author_name', 'N/A')
            commit_msg = last_commit.get('message', '').split('\n')[0]
            
            main_branch_info = {
                "name": main_branch_name,
                "last_update": commit_date,
                "updated_by": author_name,
                "commit_message": commit_msg
            }
    
    # Count contributors
    contributor_count = count_unique_contributors(project_id)
    
    project_info = {
        "name": project['name'],
        "id": project['id'],
        "path": project['path_with_namespace'],
        "description": project.get('description', 'N/A'),
        "default_branch": project.get('default_branch', 'N/A'),
        "web_url": project['web_url'],
        "summary": {
            "branch_count": len(branches),
            "main_branch": main_branch_info,
            "contributor_count": contributor_count
        },
        "branches": []
    }
    
    # Collect individual branch info
    if branches:
        for branch in branches:
            branch_name = branch['name']
            branch_info = collect_branch_info(project_id, branch_name)
            project_info["branches"].append(branch_info)
    
    return project_info


def collect_gitlab_info(parent_group_name: str) -> Dict[str, Any]:
    """
    Collect information about a GitLab group and its subgroups in a structured format.
    
    Args:
        parent_group_name: Name of the parent group to extract information for
        
    Returns:
        Dictionary with structured GitLab information
    """
    result = {
        "parent_group": None,
        "subgroups": [],
        "direct_projects": []
    }
    
    # Find the parent group
    parent_group = get_group_by_name(parent_group_name)
    
    if not parent_group:
        return result
    
    # Add parent group info
    result["parent_group"] = {
        "name": parent_group['name'],
        "id": parent_group['id'],
        "path": parent_group['full_path'],
        "description": parent_group.get('description', 'N/A'),
        "visibility": parent_group['visibility'],
        "web_url": parent_group['web_url']
    }
    
    # Get subgroups
    subgroups = get_subgroups(parent_group['id'])
    
    for subgroup in subgroups:
        subgroup_info = {
            "name": subgroup['name'],
            "id": subgroup['id'],
            "path": subgroup['full_path'],
            "description": subgroup.get('description', 'N/A'),
            "visibility": subgroup['visibility'],
            "web_url": subgroup['web_url'],
            "projects": []
        }
        
        # Get projects in the subgroup
        projects = get_projects(subgroup['id'])
        
        for project in projects:
            project_info = collect_project_info(project)
            subgroup_info["projects"].append(project_info)
        
        result["subgroups"].append(subgroup_info)
    
    # Get projects directly in the parent group
    projects = get_projects(parent_group['id'])
    direct_projects = [p for p in projects if p['namespace']['id'] == parent_group['id']]
    
    for project in direct_projects:
        project_info = collect_project_info(project)
        result["direct_projects"].append(project_info)
    
    return result


def save_to_json(data: Dict[str, Any], filename: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save
        filename: The name of the file to save to
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"JSON data saved to {filename}")
    except Exception as e:
        print(f"Error saving JSON data: {e}")


def generate_markdown(data: Dict[str, Any]) -> str:
    """
    Generate Markdown content from GitLab data.
    
    Args:
        data: Dictionary with GitLab information
        
    Returns:
        Markdown formatted string
    """
    md = []
    
    # Add title
    md.append("# GitLab Group Information\n")
    
    # Add timestamp
    md.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Add parent group info
    parent = data.get("parent_group")
    if parent:
        md.append(f"## Parent Group: {parent['name']}\n")
        md.append(f"- **ID:** {parent['id']}")
        md.append(f"- **Path:** {parent['path']}")
        md.append(f"- **Description:** {parent['description']}")
        md.append(f"- **Visibility:** {parent['visibility']}")
        md.append(f"- **Web URL:** [{parent['web_url']}]({parent['web_url']})\n")
    
    # Add subgroups
    subgroups = data.get("subgroups", [])
    if subgroups:
        md.append("## Subgroups\n")
        
        for subgroup in subgroups:
            md.append(f"### {subgroup['name']}\n")
            md.append(f"- **ID:** {subgroup['id']}")
            md.append(f"- **Path:** {subgroup['path']}")
            md.append(f"- **Description:** {subgroup['description']}")
            md.append(f"- **Visibility:** {subgroup['visibility']}")
            md.append(f"- **Web URL:** [{subgroup['web_url']}]({subgroup['web_url']})\n")
            
            # Add projects in subgroup
            projects = subgroup.get("projects", [])
            if projects:
                md.append(f"#### Projects in {subgroup['name']}\n")
                
                for project in projects:
                    md.append(f"##### {project['name']}\n")
                    md.append(f"- **ID:** {project['id']}")
                    md.append(f"- **Path:** {project['path']}")
                    md.append(f"- **Description:** {project['description']}")
                    md.append(f"- **Default Branch:** {project['default_branch']}")
                    md.append(f"- **Web URL:** [{project['web_url']}]({project['web_url']})\n")
                    
                    # Add project summary
                    summary = project.get("summary", {})
                    md.append("**Project Summary:**\n")
                    md.append(f"- **Total Branches:** {summary.get('branch_count', 0)}")
                    
                    main_branch = summary.get("main_branch")
                    if main_branch:
                        md.append(f"- **Latest Update on '{main_branch['name']}':** {main_branch.get('last_update', 'N/A')} by {main_branch.get('updated_by', 'N/A')}")
                    else:
                        md.append("- **Latest Update on Main Branch:** No main branch found")
                    
                    md.append(f"- **Number of Contributors:** {summary.get('contributor_count', 0)}\n")
                    
                    # Add branches
                    branches = project.get("branches", [])
                    if branches:
                        md.append("**Branches:**\n")
                        md.append("| Branch Name | Last Updated | Updated By | Commit Message |")
                        md.append("|------------|--------------|------------|----------------|")
                        
                        for branch in branches:
                            branch_name = branch['name']
                            last_update = branch.get('last_update', 'N/A')
                            updated_by = branch.get('updated_by', 'N/A')
                            commit_msg = branch.get('commit_message', 'N/A')
                            
                            md.append(f"| {branch_name} | {last_update} | {updated_by} | {commit_msg} |")
                        
                        md.append("")
    
    # Add direct projects
    direct_projects = data.get("direct_projects", [])
    if direct_projects:
        md.append("## Projects in Parent Group\n")
        
        for project in direct_projects:
            md.append(f"### {project['name']}\n")
            md.append(f"- **ID:** {project['id']}")
            md.append(f"- **Path:** {project['path']}")
            md.append(f"- **Description:** {project['description']}")
            md.append(f"- **Default Branch:** {project['default_branch']}")
            md.append(f"- **Web URL:** [{project['web_url']}]({project['web_url']})\n")
            
            # Add project summary
            summary = project.get("summary", {})
            md.append("**Project Summary:**\n")
            md.append(f"- **Total Branches:** {summary.get('branch_count', 0)}")
            
            main_branch = summary.get("main_branch")
            if main_branch:
                md.append(f"- **Latest Update on '{main_branch['name']}':** {main_branch.get('last_update', 'N/A')} by {main_branch.get('updated_by', 'N/A')}")
            else:
                md.append("- **Latest Update on Main Branch:** No main branch found")
            
            md.append(f"- **Number of Contributors:** {summary.get('contributor_count', 0)}\n")
            
            # Add branches
            branches = project.get("branches", [])
            if branches:
                md.append("**Branches:**\n")
                md.append("| Branch Name | Last Updated | Updated By | Commit Message |")
                md.append("|------------|--------------|------------|----------------|")
                
                for branch in branches:
                    branch_name = branch['name']
                    last_update = branch.get('last_update', 'N/A')
                    updated_by = branch.get('updated_by', 'N/A')
                    commit_msg = branch.get('commit_message', 'N/A')
                    
                    md.append(f"| {branch_name} | {last_update} | {updated_by} | {commit_msg} |")
                
                md.append("")
    
    return "\n".join(md)


def save_to_markdown(data: Dict[str, Any], filename: str) -> None:
    """
    Generate and save Markdown content to a file.
    
    Args:
        data: Dictionary with GitLab information
        filename: The name of the file to save to
    """
    try:
        markdown_content = generate_markdown(data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Markdown data saved to {filename}")
    except Exception as e:
        print(f"Error saving Markdown data: {e}")


def generate_csv_data(data: Dict[str, Any]) -> List[List[str]]:
    """
    Generate CSV data from GitLab information.
    
    Args:
        data: Dictionary with GitLab information
        
    Returns:
        List of rows for CSV, where each row contains values for the columns:
        group, subgroup, project, branch, branch updated by, branch last updated, branch last commit message
    """
    csv_rows = []
    
    # Add header row
    header = [
        "Group", 
        "Subgroup", 
        "Project/Repository", 
        "Branch", 
        "Updated By", 
        "Last Updated", 
        "Commit Message"
    ]
    csv_rows.append(header)
    
    parent_group = data.get("parent_group", {})
    parent_group_name = parent_group.get("name", "N/A") if parent_group else "N/A"
    
    # Process projects directly in parent group
    direct_projects = data.get("direct_projects", [])
    for project in direct_projects:
        project_name = project.get("name", "N/A")
        branches = project.get("branches", [])
        
        for branch in branches:
            branch_name = branch.get("name", "N/A")
            updated_by = branch.get("updated_by", "N/A")
            last_updated = branch.get("last_update", "N/A")
            commit_message = branch.get("commit_message", "N/A")
            
            row = [
                parent_group_name,  # Group
                "",                 # Subgroup (empty for direct projects)
                project_name,       # Project/Repository
                branch_name,        # Branch
                updated_by,         # Updated By
                last_updated,       # Last Updated
                commit_message      # Commit Message
            ]
            csv_rows.append(row)
    
    # Process subgroups and their projects
    subgroups = data.get("subgroups", [])
    for subgroup in subgroups:
        subgroup_name = subgroup.get("name", "N/A")
        projects = subgroup.get("projects", [])
        
        for project in projects:
            project_name = project.get("name", "N/A")
            branches = project.get("branches", [])
            
            for branch in branches:
                branch_name = branch.get("name", "N/A")
                updated_by = branch.get("updated_by", "N/A")
                last_updated = branch.get("last_update", "N/A")
                commit_message = branch.get("commit_message", "N/A")
                
                row = [
                    parent_group_name,  # Group
                    subgroup_name,      # Subgroup
                    project_name,       # Project/Repository
                    branch_name,        # Branch
                    updated_by,         # Updated By
                    last_updated,       # Last Updated
                    commit_message      # Commit Message
                ]
                csv_rows.append(row)
    
    return csv_rows


def save_to_csv(data: List[List[str]], filename: str) -> None:
    """
    Save data to a CSV file.
    
    Args:
        data: List of rows, where each row is a list of column values
        filename: The name of the file to save to
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            for row in data:
                csv_writer.writerow(row)
        
        print(f"CSV data saved to {filename}")
    except Exception as e:
        print(f"Error saving CSV data: {e}")


def extract_gitlab_info(parent_group_name: str) -> None:
    """
    Extract and display information about a GitLab group and its subgroups.
    
    Args:
        parent_group_name: Name of the parent group to extract information for
    """
    # Find the parent group
    parent_group = get_group_by_name(parent_group_name)
    
    if not parent_group:
        return
    
    print("\n===== PARENT GROUP INFORMATION =====\n")
    print_group_info(parent_group)
    
    # Get subgroups
    subgroups = get_subgroups(parent_group['id'])
    
    if subgroups:
        print("\n===== SUBGROUPS =====\n")
        for subgroup in subgroups:
            print_group_info(subgroup, level=1)
            
            # Get projects in the subgroup
            projects = get_projects(subgroup['id'])
            
            if projects:
                print(f"  Projects in {subgroup['name']}:\n")
                for project in projects:
                    print_project_info(project, level=2)
    
    # Get projects directly in the parent group
    projects = get_projects(parent_group['id'])
    
    if projects:
        direct_projects = [p for p in projects if p['namespace']['id'] == parent_group['id']]
        
        if direct_projects:
            print("\n===== PROJECTS IN PARENT GROUP =====\n")
            for project in direct_projects:
                print_project_info(project, level=1)


def main() -> None:
    """Main function to run the script."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Validate required environment variables
    validate_env_vars()
    
    parent_group_name = "DS and ML Research Sandbox"
    
    print(f"Extracting information for GitLab group: {parent_group_name}")
    
    # Display information in the console
    extract_gitlab_info(parent_group_name)
    
    # Collect data for JSON and Markdown output
    gitlab_data = collect_gitlab_info(parent_group_name)
    
    # Save to JSON
    json_filename = f"gitlab_info_{parent_group_name.replace(' ', '_').lower()}.json"
    save_to_json(gitlab_data, json_filename)
    
    # Save to Markdown
    markdown_filename = f"gitlab_info_{parent_group_name.replace(' ', '_').lower()}.md"
    save_to_markdown(gitlab_data, markdown_filename)
    
    # Generate and save CSV data
    csv_data = generate_csv_data(gitlab_data)
    csv_filename = f"gitlab_info_{parent_group_name.replace(' ', '_').lower()}.csv"
    save_to_csv(csv_data, csv_filename)


if __name__ == "__main__":
    main() 