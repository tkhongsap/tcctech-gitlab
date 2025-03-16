#!/usr/bin/env python3

import os
import sys
import requests
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Get GitLab configuration from environment variables
gitlab_url = os.getenv('GITLAB_URL')
gitlab_token = os.getenv('GITLAB_API_TOKEN')

# Validate environment variables
if not gitlab_url or not gitlab_token:
    print("Error: GITLAB_URL and GITLAB_API_TOKEN must be set in .env file")
    print("Please create a .env file based on .env.example")
    sys.exit(1)

# API endpoints
base_api_url = f"{gitlab_url.rstrip('/')}/api/v4"

# Headers for API requests
headers = {
    'Private-Token': gitlab_token,
    'Content-Type': 'application/json'
}

def get_subgroup_id(subgroup_name):
    """Get subgroup ID by name"""
    try:
        # Search for the subgroup by name
        search_url = f"{base_api_url}/groups"
        params = {'search': subgroup_name}
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        
        groups = response.json()
        for group in groups:
            if group['name'] == subgroup_name:
                return group['id']
        
        print(f"Error: Subgroup '{subgroup_name}' not found")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching subgroup: {e}")
        return None

def get_projects_for_subgroup(subgroup_id):
    """Get all projects within a subgroup"""
    try:
        projects = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{base_api_url}/groups/{subgroup_id}/projects"
            params = {'page': page, 'per_page': per_page, 'include_subgroups': True}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            batch = response.json()
            if not batch:
                break
                
            projects.extend(batch)
            page += 1
            
        return projects
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}")
        return []

def check_branch_exists(project_id, branch_name):
    """Check if a branch exists in a project"""
    try:
        url = f"{base_api_url}/projects/{project_id}/repository/branches/{branch_name}"
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def rename_branch(project_id, project_name, old_branch, new_branch):
    """Rename a branch in a GitLab project"""
    try:
        # First, check if the old branch exists
        if not check_branch_exists(project_id, old_branch):
            print(f"  - '{old_branch}' branch not found in project '{project_name}'")
            return False
            
        # Check if the new branch already exists
        if check_branch_exists(project_id, new_branch):
            print(f"  - '{new_branch}' branch already exists in project '{project_name}'")
            return False
            
        # Create new branch based on old branch
        create_url = f"{base_api_url}/projects/{project_id}/repository/branches"
        create_params = {'branch': new_branch, 'ref': old_branch}
        create_response = requests.post(create_url, headers=headers, params=create_params)
        create_response.raise_for_status()
        
        # Update default branch to new branch
        update_url = f"{base_api_url}/projects/{project_id}"
        update_params = {'default_branch': new_branch}
        update_response = requests.put(update_url, headers=headers, json=update_params)
        update_response.raise_for_status()
        
        # Delete old branch
        delete_url = f"{base_api_url}/projects/{project_id}/repository/branches/{old_branch}"
        delete_response = requests.delete(delete_url, headers=headers)
        delete_response.raise_for_status()
        
        print(f"  ✓ Successfully renamed '{old_branch}' to '{new_branch}' in project '{project_name}'")
        return True
    except requests.exceptions.RequestException as e:
        print(f"  × Error renaming branch in project '{project_name}': {e}")
        return False

def process_group(group_name):
    """Process all projects in a group to rename branches"""
    print(f"\nProcessing group: {group_name}")
    print("-" * 50)
    
    # Get group ID
    group_id = get_subgroup_id(group_name)
    if not group_id:
        return False
    
    # Get all projects in the group and its subgroups
    projects = get_projects_for_subgroup(group_id)
    if not projects:
        print(f"No projects found in group '{group_name}'")
        return False
    
    print(f"Found {len(projects)} projects in group '{group_name}' and its subgroups")
    
    # Process each project
    success_count = 0
    for project in projects:
        project_id = project['id']
        project_name = project['name']
        print(f"\nProcessing project: {project_name} (ID: {project_id})")
        
        if rename_branch(project_id, project_name, "trunk", "main"):
            success_count += 1
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
    
    print(f"\nSummary for '{group_name}': Renamed {success_count} out of {len(projects)} projects")
    return True

def main():
    """Main function to process the AI-ML-Services subgroup"""
    print("GitLab Branch Rename Tool: 'trunk' → 'main'")
    print("=" * 50)
    
    group_name = "AI-ML-Services"
    
    if process_group(group_name):
        print("\nOperation completed successfully!")
    else:
        print("\nOperation completed with errors.")

if __name__ == "__main__":
    main() 