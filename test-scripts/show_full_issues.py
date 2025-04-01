#!/usr/bin/env python3
"""
Script to display the full contents of each issue in a clear format
"""

import os
import json
import sys
from typing import Dict, List, Any

def parse_issues_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse issues from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip the header line
        if content.startswith("High-Level GitLab Issues"):
            content = content.split('\n', 1)[1]
        
        # Split content by separator lines (underscores)
        sections = content.split('________________________________________')
        
        issues = []
        
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
    
    except Exception as e:
        print(f"Error parsing file: {e}")
        return []

def main():
    """Main function to display issues in a clear format"""
    issue_file = "issues/issue-flow-product-recommendation.txt"
    output_file = "full_issues_content.txt"
    
    if len(sys.argv) > 1:
        issue_file = sys.argv[1]
    
    if not os.path.exists(issue_file):
        print(f"Error: Issues file '{issue_file}' not found.")
        sys.exit(1)
    
    print(f"Processing issues file: {issue_file}")
    issues = parse_issues_from_file(issue_file)
    
    print(f"\nFound {len(issues)} issues")
    
    # Open output file for writing
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Issues from {issue_file}\n\n")
        f.write(f"Total issues found: {len(issues)}\n\n")
        
        # Write each issue with clear separation
        for i, issue in enumerate(issues, 1):
            separator = "=" * 80
            f.write(f"{separator}\n")
            f.write(f"ISSUE {i}: {issue['title']} [{issue['type']}]\n")
            f.write(f"{separator}\n\n")
            
            # Write labels
            f.write(f"LABELS: {', '.join(issue['labels'])}\n\n")
            
            # Write full description content
            f.write("DESCRIPTION:\n")
            f.write("-" * 40 + "\n")
            lines = issue['raw_description'].strip().split('\n')
            for line in lines:
                f.write(f"{line}\n")
            
            # Write full acceptance criteria content
            f.write("\nACCEPTANCE CRITERIA:\n")
            f.write("-" * 40 + "\n")
            lines = issue['raw_acceptance'].strip().split('\n')
            for line in lines:
                f.write(f"{line}\n")
                
            f.write("\n\n")  # Extra space between issues
    
    print(f"Full issue details written to {output_file}")
    
    # Also print summary to console
    for i, issue in enumerate(issues, 1):
        print(f"{i}. [{issue['type']}] {issue['title']}")
        print(f"   Labels: {', '.join(issue['labels'])}")
        print(f"   Description lines: {len(issue['raw_description'].strip().split('\n'))}")
        print(f"   Acceptance criteria lines: {len(issue['raw_acceptance'].strip().split('\n'))}")
        print()

if __name__ == "__main__":
    main() 