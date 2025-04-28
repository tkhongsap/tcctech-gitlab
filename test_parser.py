#!/usr/bin/env python3

import os
import sys
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
    for i, section in enumerate(sections):
        print(f"\nProcessing section {i+1}...")
        if not section.strip():
            print("  - Empty section, skipping")
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            print("  - No lines found, skipping")
            continue
            
        # Find the first line which should contain issue type and title
        first_line = lines[0].strip()
        print(f"  First line: '{first_line}'")
        
        # Variables to accumulate issue data
        current_issue_title = ""
        current_issue_type = ""
        current_description = ""
        current_acceptance = ""
        current_labels = []
        
        # Parse issue type and title from the first line
        if "[Feature]" in first_line:
            print("  - Found [Feature] tag")
            current_issue_type = "Feature"
            current_issue_title = first_line.split("[Feature]")[1].strip()
            print(f"  - Title: '{current_issue_title}'")
        elif "[Task]" in first_line:
            print("  - Found [Task] tag")
            current_issue_type = "Task"
            current_issue_title = first_line.split("[Task]")[1].strip()
            print(f"  - Title: '{current_issue_title}'")
        else:
            print("  ❌ Error: No [Feature] or [Task] tag found in first line")
            print("  - This section will be skipped by the parser")
            continue
        
        # Flags to track what we're parsing
        parse_mode = None
        
        # Process the remaining lines
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            # Check for section markers
            if line == "Description:" or line.startswith("• Description:"):
                parse_mode = "description"
                line = line.replace("• Description:", "").strip()
                if line:
                    current_description += f"- {line}\n"
            elif line == "Acceptance:" or line.startswith("• Acceptance:"):
                parse_mode = "acceptance"
                line = line.replace("• Acceptance:", "").strip()
                if line:
                    current_acceptance += f"- {line}\n"
            elif line.startswith("• Labels:") or line.startswith("Labels:"):
                parse_mode = None  # No multi-line parsing for labels
                labels_text = line.replace("• Labels:", "").replace("Labels:", "").strip()
                current_labels = [label.strip() for label in labels_text.split(',')]
                print(f"  - Found labels: {current_labels}")
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
            print(f"  ✓ Added issue: {current_issue_title}")
    
    print(f"\nTotal issues found: {len(issues)}")
    return issues


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "issues/issues-ocr-validation.txt"
    print(f"Testing parser with file: {file_path}")
    issues = parse_issues_from_file(file_path)
    
    print("\nIssues to be created:")
    print("=" * 80)
    
    for i, issue in enumerate(issues, 1):
        issue_type = f"[{issue.get('type', 'Issue')}]" if issue.get('type') else ""
        print(f"{i}. {issue_type} {issue['title']}")
        
        # Show labels
        if issue['labels']:
            print(f"   Labels: {', '.join(issue['labels'])}") 