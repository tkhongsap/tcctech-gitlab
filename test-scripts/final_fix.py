#!/usr/bin/env python3
"""
Modified GitLab Issue Creator to fix parsing issues
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

def parse_issues_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse issues from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip the header line if present
        if content.startswith("High-Level GitLab Issues"):
            content = content.split('\n', 1)[1]
            
        issues = []
        sections = content.split('________________________________________')
        
        print(f"Found {len(sections)} sections")
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            first_line = lines[0].strip()
            
            # Extract issue type and title
            if "[Feature]" in first_line or "[Task]" in first_line:
                if "[Feature]" in first_line:
                    issue_type = "Feature"
                    title = first_line.split("[Feature]")[1].strip()
                else:
                    issue_type = "Task"
                    title = first_line.split("[Task]")[1].strip()
                    
                # Extract description, acceptance criteria, and labels
                desc_text = ""
                accept_text = ""
                labels = []
                
                current_section = None
                
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line == "Description:":
                        current_section = "description"
                    elif line in ["Acceptance Criteria:", "Acceptance:"]:
                        current_section = "acceptance"
                    elif line.startswith("Labels:"):
                        labels_text = line.split("Labels:", 1)[1].strip()
                        labels = [label.strip() for label in labels_text.split(',')]
                        if issue_type:
                            labels.append(issue_type.lower())
                    elif current_section == "description":
                        if line.startswith('•'):
                            line = line[1:].strip()
                        desc_text += f"- {line}\n"
                    elif current_section == "acceptance":
                        if line.startswith('•'):
                            line = line[1:].strip()
                        accept_text += f"- {line}\n"
                
                # Format the description for GitLab
                formatted_description = "## Description\n"
                if desc_text.strip():
                    formatted_description += desc_text
                else:
                    formatted_description += "- No description provided.\n"
                
                formatted_description += "\n## Acceptance Criteria\n"
                if accept_text.strip():
                    formatted_description += accept_text
                else:
                    formatted_description += "- No acceptance criteria provided.\n"
                
                # Create issue dict
                issue = {
                    'title': title,
                    'description': formatted_description,
                    'labels': labels,
                    'type': issue_type,
                    'raw_description': desc_text,
                    'raw_acceptance': accept_text
                }
                
                issues.append(issue)
                print(f"Added issue: {title} [{issue_type}]")
        
        return issues
    
    except Exception as e:
        print(f"Error reading or parsing file {file_path}: {e}")
        return []

def main():
    """Main function"""
    issue_file = "issues/issue-flow-product-recommendation.txt"
    
    if not os.path.exists(issue_file):
        print(f"Error: Issues file '{issue_file}' not found.")
        sys.exit(1)
        
    issues = parse_issues_from_file(issue_file)
    
    # Print results
    print(f"\nTotal issues found: {len(issues)}")
    
    # Save parsed issues to JSON file
    with open("parsed_issues.json", "w", encoding="utf-8") as f:
        json.dump([{
            "title": issue["title"],
            "type": issue["type"],
            "description": issue["description"]
        } for issue in issues], f, indent=2)
    
    print("Saved parsed issues to parsed_issues.json")
    
    # Print full details of first issue
    if issues:
        print(f"\nFirst issue details:")
        print(f"Title: {issues[0]['title']}")
        print(f"Type: {issues[0]['type']}")
        print(f"Labels: {', '.join(issues[0]['labels'])}")
        print("\nDescription:")
        print(issues[0]['description'])

if __name__ == "__main__":
    main() 