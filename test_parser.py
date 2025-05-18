#!/usr/bin/env python3
"""
Test Script for GitLab Issues Parser

This script directly tests the issue parser with verbose output.
"""

import os
import sys
from dotenv import load_dotenv

# Create a simplified version of the parser for testing
def test_parse_issues(file_path):
    """Parse issues with detailed output for debugging"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File content length: {len(content)} characters")
    
    # Split content by separator lines
    sections = content.split('________________________________________')
    print(f"Found {len(sections)} sections")
    
    issues = []
    
    # Process each section
    for section_idx, section in enumerate(sections):
        if not section.strip():
            print(f"Section {section_idx}: [Empty section]")
            continue
            
        lines = section.strip().split('\n')
        if not lines:
            print(f"Section {section_idx}: [No lines]")
            continue
            
        print(f"\n===== SECTION {section_idx + 1} =====")
        print(f"First few lines:")
        for i, line in enumerate(lines[:min(5, len(lines))]):
            print(f"  Line {i}: '{line}'")
        
        # Find the title line
        first_line = lines[0].strip()
        
        # Handle optional numbered prefixes
        if first_line and first_line[0].isdigit() and len(lines) > 1:
            print(f"  Found numbered prefix: '{first_line}'")
            # Skip the number prefix line and use the next line as the title
            first_line = lines[1].strip()
            lines = lines[1:]  # Remove the number prefix line
            print(f"  Using next line as title: '{first_line}'")
        
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
            print(f"  Found Feature: '{current_issue_title}'")
        elif "[Task]" in first_line:
            current_issue_type = "Task"
            current_issue_title = first_line.split("[Task]")[1].strip()
            print(f"  Found Task: '{current_issue_title}'")
        else:
            print(f"  ❌ No [Feature] or [Task] tag found in first line")
            continue
        
        # Flags to track what we're parsing
        parse_mode = None
        
        # Process the remaining lines
        for line_idx, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                continue
                
            # Check for bullet points with labels
            if line.startswith('•'):
                parts = line[1:].strip().split(':', 1)
                if len(parts) == 2:
                    label, content = parts[0].strip(), parts[1].strip()
                    print(f"  Found bullet point with label: '{label}': '{content}'")
                    
                    if label.lower() == "description":
                        parse_mode = "description"
                        current_description += f"- {content}\n"
                        print(f"    Added to description")
                    elif label.lower() in ["acceptance criteria", "acceptance"]:
                        parse_mode = "acceptance"
                        current_acceptance += f"- {content}\n"
                        print(f"    Added to acceptance")
                    elif label.lower() == "labels":
                        parse_mode = None
                        current_labels = [l.strip() for l in content.split(',')]
                        if current_issue_type:
                            current_labels.append(current_issue_type.lower())
                        print(f"    Set labels: {current_labels}")
                else:
                    print(f"  ❌ Bullet point line doesn't contain a colon: '{line}'")
            # Regular section markers without bullet points
            elif line == "Description:":
                parse_mode = "description"
                print(f"  Found Description marker")
            elif line in ["Acceptance Criteria:", "Acceptance:"]:
                parse_mode = "acceptance"
                print(f"  Found Acceptance marker")
            elif line.startswith("Labels:"):
                parse_mode = None
                labels_text = line.split("Labels:", 1)[1].strip()
                current_labels = [label.strip() for label in labels_text.split(',')]
                if current_issue_type:
                    current_labels.append(current_issue_type.lower())
                print(f"  Found Labels: {current_labels}")
            # Handle content lines
            elif parse_mode == "description":
                if line.startswith('•'):
                    line = line[1:].strip()
                current_description += f"- {line}\n"
                print(f"  Added to description: '{line}'")
            elif parse_mode == "acceptance":
                if line.startswith('•'):
                    line = line[1:].strip()
                current_acceptance += f"- {line}\n"
                print(f"  Added to acceptance: '{line}'")
            else:
                print(f"  Unhandled line: '{line}'")
        
        # If we found a valid issue, add it to the list
        if current_issue_title:
            issue = {
                'title': current_issue_title,
                'type': current_issue_type,
                'labels': current_labels,
                'description': current_description,
                'acceptance': current_acceptance,
            }
            
            issues.append(issue)
            print(f"  ✓ Added issue: {current_issue_type} - {current_issue_title}")
            print(f"    Description: {len(current_description)} chars")
            print(f"    Acceptance: {len(current_acceptance)} chars")
            print(f"    Labels: {', '.join(current_labels)}")
        else:
            print(f"  ❌ No valid issue found in this section")
    
    return issues


def main():
    # Use the file passed as argument or default to issues_services_status.txt
    file_path = sys.argv[1] if len(sys.argv) > 1 else "issues/issues_services_status.txt"
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    print(f"Testing parser with file: {file_path}")
    issues = test_parse_issues(file_path)
    
    print("\n===== SUMMARY =====")
    print(f"Found {len(issues)} issues:")
    for i, issue in enumerate(issues):
        print(f"{i+1}. [{issue['type']}] {issue['title']}")
    
    if not issues:
        print("❌ No issues were found. Parser may need to be fixed.")


if __name__ == "__main__":
    main() 