#!/usr/bin/env python3
"""
Test script to verify the updated issue parsing logic
"""

import os
import json
from typing import Dict, List, Any

def parse_issues_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse issues from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return parse_issues_from_text(content)
    
    except Exception as e:
        print(f"Error reading or parsing file {file_path}: {e}")
        return []

def parse_issues_from_text(content: str) -> List[Dict[str, Any]]:
    """Parse issues from text content."""
    issues = []
    
    # Skip the header line
    if content.startswith("High-Level GitLab Issues"):
        content = content.split('\n', 1)[1]
    
    # Split content by separator lines (underscores)
    sections = content.split('________________________________________')
    
    print(f"Found {len(sections)} sections")
    
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
            print(f"Added issue: {current_issue_title}")
    
    return issues

def main():
    """Main test function"""
    issue_file = "issues/issue-flow-product-recommendation.txt"
    
    if not os.path.exists(issue_file):
        print(f"Error: Issues file '{issue_file}' not found.")
        return
    
    print(f"Processing issues file: {issue_file}")
    issues = parse_issues_from_file(issue_file)
    
    print(f"\nTotal issues found: {len(issues)}")
    
    # Save the parsed issues to a JSON file for review
    with open("parsed_issues.json", "w", encoding="utf-8") as f:
        json.dump([{
            "title": issue["title"],
            "type": issue["type"],
            "description": issue["description"],
            "labels": issue["labels"]
        } for issue in issues], f, indent=2)
    
    print("Issues saved to parsed_issues.json")
    
    # Print details of each issue
    for i, issue in enumerate(issues, 1):
        print(f"\nIssue {i}: {issue['title']} [{issue['type']}]")
        print(f"Labels: {', '.join(issue['labels'])}")
        
        # Show first lines of description and acceptance criteria
        desc_lines = issue['raw_description'].strip().split('\n')
        if desc_lines:
            print("Description preview:")
            for line in desc_lines[:2]:  # Show first 2 lines
                print(f"  {line}")
                
        acc_lines = issue['raw_acceptance'].strip().split('\n')
        if acc_lines:
            print("Acceptance criteria preview:")
            for line in acc_lines[:2]:  # Show first 2 lines
                print(f"  {line}")

if __name__ == "__main__":
    main() 